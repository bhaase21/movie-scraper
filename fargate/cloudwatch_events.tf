resource "aws_cloudwatch_event_rule" "task_cron" {
  for_each = var.ecs_tasks

  name = each.value["name"] 
  description = "Runs fargate task cinesnack: ${each.value["name"]}"
  schedule_expression = each.value["cron"] 
}
