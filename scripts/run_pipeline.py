"""Usage:  python scripts/run_pipeline.py --scale small [--db exasol|duckdb]"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dotenv import load_dotenv  # noqa: E402

load_dotenv()
from amlens.db import connect  # noqa: E402
from amlens.pipeline import run  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--scale", default="small", help="tiny | small | medium | large | <number of accounts>")
ap.add_argument("--seed", type=int, default=42)
ap.add_argument("--db", default="exasol", choices=["exasol", "duckdb"])
args = ap.parse_args()

db = connect(args.db)
ev, typ, n_gt = run(db, args.scale, args.seed)
print(f"\nPlanted suspicious accounts: {n_gt}\n")
print(ev.to_string(index=False))
print("\nPer typology:")
print(typ.to_string(index=False))
