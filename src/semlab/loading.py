"""Locate and load the project's RDF files."""

from pathlib import Path

from rdflib import Graph

from semlab.namespaces import PREFIXES

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
QUERIES = ROOT / "queries"

VOCABULARY_FILE = DATA / "vocabulary" / "eu-data-governance.ttl"
ONTOLOGY_FILE = DATA / "ontology" / "legal-acts.ttl"
ACTS_FILE = DATA / "dataset" / "legal-acts.ttl"
CATALOG_FILE = DATA / "dataset" / "catalog.ttl"
SHAPES_FILE = DATA / "shapes" / "shapes.ttl"

# The Turtle files are the source of truth. Each maps to its generated files in data/dist.
SOURCES = {
    "eu-data-governance": VOCABULARY_FILE,
    "legal-acts-ontology": ONTOLOGY_FILE,
    "legal-acts": ACTS_FILE,
    "catalog": CATALOG_FILE,
}


def load_graph(*paths: str | Path) -> Graph:
    """Parse one or more RDF files into a single in-memory graph.

    The file format is guessed from the file extension (.ttl is Turtle).
    """
    graph = Graph()
    for path in paths:
        graph.parse(Path(path))
    for prefix, namespace in PREFIXES.items():
        graph.bind(prefix, namespace)
    return graph


def load_all() -> Graph:
    """Load thesaurus, ontology, acts and catalog into one graph."""
    return load_graph(*SOURCES.values())
