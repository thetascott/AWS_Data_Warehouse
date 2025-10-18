import sys
import boto3
import os

AWS_REGION = os.environ.get("AWS_REGION", "us-east-2")
SILVER_BUCKET = os.environ.get("SILVER_BUCKET", "srs-silver-layer-0a493a95")
GLUE_DATABASE = os.environ.get("BRONZE_GLUE_DATABASE", "srs_silver_db")

glue_client = boto3.client("glue", region_name=AWS_REGION)

def build_table_input(table_name, columns, s3_path):
    """Build the common TableInput structure for Glue."""
    return {
        "Name": table_name,
        "StorageDescriptor": {
            "Columns": columns,
            "Location": s3_path,
            "InputFormat": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat",
            "OutputFormat": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat",
            "SerdeInfo": {
                "SerializationLibrary": "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe",
                "Parameters": {"serialization.format": "1"},
            },
        },
        "TableType": "EXTERNAL_TABLE",
        "Parameters": {"classification": "parquet"},
    }

def create_or_update_table(glue, db_name, table_name, columns, s3_path):
    """Create or update a Glue table."""
    table_input = build_table_input(table_name, columns, s3_path)
    try:
        glue.create_table(DatabaseName=db_name, TableInput=table_input)
        print(f"Created table: {table_name}")
    except glue.exceptions.AlreadyExistsException:
        glue.update_table(DatabaseName=db_name, TableInput=table_input)
        print(f"Updated table: {table_name}")

def main():
    # Create the database if it doesn’t exist
    try:
        glue_client.create_database(DatabaseInput={"Name": GLUE_DATABASE})
        print(f"Created database: {GLUE_DATABASE}")
    except glue_client.exceptions.AlreadyExistsException:
        print(f"Database '{GLUE_DATABASE}' already exists.")

    # Define schemas
    tables = {
        "crm_cust_info": [
            {"Name": "cst_id", "Type": "int"},
            {"Name": "cst_key", "Type": "string"},
            {"Name": "cst_firstname", "Type": "string"},
            {"Name": "cst_lastname", "Type": "string"},
            {"Name": "cst_marital_status", "Type": "string"},
            {"Name": "cst_gndr", "Type": "string"},
            {"Name": "cst_create_date", "Type": "date"},
            {"Name": "dwh_create_date", "Type": "timestamp"},
        ],
        "crm_prd_info": [
            {"Name": "prd_id", "Type": "int"},
            {"Name": "cat_id", "Type": "string"},
            {"Name": "prd_key", "Type": "string"},
            {"Name": "prd_nm", "Type": "string"},
            {"Name": "prd_cost", "Type": "int"},
            {"Name": "prd_line", "Type": "string"},
            {"Name": "prd_start_dt", "Type": "date"},
            {"Name": "prd_end_dt", "Type": "date"},
            {"Name": "dwh_create_date", "Type": "timestamp"},
        ],
        "crm_sales_details": [
            {"Name": "sls_ord_num", "Type": "string"},
            {"Name": "sls_prd_key", "Type": "string"},
            {"Name": "sls_cust_id", "Type": "int"},
            {"Name": "sls_order_dt", "Type": "date"},
            {"Name": "sls_ship_dt", "Type": "date"},
            {"Name": "sls_due_dt", "Type": "date"},
            {"Name": "sls_sales", "Type": "int"},
            {"Name": "sls_quantity", "Type": "int"},
            {"Name": "sls_price", "Type": "int"},
            {"Name": "dwh_create_date", "Type": "timestamp"},
        ],
        "erp_cust_az12": [
            {"Name": "cid", "Type": "string"},
            {"Name": "bdate", "Type": "date"},
            {"Name": "gen", "Type": "string"},
            {"Name": "dwh_create_date", "Type": "timestamp"},
        ],
        "erp_loc_a101": [
            {"Name": "cid", "Type": "string"},
            {"Name": "cntry", "Type": "string"},
            {"Name": "dwh_create_date", "Type": "timestamp"},
        ],
        "erp_px_cat_g1v2": [
            {"Name": "id", "Type": "string"},
            {"Name": "cat", "Type": "string"},
            {"Name": "subcat", "Type": "string"},
            {"Name": "maintenance", "Type": "string"},
            {"Name": "dwh_create_date", "Type": "timestamp"},
        ],
    }

    # Create/update all tables
    for table_name, columns in tables.items():
        s3_prefix = table_name.replace("_", "/")
        s3_path = f"s3://{SILVER_BUCKET}/{s3_prefix}/"
        create_or_update_table(glue_client, GLUE_DATABASE, table_name, columns, s3_path)

if __name__ == "__main__":
    main()