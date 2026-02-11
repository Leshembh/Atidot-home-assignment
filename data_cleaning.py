#!/usr/bin/env python3
"""
Data Cleaning Pipeline
=======================
Step 1 — Data Quality Checks:  validates policies.csv  → sanity_checks_report.txt
Step 2 — Data Cleaning:        standardizes demographics → policies_standardized.csv
"""

import sys
import pandas as pd

CSV_FILE               = 'policies.csv'
SANITY_OUTPUT          = 'sanity_checks_report.txt'
STANDARDIZED_OUTPUT    = 'policies_standardized.csv'


# ══════════════════════════════════════════════════════════════════════════════
#  STEP 1 — DATA QUALITY CHECKS
# ══════════════════════════════════════════════════════════════════════════════

def print_shape(df):
    print("\n" + "=" * 80)
    print("1. SHAPE")
    print("=" * 80)
    print(f"  Rows:    {len(df):,}")
    print(f"  Columns: {len(df.columns)}")


def print_dtypes(df):
    print("\n" + "=" * 80)
    print("2. DATA TYPES")
    print("=" * 80)
    for dtype, count in df.dtypes.value_counts().items():
        print(f"  {dtype}: {count} columns")
    print("\n  Detailed:")
    for col, dtype in df.dtypes.items():
        print(f"    {col:30} {dtype}")


def print_categorical_distribution(df):
    print("\n" + "=" * 80)
    print("3. CATEGORICAL DISTRIBUTION")
    print("=" * 80)

    for col in ['customer_gender', 'marital_status', 'product_type',
                'payment_frequency', 'acquisition_channel', 'country', 'income_band']:
        if col not in df.columns:
            continue
        print(f"\n  {col}:")
        print("  " + "-" * 55)
        for value, count in df[col].value_counts(dropna=False).items():
            label = 'NULL/Missing' if pd.isna(value) else str(value)
            print(f"    {label:30} {count:6,}  ({count / len(df) * 100:5.1f}%)")

    if 'churn_reason' in df.columns and 'churned' in df.columns:
        churned_df = df[df['churned'] == True]
        print(f"\n  churn_reason  (churned=True only, n={len(churned_df):,}):")
        print("  " + "-" * 55)
        for value, count in churned_df['churn_reason'].value_counts(dropna=False).items():
            label = 'NULL/Missing' if pd.isna(value) else str(value)
            print(f"    {label:30} {count:6,}  ({count / len(churned_df) * 100:5.1f}%)")


def print_missing_values(df):
    print("\n" + "=" * 80)
    print("4. MISSING VALUES")
    print("=" * 80)

    missing    = df.isnull().sum()
    missing_df = (
        pd.DataFrame({'Column': missing.index, 'Missing': missing.values,
                      'Percent': (missing / len(df) * 100).round(2).values})
        .query('Missing > 0')
        .sort_values('Missing', ascending=False)
    )

    if missing_df.empty:
        print("  No missing values found.")
        return

    justifications = {}
    if 'churned' in df.columns and 'policy_end_date' in df.columns:
        tmp = df.copy()
        tmp['policy_end_date'] = pd.to_datetime(tmp['policy_end_date'], errors='coerce')
        if tmp['policy_end_date'].isna().sum() == (tmp['churned'] == False).sum():
            justifications['policy_end_date'] = '✓ churned=False'
            justifications['churn_reason']    = '✓ churned=False'
    if 'discount_applied' in df.columns and 'discount_rate' in df.columns:
        if df['discount_rate'].isna().sum() == (df['discount_applied'] == False).sum():
            justifications['discount_rate'] = '✓ discount_applied=False'
    if 'acquisition_channel' in df.columns and 'agent_id' in df.columns:
        if df['agent_id'].isna().sum() == (df['acquisition_channel'].str.lower() != 'agent').sum():
            justifications['agent_id'] = '✓ acquisition_channel != Agent'

    print(f"\n  Columns with missing values: {len(missing_df)}")
    print(f"\n  {'Column':<30} {'Missing':>8}  {'%':>7}   Justification")
    print("  " + "-" * 70)
    for _, row in missing_df.iterrows():
        justif = justifications.get(row['Column'], '-')
        print(f"  {row['Column']:<30} {row['Missing']:>8,.0f}  {row['Percent']:>6.2f}%   {justif}")


