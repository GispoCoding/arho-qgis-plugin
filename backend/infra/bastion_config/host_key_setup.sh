#!/bin/bash
set -e

# Parameters passed from Terraform
SSM_PARAM_NAME="${ssm_parameter_name}"
AWS_REGION="${aws_region}"

echo "Configuring exclusive Ed25519 Host Key..."

# Fetch and setup key
service sshd stop

echo "Fetching Host Key from SSM..."
aws ssm get-parameter \
  --name "$SSM_PARAM_NAME" \
  --with-decryption \
  --region "$AWS_REGION" \
  --query "Parameter.Value" \
  --output text > /etc/ssh/ssh_host_ed25519_key

chmod 640 /etc/ssh/ssh_host_ed25519_key
chown root:ssh_keys /etc/ssh/ssh_host_ed25519_key
ssh-keygen -y -f /etc/ssh/ssh_host_ed25519_key > /etc/ssh/ssh_host_ed25519_key.pub
chmod 644 /etc/ssh/ssh_host_ed25519_key.pub


# Comment out any existing HostKey definitions
sed -i 's/^HostKey/#HostKey/g' /etc/ssh/sshd_config

# Append our specific Ed25519 key as the only valid host key
echo "HostKey /etc/ssh/ssh_host_ed25519_key" >> /etc/ssh/sshd_config

# 5. Destroy the default OS-generated keys to ensure they are never used
rm -f /etc/ssh/ssh_host_rsa_key*
rm -f /etc/ssh/ssh_host_ecdsa_key*

service sshd start
