variable "AWS_REGION_NAME" {
  description = "AWS Region name."
  type        = string
}

variable "AWS_LAMBDA_USER" {
  description = "AWS user for updating lambda functions"
  type        = string
}

variable "AWS_HOSTED_DOMAIN" {
  description = "Domain for create route53 record."
  type        = string
}

variable "enable_route53_record" {
  type    = bool
  default = false
}

variable "SLACK_HOOK_URL" {
  description = "Slack URL to post cloudwatch notifications to"
  type        = string
}

variable "bastion_public_key" {
  description = "Public ssh key to access the bastion EC2 instance"
  type        = string
}

variable "db_storage" {
  description = "DB Storage in GB"
  type        = number
  default     = 15
}

variable "db_instance_type" {
  description = "AWS instance type of the DB. Default: db.t3.small"
  type        = string
  default     = "db.t3.small"
}

variable "db_postgres_version" {
  description = "Version number of the PostgreSQL DB. DEfault: 13.10"
  type        = string
  default     = "13.10"
}

variable "hame_db_name" {
  description = "Hame DB Name"
  type        = string
  default     = "db"
}

variable "su_secrets" {
  default = {
    "username" = "postgres",
    "password" = "postgres"
  }
}

variable "hame_admin_secrets" {
  default = {
    "username" = "hame_admin",
    "password" = "hame_admin"
  }
}

variable "hame_r_secrets" {
  default = {
    "username" = "hame_read",
    "password" = "hame_read"
  }
}

variable "hame_rw_secrets" {
  default = {
    "username" = "hame_read_write",
    "password" = "hame_read_write"
  }
}

variable "public-subnet-count" {
  description = "TODO"
  type        = number
  default     = 2
}

variable "private-subnet-count" {
  description = "TODO"
  type        = number
  default     = 2
}

variable "prefix" {
  description = "Prefix to be used in resource names"
  type        = string
}

variable "extra_tags" {
  description = "Some extra tags for all resources. Use JSON format"
  type        = any
  default     = {}
}

locals {
  default_tags         = merge(var.extra_tags, {
    "Prefix"    = var.prefix
    "Name"      = var.prefix
    "Terraform" = "true"
  })
}