def print_duplicates(df):
    print("\n" + "=" * 80)
    print("5. DUPLICATES")
    print("=" * 80)
    print(f"  Full row duplicates:    {df.duplicated().sum():,}")
    if 'policy_id' in df.columns:
        id_dupes = df['policy_id'].duplicated().sum()
        print(f"  Duplicate policy_id:    {id_dupes:,}")
        if id_dupes > 0:
            for pid, count in df[df['policy_id'].duplicated(keep=False)]['policy_id'].value_counts().head(10).items():
                print(f"    {pid}: {count} occurrences")
    if 'customer_id' in df.columns:
        cust_dupes = df['customer_id'].duplicated().sum()
        print(f"  Duplicate customer_id:  {cust_dupes:,}")
        if cust_dupes > 0:
            print("  (showing top 10)")
            for cid, count in df[df['customer_id'].duplicated(keep=False)]['customer_id'].value_counts().head(10).items():
                print(f"    {cid}: {count} occurrences")


def print_impossible_values(df):
    print("\n" + "=" * 80)
    print("6. IMPOSSIBLE VALUES")
    print("=" * 80)

    issues = []
    checks = [
        ('customer_age',          lambda s: (s < 18) | (s > 120),  'not in [18–120]'),
        ('num_dependents',        lambda s: s < 0,                  '< 0'),
        ('coverage_amount',       lambda s: s <= 0,                 '<= 0'),
        ('premium',               lambda s: s <= 0,                 '<= 0'),
        ('tenure_months',         lambda s: s < 0,                  '< 0'),
        ('renewal_count',         lambda s: s < 0,                  '< 0'),
        ('num_riders',            lambda s: s < 0,                  '< 0'),
        ('late_payment_count',    lambda s: s < 0,                  '< 0'),
        ('customer_service_calls',lambda s: s < 0,                  '< 0'),
        ('premium_change_pct',    lambda s: (s < -1) | (s > 1),    'not in [-1, 1]'),
        ('discount_rate',         lambda s: (s < 0) | (s > 1),     'not in [0, 1]'),
    ]
    for col, fn, label in checks:
        if col in df.columns:
            n = fn(df[col]).sum()
            if n > 0:
                issues.append(f"  {col} {label}: {n:,}")

    if 'policy_start_date' in df.columns and 'policy_end_date' in df.columns:
        tmp = df[['policy_start_date', 'policy_end_date']].copy()
        tmp['policy_start_date'] = pd.to_datetime(tmp['policy_start_date'], errors='coerce')
        tmp['policy_end_date']   = pd.to_datetime(tmp['policy_end_date'],   errors='coerce')
        mask = tmp['policy_start_date'].notna() & tmp['policy_end_date'].notna()
        n = (tmp.loc[mask, 'policy_end_date'] < tmp.loc[mask, 'policy_start_date']).sum()
        if n > 0:
            issues.append(f"  policy_end_date before policy_start_date: {n:,}")

    if 'churned' in df.columns and 'policy_end_date' in df.columns:
        tmp = df.copy()
        tmp['policy_end_date'] = pd.to_datetime(tmp['policy_end_date'], errors='coerce')
        n1 = ((tmp['churned'] == True)  & tmp['policy_end_date'].isna()).sum()
        n2 = (tmp['policy_end_date'].notna() & (tmp['churned'] == False)).sum()
        if n1 > 0: issues.append(f"  churned=True but policy_end_date missing: {n1:,}")
        if n2 > 0: issues.append(f"  policy_end_date exists but churned=False: {n2:,}")

    if 'discount_applied' in df.columns and 'discount_rate' in df.columns:
        n1 = ((df['discount_applied'] == True)  & df['discount_rate'].isna()).sum()
        n2 = (df['discount_rate'].notna() & (df['discount_applied'] == False)).sum()
        if n1 > 0: issues.append(f"  discount_applied=True but discount_rate missing: {n1:,}")
        if n2 > 0: issues.append(f"  discount_rate exists but discount_applied=False: {n2:,}")

    if 'acquisition_channel' in df.columns and 'agent_id' in df.columns:
        is_agent = df['acquisition_channel'].str.lower() == 'agent'
        n1 = (is_agent  & df['agent_id'].isna()).sum()
        n2 = (df['agent_id'].notna() & ~is_agent).sum()
        if n1 > 0: issues.append(f"  acquisition_channel=Agent but agent_id missing: {n1:,}")
        if n2 > 0: issues.append(f"  agent_id exists but acquisition_channel != Agent: {n2:,}")

    if issues:
        print(f"\n  Issues found: {len(issues)}\n")
        for issue in issues:
            print(issue)
    else:
        print("  No impossible values detected.")


