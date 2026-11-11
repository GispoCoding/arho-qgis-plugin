data "aws_route53_zone" "public_zone" {
  count = 1
  name  = var.AWS_HOSTED_DOMAIN
}

resource "aws_route53_record" "xroad-verification" {
  count = var.enable_route53_record ? 1 : 0

  zone_id = data.aws_route53_zone.public_zone[0].id
  name    = local.xroad_dns_record
  type    = "TXT"
  records = [
      var.x-road_verification_record
  ]
  ttl     = "60"
}

# Create private domain for X-road server only

# We have to use AWS service discovery, since the X-Road ECS ip will change if
# the container is redeployed
resource "aws_service_discovery_private_dns_namespace" "private" {
  name        = local.xroad_private_domain
  vpc         = var.vpc_id

  tags = merge(var.default_tags, { Name = "${var.prefix}-private_zone" })
}

resource "aws_service_discovery_service" "x-road_securityserver" {
  name = var.x-road_host
  dns_config {
    namespace_id = aws_service_discovery_private_dns_namespace.private.id

    dns_records {
      ttl  = "60"
      type = "A"
    }

    routing_policy = "MULTIVALUE"
  }

  health_check_custom_config {
    failure_threshold = 1
  }

  tags = merge(var.default_tags, { Name = "${var.prefix}-private_zone" })
}
