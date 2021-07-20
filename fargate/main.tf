terraform {
  required_version = ">= 0.12"

  backend "s3" {
    region  = "us-east-1"
    profile = ""
    bucket  = "cinesnack-terraform-state"
    key     = "terraform.tfstate"
  }
}

provider "aws" {
#  version = ">= 1.53.0"
  region  = var.region
}
