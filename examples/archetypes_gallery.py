"""Render the archetype functions into one contact sheet (examples/gallery_archetypes.png).

Run: python examples/archetypes_gallery.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import matplotlib.pyplot as plt
import paperfig as pf

pf.paper_style(font="sans")
rng = np.random.default_rng(3)
HERE = Path(__file__).resolve().parent

fig, axes = plt.subplots(2, 4, figsize=(13.5, 6.2))
fig.subplots_adjust(wspace=0.42, hspace=0.5, left=0.05, right=0.985, top=0.93, bottom=0.09)

# A1 time series + CI
t = np.linspace(0, 12, 60); base = 1 - np.exp(-0.3 * t)
pf.timeseries_ci(t, base + rng.normal(0, 0.05, 60), base, base - 0.06, base + 0.06,
                 ylabel="Signal", ax=axes[0, 0]); axes[0, 0].set_title("A1 time series + CI")

# A2 sorted bar
pf.sorted_bar([f"item {c}" for c in "ABCDE"], rng.uniform(0.1, 0.9, 5),
              xlabel="Share", ax=axes[0, 1]); axes[0, 1].set_title("A2 sorted bar")

# A3 grouped bar
pf.grouped_bar(["M1", "M2", "M3"], {"RMSE": [0.34, 0.27, 0.41], "MAE": [0.22, 0.19, 0.3]},
               ylabel="Error", ax=axes[0, 2]); axes[0, 2].set_title("A3 grouped bar")

# A6 scatter + fit
xx = np.sort(rng.uniform(0, 10, 40))
pf.scatter_fit(xx, 0.6 * xx + rng.normal(0, 1.1, 40), ax=axes[0, 3])
axes[0, 3].set_title("A6 scatter + fit")

# A5 heatmap (correlation)
C = rng.normal(0, 1, (50, 5)); R = np.corrcoef(C.T)
pf.heatmap(R, row_labels=list("vwxyz"), col_labels=list("vwxyz"),
           cbar_label="corr", ax=axes[1, 0]); axes[1, 0].set_title("A5 heatmap")

# A7 Pareto
o1 = rng.random(60); o2 = rng.random(60)
isp = np.array([not np.any((o1 < a) & (o2 < b)) for a, b in zip(o1, o2)])
pf.pareto(o1, o2, isp, xlabel="Cost", ylabel="Risk", ax=axes[1, 1])
axes[1, 1].set_title("A7 Pareto frontier")

# A8 tornado
p = [f"$p_{i}$" for i in range(1, 5)]
pf.tornado(p, [1.6, 1.2, 1.8, 0.9], [2.6, 3.1, 2.3, 3.6], 2.1, ax=axes[1, 2])
axes[1, 2].set_title("A8 tornado")

# A9 confusion
pf.confusion(np.array([[42, 5], [7, 38]]), labels=["neg", "pos"], ax=axes[1, 3])
axes[1, 3].set_title("A9 confusion")

for ax, tag in zip(axes.flat, "abcdefgh"):
    ax.text(-0.02, 1.14, f"({tag})", transform=ax.transAxes, fontweight="bold",
            va="top", ha="right", fontsize=10)

pf.save(fig, "gallery_archetypes", outdir=str(HERE))
plt.close(fig)
print("[gallery] wrote examples/gallery_archetypes.png")
