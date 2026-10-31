-- Feature tables: the heavy aggregations over all transactions, done once,
-- inside the database.
CREATE OR REPLACE VIEW v_cfg AS
SELECT
    MAX(CASE WHEN param = 'band_low'         THEN val END) AS band_low,
    MAX(CASE WHEN param = 'band_high'        THEN val END) AS band_high,
    MAX(CASE WHEN param = 'struct_min_n'     THEN val END) AS struct_min_n,
    MAX(CASE WHEN param = 'struct_min_total' THEN val END) AS struct_min_total,
    MAX(CASE WHEN param = 'pt_min_cr'        THEN val END) AS pt_min_cr,
    MAX(CASE WHEN param = 'pt_ratio'         THEN val END) AS pt_ratio,
    MAX(CASE WHEN param = 'fan_min_senders'  THEN val END) AS fan_min_senders,
    MAX(CASE WHEN param = 'fan_min_total'    THEN val END) AS fan_min_total,
    MAX(CASE WHEN param = 'fan_out_ratio'    THEN val END) AS fan_out_ratio,
    MAX(CASE WHEN param = 'min_edge'         THEN val END) AS min_edge,
    MAX(CASE WHEN param = 'cyc_min_ratio'    THEN val END) AS cyc_min_ratio,
    MAX(CASE WHEN param = 'inc_mult'         THEN val END) AS inc_mult,
    MAX(CASE WHEN param = 'inc_min_cr'       THEN val END) AS inc_min_cr,
    MAX(CASE WHEN param = 'business_mult'    THEN val END) AS business_mult,
    MAX(CASE WHEN param = 'flag_score'       THEN val END) AS flag_score,
    MAX(CASE WHEN param = 'ctr_single'       THEN val END) AS ctr_single
FROM config;

CREATE OR REPLACE TABLE acct_week AS
SELECT
    t.account_id,
    t.wk_start,
    a.segment,
    CASE WHEN a.segment = 'BUSINESS' THEN c.business_mult ELSE 1 END AS seg_mult,
    SUM(CASE WHEN t.direction = 'CREDIT' AND t.channel <> 'CASH' THEN t.amount ELSE 0 END) AS cr_nc,
    SUM(CASE WHEN t.direction = 'DEBIT'  AND t.channel <> 'CASH' THEN t.amount ELSE 0 END) AS dr_nc,
    COUNT(DISTINCT CASE WHEN t.direction = 'CREDIT' AND t.channel <> 'CASH' THEN t.counterparty_id END) AS n_senders,
    SUM(CASE WHEN t.direction = 'CREDIT' AND t.channel = 'CASH'
                  AND t.amount BETWEEN c.band_low AND c.band_high THEN 1 ELSE 0 END) AS n_band_cash,
    SUM(CASE WHEN t.direction = 'CREDIT' AND t.channel = 'CASH'
                  AND t.amount BETWEEN c.band_low AND c.band_high THEN t.amount ELSE 0 END) AS band_cash_total
FROM transactions t
JOIN accounts a ON a.account_id = t.account_id
CROSS JOIN v_cfg c
GROUP BY t.account_id, t.wk_start, a.segment, c.business_mult;

CREATE OR REPLACE TABLE acct_month AS
SELECT
    t.account_id,
    t.mth_start,
    a.declared_monthly_income,
    SUM(CASE WHEN t.direction = 'CREDIT' THEN t.amount ELSE 0 END) AS cr_total
FROM transactions t
JOIN accounts a ON a.account_id = t.account_id
GROUP BY t.account_id, t.mth_start, a.declared_monthly_income;

-- Directed money-flow graph between accounts of this bank
CREATE OR REPLACE TABLE edges AS
SELECT src, dst, tot, n, first_dt, last_dt
FROM (
    SELECT t.account_id AS src, t.counterparty_id AS dst,
           SUM(t.amount) AS tot, COUNT(*) AS n,
           MIN(t.txn_dt) AS first_dt, MAX(t.txn_dt) AS last_dt
    FROM transactions t
    JOIN accounts d ON d.account_id = t.counterparty_id
    WHERE t.direction = 'DEBIT' AND t.channel <> 'CASH'
    GROUP BY t.account_id, t.counterparty_id
) e
WHERE e.tot >= (SELECT min_edge FROM v_cfg)
