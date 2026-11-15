-- =====================================================================
-- 02_analysis_queries.sql : 10 business questions on 21 years of ICICI data
-- All amounts in Rs crore.
-- =====================================================================

-- Q1. Data coverage: how many years of data does each metric have?
SELECT category, sub_category, COUNT(*) AS years_available,
       MIN(fy_label) AS from_year, MAX(fy_label) AS to_year
FROM icici_metrics
GROUP BY category, sub_category
ORDER BY category, years_available DESC;

-- Q2. Bad-loan (GNPA) ratio by year, ranked from worst to best
SELECT fy_label, gnpa_ratio_pct,
       RANK() OVER (ORDER BY gnpa_ratio_pct DESC) AS worst_rank
FROM v_icici_yearly
WHERE gnpa_ratio_pct IS NOT NULL
ORDER BY worst_rank
LIMIT 5;

-- Q3. Year-on-year growth in loans (gross advances)
SELECT fy_label, gross_advances,
       ROUND(100.0 * (gross_advances / LAG(gross_advances) OVER (ORDER BY fiscal_year) - 1), 1) AS yoy_growth_pct
FROM v_icici_yearly
ORDER BY fiscal_year;

-- Q4. Compound annual growth of loans FY04 -> FY25
SELECT ROUND(100.0 * (POWER(MAX(gross_advances) FILTER (WHERE fiscal_year = 2025)
                     / MAX(gross_advances) FILTER (WHERE fiscal_year = 2004), 1.0 / 21) - 1), 1) AS loan_cagr_pct,
       ROUND(MAX(gross_advances) FILTER (WHERE fiscal_year = 2025)
           / MAX(gross_advances) FILTER (WHERE fiscal_year = 2004), 1) AS times_growth
FROM v_icici_yearly;

-- Q5. How much of operating profit was used up by provisions (bad-loan losses)?
SELECT fy_label, operating_profit, provisions,
       ROUND(100.0 * provisions / operating_profit, 1) AS provisions_pct_of_op_profit,
       operating_profit - provisions AS profit_after_provisions
FROM v_icici_yearly
WHERE operating_profit IS NOT NULL
ORDER BY fiscal_year;

-- Q6. Years where provisions took more than half of operating profit (stress years)
SELECT fy_label, ROUND(100.0 * provisions / operating_profit, 1) AS provisions_pct
FROM v_icici_yearly
WHERE provisions > 0.5 * operating_profit
ORDER BY provisions_pct DESC;

-- Q7. NPA build-up vs clean-up: new bad loans added vs recovered + written off
SELECT fy_label, new_npa_added,
       recoveries + write_offs AS npa_cleared,
       new_npa_added - (recoveries + write_offs) AS net_addition
FROM v_icici_yearly
WHERE new_npa_added IS NOT NULL
ORDER BY fiscal_year;

-- Q8. 3-year moving average of the GNPA ratio (smooths out one-off years)
SELECT fy_label, gnpa_ratio_pct,
       ROUND(AVG(gnpa_ratio_pct) OVER (ORDER BY fiscal_year ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) AS gnpa_3yr_avg
FROM v_icici_yearly
ORDER BY fiscal_year;

-- Q9. Fraud: incidents, amount and average amount per incident (Rs lakh)
SELECT fy_label, fraud_incidents, fraud_amount,
       ROUND(100.0 * fraud_amount / fraud_incidents, 2) AS avg_fraud_lakh
FROM v_icici_yearly
WHERE fraud_incidents IS NOT NULL
ORDER BY fiscal_year;

-- Q10. Customer complaints to the RBI Ombudsman, with change vs previous available year
SELECT fy_label, ombudsman_complaints,
       ombudsman_complaints - LAG(ombudsman_complaints) OVER (ORDER BY fiscal_year) AS change_vs_prev
FROM v_icici_yearly
WHERE ombudsman_complaints IS NOT NULL
ORDER BY fiscal_year;
