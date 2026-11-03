from pathlib import Path

import pytest
from rdflib import Graph

from semlab import load_all, load_graph

DATA_DIR = Path(__file__).parent / "data"


@pytest.fixture(scope="session")
def graph() -> Graph:
    """The real project data, loaded once for the whole test run."""
    return load_all()


@pytest.fixture
def with_extra(graph):
    """Return the real data plus one extra Turtle file, as a new graph."""

    def _combine(filename: str) -> Graph:
        combined = Graph()
        for triple in graph:
            combined.add(triple)
        combined += load_graph(DATA_DIR / filename)
        return combined

    return _combine
