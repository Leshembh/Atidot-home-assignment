#!/usr/bin/env python3
"""
Churn Rate by Tenure
Output: tenure_churn_histogram.png
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

ABOVE_COLOR = '#E8D180'
BELOW_COLOR = '#C5D4B0'
OUTPUT_FILE = 'tenure_churn_histogram.png'

# ── Load & aggregate ───────────────────────────────────────────────────────────
df                 = pd.read_csv('policies_standardized.csv')
overall_churn_rate = df['churned'].mean() * 100

# Bin tenure into 12-month buckets
max_tenure = df['tenure_months'].max()
bins   = list(range(0, int(max_tenure) + 13, 12))
labels = [f"{b//12}-{b//12 + 1}yr" for b in bins[:-1]]
df['tenure_bin'] = pd.cut(df['tenure_months'], bins=bins, labels=labels, right=False)

grp = (df.groupby('tenure_bin', observed=True)
         .agg(total=('policy_id', 'nunique'), churned=('churned', 'sum'))
         .assign(churn_rate=lambda d: d['churned'] / d['total'] * 100)
         .reset_index())

# ── Plot ───────────────────────────────────────────────────────────────────────
colors = [ABOVE_COLOR if r > overall_churn_rate else BELOW_COLOR
          for r in grp['churn_rate']]

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(grp['tenure_bin'].astype(str), grp['churn_rate'],
              color=colors, edgecolor='white', linewidth=0.5)

# Value labels on each bar
for bar, rate in zip(bars, grp['churn_rate']):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
            f'{rate:.1f}%', ha='center', va='bottom', fontsize=8.5, color='#333333')

# Overall average line
ax.axhline(overall_churn_rate, color='black', linestyle='--', linewidth=1.4)

# ── Axes & style ───────────────────────────────────────────────────────────────
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

# ── Legend ─────────────────────────────────────────────────────────────────────
ax.legend(handles=[
    mpatches.Patch(facecolor=ABOVE_COLOR, edgecolor='#888888', label='Above average'),
    mpatches.Patch(facecolor=BELOW_COLOR, edgecolor='#888888', label='Below average'),
    plt.Line2D([0], [0], color='black', linestyle='--', linewidth=1.4,
               label=f'Overall avg: {overall_churn_rate:.1f}%'),
], fontsize=9, frameon=False)

# ── Save ───────────────────────────────────────────────────────────────────────
plt.tight_layout()
plt.savefig(OUTPUT_FILE, dpi=150)
plt.close()
print(f"Saved to: {OUTPUT_FILE}")
