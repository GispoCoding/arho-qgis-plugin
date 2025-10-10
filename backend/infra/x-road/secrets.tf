
resource "aws_secretsmanager_secret" "xroad-db-pwd" {
  name = "${var.prefix}-xroad-postgres-database-su"
  tags = merge(var.default_tags, {Name = "${var.prefix}-xroad-postgres-database-su"})
}

resource "aws_secretsmanager_secret_version" "xroad-db-pwd" {
  secret_id     = aws_secretsmanager_secret.xroad-db-pwd.id
  secret_string = jsonencode(var.x-road_db_password)
}

# Ryhti X-Road API client secret

resource "aws_secretsmanager_secret" "syke-xroad-client-secret" {
  name = "${var.prefix}-syke-xroad-client-secret"
  tags = merge(var.default_tags, {Name = "${var.prefix}-syke-xroad-client-secret"})
}

resource "aws_secretsmanager_secret_version" "syke-xroad-client-secret" {
  secret_id     = aws_secretsmanager_secret.syke-xroad-client-secret.id
  secret_string = var.syke_xroad_client_secret
}
