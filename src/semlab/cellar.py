"""Optional live module: query the public Cellar SPARQL endpoint.

Cellar is the repository of the Publications Office of the European Union. It is the
source behind EUR-Lex. The endpoint is public and needs no key. This module is careful
about three things: it sets a timeout, it caches answers on disk, and it turns network
problems into a clear error message instead of a crash.

Endpoint: https://publications.europa.eu/webapi/rdf/sparql
"""

import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from rdflib import Graph
from rdflib.namespace import DCTERMS

from semlab.loading import ROOT
from semlab.namespaces import LAB

ENDPOINT = "https://publications.europa.eu/webapi/rdf/sparql"
CACHE_DIR = ROOT / ".cache" / "cellar"
CACHE_SECONDS = 24 * 60 * 60
ENGLISH = "http://publications.europa.eu/resource/authority/language/ENG"


class CellarError(Exception):
    """A problem reaching or reading Cellar. The message is safe to show to a user."""


def _cache_file(query: str, cache_dir: Path) -> Path:
    return cache_dir / (hashlib.sha256(query.encode("utf-8")).hexdigest() + ".json")


def run_sparql(
    query: str,
    timeout: float = 20.0,
    cache_dir: Path = CACHE_DIR,
    max_age: float = CACHE_SECONDS,
) -> list[dict[str, str]]:
    """Run a SELECT query on Cellar and return rows as plain dictionaries.

    A fresh cached answer is used when available. If the network fails, an older cached
    answer is used instead of failing, and only if there is none does it raise CellarError.
    """
    cache_file = _cache_file(query, cache_dir)
    cached = None
    if cache_file.exists():
        try:
            cached = json.loads(cache_file.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            cached = None
        age = time.time() - cache_file.stat().st_mtime if cached is not None else None
        if cached is not None and age is not None and age < max_age:
            return cached

    url = ENDPOINT + "?" + urllib.parse.urlencode({"query": query})
    request = urllib.request.Request(
        url, headers={"Accept": "application/sparql-results+json", "User-Agent": "semlab/0.1"}
    )
    problem = ""
    for attempt in range(2):  # one retry, because the public endpoint sometimes fails once
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                payload = json.load(response)
            rows = [
                {name: cell["value"] for name, cell in binding.items()}
                for binding in payload["results"]["bindings"]
            ]
        except urllib.error.HTTPError as error:
            problem = f"Cellar answered with an error (HTTP {error.code})."
            if error.code < 500:
                break
        except (urllib.error.URLError, TimeoutError, OSError):
            problem = f"Cellar could not be reached within {timeout:g} seconds."
            break
        except (ValueError, KeyError):
            problem = "Cellar sent an answer that could not be read."
            break
        else:
            try:
                cache_file.parent.mkdir(parents=True, exist_ok=True)
                cache_file.write_text(json.dumps(rows), encoding="utf-8")
            except OSError:
                pass  # a cache that cannot be written is not worth failing for
            return rows
        if attempt == 0:
            time.sleep(1.0)

    if cached is not None:
        return cached
    raise CellarError(problem)


def act_query(celex: str) -> str:
    """SPARQL query for the official English title, date and ELI of one act."""
    if not celex.isalnum():
        raise CellarError("A CELEX number contains only letters and digits.")
    return f"""
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
SELECT ?title ?date ?eli WHERE {{
  ?work cdm:resource_legal_id_celex "{celex}"^^<http://www.w3.org/2001/XMLSchema#string> ;
        cdm:work_date_document ?date ;
        cdm:resource_legal_eli ?eli .
  ?exp cdm:expression_belongs_to_work ?work ;
       cdm:expression_uses_language <{ENGLISH}> ;
       cdm:expression_title ?title .
}} LIMIT 1"""


@dataclass(frozen=True)
class LiveAct:
    celex: str
    title: str
    date: str
    eli: str


def fetch_act(celex: str, **options) -> LiveAct | None:
    """Official record of one act from Cellar, or None if Cellar does not know the CELEX."""
    rows = run_sparql(act_query(celex), **options)
    if not rows:
        return None
    row = rows[0]
    return LiveAct(celex, " ".join(row["title"].split()), row["date"], row["eli"])


def verify_dataset(graph: Graph, **options) -> list[str]:
    """Compare every act in our dataset with Cellar. Returns problems, empty if all match."""
    problems = []
    for act in sorted(graph.subjects(LAB.hasCELEX, None), key=str):
        celex = str(graph.value(act, LAB.hasCELEX))
        live = fetch_act(celex, **options)
        if live is None:
            problems.append(f"{celex}: not found in Cellar")
            continue
        ours = {
            "title": str(graph.value(act, DCTERMS.title)),
            "date": str(graph.value(act, DCTERMS.date)),
            "eli": str(graph.value(act, LAB.hasELI)),
        }
        for field_name, live_value in (
            ("title", live.title),
            ("date", live.date),
            ("eli", live.eli),
        ):
            if ours[field_name] != live_value:
                problems.append(f"{celex}: {field_name} differs")
    return problems
