# Database secrets
resource "aws_secretsmanager_secret" "hame-db-su" {
  name = "${var.prefix}-postgres-database-su"
  tags = merge(local.default_tags, {Name = "${var.prefix}-postgres-database-su"})
}

resource "aws_secretsmanager_secret_version" "hame-db-su" {
  secret_id     = aws_secretsmanager_secret.hame-db-su.id
  secret_string = jsonencode(var.su_secrets)
}

resource "aws_secretsmanager_secret" "hame-db-admin" {
  name = "${var.prefix}-postgres-database-admin"
  tags = merge(local.default_tags, {Name = "${var.prefix}-postgres-database-admin"})
}

resource "aws_secretsmanager_secret_version" "hame-db-admin" {
  secret_id     = aws_secretsmanager_secret.hame-db-admin.id
  secret_string = jsonencode(var.hame_admin_secrets)
}

resource "aws_secretsmanager_secret" "hame-db-rw" {
  name = "${var.prefix}-postgres-database-rw"
  tags = merge(local.default_tags, {Name = "${var.prefix}-postgres-database-rw"})
}

resource "aws_secretsmanager_secret_version" "hame-db-rw" {
  secret_id     = aws_secretsmanager_secret.hame-db-rw.id
  secret_string = jsonencode(var.hame_rw_secrets)
}

resource "aws_secretsmanager_secret" "hame-db-r" {
  name = "${var.prefix}-postgres-database-r"
  tags = merge(local.default_tags, {Name = "${var.prefix}-postgres-database-r"})
}

resource "aws_secretsmanager_secret_version" "hame-db-r" {
  secret_id     = aws_secretsmanager_secret.hame-db-r.id
  secret_string = jsonencode(var.hame_r_secrets)
}
