-- AMLens schema. Portable SQL: runs on Exasol Personal (production target)
-- and on DuckDB (used only by the offline unit test).
CREATE OR REPLACE TABLE accounts (
    account_id              VARCHAR(12),
    segment                 VARCHAR(16),
    declared_monthly_income DECIMAL(14,2),
    opened_dt               DATE,
    branch                  VARCHAR(8)
);

CREATE OR REPLACE TABLE transactions (
    txn_id          BIGINT,
    account_id      VARCHAR(12),
    counterparty_id VARCHAR(16),
    direction       VARCHAR(6),
    channel         VARCHAR(6),
    amount          DECIMAL(14,2),
    txn_dt          DATE,
    txn_hour        SMALLINT,
    wk_start        DATE,
    mth_start       DATE
);

-- Ground truth planted by the generator. Used ONLY by the evaluation views.
CREATE OR REPLACE TABLE gt_accounts (
    account_id VARCHAR(12),
    typology   VARCHAR(20)
);

CREATE OR REPLACE TABLE config (
    param VARCHAR(40),
    val   DECIMAL(18,2)
);

CREATE OR REPLACE TABLE typology_weights (
    typology VARCHAR(20),
    weight   DECIMAL(6,2)
)
