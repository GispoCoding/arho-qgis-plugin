#!/usr/bin/env bash

set -e

if ! command -v aws &>/dev/null; then
    echo "Command aws not found: install AWS CLI first!" >&2
    exit 1
fi

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 [ARN] [CODE]" >&2
    echo "See https://aws.amazon.com/premiumsupport/knowledge-center/authenticate-mfa-cli/" >&2
    exit 1
fi

AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_SESSION_TOKEN=


CREDENTIALS=$(aws sts get-session-token --serial-number $1 --token-code $2)

if ! command -v jq &>/dev/null; then
    echo "Command jq not found: install jq to parse JSON response"
    echo $CREDENTIALS
    exit 0
fi

AWS_ACCESS_KEY_ID=$(echo $CREDENTIALS | jq -r ".Credentials.AccessKeyId")
AWS_SECRET_ACCESS_KEY=$(echo $CREDENTIALS | jq -r ".Credentials.SecretAccessKey")
AWS_SESSION_TOKEN=$(echo $CREDENTIALS | jq -r ".Credentials.SessionToken")

(umask 066 && touch /tmp/aws-mfa-token)

echo "export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID" > /tmp/aws-mfa-token
echo "export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY" >> /tmp/aws-mfa-token
echo "export AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN" >> /tmp/aws-mfa-token

echo "Success! Run '. /tmp/aws-mfa-token' to set environment variables"
