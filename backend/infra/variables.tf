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

variable "apigateway_subdomain" {
  description = "Subdomain for private API gateway to lambda"
  type        = string
  default     = "lambda-api"
}

variable "x-road_host" {
  description = "Host name for X-Road security server"
  type        = string
}

variable "x-road_subdomain" {
  description = "Subdomain for X-road security server"
  type     = string
}

variable "x-road_verification_record" {
  description = "Domain verification string to set for x-road DNS record"
  type     = string
}

variable "x-road_instance" {
  description = "X-road instance to connect to (test or production). Default is FI-TEST."
  type     = string
  default  = "FI-TEST"
}

variable "x-road_member_class" {
  description = "X-road member class of your organization (government, municipality etc.). Default is MUN."
  type     = string
  default  = "MUN"
}

variable "x-road_member_code" {
  description = "Member code to set for x-road client instance. Usually this is Y-tunnus of your organization."
  type     = string
}

variable "enable_route53_record" {
  type    = bool
  default = false
}

variable "SLACK_HOOK_URL" {
  description = "Slack URL to post cloudwatch notifications to"
  type        = string
}

variable "bastion_ec2_user_public_keys" {
  description = "Public ssh key for bastion EC2 superuser"
  type        = list
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
  description = "Version number of the PostgreSQL DB. Default: 13.20"
  type        = string
  default     = "13.20"
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

variable "syke_apikey" {
  description = "Syke API key for Ryhti public API client"
  type        = string
}

variable "mml_apikey" {
  description = "MML API key for MML Loader"
  type        = string
}

variable "syke_xroad_client_id" {
  description = "Syke client id for Ryhti X-road API client"
  type        = string
}

variable "syke_xroad_client_secret" {
  description = "Syke secret for Ryhti X-road API client"
  type        = string
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

variable "x-road_securityserver_cpu" {
  description = "CPU for X-Road Security Server"
  type        = number
  default     = 2048
}

variable "x-road_securityserver_memory" {
  description = "Memory for X-Road Security Server"
  type        = number
  default     = 4096
}

variable "x-road_securityserver_image" {
  description = "Image for X-Road Security Server"
  default     = "docker.io/niis/xroad-security-server-sidecar:7.3.2-slim-fi"
}

variable "x-road_secrets" {
}

variable "x-road_db_password" {
}

variable "x-road_token_pin" {
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
  bastion_dns_alias    = "${var.prefix}.${var.bastion_subdomain}.${var.AWS_HOSTED_DOMAIN}"
  apigateway_dns_record = "${var.prefix}.${var.apigateway_subdomain}.${var.AWS_HOSTED_DOMAIN}"
  xroad_private_domain = "${var.x-road_subdomain}.${var.AWS_HOSTED_DOMAIN}"
  xroad_dns_record     = "${var.x-road_host}.${var.x-road_subdomain}.${var.AWS_HOSTED_DOMAIN}"
  default_tags         = merge(var.extra_tags, {
    "Prefix"    = var.prefix
    "Name"      = var.prefix
    "Terraform" = "true"
  })
  bastion_user_data = templatefile(
    "bastion_user_data.tpl",
    {
      ec2_user_public_keys    = var.bastion_ec2_user_public_keys,
    }
  )
}
