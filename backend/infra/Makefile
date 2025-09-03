
build:
	make build-lambda -C ..

update-lambda: update-db-manager update-koodistot-loader update-ryhti-client update-mml-loader
	echo "All updated"

update-db-manager:
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com
	docker tag arho-ryhti-db_manager:latest $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(prefix)-db_manager:latest
	docker push $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(prefix)-db_manager:latest
	aws lambda update-function-code --function-name $(prefix)-db_manager --image-uri $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(prefix)-db_manager:latest

update-koodistot-loader:
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com
	docker tag arho-ryhti-koodistot_loader:latest $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(prefix)-koodistot_loader:latest
	docker push $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(prefix)-koodistot_loader:latest
	aws lambda update-function-code --function-name $(prefix)-koodistot_loader --image-uri $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(prefix)-koodistot_loader:latest

## With ryhti client, we need to publish new version and update alias for provisioned concurrency.
## Also, we have to wait until update is complete to publish the new version.
update-ryhti-client:
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com
	docker tag arho-ryhti-ryhti_client:latest $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(prefix)-ryhti_client:latest
	docker push $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(prefix)-ryhti_client:latest
	aws lambda update-function-code --function-name $(prefix)-ryhti_client --image-uri $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(prefix)-ryhti_client:latest
	while aws lambda get-function --function-name $(prefix)-ryhti_client --query "Configuration.LastUpdateStatus" | grep "InProgress" ; do sleep 1; echo "Waiting for AWS to complete function update..."; done
	aws lambda publish-version --function-name $(prefix)-ryhti_client --query "Version" | \
		xargs -I {} aws lambda update-alias --function-name $(prefix)-ryhti_client --name live --function-version {}

update-mml-loader:
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com
	docker tag arho-ryhti-mml_loader:latest $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(prefix)-mml_loader:latest
	docker push $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(prefix)-mml_loader:latest
	aws lambda update-function-code --function-name $(prefix)-mml_loader --image-uri $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(prefix)-mml_loader:latest

log-db-manager:
	aws logs tail "/aws/lambda/$(prefix)-db_manager"

log-koodistot-loader:
	aws logs tail "/aws/lambda/$(prefix)-koodistot_loader"

log-ryhti-client:
	aws logs tail "/aws/lambda/$(prefix)-ryhti_client"

## Commands to invoke lambda functions
create-db:
	aws lambda invoke --cli-binary-format raw-in-base64-out --function-name $(prefix)-db_manager --payload '{"action": "create_db"}' response_db.json

change-db-pw:
	aws lambda invoke --cli-binary-format raw-in-base64-out --function-name $(prefix)-db_manager --payload '{"action": "change_pws"}' response_db.json

migrate-db:
	aws lambda invoke --cli-binary-format raw-in-base64-out --function-name $(prefix)-db_manager --payload '{"action": "migrate_db"}' response_db.json

load-koodistot:
	aws lambda invoke --cli-binary-format raw-in-base64-out --function-name $(prefix)-koodistot_loader --payload '{}' response_koodistot.json

validate-plans:
	aws lambda invoke --cli-binary-format raw-in-base64-out --function-name $(prefix)-ryhti_client --payload '{"action": "validate_plans"}' response_ryhti.json

get-plans:
	aws lambda invoke --cli-binary-format raw-in-base64-out --function-name $(prefix)-ryhti_client --payload '{"action": "get_plans"}' response_ryhti.json

decrypt-ssh-keys:
	sops -d public_keys/$(shell terraform workspace show).enc > public_keys/$(shell terraform workspace show)

encrypt-ssh-keys:
	sops -e public_keys/$(shell terraform workspace show) > public_keys/$(shell terraform workspace show).enc
