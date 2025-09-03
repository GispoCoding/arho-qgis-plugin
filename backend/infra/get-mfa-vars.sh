#!/usr/bin/env bash

SOURCING=false
if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
    # Script is being sourced. We must use return instead of exit since the script
    # is run in the context of the calling shell
    SOURCING=true
fi

MFA_IDENTIFIER=
TOKEN_CODE=

# Usage instructions
usage() {
    cat <<EOF
Usage: get-mfa-vars.sh [MFA_IDENTIFIER] [TOKEN_CODE]
       source get-mfa-vars.sh [MFA_IDENTIFIER] [TOKEN_CODE]

Arguments:
  MFA_IDENTIFIER   MFA device ARN (can also be set via AWS_MFA_IDENTIFIER env variable)
  TOKEN_CODE       6-digit MFA token code

If arguments are omitted, you will be prompted for missing values.

Examples:
  source get-mfa-vars.sh arn:aws:iam::123456789012:mfa/user 123456
  get-mfa-vars.sh arn:aws:iam::123456789012:mfa/user 123456

Environment variables set:
  AWS_ACCESS_KEY_ID
  AWS_SECRET_ACCESS_KEY
  AWS_SESSION_TOKEN

EOF
}

# Check for --help argument
if [[ "$1" == "--help" ]]; then
    usage
    if $SOURCING; then
        return 0
    else
        exit 0
    fi
fi

if ! command -v aws &>/dev/null; then
    echo "Command aws not found: install AWS CLI first!" >&2
    if $SOURCING; then
        return 1
    else
        exit 1
    fi
fi

# Parse parameters
while [[ $# -gt 0 ]]; do
    if [[ "$1" =~ ^[0-9]{6}$ ]]; then
        # If the argument is a 6-digit number, treat it as the token code
        TOKEN_CODE="$1"
    else
        MFA_IDENTIFIER="$1"
    fi
    shift
done

# Use env variable if MFA_IDENTIFIER not set by parameter
MFA_IDENTIFIER="${MFA_IDENTIFIER:-${AWS_MFA_IDENTIFIER:-}}"

# Prompt for missing values
if [ -z "$MFA_IDENTIFIER" ]; then
    read -p "Enter MFA identifier (ARN): " MFA_IDENTIFIER
fi
if [ -z "$TOKEN_CODE" ]; then
    read -p "Enter MFA token code: " TOKEN_CODE
fi

AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_SESSION_TOKEN=

CREDENTIALS=$(aws sts get-session-token --serial-number "$MFA_IDENTIFIER" --token-code "$TOKEN_CODE" 2>/dev/null)
AWS_CMD_EXIT=$?
if [ $AWS_CMD_EXIT -ne 0 ]; then
    echo "Error: Failed to fetch session token. Probably because expired/invalid MFA token or incorrect MFA ARN" >&2
    if $SOURCING; then
        return 1
    else
        exit 1
    fi
fi

if ! command -v jq &>/dev/null; then
    echo "Command jq not found: install jq to parse JSON response. Without jq, environment variables will NOT be set automatically."
    echo $CREDENTIALS
    if $SOURCING; then
        return 0
    else
        exit 0
    fi
fi

AWS_ACCESS_KEY_ID=$(echo $CREDENTIALS | jq -r ".Credentials.AccessKeyId")
AWS_SECRET_ACCESS_KEY=$(echo $CREDENTIALS | jq -r ".Credentials.SecretAccessKey")
AWS_SESSION_TOKEN=$(echo $CREDENTIALS | jq -r ".Credentials.SessionToken")

if $SOURCING; then
    # Script is being sourced
    export AWS_ACCESS_KEY_ID
    export AWS_SECRET_ACCESS_KEY
    export AWS_SESSION_TOKEN
    echo "Environment variables set in current shell."
else
    (umask 066 && {
        echo "export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID" > /tmp/aws-mfa-token
        echo "export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY" >> /tmp/aws-mfa-token
        echo "export AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN" >> /tmp/aws-mfa-token
    })
    echo "Success! Run '. /tmp/aws-mfa-token' in bash or a compatible shell to set environment variables"
    echo "WARNING: Remove /tmp/aws-mfa-token after use to avoid leaking credentials (e.g., run 'rm /tmp/aws-mfa-token')."
fi
