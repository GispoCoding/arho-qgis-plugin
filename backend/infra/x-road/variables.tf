variable "AWS_REGION_NAME" {
  description = "AWS Region name."
  type        = string
  validation {
    condition     = var.AWS_REGION_NAME != null
    error_message = "AWS_REGION_NAME must not be empty."
  }
}

variable "AWS_HOSTED_DOMAIN" {
  description = "Domain for create route53 record."
  type        = string
  validation {
    condition     = var.AWS_HOSTED_DOMAIN != null
    error_message = "AWS_HOSTED_DOMAIN must not be empty."
  }
}

variable vpc_id {
  description = "VPC id where to create resources"
  type        = string
  validation {
    condition     = var.vpc_id != null
    error_message = "vpc_id must not be empty."
  }
}

variable "prefix" {
  description = "Prefix to be used in resource names"
  type        = string
  validation {
    condition     = var.prefix != null
    error_message = "prefix must not be empty"
  }
}

variable "default_tags" {
    description = "Default tags to be applied to all resources"
    type        = map(string)
    default     = {}
}

variable "syke_xroad_client_id" {
  description = "Syke client id for Ryhti X-road API client"
  type        = string
  validation {
    condition     = var.syke_xroad_client_id != null
    error_message = "syke_xroad_client_id must not be empty"
  }
}

variable "syke_xroad_client_secret" {
  description = "Syke secret for Ryhti X-road API client"
  type        = string
  validation {
    condition     = var.syke_xroad_client_secret != null
    error_message = "syke_xroad_client_secret must not be empty"
  }
}

variable "x-road_securityserver_image" {
  description = "Image for X-Road Security Server"
  default     = "docker.io/niis/xroad-security-server-sidecar:7.3.2-slim-fi"
}

variable "x-road_host" {
  description = "Host name for X-Road security server"
  type        = string
  validation {
    condition     = var.x-road_host != null
    error_message = "x-road_host must not be empty"
  }
}

variable "x-road_subdomain" {
  description = "Subdomain for X-road security server"
  type     = string
  validation {
    condition     = var.x-road_subdomain != null
    error_message = "x-road_subdomain must not be empty"
  }
}

variable "x-road_verification_record" {
  description = "Domain verification string to set for x-road DNS record"
  type     = string
  validation {
    condition     = var.x-road_verification_record != null
    error_message = "x-road_verification_record must not be empty"
  }
}

variable "x-road_instance" {
  description = "X-road instance to connect to (test or production). Default is FI-TEST."
  type     = string
  validation {
    condition     = var.x-road_instance != null
    error_message = "x-road_instance must not be empty"
  }
}

variable "x-road_member_class" {
  description = "X-road member class of your organization (government, municipality etc.). Default is MUN."
  type     = string
  validation {
    condition     = var.x-road_member_class != null
    error_message = "x-road_member_class must not be empty"
  }
}

variable "x-road_member_code" {
  description = "Member code to set for x-road client instance. Usually this is Y-tunnus of your organization."
  type     = string
  validation {
    condition     = var.x-road_member_code != null
    error_message = "x-road_member_code must not be empty"
  }
}

variable "x-road_securityserver_memory" {
  description = "Memory for X-Road Security Server"
  type        = number
  validation {
    condition     = var.x-road_securityserver_memory != null
    error_message = "x-road_securityserver_memory must not be null"
  }
}

variable "x-road_securityserver_cpu" {
  description = "CPU for X-Road Security Server"
  type        = number
  validation {
    condition     = var.x-road_securityserver_cpu != null
    error_message = "x-road_securityserver_cpu must not be null"
  }
}

variable "x-road_secrets" {
  description = "Admin username and password for X-Road Security Server"
  type        = map(string)
  validation {
    condition     = var.x-road_secrets != null
    error_message = "x-road_secrets must not be null"
  }
}

variable "x-road_db_password" {
  description = "Password for the X-Road database."
  type        = string
  validation {
    condition     = var.x-road_db_password != null
    error_message = "x-road_db_password must not be empty"
  }
}

variable "x-road_token_pin" {
  description = "PIN for accessing x-road authentication tokens"
  type        = string
  validation {
    condition     = var.x-road_token_pin != null
    error_message = "x-road_token_pin must not be empty"
  }
}

variable "enable_route53_record" {
  type    = bool
  default = false
}

variable "private-subnet-count" {
  description = "Number of private subnets created"
  type        = number
  validation {
    condition     = var.private-subnet-count != null
    error_message = "private-subnet-count must not be null"
  }
}

variable "db_instance_type" {
  description = "AWS instance type of the DB. Default: db.t3.small"
  type        = string
  validation {
    condition     = var.db_instance_type != null
    error_message = "db_instance_type must not be empty"
  }
}

variable "db_storage" {
  description = "DB Storage in GB"
  type        = number
  validation {
    condition     = var.db_storage != null
    error_message = "db_storage must not be null"
  }
}

variable "db_postgres_version" {
  description = "Version number of the PostgreSQL DB. Default: 13.20"
  type        = string
  validation {
    condition     = var.db_postgres_version != null
    error_message = "db_postgres_version must not be empty"
  }
}

variable "db_name" {
  description = "X-Road DB Name"
  type        = string
  validation {
    condition     = var.db_name != null
    error_message = "db_name must not be empty"
  }
}

variable "db_subnet_group_name" {
  description = "DB subnet group name"
  type        = string
  validation {
    condition     = var.db_subnet_group_name != null
    error_message = "db_subnet_group_name must not be empty"
  }
}

variable db_parameter_group_name {
  description = "DB parameter group name"
  type        = string
  validation {
    condition     = var.db_parameter_group_name != null
    error_message = "db_parameter_group_name must not be empty"
  }
}

variable db_vpc_security_group_ids {
  description = "List of VPC security group IDs to associate"
  type        = list(string)
  validation {
    condition     = var.db_vpc_security_group_ids != null
    error_message = "db_vpc_security_group_ids must not be null"
  }
}

variable rds_security_group_id {
    description = "RDS security group ID"
    type        = string
    validation {
      condition     = var.rds_security_group_id != null
      error_message = "rds_security_group_id must not be empty"
    }
}

variable lambda_security_group_id {
    description = "Lambda security group ID"
    type        = string
    validation {
      condition     = var.lambda_security_group_id != null
      error_message = "lambda_security_group_id must not be empty"
    }
}

variable bastion_security_group_id {
    description = "Bastion security group ID"
    type        = string
    validation {
      condition     = var.bastion_security_group_id != null
      error_message = "bastion_security_group_id must not be empty"
    }
}

variable docker_execution_role_arn {
  description = "ARN of the role that runs the docker deamon"
  type        = string
  validation {
    condition     = var.docker_execution_role_arn != null
    error_message = "docker_execution_role_arn must not be empty"
  }
}

variable private_subnet_ids {
  description = "List of private subnet IDs"
  type        = list(string)
  validation {
    condition     = var.private_subnet_ids != null
    error_message = "private_subnet_ids must not be null"
  }
}

locals {
  xroad_private_domain = "${var.x-road_subdomain}.${var.AWS_HOSTED_DOMAIN}"
  xroad_dns_record     = "${var.x-road_host}.${var.x-road_subdomain}.${var.AWS_HOSTED_DOMAIN}"
}
