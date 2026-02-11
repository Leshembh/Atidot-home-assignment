#!/usr/bin/env python3
"""
Exploratory Analysis
=====================
Step 1 — Churn Rate Report:  breaks down churn by 15+ features → churn_rate_report.txt
Step 2 — Churn by Tenure:    bar chart of churn rate per 1-year bucket → tenure_churn_histogram.png
Step 3 — Risky Channels:     payment frequency chart → risky_payment.png
                             acquisition channel table → terminal
Step 4 — Price-per-Coverage:  box plot by product type → price_per_coverage_plot.png
"""

import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker

CSV_FILE       = 'policies_standardized.csv'
ABOVE_COLOR    = '#E8D180'
BELOW_COLOR    = '#C5D4B0'
PRODUCT_TYPES  = ['Term', 'Whole', 'Universal']
PRODUCT_COLORS = ['#C5D4B0', '#E8D180', '#B0C4D4']


# ══════════════════════════════════════════════════════════════════════════════
#  STEP 1 — CHURN RATE REPORT
# ══════════════════════════════════════════════════════════════════════════════

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


def run_churn_report():
    original_stdout = sys.stdout
    try:
        with open('churn_rate_report.txt', 'w') as f:
            sys.stdout = f

            print("=" * 65)
            print("CHURN RATE ANALYSIS")
            print("=" * 65)
            print(f"\nDataset:       {len(df):,} policies")
            print(f"Total churned: {int(df['churned'].sum()):,}  ({overall_churn_rate:.1f}% overall churn rate)")
            print()

            print("=" * 65)
            print("SECTION 1: POLICY CHARACTERISTICS")
            print("How the policy structure relates to churn")
            print("=" * 65)
            print()
            churn_table(df, 'product_type',        'Product Type')
            churn_table(df, 'payment_frequency',   'Payment Frequency  ← strong signal')
            churn_table(df, 'acquisition_channel', 'Acquisition Channel')

            print("=" * 65)
            print("SECTION 2: CUSTOMER BEHAVIOR SIGNALS")
            print("Activity and engagement indicators")
            print("=" * 65)
            print()
            churn_table(df, 'late_payment_count',     'Late Payment Count  ← strongest signal')
            churn_table(df, 'customer_service_calls', 'Customer Service Calls')
            churn_table(df, 'beneficiary_updated',    'Beneficiary Updated')

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

            print("=" * 65)
            print("SECTION 4: ADD-ONS AND DISCOUNTS")
            print("Whether riders or discounts affect retention")
            print("=" * 65)
            print()
            churn_table(df, 'discount_applied',       'Discount Applied')
            churn_table(df, 'has_rider',              'Has Rider')
            churn_table(df, 'critical_illness_rider', 'Critical Illness Rider')
            churn_table(df, 'disability_rider',       'Disability Rider')

            print("=" * 65)
            print("SECTION 5: NUMERIC POLICY CHARACTERISTICS")
            print("Policy age, size, and financial signals")
            print("=" * 65)
            print()
            churn_table(df, 'tenure_group',   'Tenure Group  ← 6-8yr highest risk')
            churn_table(df, 'num_dependents', 'Number of Dependents')

    finally:
        sys.stdout = original_stdout

    print(f"Saved to: churn_rate_report.txt")


# ══════════════════════════════════════════════════════════════════════════════
#  STEP 2 — CHURN BY TENURE CHART
# ══════════════════════════════════════════════════════════════════════════════

