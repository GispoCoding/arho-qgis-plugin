# Database secrets
resource "aws_secretsmanager_secret" "hame-db-su" {
  name = "${var.prefix}-postgres-database-su"
  tags = merge(local.default_tags, {Name = "${var.prefix}-postgres-database-su"})
}

resource "aws_secretsmanager_secret_version" "hame-db-su" {
  secret_id     = aws_secretsmanager_secret.hame-db-su.id
  secret_string = jsonencode(var.arho_su_secrets)
}

resource "aws_secretsmanager_secret" "hame-db-dba" {
  name = "${var.prefix}-postgres-database-dba"
  tags = merge(local.default_tags, {Name = "${var.prefix}-postgres-database-dba"})
}

resource "aws_secretsmanager_secret_version" "hame-db-dba" {
  secret_id     = aws_secretsmanager_secret.hame-db-dba.id
  secret_string = jsonencode(var.arho_dba_secrets)
}

# API keys. A lambda shows its environment variables to anyone who can read its
# configuration, and aws lambda commands such as update-function-code print them,
# so the lambdas get the ARN of a secret instead of the key.
resource "aws_secretsmanager_secret" "syke-apikey" {
  name = "${var.prefix}-syke-apikey"
  tags = merge(local.default_tags, {Name = "${var.prefix}-syke-apikey"})
}

resource "aws_secretsmanager_secret_version" "syke-apikey" {
  secret_id     = aws_secretsmanager_secret.syke-apikey.id
  secret_string = var.syke_apikey
}

resource "aws_secretsmanager_secret" "mml-apikey" {
  name = "${var.prefix}-mml-apikey"
  tags = merge(local.default_tags, {Name = "${var.prefix}-mml-apikey"})
}

resource "aws_secretsmanager_secret_version" "mml-apikey" {
  secret_id     = aws_secretsmanager_secret.mml-apikey.id
  secret_string = var.mml_apikey
}
