#!/usr/bin/env bash
# Create the OpenTofu state bucket in UpCloud Managed Object Storage, in the UpCloud
# account of the current credentials. OpenTofu cannot create the bucket that holds its own
# state, so this runs once per account, before the first `tofu init`. It skips what already
# exists, so it is safe to run again.
#
# Needs curl, jq, openssl and the aws cli (for the S3 versioning call). UpCloud credentials come from
# UPCLOUD_TOKEN, or UPCLOUD_USERNAME and UPCLOUD_PASSWORD, as for the UpCloud provider.
# Without them, the script reads the token from the upctl config, ~/.config/upctl.yaml.
set -euo pipefail

# The aws cli would otherwise stop at a pager after every call that prints output.
export AWS_PAGER=""

# --- Settings -------------------------------------------------------------------------------

# Base URL of the UpCloud Managed Object Storage API.
API="https://api.upcloud.com/1.3/object-storage-2"
# A service of its own, so the terraform user's full S3 access reaches only the state.
SERVICE_NAME="arho-tfstate"
# The bucket that holds the state. Test and prod are workspaces in the same bucket.
BUCKET="arho-tfstate"
# The Object Storage user OpenTofu signs in as. Not an UpCloud account user.
STATE_USER="terraform"

# --- Arguments ------------------------------------------------------------------------------

usage() {
    cat <<EOF
Usage: bootstrap-state-bucket.sh [REGION]

Creates, in the UpCloud account of the current credentials:
  - the Managed Object Storage service $SERVICE_NAME, public network only, with
    termination protection (data is encrypted at rest by default)
  - the bucket $BUCKET, with versioning
  - the user $STATE_USER with the policy ECSS3FullAccess, and an access key for it
    if the user has none

REGION is an Object Storage region, default europe-1 (primary zone fi-hel1).

Credentials: UPCLOUD_TOKEN, or UPCLOUD_USERNAME and UPCLOUD_PASSWORD, or the token in
~/.config/upctl.yaml.

Example:
  ./bootstrap-state-bucket.sh
EOF
}

