# OpenTofu client-side encryption of the state and of saved plan files. Both are encrypted
# with AES-GCM before they leave this machine, so the state bucket only ever holds
# ciphertext, and a leaked bucket key does not expose the state. "enforced" makes OpenTofu
# refuse to read or write unencrypted state.
#
# The key is derived from a passphrase with PBKDF2. The passphrase is per backend and lives in
# arho-deploy, in backends/<name>/credentials.enc.env as TF_VAR_state_encryption_passphrase,
# which the make targets put in the environment. Without the passphrase the state cannot be
# read, and bucket versioning does not help: keep it only in arho-deploy, which several
# people's age keys can decrypt.
#
# To change the passphrase, add the old one as a second pbkdf2 key provider with its own
# aes_gcm method, list that method in a `fallback` block in both state and plan, apply every
# workspace once, then remove the fallback.
terraform {
  encryption {
    key_provider "pbkdf2" "main" {
      passphrase = var.state_encryption_passphrase
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
  }
}
