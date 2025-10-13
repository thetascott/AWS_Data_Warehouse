terraform {
  required_version = ">= 1.13.1"

  backend "s3" {
    bucket         = "srs-terraform-0012"
    key            = "terraform.tfstate"
    region         = "us-east-2"
    encrypt        = true
  }
}