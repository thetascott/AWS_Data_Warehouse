output "vpc_id" {
  value = module.vpc.vpc_id
}

output "public_subnets" {
  value = module.vpc.public_subnets
}

output "private_subnets" {
  value = module.vpc.private_subnets
}

output "bronze_bucket_name" {
  value = module.bronze_bucket.bucket_name
}

output "silver_bucket_name" {
  value = module.silver_bucket.bucket_name
}

output "scripts_bucket_name" {
  value = module.scripts_bucket.bucket_name
}

output "glue_role_arn" {
  value = module.iam.glue_role_arn
}

output "redshift_role_arn" {
  value = module.iam.redshift_role_arn
}