test-create-db:
	@echo "Creating Hame database..."
	curl -XPOST "http://localhost:8081/2015-03-31/functions/function/invocations" -d '{"event_type" : 1}'

test-migrate-db:
	@echo "Migrating Hame database..."
	curl -XPOST "http://localhost:8081/2015-03-31/functions/function/invocations" -d '{"event_type" : 3}'

pytest:
	docker-compose -f docker-compose.dev.yml down -v
	docker-compose -f docker-compose.dev.yml build db_manager
	cd database; pytest

rebuild:
	docker-compose -f docker-compose.dev.yml down -v
	docker-compose -f docker-compose.dev.yml build db_manager
	docker-compose -f docker-compose.dev.yml up -d

build-lambda:
	docker-compose -f docker-compose.dev.yml build db_manager
	docker-compose -f docker-compose.dev.yml up -d --no-deps db_manager
	for func in db_manager ; do \
  	  rm -rf tmp_lambda; \
  	  echo $$func; \
	  docker cp hame-ryhti_$${func}_1:/var/task tmp_lambda; \
	  cd tmp_lambda; \
	  zip -r ../"$${func}.zip" .; \
	  cd ..; \
	  rm -rf tmp_lambda; \
	done
	docker-compose -f docker-compose.dev.yml down -v

revision:
	cd database; \
	alembic revision --autogenerate -m "$(name)"; \
	cd ..
