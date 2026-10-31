"""AMLens API + static host for the React console.

Run:  uvicorn api:app --port 8000      then open http://localhost:8000
Every number returned here is computed by SQL inside Exasol Personal.
"""
import datetime
import decimal
import json
import os
import re
import threading
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

load_dotenv()
from amlens.db import SQL_DIR, connect  # noqa: E402
from amlens.narrative import build_narrative  # noqa: E402
from amlens.pipeline import evaluate, run  # noqa: E402

KIND = os.getenv("AMLENS_DB", "exasol")  # "duckdb" is for offline testing only
app = FastAPI(title="AMLens API")
_db = None
_lock = threading.Lock()


def _get_db():
    global _db
    if _db is None:
        _db = connect(KIND)
        if KIND == "duckdb":
            run(_db, os.getenv("AMLENS_SCALE", "tiny"), 7, log=lambda *_: None)
    return _db


def q(sql):
    with _lock:
        return _get_db().query(sql)


def rows(df):
    df = df.copy()
    for c in df.columns:
        if df[c].dtype == object:
            s = df[c].dropna()
            if len(s) and isinstance(s.iloc[0], decimal.Decimal):
                df[c] = df[c].astype(float)
            elif len(s) and isinstance(s.iloc[0], (datetime.date, datetime.datetime)):
                df[c] = df[c].astype(str)
        elif str(df[c].dtype).startswith("datetime"):
            df[c] = df[c].dt.strftime("%Y-%m-%d")
    return json.loads(df.to_json(orient="records"))


def one(df):
    return rows(df)[0]


@app.get("/api/summary")
def summary():
    n = one(q("SELECT (SELECT COUNT(*) FROM accounts) AS accounts, (SELECT COUNT(*) FROM transactions) AS txns, "
              "(SELECT COUNT(*) FROM alerts) AS alerts"))
    flag = one(q("SELECT s.cnt AS flagged FROM (SELECT COUNT(*) AS cnt FROM case_scores c CROSS JOIN v_cfg g "
                 "WHERE c.risk_score >= g.flag_score) s"))
    typ = rows(q("SELECT typology, COUNT(DISTINCT account_id) AS accounts, COUNT(*) AS alerts "
                 "FROM alerts GROUP BY typology ORDER BY accounts DESC"))
    return {**n, **flag, "typologies": typ}


@app.get("/api/queue")
def queue(min_score: int = 40, limit: int = 500):
    df = q(f"""SELECT s.account_id, a.segment, a.declared_monthly_income, s.risk_score, s.n_typologies,
                      s.total_amount, s.first_dt, s.last_dt
               FROM case_scores s JOIN accounts a ON a.account_id = s.account_id
               WHERE s.risk_score >= {int(min_score)}
               ORDER BY s.risk_score DESC, s.total_amount DESC""").head(int(limit))
    return rows(df)


@app.get("/api/case/{account_id}")
def case(account_id: str):
    if not re.fullmatch(r"[A-Za-z0-9_]{1,16}", account_id):
        raise HTTPException(400, "bad account id")
    acc = q(f"SELECT * FROM accounts WHERE account_id = '{account_id}'")
    if acc.empty:
        raise HTTPException(404, "unknown account")
    info = one(acc)
    sc = q(f"SELECT risk_score FROM case_scores WHERE account_id = '{account_id}'")
    score = float(sc["risk_score"][0]) if not sc.empty else 0.0
    alerts = q(f"SELECT typology, period_start, amount, detail FROM alerts "
               f"WHERE account_id = '{account_id}' ORDER BY period_start")
    weekly = q(f"SELECT wk_start, cr_nc, dr_nc FROM acct_week WHERE account_id = '{account_id}' ORDER BY wk_start")
    a_rows = rows(alerts)
    import pandas as pd
    text, mode = build_narrative(info, pd.DataFrame(a_rows) if a_rows else alerts, score) if a_rows else (
        "No alerts for this account.", "template")
    return {"info": info, "score": score, "alerts": a_rows, "weekly": rows(weekly), "summary": text, "summary_source": mode}


@app.get("/api/eval")
def evaluation():
    with _lock:
        ev, typ, n_gt = evaluate(_get_db())
    return {"planted": n_gt, "methods": rows(ev), "typologies": rows(typ)}


@app.get("/api/rules")
def rules():
    return {"config": rows(q("SELECT param, val FROM config ORDER BY param")),
            "weights": rows(q("SELECT typology, weight FROM typology_weights ORDER BY weight DESC")),
            "sql": (SQL_DIR / "04_detectors.sql").read_text()}


DIST = Path(__file__).parent / "web" / "dist"
if DIST.exists():
    app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")

    @app.get("/{path:path}")
    def spa(path: str):
        f = DIST / path
        return FileResponse(f if path and f.is_file() else DIST / "index.html")
