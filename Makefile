SHELL := /bin/bash

################################
# Setup
################################

setup: setup-python setup-poetry install-deps setup-pre-commit setup-node setup-fern

setup-python:
	brew list python@3.9 || brew install python@3.9

setup-poetry:
	python3 -m scripts.install_poetry -y --version 1.8.3 \
	&& $(HOME)/.local/bin/poetry config virtualenvs.in-project true \
	&& $(HOME)/.local/bin/poetry config virtualenvs.create true

# We use the full path to poetry to avoid any issues with the shell configuration from the setup-poetry step
install-deps:
	$(HOME)/.local/bin/poetry env use 3.9 && $(HOME)/.local/bin/poetry lock && $(HOME)/.local/bin/poetry install

setup-pre-commit:
	$(HOME)/.local/bin/poetry run pre-commit install \
	&& $(HOME)/.local/bin/poetry run pre-commit install -t pre-push

setup-node:
	$(HOME)/.nvm/nvm.sh use $$(cat ee/codegen/.nvmrc) || $(HOME)/.nvm/nvm.sh install $$(cat ee/codegen/.nvmrc)

setup-fern:
	which fern || npm install -g fern-api


################################
# Testing
################################

file ?= .
test:
	poetry run pytest -rEf -s -vv -n 4 $(file)

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

generate-node-definitions:
	poetry run generate_node_definitions
