variable "project_name" {
  description = "Prefix for naming Glue resources"
  type        = string
}

variable "glue_role_arn" {
  description = "IAM role ARN used by Glue crawlers"
  type        = string
}

variable "databases" {
  description = "Map of Glue databases to create"
  type = map(object({
    db_name     = string
    description = optional(string)
    location_uri = optional(string)
    parameters  = optional(map(string))
  }))
}

variable "crawlers" {
  description = "Crawler configs: bucket, prefix, db ref, and optional file list"
  type = map(object({
    bucket   = string
    prefix   = string
    db_ref   = string
    files    = optional(list(string), []) # empty list = crawl entire folder
  }))
}