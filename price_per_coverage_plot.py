#!/usr/bin/env python3
"""
Price-per-Coverage by Product Type
Output: price_per_coverage_plot.png
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

OUTPUT_FILE   = 'price_per_coverage_plot.png'
PRODUCT_TYPES = ['Term', 'Whole', 'Universal']
COLORS        = ['#C5D4B0', '#E8D180', '#B0C4D4']

# ── Load & compute ─────────────────────────────────────────────────────────────
df = pd.read_csv('policies_standardized.csv')
df['price_per_coverage'] = df['premium'] / df['coverage_amount']

# ── Prepare data (scaled ×1000 for readable y-axis) ───────────────────────────
data = [
    df.loc[df['product_type'] == pt, 'price_per_coverage'].dropna().values * 1000
    for pt in PRODUCT_TYPES
]

# ── Plot ───────────────────────────────────────────────────────────────────────
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

for patch, color in zip(bp['boxes'], COLORS):
    patch.set_facecolor(color)
    patch.set_edgecolor('#666666')
    patch.set_linewidth(1)

# ── Axes & style ───────────────────────────────────────────────────────────────
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

# ── Save ───────────────────────────────────────────────────────────────────────
plt.tight_layout()
plt.savefig(OUTPUT_FILE, dpi=150)
plt.close()
print(f"Saved to: {OUTPUT_FILE}")
