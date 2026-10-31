"""End-to-end pipeline: schema -> synthetic data -> load -> SQL features/detectors/scores -> evaluation."""
import time

from .db import run_sql_file
from .generate import generate


def run(db, scale="small", seed=42, log=print):
    t0 = time.time()
    step = lambda msg: log(f"[{time.time() - t0:6.1f}s] {msg}")

    run_sql_file(db, "01_schema.sql")
    run_sql_file(db, "02_config.sql")
    step("schema + config created")

    accounts, txns, gt = generate(scale, seed)
    step(f"generated {len(accounts):,} accounts, {len(txns):,} transactions (synthetic)")
    db.load_df(accounts, "accounts")
    db.load_df(txns, "transactions")
    db.load_df(gt, "gt_accounts")
    step("loaded into database")

    for f in ("03_features.sql", "04_detectors.sql", "05_scoring.sql", "06_eval.sql"):
        run_sql_file(db, f)
        step(f"ran {f}")
    return evaluate(db)


def evaluate(db):
    ev = db.query("SELECT * FROM v_eval")
    n_gt = int(db.query("SELECT COUNT(DISTINCT account_id) AS n FROM gt_accounts")["n"][0])
    ev["flagged"] = ev["flagged"].astype(int)
    ev["true_pos"] = ev["true_pos"].astype(int)
    ev["precision"] = (ev["true_pos"] / ev["flagged"].clip(lower=1)).round(3)
    ev["recall"] = (ev["true_pos"] / n_gt).round(3)
    ev["false_alarms"] = ev["flagged"] - ev["true_pos"]
    typ = db.query("SELECT * FROM v_eval_typology ORDER BY typology")
    return ev, typ, n_gt
