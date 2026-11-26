resource "aws_db_instance" "xroad_db" {
  identifier             = var.db_name
  instance_class         = var.db_instance_type
  allocated_storage      = var.db_storage
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  engine                 = "postgres"
  engine_version         = var.db_postgres_version
  username               = "postgres"
  password               = var.x-road_db_password
  db_subnet_group_name   = var.db_subnet_group_name
  vpc_security_group_ids = var.db_vpc_security_group_ids
  parameter_group_name   = var.db_parameter_group_name
  multi_az               = false
  apply_immediately      = false
  publicly_accessible    = false
  skip_final_snapshot    = true
  deletion_protection    = true
  tags                   = var.default_tags
}
