"""A small demonstration of OWL RL reasoning with owlrl.

Reasoning means deriving triples that are not written down but follow from the
ontology. For example, if the data says "GDPR is a Regulation" and the ontology says
"every Regulation is a LegalAct", a reasoner adds "GDPR is a LegalAct".
"""

from rdflib import Graph, URIRef
from rdflib.namespace import RDF

from semlab.namespaces import LAB

_ERROR = URIRef("http://www.daml.org/2002/03/agents/agent-ont#error")


def expand(data: Graph, ontology: Graph) -> tuple[Graph, Graph]:
    """Return (expanded graph, only the new triples) after OWL RL reasoning.

    The input graphs are not changed.
    """
    from owlrl import DeductiveClosure, OWLRL_Semantics

    expanded = Graph()
    for triple in data:
        expanded.add(triple)
    for triple in ontology:
        expanded.add(triple)
    before = {t for t in expanded}

    DeductiveClosure(
        OWLRL_Semantics,
        axiomatic_triples=False,
        datatype_axioms=False,
    ).expand(expanded)

    inferred = Graph()
    for triple in expanded:
        if triple not in before and _is_interesting(triple):
            inferred.add(triple)
    return expanded, inferred


def _is_interesting(triple) -> bool:
    """Keep only triples about our own terms. This hides reasoner noise such as
    'x is a owl:Thing' or 'x sameAs x'."""
    _, predicate, obj = triple
    if str(predicate).startswith(str(LAB)):
        return True
    return predicate == RDF.type and str(obj).startswith(str(LAB))


def inconsistencies(graph: Graph) -> list[str]:
    """Run OWL RL and return the messages of any detected inconsistency.

    OWL RL reports contradictions, such as an individual belonging to two disjoint
    classes, by adding error messages to the graph. An empty list means none was found.
    """
    from owlrl import DeductiveClosure, OWLRL_Semantics

    work = Graph()
    for triple in graph:
        work.add(triple)
    DeductiveClosure(OWLRL_Semantics, axiomatic_triples=False, datatype_axioms=False).expand(work)
    return sorted(str(message) for message in work.objects(None, _ERROR))
