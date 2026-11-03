"""Tests for the helpers that the app uses."""

from semlab import acts, vocabulary
from semlab.namespaces import CPT


def test_label_falls_back_to_english_then_uri(graph):
    assert vocabulary.label(graph, CPT["data-controller"], "fr") == "responsable du traitement"
    assert vocabulary.label(graph, CPT["data-controller"], "xx") == "Data controller"
    assert vocabulary.label(graph, CPT["does-not-exist"], "en") == "does-not-exist"


def test_tree_has_six_roots_and_68_nodes(graph):
    roots = vocabulary.tree(graph)
    assert len(roots) == 6

    def count(node):
        return 1 + sum(count(c) for c in node.children)

    assert sum(count(r) for r in roots) == 68


def test_tree_is_sorted_in_the_chosen_language(graph):
    labels = [n.label for n in vocabulary.tree(graph, "de")]
    assert labels == sorted(labels)


def test_search_finds_labels_in_any_language_and_definitions(graph):
    assert CPT["data-controller"] in vocabulary.search(graph, "verantwortlicher")
    assert CPT["data-controller"] in vocabulary.search(graph, "CONTROLLER")
    assert CPT["right-to-erasure"] in vocabulary.search(graph, "be forgotten")  # an altLabel
    assert vocabulary.search(graph, "   ") == []
    assert vocabulary.search(graph, "zzzzzz") == []


def test_concept_card_shows_everything_for_one_concept(graph):
    card = vocabulary.concept_card(graph, CPT["data-protection"])
    assert card["labels"] == {
        "en": "Data protection",
        "fr": "protection des données",
        "de": "Datenschutz",
    }
    assert card["definition"].startswith("Rules and practices")
    assert len(card["narrower"]) == 11
    assert card["alignments"] == [{"type": "exactMatch", "uri": "http://eurovoc.europa.eu/5181"}]
    assert any("GDPR" in text for text, _ in [(s["text"], s["uri"]) for s in card["sources"]])
    assert any(name == "GDPR" for _, name in card["acts"])
    assert card["pending_review"] == []  # labels come from EuroVoc


def test_concept_card_for_a_concept_with_pending_translations(graph):
    card = vocabulary.concept_card(graph, CPT["data-subject"])
    assert card["pending_review"] == ["de", "fr"]
    assert [label for _, label in card["broader"]] == ["Data protection"]


def test_pending_review_report(graph):
    pending = vocabulary.pending_review(graph)
    assert set(pending) == {"fr", "de"}
    assert len(pending["fr"]) == len(pending["de"]) == 58


def test_acts_table(graph):
    rows = acts.acts_table(graph)
    assert len(rows) == 20
    gdpr = next(r for r in rows if r["celex"] == "32016R0679")
    assert gdpr["type"] == "Regulation"
    assert gdpr["date"] == "2016-04-27"
    assert gdpr["eli"] == "http://data.europa.eu/eli/reg/2016/679/oj"
    assert gdpr["relations"] == [{"relation": "repeals", "target": "31995L0046"}]
    assert "Data protection" in gdpr["regulates"]


def test_graph_elements_have_valid_edges(graph):
    nodes, edges = acts.graph_elements(graph, with_topics=True)
    ids = {n[0] for n in nodes}
    assert len(edges) > 20
    for source, target, _ in edges:
        assert source in ids and target in ids
    only_acts, act_edges = acts.graph_elements(graph, with_topics=False)
    assert len(only_acts) == 20
    assert len(act_edges) == 6