def run_tenure_chart():
    max_tenure = df['tenure_months'].max()
    bins   = list(range(0, int(max_tenure) + 13, 12))
    labels = [f"{b//12}-{b//12 + 1}yr" for b in bins[:-1]]
    df['tenure_bin'] = pd.cut(df['tenure_months'], bins=bins, labels=labels, right=False)

    grp = (df.groupby('tenure_bin', observed=True)
             .agg(total=('policy_id', 'nunique'), churned=('churned', 'sum'))
             .assign(churn_rate=lambda d: d['churned'] / d['total'] * 100)
             .reset_index())

    colors = [ABOVE_COLOR if r > overall_churn_rate else BELOW_COLOR
              for r in grp['churn_rate']]

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(grp['tenure_bin'].astype(str), grp['churn_rate'],
                  color=colors, edgecolor='white', linewidth=0.5)

    for bar, rate in zip(bars, grp['churn_rate']):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                f'{rate:.1f}%', ha='center', va='bottom', fontsize=8.5, color='#333333')

    ax.axhline(overall_churn_rate, color='black', linestyle='--', linewidth=1.4)

    ax.set_title('Churn Rate by Tenure (1-year buckets)', fontsize=14, fontweight='bold',
                 pad=14, fontfamily='Gill Sans')
    ax.set_xlabel('Tenure', fontsize=11, fontfamily='Gill Sans')
    ax.set_ylabel('Churn Rate (%)', fontsize=11, fontfamily='Gill Sans')
    ax.set_ylim(0, grp['churn_rate'].max() * 1.2)
    ax.tick_params(axis='x', rotation=35, length=0)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    for spine in ('left', 'bottom'):
        ax.spines[spine].set_color('#aaaaaa')
        ax.spines[spine].set_linewidth(1)
    ax.grid(axis='y', linestyle='--', linewidth=0.4, alpha=0.4, color='#aaaaaa')

    ax.legend(handles=[
        mpatches.Patch(facecolor=ABOVE_COLOR, edgecolor='#888888', label='Above average'),
        mpatches.Patch(facecolor=BELOW_COLOR, edgecolor='#888888', label='Below average'),
        plt.Line2D([0], [0], color='black', linestyle='--', linewidth=1.4,
                   label=f'Overall avg: {overall_churn_rate:.1f}%'),
    ], fontsize=9, frameon=False)

    plt.tight_layout()
    plt.savefig('tenure_churn_histogram.png', dpi=150)
    plt.close()
    print(f"Saved to: tenure_churn_histogram.png")


# ══════════════════════════════════════════════════════════════════════════════
#  STEP 3 — RISKY CHANNELS AND PAYMENT METHODS
# ══════════════════════════════════════════════════════════════════════════════

