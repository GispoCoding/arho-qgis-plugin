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

# To prevent users from having issues whenever ssh tunnel server host key changes,
# we will specify a static private key for the EC2 server. This key must be saved
# in AWS KMS manually; it is not created or changed by terraform.

# resource "aws_secretsmanager_secret" "bastion-private-key" {
#   name = "${var.prefix}-bastion-ec2-host-key"
# }

# resource "aws_secretsmanager_secret_version" "previous" {
#   secret_id = aws_secretsmanager_secret.bastion-private-key.id
#   secret_string = "use constant host key saved in AWS KMS"
#   lifecycle {
#     ignore_changes = [
#       secret_string,
#       version_stages
#     ]
#   }
#   version_stages = ["AWSPREVIOUS", ]
# }

# resource "aws_secretsmanager_secret_version" "current" {
#   secret_id = aws_secretsmanager_secret.bastion-private-key.id
#   secret_string = "use constant host key saved in AWS KMS"
#   version_stages = ["AWSCURRENT", ]
#   lifecycle {
#     ignore_changes = [
#       secret_string,
#       version_stages,
#     ]
#   }
# }
