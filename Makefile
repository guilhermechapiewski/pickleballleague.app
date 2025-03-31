run: clean
	@export DEV_ENVIRONMENT="true" && python3 main.py

test: clean
	@export DEV_ENVIRONMENT="true" && pytest --cache-clear --verbose --full-trace --color=yes --log-level=DEBUG --log-cli-level=DEBUG $(RUN_TEST_WITH_COVERAGE)
	@rm -rf _dev_database/

test-coverage: clean
	@export RUN_TEST_WITH_COVERAGE="--cov=app --cov-report=term-missing" && make test

deploy: clean test create_deployment_info
	@echo "Deploying to Google App Engine..."
	@gcloud app deploy

# Create/update version.py with latest git commit version and timestamp
create_deployment_info: clean
	@echo "Creating/updating version.py with latest git commit version and timestamp..."
	@echo "# AUTO-GENERATED file - run 'make deploy' or 'make create_deployment_info' to update" > version.py
	@echo "git_commit = '`git rev-parse HEAD`'" >> version.py
	@echo "deploy_timestamp = '`date '+%Y-%m-%d %H:%M:%S'`'" >> version.py

clean:
	@rm -f version.py
	@rm -rf _dev_database/