/*
 * variables.tf
 * Common variables to use in various Terraform files (*.tf)
 */

variable "region" {
  default = "us-east-1"
}

# Tags for the infrastructure
variable "tags" {
  type = map(string)

  default = {
    "app" = "cinesnack"
  }
}

variable "schedule_expression" {
  default = "cron(0/15, * * * ? *)"
}

# The application's name
variable "app" {
  default = "cinesnack"
}

# The environment that is being built
variable "environment" {
  default = "prod"
}

variable "ecr_image" {
  default = ""
}

# The VPC to use for the Fargate cluster
variable "vpc" {
  default  = ""
}

# The public subnets, minimum of 2, that are a part of the VPC(s)
variable "public_subnets" {
  default = ""
}

# locals

locals {
  namespace = "${var.app}-${var.environment}"
  log_group = "/fargate/task/${local.namespace}"
}

