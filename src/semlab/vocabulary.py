"""Read-only helpers for browsing the SKOS thesaurus."""

from dataclasses import dataclass, field

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import DCTERMS, RDF, SKOS

from semlab.namespaces import ACT, CPT, EUROVOC, LAB, LANGUAGES, SCHEME_URI

MATCH_PROPERTIES = {
    "exactMatch": SKOS.exactMatch,
    "closeMatch": SKOS.closeMatch,
    "broadMatch": SKOS.broadMatch,
}


@dataclass
class TreeNode:
    uri: URIRef
    label: str
    children: list["TreeNode"] = field(default_factory=list)


def short_name(uri) -> str:
    """The last part of a URI, for example data-protection."""
    return str(uri).rstrip("/").rsplit("/", 1)[-1].rsplit("#", 1)[-1]


def label(graph: Graph, node, lang: str = "en") -> str:
    """Preferred label in the language, falling back to English, then to the URI end."""
    labels = {lit.language: str(lit) for lit in graph.objects(node, SKOS.prefLabel)}
    return labels.get(lang) or labels.get("en") or short_name(node)


def top_concepts(graph: Graph, lang: str = "en") -> list[URIRef]:
    return sorted(
        graph.objects(SCHEME_URI, SKOS.hasTopConcept), key=lambda c: label(graph, c, lang)
    )


def children(graph: Graph, node, lang: str = "en") -> list[URIRef]:
    """Direct narrower concepts, found through skos:broader."""
    return sorted(graph.subjects(SKOS.broader, node), key=lambda c: label(graph, c, lang))


def tree(graph: Graph, lang: str = "en") -> list[TreeNode]:
    """The whole hierarchy as nested nodes, sorted by label in the chosen language."""

    def build(node) -> TreeNode:
        return TreeNode(
            node, label(graph, node, lang), [build(c) for c in children(graph, node, lang)]
        )

    return [build(top) for top in top_concepts(graph, lang)]


def all_concepts(graph: Graph, lang: str = "en") -> list[URIRef]:
    return sorted(graph.subjects(RDF.type, SKOS.Concept), key=lambda c: label(graph, c, lang))


def search(graph: Graph, text: str, lang: str = "en") -> list[URIRef]:
    """Concepts whose label in any language, alternative label or definition contains the text."""
    needle = text.strip().casefold()
    if not needle:
        return []
    found = []
    for concept in all_concepts(graph, lang):
        haystack = [
            str(o)
            for p in (SKOS.prefLabel, SKOS.altLabel, SKOS.definition)
            for o in graph.objects(concept, p)
        ]
        if any(needle in h.casefold() for h in haystack):
            found.append(concept)
    return found


def _links(graph: Graph, concept, predicate, lang: str) -> list[tuple[URIRef, str]]:
    return [(o, label(graph, o, lang)) for o in sorted(graph.objects(concept, predicate), key=str)]


def concept_card(graph: Graph, concept: URIRef, lang: str = "en") -> dict:
    """Everything the app shows about one concept, as plain Python data."""
    pref = {
        lit.language: str(lit)
        for lit in graph.objects(concept, SKOS.prefLabel)
        if isinstance(lit, Literal) and lit.language in LANGUAGES
    }
    alt = sorted(str(o) for o in graph.objects(concept, SKOS.altLabel))
    definition = next((str(o) for o in graph.objects(concept, SKOS.definition)), "")
    alignments = []
    for kind, prop in MATCH_PROPERTIES.items():
        for target in graph.objects(concept, prop):
            if str(target).startswith(str(EUROVOC)):
                alignments.append({"type": kind, "uri": str(target)})
    sources = []
    for source in graph.objects(concept, DCTERMS.source):
        if str(source).startswith(str(ACT)):
            title = graph.value(source, DCTERMS.alternative)
            celex = short_name(source)
            sources.append({"text": f"{title} ({celex})" if title else celex, "uri": str(source)})
        else:
            sources.append({"text": str(source), "uri": str(source)})
    covering = sorted(
        {
            (str(act), str(graph.value(act, DCTERMS.alternative) or short_name(act)))
            for predicate in (LAB.hasTopic, LAB.regulates)
            for act in graph.subjects(predicate, concept)
        },
        key=lambda pair: pair[1],
    )
    return {
        "uri": str(concept),
        "id": short_name(concept),
        "label": label(graph, concept, lang),
        "labels": pref,
        "alt_labels": alt,
        "definition": definition,
        "broader": _links(graph, concept, SKOS.broader, lang),
        "narrower": [(c, label(graph, c, lang)) for c in children(graph, concept, lang)],
        "related": _links(graph, concept, SKOS.related, lang),
        "alignments": alignments,
        "sources": sources,
        "acts": covering,
        "pending_review": sorted(str(o) for o in graph.objects(concept, LAB.pendingReview)),
    }


def pending_review(graph: Graph) -> dict[str, list[URIRef]]:
    """Concepts whose translations still need a human check, grouped by language."""
    result: dict[str, list[URIRef]] = {lang: [] for lang in LANGUAGES if lang != "en"}
    for concept, _, lang in graph.triples((None, LAB.pendingReview, None)):
        result.setdefault(str(lang), []).append(concept)
    return {lang: sorted(items, key=short_name) for lang, items in result.items()}


def concept_uri(slug: str) -> URIRef:
    return CPT[slug]
