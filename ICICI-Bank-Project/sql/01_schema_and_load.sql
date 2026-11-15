-- =====================================================================
-- ICICI Bank Historical Performance & Risk Analytics
-- 01_schema_and_load.sql : create table and load the cleaned RBI data
-- Run from the repository root:  psql -d icici -f sql/01_schema_and_load.sql
-- =====================================================================
DROP TABLE IF EXISTS icici_metrics CASCADE;

-- Long format: one row per (year, metric). Clean, flexible, easy to filter.
CREATE TABLE icici_metrics (
    fiscal_year   SMALLINT     NOT NULL,          -- 2025 = FY 2024-25
    fy_label      VARCHAR(5)   NOT NULL,          -- 'FY25'
    category      VARCHAR(30)  NOT NULL,          -- Credit Risk, Profitability, ...
    sub_category  VARCHAR(80)  NOT NULL,          -- original RBI metric name
    metric        VARCHAR(40)  NOT NULL,          -- short name, e.g. gross_npa
    value         NUMERIC(14,2) NOT NULL,
    unit          VARCHAR(10)  NOT NULL,          -- Rs crore / % / Count
    data_type     VARCHAR(20)  NOT NULL,          -- Year-end balance / Full-year total
    PRIMARY KEY (fiscal_year, metric)
);

\copy icici_metrics FROM 'data/clean/icici_clean_long.csv' WITH (FORMAT csv, HEADER true)

-- Wide view: one row per year, one column per metric (easier for analysis)
CREATE OR REPLACE VIEW v_icici_yearly AS
SELECT fiscal_year, fy_label,
       MAX(value) FILTER (WHERE metric = 'gross_advances')            AS gross_advances,
       MAX(value) FILTER (WHERE metric = 'gross_npa')                 AS gross_npa,
       MAX(value) FILTER (WHERE metric = 'gnpa_ratio_pct')            AS gnpa_ratio_pct,
       MAX(value) FILTER (WHERE metric = 'new_npa_added')             AS new_npa_added,
       MAX(value) FILTER (WHERE metric = 'recoveries')                AS recoveries,
       MAX(value) FILTER (WHERE metric = 'write_offs')                AS write_offs,
       MAX(value) FILTER (WHERE metric = 'operating_profit')          AS operating_profit,
       MAX(value) FILTER (WHERE metric = 'provisions')                AS provisions,
       MAX(value) FILTER (WHERE metric = 'contingent_liabilities')    AS contingent_liabilities,
       MAX(value) FILTER (WHERE metric = 'sensitive_sector_exposure') AS sensitive_sector_exposure,
       MAX(value) FILTER (WHERE metric = 'fraud_incidents')           AS fraud_incidents,
       MAX(value) FILTER (WHERE metric = 'fraud_amount')              AS fraud_amount,
       MAX(value) FILTER (WHERE metric = 'ombudsman_complaints')      AS ombudsman_complaints,
       MAX(value) FILTER (WHERE metric = 'complaints_disposed')       AS complaints_disposed
FROM icici_metrics
GROUP BY fiscal_year, fy_label;

SELECT COUNT(*) AS rows_loaded, MIN(fiscal_year) AS first_year, MAX(fiscal_year) AS last_year FROM icici_metrics;
