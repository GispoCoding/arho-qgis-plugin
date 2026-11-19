# Runs OpenTofu for the ARHO platforms with the deployment config from the private
# arho-deploy repository. Each OpenTofu configuration is a subdirectory here (upcloud/ for
# UpCloud); these targets work for any of them whose state is in an S3-compatible bucket.
#
# Each backend in arho-deploy has a folder backends/<backend>/ with
#   backend.hcl                         the state bucket and endpoint (plaintext)
#   credentials.enc.env                 the state access keys and the state encryption
#                                       passphrase (sops)
#   var-files/<workspace>.tfvars.enc.json   the variables of each platform (sops)
# The secrets are decrypted only while a command runs: the keys into its environment, the
# variable file into a temporary file that sops deletes afterwards.
#
# A configuration works with these targets when it has a partial backend "s3" block (bucket and
# endpoint come from backend.hcl), see upcloud/backend.tf. Every tofu command that touches the
# state runs through tofu-encrypted.sh, which encrypts the state with the passphrase of the
# backend, so the configurations have no encryption block of their own.
#
# The cloud provider credentials, e.g. the UpCloud API token, are not handled here. Each
# provider reads its own from the environment or the system keyring (see README).

# Defaults to a sibling checkout of this repository. Made absolute, because tofu resolves
# relative paths from the configuration directory.
ARHO_DEPLOY_DIR ?= ../../arho-deploy
ARHO_DEPLOY = $(abspath $(ARHO_DEPLOY_DIR))
# The tofu binary. tofu-encrypted.sh reads it from the environment.
TOFU ?= tofu
export TOFU

# The configuration directory. make tf-init dir=<directory> records it in .terraform-dir, so the
# other targets use it; dir=<directory> on any target overrides it for that command.
CONFIG_DIR := $(or $(dir),$(shell cat .terraform-dir 2>/dev/null))
TOFU_IN_DIR = $(CURDIR)/tofu-encrypted.sh -chdir=$(CONFIG_DIR)

# Reads only the local .terraform folder, so it needs no passphrase.
WORKSPACE = $(shell $(TOFU) -chdir=$(CONFIG_DIR) workspace show 2>/dev/null)
# make tf-init records the backend it used, so the other targets find its folder.
BACKEND = $(shell cat $(CONFIG_DIR)/.terraform/backend-name 2>/dev/null)
BACKEND_DIR = backends/$(BACKEND)
CREDENTIALS = $(ARHO_DEPLOY)/$(BACKEND_DIR)/credentials.enc.env
TFVARS_ENC = $(BACKEND_DIR)/var-files/$(WORKSPACE).tfvars.enc.json

# with_secrets COMMAND: run COMMAND with the state keys in the environment and the decrypted
# variable file as {}. The file needs the .tfvars.json suffix, or tofu would read it as HCL.
with_secrets = sops exec-env $(CREDENTIALS) \
	"sops exec-file --no-fifo --filename vars.tfvars.json $(ARHO_DEPLOY)/$(TFVARS_ENC) '$(1)'"

# check_workspace NAME: stop unless NAME can be a deployment workspace. Every deployment is a
# workspace, e.g. test or prod, and the configurations use its name as the environment name
# in resource names and labels. That rules out
# - the default workspace: its state would sit at the bare key, outside <prefix>/<workspace>/,
#   and it would name resources arho-default-*.
# - a name that is not valid in resource names and labels.
check_workspace = \
	if [ '$(1)' = default ]; then \
		echo "Select a deployment workspace first: make tf-init dir=<directory> ws=<environment> backend=<backend>." >&2; \
		exit 1; \
	fi; \
	if ! echo '$(1)' | grep -Eq '^[a-z][a-z0-9-]*$$'; then \
		echo "The workspace name \"$(1)\" is used as the environment name. Use lowercase letters, digits and hyphens, starting with a letter." >&2; \
		exit 1; \
	fi

.PHONY: check-deploy check-dir check-backend check-workspace tf-init tf-plan tf-apply edit-vars \
	edit-credentials

check-deploy:
	@$(if $(wildcard $(ARHO_DEPLOY)/.sops.yaml),,$(error arho-deploy not found in $(ARHO_DEPLOY). Set ARHO_DEPLOY_DIR=<path>))

check-dir:
	@$(if $(CONFIG_DIR),,$(error the configuration is not known. Run make tf-init dir=<directory> ws=<workspace> backend=<backend>))
	@$(if $(wildcard $(CONFIG_DIR)/*.tf),,$(error $(CONFIG_DIR)/ has no OpenTofu configuration))

check-backend: check-deploy check-dir
	@$(if $(BACKEND),,$(error the backend of $(CONFIG_DIR)/ is not known. Run make tf-init dir=$(CONFIG_DIR) ws=<workspace> backend=<backend>))

check-workspace: check-backend
	@$(call check_workspace,$(WORKSPACE))

# Initialise the backend of the configuration and select the workspace, creating it if
# needed. The workspace of the previous backend may not exist in this one, so it is
# forgotten first.
tf-init: check-deploy check-dir
	@$(if $(ws),,$(error set ws=<workspace>, e.g. make tf-init dir=upcloud ws=test backend=<backend>))
	@$(if $(backend),,$(error set backend=<backend>, see $(ARHO_DEPLOY)/backends/))
	@$(call check_workspace,$(ws))
	echo $(CONFIG_DIR) > .terraform-dir
	rm -f $(CONFIG_DIR)/.terraform/environment $(CONFIG_DIR)/.terraform/backend-name
	sops exec-env $(ARHO_DEPLOY)/backends/$(backend)/credentials.enc.env \
		'$(TOFU_IN_DIR) init -reconfigure -backend-config=$(ARHO_DEPLOY)/backends/$(backend)/backend.hcl'
	mkdir -p $(CONFIG_DIR)/.terraform && echo $(backend) > $(CONFIG_DIR)/.terraform/backend-name
	sops exec-env $(ARHO_DEPLOY)/backends/$(backend)/credentials.enc.env \
		'$(TOFU_IN_DIR) workspace select -or-create $(ws)'

tf-plan: check-workspace
	$(call with_secrets,$(TOFU_IN_DIR) plan -var-file={})

tf-apply: check-workspace
	$(call with_secrets,$(TOFU_IN_DIR) apply -var-file={})

# Edit, or create, the variable file of the current workspace in your editor. sops runs from
# the arho-deploy root, so it finds .sops.yaml and its path rules match.
edit-vars: check-workspace
	cd $(ARHO_DEPLOY) && sops edit $(TFVARS_ENC)

# Edit, or create, the secrets of the current backend: AWS_ACCESS_KEY_ID and
# AWS_SECRET_ACCESS_KEY of the state bucket user, and TF_VAR_state_encryption_passphrase.
edit-credentials: check-backend
	cd $(ARHO_DEPLOY) && sops edit $(BACKEND_DIR)/credentials.enc.env
