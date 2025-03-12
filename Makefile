run:
	@python3 main.py

test:
	@pytest

deploy:
	@echo "Deploying to Google App Engine..."
	@gcloud app deploy