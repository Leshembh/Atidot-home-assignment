#!/usr/bin/env python3
"""
Customer Demographic Standardization
=====================================
Resolves inconsistent customer_gender and country values across policies
for the same customer. Adds standardized columns and conflict flags.

Input:  policies.csv
Output: policies_standardized.csv
"""

import pandas as pd

# ── Config ─────────────────────────────────────────────────────────────────────
CSV_FILE    = 'policies.csv'
OUTPUT_FILE = 'policies_standardized.csv'


# ── Load & prepare ─────────────────────────────────────────────────────────────
df = pd.read_csv(CSV_FILE)

for date_col in ['snapshot_date', 'policy_start_date']:
    if date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')

df.replace('', pd.NA, inplace=True)

if 'income_band' in df.columns:
    df['income_band'] = df['income_band'].fillna('Unknown')


# ── Resolve conflicts per customer ─────────────────────────────────────────────
def resolve(series):
    """
    Given a Series of values for one customer across all their policies:
    - All agree      → (value, no conflict)
    - One clear mode → (mode,  conflict flagged)
    - Tied modes     → ("Conflict", conflict flagged)
    - All null       → ("Unknown", no conflict)
    """
    values = series.dropna()
    if len(values) == 0:
        return 'Unknown', 0
    unique = values.unique()
    if len(unique) == 1:
        return unique[0], 0
    mode = values.mode()
    if len(mode) == 1:
        return mode.iloc[0], 1
    return 'Conflict', 1


# ── Build customer-level table ─────────────────────────────────────────────────
records = []
for customer_id, group in df.groupby('customer_id'):
    gender_val,  gender_conflict  = resolve(group['customer_gender'])
    country_val, country_conflict = resolve(group['country'])
    records.append({
        'customer_id':      customer_id,
        'gender_std':       gender_val,
        'gender_conflict':  gender_conflict,
        'country_std':      country_val,
        'country_conflict': country_conflict,
    })

df_customer = pd.DataFrame(records)


# ── Merge back to policy level ─────────────────────────────────────────────────
df = df.merge(df_customer, on='customer_id', how='left')
df.rename(columns={'gender_std': 'customer_gender_std'}, inplace=True)


# ── Summary ────────────────────────────────────────────────────────────────────
n = len(df_customer)
print("=" * 60)
print("CUSTOMER DEMOGRAPHIC STANDARDIZATION SUMMARY")
print("=" * 60)
print(f"  Total unique customers:          {n:,}")
print(f"  Customers with gender conflict:  {df_customer['gender_conflict'].sum():,}  ({df_customer['gender_conflict'].mean()*100:.1f}%)")
print(f"  Customers with country conflict: {df_customer['country_conflict'].sum():,}  ({df_customer['country_conflict'].mean()*100:.1f}%)")


# ── Save ───────────────────────────────────────────────────────────────────────
df.to_csv(OUTPUT_FILE, index=False)
print(f"\nSaved to: {OUTPUT_FILE}  ({len(df):,} rows, {len(df.columns)} columns)")
