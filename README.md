# Insurance Policy Analysis

> For full methodology and findings, see the accompanying PDF report.

## Setup

```bash
pip install pandas matplotlib
```

Place `policies.csv` in the project directory, then run:

```bash
python3 analysis.py
```

## Scripts

- `analysis.py` — Runs the full pipeline *(start here)*
- `data_cleaning.py` — Data quality checks + customer standardization
- `exploratory_analysis.py` — Churn analysis, charts, channel breakdown, and price-per-coverage

## Outputs

| File | Description |
|---|---|
| `policies_standardized.csv` | Cleaned dataset |
| `sanity_checks_report.txt` | Data quality report |
| `churn_rate_report.txt` | Churn breakdown by 15+ features |
| `tenure_churn_histogram.png` | Churn rate by tenure |
| `risky_payment.png` | Churn rate by payment frequency |
| `price_per_coverage_plot.png` | Price-per-coverage by product type |
