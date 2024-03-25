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

variable "bastion_subdomain" {
  description = "Subdomain for ssh tunneling server"
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

variable "bastion_ec2_host_private_key" {
  description = "Private ssh key for bastion EC2 host"
  type        = string
}

variable "bastion_ec2_host_public_key" {
  description = "Public ssh key for bastion EC2 host"
  type        = string
}

variable "bastion_ec2_user_public_key" {
  description = "Public ssh key for bastion EC2 superuser"
  type        = string
}

variable "bastion_ec2_tunnel_public_keys" {
  description = "Public ssh keys for bastion EC2 tunnel user"
  type        = list
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
  nullable = false
}

variable "hame_admin_secrets" {
  nullable = false
}

variable "hame_r_secrets" {
  nullable = false
}

variable "hame_rw_secrets" {
  nullable = false
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
  bastion_dns_alias   = "${var.prefix}.${var.bastion_subdomain}.${var.AWS_HOSTED_DOMAIN}"
  default_tags         = merge(var.extra_tags, {
    "Prefix"    = var.prefix
    "Name"      = var.prefix
    "Terraform" = "true"
  })
}
