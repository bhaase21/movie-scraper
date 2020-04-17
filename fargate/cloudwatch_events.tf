resource "aws_cloudwatch_event_rule" "trending_task" {
  name = "cinesnack-trending-task"
  description = "Runs fargate task cinesnack: trending_task"
  schedule_expression = "cron(0 * * * ? *)"
}

resource "aws_cloudwatch_event_target" "trending_task" {
  rule = aws_cloudwatch_event_rule.trending_task.name
  target_id = "cinesnack-trending-task"
  arn = aws_ecs_cluster.app.arn
  role_arn = aws_iam_role.cloudwatch_events_role.arn
  input = "{}"

  ecs_target {
    task_count = 1
    task_definition_arn = aws_ecs_task_definition.getTrending.arn
    launch_type = "FARGATE"
    platform_version = "LATEST"

    network_configuration {
      assign_public_ip = true
      security_groups = [aws_security_group.nsg_task.id]
      subnets = split(",", var.public_subnets)
    }
  }

  # allow the task definition to be managed by external ci/cd system
  lifecycle {
    ignore_changes = [
      ecs_target[0].task_definition_arn,
    ]
  }
}

resource "aws_cloudwatch_event_rule" "recent_task" {
  name = "cinesnack-recent-task"
  description = "Runs fargate task cinesnack: recent_task"
  schedule_expression = "cron(0 0/6 * * ? *)"
}

resource "aws_cloudwatch_event_target" "recent_task" {
  rule = aws_cloudwatch_event_rule.recent_task.name
  target_id = "cinesnack-recent-task"
  arn = aws_ecs_cluster.app.arn
  role_arn = aws_iam_role.cloudwatch_events_role.arn
  input = "{}"

  ecs_target {
    task_count = 1
    task_definition_arn = aws_ecs_task_definition.getRecent.arn
    launch_type = "FARGATE"
    platform_version = "LATEST"

    network_configuration {
      assign_public_ip = true
      security_groups = [aws_security_group.nsg_task.id]
      subnets = split(",", var.public_subnets)
    }
  }

  # allow the task definition to be managed by external ci/cd system
  lifecycle {
    ignore_changes = [
      ecs_target[0].task_definition_arn,
    ]
  }
}

resource "aws_cloudwatch_event_rule" "future_task" {
  name = "cinesnack"
  description = "Runs fargate task cinesnack: future_task"
  schedule_expression = "cron(0 * * * ? *)"
}

resource "aws_cloudwatch_event_target" "future_task" {
  rule = aws_cloudwatch_event_rule.future_task.name
  target_id = "cinesnack"
  arn = aws_ecs_cluster.app.arn
  role_arn = aws_iam_role.cloudwatch_events_role.arn
  input = "{}"

  ecs_target {
    task_count = 1
    task_definition_arn = aws_ecs_task_definition.getFuture.arn
    launch_type = "FARGATE"
    platform_version = "LATEST"

    network_configuration {
      assign_public_ip = true
      security_groups = [aws_security_group.nsg_task.id]
      subnets = split(",", var.public_subnets)
    }
  }

  # allow the task definition to be managed by external ci/cd system
  lifecycle {
    ignore_changes = [
      ecs_target[0].task_definition_arn,
    ]
  }
}

resource "aws_cloudwatch_event_rule" "tv_task" {
  name = "cinesnack-tv-task"
  description = "Runs fargate task cinesnack: tv_task"
  schedule_expression = "cron(0 0/6 * * ? *)"
}

resource "aws_cloudwatch_event_target" "tv_task" {
  rule = aws_cloudwatch_event_rule.tv_task.name
  target_id = "cinesnack-tv-task"
  arn = aws_ecs_cluster.app.arn
  role_arn = aws_iam_role.cloudwatch_events_role.arn
  input = "{}"

  ecs_target {
    task_count = 1
    task_definition_arn = aws_ecs_task_definition.getTv.arn
    launch_type = "FARGATE"
    platform_version = "LATEST"

    network_configuration {
      assign_public_ip = true
      security_groups = [aws_security_group.nsg_task.id]
      subnets = split(",", var.public_subnets)
    }
  }

  # allow the task definition to be managed by external ci/cd system
  lifecycle {
    ignore_changes = [
      ecs_target[0].task_definition_arn,
    ]
  }
}

