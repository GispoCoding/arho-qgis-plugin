# ARHO platform infrastructure

`new_infra/` holds the OpenTofu configurations for the shared ARHO platform that replaces
the AWS deployment in `../infra` (`../docs/transition-plan.md`, task 02 and later). Once
the AWS instances have moved (task 13), `../infra` is deleted. Until then, do not change
`../infra` for platform work, and do not copy its patterns (Lambda, RDS, MFA sessions)
here. `README.md` has the procedures; this file has what the code does not say.

## Structure

`new_infra/` is cloud-neutral. The platform needs only servers, a managed PostgreSQL
database and S3-compatible object storage, so it can run on any cloud or in a data
center that offers them (plan decision 12). UpCloud is the first provider, not the
design.

- This folder has only what every provider shares: `Makefile` (backend, workspaces,
  secrets), `tofu-encrypted.sh` (state encryption), `backend.example.hcl` (the format of a
  backend file) and `README.md`. These assume only OpenTofu, sops and an S3-compatible
  state bucket.
- Each provider has exactly one configuration: one OpenTofu root module in a subdirectory
  of its own, with one state per workspace. Do not split a provider into several
  configurations; new resources for a provider go into its existing configuration. Today
  there is one, `upcloud/`: the router, the private network and the NAT gateway of a
  platform. Later tasks add the servers, the database cluster per tenant, monitoring and
  X-Road.
- Everything UpCloud-specific goes in `upcloud/`: resources, provider settings, zones and
  regions, the backend's skipped AWS checks and scripts that call the UpCloud API (such
  as `bootstrap-state-bucket.sh`). No shared code may assume UpCloud; a make target or
  script that works for only one provider belongs in that provider's directory.
- The exceptions are `README.md` and this file. They may describe each provider: the
  README has one section per provider (today only "UpCloud") for its credentials, account
  set-up and resources, and this file has notes on providers where they matter (today
  UpCloud's). A new provider gets its own README section, and its notes go here too.
- Shared files may use UpCloud in examples (an Object Storage endpoint, the API token as
  a provider credential), as long as the example is something other providers also have.
  An example that only makes sense on UpCloud belongs in `upcloud/` or the UpCloud
  section of the README.
- A new cloud or data center is a new provider: one directory next to `upcloud/`, with a
  `backend "s3"` block like `upcloud/backend.tf` and a backend of its own in arho-deploy.
  Providers never share a backend (bucket, keys and passphrase). The servers it creates
  must run the same images and Ansible set-up as on UpCloud.
- `workspace_key_prefix` is `arho` in every provider. It marks the state as ARHO state,
  apart from anything else in the same bucket or account. It does not tell providers
  apart, and must not be changed to do so.

## OpenTofu, not Terraform

- OpenTofu 1.10 or later. The lock file holds OpenTofu registry hashes, the s3 backend
  uses `use_lockfile`, and state encryption is an OpenTofu feature. Do not run
  `terraform` here or write Terraform-only syntax. The language keeps Terraform's names
  (`terraform {}`, `terraform.workspace`, `.terraform/`), which is expected.
- Run every command that touches state through make: `make tf-init dir=<dir> ws=<ws>
  backend=<backend>`, then `make tf-plan` / `tf-apply`. A bare `tofu` has no backend
  config and no encryption config, so it cannot read existing state and would write a new
  workspace in plaintext. For a command the Makefile lacks, run
  `tofu-encrypted.sh -chdir=<dir> ...` inside `sops exec-env <credentials.enc.env>`.
- Do not add an `encryption` block to a configuration. `tofu-encrypted.sh` passes the
  same config to every one in `TF_ENCRYPTION`.

## State, configuration and secrets

- Nothing deployment-specific belongs in this public repository: no endpoints of a real
  account, no tfvars, no keys, no IP ranges, no customer names. `.gitignore` blocks the
  usual file names, but check anyway. The state service and bucket are called
  `arho-tfstate` in every account, so that name is not deployment-specific.
- Everything lives in the private arho-deploy repository under `backends/<backend>/`:
  `backend.hcl` (plaintext), `credentials.enc.env` (state keys and the state encryption
  passphrase) and `var-files/<workspace>.tfvars.enc.json`, both sops with age keys.
  `ARHO_DEPLOY_DIR` points to its checkout and defaults to a sibling of this repository.
- Secrets are decrypted only for the duration of a command (`sops exec-env`,
  `sops exec-file`). Never decrypt into a file, and never print secret values while
  checking something; print keys or names only.
- Losing the state passphrase loses the state; bucket versioning does not help. Never
  generate a new passphrase for a backend that already has state.
- Cloud provider credentials are personal and are not handled by make. For UpCloud: the
  system keyring (`upctl account login`) or `UPCLOUD_TOKEN`. `~/.config/upctl.yaml` is
  supported, but tofu does not read it. The bootstrap script reads the environment and
  `upctl.yaml`, not the keyring. Never read or print the token itself.

## Workspaces and naming

- Each platform (test, prod) is a workspace. The workspace name is the environment name:
  resources are `arho-<workspace>-*` and labelled `project` and `environment`. Do not add
  an `environment` variable. The make targets refuse `default` and names that are not
  lowercase letters, digits and hyphens.
- Tenants are not workspaces. A cluster per tenant will come from the tenant registry in
  arho-deploy (ADR 0003), inside the platform's workspace.

## Resources to handle with care

- The NAT gateway's public address is the X-Road security server's address registered
  with DVV, and UpCloud cannot reserve it. `prevent_destroy` stays on; a plan that
  replaces the gateway is a stop, not something to work around.
- `private_network_cidr` is routed by customer VPNs and WireGuard, so it must stay an
  uncommon range and does not change once customers connect.
- The state bucket is created by `upcloud/bootstrap-state-bucket.sh`, not by OpenTofu, in
  an Object Storage service of its own, `arho-tfstate`, that holds only ARHO state. The
  whole service is protected: the script creates it with termination protection, because
  a bucket has no protection setting of its own. The script sets it only when it creates
  the service, not on a service that already exists.

## Checks

There are no tests here. After a change, run `tofu fmt -check -recursive` and
`tofu -chdir=<dir> validate` (after `make tf-init`, or `tofu init -backend=false`), and
show the `make tf-plan` output to a person before any apply. Never run `tf-apply`
without being asked.
