"""Every documented query runs and returns the documented result."""

import re

import pytest
from rdflib import Graph

from semlab.namespaces import CPT
from semlab.queries import QueryError, QueryTimeout, list_queries, run_query


@pytest.fixture(scope="module")
def queries():
    return {q.number: q for q in list_queries()}


def select(graph, queries, number):
    result = run_query(graph, queries[number].text)
    assert result.kind == "select"
    return result


def test_fifteen_documented_queries_with_headers(queries):
    assert len(queries) == 15
    for q in queries.values():
        assert (
            q.title and q.purpose and q.expected and q.level in {"easy", "intermediate", "advanced"}
        )


def test_every_query_runs(graph, queries):
    for q in queries.values():
        run_query(graph, q.text)


def test_01_top_concepts(graph, queries):
    result = select(graph, queries, "01")
    labels = [row[1].replace(" (en)", "") for row in result.rows]
    assert labels == sorted(labels)
    assert set(labels) == {
        "AI governance",
        "Data governance",
        "Data protection",
        "Data quality and metadata",
        "Digital resilience",
        "Open data and reuse",
    }


def test_02_labels_in_three_languages(graph, queries):
    result = select(graph, queries, "02")
    assert len(result.rows) == 68
    assert all(row[2] and row[3] for row in result.rows)  # no empty French or German cell
    by_en = {row[1]: row for row in result.rows}
    assert by_en["Data controller (en)"][2] == "responsable du traitement (fr)"
    assert by_en["Data controller (en)"][3] == "Verantwortlicher (de)"


def test_03_search_by_keyword(graph, queries):
    labels = {row[1].replace(" (en)", "") for row in select(graph, queries, "03").rows}
    assert labels == {"ICT incident", "Incident reporting", "Personal data breach"}


def test_04_direct_narrower(graph, queries):
    result = select(graph, queries, "04")
    assert len(result.rows) == 11
    labels = {row[1] for row in result.rows}
    assert "Personal data (en)" in labels
    assert "Special categories of personal data (en)" not in labels  # that one is two levels down


def test_05_all_descendants(graph, queries):
    result = select(graph, queries, "05")
    assert len(result.rows) == 14
    labels = {row[1] for row in result.rows}
    assert {
        "Special categories of personal data (en)",
        "Right to erasure (en)",
        "Data portability (en)",
    } <= labels


def test_06_ancestors(graph, queries):
    labels = {row[1] for row in select(graph, queries, "06").rows}
    assert labels == {"Data subject (en)", "Data protection (en)"}


def test_07_counts_add_up_to_all_concepts(graph, queries):
    result = select(graph, queries, "07")
    counts = {row[0]: int(row[1]) for row in result.rows}
    assert counts == {
        "Data protection (en)": 14,
        "Data quality and metadata (en)": 12,
        "AI governance (en)": 11,
        "Digital resilience (en)": 9,
        "Data governance (en)": 8,
        "Open data and reuse (en)": 8,
    }
    assert sum(counts.values()) + 6 == 68


def test_08_missing_translations_is_empty_on_real_data(graph, queries):
    assert select(graph, queries, "08").rows == []


def test_08_finds_a_deliberately_missing_translation(with_extra, queries):
    result = select(with_extra("broken_missing_translations.ttl"), queries, "08")
    assert sorted(row[2] for row in result.rows) == ["de", "fr"]
    assert all(row[1] == "Broken test (en)" for row in result.rows)


def test_09_eurovoc_alignments(graph, queries):
    result = select(graph, queries, "09")
    kinds = [row[2] for row in result.rows]
    assert len(kinds) == 19
    assert kinds.count("exactMatch") == 10
    assert kinds.count("closeMatch") == 4
    assert kinds.count("broadMatch") == 5
    data_protection = next(r for r in result.rows if r[1] == "Data protection (en)")
    assert data_protection[3] == "http://eurovoc.europa.eu/5181"


def test_10_acts_overview(graph, queries):
    result = select(graph, queries, "10")
    assert len(result.rows) == 20
    dates = [row[3] for row in result.rows]
    assert dates == sorted(dates)
    assert result.rows[0][4] == "31995L0046"  # the oldest act, the 1995 directive
    assert result.rows[-1][4] == "32025R0327"  # the newest, the Health Data Space regulation


