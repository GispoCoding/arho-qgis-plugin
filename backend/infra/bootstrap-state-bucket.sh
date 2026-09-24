#!/usr/bin/env bash
# Create the terraform state bucket and its KMS key in the AWS account of the current
# session. Terraform cannot create the bucket that holds its own state, so this runs once
# per account, before the first `make tf-init`. It skips what already exists, so it is
# safe to run again.
set -euo pipefail

# The aws cli would otherwise stop at a pager after every call that prints output.
export AWS_PAGER=""

KEY_ALIAS="alias/arho-terraform-state"

usage() {
    cat <<EOF
Usage: bootstrap-state-bucket.sh REGION

Creates, in the AWS account of the current session:
  - the KMS key $KEY_ALIAS, with yearly key rotation
  - the S3 bucket arho-deployments-<account-id>, with versioning, default encryption
    with that key, and all public access blocked

Example:
  ./bootstrap-state-bucket.sh eu-north-1
EOF
}

if [[ $# -ne 1 || "$1" == "--help" ]]; then
    usage
    exit 1
fi

region="$1"
account_id=$(aws sts get-caller-identity --query Account --output text)
caller_arn=$(aws sts get-caller-identity --query Arn --output text)
bucket="arho-deployments-${account_id}"

echo "Account: $account_id"
echo "Caller:  $caller_arn"
echo "Region:  $region"
echo "Bucket:  $bucket"
read -r -p "Create the state bucket in this account? [y/N] " answer
if [[ "$answer" != "y" ]]; then
    echo "Stopped. Nothing was created."
    exit 1
fi

if aws kms describe-key --region "$region" --key-id "$KEY_ALIAS" >/dev/null 2>&1; then
    echo "KMS key $KEY_ALIAS exists."
else
    echo "Creating KMS key $KEY_ALIAS..."
    key_id=$(aws kms create-key --region "$region" \
        --description "Encrypts the ARHO terraform state" \
        --query KeyMetadata.KeyId --output text)
    aws kms create-alias --region "$region" --alias-name "$KEY_ALIAS" --target-key-id "$key_id"
    aws kms enable-key-rotation --region "$region" --key-id "$key_id"
fi
key_arn=$(aws kms describe-key --region "$region" --key-id "$KEY_ALIAS" \
    --query KeyMetadata.Arn --output text)

if aws s3api head-bucket --region "$region" --bucket "$bucket" >/dev/null 2>&1; then
    echo "Bucket $bucket exists."
else
    echo "Creating bucket $bucket..."
    # us-east-1 is the default location and rejects a location constraint.
    if [[ "$region" == "us-east-1" ]]; then
        aws s3api create-bucket --region "$region" --bucket "$bucket"
    else
        aws s3api create-bucket --region "$region" --bucket "$bucket" \
            --create-bucket-configuration "LocationConstraint=$region"
    fi
fi

# These calls set the same values every time, so they also repair a bucket that was
# changed by hand.
echo "Setting versioning, encryption and the public access block..."
aws s3api put-bucket-versioning --region "$region" --bucket "$bucket" \
    --versioning-configuration Status=Enabled
aws s3api put-bucket-encryption --region "$region" --bucket "$bucket" \
    --server-side-encryption-configuration "{\"Rules\": [{\"ApplyServerSideEncryptionByDefault\": {\"SSEAlgorithm\": \"aws:kms\", \"KMSMasterKeyID\": \"$key_arn\"}, \"BucketKeyEnabled\": true}]}"
aws s3api put-public-access-block --region "$region" --bucket "$bucket" \
    --public-access-block-configuration \
    BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

cat <<EOF

Done. Save these lines as backends/<name>/backend.hcl in arho-deploy:

bucket               = "$bucket"
key                  = "arho.tfstate"
region               = "$region"
encrypt              = true
kms_key_id           = "$key_arn"
use_lockfile         = true
workspace_key_prefix = "arho"

Then initialise terraform for the instance:
  make tf-init ws=<workspace> backend=<name>
EOF
