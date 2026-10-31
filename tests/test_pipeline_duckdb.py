"""Offline check that the SQL logic finds the planted typologies.
Runs on DuckDB (no Exasol needed). The real target is Exasol Personal."""
from amlens.db import connect
from amlens.pipeline import run


def test_detectors_recover_planted_patterns():
    db = connect("duckdb")
    ev, typ, n_gt = run(db, "tiny", 7, log=lambda *_: None)
    ours = ev[ev.method.str.startswith("AMLens")].iloc[0]
    base = ev[ev.method.str.startswith("Baseline")].iloc[0]
    assert ours.recall >= 0.9
    assert ours.precision >= 0.8
    assert ours.precision > base.precision
    assert ours.recall > base.recall
    for _, r in typ.iterrows():
        assert r.caught_by_own_detector / r.n_planted >= 0.85, r.typology


def test_api_endpoints(monkeypatch):
    monkeypatch.setenv("AMLENS_DB", "duckdb")
    monkeypatch.setenv("AMLENS_SCALE", "tiny")
    import importlib
    import api
    importlib.reload(api)
    from fastapi.testclient import TestClient
    c = TestClient(api.app)
    assert c.get("/api/summary").json()["flagged"] > 0
    top = c.get("/api/queue?min_score=40").json()[0]["account_id"]
    case = c.get(f"/api/case/{top}").json()
    assert case["alerts"] and case["weekly"] and case["summary"]
    assert c.get("/api/case/x';drop").status_code == 400
    assert c.get("/api/eval").json()["methods"][0]["recall"] >= 0.9
