# We don't want to create the key in terraform. Otherwise the private key(s) would be saved in terraform state.
# Let's save the public key(s) here as ec2 instance user data.

data "aws_ssm_parameter" "amazon_linux" {
  name = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-arm64"
}

data "cloudinit_config" "bastion_config" {
  gzip          = true  # Compresses data to fit more in the 16KB limit
  base64_encode = true  # AWS requires base64

  # Part 1: Cloud-Config (Runs first by default)
  part {
    content_type = "text/cloud-config"
    content      = templatefile(
      "bastion_config/cloud-config.yaml.tftpl",
      {
        ec2_user_public_keys    = var.bastion_ec2_user_public_keys,
      }
    )
  }

  # Part 2: Shell Script (Runs after)
  part {
    content_type = "text/x-shellscript"
    content      = templatefile(
      "bastion_config/host_key_setup.sh",
      {
        ssm_parameter_name = "/infra/${var.prefix}-bastion/host_key_ed25519"
        aws_region         = data.aws_region.current.name
      }
    )
  }
}

# Just the smallest arm instance available, for routing traffic to postgres
resource "aws_instance" "bastion-ec2-instance" {
  ami = data.aws_ssm_parameter.amazon_linux.value
  instance_type = "t4g.nano"
  subnet_id     = aws_subnet.public[0].id
  vpc_security_group_ids = [aws_security_group.bastion.id]
  iam_instance_profile = aws_iam_instance_profile.ec2-iam-profile.name
  tenancy              = "default"
  user_data_replace_on_change = true  # This is needed to update user data *and* ip address
  user_data_base64 = data.cloudinit_config.bastion_config.rendered
  tags = merge(local.default_tags, {
    Name = "${var.prefix}-bastion"
  })
}
