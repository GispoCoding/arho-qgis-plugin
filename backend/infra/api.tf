# Lambda URLs are either public or require authentication, that won't do.
# We will need private API gateway to call ryhti client from EC2
resource "aws_api_gateway_rest_api" "lambda_api" {
  name = "${var.prefix}-lambda_api"
  description = "API gateway for calling lambda"

  endpoint_configuration {
    types = ["PRIVATE"]
    vpc_endpoint_ids = [aws_vpc_endpoint.lambda_api.id]
  }

  tags = merge(local.default_tags, {
    Name = "${var.prefix}-lambda-api"
  })
}

data "aws_iam_policy_document" "lambda_api_policy" {
  statement {
    effect = "Allow"

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    actions   = ["execute-api:Invoke"]
    resources = ["${aws_api_gateway_rest_api.lambda_api.execution_arn}/*"]
  }
  statement {
    effect = "Deny"

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    actions   = ["execute-api:Invoke"]
    resources = ["${aws_api_gateway_rest_api.lambda_api.execution_arn}/*"]

    condition {
      test     = "StringNotEquals"
      variable = "aws:SourceVpce"
      values   = [aws_vpc_endpoint.lambda_api.id]
    }
  }
}

resource "aws_api_gateway_rest_api_policy" "lambda_api_policy" {
  rest_api_id = aws_api_gateway_rest_api.lambda_api.id
  policy      = data.aws_iam_policy_document.lambda_api_policy.json
}

resource "aws_api_gateway_resource" "ryhti_client" {
  rest_api_id = aws_api_gateway_rest_api.lambda_api.id
  parent_id = aws_api_gateway_rest_api.lambda_api.root_resource_id
  path_part = "ryhti"
}

resource "aws_api_gateway_method" "ryhti_call" {
  rest_api_id = aws_api_gateway_rest_api.lambda_api.id
  resource_id = aws_api_gateway_resource.ryhti_client.id
  http_method = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda_integration" {
  rest_api_id = aws_api_gateway_rest_api.lambda_api.id
  resource_id = aws_api_gateway_resource.ryhti_client.id
  http_method = aws_api_gateway_method.ryhti_call.http_method
  integration_http_method = "POST"
  type        = "AWS_PROXY"
  # Our lambdas may run long if everything is processed. For a single
  # plan, the request will be much faster.
  timeout_milliseconds = 120000
  uri         = aws_lambda_function.ryhti_client.invoke_arn
}

resource "aws_api_gateway_deployment" "api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.lambda_api.id

  triggers = {
    redeployment = sha1(join(",",[
      jsonencode(aws_api_gateway_resource.ryhti_client),
      jsonencode(aws_api_gateway_method.ryhti_call),
      jsonencode(aws_api_gateway_integration.lambda_integration),
      data.aws_iam_policy_document.lambda_api_policy.json,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }

}

resource "aws_api_gateway_stage" "api_stage" {
  deployment_id = aws_api_gateway_deployment.api_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.lambda_api.id
  stage_name    = "v0"

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway_log_group.arn
    format = jsonencode(
      {
        requestId = "$context.requestId"
        extendedRequestId = "$context.extendedRequestId"
        ip = "$context.identity.sourceIp"
        httpMethod = "$context.httpMethod"
        path = "$context.path"
        requestTime = "$context.requestTime"
        status = "$context.status"
        responseLength = "$context.responseLength"
        domainName = "$context.domainName"
      }
    )
  }
}

resource "aws_api_gateway_method_settings" "api_stage_settings" {
  rest_api_id = aws_api_gateway_rest_api.lambda_api.id
  stage_name  = aws_api_gateway_stage.api_stage.stage_name
  method_path = "*/*"

  settings {
    logging_level = "INFO"
    data_trace_enabled = true
    metrics_enabled = true
  }
}

# We have to specify a role that has permissions to create logs
resource "aws_api_gateway_account" "api_gateway_account" {
  cloudwatch_role_arn = aws_iam_role.api-gateway-cloudwatch.arn
}