def run_risky_channels():
    # ── Chart: Payment Frequency — Churn Rate ──────────────────────────────
    grp = (df.groupby('payment_frequency')
             .agg(total=('policy_id', 'nunique'), churned=('churned', 'sum'))
             .assign(churn_rate=lambda d: d['churned'] / d['total'] * 100)
             .sort_values('churn_rate', ascending=False)
             .reset_index())

    labels = grp['payment_frequency'].tolist()
    vals   = grp['churn_rate'].tolist()
    colors = [ABOVE_COLOR if v > overall_churn_rate else BELOW_COLOR for v in vals]

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(labels, vals, color=colors, edgecolor='white', linewidth=0.5, width=0.55)

    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(vals) * 0.01,
                f'{val:.1f}%', va='bottom', ha='center', fontsize=10, color='#333333')

    ax.axhline(overall_churn_rate, color='black', linestyle='--', linewidth=1.2)

    ax.set_ylim(0, max(vals) * 1.25)
    ax.set_ylabel('Churn Rate (%)', fontsize=11, fontfamily='Gill Sans')
    ax.set_title('Payment Frequency — Churn Rate',
                 fontsize=14, fontweight='bold', fontfamily='Gill Sans', pad=14)
    ax.tick_params(axis='x', labelsize=11, length=0)
    ax.tick_params(axis='y', labelsize=8)
    for label in ax.get_xticklabels():
        label.set_fontfamily('Gill Sans')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    for spine in ('left', 'bottom'):
        ax.spines[spine].set_color('#aaaaaa')
        ax.spines[spine].set_linewidth(1)
    ax.grid(axis='y', linestyle='--', linewidth=0.4, alpha=0.4, color='#aaaaaa')

    ax.legend(handles=[
        mpatches.Patch(facecolor=ABOVE_COLOR, edgecolor='#888888', label='Above average'),
        mpatches.Patch(facecolor=BELOW_COLOR, edgecolor='#888888', label='Below average'),
        plt.Line2D([0], [0], color='black', linestyle='--', linewidth=1.2,
                   label=f'Overall avg: {overall_churn_rate:.1f}%'),
    ], fontsize=9, frameon=False)

    plt.tight_layout()
    plt.savefig('risky_payment.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved to: risky_payment.png")

    # ── Table: Acquisition Channel — Churn Rate ────────────────────────────
    ch = (df.groupby('acquisition_channel')
            .agg(total=('policy_id', 'nunique'), churned=('churned', 'sum'))
            .assign(churn_rate=lambda d: d['churned'] / d['total'] * 100)
            .sort_values('churn_rate', ascending=False)
            .reset_index())

    print(f"\nAcquisition Channel — Churn Rate  (overall avg: {overall_churn_rate:.1f}%)")
    print("-" * 58)
    print(f"  {'Channel':<20} {'Total':>7} {'Churned':>8} {'Churn%':>8} {'vs avg':>8}")
    print("-" * 58)
    for _, row in ch.iterrows():
        diff = row['churn_rate'] - overall_churn_rate
        sign = '+' if diff >= 0 else ''
        print(f"  {row['acquisition_channel']:<20} {row['total']:>7,} {row['churned']:>8,} "
              f"{row['churn_rate']:>7.1f}% {sign}{diff:.1f}%")
    print("-" * 58)


# ══════════════════════════════════════════════════════════════════════════════
#  STEP 4 — PRICE-PER-COVERAGE CHART
# ══════════════════════════════════════════════════════════════════════════════

def run_price_coverage_chart():
    data = [
        df.loc[df['product_type'] == pt, 'price_per_coverage'].dropna().values * 1000
        for pt in PRODUCT_TYPES
    ]

    fig, ax = plt.subplots(figsize=(8, 6))
    bp = ax.boxplot(
        data,
        patch_artist=True,
        widths=0.45,
        medianprops=dict(color='#333333', linewidth=2),
        whiskerprops=dict(color='#777777', linewidth=1),
        capprops=dict(color='#777777', linewidth=1),
        flierprops=dict(marker='o', markersize=3, alpha=0.3,
                        markerfacecolor='#999999', markeredgecolor='none'),
        boxprops=dict(linewidth=1),
    )

    for patch, color in zip(bp['boxes'], PRODUCT_COLORS):
        patch.set_facecolor(color)
        patch.set_edgecolor('#666666')
        patch.set_linewidth(1)

    ax.set_xticks([1, 2, 3])
    ax.set_xticklabels(PRODUCT_TYPES, fontsize=12, fontfamily='Gill Sans')
    ax.set_title('Price-per-Coverage by Product Type',
                 fontsize=14, fontweight='bold', pad=14, fontfamily='Gill Sans')
    ax.set_ylabel('Premium per Unit of Coverage  (x 0.001)',
                  fontsize=11, fontfamily='Gill Sans')
    ax.set_ylim(bottom=0)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.2f'))
    ax.tick_params(axis='x', length=0)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    for spine in ('left', 'bottom'):
        ax.spines[spine].set_color('#aaaaaa')
        ax.spines[spine].set_linewidth(1)
    ax.grid(axis='y', linestyle='--', linewidth=0.5, alpha=0.4, color='#aaaaaa')

    plt.tight_layout()
    plt.savefig('price_per_coverage_plot.png', dpi=150)
    plt.close()
    print(f"Saved to: price_per_coverage_plot.png")


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════

df                 = pd.read_csv(CSV_FILE)
overall_churn_rate = df['churned'].mean() * 100

df['price_per_coverage'] = df['premium'] / df['coverage_amount']
df['age_group']          = pd.cut(
    df['customer_age'],
    bins=[17, 30, 40, 50, 60, 70, 120],
    labels=['18-30', '31-40', '41-50', '51-60', '61-70', '71+']
)
df['tenure_group']       = pd.cut(
    df['tenure_months'],
    bins=[0, 12, 24, 36, 48, 60, 72, 84, 96, 108, 120, 9999],
    labels=['0-1yr', '1-2yr', '2-3yr', '3-4yr', '4-5yr',
            '5-6yr', '6-7yr', '7-8yr', '8-9yr', '9-10yr', '10yr+'],
    right=False
)

print("=" * 60)
print("STEP 1 — CHURN RATE REPORT")
print("=" * 60)
run_churn_report()

print()
print("=" * 60)
print("STEP 2 — CHURN BY TENURE CHART")
print("=" * 60)
run_tenure_chart()

print()
print("=" * 60)
print("STEP 3 — RISKY CHANNELS")
print("=" * 60)
run_risky_channels()

print()
print("=" * 60)
print("STEP 4 — PRICE-PER-COVERAGE CHART")
print("=" * 60)
run_price_coverage_chart()
