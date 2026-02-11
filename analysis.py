#!/usr/bin/env python3
"""
Analysis Pipeline
==================
Runs the full pipeline end-to-end:
  1. Data Cleaning        → sanity_checks_report.txt, policies_standardized.csv
  2. Exploratory Analysis → churn_rate_report.txt, tenure_churn_histogram.png,
                            risky_payment.png
"""

import runpy

runpy.run_path('data_cleaning.py')

print()

runpy.run_path('exploratory_analysis.py')
