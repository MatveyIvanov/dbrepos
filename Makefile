test:
	poetry run pytest .
unittest:
	poetry run pytest . -m unit
integrationtest:
	poetry run pytest . -m integration
lint:
	poetry run flake8 .
typecheck:
	poetry run mypy .
black:
	poetry run black .
isort:
	poetry run isort . --profile black --filter-files
