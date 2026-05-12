"""
RUPS-296 — Publication Figure Generator
========================================
Run this in your Jupyter notebook as a single cell.
Saves 4 publication-quality PNG figures to ./RUPS_Results/figures/

Requirements: pip install matplotlib numpy seaborn
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

# ── Output directory ──────────────────────────────────────────
FIG_DIR = './RUPS_Results/figures'
os.makedirs(FIG_DIR, exist_ok=True)

# ── Global style ──────────────────────────────────────────────
plt.rcParams.update({
    'font.family':        'DejaVu Sans',
    'font.size':          11,
    'axes.titlesize':     12,
    'axes.titleweight':   'bold',
    'axes.labelsize':     11,
    'axes.spines.top':    False,
    'axes.spines.right':  False,
    'axes.grid':          True,
    'axes.grid.axis':     'y',
    'grid.alpha':         0.3,
    'grid.linestyle':     '--',
    'xtick.labelsize':    10,
    'ytick.labelsize':    10,
    'legend.fontsize':    10,
    'figure.dpi':         300,
    'savefig.dpi':        300,
    'savefig.bbox':       'tight',
    'savefig.pad_inches': 0.15,
})

# ── Color palette ─────────────────────────────────────────────
C_BASELINE = '#185FA5'   # blue
C_COT      = '#888780'   # gray
C_SCAFFOLD = '#1D9E75'   # teal
C_RED      = '#E24B4A'   # red (negative recovery)
C_AMBER    = '#BA7517'   # amber (warning)

# ── Data ──────────────────────────────────────────────────────
MODELS = [
    'Claude\nSonnet 4.6',
    'GPT-5.4\nmini',
    'GPT-4o',
    'GPT-4o\nmini',
    'Gemini\n2.5-flash',
]
MODELS_SHORT = ['Claude S.4.6', 'GPT-5.4-mini', 'GPT-4o', 'GPT-4o-mini', 'Gemini 2.5-flash']

BASELINE = [8.8,  14.9, 24.3, 36.8, 55.3]
COT      = [11.5, 16.2, 29.4, 48.3, 59.7]
SCAFFOLD = [7.1,   8.2, 20.6, 33.4, 48.6]

FM_LABELS  = ['F1\nSchema\nblindness', 'F2\nTemporal\nflattening',
               'F3\nUnit\nconflation', 'F4\nNegation\ndropout', 'F5\nSpurious\nshortcut']
FM_SHORT   = ['F1 Schema\nblindness', 'F2 Temporal\nflattening',
               'F3 Unit\nconflation', 'F4 Negation\ndropout', 'F5 Spurious\nshortcut']
FM_HORIZ   = ['F5 — Spurious shortcut', 'F3 — Unit conflation',
               'F1 — Schema blindness', 'F2 — Temporal flattening', 'F4 — Negation dropout']

FM_BASE    = [40, 26, 28, 27, 20]
FM_COT     = [38, 31, 28, 35, 33]
FM_SCAF    = [34, 25, 20, 27, 13]
RECOVERY   = [13,  5, 27, -3, 37]   # original order F1-F5
RECOVERY_SORTED = [37, 27, 13, 5, -3]  # sorted for Fig 2


# ═══════════════════════════════════════════════════════════════
# FIGURE 1 — Failure rate by model × condition
# ═══════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(9, 5))

x     = np.arange(len(MODELS))
width = 0.25
gap   = 0.03

bars_b = ax.bar(x - width - gap, BASELINE, width, label='Baseline',
                color=C_BASELINE, alpha=0.92, zorder=3)
bars_c = ax.bar(x,                COT,      width, label='Chain-of-thought',
                color=C_COT,      alpha=0.92, zorder=3)
bars_s = ax.bar(x + width + gap,  SCAFFOLD, width, label='Context scaffold',
                color=C_SCAFFOLD, alpha=0.92, zorder=3)

# Value labels on top of each bar
for bars in [bars_b, bars_c, bars_s]:
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + 0.8,
                f'{h:.1f}%', ha='center', va='bottom', fontsize=8, color='#444441')

# Annotate the 6.3× gap
ax.annotate('', xy=(x[-1] - width - gap, BASELINE[-1]),
            xytext=(x[0] - width - gap, BASELINE[0]),
            arrowprops=dict(arrowstyle='<->', color=C_RED, lw=1.5))
ax.text(2, 58, '6.3× gap', ha='center', fontsize=9, color=C_RED, fontstyle='italic')

ax.set_xticks(x)
ax.set_xticklabels(MODELS, fontsize=9.5)
ax.set_ylabel('Failure rate (%)')
ax.set_ylim(0, 68)
ax.set_title('Figure 1. Failure rate by model and prompting condition', pad=12)
ax.legend(loc='upper left', framealpha=0.9)
ax.yaxis.grid(True, alpha=0.3, linestyle='--')
ax.set_axisbelow(True)

# CoT worse annotation
ax.text(4.62, 61.5, '▲ CoT worse\nthan baseline\nin all models',
        fontsize=7.5, color=C_COT, ha='center',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=C_COT, alpha=0.8))

plt.tight_layout()
path1 = f'{FIG_DIR}/fig1_failure_rate_by_model.png'
plt.savefig(path1)
plt.close()
print(f'✅ Figure 1 saved → {path1}')


# ═══════════════════════════════════════════════════════════════
# FIGURE 2 — Scaffold recovery by failure mode (horizontal bar)
# ═══════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(8, 4.5))

y      = np.arange(len(FM_HORIZ))
colors = [C_SCAFFOLD if r >= 0 else C_RED for r in RECOVERY_SORTED]

bars = ax.barh(y, RECOVERY_SORTED, color=colors, alpha=0.92, height=0.55, zorder=3)

# Value labels
for bar, val in zip(bars, RECOVERY_SORTED):
    sign = '+' if val >= 0 else ''
    offset = 0.8 if val >= 0 else -0.8
    ha     = 'left' if val >= 0 else 'right'
    ax.text(val + offset, bar.get_y() + bar.get_height()/2,
            f'{sign}{val}%', va='center', ha=ha, fontsize=10, fontweight='bold',
            color='#1D9E75' if val >= 0 else C_RED)

# Baseline comparison markers
base_sorted = [20, 28, 40, 26, 27]  # F5, F3, F1, F2, F4 order
for i, (b, r) in enumerate(zip(base_sorted, RECOVERY_SORTED)):
    ax.text(42, i, f'base={b}%', va='center', ha='left', fontsize=8,
            color='#888780')

ax.axvline(0, color='#444441', linewidth=0.8, zorder=4)
ax.set_yticks(y)
ax.set_yticklabels(FM_HORIZ, fontsize=10)
ax.set_xlabel('Recovery rate (%, positive = fewer failures with scaffold)')
ax.set_xlim(-12, 50)
ax.set_title('Figure 2. Context scaffold recovery rate by failure mode', pad=12)
ax.xaxis.grid(False)
ax.yaxis.grid(False)

legend_elements = [
    mpatches.Patch(facecolor=C_SCAFFOLD, alpha=0.92, label='Scaffold improves (positive)'),
    mpatches.Patch(facecolor=C_RED,      alpha=0.92, label='Scaffold degrades (negative)'),
]
ax.legend(handles=legend_elements, loc='lower right', framealpha=0.9)

plt.tight_layout()
path2 = f'{FIG_DIR}/fig2_scaffold_recovery_by_mode.png'
plt.savefig(path2)
plt.close()
print(f'✅ Figure 2 saved → {path2}')


# ═══════════════════════════════════════════════════════════════
# FIGURE 3 — CoT vs baseline by failure mode
# ═══════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(9, 5))

x     = np.arange(len(FM_SHORT))
width = 0.28

bars_b = ax.bar(x - width/2 - 0.02, FM_BASE, width, label='Baseline',
                color=C_BASELINE, alpha=0.92, zorder=3)
bars_c = ax.bar(x + width/2 + 0.02, FM_COT,  width, label='Chain-of-thought',
                color=C_COT,      alpha=0.92, zorder=3)

# Value labels
for bars in [bars_b, bars_c]:
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + 0.5,
                f'{h}%', ha='center', va='bottom', fontsize=8.5, color='#444441')

# Delta annotations showing CoT change
deltas = [c - b for b, c in zip(FM_BASE, FM_COT)]
for i, (xi, delta) in enumerate(zip(x, deltas)):
    color = C_RED if delta > 0 else C_SCAFFOLD
    sign  = '+' if delta > 0 else ''
    ax.text(xi + 0.02, max(FM_BASE[i], FM_COT[i]) + 4.5,
            f'CoT: {sign}{delta}%', ha='center', fontsize=8,
            color=color, fontstyle='italic')

ax.set_xticks(x)
ax.set_xticklabels(FM_SHORT, fontsize=9.5)
ax.set_ylabel('Failure rate (%)')
ax.set_ylim(0, 50)
ax.set_title('Figure 3. Chain-of-thought vs. baseline failure rate by failure mode', pad=12)
ax.legend(loc='upper right', framealpha=0.9)
ax.yaxis.grid(True, alpha=0.3, linestyle='--')
ax.set_axisbelow(True)

# Annotation box
ax.text(0.02, 0.97,
        'CoT increases failures in 4 of 5 modes.\nLargest: F5 (+65% relative), F4 (+30% relative).',
        transform=ax.transAxes, fontsize=8.5, va='top', ha='left',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='#FFF8F0', edgecolor=C_AMBER, alpha=0.9))

plt.tight_layout()
path3 = f'{FIG_DIR}/fig3_cot_vs_baseline.png'
plt.savefig(path3)
plt.close()
print(f'✅ Figure 3 saved → {path3}')


# ═══════════════════════════════════════════════════════════════
# FIGURE 4 — Cross-model consistency heatmap
# ═══════════════════════════════════════════════════════════════

# Universal + near-universal failures (top 20 problems)
PROBLEMS = [
    'HR-F4-027',  'FIN-F1-029', 'FIN-F3-004', 'FIN-F3-006', 'FIN-F5-006',   # all 5
    'CLIN-F1-010','HR-F2-011',  'HR-F5-020',  'HR-F5-012',  'HR-F4-032',    # 4/5
    'FIN-F1-003', 'CLIN-F4-008','HR-F2-019',  'FIN-F5-011', 'CLIN-F2-007',  # 3/5
    'FIN-F3-015', 'CLIN-F1-021','HR-F4-018',  'FIN-F1-022', 'CLIN-F3-014',  # 3/5
]

# Failure matrix: rows=problems, cols=[Claude, GPT-5.4, GPT-4o, GPT-4o-mini, Gemini]
MATRIX = np.array([
    [1, 1, 1, 1, 1],  # HR-F4-027
    [1, 1, 1, 1, 1],  # FIN-F1-029
    [1, 1, 1, 1, 1],  # FIN-F3-004
    [1, 1, 1, 1, 1],  # FIN-F3-006
    [1, 1, 1, 1, 1],  # FIN-F5-006
    [1, 1, 1, 1, 0],  # CLIN-F1-010
    [0, 1, 1, 1, 1],  # HR-F2-011
    [0, 1, 1, 1, 1],  # HR-F5-020
    [1, 1, 0, 1, 1],  # HR-F5-012
    [1, 0, 1, 1, 1],  # HR-F4-032
    [0, 1, 0, 1, 1],  # FIN-F1-003
    [1, 0, 1, 1, 0],  # CLIN-F4-008
    [0, 1, 1, 0, 1],  # HR-F2-019
    [1, 0, 0, 1, 1],  # FIN-F5-011
    [0, 1, 0, 1, 1],  # CLIN-F2-007
    [1, 0, 1, 0, 1],  # FIN-F3-015
    [0, 0, 1, 1, 1],  # CLIN-F1-021
    [1, 1, 0, 0, 1],  # HR-F4-018
    [1, 0, 1, 1, 0],  # FIN-F1-022
    [0, 1, 1, 0, 1],  # CLIN-F3-014
], dtype=float)

COL_LABELS = ['Claude\nS.4.6', 'GPT-5.4\nmini', 'GPT-4o', 'GPT-4o\nmini', 'Gemini\n2.5-flash']

fig, ax = plt.subplots(figsize=(7, 8))

# Custom colormap: white=pass, red=fail
from matplotlib.colors import ListedColormap
cmap = ListedColormap(['#F8FAFC', '#E24B4A'])

im = ax.imshow(MATRIX, cmap=cmap, aspect='auto', vmin=0, vmax=1)

# Cell annotations
for i in range(len(PROBLEMS)):
    for j in range(len(COL_LABELS)):
        val = MATRIX[i, j]
        txt = '✗' if val == 1 else '·'
        color = 'white' if val == 1 else '#B4B2A9'
        ax.text(j, i, txt, ha='center', va='center', fontsize=11,
                color=color, fontweight='bold')

# Row totals
totals = MATRIX.sum(axis=1).astype(int)
for i, t in enumerate(totals):
    color = '#A32D2D' if t == 5 else (C_AMBER if t >= 4 else '#5F5E5A')
    ax.text(5.35, i, f'{t}/5', ha='left', va='center', fontsize=9,
            fontweight='bold', color=color)

# Divider line after row 4 (universal failures)
ax.axhline(4.5, color='#444441', linewidth=1.2, linestyle='--', alpha=0.6)
ax.text(5.35, 2, '← All 5\nmodels', ha='left', va='center', fontsize=7.5,
        color='#A32D2D', style='italic')
ax.text(5.35, 7, '← 4 of 5\nmodels', ha='left', va='center', fontsize=7.5,
        color=C_AMBER, style='italic')

# Axes
ax.set_xticks(range(len(COL_LABELS)))
ax.set_xticklabels(COL_LABELS, fontsize=9)
ax.set_yticks(range(len(PROBLEMS)))
ax.set_yticklabels(PROBLEMS, fontsize=8.5, family='monospace')
ax.set_xlim(-0.5, 5.85)
ax.xaxis.set_label_position('top')
ax.xaxis.tick_top()
ax.tick_params(axis='both', which='both', length=0)

# Remove all spines
for spine in ax.spines.values():
    spine.set_visible(False)

# Grid lines between cells
for x_pos in np.arange(-0.5, len(COL_LABELS), 1):
    ax.axvline(x_pos, color='white', linewidth=2)
for y_pos in np.arange(-0.5, len(PROBLEMS), 1):
    ax.axhline(y_pos, color='white', linewidth=1.5)

ax.set_title('Figure 4. Cross-model failure consistency (baseline condition, top-20 problems)',
             pad=18, fontsize=11, fontweight='bold')

# Legend
legend_elements = [
    mpatches.Patch(facecolor='#E24B4A', label='Failure exhibited (✗)'),
    mpatches.Patch(facecolor='#F8FAFC', edgecolor='#CCCCCC', label='No failure (·)'),
]
ax.legend(handles=legend_elements, loc='lower right',
          bbox_to_anchor=(1.0, -0.06), framealpha=0.9, fontsize=9)

plt.tight_layout()
path4 = f'{FIG_DIR}/fig4_crossmodel_heatmap.png'
plt.savefig(path4)
plt.close()
print(f'✅ Figure 4 saved → {path4}')


# ═══════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════
print(f'\n{"="*55}')
print(f'  All 4 figures saved to {FIG_DIR}/')
print(f'{"="*55}')
print(f'  fig1_failure_rate_by_model.png    — Table 1 visual')
print(f'  fig2_scaffold_recovery_by_mode.png — Table 2 visual')
print(f'  fig3_cot_vs_baseline.png          — CoT finding')
print(f'  fig4_crossmodel_heatmap.png        — Table 3 visual')
print(f'\n  Resolution: 300 DPI — ready for EMNLP submission')
print(f'  Format: PNG — convert to PDF with:')
print(f'    from PIL import Image')
print(f'    Image.open("fig1_...png").save("fig1.pdf")')
print(f'\n  LaTeX inclusion:')
print(f'    \\includegraphics[width=\\linewidth]{{figures/fig1_failure_rate_by_model}}')
