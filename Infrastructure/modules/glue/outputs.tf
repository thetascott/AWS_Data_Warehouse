output "database_names" {
  value = { for k, v in aws_glue_catalog_database.glue_database : k => v.name }
}