resource "aws_ecs_task_definition" "task" {
  for_each = var.ecs_tasks 
  family                   = each.value["name"] 
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
    "name": "${each.value["name"]}",
    "image": "${var.ecr_image}",
    "essential": true,
    "portMappings": [],
    "environment": [],
    "entryPoint": [ "python" ],
    "command": [ "app.py", "${each.value["command"]}" ],
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
