# Path to the private GispoCoding/arho-deploy checkout that holds the instance
# specific configuration (var-files/, public_keys/, .sops.yaml).
# Defaults to a sibling checkout of this repository.
ARHO_DEPLOY_DIR ?= ../../arho-deploy
WORKSPACE = $(shell terraform workspace show)
TFVARS := $(ARHO_DEPLOY_DIR)/var-files/$(WORKSPACE).tfvars.json
TFVARS_ENC := $(ARHO_DEPLOY_DIR)/var-files/$(WORKSPACE).tfvars.enc.json

# The deployment values come from the decrypted variable file of the current
# terraform workspace and from the AWS credentials in use, so that a make target
# cannot use a different prefix, region or account than the one terraform deploys
# to. Set any of them in the environment or on the command line to work without a
# variable file. Simple assignment, so each value is looked up once per make run
# instead of once per reference.
ifndef prefix
prefix := $(shell jq -re '.prefix // empty' $(TFVARS) 2>/dev/null)
endif
ifndef AWS_REGION
AWS_REGION := $(shell jq -re '.AWS_REGION_NAME // empty' $(TFVARS) 2>/dev/null)
endif
ifndef AWS_ACCOUNT_ID
AWS_ACCOUNT_ID := $(shell aws sts get-caller-identity --query Account --output text 2>/dev/null)
endif

# create-db, migrate-db and the log targets give the aws cli no --region option, so
# they relied on the region being exported. Export it from here instead.
export AWS_REGION

# The aws cli v2 sends output to a pager when it writes to a terminal, which stops a
# make recipe until the pager is closed. An empty AWS_PAGER disables the pager. CI
# never saw this, because the cli uses no pager when the output is not a terminal.
export AWS_PAGER :=

build:
	make build-lambda -C ..

# The likely causes of an empty value are a variable file that is still encrypted and
# an expired MFA session, so say that instead of letting aws fail on a malformed
# resource name.
check-deployment-vars:
	@$(if $(and $(prefix),$(AWS_REGION),$(AWS_ACCOUNT_ID)),,$(error prefix, AWS_REGION and AWS_ACCOUNT_ID are not all set. Run `make decrypt-workspace-secrets` for workspace "$(WORKSPACE)" and check that your AWS session is valid, or pass the values on the command line))

push-lambdas: build push-db-manager push-koodistot-loader push-ryhti-client push-mml-loader
	echo "All pushed"

update-lambdas: update-db-manager update-koodistot-loader update-ryhti-client update-mml-loader
	echo "All updated"

push-db-manager: check-deployment-vars
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com
	docker tag arho-db_manager:latest $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(prefix)-db_manager:latest
	docker push $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(prefix)-db_manager:latest

update-db-manager: push-db-manager
	aws lambda update-function-code --function-name $(prefix)-db_manager --image-uri $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(prefix)-db_manager:latest

push-koodistot-loader: check-deployment-vars
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com
	docker tag arho-koodistot_loader:latest $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(prefix)-koodistot_loader:latest
	docker push $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(prefix)-koodistot_loader:latest

update-koodistot-loader: push-koodistot-loader
	aws lambda update-function-code --function-name $(prefix)-koodistot_loader --image-uri $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(prefix)-koodistot_loader:latest

## With ryhti client, we need to publish new version and update alias for provisioned concurrency.
## Also, we have to wait until update is complete to publish the new version.
push-ryhti-client: check-deployment-vars
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com
	docker tag arho-ryhti_client:latest $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(prefix)-ryhti_client:latest
	docker push $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(prefix)-ryhti_client:latest

update-ryhti-client: push-ryhti-client
	aws lambda update-function-code --function-name $(prefix)-ryhti_client --image-uri $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(prefix)-ryhti_client:latest
	while aws lambda get-function --function-name $(prefix)-ryhti_client --query "Configuration.LastUpdateStatus" | grep "InProgress" ; do sleep 1; echo "Waiting for AWS to complete function update..."; done
	aws lambda publish-version --function-name $(prefix)-ryhti_client --query "Version" | \
		xargs -I {} aws lambda update-alias --function-name $(prefix)-ryhti_client --name live --function-version {}

