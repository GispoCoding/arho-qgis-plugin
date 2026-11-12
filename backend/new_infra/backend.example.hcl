# The format of backends/<name>/backend.hcl in arho-deploy. It holds no secrets: the state
# access keys come from AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY, which `make` sets from
# the sops-encrypted credentials.enc.env next to it.
bucket = "arho-tfstate"
endpoints = {
  s3 = "https://<object-storage-id>.upcloudobjects.com"
}
