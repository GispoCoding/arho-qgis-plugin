# The backend settings differ per AWS account, so they are not stored here. Each account
# has a file in arho-deploy under backends/. Run `make tf-init` instead of a bare
# `terraform init`.
terraform {
  backend "s3" {}
}