def print_outliers(df):
    print("\n" + "=" * 80)
    print("7. OUTLIERS  (IQR method: outside Q1 − 1.5×IQR  /  Q3 + 1.5×IQR)")
    print("=" * 80)

    numeric_cols = [
        'customer_age', 'coverage_amount', 'premium', 'tenure_months',
        'num_dependents', 'renewal_count', 'num_riders', 'late_payment_count',
        'customer_service_calls', 'premium_change_pct', 'discount_rate',
    ]
    print(f"\n  {'Column':<28} {'Q1':>8} {'Q3':>8} {'IQR':>8} {'Lower':>10} {'Upper':>10} {'Outliers':>10} {'%':>6}")
    print("  " + "-" * 92)

    any_outliers = False
    for col in numeric_cols:
        if col not in df.columns:
            continue
        s = df[col].dropna()
        if len(s) == 0:
            continue
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        iqr = q3 - q1
        if iqr == 0:
            continue
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        n_out = ((s < lower) | (s > upper)).sum()
        pct   = n_out / len(s) * 100
        flag  = '  <--' if n_out > 0 else ''
        print(f"  {col:<28} {q1:>8.2f} {q3:>8.2f} {iqr:>8.2f} {lower:>10.2f} {upper:>10.2f} {n_out:>10,} {pct:>5.1f}%{flag}")
        if n_out > 0:
            any_outliers = True

    if not any_outliers:
        print("\n  No outliers detected.")


def run_quality_checks():
    original_stdout = sys.stdout
    try:
        with open(SANITY_OUTPUT, 'w') as f:
            sys.stdout = f
            print("=" * 80)
            print("DATA QUALITY CHECKS — policies.csv")
            print("=" * 80)
            df = pd.read_csv(CSV_FILE)
            print_shape(df)
            print_dtypes(df)
            print_categorical_distribution(df)
            print_missing_values(df)
            print_duplicates(df)
            print_impossible_values(df)
            print_outliers(df)
            print("\n" + "=" * 80)
            print("CHECKS COMPLETE")
            print("=" * 80 + "\n")
    finally:
        sys.stdout = original_stdout
    print(f"Saved to: {SANITY_OUTPUT}")


# ══════════════════════════════════════════════════════════════════════════════
#  STEP 2 — DATA CLEANING
# ══════════════════════════════════════════════════════════════════════════════

def resolve(series):
    """
    Resolve a customer's demographic field across multiple policies:
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


def run_data_cleaning():
    df = pd.read_csv(CSV_FILE)

    for date_col in ['snapshot_date', 'policy_start_date']:
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    df.replace('', pd.NA, inplace=True)
    if 'income_band' in df.columns:
        df['income_band'] = df['income_band'].fillna('Unknown')

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
    df = df.merge(df_customer, on='customer_id', how='left')
    df.rename(columns={'gender_std': 'customer_gender_std'}, inplace=True)

    n = len(df_customer)
    print(f"\n  Total unique customers:          {n:,}")
    print(f"  Customers with gender conflict:  {df_customer['gender_conflict'].sum():,}  ({df_customer['gender_conflict'].mean()*100:.1f}%)")
    print(f"  Customers with country conflict: {df_customer['country_conflict'].sum():,}  ({df_customer['country_conflict'].mean()*100:.1f}%)")

    df.to_csv(STANDARDIZED_OUTPUT, index=False)
    print(f"Saved to: {STANDARDIZED_OUTPUT}  ({len(df):,} rows, {len(df.columns)} columns)")


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════

print("=" * 60)
print("STEP 1 — DATA QUALITY CHECKS")
print("=" * 60)
run_quality_checks()

print()
print("=" * 60)
print("STEP 2 — DATA CLEANING")
print("=" * 60)
run_data_cleaning()
