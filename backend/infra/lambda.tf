resource "aws_lambda_function" "db_manager" {
  function_name = "${var.prefix}-db_manager"
  filename      = "../database/db_manager.zip"
  runtime       = "python3.12"
  handler       = "db_manager.handler"
  memory_size   = 128
  timeout       = 120

  role = aws_iam_role.lambda_exec.arn
  vpc_config {
    subnet_ids         = data.aws_subnets.private.ids
    security_group_ids = [aws_security_group.lambda.id]
  }

  environment {
    variables = {
      AWS_REGION_NAME     = var.AWS_REGION_NAME
      DB_INSTANCE_ADDRESS = aws_db_instance.main_db.address
      DB_MAIN_NAME        = var.hame_db_name
      DB_MAINTENANCE_NAME = "postgres"
      READ_FROM_AWS       = 1
      DB_SECRET_SU_ARN    = aws_secretsmanager_secret.hame-db-su.arn
      DB_SECRET_ADMIN_ARN = aws_secretsmanager_secret.hame-db-admin.arn
      DB_SECRET_R_ARN     = aws_secretsmanager_secret.hame-db-r.arn
      DB_SECRET_RW_ARN    = aws_secretsmanager_secret.hame-db-rw.arn
    }
  }
  tags = merge(local.default_tags, { Name = "${var.prefix}-db_manager" })
}

resource "aws_lambda_function" "koodistot_loader" {
  function_name = "${var.prefix}-koodistot_loader"
  filename      = "../database/koodistot_loader.zip"
  runtime       = "python3.12"
  handler       = "koodistot_loader.handler"
  memory_size   = 128
  timeout       = 120

  role = aws_iam_role.lambda_exec.arn
  vpc_config {
    subnet_ids         = data.aws_subnets.private.ids
    security_group_ids = [aws_security_group.lambda.id]
  }

  environment {
    variables = {
      AWS_REGION_NAME     = var.AWS_REGION_NAME
      DB_INSTANCE_ADDRESS = aws_db_instance.main_db.address
      DB_MAIN_NAME        = var.hame_db_name
      DB_MAINTENANCE_NAME = "postgres"
      READ_FROM_AWS       = 1
      DB_SECRET_ADMIN_ARN = aws_secretsmanager_secret.hame-db-admin.arn
    }
  }
  tags = merge(local.default_tags, { Name = "${var.prefix}-koodistot_loader" })
}


resource "aws_lambda_permission" "cloudwatch_call_koodistot_loader" {
    action = "lambda:InvokeFunction"
    function_name = aws_lambda_function.koodistot_loader.function_name
    principal = "events.amazonaws.com"
    source_arn = aws_cloudwatch_event_rule.lambda_koodistot.arn
}


resource "aws_lambda_function" "ryhti_client" {
  function_name = "${var.prefix}-ryhti_client"
  filename      = "../database/ryhti_client.zip"
  runtime       = "python3.12"
  handler       = "ryhti_client.handler"
  memory_size   = 128
  timeout       = 120

  role = aws_iam_role.lambda_exec.arn
  vpc_config {
    subnet_ids         = data.aws_subnets.private.ids
    security_group_ids = [aws_security_group.lambda.id]
  }

  environment {
    variables = {
      AWS_REGION_NAME     = var.AWS_REGION_NAME
      DB_INSTANCE_ADDRESS = aws_db_instance.main_db.address
      DB_MAIN_NAME        = var.hame_db_name
      DB_MAINTENANCE_NAME = "postgres"
      READ_FROM_AWS       = 1
      DB_SECRET_RW_ARN    = aws_secretsmanager_secret.hame-db-rw.arn
      SYKE_APIKEY         = var.syke_apikey
    }
  }
  tags = merge(local.default_tags, { Name = "${var.prefix}-ryhti_client" })
}


resource "aws_lambda_permission" "cloudwatch_call_ryhti_client" {
    action = "lambda:InvokeFunction"
    function_name = aws_lambda_function.ryhti_client.function_name
    principal = "events.amazonaws.com"
    source_arn = aws_cloudwatch_event_rule.ryhti_client.arn
}
