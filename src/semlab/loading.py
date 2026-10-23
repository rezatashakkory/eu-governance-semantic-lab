"""Load RDF files into an rdflib graph."""

from pathlib import Path

from rdflib import Graph


def load_graph(*paths: str | Path) -> Graph:
    """Parse one or more RDF files into a single in-memory graph.

    The file format is guessed from the file extension (.ttl is Turtle).
    """
    graph = Graph()
    for path in paths:
        graph.parse(Path(path))
    return graph
