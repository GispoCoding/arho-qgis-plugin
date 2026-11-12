# Runs OpenTofu for the ARHO platforms on UpCloud with the deployment config from the private
# arho-deploy repository. Each backend there has a folder backends/<name>/ with
#   backend.hcl                         the state bucket and endpoint (plaintext)
#   credentials.enc.env                 the state access keys and the state encryption
#                                       passphrase (sops)
#   var-files/<workspace>.tfvars.enc.json   the variables of each platform (sops)
# The secrets are decrypted only while a command runs: the keys into its environment, the
# variable file into a temporary file that sops deletes afterwards.
#
# The UpCloud API token is not handled here. The provider reads it from UPCLOUD_TOKEN or from
# the system keyring (upctl account login --with-token).

# Defaults to a sibling checkout of this repository.
ARHO_DEPLOY_DIR ?= ../../arho-deploy
TOFU ?= tofu

WORKSPACE = $(shell $(TOFU) workspace show 2>/dev/null)
# make tf-init records the backend it used, so the other targets find its folder.
BACKEND := $(shell cat .terraform/backend-name 2>/dev/null)
BACKEND_DIR = backends/$(BACKEND)
CREDENTIALS = $(ARHO_DEPLOY_DIR)/$(BACKEND_DIR)/credentials.enc.env
TFVARS_ENC = $(BACKEND_DIR)/var-files/$(WORKSPACE).tfvars.enc.json

# with_secrets COMMAND: run COMMAND with the state keys in the environment and the decrypted
# variable file as {}. The file needs the .tfvars.json suffix, or tofu would read it as HCL.
with_secrets = sops exec-env $(CREDENTIALS) \
	"sops exec-file --no-fifo --filename vars.tfvars.json $(ARHO_DEPLOY_DIR)/$(TFVARS_ENC) '$(1)'"

.PHONY: check-backend tf-init tf-plan tf-apply edit-vars edit-credentials

check-backend:
	@$(if $(wildcard $(ARHO_DEPLOY_DIR)/.sops.yaml),,$(error arho-deploy not found in $(ARHO_DEPLOY_DIR). Set ARHO_DEPLOY_DIR=<path>))
	@$(if $(BACKEND),,$(error the backend is not known. Run make tf-init ws=<workspace> backend=<name>))

# Initialise the backend and select the workspace, creating it if needed. The workspace of the
# previous backend may not exist in this one, so it is forgotten first.
tf-init:
	@$(if $(ws),,$(error set ws=<workspace>, e.g. make tf-init ws=test backend=gispo-upcloud))
	@$(if $(backend),,$(error set backend=<name>, see $(ARHO_DEPLOY_DIR)/backends/))
	rm -f .terraform/environment .terraform/backend-name
	sops exec-env $(ARHO_DEPLOY_DIR)/backends/$(backend)/credentials.enc.env \
		'$(TOFU) init -reconfigure -backend-config=$(ARHO_DEPLOY_DIR)/backends/$(backend)/backend.hcl'
	mkdir -p .terraform && echo $(backend) > .terraform/backend-name
	sops exec-env $(ARHO_DEPLOY_DIR)/backends/$(backend)/credentials.enc.env \
		'$(TOFU) workspace select -or-create $(ws)'

tf-plan: check-backend
	$(call with_secrets,$(TOFU) plan -var-file={})

tf-apply: check-backend
	$(call with_secrets,$(TOFU) apply -var-file={})

# Edit, or create, the variable file of the current workspace in your editor. sops runs from
# the arho-deploy root, so it finds .sops.yaml and its path rules match.
edit-vars: check-backend
	cd $(ARHO_DEPLOY_DIR) && sops edit $(TFVARS_ENC)

# Edit, or create, the secrets of the current backend: AWS_ACCESS_KEY_ID and
# AWS_SECRET_ACCESS_KEY of the Object Storage user terraform, and
# TF_VAR_state_encryption_passphrase (encryption.tf).
edit-credentials: check-backend
	cd $(ARHO_DEPLOY_DIR) && sops edit $(BACKEND_DIR)/credentials.enc.env
