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

variable "state_encryption_passphrase" {
  description = <<-EOT
    Passphrase for the state encryption key (encryption.tf). Set it through
    TF_VAR_state_encryption_passphrase in credentials.enc.env of the backend, never in a
    variable file.
  EOT
  type        = string
  sensitive   = true

  validation {
    condition     = length(var.state_encryption_passphrase) >= 32
    error_message = "Use at least 32 characters, e.g. openssl rand -base64 32."
  }
}
