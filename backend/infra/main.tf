terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.AWS_REGION_NAME
}

module "x-road" {
  source = "./x-road"
  for_each = var.enable_x_road ? { "this" = true } : {}

  providers = {
    aws = aws
  }

  AWS_REGION_NAME = var.AWS_REGION_NAME
  AWS_HOSTED_DOMAIN = var.AWS_HOSTED_DOMAIN

  prefix = var.prefix
  vpc_id = aws_vpc.main.id

  x-road_host = var.x-road_host
  x-road_subdomain = var.x-road_subdomain
  x-road_verification_record = var.x-road_verification_record
  x-road_member_code = var.x-road_member_code
  x-road_securityserver_image = var.x-road_securityserver_image
  x-road_instance = var.x-road_instance
  x-road_member_class = var.x-road_member_class
  x-road_securityserver_memory = var.x-road_securityserver_memory
  x-road_secrets = var.x-road_secrets
  x-road_token_pin = var.x-road_token_pin
  x-road_db_password = var.x-road_db_password
  x-road_securityserver_cpu = var.x-road_securityserver_cpu
  syke_xroad_client_id = var.syke_xroad_client_id
  syke_xroad_client_secret = var.syke_xroad_client_secret

  enable_route53_record = var.enable_route53_record
  private-subnet-count = var.private-subnet-count

  db_instance_type = var.db_instance_type
  db_storage = var.db_storage
  db_postgres_version = var.db_postgres_version
  db_parameter_group_name = aws_db_parameter_group.hame.name
  db_subnet_group_name = aws_db_subnet_group.db.name
  db_vpc_security_group_ids = [aws_security_group.rds.id]
  db_name = "${var.hame_db_name}-xroad-db"

  private_subnet_ids = aws_subnet.private.*.id
  docker_execution_role_arn = aws_iam_role.backend-task-execution.arn
  rds_security_group_id = aws_security_group.rds.id
  lambda_security_group_id = aws_security_group.lambda.id
  bastion_security_group_id = aws_security_group.bastion.id

  default_tags = local.default_tags
}
