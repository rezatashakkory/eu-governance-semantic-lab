"""Smoke tests for the Streamlit app, using Streamlit's own test runner (no browser)."""

from pathlib import Path

import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402

APP = str(Path(__file__).resolve().parent.parent / "app" / "streamlit_app.py")
TIMEOUT = 120


@pytest.fixture
def app():
    at = AppTest.from_file(APP, default_timeout=TIMEOUT)
    at.run()
    return at


def test_app_starts_without_errors(app):
    assert not app.exception
    assert [t.label for t in app.tabs] == [
        "Overview",
        "Vocabulary Browser",
        "Acts and Graph",
        "SPARQL Playground",
        "Data Quality",
        "About and Method",
    ]
    assert app.title[0].value == "EU Data Governance Semantic Lab"


def test_disclaimer_is_shown(app):
    html = " ".join(m.value for m in app.markdown)
    assert "not affiliated with" in html.lower()


def test_overview_shows_the_numbers(app):
    metrics = {m.label: m.value for m in app.metric}
    assert metrics["Concepts"] == "68"
    assert metrics["Legal acts"] == "20"
    assert metrics["SPARQL queries"] == "15"
    assert metrics["SHACL"] == "Conforms"


def test_default_concept_card_is_data_protection(app):
    html = " ".join(m.value for m in app.markdown)
    assert "Data protection" in html
    assert "Rules and practices that protect individuals" in html


def test_language_switch_changes_labels(app):
    app.sidebar.selectbox[0].select("de").run()
    assert not app.exception
    html = " ".join(m.value for m in app.markdown)
    assert "Datenschutz" in html


def test_search_with_no_match_shows_a_friendly_message(app):
    app.text_input[0].set_value("zzzzqqqq").run()
    assert not app.exception
    assert any("No concept matches" in i.value for i in app.info)


def test_search_with_a_match_lists_concepts(app):
    app.text_input[0].set_value("breach").run()
    assert not app.exception
    assert any("1 concept(s) found" in c.value for c in app.caption)


def test_playground_runs_a_query(app):
    app.button[[b.label for b in app.button].index("Run query")].click().run()
    assert not app.exception
    assert not app.error
    assert len(app.dataframe) >= 2  # the acts table and the query result


def test_playground_rejects_an_update(app):
    app.text_area[0].set_value("DROP ALL").run()
    app.button[[b.label for b in app.button].index("Run query")].click().run()
    assert not app.exception
    assert any("could not be parsed" in e.value for e in app.error)


def test_data_quality_tab_reports_conformance(app):
    assert any("Conforms" in s.value for s in app.success)


def test_broken_example_fails_validation(app):
    labels = [b.label for b in app.button]
    app.button[labels.index("Validate with this example added")].click().run()
    assert not app.exception
    assert any("Does not conform" in e.value for e in app.error)
