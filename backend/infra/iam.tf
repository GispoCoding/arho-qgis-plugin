
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


# Lambda update user
resource "aws_iam_user" "lambda_update_user" {
  name               = var.AWS_LAMBDA_USER
  tags               = merge(local.default_tags, { Name = "${var.prefix}_lambda_update" })
}

# Create the policy to update lambda functions
resource "aws_iam_policy" "lambda_update_policy" {
  # We need a separate policy for each hame instance, since they have separate lambda functions
  name        = "${var.prefix}-lambda_update_policy"
  path        = "/"
  description = "Github CI lambda update policy"

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : [
          "lambda:CreateFunction",
          "lambda:UpdateFunctionCode",
          "lambda:InvokeFunction",
          "lambda:UpdateFunctionConfiguration"
        ],
        "Resource" : [
          aws_lambda_function.db_manager.arn,
          aws_lambda_function.koodistot_loader.arn
          ]
      }
    ]
  })
  tags   = merge(local.default_tags, { Name = "${var.prefix}-lambda_update_policy" })
}

resource "aws_iam_policy_attachment" "lambda_update_attachment" {
  name       = "${var.prefix}-lambda_update_attachment"
  users      = [aws_iam_user.lambda_update_user.name]
  policy_arn = aws_iam_policy.lambda_update_policy.arn
}

#
# Bastion
#

# Adding a role for the EC2 machine allows making AWS service APIs available via IAM policies
resource "aws_iam_role" "ec2-role" {
  name               = "${var.prefix}-ec2-iam-role"
  path               = "/"
  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": "sts:AssumeRole",
            "Principal": {
               "Service": "ec2.amazonaws.com"
            },
            "Effect": "Allow",
            "Sid": ""
        }
    ]
}
EOF

  tags = merge(local.default_tags, {
    Name = "${var.prefix}-ec2-iam-role"
  })
}

resource "aws_iam_instance_profile" "ec2-iam-profile" {
  name = "${var.prefix}-ec2-iam-profile"
  role = aws_iam_role.ec2-role.name
}

resource "aws_iam_role_policy_attachment" "ssm-policy-attachment" {
  role       = aws_iam_role.ec2-role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}
