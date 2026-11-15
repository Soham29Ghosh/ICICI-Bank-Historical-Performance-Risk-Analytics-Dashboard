"""Builds the Excel analysis workbook (with live formulas) and the chart images."""
import pandas as pd, matplotlib.pyplot as plt
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

raw = pd.read_csv("../data/raw/icici_rbi_raw.csv")
long = pd.read_csv("../data/clean/icici_clean_long.csv")
w = pd.read_csv("../data/clean/icici_wide_with_metrics.csv")

HDR = PatternFill("solid", fgColor="0B3B5C"); HF = Font(bold=True, color="FFFFFF")
def sheet_from_df(ws, df):
    ws.append(list(df.columns))
    for r in df.itertuples(index=False): ws.append([None if pd.isna(v) else v for v in r])
    for c in ws[1]: c.fill, c.font, c.alignment = HDR, HF, Alignment(wrap_text=True, vertical="center")
    for i, col in enumerate(df.columns, 1): ws.column_dimensions[get_column_letter(i)].width = max(12, min(40, len(str(col)) + 2))
    ws.freeze_panes = "A2"

wb = Workbook()
ws = wb.active; ws.title = "README"
for line in ["ICICI Bank Historical Performance & Risk Analytics (FY2004-FY2025)",
             "Source: Reserve Bank of India (via Dataful, dataset 23856). Amounts in Rs crore.",
             "",
             "Sheets:",
             "1_Raw_RBI      - data exactly as downloaded",
             "2_Clean_Long   - cleaned: one fiscal-year format (FY25 = 2024-25), units standardised",
             "3_Yearly       - one row per year, one column per metric (pivot of 2_Clean_Long)",
             "4_Metrics      - derived ratios calculated with Excel formulas (blue columns)",
             "5_Notes        - data-quality notes and definitions"]:
    ws.append([line])
ws["A1"].font = Font(bold=True, size=14); ws.column_dimensions["A"].width = 95

sheet_from_df(wb.create_sheet("1_Raw_RBI"), raw)
sheet_from_df(wb.create_sheet("2_Clean_Long"), long)
base = ["fiscal_year", "fy_label", "gross_advances", "gross_npa", "gnpa_ratio_pct", "new_npa_added", "recoveries",
        "write_offs", "operating_profit", "provisions", "contingent_liabilities", "sensitive_sector_exposure",
        "fraud_incidents", "fraud_amount", "ombudsman_complaints", "complaints_disposed"]
sheet_from_df(wb.create_sheet("3_Yearly"), w[base])

# 4_Metrics: formulas referencing 3_Yearly so the analysis is genuinely done in Excel
m = wb.create_sheet("4_Metrics")
cols = ["fiscal_year", "fy_label", "Loan growth %", "GNPA ratio check %", "Provisions % of operating profit",
        "Profit after provisions", "NPA cleared (recoveries + write-offs)", "Net NPA addition",
        "Avg fraud per incident (Rs lakh)", "Complaints disposed %"]
m.append(cols)
for c in m[1]: c.fill, c.font, c.alignment = HDR, HF, Alignment(wrap_text=True)
n = len(w)
for i in range(2, n + 2):
    Y = "'3_Yearly'!"
    m.append([f"={Y}A{i}", f"={Y}B{i}",
              (f'=IF(OR({Y}C{i-1}="",{Y}C{i-1}=0),"",({Y}C{i}/{Y}C{i-1}-1)*100)' if i > 2 else ""),
              f'=IF({Y}C{i}="","",{Y}D{i}/{Y}C{i}*100)',
              f'=IF({Y}I{i}="","",{Y}J{i}/{Y}I{i}*100)',
              f'=IF({Y}I{i}="","",{Y}I{i}-{Y}J{i})',
              f'=IF({Y}G{i}="","",{Y}G{i}+{Y}H{i})',
              f'=IF({Y}F{i}="","",{Y}F{i}-({Y}G{i}+{Y}H{i}))',
              f'=IF({Y}M{i}="","",{Y}N{i}/{Y}M{i}*100)',
              f'=IF(OR({Y}O{i}="",{Y}P{i}=""),"",{Y}P{i}/{Y}O{i}*100)'])
for row in m.iter_rows(min_row=2, min_col=3, max_col=10):
    for c in row: c.number_format = "#,##0.0"; c.font = Font(color="1F4E79")
for i in range(1, 11): m.column_dimensions[get_column_letter(i)].width = 18
m.freeze_panes = "C2"

