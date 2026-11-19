variable "zone" {
  description = "UpCloud zone."
  type        = string
  default     = "fi-hel1"
}

variable "private_network_cidr" {
  description = <<-EOT
    Address range of the private platform network. Pick an uncommon range that customer
    networks and VPNs are unlikely to use, because site-to-site VPNs and WireGuard route it.
  EOT
  type        = string

  validation {
    condition     = can(cidrhost(var.private_network_cidr, 0))
    error_message = "Must be an IPv4 CIDR block."
  }
}
