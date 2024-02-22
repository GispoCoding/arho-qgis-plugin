
build:
	make build-lambda -C ..

update-lambda: update-db-manager update-koodistot-loader
	echo "All updated"

update-db-manager:
	aws lambda update-function-code --function-name $(prefix)-db_manager --zip-file fileb://../db_manager.zip

update-koodistot-loader:
	aws lambda update-function-code --function-name $(prefix)-koodistot_loader --zip-file fileb://../koodistot_loader.zip

log-db-manager:
	aws logs tail "/aws/lambda/$(prefix)-db_manager"

log-koodistot-loader:
	aws logs tail "/aws/lambda/$(prefix)-koodistot_loader"

## Commands to invoke lambda functions
create-db:
	aws lambda invoke --cli-binary-format raw-in-base64-out --function-name $(prefix)-db_manager --payload '{"event_type": 1}' response_db.json

change-db-pw:
	aws lambda invoke --cli-binary-format raw-in-base64-out --function-name $(prefix)-db_manager --payload '{"event_type": 2}' response_db.json

migrate-db:
	aws lambda invoke --cli-binary-format raw-in-base64-out --function-name $(prefix)-db_manager --payload '{"event_type": 3}' response_db.json

load-koodistot:
	aws lambda invoke --cli-binary-format raw-in-base64-out --function-name $(prefix)-koodistot_loader --payload '{}' response_db.json
