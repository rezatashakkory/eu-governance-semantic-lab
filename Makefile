# Thin wrappers around plain Python commands. Every target can also be run by hand,
# see the README. Run "make" from the repo root with your virtual environment active.

PYTHON ?= python

.PHONY: setup lint test validate build docs app all

# Install the project with the app and documentation extras, and the git hook.
setup:
	$(PYTHON) -m pip install -e ".[dev,app,docs]"
	$(PYTHON) -m pre_commit install

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .

test:
	$(PYTHON) -m pytest

# SHACL validation of the real data, plus a check that data/dist matches the Turtle files.
validate:
	$(PYTHON) -m semlab validate
	$(PYTHON) -m semlab check-dist

# Regenerate JSON-LD and RDF/XML in data/dist from the Turtle sources.
build:
	$(PYTHON) -m semlab build

# Regenerate the ontology documentation page and the translation review list.
docs:
	$(PYTHON) -m pylode data/ontology/legal-acts.ttl -o docs/ontology.html
	$(PYTHON) -m semlab translations

app:
	$(PYTHON) -m streamlit run app/streamlit_app.py

all: lint test validate