def test_11_acts_by_topic_with_narrower(graph, queries):
    celex = {row[2] for row in select(graph, queries, "11").rows}
    assert celex == {
        "31995L0046",
        "32002L0058",
        "32016L0680",
        "32016R0679",
        "32018R1725",
        "32025R0327",
    }


def test_12_legal_relations(graph, queries):
    rows = {tuple(row) for row in select(graph, queries, "12").rows}
    assert rows == {
        ("32022L2555", "amends", "32014R0910"),
        ("32024R1183", "amends", "32014R0910"),
        ("32025R0327", "amends", "32024R2847"),
        ("32016R0679", "repeals", "31995L0046"),
        ("32019L1024", "repeals", "32003L0098"),
        ("32023R0138", "is based on", "32019L1024"),
    }


def test_13_acts_per_type(graph, queries):
    counts = {row[0]: int(row[1]) for row in select(graph, queries, "13").rows}
    assert counts == {"Regulation": 12, "Directive": 7, "ImplementingRegulation": 1}


def test_14_ask_is_false_on_real_data_and_true_on_broken_data(graph, queries):
    assert run_query(graph, queries["14"].text).boolean is False
    broken = Graph()
    for triple in graph:
        broken.add(triple)
    broken.parse(
        data=(
            "@prefix skos: <http://www.w3.org/2004/02/skos/core#> ."
            f"<{CPT['no-definition']}> a skos:Concept ."
        ),
        format="turtle",
    )
    assert run_query(broken, queries["14"].text).boolean is True


def test_15_construct_builds_a_graph_with_every_act(graph, queries):
    result = run_query(graph, queries["15"].text)
    assert result.kind == "construct"
    from rdflib.namespace import DCTERMS

    acts_with_subject = set(result.graph.subjects(DCTERMS.subject, None))
    assert len(acts_with_subject) == 20


def test_reasoning_makes_has_topic_alone_enough(graph):
    """Acts link to Interoperability only through lab:regulates, a sub-property of
    lab:hasTopic. Plain SPARQL finds nothing with hasTopic alone, the reasoned graph finds four."""
    from semlab.loading import ONTOLOGY_FILE, load_graph
    from semlab.reasoning import expand

    text = """
        PREFIX lab: <https://rezatashakkory.github.io/eu-governance-semantic-lab/def/>
        PREFIX cpt: <https://rezatashakkory.github.io/eu-governance-semantic-lab/id/concept/>
        SELECT DISTINCT ?act WHERE { ?act lab:hasTopic cpt:interoperability }
    """
    expanded, _ = expand(graph, load_graph(ONTOLOGY_FILE))
    assert run_query(graph, text).rows == []
    assert len(run_query(expanded, text).rows) == 4


# ---- Playground safety ----------------------------------------------------------------


@pytest.mark.parametrize(
    "text",
    [
        "INSERT DATA { <http://example.org/a> <http://example.org/b> <http://example.org/c> }",
        "DELETE WHERE { ?s ?p ?o }",
        "DROP ALL",
        "this is not sparql",
    ],
)
def test_updates_and_garbage_are_rejected(graph, text):
    with pytest.raises(QueryError):
        run_query(graph, text)
    assert len(graph) > 1000  # nothing was deleted


def test_service_is_rejected(graph):
    text = "SELECT * WHERE { SERVICE <http://example.org/sparql> { ?s ?p ?o } }"
    with pytest.raises(QueryError, match="SERVICE"):
        run_query(graph, text)


def test_slow_query_times_out_and_the_worker_is_stopped(graph):
    import threading

    before = threading.active_count()
    slow = "SELECT (COUNT(*) AS ?n) WHERE { ?a ?b ?c . ?d ?e ?f . ?g ?h ?i }"
    with pytest.raises(QueryTimeout):
        run_query(graph, slow, timeout=0.3)
    assert threading.active_count() <= before  # the runaway thread is gone


def test_row_limit_marks_result_as_truncated(graph):
    result = run_query(graph, "SELECT * WHERE { ?s ?p ?o }", max_rows=10)
    assert len(result.rows) == 10
    assert result.truncated


def test_query_files_do_not_use_forbidden_dashes(queries):
    for q in queries.values():
        assert not re.search(f"[{chr(0x2013)}{chr(0x2014)}]|--", q.text), q.path.name
