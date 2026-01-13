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
