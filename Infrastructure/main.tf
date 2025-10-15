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

module "scripts_bucket" {
  source      = "./modules/s3"
  bucket_name = "srs-scripts-${random_id.suffix.hex}"
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
}

module "redshift" {
  source = "./modules/redshift"

  namespace_name     = "data-warehouse-ns"
  workgroup_name     = "data-warehouse-wg"
  db_name            = "datawarehouse"
  admin_username     = "adminuser"
  admin_password     = var.redshift_admin_password
  iam_role_arn       = module.iam.redshift_role_arn
  base_capacity      = 32
  subnet_ids         = module.vpc.private_subnet_ids

  vpc_id = module.vpc.vpc_id
  project_name = var.project_name

}