import json

from rdflib import Graph
from rdflib.compare import isomorphic

from semlab import serialization
from semlab.loading import SOURCES, load_graph


def test_committed_dist_files_match_the_turtle_sources():
    assert serialization.out_of_sync() == []


def test_build_roundtrip_in_a_temp_folder(tmp_path):
    written = serialization.build_dist(tmp_path)
    assert len(written) == len(SOURCES) * 2
    for name, source in SOURCES.items():
        original = load_graph(source)
        for extension in ("jsonld", "rdf"):
            again = Graph().parse(tmp_path / f"{name}.{extension}")
            assert isomorphic(original, again), (name, extension)


def test_out_of_sync_detects_changes_and_missing_files(tmp_path):
    serialization.build_dist(tmp_path)
    assert serialization.out_of_sync(tmp_path) == []
    (tmp_path / "catalog.rdf").unlink()
    broken = tmp_path / "legal-acts.jsonld"
    data = json.loads(broken.read_text(encoding="utf-8"))
    data["@graph"] = data["@graph"][:-1]
    broken.write_text(json.dumps(data), encoding="utf-8")
    problems = serialization.out_of_sync(tmp_path)
    assert "catalog.rdf: missing" in problems
    assert any(p.startswith("legal-acts.jsonld: differs") for p in problems)


def test_jsonld_is_compact_with_prefixes():
    text = (serialization.DIST / "legal-acts.jsonld").read_text(encoding="utf-8")
    data = json.loads(text)
    assert "lab" in data["@context"]
    assert "@graph" in data
