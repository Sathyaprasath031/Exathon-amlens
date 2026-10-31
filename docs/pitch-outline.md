# Pitch deck outline (8 slides)

1. **Title.** AMLens: AML case triage on Exasol Personal. Track: Money, Risk & Regulation.
2. **The person.** The compliance analyst and her queue (use the one-sentence problem statement).
3. **Why today's rules fail.** Single-transaction thresholds: false alarms plus missed layered patterns.
4. **Five patterns, one engine.** Structuring, pass-through, fan-in mule, circular flow, income mismatch (one line each).
5. **Architecture.** Synthetic data -> Exasol Personal (features, graph, detectors, scores, evaluation as SQL) -> React console (FastAPI backend).
6. **Why Exasol.** Weekly aggregation over about 1.4M rows, self-joins on the money-flow graph, and evaluation all stay in the database; rules live in a table.
7. **Results (paste your own numbers).** Evaluation table from your run, with the caveat: synthetic, planted data.
8. **What's next and honest limits.** Real data under a bank's own governance, more typologies, analyst feedback loop, business-account blind spot.
