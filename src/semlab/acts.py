"""Read-only helpers for the dataset of legal acts."""

from rdflib import Graph, URIRef
from rdflib.namespace import DCTERMS, RDF, RDFS

from semlab.namespaces import LAB
from semlab.vocabulary import label, short_name

ACT_CLASSES = (LAB.Regulation, LAB.Directive, LAB.ImplementingRegulation)
RELATIONS = {"amends": LAB.amends, "repeals": LAB.repeals, "is based on": LAB.isBasedOn}


def act_nodes(graph: Graph) -> list[URIRef]:
    nodes = {s for cls in ACT_CLASSES for s in graph.subjects(RDF.type, cls)}
    return sorted(nodes, key=lambda n: (str(graph.value(n, DCTERMS.date)), str(n)))


def act_row(graph: Graph, act: URIRef, lang: str = "en") -> dict:
    """One act as plain Python data for tables and cards."""
    klass = next(c for c in ACT_CLASSES if (act, RDF.type, c) in graph)
    return {
        "uri": str(act),
        "celex": str(graph.value(act, LAB.hasCELEX)),
        "short_name": str(graph.value(act, DCTERMS.alternative) or ""),
        "title": str(graph.value(act, DCTERMS.title)),
        "type": short_name(klass),
        "date": str(graph.value(act, DCTERMS.date)),
        "eli": str(graph.value(act, LAB.hasELI)),
        "eur_lex": str(graph.value(act, RDFS.seeAlso)),
        "regulates": [label(graph, o, lang) for o in graph.objects(act, LAB.regulates)],
        "topics": sorted(label(graph, o, lang) for o in graph.objects(act, LAB.hasTopic)),
        "relations": [
            {"relation": name, "target": str(graph.value(t, LAB.hasCELEX))}
            for name, prop in RELATIONS.items()
            for t in graph.objects(act, prop)
        ],
    }


def acts_table(graph: Graph, lang: str = "en") -> list[dict]:
    return [act_row(graph, a, lang) for a in act_nodes(graph)]


def graph_elements(graph: Graph, with_topics: bool = True, lang: str = "en"):
    """Nodes and edges for the interactive graph.

    Returns (nodes, edges). A node is (id, label, kind, tooltip). An edge is
    (source id, target id, label).
    """
    nodes: dict[str, tuple[str, str, str, str]] = {}
    edges: list[tuple[str, str, str]] = []
    for act in act_nodes(graph):
        row = act_row(graph, act, lang)
        nodes[row["uri"]] = (row["uri"], row["short_name"] or row["celex"], "act", row["title"])
        for name, prop in RELATIONS.items():
            for target in graph.objects(act, prop):
                edges.append((row["uri"], str(target), name))
        if with_topics:
            for topic in graph.objects(act, LAB.regulates):
                topic_label = label(graph, topic, lang)
                nodes[str(topic)] = (str(topic), topic_label, "topic", f"Topic: {topic_label}")
                edges.append((row["uri"], str(topic), "regulates"))
    return list(nodes.values()), edges
