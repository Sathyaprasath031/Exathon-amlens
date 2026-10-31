-- Materialise alerts, then roll them up into one explainable score per account.
CREATE OR REPLACE TABLE alerts AS
SELECT account_id, typology, period_start, amount, detail FROM v_alerts;

CREATE OR REPLACE TABLE case_scores AS
SELECT s.account_id,
       LEAST(SUM(s.typ_score), 100) AS risk_score,
       COUNT(*)                     AS n_typologies,
       SUM(s.amt)                   AS total_amount,
       MIN(s.first_dt)              AS first_dt,
       MAX(s.last_dt)               AS last_dt
FROM (
    SELECT t.account_id, t.typology, t.amt, t.first_dt, t.last_dt,
           -- base weight, +10 for each repeat, capped at 60 per typology
           LEAST(w.weight + 10 * (t.n_hits - 1), 60) AS typ_score
    FROM (
        SELECT account_id, typology, COUNT(*) AS n_hits, SUM(amount) AS amt,
               MIN(period_start) AS first_dt, MAX(period_start) AS last_dt
        FROM alerts
        GROUP BY account_id, typology
    ) t
    JOIN typology_weights w ON w.typology = t.typology
) s
GROUP BY s.account_id
