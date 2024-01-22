
# Lambda role
resource "aws_iam_role" "lambda_exec" {
  # Separate roles for each hame instance
  name               = "${var.prefix}_serverless_lambda"
  assume_role_policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Sid       = ""
        Principal = { Service = "lambda.amazonaws.com" }
      }
    ]
  })
  tags               = merge(local.default_tags, { Name = "${var.prefix}_serverless_lambda" })
}

resource "aws_iam_role_policy_attachment" "lambda_policy" {
  role       = aws_iam_role.lambda_exec.name
  # Lambda must have rights to connect to VPC
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

# Create the policy to access secrets manager in the region
resource "aws_iam_policy" "secrets-policy" {
  # We need a separate policy for each hame instance, since they have separate secrets
  name        = "${var.prefix}-lambda-secrets-policy"
  path        = "/"
  description = "Lambda db secrets policy"

  policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [
      {
        Action   = [
          "secretsmanager:GetResourcePolicy",
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret",
          "secretsmanager:ListSecretVersionIds"
        ],
        Effect   = "Allow",
        Resource = [
          aws_secretsmanager_secret.hame-db-su.arn,
          aws_secretsmanager_secret.hame-db-admin.arn,
          aws_secretsmanager_secret.hame-db-rw.arn,
          aws_secretsmanager_secret.hame-db-r.arn
        ]
      }
    ]
  })
  tags   = merge(local.default_tags, { Name = "${var.prefix}-lambda-secrets-policy" })
}

resource "aws_iam_role_policy_attachment" "lambda_secrets_attachment" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = aws_iam_policy.secrets-policy.arn
}
