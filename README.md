# AMLens: AML case triage on Exasol Personal

**ExaThon India 2026, Track 01: Money, Risk & Regulation**

> A compliance analyst at a mid-size bank can't tell which of today's thousands of alerts deserve an
> investigation, because single-transaction threshold rules flag big but innocent deposits and miss patterns
> spread across many transactions and accounts. If this worked, she would open a short ranked queue where every
> case already shows the pattern, amounts, dates and a suggested next step.

Full problem statement: [docs/problem-statement.md](docs/problem-statement.md)

## What it does

AMLens loads bank transactions into **Exasol Personal** and, in SQL inside the database:

1. builds weekly and monthly account features and a directed money-flow graph;
2. detects five typologies: **structuring**, **pass-through**, **fan-in mule**, **circular flow**, **income mismatch**;
3. applies **segment-aware thresholds** (business accounts are judged against business behaviour);
4. rolls alerts into one explainable 0-100 risk score per account;
5. serves a React console (FastAPI backend) with a ranked case queue and a case file (evidence, chart, summary, next steps).

Rules are rows in a `config` table, so a compliance officer can tune one with a single `UPDATE`.

```
 generate.py --> Exasol Personal ------------------------------------------> api.py (FastAPI) --> React console
 (synthetic)     transactions, accounts                                      /api/queue, /api/case, ...      (web/)
                 -> acct_week, acct_month, edges        (SQL features)
                 -> v_det_* x5 -> alerts                (SQL detectors)
                 -> case_scores                         (SQL scoring)
                 -> v_eval, v_eval_typology             (SQL evaluation vs planted truth)
```

## Quick start

```bash
pip install -r requirements.txt
cp .env.example .env            # add your Exasol Personal password
python scripts/run_pipeline.py --scale small
uvicorn api:app --port 8000      # then open http://localhost:8000
```

The React build is already included in `web/dist`, so Node.js is not needed to run it. To edit the UI: `cd web && npm install && npm run dev` (UI on :5173, proxied to the API on :8000).

Complete steps, including installing Exasol Personal: [docs/run-guide.md](docs/run-guide.md)

## Results

The data is **synthetic**, and the suspicious accounts were **planted by our own generator**. These numbers show
the pipeline and SQL logic work end to end. They are not a claim about accuracy on real bank data.

Offline check of the same SQL files on DuckDB (`--scale small --seed 1`, 10,000 accounts, about 1.4M transactions, 225 planted accounts):

| Method | Flagged | True positives | Precision | Recall |
|---|---|---|---|---|
| AMLens: behavioural SQL scoring | 231 | 225 | 0.974 | 1.00 |
| Baseline: any transaction of INR 10 lakh or more | 554 | 18 | 0.032 | 0.08 |

### Pipeline Benchmark Output (`--scale small --seed 42`)

```text
[   0.0s] schema + config created
[   3.3s] generated 10,000 accounts, 1,386,902 transactions (synthetic)
[   3.9s] loaded into database
[   4.4s] ran 03_features.sql
[   4.4s] ran 04_detectors.sql
[   4.5s] ran 05_scoring.sql
[   4.5s] ran 06_eval.sql

Planted suspicious accounts: 225

                                method  flagged  true_pos  precision  recall  false_alarms
       AMLens: behavioural SQL scoring      227       225      0.991   1.000             2
Baseline: single-transaction threshold      561        19      0.034   0.084           542

Per typology:
       typology  n_planted  caught_by_own_detector  flagged_by_score  flagged_by_baseline
       CIRCULAR         75                    75.0              75.0                  0.0
     FANIN_MULE         40                    40.0              40.0                  0.0
INCOME_MISMATCH         40                    40.0              40.0                  0.0
    PASSTHROUGH         30                    30.0              30.0                 19.0
    STRUCTURING         40                    40.0              40.0                  0.0
```

## Pitch Deck & Demo Video
- **Pitch Deck (HTML / Print-ready PDF)**: [docs/pitch-deck.html](docs/pitch-deck.html) | [Markdown](docs/pitch-deck.md)
- **Demo Video**: [Watch Demo Video on YouTube](https://youtu.be/fi0CL3FHPtI)


## Repository layout

| Path | Purpose |
|---|---|
| `sql/` | The whole analytics pipeline: schema, config, features, detectors, scoring, evaluation |
| `amlens/generate.py` | Seeded synthetic data with planted typologies |
| `amlens/pipeline.py`, `scripts/run_pipeline.py` | Orchestration |
| `amlens/narrative.py` | Case summary (template, optional LLM) |
| `api.py` | FastAPI backend: reads from Exasol, serves the React console |
| `web/` | React (Vite) analyst console; built files in `web/dist` |
| `tests/` | Offline test of the SQL logic on DuckDB |
| `docs/` | Problem statement, run guide, data sources, demo script, pitch outline |

## Data, licences and tools

No real data. Everything is generated. Full list of libraries, licences and the one optional API:
[docs/data-sources.md](docs/data-sources.md)

## Limitations

- Planted patterns and our own thresholds: results are optimistic by construction.
- Business accounts get relaxed thresholds, a known blind spot.
- Default thresholds reference commonly cited Indian cash-reporting limits. Verify current rules before any real use.
- Decision support only. A human must review any case before a report is filed.

## Licence

MIT. See [LICENSE](LICENSE). Exasol Personal itself is proprietary and free for personal use under its own EULA.
