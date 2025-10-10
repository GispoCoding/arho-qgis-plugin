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
  count = var.enable_x_road  ? 1 : 0

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


moved {
  from = aws_cloudwatch_log_group.x-road_securityserver
  to = module.x-road[0].aws_cloudwatch_log_group.x-road_securityserver
}

moved {
  from = aws_route53_record.xroad-verification
  to = module.x-road[0].aws_route53_record.xroad-verification
}

moved {
  from = aws_service_discovery_private_dns_namespace.private
  to = module.x-road[0].aws_service_discovery_private_dns_namespace.private
}

moved {
  from = aws_service_discovery_service.x-road_securityserver
  to = module.x-road[0].aws_service_discovery_service.x-road_securityserver
}

moved {
  from = aws_ecs_task_definition.x-road_securityserver
  to = module.x-road[0].aws_ecs_task_definition.x-road_securityserver
}

moved {
  from = aws_db_instance.xroad_db
  to = module.x-road[0].aws_db_instance.xroad_db
}

moved {
  from = aws_ecs_cluster.x-road_securityserver
  to = module.x-road[0].aws_ecs_cluster.x-road_securityserver
}

moved {
  from = aws_ecs_service.x-road_securityserver
  to = module.x-road[0].aws_ecs_service.x-road_securityserver
}

moved {
  from = aws_efs_file_system.x-road_archive_volume
  to = module.x-road[0].aws_efs_file_system.x-road_archive_volume
}

moved {
  from = aws_efs_file_system.x-road_configuration_volume
  to = module.x-road[0].aws_efs_file_system.x-road_configuration_volume
}

moved {
  from = aws_efs_mount_target.x-road_archive_volume
  to = module.x-road[0].aws_efs_mount_target.x-road_archive_volume
}

moved {
  from = aws_efs_mount_target.x-road_configuration_volume
  to = module.x-road[0].aws_efs_mount_target.x-road_configuration_volume
}

moved {
  from = aws_secretsmanager_secret.syke-xroad-client-secret
  to = module.x-road[0].aws_secretsmanager_secret.syke-xroad-client-secret
}

moved {
  from = aws_secretsmanager_secret.xroad-db-pwd
  to = module.x-road[0].aws_secretsmanager_secret.xroad-db-pwd
}

moved {
  from = aws_secretsmanager_secret_version.syke-xroad-client-secret
  to = module.x-road[0].aws_secretsmanager_secret_version.syke-xroad-client-secret
}

moved {
  from = aws_secretsmanager_secret_version.xroad-db-pwd
  to = module.x-road[0].aws_secretsmanager_secret_version.xroad-db-pwd
}

moved {
  from = aws_security_group.x-road
  to = module.x-road[0].aws_security_group.x-road
}

moved {
  from = aws_security_group_rule.bastion-x-road
  to = module.x-road[0].aws_security_group_rule.bastion-x-road
}

moved {
  from = aws_security_group_rule.lambda-x-road
  to = module.x-road[0].aws_security_group_rule.lambda-x-road
}

moved {
  from = aws_security_group_rule.rds-x-road
  to = module.x-road[0].aws_security_group_rule.rds-x-road
}

moved {
  from = aws_security_group_rule.x-road-filesystem
  to = module.x-road[0].aws_security_group_rule.x-road-filesystem
}
