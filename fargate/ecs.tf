/**
 * Elastic Container Service (ecs)
 * This component is required to create the Fargate ECS components. It will create a Fargate cluster
 * based on the application name and environment. It will create a "Task Definition", which is required
 * to run a Docker container, https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definitions.html.
 * It also creates a role with the correct permissions. And lastly, ensures that logs are captured in CloudWatch.
 *
 * When building for the first time, it will install the "hello-world" () image. 
 * The Fargate CLI can be used to deploy new application image on top of this infrastructure.
 */

resource "aws_ecs_cluster" "app" {
  name = "cinesnack"
  capacity_providers = ["FARGATE", "FARGATE_SPOT"]
}

# https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_execution_IAM_role.html
resource "aws_iam_role" "ecsTaskExecutionRole" {
  name = "cinesnack-ecs"
  assume_role_policy = data.aws_iam_policy_document.assume_role_policy.json
}

# allow task execution role to be assumed by ecs
data "aws_iam_policy_document" "assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

# allow task execution role to work with ecr and cw logs
resource "aws_iam_role_policy_attachment" "ecsTaskExecutionRole_policy" {
  role = aws_iam_role.ecsTaskExecutionRole.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# https://docs.aws.amazon.com/AmazonECS/latest/developerguide/CWE_IAM_role.html
resource "aws_iam_role" "cloudwatch_events_role" {
  name = "cinesnack-events"
  assume_role_policy = data.aws_iam_policy_document.events_assume_role_policy.json
}

# allow events role to be assumed by events service 
data "aws_iam_policy_document" "events_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type = "Service"
      identifiers = ["events.amazonaws.com"]
    }
  }
}

# allow events role to run ecs tasks
data "aws_iam_policy_document" "events_ecs" {
  statement {
    effect = "Allow"
    actions = ["ecs:RunTask"]
    resources = ["arn:aws:ecs:${var.region}:${data.aws_caller_identity.current.account_id}:task-definition/cinesnack-*"]

    condition {
      test = "StringLike"
      variable = "ecs:cluster"
      values = [aws_ecs_cluster.app.arn]
    }
  }
}

resource "aws_iam_role_policy" "events_ecs" {
  name = "${var.app}-${var.environment}-events-ecs"
  role = aws_iam_role.cloudwatch_events_role.id
  policy = data.aws_iam_policy_document.events_ecs.json
}

# allow events role to pass role to task execution role and app role
data "aws_iam_policy_document" "passrole" {
  statement {
    effect = "Allow"
    actions = ["iam:PassRole"]

    resources = [
      aws_iam_role.app_role.arn,
      aws_iam_role.ecsTaskExecutionRole.arn,
    ]
  }
}

resource "aws_iam_role_policy" "events_ecs_passrole" {
  name = "${var.app}-${var.environment}-events-ecs-passrole"
  role = aws_iam_role.cloudwatch_events_role.id
  policy = data.aws_iam_policy_document.passrole.json
}

variable "logs_retention_in_days" {
  type        = number
  default     = 7 
  description = "Specifies the number of days you want to retain log events"
}

resource "aws_cloudwatch_log_group" "logs" {
  name = local.log_group
  retention_in_days = var.logs_retention_in_days
  tags = var.tags
}
