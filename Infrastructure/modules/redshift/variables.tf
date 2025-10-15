variable "project_name" {
  description = "Project name prefix for resource naming"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where Redshift resides"
  type        = string
}

variable "namespace_name" { 
  type = string 

}
variable "workgroup_name" { 
  type = string 
}
variable "db_name"        { 
  type = string 
}
variable "admin_username" { 
  type = string 
}
variable "admin_password" { 
  type = string 
}
variable "iam_role_arn"   { 
  type = string 
}
variable "base_capacity"  { 
  type = number 
}
variable "subnet_ids"     { 
  type = list(string) 
}