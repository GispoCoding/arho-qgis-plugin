output "private_network_id" {
  description = "ID of the private platform network."
  value       = upcloud_network.private.id
}

output "router_id" {
  description = "ID of the router attached to the private network."
  value       = upcloud_router.main.id
}

output "nat_gateway_addresses" {
  description = "Public addresses of the NAT gateway: the outbound address of every private server, and the X-Road security server's address registered with DVV."
  value       = upcloud_gateway.nat.addresses
}
