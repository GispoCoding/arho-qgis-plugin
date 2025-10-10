resource "aws_lambda_function" "db_manager" {
  function_name = "${var.prefix}-db_manager"
  image_uri     = "${aws_ecr_repository.db_manager.repository_url}:latest"
  package_type  = "Image"
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

resource "aws_ecr_repository" "db_manager" {
  name                 = "${var.prefix}-db_manager"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = merge(local.default_tags, { Name = "${var.prefix}-db_manager" })
}

resource "aws_lambda_function" "koodistot_loader" {
  function_name = "${var.prefix}-koodistot_loader"
  image_uri     = "${aws_ecr_repository.koodistot_loader.repository_url}:latest"
  package_type  = "Image"
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

resource "aws_ecr_repository" "koodistot_loader" {
  name                 = "${var.prefix}-koodistot_loader"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
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
  image_uri     = "${aws_ecr_repository.ryhti_client.repository_url}:latest"
  package_type  = "Image"
  memory_size   = 256
  timeout       = 120

  role = aws_iam_role.lambda_exec.arn
  vpc_config {
    subnet_ids         = data.aws_subnets.private.ids
    security_group_ids = [aws_security_group.lambda.id]
  }

  environment {
    variables = local.ryhti_client_env
  }
  tags = merge(local.default_tags, { Name = "${var.prefix}-ryhti_client" })
}

resource "aws_ecr_repository" "ryhti_client" {
  name                 = "${var.prefix}-ryhti_client"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = merge(local.default_tags, { Name = "${var.prefix}-ryhti_client" })
}

# For reasons unknown, provisioned concurrency requires an alias and qualifier
# for lambda function, just for the fun of it. $LATEST is not an alias itself.
resource "aws_lambda_alias" "ryhti_client_live" {
  name             = "live"
  description      = "Alias to latest ryhti client"
  function_name    = "${var.prefix}-ryhti_client"
  function_version = aws_lambda_function.ryhti_client.version
}

resource "aws_lambda_provisioned_concurrency_config" "ryhti_client" {
  function_name = aws_lambda_alias.ryhti_client_live.function_name
  # Assume only one run at a time for now
  provisioned_concurrent_executions = 1
  # Should we use ARN, it changes with every lambda deploy?
  qualifier = aws_lambda_alias.ryhti_client_live.name
}

resource "aws_lambda_permission" "api_gateway_call_ryhti_client" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ryhti_client.function_name
  principal     = "apigateway.amazonaws.com"
  # The /* part allows invocation from any stage, method and resource path
  # within API Gateway.
  source_arn = "${aws_api_gateway_rest_api.lambda_api.execution_arn}/*"
}

resource "aws_lambda_function" "mml_loader" {
  function_name = "${var.prefix}-mml_loader"
  image_uri     = "${aws_ecr_repository.mml_loader.repository_url}:latest"
  package_type  = "Image"
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
      DB_SECRET_ADMIN_ARN    = aws_secretsmanager_secret.hame-db-admin.arn
      MML_APIKEY          = var.mml_apikey
    }
  }
  tags = merge(local.default_tags, { Name = "${var.prefix}-mml_loader" })
}

resource "aws_ecr_repository" "mml_loader" {
  name                 = "${var.prefix}-mml_loader"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = merge(local.default_tags, { Name = "${var.prefix}-mml_loader" })
}

locals {
  ryhti_client_base_environment = {
      AWS_REGION_NAME     = var.AWS_REGION_NAME
      DB_INSTANCE_ADDRESS = aws_db_instance.main_db.address
      DB_MAIN_NAME        = var.hame_db_name
      DB_MAINTENANCE_NAME = "postgres"
      READ_FROM_AWS       = 1
      DB_SECRET_RW_ARN    = aws_secretsmanager_secret.hame-db-rw.arn
      SYKE_APIKEY         = var.syke_apikey
  }
  ryhti_client_x-road_environment = var.enable_x_road ?{
      XROAD_SERVER_ADDRESS = local.xroad_dns_record
      XROAD_INSTANCE = module.x-road[0].instance
      XROAD_MEMBER_CLASS = module.x-road[0].member_class
      XROAD_MEMBER_CODE   = module.x-road[0].member_code
      XROAD_MEMBER_CLIENT_NAME = module.x-road[0].subdomain
      XROAD_SYKE_CLIENT_ID = module.x-road[0].client_id
      XROAD_SYKE_CLIENT_SECRET_ARN = module.x-road[0].client_secret_arn
  } : {}
  ryhti_client_env = merge(
    local.ryhti_client_base_environment,
    local.ryhti_client_x-road_environment
  )
}