# Take at most one argument, the region. --help prints the usage and stops.
if [[ $# -gt 1 || "${1:-}" == "--help" ]]; then
    usage
    exit 1
fi
region="${1:-europe-1}"

# --- UpCloud credentials --------------------------------------------------------------------

# Fall back to the token in the upctl config file when the environment has no credentials.
UPCTL_CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}/upctl.yaml"
if [[ -z "${UPCLOUD_TOKEN:-}" && -z "${UPCLOUD_USERNAME:-}" && -r "$UPCTL_CONFIG" ]]; then
    # The top-level `token:` line, without surrounding quotes or whitespace.
    UPCLOUD_TOKEN=$(sed -nE "s/^token:[[:space:]]*['\"]?([^'\"[:space:]]+)['\"]?[[:space:]]*$/\1/p" \
        "$UPCTL_CONFIG" | head -n 1)
    if [[ -n "$UPCLOUD_TOKEN" ]]; then
        echo "Using the token from $UPCTL_CONFIG."
    fi
fi

# Build the curl options for the API: a bearer token if there is one, otherwise the account
# user name and password. Stop if there are no credentials at all.
if [[ -n "${UPCLOUD_TOKEN:-}" ]]; then
    auth=(-H "Authorization: Bearer $UPCLOUD_TOKEN")
elif [[ -n "${UPCLOUD_USERNAME:-}" && -n "${UPCLOUD_PASSWORD:-}" ]]; then
    auth=(-u "$UPCLOUD_USERNAME:$UPCLOUD_PASSWORD")
else
    echo "Set UPCLOUD_TOKEN, or UPCLOUD_USERNAME and UPCLOUD_PASSWORD, or add a token" >&2
    echo "to $UPCTL_CONFIG." >&2
    exit 1
fi

# api METHOD PATH [JSON]: call the Object Storage API, print the body, fail on an error.
api() {
    local method="$1" path="$2" body="${3:-}"
    local args=(-sS --fail-with-body -X "$method" "${auth[@]}" -H "Content-Type: application/json")
    if [[ -n "$body" ]]; then
        args+=(-d "$body")
    fi
    curl "${args[@]}" "$API$path"
}

# --- Confirmation ---------------------------------------------------------------------------

# Look up the account the credentials belong to. This also checks that they work. Show what
# will be created and ask before changing anything.
account=$(curl -sS --fail-with-body "${auth[@]}" https://api.upcloud.com/1.3/account \
    | jq -r .account.username)

echo "Account: $account"
echo "Region:  $region"
echo "Service: $SERVICE_NAME"
echo "Bucket:  $BUCKET"
read -r -p "Create the state bucket in this account? [y/N] " answer
if [[ "$answer" != "y" ]]; then
    echo "Stopped. Nothing was created."
    exit 1
fi

# --- Object Storage service -----------------------------------------------------------------

# Find the service by name, or create it. It gets a public network only, so OpenTofu can
# reach it from a laptop or CI, and termination protection, so it cannot be deleted by
# mistake while it holds the state.
service_uuid=$(api GET "?limit=100" \
    | jq -r --arg n "$SERVICE_NAME" '.[] | select(.name == $n) | .uuid')
if [[ -n "$service_uuid" ]]; then
    echo "Service $SERVICE_NAME exists."
else
    echo "Creating service $SERVICE_NAME..."
    service_uuid=$(api POST "" "$(jq -n --arg n "$SERVICE_NAME" --arg r "$region" '{
        name: $n,
        region: $r,
        configured_status: "started",
        termination_protection: true,
        networks: [{name: "public", type: "public", family: "IPv4"}],
        labels: [{key: "project", value: "arho"}]
    }')" | jq -r .uuid)
fi

# A new service takes a few minutes to start, and buckets and users can only be added to a
# running one. Check every 10 seconds, for at most 10 minutes.
echo "Waiting for the service to run..."
for _ in $(seq 60); do
    state=$(api GET "/$service_uuid" | jq -r .operational_state)
    [[ "$state" == "running" ]] && break
    sleep 10
done
if [[ "$state" != "running" ]]; then
    echo "The service is still '$state' after 10 minutes. Run this script again later." >&2
    exit 1
fi
# The public S3 API address of the service, e.g. 7mf5k.upcloudobjects.com. The backend file
# and the versioning call need it.
endpoint=$(api GET "/$service_uuid" \
    | jq -r '.endpoints[] | select(.type == "public" and .mode == "api") | .domain_name')

# --- Bucket ---------------------------------------------------------------------------------

# Create the state bucket unless the service already has it.
if api GET "/$service_uuid/buckets?limit=100" \
    | jq -e --arg b "$BUCKET" 'any(.[]; .name == $b)' >/dev/null; then
    echo "Bucket $BUCKET exists."
else
    echo "Creating bucket $BUCKET..."
    api POST "/$service_uuid/buckets" "$(jq -n --arg b "$BUCKET" '{name: $b}')" >/dev/null
fi

# --- User, policy and access key ------------------------------------------------------------

# Create the Object Storage user for OpenTofu unless it exists.
if api GET "/$service_uuid/users?limit=100" \
    | jq -e --arg u "$STATE_USER" 'any(.[]; .username == $u)' >/dev/null; then
    echo "User $STATE_USER exists."
else
    echo "Creating user $STATE_USER..."
    api POST "/$service_uuid/users" "$(jq -n --arg u "$STATE_USER" '{username: $u}')" >/dev/null
fi

# A new user has no rights. Give it the built-in full S3 access policy, which covers every
# bucket in this service, i.e. only the state bucket.
if api GET "/$service_uuid/users/$STATE_USER/policies" \
    | jq -e 'any(.[]; .name == "ECSS3FullAccess")' >/dev/null; then
    echo "User $STATE_USER has ECSS3FullAccess."
else
    echo "Attaching ECSS3FullAccess to $STATE_USER..."
    api POST "/$service_uuid/users/$STATE_USER/policies" '{"name": "ECSS3FullAccess"}' >/dev/null
fi

# UpCloud shows a secret key only when it is created, so a new key is made only when the
# user has none. Otherwise use the saved key, from AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY.
access_key=""
secret_key=""
if api GET "/$service_uuid/users/$STATE_USER/access-keys" \
    | jq -e 'any(.[]; .status == "Active")' >/dev/null; then
    echo "User $STATE_USER has an active access key."
    access_key="${AWS_ACCESS_KEY_ID:-}"
    secret_key="${AWS_SECRET_ACCESS_KEY:-}"
else
    echo "Creating an access key for $STATE_USER..."
    key_json=$(api POST "/$service_uuid/users/$STATE_USER/access-keys")
    access_key=$(jq -r .access_key_id <<<"$key_json")
    secret_key=$(jq -r .secret_access_key <<<"$key_json")
fi

# --- Versioning -----------------------------------------------------------------------------

# Versioning keeps the earlier versions of the state file, so a broken state can be rolled
# back. The UpCloud API has no call for it, so it goes through the S3 API with the terraform
# user's key. This sets the same value every time, so it also repairs a bucket changed by hand.
if [[ -n "$access_key" && -n "$secret_key" ]]; then
    echo "Setting versioning..."
    if ! AWS_ACCESS_KEY_ID="$access_key" AWS_SECRET_ACCESS_KEY="$secret_key" \
        aws s3api put-bucket-versioning --region "$region" \
        --endpoint-url "https://$endpoint" --bucket "$BUCKET" \
        --versioning-configuration Status=Enabled; then
        echo "WARNING: versioning could not be set. Check the bucket in the UpCloud console." >&2
    fi
else
    echo "WARNING: versioning was not set. Run again with the $STATE_USER key in" >&2
    echo "AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY." >&2
fi

# --- Result ---------------------------------------------------------------------------------

# Print the two backend files for arho-deploy: the plaintext settings, and the keys and the
# state encryption passphrase, which must be encrypted. When the key was not created in this
# run and is not in the environment, print placeholders instead of the key.
cat <<EOF

Done. In arho-deploy, save these lines as backends/<name>/backend.hcl (no secrets):

bucket = "$BUCKET"
endpoints = {
  s3 = "https://$endpoint"
}

Then save the keys encrypted, never in plaintext. From the arho-deploy root, run
\`sops edit backends/<name>/credentials.enc.env\` and enter:

AWS_ACCESS_KEY_ID=${access_key:-<the saved access key of $STATE_USER>}
AWS_SECRET_ACCESS_KEY=${secret_key:-<the saved secret key of $STATE_USER>}
TF_VAR_state_encryption_passphrase=$(openssl rand -base64 32)

The passphrase above is new and random. It encrypts the state (encryption.tf), so use it
only for a backend that has no state yet. If the file already has a passphrase, keep that
one: without it the existing state cannot be read.
EOF
# A secret that did not come from the environment was created in this run, and UpCloud will
# not show it again.
if [[ -n "$secret_key" && "$secret_key" != "${AWS_SECRET_ACCESS_KEY:-}" ]]; then
    echo
    echo "The secret key is shown only now. Save it before closing this terminal."
fi
cat <<EOF

Then initialise the configuration:
  make tf-init ws=<workspace> backend=<name>
EOF
