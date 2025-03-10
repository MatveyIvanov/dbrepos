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
formatcheck:
	poetry run black . --check
sortcheck:
	poetry run isort . --profile black --filter-files --check
install-git-hooks:
	poetry run pre-commit install --hook-type pre-commit
uninstall-git-hooks:
	poetry run pre-commit uninstall -t pre-commit
