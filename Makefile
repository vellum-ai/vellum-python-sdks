SHELL := /bin/bash

################################
# Setup
################################

setup: setup-python setup-poetry install-deps setup-pre-commit setup-fern

setup-python:
	brew list python@3.9 || brew install python@3.9

setup-poetry:
	python3 -m scripts.install_poetry -y --version 1.8.3

# We use the full path to poetry to avoid any issues with the shell configuration from the setup-poetry step
install-deps:
	$(HOME)/.local/bin/poetry env use 3.9 && $(HOME)/.local/bin/poetry lock && $(HOME)/.local/bin/poetry install

setup-pre-commit:
	$(HOME)/.local/bin/poetry run pre-commit install \
	&& $(HOME)/.local/bin/poetry run pre-commit install -t pre-push

setup-node:
	command -v nvm >/dev/null 2>&1 || (curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash) \
	&& (nvm use $(cat ee/codegen/.nvmrc) || nvm install $(cat ee/codegen/.nvmrc))

setup-fern:
	which fern || npm install -g fern-api


################################
# Testing
################################

file ?= .
test:
	poetry run pytest -rEf -s -vv $(file)

# This used to be different from `make test`, but were aligned after we removed the auto-generated fern tests from `make test`
# Kept for now until users are migrated to the new `make test` command
file ?= .
test-raw:
	poetry run pytest -rEf -s -vv $(file) && echo '"make test-raw" is DEPRECATED. Use "make test" instead'

test-ci:
	poetry run pytest -rEf -s -vv $(file) --cov --cov-report=html --cov-report=term-missing


################################
# Linting
################################

format:
	poetry run black . \
	&& poetry run isort .

types:
	poetry run mypy .
