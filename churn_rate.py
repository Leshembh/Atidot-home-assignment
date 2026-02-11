#!/usr/bin/env python3
"""
Churn Rate Analysis
====================
For each feature, breaks down total policies, churned count, churn rate,
and deviation from the overall average. Groups sorted highest churn first.

Input:  policies_standardized.csv
Output: churn_rate_report.txt
"""

import sys
import pandas as pd

OUTPUT_FILE = 'churn_rate_report.txt'

# ── Load ───────────────────────────────────────────────────────────────────────
df                 = pd.read_csv('policies_standardized.csv')
overall_churn_rate = df['churned'].mean() * 100


# ── Helper ─────────────────────────────────────────────────────────────────────
def churn_table(df, col, title):
    """Print a churn rate breakdown table for a given column."""
    grp = (df.groupby(col)
             .agg(Total=('policy_id', 'nunique'), Churned=('churned', 'sum'))
             .assign(**{'Rate%': lambda d: d['Churned'] / d['Total'] * 100})
             .sort_values('Rate%', ascending=False))

    print(f"  {title}")
    print(f"  {'-' * 60}")
    print(f"  {'Value':<22} {'Total':>6}  {'Churned':>8}  {'Churn%':>7}  {'vs avg':>7}")
    print(f"  {'·' * 52}")
    for val, row in grp.iterrows():
        diff = row['Rate%'] - overall_churn_rate
        sign = '+' if diff >= 0 else ''
        print(f"  {str(val):<22} {int(row['Total']):>6,}  {int(row['Churned']):>8,}  "
              f"{row['Rate%']:>6.1f}%  {sign}{diff:>5.1f}%")
    print(f"  {'·' * 52}")
    print(f"  {'TOTAL':<22} {grp['Total'].sum():>6,}  {int(grp['Churned'].sum()):>8,}")
    print()


# ── Prepare derived columns ────────────────────────────────────────────────────
df['age_group'] = pd.cut(
    df['customer_age'],
    bins=[17, 30, 40, 50, 60, 70, 120],
    labels=['18-30', '31-40', '41-50', '51-60', '61-70', '71+']
)

df['tenure_group'] = pd.cut(
    df['tenure_months'],
    bins=[0, 12, 24, 36, 48, 60, 72, 84, 96, 108, 120, 9999],
    labels=['0-1yr', '1-2yr', '2-3yr', '3-4yr', '4-5yr',
            '5-6yr', '6-7yr', '7-8yr', '8-9yr', '9-10yr', '10yr+'],
    right=False
)


# ── Write report ───────────────────────────────────────────────────────────────
original_stdout = sys.stdout

try:
    with open(OUTPUT_FILE, 'w') as f:
        sys.stdout = f

        print("=" * 65)
        print("CHURN RATE ANALYSIS")
        print("=" * 65)
        print(f"\nDataset:       {len(df):,} policies")
        print(f"Total churned: {int(df['churned'].sum()):,}  ({overall_churn_rate:.1f}% overall churn rate)")
        print()

        # Section 1 — Policy characteristics
        print("=" * 65)
        print("SECTION 1: POLICY CHARACTERISTICS")
        print("How the policy structure relates to churn")
        print("=" * 65)
        print()
        churn_table(df, 'product_type',        'Product Type')
        churn_table(df, 'payment_frequency',   'Payment Frequency  ← strong signal')
        churn_table(df, 'acquisition_channel', 'Acquisition Channel')

        # Section 2 — Customer behavior signals
        print("=" * 65)
        print("SECTION 2: CUSTOMER BEHAVIOR SIGNALS")
        print("Activity and engagement indicators")
        print("=" * 65)
        print()
        churn_table(df, 'late_payment_count',     'Late Payment Count  ← strongest signal')
        churn_table(df, 'customer_service_calls', 'Customer Service Calls')
        churn_table(df, 'beneficiary_updated',    'Beneficiary Updated')

        # Section 3 — Customer demographics
        print("=" * 65)
        print("SECTION 3: CUSTOMER DEMOGRAPHICS")
        print("Who the customer is")
        print("=" * 65)
        print()
        churn_table(df, 'age_group',           'Age Group')
        churn_table(df, 'customer_gender_std', 'Gender (standardized)')
        churn_table(df, 'marital_status',      'Marital Status')
        churn_table(df, 'income_band',         'Income Band')
        churn_table(df, 'country_std',         'Country (standardized)')

        # Section 4 — Add-ons and discounts
        print("=" * 65)
        print("SECTION 4: ADD-ONS AND DISCOUNTS")
        print("Whether riders or discounts affect retention")
        print("=" * 65)
        print()
        churn_table(df, 'discount_applied',       'Discount Applied')
        churn_table(df, 'has_rider',              'Has Rider')
        churn_table(df, 'critical_illness_rider', 'Critical Illness Rider')
        churn_table(df, 'disability_rider',       'Disability Rider')

        # Section 5 — Numeric policy characteristics
        print("=" * 65)
        print("SECTION 5: NUMERIC POLICY CHARACTERISTICS")
        print("Policy age, size, and financial signals")
        print("=" * 65)
        print()
        churn_table(df, 'tenure_group',   'Tenure Group  ← 6-8yr highest risk')
        churn_table(df, 'num_dependents', 'Number of Dependents')

finally:
    sys.stdout = original_stdout

print(f"Report saved to: {OUTPUT_FILE}")
