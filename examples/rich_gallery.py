"""Richer multi-axes figures (examples/gallery_rich.png): jointplot, radar, slopegraph.

Run: python examples/rich_gallery.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import paperfig as pf

pf.paper_style(font="sans")
rng = np.random.default_rng(4)
HERE = Path(__file__).resolve().parent

# jointplot: correlated scatter + marginals
x = rng.normal(0, 1, 600); y = 0.7 * x + rng.normal(0, 0.7, 600)
figj, _ = pf.jointplot(x, y, xlabel="$x$", ylabel="$y$")
figj.savefig(HERE / "_r_joint.png", dpi=200); plt.close(figj)

# radar: two models over five metrics
figr, _ = pf.radar({"model A": [0.82, 0.61, 0.9, 0.74, 0.55],
                    "model B": [0.7, 0.78, 0.66, 0.8, 0.72]},
                   ["accuracy", "precision", "recall", "F1", "AUC"])
figr.savefig(HERE / "_r_radar.png", dpi=200); plt.close(figr)

# slopegraph: paired before/after
figs, _ = pf.slopegraph([3.1, 2.4, 4.0, 1.8], [4.2, 2.1, 4.6, 3.0],
                        ["alpha", "beta", "gamma", "delta"])
figs.savefig(HERE / "_r_slope.png", dpi=200); plt.close(figs)

titles = ["jointplot (scatter + marginals)", "radar", "slopegraph"]
files = ["_r_joint.png", "_r_radar.png", "_r_slope.png"]
fig, axes = plt.subplots(1, 3, figsize=(12, 4))
for ax, f, t in zip(axes, files, titles):
    ax.imshow(mpimg.imread(HERE / f)); ax.set_axis_off(); ax.set_title(t, fontsize=10)
fig.subplots_adjust(wspace=0.04, left=0.01, right=0.99, top=0.92, bottom=0.01)
fig.savefig(HERE / "gallery_rich.png", dpi=150, bbox_inches="tight")
plt.close(fig)
for f in files:
    (HERE / f).unlink(missing_ok=True)
print("[gallery] wrote examples/gallery_rich.png")
