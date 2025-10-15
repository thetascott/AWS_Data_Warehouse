 variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-2"
}

variable "project_name" {
  description = "Project name used for tagging"
  type        = string
  default     = "TastyTrade"
}

 variable "public_subnets" {
  description = "Map of public subnets with CIDR and AZ"
  type = map(object({
    cidr = string
    az   = string
  }))
  default = {
    "public-subnet-1" = { cidr = "10.0.1.0/24", az = "us-east-2a" }
    "public-subnet-2" = { cidr = "10.0.2.0/24", az = "us-east-2b" }
  }
}

variable "private_subnets" {
  description = "Map of private subnets with CIDR and AZ"
  type = map(object({
    cidr = string
    az   = string
  }))
  default = {
    "private-subnet-1" = { cidr = "10.0.101.0/24", az = "us-east-2a" }
    "private-subnet-2" = { cidr = "10.0.102.0/24", az = "us-east-2b" }
  }
}

variable "redshift_admin_password" {
  description = "Admin password for Redshift Serverless"
  type        = string
  sensitive   = true
}