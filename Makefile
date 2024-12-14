# Any args passed to the make script, use with $(call args, default_value)
args = `arg="$(filter-out $@,$(MAKECMDGOALS))" && echo $${arg:-${1}}`

########################################################################################################################
# Quality checks
########################################################################################################################

test:
	PYTHONPATH=. poetry run pytest tests

test-coverage:
	PYTHONPATH=. poetry run pytest tests --cov u_copilot --cov-report term --cov-report=html --cov-report xml --junit-xml=tests-results.xml

black:
	poetry run black . --check

ruff:
	poetry run ruff check u_copilot tests

format:
	poetry run black .
	poetry run ruff check u_copilot tests --fix

mypy:
	poetry run mypy u_copilot

check:
	make format
	make mypy

########################################################################################################################
# Run
########################################################################################################################

run:
	poetry run python -m u_copilot

dev-windows:
	(set PGPT_PROFILES=local & poetry run python -m uvicorn u_copilot.main:app --reload --port 50004)

dev:
	PYTHONUNBUFFERED=1 PGPT_PROFILES=local poetry run python -m uvicorn u_copilot.main:app --reload --port 50004 

########################################################################################################################
# Misc
########################################################################################################################

api-docs:
	PGPT_PROFILES=mock poetry run python scripts/extract_openapi.py u_copilot.main:app --out fern/openapi/openapi.json

ingest:
	@poetry run python scripts/ingest_folder.py $(call args)

wipe:
	poetry run python scripts/utils.py wipe

setup:
	poetry run python scripts/setup
