include ./.env

dev-create-db:
	@echo "Creating Hame database..."
	curl -XPOST "http://localhost:8081/2015-03-31/functions/function/invocations" -d '{"action" : "create_db"}'

dev-migrate-db:
	@echo "Migrating Hame database..."
	@if [ -n "$(version)" ]; then \
		DATA='{"action": "migrate_db", "version": "$(version)"}'; \
	else \
		DATA='{"action": "migrate_db"}'; \
	fi; \
	curl -XPOST "http://localhost:8081/2015-03-31/functions/function/invocations" -d "$$DATA"

dev-users:
	docker compose -f docker-compose.dev.yml run --rm -e PGPASSWORD=postgres db psql -U postgres -h db -c "\
		CREATE ROLE admin LOGIN PASSWORD 'admin';\
		GRANT arho_admin TO admin;\
		CREATE ROLE rw_user LOGIN PASSWORD 'rw_user';\
		GRANT arho_read_write TO rw_user;\
		CREATE ROLE ro_user LOGIN PASSWORD 'ro_user';\
		GRANT arho_read_only TO ro_user;\
	"

dev-populate-test-data:
	@echo "Populating database with test data..."
	docker compose -f docker-compose.dev.yml run --rm db pg_restore -h db -d hame -U postgres --disable-triggers /opt/pg_backups/sample_data.dump

dev-koodistot:
	@echo "Loading Koodistot data..."
	curl -XPOST "http://localhost:8082/2015-03-31/functions/function/invocations" -d '{}'
	curl -XPOST "http://localhost:8085/2015-03-31/functions/function/invocations" -d '{}'

dev-setup-db: up dev-create-db dev-migrate-db dev-users dev-koodistot
	@echo "Development database is set up"

dev-ryhti-validate:
	@echo "Validating database contents with Ryhti API..."
	curl -XPOST "http://localhost:8083/2015-03-31/functions/function/invocations" -d '{"action": "validate_plans"}'

pytest-fail:
	pytest --maxfail=1

up:
	docker compose -f docker-compose.dev.yml up -d

dev-debug-ryhti:
	@echo "Starting ryhti_client with debugpy on port 5678..."
	docker compose -f docker-compose.dev.yml -f docker-compose.debug.yml up -d --force-recreate ryhti_client

stop:
	docker compose -f docker-compose.dev.yml stop

down:
	docker compose -f docker-compose.dev.yml down -v

build-lambda:
	docker compose -f docker-compose.dev.yml build db_manager koodistot_loader ryhti_client mml_loader

revision:
	DBA_USER=$(DBA_USER) \
	DBA_USER_PW=$(DBA_USER_PW) \
	DB_MAIN_NAME=$(DB_MAIN_NAME) \
	DB_INSTANCE_ADDRESS=$(DB_INSTANCE_ADDRESS) \
	DB_INSTANCE_PORT=$(DB_INSTANCE_PORT) \
	alembic revision --autogenerate -m "$(name)"

downgrade:
	DBA_USER=$(DBA_USER) \
	DBA_USER_PW=$(DBA_USER_PW) \
	DB_MAIN_NAME=$(DB_MAIN_NAME) \
	DB_INSTANCE_ADDRESS=$(DB_INSTANCE_ADDRESS) \
	DB_INSTANCE_PORT=$(DB_INSTANCE_PORT) \
	alembic downgrade -1

pip-compile:
	pip-compile requirements.in
	pip-compile requirements-dev.in
	pip-compile lambdas/db_manager/requirements.in
	pip-compile lambdas/koodistot_loader/requirements.in
	pip-compile lambdas/mml_loader/requirements.in
	pip-compile lambdas/ryhti_client/requirements.in
