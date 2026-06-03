"""Modern distribution archetypes (examples/gallery_modern.png).

raincloud / violin / ridgeline — the distribution figures current bio/ML/physics
papers use. Run: python examples/modern_gallery.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import matplotlib.pyplot as plt
import paperfig as pf

pf.paper_style(font="sans")
rng = np.random.default_rng(8)
HERE = Path(__file__).resolve().parent

# three conditions with shifting + changing-shape distributions
groups = {
    "control": rng.normal(0.0, 1.0, 220),
    "low dose": np.concatenate([rng.normal(0.4, 0.7, 150), rng.normal(2.0, 0.5, 70)]),
    "high dose": rng.normal(1.8, 1.2, 220),
}

fig, axes = plt.subplots(1, 3, figsize=(13, 3.8))
fig.subplots_adjust(wspace=0.32, left=0.05, right=0.99, top=0.86, bottom=0.13)

pf.raincloud(groups, ylabel="Response (a.u.)", ax=axes[0]); axes[0].set_title("raincloud")
pf.violin(groups, ylabel="Response (a.u.)", ax=axes[1]); axes[1].set_title("violin")
pf.ridgeline(groups, xlabel="Response (a.u.)", ax=axes[2]); axes[2].set_title("ridgeline")

for ax, tag in zip(axes, "abc"):
    ax.text(-0.02, 1.13, f"({tag})", transform=ax.transAxes, fontweight="bold",
            va="top", ha="right", fontsize=10)

pf.save(fig, "gallery_modern", outdir=str(HERE))
plt.close(fig)
print("[gallery] wrote examples/gallery_modern.png")
