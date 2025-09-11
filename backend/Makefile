test-create-db:
	@echo "Creating Hame database..."
	curl -XPOST "http://localhost:8081/2015-03-31/functions/function/invocations" -d '{"action" : "create_db"}'

test-migrate-db:
	@echo "Migrating Hame database..."
	curl -XPOST "http://localhost:8081/2015-03-31/functions/function/invocations" -d '{"action" : "migrate_db"}'

test-populate-test-data:
	@echo "Populating database with test data..."
	docker compose -f docker-compose.dev.yml run --rm db pg_restore -h db -d hame -U postgres --disable-triggers /opt/pg_backups/sample_data.dump

test-koodistot:
	@echo "Loading Koodistot data..."
	curl -XPOST "http://localhost:8082/2015-03-31/functions/function/invocations" -d '{}'
	curl -XPOST "http://localhost:8085/2015-03-31/functions/function/invocations" -d '{}'

test-ryhti-validate:
	@echo "Validating database contents with Ryhti API..."
	curl -XPOST "http://localhost:8083/2015-03-31/functions/function/invocations" -d '{"action": "validate_plans"}'

pytest-fail:
	pytest --maxfail=1

up:
	docker compose -f docker-compose.dev.yml up -d

stop:
	docker compose -f docker-compose.dev.yml stop

down:
	docker compose -f docker-compose.dev.yml down -v

build-lambda:
	docker compose -f docker-compose.dev.yml build db_manager koodistot_loader ryhti_client mml_loader

revision:
	alembic revision --autogenerate -m "$(name)"; \

pip-compile:
	pip-compile requirements.in
	pip-compile requirements-dev.in
	pip-compile lambdas/db_manager/requirements.in
	pip-compile lambdas/koodistot_loader/requirements.in
	pip-compile lambdas/mml_loader/requirements.in
	pip-compile lambdas/ryhti_client/requirements.in
