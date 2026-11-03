"""Write the generated JSON-LD and RDF/XML files from the Turtle sources."""

from pathlib import Path

from rdflib import Graph
from rdflib.compare import isomorphic

from semlab.loading import DATA, SOURCES, load_graph
from semlab.namespaces import PREFIXES

DIST = DATA / "dist"

FORMATS = {
    "jsonld": "json-ld",
    "rdf": "xml",
}


def dist_path(name: str, extension: str, folder: Path = DIST) -> Path:
    return folder / f"{name}.{extension}"


def build_dist(folder: Path = DIST) -> list[Path]:
    """Generate JSON-LD and RDF/XML for every source file. Turtle stays the source of truth."""
    folder.mkdir(parents=True, exist_ok=True)
    written = []
    for name, source in SOURCES.items():
        graph = load_graph(source)
        for extension, rdflib_format in FORMATS.items():
            target = dist_path(name, extension, folder)
            if rdflib_format == "json-ld":
                text = graph.serialize(format="json-ld", context=PREFIXES, indent=2)
            else:
                text = graph.serialize(format=rdflib_format)
            target.write_text(text, encoding="utf-8", newline="\n")
            written.append(target)
    return written


def out_of_sync(folder: Path = DIST) -> list[str]:
    """Names of generated files that are missing or no longer match their Turtle source."""
    problems = []
    for name, source in SOURCES.items():
        expected = load_graph(source)
        for extension in FORMATS:
            target = dist_path(name, extension, folder)
            if not target.exists():
                problems.append(f"{target.name}: missing")
                continue
            actual = Graph().parse(target)
            if not isomorphic(expected, actual):
                problems.append(f"{target.name}: differs from {source.name}")
    return problems
