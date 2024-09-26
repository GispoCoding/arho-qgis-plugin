# Public domain already exists
data "aws_route53_zone" "public_zone" {
  count = 1
  name  = var.AWS_HOSTED_DOMAIN
}

resource "aws_route53_record" "bastion" {
  count = var.enable_route53_record ? 1 : 0

  zone_id = data.aws_route53_zone.public_zone[0].id
  name    = local.bastion_dns_alias
  type    = "A"
  records = [
      aws_instance.bastion-ec2-instance.public_ip
  ]
  ttl     = "60"
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
resource "aws_route53_zone" "private_zone" {
  name = local.xroad_private_domain

  vpc {
    vpc_id = aws_vpc.main.id
  }

  tags = merge(local.default_tags, { Name = "${var.prefix}-private_zone" })
}

resource "aws_route53_record" "xroad-private" {

  zone_id = aws_route53_zone.private_zone.id
  name    = local.xroad_dns_record
  type    = "A"
  records = [
      data.aws_network_interface.interface_tags.private_ip
  ]
  ttl     = "60"
}
