#!/usr/bin/env bash

SOURCING=false
if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
    # Script is being sourced. We must use return instead of exit since the script
    # is run in the context of the calling shell
    SOURCING=true
fi

SESSION_PROFILE=
MFA_IDENTIFIER=
TOKEN_CODE=

# Usage instructions
usage() {
    cat <<EOF
Usage: get-mfa-vars.sh [PROFILE] [MFA_IDENTIFIER] [TOKEN_CODE]
       source get-mfa-vars.sh [PROFILE] [MFA_IDENTIFIER] [TOKEN_CODE]

Arguments, in any order:
  PROFILE          AWS profile with the access key to use
  MFA_IDENTIFIER   MFA device ARN (starts with arn:)
  TOKEN_CODE       6-digit MFA token code

The profile is taken from, in this order:
  1. the PROFILE argument
  2. the AWS_PROFILE env variable
  3. a list of your profiles to pick from (used without asking if there is only one)

The MFA device ARN is taken from, in this order:
  1. the MFA_IDENTIFIER argument
  2. mfa_serial of the profile
  3. the AWS_MFA_IDENTIFIER env variable
  4. a prompt

The session is always made with the access key of the profile. An old session in
AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY and AWS_SESSION_TOKEN is ignored, and it is
replaced only when the new session succeeds.

If the token code is omitted, you will be prompted for it.

Examples:
  source get-mfa-vars.sh my-profile
  source get-mfa-vars.sh
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
    elif [[ "$1" == arn:* ]]; then
        MFA_IDENTIFIER="$1"
    else
        SESSION_PROFILE="$1"
    fi
    shift
done

mapfile -t PROFILES < <(aws configure list-profiles 2>/dev/null)
if [ ${#PROFILES[@]} -eq 0 ]; then
    echo "Error: No AWS profiles found. Run 'aws configure --profile <name>' first." >&2
    if $SOURCING; then
        return 1
    else
        exit 1
    fi
fi

if [ -z "$SESSION_PROFILE" ]; then
    SESSION_PROFILE="${AWS_PROFILE:-}"
fi
if [ -z "$SESSION_PROFILE" ] && [ ${#PROFILES[@]} -eq 1 ]; then
    SESSION_PROFILE="${PROFILES[0]}"
    echo "Using the only AWS profile: $SESSION_PROFILE"
elif [ -z "$SESSION_PROFILE" ] && [ ${#PROFILES[@]} -gt 1 ]; then
    PS3="Select AWS profile (number): "
    select SESSION_PROFILE in "${PROFILES[@]}"; do
        if [ -n "$SESSION_PROFILE" ]; then
            break
        fi
    done
fi

if [ -z "$SESSION_PROFILE" ] || ! printf '%s\n' "${PROFILES[@]}" | grep -qxF -- "$SESSION_PROFILE"; then
    echo "Error: AWS profile '$SESSION_PROFILE' not found. Your profiles: ${PROFILES[*]}" >&2
    if $SOURCING; then
        return 1
    else
        exit 1
    fi
fi

# The MFA device of the profile comes before AWS_MFA_IDENTIFIER, because each AWS
# account has its own MFA device.
if [ -z "$MFA_IDENTIFIER" ]; then
    MFA_IDENTIFIER=$(aws configure get mfa_serial --profile "$SESSION_PROFILE" 2>/dev/null)
fi
if [ -z "$MFA_IDENTIFIER" ]; then
    MFA_IDENTIFIER="${AWS_MFA_IDENTIFIER:-}"
fi

# Prompt for missing values
if [ -z "$MFA_IDENTIFIER" ]; then
    read -p "Enter MFA identifier (ARN): " MFA_IDENTIFIER
fi
if [ -z "$TOKEN_CODE" ]; then
    read -p "Enter MFA token code: " TOKEN_CODE
fi

# The aws cli prefers credentials in env variables over the profile. AWS refuses
# get-session-token with the credentials of an old session, so leave them out.
CREDENTIALS=$(env -u AWS_ACCESS_KEY_ID -u AWS_SECRET_ACCESS_KEY -u AWS_SESSION_TOKEN \
    aws sts get-session-token --profile "$SESSION_PROFILE" --serial-number "$MFA_IDENTIFIER" --token-code "$TOKEN_CODE" 2>/dev/null)
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
    echo "Environment variables set in current shell for AWS profile $SESSION_PROFILE."
else
    (umask 066 && {
        echo "export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID" > /tmp/aws-mfa-token
        echo "export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY" >> /tmp/aws-mfa-token
        echo "export AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN" >> /tmp/aws-mfa-token
    })
    echo "Success! Session for AWS profile $SESSION_PROFILE."
    echo "Run '. /tmp/aws-mfa-token' in bash or a compatible shell to set environment variables"
    echo "WARNING: Remove /tmp/aws-mfa-token after use to avoid leaking credentials (e.g., run 'rm /tmp/aws-mfa-token')."
fi
