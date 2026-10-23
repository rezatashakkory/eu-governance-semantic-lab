# Thin wrappers around plain Python commands. Every target can also be run by hand,
# see the README. Run "make" from the repo root with your virtual environment active.

PYTHON ?= python

.PHONY: setup lint test validate docs app all

setup:
	$(PYTHON) -m pip install -e ".[dev]"
	$(PYTHON) -m pre_commit install

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .

test:
	$(PYTHON) -m pytest

# The next three targets are filled in during later phases.
validate:
	@echo "validate: SHACL validation is added in Phase 5."

docs:
	@echo "docs: ontology documentation is added in Phase 7."

app:
	@echo "app: the Streamlit app is added in Phase 6."

all: lint test validate
