module "vpc" {
  source = "./modules/vpc"
  project_name = var.project_name

  public_subnets = {
    public-subnet-1 = { cidr = "10.0.1.0/24", az = "us-east-2a" }
    public-subnet-2 = { cidr = "10.0.2.0/24", az = "us-east-2b" }
  }

  private_subnets = {
    private-subnet-1 = { cidr = "10.0.101.0/24", az = "us-east-2a" }
    private-subnet-2 = { cidr = "10.0.102.0/24", az = "us-east-2b" }
  }
}

resource "random_id" "suffix" {
  byte_length = 4
}

module "bronze_bucket" {
  source      = "./modules/s3"
  bucket_name = "srs-bronze-layer-${random_id.suffix.hex}"
  tags = {
    "Project"     = var.project_name
  }
}

module "silver_bucket" {
  source      = "./modules/s3"
  bucket_name = "srs-silver-layer-${random_id.suffix.hex}"
  tags = {
    "Project"     = var.project_name
  }
}

module "iam" {
  source        = "./modules/iam"
  bronze_bucket = module.bronze_bucket.bucket_name
  silver_bucket = module.silver_bucket.bucket_name
}

module "glue" {
  source       = "./modules/glue"
  project_name = var.project_name
  glue_role_arn = module.iam.glue_role_arn

  databases = {
    bronze = {
      db_name      = "srs_bronze_db"
      description  = "Glue Catalog database for raw CSV data in bronze layer"
      location_uri = "s3://${module.bronze_bucket.bucket_name}/"
    }
    silver = {
      db_name      = "srs_silver_db"
      description  = "Glue Catalog database for cleaned Parquet data in silver layer"
      location_uri = "s3://${module.silver_bucket.bucket_name}/"
    }
  }

  crawlers = {
    bronze_crm = {
      bucket = module.bronze_bucket.bucket_name
      prefix = "crm"
      db_ref = "bronze"
      files = ["cust_info.csv", "prd_info.csv", "sales_details.csv"]
    }

    bronze_erp = {
      bucket = module.bronze_bucket.bucket_name
      prefix = "erp"
      db_ref = "bronze"
      files = ["CUST_AZ12.csv", "LOC_A101.csv", "PX_CAT_G1V2.csv"]
    }

    silver_crm = {
      bucket = module.silver_bucket.bucket_name
      prefix = "crm"
      db_ref = "silver"
      files = []
    }

    silver_erp = {
      bucket = module.silver_bucket.bucket_name
      prefix = "erp"
      db_ref = "silver"
      files = []
    }
  }
}