#!/usr/bin/env bash
# Runs tofu with the state encryption config of every ARHO configuration. The make targets run
# tofu through this script, so no configuration needs an encryption block of its own.
#
# OpenTofu encrypts the state and saved plan files with AES-GCM before they leave this
# machine, so the state bucket only ever holds ciphertext, and a leaked bucket key does not
# expose the state. "enforced" makes OpenTofu refuse to read or write unencrypted state.
#
# The key is derived from a passphrase with PBKDF2. The passphrase is per backend and lives in
# arho-deploy, in backends/<backend>/credentials.enc.env as TF_VAR_state_encryption_passphrase,
# which the make targets put in the environment. (The name is kept from when it was an
# OpenTofu variable; tofu ignores it, as no configuration declares that variable.) Without the
# passphrase the state cannot be read, and bucket versioning does not help: keep it only in
# arho-deploy, which several people's age keys can decrypt.
#
# The config goes to tofu in TF_ENCRYPTION, which OpenTofu reads as if it were the
# terraform { encryption { ... } } block of the configuration.
#
# To change the passphrase, add the old one as a second pbkdf2 key provider with its own
# aes_gcm method, list that method in a `fallback` block in both state and plan, apply every
# workspace once, then remove the fallback.
set -euo pipefail

passphrase="${TF_VAR_state_encryption_passphrase:-}"
if [[ -z "$passphrase" ]]; then
    echo "TF_VAR_state_encryption_passphrase is not set. Run tofu through make, which reads it" >&2
    echo "from credentials.enc.env of the backend." >&2
    exit 1
fi
if [[ ${#passphrase} -lt 32 ]]; then
    echo "The state encryption passphrase is too short. Use at least 32 characters, e.g." >&2
    echo "openssl rand -base64 32." >&2
    exit 1
fi
# The passphrase goes into an HCL string, where quotes, backslashes and ${ would change its
# meaning. openssl rand -base64 uses only these characters.
if [[ ! "$passphrase" =~ ^[A-Za-z0-9+/=_-]+$ ]]; then
    echo "The state encryption passphrase may contain only letters, digits and + / = _ -." >&2
    exit 1
fi

TF_ENCRYPTION=$(cat <<EOF
key_provider "pbkdf2" "main" {
  passphrase = "$passphrase"
}

method "aes_gcm" "main" {
  keys = key_provider.pbkdf2.main
}

state {
  method   = method.aes_gcm.main
  enforced = true
}

plan {
  method   = method.aes_gcm.main
  enforced = true
}
EOF
)
export TF_ENCRYPTION

exec "${TOFU:-tofu}" "$@"
