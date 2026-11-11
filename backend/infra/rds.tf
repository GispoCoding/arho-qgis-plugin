resource "aws_db_parameter_group" "hame" {
  # Make the name unique to create a new parameter group instead of modifying the existing one
  name_prefix = "${var.prefix}-params-"
  family = "postgres17"

  parameter {
    name  = "log_connections"
    value = "1"
  }
  tags = local.default_tags

  # Ensure the new group is created before the old one is destroyed
  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_db_instance" "main_db" {
  identifier             = "${var.hame_db_name}db"
  instance_class         = var.db_instance_type
  allocated_storage      = var.db_storage
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  engine                 = "postgres"
  engine_version         = var.db_postgres_version
  username               = var.arho_su_secrets.username
  password               = var.arho_su_secrets.password
  db_subnet_group_name   = aws_db_subnet_group.db.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  parameter_group_name   = aws_db_parameter_group.hame.name

  allow_major_version_upgrade = true
  multi_az               = false
  apply_immediately      = true
  publicly_accessible    = false
  skip_final_snapshot    = true
  deletion_protection    = true
  tags                   = local.default_tags
}
