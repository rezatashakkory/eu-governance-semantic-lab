"""Load the documented .rq files and run SPARQL queries safely."""

import ctypes
import re
import threading
from dataclasses import dataclass, field
from pathlib import Path

from rdflib import Graph, Literal
from rdflib.plugins.sparql import prepareQuery
from rdflib.plugins.sparql.algebra import traverse

from semlab.loading import QUERIES

HEADER_KEYS = ("title", "level", "purpose", "expected", "concepts")


class QueryError(Exception):
    """Raised for a query that is not allowed or cannot be parsed. The message is user friendly."""


class QueryTimeout(QueryError):
    """Raised when a query takes longer than the allowed time."""


@dataclass(frozen=True)
class QueryInfo:
    number: str
    path: Path
    title: str
    level: str
    purpose: str
    expected: str
    concepts: str
    text: str


@dataclass
class QueryResult:
    kind: str  # "select", "ask", "construct" or "describe"
    columns: list[str] = field(default_factory=list)
    rows: list[list[str]] = field(default_factory=list)
    boolean: bool | None = None
    graph: Graph | None = None
    truncated: bool = False


def parse_header(text: str) -> dict[str, str]:
    """Read '# key: value' lines at the top of a query file."""
    found = {}
    for line in text.splitlines():
        match = re.match(r"#\s*(\w+):\s*(.*)$", line)
        if match:
            found[match.group(1).lower()] = match.group(2).strip()
        elif line.strip() and not line.startswith("#"):
            break
    return found


def list_queries(folder: Path = QUERIES) -> list[QueryInfo]:
    """All numbered .rq files in the folder, in order."""
    infos = []
    for path in sorted(folder.glob("*.rq")):
        text = path.read_text(encoding="utf-8")
        header = parse_header(text)
        infos.append(
            QueryInfo(
                number=path.name.split("_", 1)[0],
                path=path,
                title=header.get("title", path.stem),
                level=header.get("level", ""),
                purpose=header.get("purpose", ""),
                expected=header.get("expected", ""),
                concepts=header.get("concepts", ""),
                text=text,
            )
        )
    return infos


def _node_to_text(node) -> str:
    if node is None:
        return ""
    if isinstance(node, Literal):
        value = str(node)
        return f"{value} ({node.language})" if node.language else value
    return str(node)


def _check_read_only(text: str):
    """Parse the query and refuse anything other than a local read query."""
    try:
        prepared = prepareQuery(text)
    except Exception as error:
        message = str(error).splitlines()[0] if str(error) else "invalid query"
        raise QueryError(
            "The query could not be parsed. Only SELECT, ASK, CONSTRUCT and DESCRIBE queries "
            f"are accepted. Details: {message}"
        ) from error

    uses_service = []

    def visit(node):
        if getattr(node, "name", "") == "ServiceGraphPattern":
            uses_service.append(node)

    traverse(prepared.algebra, visitPost=visit)
    if uses_service:
        raise QueryError("SERVICE (federated queries) is not allowed in this playground.")
    return prepared


def _execute(graph: Graph, prepared, max_rows: int) -> QueryResult:
    result = graph.query(prepared)
    if result.type == "ASK":
        return QueryResult(kind="ask", boolean=bool(result.askAnswer))
    if result.type in ("CONSTRUCT", "DESCRIBE"):
        out = Graph()
        for prefix, namespace in graph.namespaces():
            out.bind(prefix, namespace)
        for count, triple in enumerate(result.graph):
            if count >= max_rows:
                return QueryResult(kind=result.type.lower(), graph=out, truncated=True)
            out.add(triple)
        return QueryResult(kind=result.type.lower(), graph=out)
    columns = [str(v) for v in result.vars]
    rows = []
    truncated = False
    for row in result:
        if len(rows) >= max_rows:
            truncated = True
            break
        rows.append([_node_to_text(row[c]) for c in columns])
    return QueryResult(kind="select", columns=columns, rows=rows, truncated=truncated)


def _stop(thread: threading.Thread) -> None:
    """Ask a running thread to stop by raising an exception inside it.

    rdflib evaluates queries in pure Python, so the exception arrives within a moment.
    A thread that ends with SystemExit stays silent. This is a CPython feature and the
    only way to cancel a thread.
    """
    if thread.ident is not None:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(
            ctypes.c_ulong(thread.ident), ctypes.py_object(SystemExit)
        )


def run_query(graph: Graph, text: str, timeout: float = 10.0, max_rows: int = 2000) -> QueryResult:
    """Run a read-only query with a time limit and a row limit.

    A query that runs longer than the timeout is stopped and QueryTimeout is raised.
    """
    prepared = _check_read_only(text)
    outcome: dict[str, object] = {}

    def work() -> None:
        try:
            outcome["result"] = _execute(graph, prepared, max_rows)
        except Exception as error:  # reported to the caller below
            outcome["error"] = error
        except SystemExit:  # raised by _stop after a timeout
            pass

    worker = threading.Thread(target=work, daemon=True)
    worker.start()
    worker.join(timeout)
    if worker.is_alive():
        _stop(worker)
        worker.join(2.0)
        raise QueryTimeout(f"The query took longer than {timeout:g} seconds and was stopped.")
    if "error" in outcome:
        raise QueryError(f"The query failed: {outcome['error']}") from outcome["error"]
    return outcome["result"]  # type: ignore[return-value]
