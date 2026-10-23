from rdflib import Literal, URIRef
from rdflib.namespace import RDFS

from semlab import load_graph

TURTLE = """\
@prefix ex: <http://example.org/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

ex:alice rdfs:label "Alice"@en ;
         ex:knows ex:bob .
"""


def test_load_graph_reads_turtle(tmp_path):
    file = tmp_path / "tiny.ttl"
    file.write_text(TURTLE, encoding="utf-8")

    graph = load_graph(file)

    assert len(graph) == 2
    alice = URIRef("http://example.org/alice")
    assert (alice, RDFS.label, Literal("Alice", lang="en")) in graph


def test_load_graph_merges_several_files(tmp_path):
    first = tmp_path / "a.ttl"
    second = tmp_path / "b.ttl"
    first.write_text(TURTLE, encoding="utf-8")
    second.write_text(
        "@prefix ex: <http://example.org/> .\nex:bob ex:knows ex:carol .\n", encoding="utf-8"
    )

    assert len(load_graph(first, second)) == 3
