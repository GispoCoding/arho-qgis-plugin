terraform {
  # OpenTofu only (see README). use_lockfile in the s3 backend needs OpenTofu 1.10.
  required_version = ">= 1.10"

  required_providers {
    upcloud = {
      source  = "UpCloudLtd/upcloud"
      version = "~> 5.49"
    }
  }
}

# Credentials come from UPCLOUD_TOKEN, or UPCLOUD_USERNAME and UPCLOUD_PASSWORD, or the system
# keyring that `upctl account login` writes (see "UpCloud API token" in ../README.md). Never
# put them in this repository.
provider "upcloud" {}
