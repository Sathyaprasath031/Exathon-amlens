# Demo video script (target 2:30, limit 3:00)

**0:00 - 0:20 Problem.** "A compliance analyst gets thousands of alerts a day. A rule like 'cash over 10 lakh'
flags honest shopkeepers and misses people who split deposits under 50,000. Real cases wait in the queue."

**0:20 - 0:50 Setup, on screen.** Terminal: `python scripts/run_pipeline.py --scale small`.
Point out: about 1.4 million synthetic transactions loaded; features, five detectors and scoring all run as SQL
inside Exasol Personal; show the step timings.

**0:50 - 1:20 The result.** Show the evaluation table. Baseline: many flagged, almost all false alarms.
AMLens: a short queue with high precision. Say plainly that data is synthetic and planted, so this proves the
pipeline, not real-world accuracy.

**1:20 - 2:10 Analyst console (open http://localhost:8000).** Overview with the case queue sorted by score. Open the top case. Show the weekly in/out chart,
the evidence rows (each is a sentence), the summary and the suggested next steps. Open a circular-flow case:
three accounts, one loop.

**2:10 - 2:30 Tunable rules.** Rules & SQL tab: thresholds are rows in a table. Run one `UPDATE`, re-run the
detector step, and show the queue change.

**2:30 - 2:50 Close.** "Everything is open source under MIT, runs locally on Exasol Personal in about 15 minutes.
Decision support for the analyst, never an automatic verdict."
