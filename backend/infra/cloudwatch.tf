resource "aws_cloudwatch_log_group" "lambda_db_manager" {
  name              = "/aws/lambda/${aws_lambda_function.db_manager.function_name}"
  retention_in_days = 30
  tags = local.default_tags
}

resource "aws_cloudwatch_log_group" "lambda_koodistot_loader" {
  name              = "/aws/lambda/${aws_lambda_function.koodistot_loader.function_name}"
  retention_in_days = 30
  tags = local.default_tags
}

resource "aws_cloudwatch_log_group" "x-road_securityserver" {
  name              = "/aws/ecs/${aws_ecs_task_definition.x-road_securityserver.family}"
  retention_in_days = 30
  tags = local.default_tags
}

resource "aws_cloudwatch_event_rule" "lambda_koodistot" {
  name        = "${var.prefix}-lambda-koodistot-update"
  description = "Run koodistot import every night"
  schedule_expression = "cron(0 4 * * ? *)"
  tags              = local.default_tags
}

resource "aws_cloudwatch_event_target" "lambda_koodistot" {
  target_id = "${var.prefix}_load_koodistot"
  rule      = aws_cloudwatch_event_rule.lambda_koodistot.name
  arn       = aws_lambda_function.koodistot_loader.arn
  input     = "{}"
}
