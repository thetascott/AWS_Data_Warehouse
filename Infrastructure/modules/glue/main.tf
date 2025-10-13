# Create Glue Catalog Databases
resource "aws_glue_catalog_database" "glue_database" {
  for_each = var.databases

  name        = each.value.db_name
  description = lookup(each.value, "description", null)
  location_uri = lookup(each.value, "location_uri", null)
  parameters   = lookup(each.value, "parameters", null)
}