notes = wb.create_sheet("5_Notes")
for r in [["Topic", "Note"],
          ["Year format", "RBI mixes '31-03-2025' (balance at year end) and '2024-25' (total for the year). Both converted to FY25."],
          ["Units", "'rupees crore' and 'rupees crores' standardised to 'Rs crore'."],
          ["Missing years", "Fraud data only FY18-FY24 (FY23 missing); complaints FY14-FY23; NPA flows FY15-FY25. Left blank, not zero."],
          ["Anomaly to verify", "Gross advances drop from Rs 2.24 lakh cr (FY09) to Rs 1.42 lakh cr (FY10): check against annual report."],
          ["Anomaly to verify", "Contingent liabilities spike in FY08 (Rs 12.1 lakh cr) then fall in FY09."],
          ["Limitation", "Gross NPA can fall even when new NPAs exceed recoveries + write-offs, because upgrades (loans becoming regular again) are not in this dataset."],
          ["NPA", "Non-Performing Asset: loan with interest/principal unpaid for 90+ days."],
          ["GNPA ratio", "Gross NPAs / Gross Advances x 100. Lower is better."],
          ["Provisions", "Money set aside from profit to cover expected losses on bad loans."],
          ["Operating profit", "Profit before provisions and tax."]]:
    notes.append(r)
for c in notes[1]: c.fill, c.font = HDR, HF
notes.column_dimensions["A"].width = 20; notes.column_dimensions["B"].width = 120
wb.save("../excel/ICICI_Bank_Analysis.xlsx")

# ---------------- charts ----------------
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
IMG = "../images/"
def save(n): plt.tight_layout(); plt.savefig(IMG + n, dpi=150); plt.close()

fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(w.fy_label, w.gnpa_ratio_pct, marker="o", color="#c0392b", lw=2)
ax.annotate("Peak 9.9% (FY18)", xy=(14, 9.9), xytext=(9, 9.3), arrowprops=dict(arrowstyle="->"))
ax.annotate("1.73% (FY25)", xy=(21, 1.73), xytext=(17.5, 3.2), arrowprops=dict(arrowstyle="->"))
ax.set_title("Gross NPA ratio (%): bad loans as a share of total loans"); ax.set_ylabel("%"); plt.xticks(rotation=60)
save("01_gnpa_ratio_trend.png")

fig, ax = plt.subplots(figsize=(9, 4))
ax.bar(w.fy_label, w.gross_advances / 1e5, color="#1f6f8b")
ax.set_title("Gross advances (total loans), Rs lakh crore"); plt.xticks(rotation=60)
save("02_gross_advances.png")

d = w.dropna(subset=["operating_profit"])
fig, ax = plt.subplots(figsize=(9, 4))
ax.bar(d.fy_label, d.operating_profit / 1000, color="#2a9d8f", label="Operating profit")
ax.bar(d.fy_label, d.provisions / 1000, color="#e76f51", label="Provisions")
ax2 = ax.twinx(); ax2.plot(d.fy_label, d.provisions_to_op_profit_pct, color="black", marker=".", label="Provisions % of op. profit")
ax2.set_ylabel("%"); ax.set_ylabel("Rs '000 crore"); ax.set_title("Operating profit vs provisions"); ax.legend(loc="upper left")
plt.setp(ax.get_xticklabels(), rotation=60); save("03_profit_vs_provisions.png")

d = w.dropna(subset=["new_npa_added"])
fig, ax = plt.subplots(figsize=(9, 4)); x = range(len(d))
ax.bar([i - 0.2 for i in x], d.new_npa_added, 0.4, label="New NPAs added", color="#e76f51")
ax.bar([i + 0.2 for i in x], d.npa_cleared, 0.4, label="Recovered + written off", color="#2a9d8f")
ax.set_xticks(list(x)); ax.set_xticklabels(d.fy_label); ax.set_title("NPA build-up vs clean-up (Rs crore)"); ax.legend()
save("04_npa_flows.png")

d = w.dropna(subset=["fraud_incidents"])
fig, ax = plt.subplots(1, 2, figsize=(10, 3.6))
ax[0].bar(d.fy_label, d.fraud_incidents, color="#6c5b7b"); ax[0].set_title("Fraud incidents")
ax[1].bar(d.fy_label, d.fraud_amount, color="#c0392b"); ax[1].set_title("Fraud amount (Rs crore)")
save("05_fraud.png")

d = w.dropna(subset=["ombudsman_complaints"])
fig, ax = plt.subplots(figsize=(9, 3.8))
ax.plot(d.fy_label, d.ombudsman_complaints, marker="o", color="#355c7d")
ax.set_title("Banking Ombudsman complaints against ICICI Bank"); save("06_complaints.png")
print("ok")
