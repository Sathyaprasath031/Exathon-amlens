# AMLens: AML Case Triage on Exasol Personal
**ExaThon India 2026 | Track 01: Money, Risk & Regulation**

---

## Slide 1: Title
- **Project**: AMLens: Behavioral AML Case Triage on Exasol Personal
- **Track**: Track 01 - Money, Risk & Regulation
- **Core Mission**: Transforming overwhelming alerts into actionable, ranked compliance cases using in-database SQL graph analytics.

---

## Slide 2: The Compliance Analyst's Reality
- Mid-size and cooperative banks receive thousands of AML alerts every day.
- Compliance teams are mandated to report suspicious activities to FIU-IND.
- Single-transaction threshold rules (e.g., cash >= 10 Lakhs) generate massive false alarm volume while missing multi-account laundering patterns.
- Result: Real, high-risk cases wait in backlogged queues while analysts manually vet false positives.

---

## Slide 3: Why Static Rules Fail
1. **High False Positive Rate**: Legitimate businesses make regular large cash deposits; flagging each creates operational paralysis.
2. **Layered Patterns Evade Detection**: Money launderers deliberately split deposits under limits, use pass-through mules, and route funds in circles.
3. **No Cross-Account Context**: A rules engine looking at single transactions cannot see network topology or weekly money velocity.

---

## Slide 4: Five Patterns, One In-Database Engine
1. **Structuring (Smurfing)**: Multiple deposits just beneath mandatory reporting limits within short windows.
2. **Pass-Through**: Rapid influx of funds transferred to external accounts within 24-48 hours.
3. **Fan-In Mule**: Multiple smaller accounts funneling money into a central aggregator.
4. **Circular Flow**: Directed loops of funds (A -> B -> C -> A) designed to obscure origin.
5. **Income Mismatch**: Transaction velocity vastly exceeding declared monthly earnings.

---

## Slide 5: End-to-End Architecture
- **Synthetic Data Generator**: Realistic customer accounts and transactions with planted suspicious typologies.
- **Exasol Personal In-Database Analytics**:
  - `03_features.sql`: Weekly/monthly rollups and directed transaction graph.
  - `04_detectors.sql`: High-speed SQL typology detectors with segment-aware thresholds.
  - `05_scoring.sql`: 0-100 composite risk scoring per account.
  - `06_eval.sql`: Ground-truth evaluation benchmarks.
- **FastAPI Backend + React Console**: Ranked queue, case evidence summaries, weekly inflow/outflow charts, and live tunable SQL rules.

---

## Slide 6: Why Exasol Personal?
- **Speed & Scale**: In-memory analytical processing aggregates 1.4M+ transactions and executes graph self-joins in milliseconds.
- **In-Database Analytics**: Features, detectors, scoring, and evaluation all happen inside the database—no heavy data movement to external Python workers.
- **Dynamic Tunability**: Threshold rules and weights live as rows in a `config` table; a compliance officer can tune a rule with a single SQL `UPDATE`.

---

## Slide 7: Evaluation Results
*Benchmark run on 10,000 accounts, ~1.4M transactions, 225 planted suspicious entities:*

| Method | Flagged | True Positives | Precision | Recall | False Alarms |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **AMLens (SQL Behavioral Scoring)** | **227** | **225** | **99.1%** | **100.0%** | **2** |
| **Baseline (Single Transaction >= 10L)** | 561 | 19 | 3.4% | 8.4% | 542 |

*Detection across all 5 typologies: 100% recall on Circular (75/75), Fan-in Mule (40/40), Income Mismatch (40/40), Structuring (40/40), and Pass-Through (30/30).*
*(Note: Evaluated on synthetic data with planted typologies to validate the end-to-end pipeline).*

---

## Slide 8: Future Roadmap & Limitations
- **Roadmap**: Direct integration into core banking streams, additional complex typologies (trade-based AML), and analyst feedback loop to continuously tune weights.
- **Honest Limitations**:
  - Synthetic planted data tests pipeline efficacy, not real-world bank variance.
  - Business accounts have higher baseline thresholds, requiring dedicated merchant-specific rules.
  - Decision support platform: human compliance review is strictly required before filing any regulatory report.
