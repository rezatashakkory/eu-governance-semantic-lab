"""Integrity checks on the real data that SHACL does not cover."""

import re

from rdflib import Namespace
from rdflib.namespace import DCTERMS, RDF, SKOS

from semlab.namespaces import ACT, CPT, EUROVOC, LAB, LANGUAGES, SCHEME_URI


def concepts(graph):
    return set(graph.subjects(RDF.type, SKOS.Concept))


def test_scheme_has_six_top_concepts_and_68_concepts(graph):
    assert len(set(graph.objects(SCHEME_URI, SKOS.hasTopConcept))) == 6
    assert len(concepts(graph)) == 68


def test_every_concept_has_three_languages_and_a_definition(graph):
    for concept in concepts(graph):
        languages = {lit.language for lit in graph.objects(concept, SKOS.prefLabel)}
        assert languages == set(LANGUAGES), concept
        assert graph.value(concept, SKOS.definition) is not None, concept


def test_hierarchy_is_consistent(graph):
    """narrower and broader mirror each other, and every non-top concept has a parent."""
    tops = set(graph.objects(SCHEME_URI, SKOS.hasTopConcept))
    for concept in concepts(graph):
        for child in graph.objects(concept, SKOS.narrower):
            assert (child, SKOS.broader, concept) in graph
        for parent in graph.objects(concept, SKOS.broader):
            assert (parent, SKOS.narrower, concept) in graph
        if concept not in tops:
            assert list(graph.objects(concept, SKOS.broader)), concept


def test_no_concept_is_its_own_ancestor(graph):
    for concept in concepts(graph):
        assert concept not in set(graph.transitive_objects(concept, SKOS.broader)) - {concept}


def test_related_links_are_symmetric(graph):
    for a, _, b in graph.triples((None, SKOS.related, None)):
        assert (b, SKOS.related, a) in graph


def test_eurovoc_alignments_have_a_valid_form(graph):
    pattern = re.compile(r"^http://eurovoc\.europa\.eu/(c_[0-9a-f]{8}|[0-9]+)$")
    links = [
        o
        for p in (SKOS.exactMatch, SKOS.closeMatch, SKOS.broadMatch)
        for o in graph.objects(None, p)
    ]
    assert len(links) == 19
    for link in links:
        assert pattern.match(str(link)), link
        assert str(link).startswith(str(EUROVOC))


def test_pending_review_matches_the_translation_source(graph):
    """Concepts that use EuroVoc labels (exactMatch) are not flagged. All others are."""
    for concept in concepts(graph):
        flagged = {str(o) for o in graph.objects(concept, LAB.pendingReview)}
        assert flagged in (set(), {"fr", "de"}), concept
    # 10 concepts take their labels from EuroVoc, so 58 of 68 need review.
    flagged_concepts = {s for s in concepts(graph) if (s, LAB.pendingReview, None) in graph}
    assert len(flagged_concepts) == 58


def test_twenty_acts_with_valid_identifiers(graph):
    acts = set(graph.subjects(LAB.hasCELEX, None))
    assert len(acts) == 20
    for act in acts:
        celex = str(graph.value(act, LAB.hasCELEX))
        assert str(act) == str(ACT[celex])
        assert re.fullmatch(r"3[0-9]{4}[RL][0-9]{4}", celex)
        assert str(graph.value(act, LAB.hasELI)).startswith("http://data.europa.eu/eli/")
        assert str(graph.value(act, DCTERMS.date)) >= "1995-10-24"


def test_celex_year_matches_the_eli_year_for_most_acts(graph):
    """The ELI path holds the year of publication. It must agree with the CELEX year."""
    for act in graph.subjects(LAB.hasCELEX, None):
        celex = str(graph.value(act, LAB.hasCELEX))
        eli = str(graph.value(act, LAB.hasELI))
        assert f"/{celex[1:5]}/" in eli, (celex, eli)


def test_every_act_topic_is_in_the_thesaurus(graph):
    known = concepts(graph)
    for predicate in (LAB.hasTopic, LAB.regulates):
        for topic in graph.objects(None, predicate):
            assert topic in known, topic


def test_every_source_act_of_a_concept_exists(graph):
    acts = set(graph.subjects(LAB.hasCELEX, None))
    for source in graph.objects(None, DCTERMS.source):
        if str(source).startswith(str(ACT)):
            assert source in acts, source


def test_concept_uris_use_the_concept_namespace(graph):
    for concept in concepts(graph):
        assert str(concept).startswith(str(CPT))
    assert isinstance(CPT, Namespace)


def test_catalog_describes_three_datasets_with_nine_distributions(graph):
    from rdflib.namespace import DCAT

    assert len(set(graph.subjects(RDF.type, DCAT.Dataset))) == 3
    assert len(set(graph.subjects(RDF.type, DCAT.Distribution))) == 9
