#!/usr/bin/env python3
"""
Churn Risk by Payment Frequency & Acquisition Channel
  - Chart: churn rate by payment frequency  → risky_payment.png
  - Table: churn rate by acquisition channel → printed to terminal
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

ABOVE_COLOR = '#E8D180'
BELOW_COLOR = '#C5D4B0'
OUTPUT_FILE = 'risky_payment.png'

# ── Load ───────────────────────────────────────────────────────────────────────
df            = pd.read_csv('policies_standardized.csv')
overall_churn = df['churned'].mean() * 100


# ── Chart: Payment Frequency — Churn Rate ─────────────────────────────────────
grp = (df.groupby('payment_frequency')
         .agg(total=('policy_id', 'nunique'), churned=('churned', 'sum'))
         .assign(churn_rate=lambda d: d['churned'] / d['total'] * 100)
         .sort_values('churn_rate', ascending=False)
         .reset_index())

labels = grp['payment_frequency'].tolist()
vals   = grp['churn_rate'].tolist()
colors = [ABOVE_COLOR if v > overall_churn else BELOW_COLOR for v in vals]

fig, ax = plt.subplots(figsize=(7, 5))
bars = ax.bar(labels, vals, color=colors, edgecolor='white', linewidth=0.5, width=0.55)

# Value labels on each bar
for bar, val in zip(bars, vals):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(vals) * 0.01,
            f'{val:.1f}%', va='bottom', ha='center', fontsize=10, color='#333333')

# Overall average line
ax.axhline(overall_churn, color='black', linestyle='--', linewidth=1.2)

# ── Axes & style ───────────────────────────────────────────────────────────────
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

# ── Legend ─────────────────────────────────────────────────────────────────────
ax.legend(handles=[
    mpatches.Patch(facecolor=ABOVE_COLOR, edgecolor='#888888', label='Above average'),
    mpatches.Patch(facecolor=BELOW_COLOR, edgecolor='#888888', label='Below average'),
    plt.Line2D([0], [0], color='black', linestyle='--', linewidth=1.2,
               label=f'Overall avg: {overall_churn:.1f}%'),
], fontsize=9, frameon=False)

# ── Save ───────────────────────────────────────────────────────────────────────
plt.tight_layout()
plt.savefig(OUTPUT_FILE, dpi=150, bbox_inches='tight')
plt.close()
print(f"Saved to: {OUTPUT_FILE}")


# ── Table: Acquisition Channel — Churn Rate ───────────────────────────────────
ch = (df.groupby('acquisition_channel')
        .agg(total=('policy_id', 'nunique'), churned=('churned', 'sum'))
        .assign(churn_rate=lambda d: d['churned'] / d['total'] * 100)
        .sort_values('churn_rate', ascending=False)
        .reset_index())

print(f"\nAcquisition Channel — Churn Rate  (overall avg: {overall_churn:.1f}%)")
print("-" * 58)
print(f"  {'Channel':<20} {'Total':>7} {'Churned':>8} {'Churn%':>8} {'vs avg':>8}")
print("-" * 58)
for _, row in ch.iterrows():
    diff = row['churn_rate'] - overall_churn
    sign = '+' if diff >= 0 else ''
    print(f"  {row['acquisition_channel']:<20} {row['total']:>7,} {row['churned']:>8,} "
          f"{row['churn_rate']:>7.1f}% {sign}{diff:.1f}%")
print("-" * 58)
