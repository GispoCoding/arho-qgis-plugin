# ARHO backend infrastructure

`infra/` is one flat Terraform root module (one workspace per deployment) with one nested
local module, `x-road/`, gated by the `enable_x_road` variable. `README.md` here has the
procedures; this file has what the code does not say.

## State and configuration

- The S3 backend is per AWS account, so `state.tf` is empty.
  `make tf-init ws=<ws> backend=<name>` passes `arho-deploy/backends/<name>/backend.hcl`
  and records the name in `.terraform/backend-name`. Always init through that target;
  a bare `terraform init` has no backend. The arho-deploy README maps workspaces to
  backend files. `bootstrap-state-bucket.sh <region>` creates the state bucket and KMS
  key in a new account and prints its backend file.
- Instance config (tfvars, ssh public keys) is sops-encrypted in the private arho-deploy
  repository, in `backends/<name>/var-files/` and `backends/<name>/public_keys/`.
  `ARHO_DEPLOY_DIR` points to its checkout and defaults to a sibling of this repository.
  `make decrypt-workspace-secrets` / `encrypt-workspace-secrets` work on the current
  workspace. Real tfvars and keys belong only there.
- An AWS session: one IAM user profile per account, with `mfa_serial` set, plus
  `. ./get-mfa-vars.sh <profile>` (no profile: pick from a list). It reads the MFA ARN
  from the profile and ignores an old session in the shell. See "AWS login on your
  computer" in `README.md`.
- Write universal text in code and docs: no company or customer names, and no account
  called "legacy". Every AWS account is equally supported.

## Make targets

- The targets that talk to AWS (`create-db`, `migrate-db`, `load-*`, `push-*`,
  `update-*`, `log-*`, `bastion-known-host`) need no exports: `prefix` and `AWS_REGION`
  come from the decrypted tfvars file of the current workspace and `AWS_ACCOUNT_ID` from
  `aws sts get-caller-identity`. A value in the environment or on the command line
  overrides the lookup. They depend on `check-deployment-vars`, which stops with a
  readable message when a value is empty.
- The Makefile exports an empty `AWS_PAGER`, so the aws cli prints its output instead of
  stopping every recipe in a pager.

## Lambdas

- Terraform does not build or push the lambda images; `make push-lambdas` does (it tags
  the local `arho-*:latest` compose images). A function cannot be created before its
  image exists, so a first deployment runs `make tf-bootstrap-ecr`, `make push-lambdas`,
  `make tf-apply`.
- Give a lambda a secret as a secret ARN in `<name>_SECRET_ARN`, read with `get_secret`.
  A secret value in an env var shows in the function configuration and in `aws lambda`
  output.
- `ryhti_client` uses provisioned concurrency, which cannot attach to `$LATEST`. The
  function has `publish = true`, the API gateway points at its `live` alias, and
  `make update-lambdas` publishes a new version and moves that alias. Terraform ignores
  changes to `function_version` for that reason.
- `ryhti_client` has its own IAM role (`aws_iam_role.ryhti_client_exec`): VPC access, the
  DBA secret, the SYKE API key secret, the X-Road client secret (with X-Road), the S3
  transfer bucket and `lambda:InvokeFunction` on itself and its qualifiers (the job
  self-invoke). The shared `lambda_exec` role has no S3 or X-Road access. Timeout 900 s,
  `JOB_RUNNER=lambda`, `JOB_TIME_LIMIT_SECONDS` from the same local, async retries 0 and
  maximum event age 900 s on `live` and `$LATEST`.
- A published version keeps the role and settings it was published with, so a Terraform
  change reaches the API gateway path only when `make update-lambdas` moves `live`.
- Rollout order: `tf-apply`, `push-lambdas`, `update-lambdas`, `migrate-db`. The new code
  raises at cold start without the job settings from the apply, and the migration ships
  in the `db_manager` image. Between `tf-apply` and `update-lambdas` the old `live`
  version runs on the shared role without S3 and X-Road, so update the lambdas right
  after the apply, at a quiet time. See "Rolling out ryhti_client jobs" in `README.md`.

## Network and bastion

- Reference subnets as `aws_subnet.private[*].id`. An `aws_subnets` data source creates
  no dependency, so it reads empty on a fresh apply.
- The bastion host key is in SSM (`/infra/<prefix>-bastion/host_key_ed25519`) and the
  instance installs it at boot, so `make bastion-known-host` prints a verified
  `known_hosts` line. Ansible cannot connect to an unknown host, so
  `make update-ssh-keys` needs this first.
