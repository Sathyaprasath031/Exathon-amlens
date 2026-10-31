"""Thin database layer. Exasol Personal is the real target (pyexasol).
DuckDB is supported only so the unit test can run without a database."""
import os
import re
import ssl
from pathlib import Path

import pandas as pd

SQL_DIR = Path(__file__).resolve().parent.parent / "sql"
SCHEMA = os.getenv("EXASOL_SCHEMA", "AMLENS")


def split_sql(text: str):
    """Split a .sql file on semicolons (our files contain no ';' inside strings)."""
    text = re.sub(r"--[^\n]*", "", text)
    return [s.strip() for s in text.split(";") if s.strip()]


class ExasolDB:
    kind = "exasol"

    def __init__(self):
        import pyexasol
        host = os.getenv("EXASOL_HOST", "localhost")
        port = os.getenv("EXASOL_PORT", "8563")
        self.conn = pyexasol.connect(
            dsn=f"{host}:{port}",
            user=os.getenv("EXASOL_USER", "sys"),
            password=os.environ["EXASOL_PASSWORD"],
            encryption=True,
            # Exasol Personal uses a self-signed certificate by default
            websocket_sslopt={"cert_reqs": ssl.CERT_NONE},
            fetch_dict=False,
        )
        self.conn.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")
        self.conn.execute(f"OPEN SCHEMA {SCHEMA}")

    def execute(self, sql: str):
        self.conn.execute(sql)

    def query(self, sql: str) -> pd.DataFrame:
        df = self.conn.export_to_pandas(sql)
        df.columns = [c.lower() for c in df.columns]
        return df

    def load_df(self, df: pd.DataFrame, table: str):
        self.conn.import_from_pandas(df, (SCHEMA, table.upper()))


class DuckDB:
    kind = "duckdb"

    def __init__(self):
        import duckdb
        self.con = duckdb.connect(":memory:")
        self.con.execute("CREATE SCHEMA IF NOT EXISTS amlens")
        self.con.execute("USE amlens")

    def execute(self, sql: str):
        self.con.execute(sql)

    def query(self, sql: str) -> pd.DataFrame:
        df = self.con.execute(sql).df()
        df.columns = [c.lower() for c in df.columns]
        return df

    def load_df(self, df: pd.DataFrame, table: str):
        self.con.register("_tmp_df", df)
        self.con.execute(f"INSERT INTO {table} SELECT * FROM _tmp_df")
        self.con.unregister("_tmp_df")


def run_sql_file(db, name: str):
    for stmt in split_sql((SQL_DIR / name).read_text()):
        db.execute(stmt)


def connect(kind: str = "exasol"):
    return DuckDB() if kind == "duckdb" else ExasolDB()
