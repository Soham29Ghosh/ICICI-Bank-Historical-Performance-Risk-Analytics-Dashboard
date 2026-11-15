# Interview Prep: ICICI Bank Project

## 1-minute pitch
> "I analysed 21 years of RBI data on ICICI Bank, from 2004 to 2025, covering loans, bad loans, profit, fraud and complaints.
>
> First I cleaned it in Excel. The years came in two formats, so I made one standard format, fixed the units, and arranged it as one row per year. Then I calculated ratios with Excel formulas and wrote SQL queries for trends, like year-on-year growth and a 3-year moving average.
>
> The main story is the bad-loan cycle. ICICI's bad-loan ratio peaked at 9.9% in 2018, when many corporate loans across Indian banks went bad, and it has come down to 1.73% in 2025. In 2019, 86% of operating profit went into provisions for bad loans; now it's only 30%. Meanwhile, loans grew 21 times.
>
> I also found a big jump in fraud amount in FY24 and a peak in customer complaints during COVID. I built a Tableau dashboard to show all of this."

## Simple definitions
| Term | Meaning |
|---|---|
| Gross Advances | Total loans given by the bank |
| NPA | A loan where payment is overdue for more than 90 days, i.e. a bad loan |
| GNPA ratio | Gross NPAs ÷ gross advances × 100 |
| Net NPA | Gross NPA minus provisions already set aside (not in this dataset) |
| Provisions | Money kept aside from profit to cover expected loan losses |
| Operating profit | Profit before provisions and tax |
| Write-off | A bad loan removed from the books; the bank can still try to recover it |
| Recovery | Money actually collected back from bad loans |
| Contingent liabilities | Possible future obligations, such as guarantees and derivatives |
| Sensitive sectors | Capital markets, real estate and commodities, which carry higher risk |
| Banking Ombudsman | RBI's complaint system for bank customers |
| CAGR | Average yearly growth rate over many years |

## Likely questions
**Why did NPAs rise in 2016–2018?**
Large corporate loans (infrastructure, power, steel) went bad across Indian banks. RBI's Asset Quality Review in 2015 also forced banks to recognise bad loans honestly.

**Why did they fall?**
- Recoveries and write-offs.
- Higher provisions.
- Insolvency and Bankruptcy Code (IBC) resolutions.
- A shift to retail lending.
- Strong loan growth, which grows the denominator.

**What was difficult in the data?**
- Mixed year formats.
- Inconsistent units.
- Missing years for fraud and complaints. I left them blank, not zero, because zero would mean "no fraud".
- An odd drop in loans in FY10, which I flagged to verify.

**Why both Excel and SQL?**
Excel for cleaning and quick ratio formulas. SQL for repeatable analysis, such as window functions for growth and moving averages.

**Which SQL functions did you use?**
- `LAG()` for year-on-year growth
- `RANK()` for the worst years
- `AVG() OVER (ROWS BETWEEN 2 PRECEDING…)` for a 3-year moving average
- `FILTER` to pivot the metrics

**What would you do next?**
Add other banks (HDFC, SBI, Axis) from the same RBI source and compare them, and add net NPA and the capital adequacy ratio.

## Numbers to remember
- GNPA: **9.9% (FY18) → 1.73% (FY25)**
- Provisions % of operating profit: **86% (FY19) → 30% (FY25)**
- Loans: **21× growth**, about **16% a year**
- Fraud amount FY24: **₹322.6 cr**
- Complaints peak: **28,065 in FY21**
