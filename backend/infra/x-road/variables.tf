variable "AWS_REGION_NAME" {
  description = "AWS Region name."
  type        = string
}

variable "AWS_HOSTED_DOMAIN" {
  description = "Domain for create route53 record."
  type        = string
}

variable vpc_id {
  description = "VPC id where to create resources"
  type        = string
}

variable "prefix" {
  description = "Prefix to be used in resource names"
  type        = string
}

variable "default_tags" {
    description = "Default tags to be applied to all resources"
    type        = map(string)
}

variable "syke_xroad_client_id" {
  description = "Syke client id for Ryhti X-road API client"
  type        = string
}

variable "syke_xroad_client_secret" {
  description = "Syke secret for Ryhti X-road API client"
  type        = string
}

variable "x-road_securityserver_image" {
  description = "Image for X-Road Security Server"
  default     = "docker.io/niis/xroad-security-server-sidecar:7.3.2-slim-fi"
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
}

variable "x-road_member_class" {
  description = "X-road member class of your organization (government, municipality etc.). Default is MUN."
  type     = string
}

variable "x-road_member_code" {
  description = "Member code to set for x-road client instance. Usually this is Y-tunnus of your organization."
  type     = string
}

variable "x-road_securityserver_memory" {
  description = "Memory for X-Road Security Server"
  type        = number
}

variable "x-road_securityserver_cpu" {
  description = "CPU for X-Road Security Server"
  type        = number
}

variable "x-road_secrets" {
  description = "Admin username and password for X-Road Security Server"
  type        = map(string)
}

variable "x-road_db_password" {
  description = "Password for the X-Road database."
  type        = string
}

variable "x-road_token_pin" {
  description = "PIN for accessing x-road authentication tokens"
  type        = string
}

variable "enable_route53_record" {
  type    = bool
  default = false
}

variable "private-subnet-count" {
  description = "Number of private subnets created"
  type        = number
}

variable "db_instance_type" {
  description = "AWS instance type of the DB. Default: db.t3.small"
  type        = string
}

variable "db_storage" {
  description = "DB Storage in GB"
  type        = number
}

variable "db_postgres_version" {
  description = "Version number of the PostgreSQL DB. Default: 13.20"
  type        = string
}

variable "db_name" {
  description = "X-Road DB Name"
  type        = string
}

variable "db_subnet_group_name" {
  description = "DB subnet group name"
  type        = string
}

variable db_parameter_group_name {
  description = "DB parameter group name"
  type        = string
}

variable db_vpc_security_group_ids {
  description = "List of VPC security group IDs to associate"
  type        = list(string)
}

variable rds_security_group_id {
    description = "RDS security group ID"
    type        = string
}

variable lambda_security_group_id {
    description = "Lambda security group ID"
    type        = string
}

variable bastion_security_group_id {
    description = "Bastion security group ID"
    type        = string
}

variable docker_execution_role_arn {
  description = "ARN of the role that runs the docker deamon"
  type        = string
}

variable private_subnet_ids {
  description = "List of private subnet IDs"
  type        = list(string)
}

locals {
  xroad_private_domain = "${var.x-road_subdomain}.${var.AWS_HOSTED_DOMAIN}"
  xroad_dns_record     = "${var.x-road_host}.${var.x-road_subdomain}.${var.AWS_HOSTED_DOMAIN}"
}
