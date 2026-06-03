"""README showcase: six high-information publication figure families.

Run: python examples/showcase_gallery.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import matplotlib.pyplot as plt
import paperfig as pf

pf.paper_style(font="sans")
rng = np.random.default_rng(23)
HERE = Path(__file__).resolve().parent

fig = plt.figure(figsize=(13.2, 8.1))
gs = fig.add_gridspec(2, 3, wspace=0.38, hspace=0.55,
                      left=0.055, right=0.97, top=0.91, bottom=0.08)
axes = [
    fig.add_subplot(gs[0, 0]),
    fig.add_subplot(gs[0, 1]),
    fig.add_subplot(gs[0, 2]),
    fig.add_subplot(gs[1, 0]),
    fig.add_subplot(gs[1, 1]),
    fig.add_subplot(gs[1, 2], projection="3d"),
]

# Genomics: Manhattan plot with controlled signal peaks.
chrom = np.repeat(np.arange(1, 11), 65)
pos = np.tile(np.linspace(0, 1_200_000, 65), 10)
pvals = 10 ** (-rng.gamma(1.0, 1.05, chrom.size))
peak = rng.choice(chrom.size, 7, replace=False)
pvals[peak] = 10 ** (-rng.uniform(7.2, 10.8, peak.size))
labels = np.array([f"rs{i:05d}" for i in range(chrom.size)])
pf.manhattan(chrom, pos, pvals, labels=labels, top=3, ax=axes[0])
axes[0].set_title("GWAS Manhattan")

# Omics: volcano plot with thresholded up/down regulation.
lfc = rng.normal(0, 1.45, 800)
p = 10 ** (-(np.abs(lfc) * rng.random(800) * 3.2))
genes = np.array([f"gene{i}" for i in range(800)])
pf.volcano(lfc, p, labels=genes, top=4, ax=axes[1])
axes[1].set_title("Differential expression")

# Clinical: Kaplan-Meier survival curves.
pf.survival({
    "standard": (rng.weibull(1.2, 100) * 15, (rng.random(100) > 0.25).astype(int)),
    "treated": (rng.weibull(1.6, 100) * 22, (rng.random(100) > 0.28).astype(int)),
}, xlabel="Follow-up time (months)", ax=axes[2])
axes[2].set_title("Kaplan-Meier")

# Evidence synthesis: forest plot.
labels_f = ["trial A", "trial B", "trial C", "trial D", "pooled"]
est = np.array([-0.18, -0.34, -0.05, -0.42, -0.27])
lo = est - np.array([0.18, 0.22, 0.20, 0.16, 0.09])
hi = est + np.array([0.16, 0.20, 0.24, 0.18, 0.08])
pf.forest(labels_f, est, lo, hi, xlabel="Treatment effect (log HR)", ax=axes[3])
axes[3].set_title("Forest meta-analysis")

# Physics: streamlines in a vector field.
x = np.linspace(-3, 3, 44)
y = np.linspace(-3, 3, 44)
X, Y = np.meshgrid(x, y)
R = X ** 2 + Y ** 2 + 0.55
U = -Y / R + 0.10 * np.cos(Y)
V = X / R + 0.06 * np.sin(X)
pf.streamplot_field(X, Y, U, V, cbar_label="speed", ax=axes[4])
axes[4].set_title("Vector-field streamlines")

# Physics / optimization: 3-D response surface.
Z = np.sin(X) * np.cos(Y) * np.exp(-(X ** 2 + Y ** 2) / 17)
pf.surface3d(X, Y, Z, cbar_label="response", ax=axes[5])
axes[5].set_title("3-D response surface")

for ax, tag in zip(axes, "abcdef"):
    if getattr(ax, "name", "") == "3d":
        ax.text2D(-0.05, 1.1, f"({tag})", transform=ax.transAxes,
                  fontweight="bold", va="top", ha="right", fontsize=9)
    else:
        ax.text(-0.05, 1.1, f"({tag})", transform=ax.transAxes,
                fontweight="bold", va="top", ha="right", fontsize=9)

pf.save(fig, "gallery_showcase", outdir=str(HERE))
plt.close(fig)
print("[gallery] wrote examples/gallery_showcase.png")
