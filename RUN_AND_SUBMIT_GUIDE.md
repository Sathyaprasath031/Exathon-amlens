# AMLens: run it, get the output, submit it

**Deadline: Saturday 31 Oct 2026, 11:59 pm IST.** Work in this order and don't polish before everything is submitted.

---

## Part A. Run the project (about 20 minutes)

### 1. Unzip and open a terminal in the folder

```bash
unzip amlens.zip
cd amlens
```

### 2. Install Exasol Personal (local)

- Quick start: https://docs.exasol.com/db/latest/get_started/quick_start_guide.htm
- Launcher: https://github.com/exasol/exasol-personal
- Mac / Linux: `curl https://downloads.exasol.com/exasol-personal/installer.sh | sh` then `exasol install local`
- Windows: follow the launcher instructions in the quick start (needs Podman or WSL 2).

When it finishes, **write down the host, port, user and password** of your deployment. The launcher shows them and keeps them in your deployment folder. Typical values: host `localhost`, port `8563`.

### 3. Set up Python

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Add your connection details

```bash
cp .env.example .env             # Windows: copy .env.example .env
```

Open `.env` and set `EXASOL_PASSWORD` (and host, port, user if different).

### 5. Run the pipeline (this produces the output)

Test small first, then the real run:

```bash
python scripts/run_pipeline.py --scale tiny
python scripts/run_pipeline.py --scale small
```

You will see step timings and then two tables: overall results (AMLens vs the baseline rule) and results per typology.

**Take a screenshot or copy this text. You need it for the README, the video and the deck.**

### 6. Start the console (React UI)

```bash
uvicorn api:app --port 8000
```

Open **http://localhost:8000**. Tabs: Overview (with the case queue), Case file, Does it work?, Rules & SQL. Click a row in the queue to open its case file.

You do **not** need Node.js: the built React app is already included in `web/dist`. Only install Node.js 18+ if you want to change the UI (`cd web && npm install && npm run dev`).

### If something fails

| Problem | Fix |
|---|---|
| Connection refused / timeout | Database not running, or wrong port in `.env` |
| Password error | Copy the password from your deployment details again |
| Any other error | Copy the full error text and send it to me |
| Slow load | Use `--scale tiny` |

---

## Part B. Prepare the submission items

The portal needs all of these. Tick each off.

- [ ] **Problem statement**: ready in `docs/problem-statement.md` (the one-sentence version is at the top of the README)
- [ ] **Public GitHub repo** with the MIT licence
- [ ] **README** with your real Exasol results pasted in
- [ ] **Pitch deck** (PDF or PPT): outline in `docs/pitch-outline.md`
- [ ] **Demo video, 3 minutes maximum**: script in `docs/demo-script.md`
- [ ] **Run guide and licence file**: already in the repo (`docs/run-guide.md`, `LICENSE`)

### 1. Paste your results into the README

Open `README.md`, find the line starting `Exasol Personal run:` and replace it with your actual output (a screenshot or a code block), plus your machine specs and timings.

### 2. Put the code on GitHub

1. Create a new **public** repository on github.com (for example `amlens-exathon`). Do not add a README or licence there.
2. In the `amlens` folder:

```bash
git init
git add .
git commit -m "AMLens: ExaThon India 2026 submission"
git branch -M main
git remote add origin https://github.com/<your-username>/amlens-exathon.git
git push -u origin main
```

3. Open the repo in a private/incognito window to confirm it is public and shows the LICENSE file. Make sure `.env` is not uploaded (it is already in `.gitignore`).

### 3. Record the demo video (max 3 minutes)

Follow `docs/demo-script.md`. Screen-record the terminal run, then the console at http://localhost:8000 (queue, a case file, the "Does it work?" tab). Use any recorder (OBS, Zoom, Windows Game Bar, QuickTime). Upload to YouTube as **Unlisted** (or Google Drive with link sharing on) and test the link in incognito. Add the link to the README under a "Demo video" line, then commit and push again.

### 4. Make the pitch deck

Use `docs/pitch-outline.md` (8 slides). Put your real results table on slide 7. Export as PDF, add it to the repo under `docs/`, and push. I can build the deck for you; just ask.

---

## Part C. Submit in the portal

1. Go to the ExaThon India 2026 page: https://www.exasol.com/events/exathon-india-2026/
2. Click **Submit your project**.
3. Fill the form. Have these ready to paste (exact field names may differ):

| What the form may ask | What to give |
|---|---|
| Team name / members | Your name (solo is allowed, 1 to 3 members) |
| Track | **01: Money, Risk & Regulation** |
| Project title | AMLens: AML case triage on Exasol Personal |
| Problem statement | The one-sentence statement from the README, plus a short paragraph from `docs/problem-statement.md` |
| GitHub repo URL | Your public repo link |
| Demo video URL | Your unlisted YouTube or Drive link |
| Pitch deck | Upload the PDF or link to it in the repo |
| Data / tools used | "Synthetic data generated by the project. Exasol Personal, pyexasol, pandas, NumPy, Streamlit. Optional: Anthropic API for case summaries." Full list: `docs/data-sources.md` |
| Licence | MIT |

4. Submit **before 11:59 pm IST**. Aim for 9 pm so a broken link doesn't cost you.
5. Save the confirmation (screenshot or email).

### Final check before you press submit

- [ ] Repo opens when logged out
- [ ] Video plays when logged out
- [ ] README has your real results and the video link
- [ ] `LICENSE` is visible in the repo
- [ ] No `.env` or password in the repo

---

## What happens next (from the official page)

- Top 5 announced: Wed 4 Nov, 6:00 pm IST
- Demo day and winners: Fri 6 Nov, 10:00 am IST (online)
- Finalists give a 15-minute live demo and pitch plus 5 minutes of questions. A working demo is required, so keep Exasol and the console runnable on your machine.

## One honest line to keep in your pitch

The data is synthetic and the suspicious accounts were planted by the generator, so the results prove the pipeline works, not real-world accuracy. Saying this yourself in the Q&A scores better than being asked about it.
