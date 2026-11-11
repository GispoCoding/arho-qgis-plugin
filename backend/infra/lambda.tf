resource "aws_lambda_function" "db_manager" {
  function_name = "${var.prefix}-db_manager"
  image_uri     = "${aws_ecr_repository.db_manager.repository_url}:latest"
  package_type  = "Image"
  timeout       = 120

  role = aws_iam_role.lambda_exec.arn
  vpc_config {
    subnet_ids         = aws_subnet.private[*].id
    security_group_ids = [aws_security_group.lambda.id]
  }
  logging_config {
    log_format            = "JSON"
    application_log_level = "INFO"
    system_log_level      = "INFO"
  }
  environment {
    variables = {
      AWS_REGION_NAME     = var.AWS_REGION_NAME
      DB_INSTANCE_ADDRESS = aws_db_instance.main_db.address
      DB_INSTANCE_PORT    = 5432
      DB_MAIN_NAME        = var.hame_db_name
      DB_MAINTENANCE_NAME = "postgres"
      READ_FROM_AWS       = 1
      DB_SECRET_SU_ARN    = aws_secretsmanager_secret.hame-db-su.arn
      DB_SECRET_DBA_ARN   = aws_secretsmanager_secret.hame-db-dba.arn
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
    subnet_ids         = aws_subnet.private[*].id
    security_group_ids = [aws_security_group.lambda.id]
  }
  logging_config {
    log_format            = "JSON"
    application_log_level = "INFO"
    system_log_level      = "INFO"
  }
  environment {
    variables = {
      AWS_REGION_NAME     = var.AWS_REGION_NAME
      DB_INSTANCE_ADDRESS = aws_db_instance.main_db.address
      DB_INSTANCE_PORT    = 5432
      DB_MAIN_NAME        = var.hame_db_name
      READ_FROM_AWS       = 1
      DB_SECRET_DBA_ARN   = aws_secretsmanager_secret.hame-db-dba.arn
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
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.koodistot_loader.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.lambda_koodistot.arn
}


resource "aws_lambda_function" "ryhti_client" {
  function_name = "${var.prefix}-ryhti_client"
  image_uri     = "${aws_ecr_repository.ryhti_client.repository_url}:latest"
  package_type  = "Image"
  # 1769 MB is the point where lambda gives a full vCPU. Serializing a large plan is
  # single threaded CPU work, so more memory than this would not help.
  memory_size = 1769
  timeout     = local.ryhti_client_timeout_seconds
  # Provisioned concurrency cannot be attached to $LATEST, so every apply must
  # publish a numbered version for the live alias to point at.
  publish = true

  role = aws_iam_role.ryhti_client_exec.arn
  vpc_config {
    subnet_ids         = aws_subnet.private[*].id
    security_group_ids = [aws_security_group.lambda.id]
  }
  logging_config {
    log_format            = "JSON"
    application_log_level = "INFO"
    system_log_level      = "INFO"
  }
  environment {
    variables = local.ryhti_client_env
  }
  tags = merge(local.default_tags, { Name = "${var.prefix}-ryhti_client" })

  # Lambda checks the VPC access of the role when it creates or updates the
  # function, and the cold start reads the secrets. The attachments are not
  # referenced above, so name them here. The self-invoke policy cannot be
  # listed: it refers to this function.
  depends_on = [
    aws_iam_role_policy_attachment.ryhti_client_vpc_access,
    aws_iam_role_policy_attachment.ryhti_client_secrets,
  ]
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
  function_name    = aws_lambda_function.ryhti_client.function_name
  function_version = aws_lambda_function.ryhti_client.version

  lifecycle {
    # The deploy Makefile publishes new versions and moves this alias with
    # the AWS CLI. Do not let terraform roll the alias back to the version
    # it saw last.
    ignore_changes = [function_version]
  }
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
  # The API gateway invokes the live alias, so the permission must be
  # attached to the alias, not to the unqualified function.
  qualifier = aws_lambda_alias.ryhti_client_live.name
  principal = "apigateway.amazonaws.com"
  # The /* part allows invocation from any stage, method and resource path
  # within API Gateway.
  source_arn = "${aws_api_gateway_rest_api.lambda_api.execution_arn}/*"
}

# A job runs on the qualifier its submit call was invoked with: the live alias
# through the API gateway, the unpublished version for a direct invoke. AWS must
# not retry a failed job, so that a half-done import never runs a second time.
# AWS still retries a throttled event for up to 6 hours by default, so the event
# is dropped at the job time limit instead: get_job already reports the job as
# failed by then, and the job is never started later.
resource "aws_lambda_function_event_invoke_config" "ryhti_client_live" {
  function_name                = aws_lambda_function.ryhti_client.function_name
  qualifier                    = aws_lambda_alias.ryhti_client_live.name
  maximum_retry_attempts       = 0
  maximum_event_age_in_seconds = local.ryhti_client_timeout_seconds
}

resource "aws_lambda_function_event_invoke_config" "ryhti_client_latest" {
  function_name                = aws_lambda_function.ryhti_client.function_name
  qualifier                    = "$LATEST"
  maximum_retry_attempts       = 0
  maximum_event_age_in_seconds = local.ryhti_client_timeout_seconds
}

resource "aws_lambda_function" "mml_loader" {
  function_name = "${var.prefix}-mml_loader"
  image_uri     = "${aws_ecr_repository.mml_loader.repository_url}:latest"
  package_type  = "Image"
  # The loader downloads the whole-Finland boundary GML and parses it in memory.
  # The 128 MB default is not enough for that. 1769 MB also gives one full vCPU.
  memory_size = 1769
  timeout     = 120

  role = aws_iam_role.lambda_exec.arn
  vpc_config {
    subnet_ids         = aws_subnet.private[*].id
    security_group_ids = [aws_security_group.lambda.id]
  }
  logging_config {
    log_format            = "JSON"
    application_log_level = "INFO"
    system_log_level      = "INFO"
  }
  environment {
    variables = {
      AWS_REGION_NAME       = var.AWS_REGION_NAME
      DB_INSTANCE_ADDRESS   = aws_db_instance.main_db.address
      DB_INSTANCE_PORT      = 5432
      DB_MAIN_NAME          = var.hame_db_name
      READ_FROM_AWS         = 1
      DB_SECRET_DBA_ARN     = aws_secretsmanager_secret.hame-db-dba.arn
      MML_APIKEY_SECRET_ARN = aws_secretsmanager_secret.mml-apikey.arn
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
  # Long actions run as background jobs, so allow the Lambda maximum. A job that
  # is still queued or running after this long has crashed, so the same value
  # is the job time limit.
  ryhti_client_timeout_seconds = 900
  ryhti_client_job_environment = {
    JOB_RUNNER             = "lambda"
    JOB_TIME_LIMIT_SECONDS = local.ryhti_client_timeout_seconds
  }
  ryhti_client_base_environment = {
    AWS_REGION_NAME        = var.AWS_REGION_NAME
    DB_INSTANCE_ADDRESS    = aws_db_instance.main_db.address
    DB_INSTANCE_PORT       = 5432
    DB_MAIN_NAME           = var.hame_db_name
    READ_FROM_AWS          = 1
    SYKE_APIKEY_SECRET_ARN = aws_secretsmanager_secret.syke-apikey.arn
    DB_SECRET_DBA_ARN      = aws_secretsmanager_secret.hame-db-dba.arn
    PROJECT_SRID           = var.project_srid
    RYHTI_FILES_BUCKET     = aws_s3_bucket.ryhti_files.id
  }
  ryhti_client_x-road_environment = var.enable_x_road ? {
    XROAD_SERVER_ADDRESS         = module.x-road["this"].dns_record
    XROAD_INSTANCE               = module.x-road["this"].instance
    XROAD_MEMBER_CLASS           = module.x-road["this"].member_class
    XROAD_MEMBER_CODE            = module.x-road["this"].member_code
    XROAD_MEMBER_CLIENT_NAME     = module.x-road["this"].subdomain
    XROAD_SYKE_CLIENT_ID         = module.x-road["this"].client_id
    XROAD_SYKE_CLIENT_SECRET_ARN = module.x-road["this"].client_secret_arn
  } : {}
  ryhti_client_env = merge(
    local.ryhti_client_base_environment,
    local.ryhti_client_job_environment,
    local.ryhti_client_x-road_environment
  )
}
