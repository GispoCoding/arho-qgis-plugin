
build:
	make build-lambda -C ..

push-lambdas: build push-db-manager push-koodistot-loader push-ryhti-client push-mml-loader
	echo "All pushed"

update-lambdas: update-db-manager update-koodistot-loader update-ryhti-client update-mml-loader
	echo "All updated"

push-db-manager:
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com
	docker tag arho-db_manager:latest $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(prefix)-db_manager:latest
	docker push $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(prefix)-db_manager:latest

update-db-manager: push-db-manager
	aws lambda update-function-code --function-name $(prefix)-db_manager --image-uri $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(prefix)-db_manager:latest

push-koodistot-loader:
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com
	docker tag arho-koodistot_loader:latest $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(prefix)-koodistot_loader:latest
	docker push $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(prefix)-koodistot_loader:latest

update-koodistot-loader: push-koodistot-loader
	aws lambda update-function-code --function-name $(prefix)-koodistot_loader --image-uri $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(prefix)-koodistot_loader:latest

## With ryhti client, we need to publish new version and update alias for provisioned concurrency.
## Also, we have to wait until update is complete to publish the new version.
push-ryhti-client:
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com
	docker tag arho-ryhti_client:latest $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(prefix)-ryhti_client:latest
	docker push $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(prefix)-ryhti_client:latest

update-ryhti-client: push-ryhti-client
	aws lambda update-function-code --function-name $(prefix)-ryhti_client --image-uri $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(prefix)-ryhti_client:latest
	while aws lambda get-function --function-name $(prefix)-ryhti_client --query "Configuration.LastUpdateStatus" | grep "InProgress" ; do sleep 1; echo "Waiting for AWS to complete function update..."; done
	aws lambda publish-version --function-name $(prefix)-ryhti_client --query "Version" | \
		xargs -I {} aws lambda update-alias --function-name $(prefix)-ryhti_client --name live --function-version {}

push-mml-loader:
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com
	docker tag arho-mml_loader:latest $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(prefix)-mml_loader:latest
	docker push $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(prefix)-mml_loader:latest

update-mml-loader: push-mml-loader
	aws lambda update-function-code --function-name $(prefix)-mml_loader --image-uri $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(prefix)-mml_loader:latest

log-db-manager:
	aws logs tail "/aws/lambda/$(prefix)-db_manager"

log-koodistot-loader:
	aws logs tail "/aws/lambda/$(prefix)-koodistot_loader"

log-ryhti-client:
	aws logs tail "/aws/lambda/$(prefix)-ryhti_client"

## Commands to invoke lambda functions
create-db:
	aws lambda invoke --cli-binary-format raw-in-base64-out --function-name $(prefix)-db_manager --payload '{"action": "create_db"}' ../logs/response_create_db.json

migrate-db:
	aws lambda invoke --cli-binary-format raw-in-base64-out --function-name $(prefix)-db_manager --payload '{"action": "migrate_db"}' ../logs/response_migrate_db.json

load-koodistot:
	aws lambda invoke --cli-binary-format raw-in-base64-out --function-name $(prefix)-koodistot_loader --payload '{}' ../logs/response_load_koodistot.json

load-mml:
	aws lambda invoke --cli-binary-format raw-in-base64-out --function-name $(prefix)-mml_loader --payload '{}' ../logs/response_load_mml.json


decrypt-workspace-secrets:
	sops -d public_keys/$(shell terraform workspace show).enc > public_keys/$(shell terraform workspace show)
	sops -d var-files/$(shell terraform workspace show).tfvars.enc.json > var-files/$(shell terraform workspace show).tfvars.json

encrypt-workspace-secrets:
	sops -e public_keys/$(shell terraform workspace show) > public_keys/$(shell terraform workspace show).enc
	sops -e var-files/$(shell terraform workspace show).tfvars.json > var-files/$(shell terraform workspace show).tfvars.enc.json
