test:
	poetry run pytest .
lint:
	poetry run flake8 .
typecheck:
	poetry run mypy .
black:
	poetry run black .
isort:
	poetry run isort . --profile black --filter-files
