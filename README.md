%%writefile README.md
# Week 3 Analytics Engagements — Duka Electronics & Mobile Money Agent Network

This repository contains two client analytics deliverables built in Python and Excel/Sheets:

1. **Engagement 1 · Duka Electronics:** Half-year (January–June 2026) sales exploration (`duka_sales.csv`, seed `2026`), branch/product/weekend/monthly comparisons, filtered CSV export (`premium_online_coast_capital.csv`), and an Excel summary workbook (`excel/duka_branch_summary.xlsx`) reconciled against `pandas`.
2. **Engagement 2 · Mobile Money Agent Network:** Data-quality audit of legacy mobile money transactions (`agent_transactions.csv` & `agents.csv`, seed `44`), modular cleaning pipeline (`cleaning_pipeline.py`), left-join merge, county and weekly summaries, six-dimension Data Quality Report, and Kenya Data Protection Act (2019) privacy controls.

## Repository Structure

```text
├── README.md
├── duka_analysis.ipynb
├── cleaning_pipeline.py
├── duka_sales.csv
├── agents.csv
├── agent_transactions.csv
├── premium_online_coast_capital.csv
└── excel/
    └── duka_branch_summary.xlsx
