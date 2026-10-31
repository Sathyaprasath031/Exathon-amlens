-- Evaluation against the planted ground truth (synthetic data only).
CREATE OR REPLACE VIEW v_flagged_baseline AS
SELECT DISTINCT t.account_id
FROM transactions t CROSS JOIN v_cfg c
WHERE t.amount >= c.ctr_single;

CREATE OR REPLACE VIEW v_eval AS
SELECT 'AMLens: behavioural SQL scoring' AS method,
       COUNT(*) AS flagged,
       SUM(CASE WHEN g.account_id IS NOT NULL THEN 1 ELSE 0 END) AS true_pos
FROM case_scores s
CROSS JOIN v_cfg c
LEFT JOIN (SELECT DISTINCT account_id FROM gt_accounts) g ON g.account_id = s.account_id
WHERE s.risk_score >= c.flag_score
UNION ALL
SELECT 'Baseline: single-transaction threshold',
       COUNT(*),
       SUM(CASE WHEN g.account_id IS NOT NULL THEN 1 ELSE 0 END)
FROM v_flagged_baseline b
LEFT JOIN (SELECT DISTINCT account_id FROM gt_accounts) g ON g.account_id = b.account_id;

CREATE OR REPLACE VIEW v_eval_typology AS
SELECT g.typology,
       COUNT(*) AS n_planted,
       SUM(CASE WHEN d.account_id IS NOT NULL THEN 1 ELSE 0 END) AS caught_by_own_detector,
       SUM(CASE WHEN s.risk_score >= c.flag_score THEN 1 ELSE 0 END) AS flagged_by_score,
       SUM(CASE WHEN b.account_id IS NOT NULL THEN 1 ELSE 0 END) AS flagged_by_baseline
FROM gt_accounts g
CROSS JOIN v_cfg c
LEFT JOIN (SELECT DISTINCT account_id, typology FROM alerts) d
       ON d.account_id = g.account_id AND d.typology = g.typology
LEFT JOIN case_scores s ON s.account_id = g.account_id
LEFT JOIN v_flagged_baseline b ON b.account_id = g.account_id
GROUP BY g.typology
