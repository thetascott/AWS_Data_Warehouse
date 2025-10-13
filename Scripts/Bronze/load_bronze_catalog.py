import boto3
import csv
import io
import os
from datetime import datetime

# -------------------------
# CONFIGURATION (Variables)
# -------------------------
AWS_REGION = os.environ.get("AWS_REGION", "us-east-2")
BRONZE_BUCKET = os.environ.get("BRONZE_BUCKET", "your-bronze-bucket")
GLUE_DATABASE = os.environ.get("BRONZE_GLUE_DATABASE", "srs_bronze_db")
FOLDERS = ["crm", "erp"]  # Can be extended

# -------------------------
# AWS Clients
# -------------------------
glue_client = boto3.client("glue", region_name=AWS_REGION)
s3_client = boto3.client("s3", region_name=AWS_REGION)

# -------------------------
# DATA TYPE INFERENCE
# -------------------------
def infer_type(value):
    """
    Try to infer Glue data type from a sample value
    """
    if value == "":
        return "string"
    try:
        int(value)
        return "int"
    except ValueError:
        pass
    try:
        float(value)
        return "double"
    except ValueError:
        pass
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y"):
        try:
            datetime.strptime(value, fmt)
            return "date"
        except ValueError:
            pass
    return "string"

def get_csv_columns(s3_bucket, key, max_rows=50):
    """
    Read first few rows to infer column names and types
    """
    resp = s3_client.get_object(Bucket=s3_bucket, Key=key)
    csv_content = resp["Body"].read().decode("utf-8")
    reader = csv.reader(io.StringIO(csv_content))
    header = next(reader)
    samples = [row for _, row in zip(range(max_rows), reader)]

    columns = []
    for col_idx, col_name in enumerate(header):
        # Collect sample values for this column
        sample_values = [row[col_idx] for row in samples if len(row) > col_idx]
        # Infer type based on first non-empty sample
        col_type = next((infer_type(v) for v in sample_values if v.strip() != ""), "string")
        columns.append({"Name": col_name.strip(), "Type": col_type})
    return columns

# -------------------------
# CREATE GLUE TABLE
# -------------------------
def create_glue_table(table_name, s3_path, columns):
    try:
        glue_client.create_table(
            DatabaseName=GLUE_DATABASE,
            TableInput={
                "Name": table_name.lower(),
                "TableType": "EXTERNAL_TABLE",
                "StorageDescriptor": {
                    "Columns": columns,
                    "Location": s3_path,
                    "InputFormat": "org.apache.hadoop.mapred.TextInputFormat",
                    "OutputFormat": "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat",
                    "SerdeInfo": {
                        "SerializationLibrary": "org.apache.hadoop.hive.serde2.OpenCSVSerde",
                        "Parameters": {"separatorChar": ",", "skip.header.line.count": "1"},
                    },
                },
                "Parameters": {"classification": "csv", "has_encrypted_data": "false"},
            },
        )
        print(f"Glue table '{table_name}' created successfully.")
    except glue_client.exceptions.AlreadyExistsException:
        print(f"Glue table '{table_name}' already exists. Skipping.")

# -------------------------
# MAIN
# -------------------------
def main():
    for folder in FOLDERS:
        resp = s3_client.list_objects_v2(Bucket=BRONZE_BUCKET, Prefix=f"{folder}/")
        if "Contents" not in resp:
            continue

        for obj in resp["Contents"]:
            key = obj["Key"]
            if not key.endswith(".csv"):
                continue

            table_name = os.path.splitext(os.path.basename(key))[0]
            s3_path = f"s3://{BRONZE_BUCKET}/{folder}/{table_name}/"
            columns = get_csv_columns(BRONZE_BUCKET, key)
            create_glue_table(table_name, s3_path, columns)


if __name__ == "__main__":
    main()