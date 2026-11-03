"""OWL RL reasoning: what is inferred and what is detected as a contradiction."""

import pytest
from rdflib import Graph
from rdflib.namespace import RDF

from semlab import load_graph
from semlab.loading import ONTOLOGY_FILE
from semlab.namespaces import ACT, CPT, LAB
from semlab.reasoning import expand, inconsistencies


@pytest.fixture(scope="module")
def inferred(graph):
    _, new = expand(graph, load_graph(ONTOLOGY_FILE))
    return new


def test_subclass_reasoning_every_act_is_a_legal_act(inferred):
    assert (ACT["32016R0679"], RDF.type, LAB.LegalAct) in inferred  # GDPR, a Regulation
    assert (ACT["32016L0680"], RDF.type, LAB.LegalAct) in inferred  # a Directive


def test_implementing_regulation_is_also_a_regulation(inferred):
    assert (ACT["32023R0138"], RDF.type, LAB.Regulation) in inferred
    assert (ACT["32023R0138"], RDF.type, LAB.LegalAct) in inferred


def test_inverse_property_reasoning(inferred):
    assert (ACT["31995L0046"], LAB.repealedBy, ACT["32016R0679"]) in inferred
    assert (ACT["32014R0910"], LAB.amendedBy, ACT["32024R1183"]) in inferred
    assert (ACT["32014R0910"], LAB.amendedBy, ACT["32022L2555"]) in inferred


def test_subproperty_reasoning_regulates_implies_has_topic(inferred):
    assert (ACT["32016R0679"], LAB.hasTopic, CPT["data-protection"]) in inferred


def test_input_graph_is_not_changed(graph):
    size = len(graph)
    expand(graph, load_graph(ONTOLOGY_FILE))
    assert len(graph) == size


def test_real_data_is_consistent(graph):
    assert inconsistencies(graph) == []


def _with(graph, turtle):
    extended = Graph()
    for triple in graph:
        extended.add(triple)
    prefixes = f"@prefix act: <{ACT}> . @prefix lab: <{LAB}> . @prefix cpt: <{CPT}> .\n"
    extended.parse(data=prefixes + turtle, format="turtle")
    return extended


def test_disjointness_catches_regulation_that_is_also_a_directive(graph):
    broken = _with(graph, "act:32016R0679 a lab:Directive .")
    messages = inconsistencies(broken)
    assert any("Disjoint classes" in m and "32016R0679" in m for m in messages)


def test_asymmetry_catches_two_acts_that_amend_each_other(graph):
    broken = _with(
        graph,
        "act:32016R0679 lab:amends act:32024R1689 . act:32024R1689 lab:amends act:32016R0679 .",
    )
    assert any("asymmetric" in m for m in inconsistencies(broken))


def test_an_act_cannot_also_be_an_obligation(graph):
    broken = _with(graph, "act:32016R0679 a lab:Obligation .")
    assert any("Disjoint" in m for m in inconsistencies(broken))
