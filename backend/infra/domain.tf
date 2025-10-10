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
