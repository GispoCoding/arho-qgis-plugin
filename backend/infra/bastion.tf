# We don't want to create the key in terraform. Otherwise the private key(s) would be saved in terraform state.
# Let's save the public key(s) here as ec2 instance user data.

data "aws_ssm_parameter" "amazon_linux" {
  name = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-arm64"
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
  user_data     = local.bastion_user_data
  tags = merge(local.default_tags, {
    Name = "${var.prefix}-bastion"
  })
}
