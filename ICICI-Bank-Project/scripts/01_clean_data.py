import pandas as pd, numpy as np
raw = pd.read_csv("../data/raw/icici_rbi_raw.csv")
df = raw.copy()
# 1. One fiscal-year label: '31-03-2025' (balance at year end) and '2024-25' (flow during year) -> FY2025
def to_fy(t):
    t = str(t)
    if len(t) == 10 and t.count("-") == 2:      # 31-03-YYYY
        return int(t[-4:])
    return int(t[:4]) + 1                       # YYYY-YY
df["fiscal_year"] = df["time_period"].map(to_fy)
df["fy_label"] = "FY" + df["fiscal_year"].astype(str).str[-2:]
df["data_type"] = np.where(df["note"].str.contains("Cumulative"), "Year-end balance", "Full-year total")
df["unit"] = df["unit"].replace({"value in rupees crores": "Rs crore", "value in rupees crore": "Rs crore",
                                 "value in percentage": "%", "value in absolute number": "Count"})
short = {"Gross NPAs": "gross_npa", "Gross Advances": "gross_advances",
         "Gross NPAs to Gross Advances Ratio": "gnpa_ratio_pct",
         "New Acretion to NPAs from Standard Advances": "new_npa_added",
         "Write-Offs": "write_offs", "Actual Recoveries": "recoveries",
         "Provisions and Contingencies": "provisions", "Operating Profit": "operating_profit",
         "Contingent Liabilities": "contingent_liabilities", "Exposure to sensitive sectors": "sensitive_sector_exposure",
         "Fraud Incidents": "fraud_incidents", "Fraud Amount": "fraud_amount",
         "Ombudsman Complaints": "ombudsman_complaints", "Total Maintainable Complaints Disposed": "complaints_disposed"}
df["metric"] = df["sub_category"].map(short)
df["sub_category"] = df["sub_category"].replace({"New Acretion to NPAs from Standard Advances": "New Accretion to NPAs from Standard Advances"})
assert df["metric"].notna().all()
long = df[["fiscal_year", "fy_label", "category", "sub_category", "metric", "value", "unit", "data_type"]].sort_values(["fiscal_year", "category", "metric"])
long.to_csv("../data/clean/icici_clean_long.csv", index=False)

wide = long.pivot_table(index=["fiscal_year", "fy_label"], columns="metric", values="value").reset_index()
order = ["fiscal_year", "fy_label", "gross_advances", "gross_npa", "gnpa_ratio_pct", "new_npa_added", "recoveries", "write_offs",
         "operating_profit", "provisions", "contingent_liabilities", "sensitive_sector_exposure",
         "fraud_incidents", "fraud_amount", "ombudsman_complaints", "complaints_disposed"]
wide = wide[order]
# 2. Derived metrics
w = wide
w["advances_growth_pct"] = (w.gross_advances / w.gross_advances.shift(1) - 1) * 100
w["gnpa_ratio_check_pct"] = w.gross_npa / w.gross_advances * 100
w["provisions_to_op_profit_pct"] = w.provisions / w.operating_profit * 100
w["profit_after_provisions"] = w.operating_profit - w.provisions
w["op_profit_growth_pct"] = (w.operating_profit / w.operating_profit.shift(1) - 1) * 100
w["npa_cleared"] = w.recoveries + w.write_offs
w["net_npa_addition"] = w.new_npa_added - w.npa_cleared
w["fraud_amount_per_incident_lakh"] = w.fraud_amount / w.fraud_incidents * 100
w["sensitive_exposure_to_advances_x"] = w.sensitive_sector_exposure / w.gross_advances
w["complaints_disposed_pct"] = w.complaints_disposed / w.ombudsman_complaints * 100
w = w.round(2)
w.to_csv("../data/clean/icici_wide_with_metrics.csv", index=False)
print(w.to_string())
