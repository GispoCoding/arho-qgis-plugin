
output dns_record {
    description = "DNS record for the X-Road Security Server."
    value       = local.xroad_dns_record
}
output instance {
    value = var.x-road_instance
}

output member_class {
    value = var.x-road_member_class
}

output member_code {
    value = var.x-road_member_code
}

output subdomain {
    value = var.x-road_subdomain
}

output client_id {
    value = var.syke_xroad_client_id
}

output client_secret_arn {
    value = aws_secretsmanager_secret.syke-xroad-client-secret.arn
}
