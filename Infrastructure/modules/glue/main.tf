# Create Glue Catalog Databases
resource "aws_glue_catalog_database" "glue_database" {
  for_each = var.databases

  name        = each.value.db_name
  description = lookup(each.value, "description", null)
  location_uri = lookup(each.value, "location_uri", null)
  parameters   = lookup(each.value, "parameters", null)
}

locals {
  s3_targets = {
    for k, crawler in var.crawlers : k => (
      length(lookup(crawler, "files", [])) > 0 ?
      [for f in crawler.files : "s3://${crawler.bucket}/${crawler.prefix}/${f}"] :
      ["s3://${crawler.bucket}/${crawler.prefix}/"]
    )
  }
}

resource "aws_glue_classifier" "cust_az12_csv" {
  name = "cust_az12_csv_classifier"

  csv_classifier {
    allow_single_column    = true
    contains_header        = "PRESENT"
    delimiter              = ","
    quote_symbol           = "\""
    disable_value_trimming = false
    header = ["CID", "BDATE", "GEN"]
  }
}

resource "aws_glue_classifier" "loc_a101_csv" {
  name = "loc_a101_csv_classifier"

  csv_classifier {
    allow_single_column    = true
    contains_header        = "PRESENT"
    delimiter              = ","
    quote_symbol           = "\""
    disable_value_trimming = false
    header = ["CID", "CNTRY"]
  }
}

resource "aws_glue_classifier" "px_cat_g1v2csv" {
  name = "px_cat_g1v2_csv_classifier"

  csv_classifier {
    allow_single_column    = true
    contains_header        = "PRESENT"
    delimiter              = ","
    quote_symbol           = "\""
    disable_value_trimming = false
    header = ["ID", "CAT", "SUBCAT", "MAINTENANCE"]
  }
}

resource "aws_glue_crawler" "bronze" {
  for_each = var.crawlers

  name          = "${var.project_name}-${each.key}-crawler"
  role          = var.glue_role_arn
  database_name = aws_glue_catalog_database.glue_database[each.value.db_ref].name

  dynamic "s3_target" {
    for_each = local.s3_targets[each.key]

    content {
      path = s3_target.value
    }
  }

  classifiers = [
    aws_glue_classifier.cust_az12_csv.name,
    aws_glue_classifier.loc_a101_csv.name,
    aws_glue_classifier.px_cat_g1v2csv.name
  ]
}