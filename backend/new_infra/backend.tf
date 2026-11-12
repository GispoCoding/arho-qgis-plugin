# State lives in UpCloud Managed Object Storage through its S3-compatible API. The
# bucket, endpoint and keys differ per UpCloud account, so they live in arho-deploy under
# backends/<name>/. Run `make tf-init ws=<workspace> backend=<name>` instead of a bare
# `tofu init` (see backend.example.hcl). The bucket must exist before the first init.
terraform {
  backend "s3" {
    # Each workspace keeps its state at arho/<workspace>/terraform.tfstate. Setting the prefix
    # avoids the default "env:" prefix, which would put colons in the paths. The default
    # workspace would use the bare key, so workspace.tf refuses to run in it.
    key                  = "terraform.tfstate"
    workspace_key_prefix = "arho"
    region               = "europe-1"

    # A lock file next to the state, instead of DynamoDB.
    use_lockfile = true

    # UpCloud is not AWS: skip the AWS-only checks.
    use_path_style              = true
    skip_credentials_validation = true
    skip_region_validation      = true
    skip_requesting_account_id  = true
    skip_metadata_api_check     = true
    skip_s3_checksum            = true
  }
}
