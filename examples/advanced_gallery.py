"""High-impact scientific chart types (examples/gallery_advanced.png).

Run: python examples/advanced_gallery.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import matplotlib.pyplot as plt
import paperfig as pf

pf.paper_style(font="sans")
rng = np.random.default_rng(11)
HERE = Path(__file__).resolve().parent

fig = plt.figure(figsize=(10.8, 7.6))
gs = fig.add_gridspec(2, 2, wspace=0.35, hspace=0.42,
                      left=0.06, right=0.96, top=0.93, bottom=0.08)
ax_m = fig.add_subplot(gs[0, 0])
ax_s = fig.add_subplot(gs[0, 1])
ax_3 = fig.add_subplot(gs[1, 0], projection="3d")
ax_k = fig.add_subplot(gs[1, 1])

# Genomics: Manhattan plot with a few engineered peaks.
chrom = np.repeat(np.arange(1, 13), 70)
pos = np.tile(np.linspace(0, 1_000_000, 70), 12)
pvals = 10 ** (-rng.gamma(1.1, 1.1, chrom.size))
peak = rng.choice(chrom.size, 8, replace=False)
pvals[peak] = 10 ** (-rng.uniform(7.0, 11.5, peak.size))
labels = np.array([f"rs{i:05d}" for i in range(chrom.size)])
pf.manhattan(chrom, pos, pvals, labels=labels, top=4, ax=ax_m)
ax_m.set_title("Manhattan")

# Physics: streamlines in a vortex-like vector field.
x = np.linspace(-3, 3, 42)
y = np.linspace(-3, 3, 42)
X, Y = np.meshgrid(x, y)
R = X ** 2 + Y ** 2 + 0.4
U = -Y / R + 0.12
V = X / R
pf.streamplot_field(X, Y, U, V, cbar_label="velocity", ax=ax_s)
ax_s.set_title("Streamplot")

# Scalar field: 3-D response surface.
Z = np.sin(X) * np.cos(Y) * np.exp(-(X ** 2 + Y ** 2) / 18)
pf.surface3d(X, Y, Z, cbar_label="response", ax=ax_3)
ax_3.set_title("3-D surface")

# Mechanism / flow: single-node Sankey.
pf.sankey([12, -6.5, -4.1, -1.4],
          ["input", "path A", "path B", "loss"],
          orientations=[0, 1, -1, 0], unit=" a.u.", gap=0.55,
          pathlengths=[0.5, 0.85, 0.85, 0.65], ax=ax_k)
ax_k.set_title("Sankey flow")

for ax, tag in zip([ax_m, ax_s, ax_3, ax_k], "abcd"):
    if getattr(ax, "name", "") == "3d":
        ax.text2D(-0.04, 1.08, f"({tag})", transform=ax.transAxes,
                  fontweight="bold", va="top", ha="right", fontsize=9)
    else:
        ax.text(-0.04, 1.08, f"({tag})", transform=ax.transAxes,
                fontweight="bold", va="top", ha="right", fontsize=9)

pf.save(fig, "gallery_advanced", outdir=str(HERE))
plt.close(fig)
print("[gallery] wrote examples/gallery_advanced.png")
