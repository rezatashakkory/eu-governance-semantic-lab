"""The Cellar module is tested without the network: urlopen is replaced by a fake."""

import io
import json
import os
import time
import urllib.error

import pytest

from semlab import cellar

ANSWER = {
    "results": {
        "bindings": [
            {
                "title": {"value": "Regulation (EU) 2016/679\xa0of the European Parliament"},
                "date": {"value": "2016-04-27"},
                "eli": {"value": "http://data.europa.eu/eli/reg/2016/679/oj"},
            }
        ]
    }
}


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def ok_response(payload=ANSWER):
    return FakeResponse(json.dumps(payload).encode("utf-8"))


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr(cellar.time, "sleep", lambda _s: None)


def test_fetch_act_reads_and_cleans_the_answer(tmp_path, monkeypatch):
    monkeypatch.setattr(cellar.urllib.request, "urlopen", lambda *a, **k: ok_response())
    act = cellar.fetch_act("32016R0679", cache_dir=tmp_path)
    assert act.title == "Regulation (EU) 2016/679 of the European Parliament"  # no odd space
    assert act.date == "2016-04-27"
    assert act.eli.endswith("/eli/reg/2016/679/oj")


def test_unknown_celex_returns_none(tmp_path, monkeypatch):
    empty = {"results": {"bindings": []}}
    monkeypatch.setattr(cellar.urllib.request, "urlopen", lambda *a, **k: ok_response(empty))
    assert cellar.fetch_act("39999R9999", cache_dir=tmp_path) is None


def test_second_call_uses_the_cache(tmp_path, monkeypatch):
    calls = []

    def fake(*args, **kwargs):
        calls.append(1)
        return ok_response()

    monkeypatch.setattr(cellar.urllib.request, "urlopen", fake)
    cellar.fetch_act("32016R0679", cache_dir=tmp_path)
    cellar.fetch_act("32016R0679", cache_dir=tmp_path)
    assert len(calls) == 1


def test_timeout_is_passed_to_the_request(tmp_path, monkeypatch):
    seen = {}

    def fake(request, timeout=None):
        seen["timeout"] = timeout
        return ok_response()

    monkeypatch.setattr(cellar.urllib.request, "urlopen", fake)
    cellar.run_sparql("SELECT * WHERE {?s ?p ?o}", timeout=3, cache_dir=tmp_path)
    assert seen["timeout"] == 3


def test_network_failure_becomes_a_clear_error(tmp_path, monkeypatch):
    def fail(*args, **kwargs):
        raise urllib.error.URLError("no network")

    monkeypatch.setattr(cellar.urllib.request, "urlopen", fail)
    with pytest.raises(cellar.CellarError, match="could not be reached"):
        cellar.run_sparql("SELECT * WHERE {?s ?p ?o}", cache_dir=tmp_path)


def test_server_error_is_retried_once_then_reported(tmp_path, monkeypatch):
    calls = []

    def fail(request, timeout=None):
        calls.append(1)
        raise urllib.error.HTTPError(request.full_url, 500, "boom", {}, None)

    monkeypatch.setattr(cellar.urllib.request, "urlopen", fail)
    with pytest.raises(cellar.CellarError, match="HTTP 500"):
        cellar.run_sparql("SELECT * WHERE {?s ?p ?o}", cache_dir=tmp_path)
    assert len(calls) == 2


def test_server_error_then_success_works(tmp_path, monkeypatch):
    calls = []

    def flaky(request, timeout=None):
        calls.append(1)
        if len(calls) == 1:
            raise urllib.error.HTTPError(request.full_url, 500, "boom", {}, None)
        return ok_response()

    monkeypatch.setattr(cellar.urllib.request, "urlopen", flaky)
    assert cellar.fetch_act("32016R0679", cache_dir=tmp_path) is not None


def test_client_error_is_not_retried(tmp_path, monkeypatch):
    calls = []

    def fail(request, timeout=None):
        calls.append(1)
        raise urllib.error.HTTPError(request.full_url, 400, "bad", {}, None)

    monkeypatch.setattr(cellar.urllib.request, "urlopen", fail)
    with pytest.raises(cellar.CellarError, match="HTTP 400"):
        cellar.run_sparql("SELECT * WHERE {?s ?p ?o}", cache_dir=tmp_path)
    assert len(calls) == 1


def test_unreadable_answer_is_reported(tmp_path, monkeypatch):
    monkeypatch.setattr(
        cellar.urllib.request, "urlopen", lambda *a, **k: FakeResponse(b"not json at all")
    )
    with pytest.raises(cellar.CellarError, match="could not be read"):
        cellar.run_sparql("SELECT * WHERE {?s ?p ?o}", cache_dir=tmp_path)


def test_stale_cache_is_used_when_the_network_fails(tmp_path, monkeypatch):
    query = "SELECT * WHERE {?s ?p ?o}"
    monkeypatch.setattr(cellar.urllib.request, "urlopen", lambda *a, **k: ok_response())
    first = cellar.run_sparql(query, cache_dir=tmp_path)
    cache_file = next(tmp_path.glob("*.json"))
    old = time.time() - 10 * 24 * 3600
    os.utime(cache_file, (old, old))

    def fail(*args, **kwargs):
        raise urllib.error.URLError("offline")

    monkeypatch.setattr(cellar.urllib.request, "urlopen", fail)
    assert cellar.run_sparql(query, cache_dir=tmp_path) == first


def test_celex_is_checked_before_it_goes_into_a_query():
    with pytest.raises(cellar.CellarError):
        cellar.act_query('32016R0679" . } DROP ALL #')


def test_verify_dataset_reports_differences(graph, tmp_path, monkeypatch):
    def fake_fetch(celex, **options):
        if celex == "32016R0679":
            return cellar.LiveAct(celex, "A different title", "2016-04-27", "http://x")
        return None

    monkeypatch.setattr(cellar, "fetch_act", fake_fetch)
    problems = cellar.verify_dataset(graph)
    assert "32016R0679: title differs" in problems
    assert "32016R0679: eli differs" in problems
    assert "32016R0679: date differs" not in problems
    assert "32024R1689: not found in Cellar" in problems
