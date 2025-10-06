output "database_names" {
  value = { for k, v in aws_glue_catalog_database.glue_database : k => v.name }
}

# ARNs of all crawlers
output "crawler_arns" {
  description = "Map of Glue crawler ARNs created"
  value       = { for k, v in aws_glue_crawler.bronze : k => v.arn }
}

# Names of all crawlers
output "crawler_names" {
  description = "Map of Glue crawler names created"
  value       = { for k, v in aws_glue_crawler.bronze : k => v.name }
}