resource "aws_ecs_task_definition" "getTrending" {
  family                   = "cinesnack"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecsTaskExecutionRole.arn

  # defined in role.tf
  task_role_arn = aws_iam_role.app_role.arn

  container_definitions = <<DEFINITION
[
  {
    "name": "cinesnack-trending",
    "image": "${var.ecr_image}",
    "essential": true,
    "portMappings": [],
    "environment": [],
    "entryPoint": [ "python" ],
    "command": [ "app.py", "--trending", "yes" ],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "${local.log_group}",
        "awslogs-region": "us-east-1",
        "awslogs-stream-prefix": "fargate"
      }
    }
  }
]
DEFINITION

tags = var.tags
}

resource "aws_ecs_task_definition" "getTv" {
  family                   = "cinesnack"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecsTaskExecutionRole.arn

  # defined in role.tf
  task_role_arn = aws_iam_role.app_role.arn

  container_definitions = <<DEFINITION
[
  {
    "name": "cinesnack-tv",
    "image": "${var.ecr_image}",
    "essential": true,
    "portMappings": [],
    "environment": [],
    "entryPoint": [ "python" ],
    "command": [ "app.py", "--tvpopular", "yes" ],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "${local.log_group}",
        "awslogs-region": "us-east-1",
        "awslogs-stream-prefix": "fargate"
      }
    }
  }
]
DEFINITION

  tags = var.tags
}

resource "aws_ecs_task_definition" "getFuture" {
  family                   = "cinesnack"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecsTaskExecutionRole.arn

  # defined in role.tf
  task_role_arn = aws_iam_role.app_role.arn

  container_definitions = <<DEFINITION
[
  {
    "name": "cinesnack-future",
    "image": "${var.ecr_image}",
    "essential": true,
    "portMappings": [],
    "environment": [],
    "entryPoint": [ "python" ],
    "command": [ "app.py", "--recent", "yes", "--daysback", "7", "--daysforward", "365" ],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "${local.log_group}",
        "awslogs-region": "us-east-1",
        "awslogs-stream-prefix": "fargate"
      }
    }
  }
]
DEFINITION

  tags = var.tags
}

resource "aws_ecs_task_definition" "getRecent" {
  family                   = "cinesnack"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecsTaskExecutionRole.arn

  # defined in role.tf
  task_role_arn = aws_iam_role.app_role.arn

  container_definitions = <<DEFINITION
[
  {
    "name": "cinesnack-recent",
    "image": "${var.ecr_image}",
    "essential": true,
    "portMappings": [],
    "environment": [],
    "entryPoint": [ "python" ],
    "command": [ "app.py", "--recent", "yes", "--daysback", "7", "--daysforward", "90" ],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "${local.log_group}",
        "awslogs-region": "us-east-1",
        "awslogs-stream-prefix": "fargate"
      }
    }
  }
]
DEFINITION

  tags = var.tags
}

