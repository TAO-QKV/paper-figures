"""Extended scientific chart types across fields (examples/gallery_scientific.png).

Run: python examples/scientific_gallery.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import matplotlib.pyplot as plt
import paperfig as pf

pf.paper_style(font="sans")
rng = np.random.default_rng(7)
HERE = Path(__file__).resolve().parent

fig, ax = plt.subplots(3, 4, figsize=(14, 9))
fig.subplots_adjust(wspace=0.5, hspace=0.62, left=0.05, right=0.96, top=0.94, bottom=0.06)

# ML
yt = (rng.random(300) > 0.5).astype(int)
ys = np.clip(yt * 0.45 + rng.random(300) * 0.55, 0, 1)
pf.roc_curve(yt, ys, ax=ax[0, 0]); ax[0, 0].set_title("ROC + AUC")
pf.calibration(yt, ys, ax=ax[0, 1]); ax[0, 1].set_title("calibration")

# stats
g = {"ctrl": rng.normal(0, 1, 120), "treat": rng.normal(0.8, 1.1, 120)}
pf.ecdf(g, ax=ax[0, 2]); ax[0, 2].set_title("ECDF")
pf.box(g, ax=ax[0, 3]); ax[0, 3].set_title("box + jitter")
pf.bar_err(g, brackets=[(0, 1, "**")], ax=ax[1, 0]); ax[1, 0].set_title("bar + error + sig")
pf.qq(rng.normal(0, 1, 200), ax=ax[1, 1]); ax[1, 1].set_title("Q-Q")

# omics
lfc = rng.normal(0, 1.6, 600); pv = 10 ** (-(np.abs(lfc) * rng.random(600) * 3))
pf.volcano(lfc, pv, ax=ax[1, 2]); ax[1, 2].set_title("volcano")

# medical
pf.survival({"A": (rng.exponential(6, 90), (rng.random(90) > 0.3).astype(int)),
             "B": (rng.exponential(10, 90), (rng.random(90) > 0.3).astype(int))},
            ax=ax[1, 3]); ax[1, 3].set_title("Kaplan-Meier")
pf.forest(["study 1", "study 2", "study 3", "pooled"],
          [0.3, -0.1, 0.5, 0.25], [0.05, -0.4, 0.2, 0.1], [0.55, 0.2, 0.8, 0.4],
          ax=ax[2, 0]); ax[2, 0].set_title("forest")
mm = rng.normal(10, 2, 80)
pf.bland_altman(mm, mm + rng.normal(0.3, 1, 80), ax=ax[2, 1]); ax[2, 1].set_title("Bland-Altman")

# physics / big data
X, Y = np.meshgrid(np.linspace(-3, 3, 60), np.linspace(-3, 3, 60))
Z = np.exp(-(X ** 2 + Y ** 2) / 3) * np.cos(2 * X)
pf.contour_field(X, Y, Z, ax=ax[2, 2]); ax[2, 2].set_title("contour field")
pf.hexbin_density(rng.normal(0, 1, 4000), rng.normal(0, 1, 4000), ax=ax[2, 3])
ax[2, 3].set_title("hexbin density")

for a, tag in zip(ax.flat, "abcdefghijkl"):
    a.text(-0.02, 1.16, f"({tag})", transform=a.transAxes, fontweight="bold",
           va="top", ha="right", fontsize=9)

pf.save(fig, "gallery_scientific", outdir=str(HERE))
plt.close(fig)
print("[gallery] wrote examples/gallery_scientific.png")
