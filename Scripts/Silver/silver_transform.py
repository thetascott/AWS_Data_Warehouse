import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col, trim, when, upper, row_number, current_date, substring, coalesce, to_date, lead, length, abs, lit, regexp_replace,expr
from pyspark.sql import Window
from pyspark.sql.types import DateType
from awsglue.utils import getResolvedOptions

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)

# Buckets
args = getResolvedOptions(sys.argv, ["BRONZE_BUCKET", "SILVER_BUCKET"])
bronze_bucket = "s3://" + args['BRONZE_BUCKET'].rstrip('/') + "/"
silver_bucket = "s3://" + args['SILVER_BUCKET'].rstrip('/') + "/"

def process_crm_cust_info():
    df = spark.read.option("header", True).csv(bronze_bucket + "crm/cust_info.csv")

    # Transformations
    df_clean = (
        df.withColumn("cst_firstname", trim(col("cst_firstname")))
          .withColumn("cst_lastname", trim(col("cst_lastname")))
          .withColumn(
              "cst_marital_status",
              when(upper(trim(col("cst_marital_status"))) == "S", "Single")
              .when(upper(trim(col("cst_marital_status"))) == "M", "Married")
              .otherwise("n/a")
          )
          .withColumn(
              "cst_gndr",
              when(upper(trim(col("cst_gndr"))) == "F", "Female")
              .when(upper(trim(col("cst_gndr"))) == "M", "Male")
              .otherwise("n/a")
          )
          .withColumn("dwh_create_date", current_date())  # Add current date column
    )

    # Remove null customer IDs
    df_filtered = df_clean.filter(col("cst_id").isNotNull())

    # Deduplicate: keep the latest record per customer based on cst_create_date
    window_spec = Window.partitionBy("cst_id").orderBy(col("cst_create_date").desc())
    df_final = df_filtered.withColumn("flag_last", row_number().over(window_spec)) \
                          .filter(col("flag_last") == 1) \
                          .drop("flag_last")
    
    # Save as Parquet
    df_final.write.mode("overwrite").parquet(silver_bucket + "crm/cust_info/")

    print("Transformation complete: cust_info → silver layer")

def process_crm_prd_info():
    df = spark.read.option("header", True).csv(bronze_bucket + "crm/prd_info.csv")

     # Transformations
    df_clean = (
        df.withColumn("cat_id", substring(col("prd_key"), 1, 5)) 
          .withColumn("cat_id", regexp_replace(col("cat_id"), "-", "_"))  # replace '-' with '_'
          .withColumn("prd_key", substring(col("prd_key"), 7, 100))  # adjust length as needed
          .withColumn("prd_nm", trim(col("prd_nm")))
          .withColumn("prd_cost", coalesce(col("prd_cost"), lit(0)))
          .withColumn(
              "prd_line",
              when(upper(trim(col("prd_line"))) == "M", "Mountain")
              .when(upper(trim(col("prd_line"))) == "R", "Road")
              .when(upper(trim(col("prd_line"))) == "S", "Other Sales")
              .when(upper(trim(col("prd_line"))) == "T", "Touring")
              .otherwise("n/a")
          )
          .withColumn("prd_start_dt", to_date(col("prd_start_dt"), "yyyy-MM-dd"))
          .withColumn("dwh_create_date", current_date())  # Add create date
    )

    # Window to calculate prd_end_dt
    window_spec = Window.partitionBy("prd_key").orderBy("prd_start_dt")
    df_final = df_clean.withColumn(
        "prd_end_dt",
        lead("prd_start_dt").over(window_spec)  # next start date
    ).withColumn(
        "prd_end_dt",
        (col("prd_end_dt").cast("date") - 1).cast("date")  # subtract 1 day
    )

    # Save as Parquet
    df_final.write.mode("overwrite").parquet(silver_bucket + "crm/prd_info/")

    print("Transformation complete: prd_info → silver layer")