push-mml-loader: check-deployment-vars
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com
	docker tag arho-mml_loader:latest $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(prefix)-mml_loader:latest
	docker push $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(prefix)-mml_loader:latest

update-mml-loader: push-mml-loader
	aws lambda update-function-code --function-name $(prefix)-mml_loader --image-uri $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(prefix)-mml_loader:latest

log-db-manager: check-deployment-vars
	aws logs tail "/aws/lambda/$(prefix)-db_manager"

log-koodistot-loader: check-deployment-vars
	aws logs tail "/aws/lambda/$(prefix)-koodistot_loader"

log-ryhti-client: check-deployment-vars
	aws logs tail "/aws/lambda/$(prefix)-ryhti_client"

## Commands to invoke lambda functions
create-db: check-deployment-vars
	aws lambda invoke --cli-binary-format raw-in-base64-out --function-name $(prefix)-db_manager --payload '{"action": "create_db"}' ../logs/response_create_db.json

migrate-db: check-deployment-vars
	aws lambda invoke --cli-binary-format raw-in-base64-out --function-name $(prefix)-db_manager --payload '{"action": "migrate_db"}' ../logs/response_migrate_db.json

load-koodistot: check-deployment-vars
	aws lambda invoke --region $(AWS_REGION) --cli-binary-format raw-in-base64-out --function-name $(prefix)-koodistot_loader --payload '{}' ../logs/response_load_koodistot.json

load-mml: check-deployment-vars
	aws lambda invoke --region $(AWS_REGION) --cli-binary-format raw-in-base64-out --function-name $(prefix)-mml_loader --payload '{}' ../logs/response_load_mml.json


decrypt-workspace-secrets:
	sops -d $(ARHO_DEPLOY_DIR)/public_keys/$(WORKSPACE).enc > $(ARHO_DEPLOY_DIR)/public_keys/$(WORKSPACE)
	sops -d $(TFVARS_ENC) > $(TFVARS)

# sops discovers .sops.yaml from the working directory, so the config of the
# arho-deploy repository must be passed explicitly when encrypting from here.
encrypt-workspace-secrets:
	sops --config $(ARHO_DEPLOY_DIR)/.sops.yaml -e $(ARHO_DEPLOY_DIR)/public_keys/$(WORKSPACE) > $(ARHO_DEPLOY_DIR)/public_keys/$(WORKSPACE).enc
	sops --config $(ARHO_DEPLOY_DIR)/.sops.yaml -e $(TFVARS) > $(TFVARS_ENC)

# A lambda function cannot be created before its container image exists in ECR, and
# terraform does not build or push images. So the first deployment creates the four
# repositories on their own, pushes the images with push-lambdas, and only then runs
# tf-apply for the rest of the infrastructure.
tf-bootstrap-ecr:
	terraform apply -var-file=$(TFVARS) \
		-target=aws_ecr_repository.db_manager \
		-target=aws_ecr_repository.koodistot_loader \
		-target=aws_ecr_repository.ryhti_client \
		-target=aws_ecr_repository.mml_loader

tf-plan:
	terraform plan -var-file=$(TFVARS)

tf-apply:
	terraform apply -var-file=$(TFVARS)

update-ssh-keys:
	ansible-playbook ansible/playbook.yml \
	-i ansible/inventory/hosts.yml \
	--extra-vars " \
		bastion_host=$(shell terraform output -raw bastion_address) \
		ssh_key_file=$(abspath $(ARHO_DEPLOY_DIR))/public_keys/$(WORKSPACE) \
	" \
	$(if $(ssh_private_key),--private-key $(ssh_private_key))

# The bastion reads its host key from SSM, so the fingerprint can be verified
# against SSM instead of being accepted blindly on the first connection.
# Append the printed line to your known hosts:
#   make bastion-known-host >> ~/.ssh/known_hosts
bastion-known-host: check-deployment-vars
	@key=$$(mktemp) && trap 'rm -f "$$key"' EXIT && \
	aws ssm get-parameter \
		--name "/infra/$(prefix)-bastion/host_key_ed25519" \
		--with-decryption --query Parameter.Value --output text > "$$key" && \
	echo "$$(terraform output -raw bastion_address) $$(ssh-keygen -y -f "$$key" | cut -d' ' -f1,2)"
