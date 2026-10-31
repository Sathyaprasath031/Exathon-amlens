-- One view per typology. Each returns the same shape so they can be unioned:
-- account_id, typology, period_start, amount, detail
CREATE OR REPLACE VIEW v_det_structuring AS
SELECT w.account_id, 'STRUCTURING' AS typology, w.wk_start AS period_start,
       w.band_cash_total AS amount,
       CAST(w.n_band_cash AS VARCHAR(10)) || ' cash deposits just under the PAN limit, total '
         || CAST(ROUND(w.band_cash_total, 0) AS VARCHAR(20)) AS detail
FROM acct_week w CROSS JOIN v_cfg c
WHERE w.n_band_cash >= c.struct_min_n * w.seg_mult
  AND w.band_cash_total >= c.struct_min_total;

CREATE OR REPLACE VIEW v_det_passthrough AS
SELECT w.account_id, 'PASSTHROUGH' AS typology, w.wk_start AS period_start,
       w.cr_nc AS amount,
       'Received ' || CAST(ROUND(w.cr_nc, 0) AS VARCHAR(20)) || ' and sent out '
         || CAST(ROUND(w.dr_nc, 0) AS VARCHAR(20)) || ' in the same week' AS detail
FROM acct_week w CROSS JOIN v_cfg c
WHERE w.cr_nc >= c.pt_min_cr * w.seg_mult
  AND w.dr_nc >= c.pt_ratio * w.cr_nc
  AND w.n_senders < c.fan_min_senders;

CREATE OR REPLACE VIEW v_det_fanin AS
SELECT w.account_id, 'FANIN_MULE' AS typology, w.wk_start AS period_start,
       w.cr_nc AS amount,
       CAST(w.n_senders AS VARCHAR(10)) || ' different senders paid in '
         || CAST(ROUND(w.cr_nc, 0) AS VARCHAR(20)) || ', then ' || CAST(ROUND(w.dr_nc, 0) AS VARCHAR(20))
         || ' left the account' AS detail
FROM acct_week w CROSS JOIN v_cfg c
WHERE w.n_senders >= c.fan_min_senders * w.seg_mult
  AND w.cr_nc >= c.fan_min_total * w.seg_mult
  AND w.dr_nc >= c.fan_out_ratio * w.cr_nc;

CREATE OR REPLACE VIEW v_triangles AS
SELECT e1.src AS a, e2.src AS b, e3.src AS c3,
       e1.tot AS ab, e2.tot AS bc, e3.tot AS ca,
       LEAST(e1.first_dt, e2.first_dt, e3.first_dt) AS first_dt
FROM edges e1
JOIN edges e2 ON e1.dst = e2.src
JOIN edges e3 ON e2.dst = e3.src AND e3.dst = e1.src
CROSS JOIN v_cfg c
WHERE e1.src < e2.src AND e1.src < e3.src AND e2.src <> e3.src
  AND LEAST(e1.tot, e2.tot, e3.tot) >= c.cyc_min_ratio * GREATEST(e1.tot, e2.tot, e3.tot);

CREATE OR REPLACE VIEW v_det_circular AS
SELECT a AS account_id, 'CIRCULAR' AS typology, first_dt AS period_start, LEAST(ab, bc, ca) AS amount,
       'Money loops ' || a || ' > ' || b || ' > ' || c3 || ' > ' || a || ', about '
         || CAST(ROUND(LEAST(ab, bc, ca), 0) AS VARCHAR(20)) || ' per leg' AS detail
FROM v_triangles
UNION ALL
SELECT b, 'CIRCULAR', first_dt, LEAST(ab, bc, ca),
       'Money loops ' || a || ' > ' || b || ' > ' || c3 || ' > ' || a || ', about '
         || CAST(ROUND(LEAST(ab, bc, ca), 0) AS VARCHAR(20)) || ' per leg'
FROM v_triangles
UNION ALL
SELECT c3, 'CIRCULAR', first_dt, LEAST(ab, bc, ca),
       'Money loops ' || a || ' > ' || b || ' > ' || c3 || ' > ' || a || ', about '
         || CAST(ROUND(LEAST(ab, bc, ca), 0) AS VARCHAR(20)) || ' per leg'
FROM v_triangles;

CREATE OR REPLACE VIEW v_det_income AS
SELECT m.account_id, 'INCOME_MISMATCH' AS typology, m.mth_start AS period_start,
       m.cr_total AS amount,
       'Credits of ' || CAST(ROUND(m.cr_total, 0) AS VARCHAR(20)) || ' in a month vs declared income '
         || CAST(ROUND(m.declared_monthly_income, 0) AS VARCHAR(20)) AS detail
FROM acct_month m CROSS JOIN v_cfg c
WHERE m.cr_total >= c.inc_min_cr
  AND m.cr_total > c.inc_mult * m.declared_monthly_income;

CREATE OR REPLACE VIEW v_alerts AS
SELECT account_id, typology, period_start, amount, detail FROM v_det_structuring
UNION ALL
SELECT account_id, typology, period_start, amount, detail FROM v_det_passthrough
UNION ALL
SELECT account_id, typology, period_start, amount, detail FROM v_det_fanin
UNION ALL
SELECT account_id, typology, period_start, amount, detail FROM v_det_circular
UNION ALL
SELECT account_id, typology, period_start, amount, detail FROM v_det_income
