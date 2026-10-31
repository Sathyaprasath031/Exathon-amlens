# Run guide

Time needed: about 15 minutes. Works on Windows, macOS and Linux with Python 3.10+.

## 1. Install Exasol Personal (local)

Follow the official quick start: https://docs.exasol.com/db/latest/get_started/quick_start_guide.htm
(launcher and starter kit: https://github.com/exasol/exasol-personal).

When the database is running, note the **host, port, user and password** of your deployment.
The launcher prints them and stores them in your deployment directory.
Apple Silicon note: use the native Exasol Personal launcher, not the x86-only Docker image.

## 2. Get the code

```bash
git clone <YOUR-REPO-URL> amlens
cd amlens
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Configure the connection

```bash
cp .env.example .env               # Windows: copy .env.example .env
```

Edit `.env` and set `EXASOL_PASSWORD` (and host/port/user if yours differ).

## 4. Build everything (data, load, detectors, scores, evaluation)

```bash
python scripts/run_pipeline.py --scale small
```

Scales: `tiny` (2k accounts), `small` (10k accounts, about 1.4M transactions), `medium` (50k), `large` (250k),
or any number of accounts. Use `--seed` to change the random data. The script prints the evaluation table.

## 5. Open the analyst console (React)

```bash
uvicorn api:app --port 8000
```

Open http://localhost:8000. Tabs: **Overview** (with the case queue), **Case file**, **Does it work?**, **Rules & SQL**.
Click any row in the queue to open its case file.

The React build is already in `web/dist`. To change the UI you need Node.js 18+:

```bash
cd web
npm install
npm run dev      # UI on http://localhost:5173 (API must be running on :8000)
npm run build    # refresh web/dist
```

## 6. Change a rule (optional)

In any Exasol SQL client:

```sql
OPEN SCHEMA AMLENS;
UPDATE config SET val = 6 WHERE param = 'struct_min_n';
```

Then re-run the detector, scoring and evaluation files, in order:
`sql/03_features.sql` (only if you changed a feature threshold), `04_detectors.sql`, `05_scoring.sql`, `06_eval.sql`.

## 7. Offline test (no database)

```bash
python -m pytest -q tests
```

This runs the same SQL files on DuckDB against a tiny synthetic set and checks that the planted patterns are found and the API answers.

## Troubleshooting

- *Connection refused / timeout:* check the database is running and the port in `.env`.
- *Certificate errors:* the code disables certificate checks because Exasol Personal uses a self-signed
  certificate locally. Do not copy that setting to a production system.
- *Load is slow:* use `--scale tiny` first.