def process_crm_sales_details():
    df = spark.read.option("header", True).csv(bronze_bucket + "crm/sales_details.csv")

    # Transformations
    df_clean = (
        df
        # Convert order dates to DateType if valid (YYYYMMDD), else null
        .withColumn(
            "sls_order_dt",
            when(
                (col("sls_order_dt") == 0) | (length(col("sls_order_dt").cast("string")) != 8),
                None
            ).otherwise(col("sls_order_dt").cast("string").cast(DateType()))
        )
        .withColumn(
            "sls_ship_dt",
            when(
                (col("sls_ship_dt") == 0) | (length(col("sls_ship_dt").cast("string")) != 8),
                None
            ).otherwise(col("sls_ship_dt").cast("string").cast(DateType()))
        )
        .withColumn(
            "sls_due_dt",
            when(
                (col("sls_due_dt") == 0) | (length(col("sls_due_dt").cast("string")) != 8),
                None
            ).otherwise(col("sls_due_dt").cast("string").cast(DateType()))
        )
        # Recalculate sales if missing or inconsistent
        .withColumn(
            "sls_sales",
            when(
                (col("sls_sales").isNull()) |
                (col("sls_sales") <= 0) |
                (col("sls_sales") != col("sls_quantity") * abs(col("sls_price"))),
                col("sls_quantity") * abs(col("sls_price"))
            ).otherwise(col("sls_sales"))
        )
        # Derive price if missing or invalid
        .withColumn(
            "sls_price",
            when(
                (col("sls_price").isNull()) | (col("sls_price") <= 0),
                col("sls_sales") / when(col("sls_quantity") == 0, lit(None)).otherwise(col("sls_quantity"))
            ).otherwise(col("sls_price"))
        )
        .withColumn("dwh_create_date", current_date())  # Add create date
    )

    # Save as Parquet
    df_clean.write.mode("overwrite").parquet(silver_bucket + "crm/sales_details/")

    print("Transformation complete: sales_details → silver layer")

def process_erp_cust_az12():
    df = spark.read.option("header", True).csv(bronze_bucket + "erp/CUST_AZ12.csv")

    # Transformations
    df_clean = (
        df
        # Remove 'NAS' prefix from cid
        .withColumn(
            "cid",
            when(col("cid").startswith("NAS"), substring(col("cid"), 4, 100))
            .otherwise(col("cid"))
        )
        # Set future birthdates to NULL
        .withColumn(
            "bdate",
            when(col("bdate") > current_date(), None).otherwise(col("bdate"))
        )
        # Normalize gender values
        .withColumn(
            "gen",
            when(upper(trim(col("gen"))).isin("F", "FEMALE"), "Female")
            .when(upper(trim(col("gen"))).isin("M", "MALE"), "Male")
            .otherwise("n/a")
        )
        .withColumn("dwh_create_date", current_date())  # Add create date
    )

    # Save as Parquet to silver layer
    df_clean.write.mode("overwrite").parquet(silver_bucket + "erp/cust_az12/")

    print("Transformation complete: cust_az12 → silver layer")

def process_erp_loc_a101():
    df = spark.read.option("header", True).csv(bronze_bucket + "erp/LOC_A101.csv")

    # Transformations
    df_clean = (
        df
        # Remove hyphens from cid
        .withColumn("cid", regexp_replace(col("cid"), "-", ""))
        # Normalize and handle missing or blank country codes
        .withColumn(
            "cntry",
            when(trim(col("cntry")) == "DE", "Germany")
            .when(trim(col("cntry")).isin("US", "USA"), "United States")
            .when((trim(col("cntry")) == "") | (col("cntry").isNull()), "n/a")
            .otherwise(trim(col("cntry")))
        )
    )

    # Save as Parquet to silver layer
    df_clean.write.mode("overwrite").parquet(silver_bucket + "erp/loc_a101/")

    print("Transformation complete: loc_a101 → silver layer")

def process_erp_px_cat_g1v2():
    df = spark.read.option("header", True).csv(bronze_bucket + "erp/PX_CAT_G1V2.csv")

    # Select relevant columns
    df_clean = (
        df.select("id", "cat", "subcat", "maintenance")
        # Add load date for silver layer consistency
        .withColumn("dwh_create_date", current_date())  # Add create date
    )

    # Save as Parquet to silver layer
    df_clean.write.mode("overwrite").parquet(silver_bucket + "erp/px_cat_g1v2/")

    print("Transformation complete: px_cat_g1v2 → silver layer")

def main():
    process_crm_cust_info()
    process_crm_prd_info()
    process_crm_sales_details()
    process_erp_cust_az12()
    process_erp_loc_a101()
    process_erp_px_cat_g1v2()

main()
job.commit()