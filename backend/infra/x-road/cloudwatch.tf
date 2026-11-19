resource "aws_cloudwatch_log_group" "x-road_securityserver" {
  name              = "/aws/ecs/${aws_ecs_task_definition.x-road_securityserver.family}"
  retention_in_days = 30
  tags = var.default_tags
}
