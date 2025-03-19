run: clean
	@export DEV_ENVIRONMENT="true" && python3 main.py

test: clean
	@export DEV_ENVIRONMENT="true" && pytest
	@rm -rf _dev_database/

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