.PHONY: help build up down install uninstall reinstall version lint format security clean
.DEFAULT_GOAL := help
VENV = venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip

define PRINT_HELP_PYSCRIPT
import re, sys
for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?$$', line)
	if match:
		target = match.groups()
		print("%s" % (target))
endef
export PRINT_HELP_PYSCRIPT

$(VENV)/bin/activate: requirements-dev.txt requirements.txt
	@python3 -m venv $(VENV)
	@$(PIP) install -U pip
	@$(PIP) install -r requirements-dev.txt

help:
	@python3 -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

build:
	@docker-compose build

up:
	@docker-compose up

down:
	@docker-compose down --rmi all --volumes --remove-orphans

install: $(VENV)/bin/activate
	@$(VENV)/bin/pre-commit install
	@$(VENV)/bin/pre-commit install --hook-type commit-msg
	@test -e .env || cp .env.sample .env

uninstall:
	-@$(VENV)/bin/pre-commit uninstall
	@rm -rf $(VENV)

reinstall: uninstall install

version: $(VENV)/bin/activate
	@$(PYTHON) --version
	@$(PIP) freeze

lint: $(VENV)/bin/activate
	@$(VENV)/bin/pre-commit run mypy
	@$(VENV)/bin/pre-commit run ruff

formatter: $(VENV)/bin/activate
	@$(VENV)/bin/pre-commit run black
	@$(VENV)/bin/pre-commit run isort
	@$(VENV)/bin/pre-commit run check-docstring-first
	@$(VENV)/bin/pre-commit run end-of-file-fixer
	@$(VENV)/bin/pre-commit run trailing-whitespace

format: formatter

security: $(VENV)/bin/activate
	@$(VENV)/bin/pre-commit run bandit
	@$(VENV)/bin/pre-commit run detect-private-key
	@$(VENV)/bin/pre-commit run debug-statements

clean:
	-@rm -fr build/
	-@rm -fr dist/
	-@rm -fr .eggs/
	-@find . -name '*.egg-info' -exec rm -fr {} +
	-@find . -name '*.egg' -exec rm -f {} +
	-@find . -name '*.pyc' -exec rm -f {} +
	-@find . -name '*.pyo' -exec rm -f {} +
	-@find . -name '*~' -exec rm -f {} +
	-@find . -name '__pycache__' -exec rm -fr {} +
	-@rm -fr .tox/
	-@rm -fr .nox/
	-@rm -f .coverage
	-@rm -fr htmlcov/
	-@rm -fr .pytest_cache
	-@rm -fr .mypy_cache
	-@rm -fr .ruff_cache
