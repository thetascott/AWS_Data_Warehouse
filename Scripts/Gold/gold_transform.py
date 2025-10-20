import boto3
import os

s3 = boto3.client("s3")
redshift_data = boto3.client("redshift-data")

WORKGROUP_NAME = os.environ.get("REDSHIFT_WORKGROUP", "data-warehouse-wg")
DATABASE = os.environ.get("REDSHIFT_DB", "datawarehouse")
REDSHIFT_ROLE_ARN = os.environ.get("REDSHIFT_ROLE_ARN", "")
S3_SCRIPTS_BUCKET = os.environ.get("S3_SCRIPTS_BUCKET", "")
S3_SCRIPTS_KEY = os.environ.get("S3_SCRIPTS_KEY", "Gold/ddl_gold.sql")

def execute_sql(sql):
    """Executes SQL statement using Redshift Data API for Serverless."""
    response = redshift_data.execute_statement(
        WorkgroupName=WORKGROUP_NAME,
        Database=DATABASE,
        Sql=sql,
    )
    return response["Id"]

def main():
    # 1️⃣ Ensure external schema exists for silver
    schema_sql = f"""
    CREATE EXTERNAL SCHEMA IF NOT EXISTS silver
    FROM DATA CATALOG
    DATABASE 'silver_db'
    IAM_ROLE '{REDSHIFT_ROLE_ARN}'
    CREATE EXTERNAL DATABASE IF NOT EXISTS;
    """
    execute_sql(schema_sql)

    # 2️⃣ Load SQL from S3
    obj = s3.get_object(Bucket=S3_SCRIPTS_BUCKET, Key=S3_SCRIPTS_KEY)
    sql_script = obj["Body"].read().decode("utf-8")

    # 3️⃣ Split into statements and execute sequentially
    statements = [stmt.strip() for stmt in sql_script.split(";") if stmt.strip()]
    for stmt in statements:
        print(f"Executing statement (first 200 chars): {stmt[:200]}")
        execute_sql(stmt)

def handler(event, context):
    main()
    return {"status": "Gold layer views created successfully."}

if __name__ == "__main__":
    main()