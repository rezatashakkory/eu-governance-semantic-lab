# EU Data Governance Semantic Lab

A small linked data stack about EU data and AI regulation: a multilingual SKOS thesaurus, an OWL ontology for legal acts, a dataset of real EU acts with DCAT metadata, SHACL data quality shapes, documented SPARQL queries, and a web app to explore it all.

> **Status:** work in progress. Phase 0 (project setup) is complete. Later phases add the data and the app.

## Disclaimer

This is an independent learning project. It is not affiliated with, endorsed by, or an official product of the Publications Office of the European Union or any other EU institution. It uses only public sources.

## Quickstart

Requires Python 3.11 or newer.

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS and Linux:    source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest
python -m ruff check .
```

If you have `make`, the same steps are available as `make setup`, `make test` and `make lint`.

## License

Code: MIT, see [LICENSE](LICENSE).
