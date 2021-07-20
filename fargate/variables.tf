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
  default = "376188100041.dkr.ecr.us-east-1.amazonaws.com/movie-scraper:latest"
}

# The VPC to use for the Fargate cluster
variable "vpc" {
  default  = "vpc-009dd7c9e3b6f282a"
}

# The public subnets, minimum of 2, that are a part of the VPC(s)
variable "public_subnets" {
  default = "subnet-0f19e71d2bbd71df4,subnet-086b238deaba86e43"
}

# Tasks
variable "ecs_tasks" {
  default = {
    "task1" = {
      name = "trending"
      command = "trending"
      cron = "cron(0 0 * * ? *)"
    }
    "task2" = {
      name = "trending"
      command = "recent"
      cron = "cron(0 0 * * ? *)"
    } 
  }
}
# locals

locals {
  namespace = "${var.app}-${var.environment}"
  log_group = "/fargate/task/${local.namespace}"
}

