locals {
  name_prefix = "arho-${local.environment}"
  labels = {
    project     = "arho"
    environment = local.environment
  }
}

resource "upcloud_router" "main" {
  name   = "${local.name_prefix}-router"
  labels = local.labels
}

resource "upcloud_network" "private" {
  name   = "${local.name_prefix}-private"
  zone   = var.zone
  router = upcloud_router.main.id
  labels = local.labels

  ip_network {
    address = var.private_network_cidr
    family  = "IPv4"
    dhcp    = true
    # Servers on this network send outbound traffic through the router and the NAT gateway.
    dhcp_default_route = true
  }
}

# Outbound internet access for servers that have no public interface. Its public address is
# also the X-Road security server's address, registered with DVV (plan.md, tasks 01 and 13).
# UpCloud cannot give a gateway a reserved address, so a new gateway gets a new one and the
# DVV registration must change. prevent_destroy stops any plan that would delete or replace
# the gateway; remove it only on purpose, after agreeing the change with DVV.
resource "upcloud_gateway" "nat" {
  name     = "${local.name_prefix}-nat"
  zone     = var.zone
  features = ["nat"]
  labels   = local.labels

  router {
    id = upcloud_router.main.id
  }

  lifecycle {
    prevent_destroy = true
  }
}
