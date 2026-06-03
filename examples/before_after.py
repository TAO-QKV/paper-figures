"""Same data, matplotlib defaults vs paperfig (examples/gallery_before_after.png).

The value proof: identical plotting calls, only the style differs.
Run: python examples/before_after.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import paperfig as pf

HERE = Path(__file__).resolve().parent
rng = np.random.default_rng(5)

# one dataset, plotted identically in both panels
x = np.linspace(0, 12, 200)
series = {
    "model A": np.sin(x) * np.exp(-0.05 * x),
    "model B": np.cos(x) * np.exp(-0.05 * x),
    "model C": 0.5 * np.sin(1.5 * x) * np.exp(-0.04 * x),
}
pts_x = np.linspace(0, 12, 24)
pts_y = np.sin(pts_x) * np.exp(-0.05 * pts_x) + rng.normal(0, 0.05, pts_x.size)


def draw(ax, palette=None, markers=None):
    for i, (name, y) in enumerate(series.items()):
        c = palette[i] if palette else None
        ax.plot(x, y, label=name, color=c)
    ax.scatter(pts_x, pts_y, s=18, color=(palette[0] if palette else None),
               marker=(markers[0] if markers else "o"), zorder=5,
               alpha=0.7, label="observed")
    ax.set_xlabel("time (s)"); ax.set_ylabel("amplitude"); ax.legend()


# --- BEFORE: matplotlib defaults ---
with plt.style.context("default"):
    figb, axb = plt.subplots(figsize=(5, 3.2))
    draw(axb); axb.set_title("matplotlib defaults")
    figb.tight_layout(); figb.savefig(HERE / "_before.png", dpi=200)
    plt.close(figb)

# --- AFTER: paperfig ---
PAL, MRK, _ = pf.paper_style(font="sans")
figa, axa = plt.subplots(figsize=(5, 3.2))
draw(axa, palette=PAL, markers=MRK); axa.set_title("paperfig")
figa.tight_layout(); figa.savefig(HERE / "_after.png", dpi=200)
plt.close(figa)

# --- combine side by side ---
fig, (l, r) = plt.subplots(1, 2, figsize=(11, 3.5))
for ax, img in ((l, "_before.png"), (r, "_after.png")):
    ax.imshow(mpimg.imread(HERE / img)); ax.set_axis_off()
fig.subplots_adjust(wspace=0.03, left=0.01, right=0.99, top=0.99, bottom=0.01)
fig.savefig(HERE / "gallery_before_after.png", dpi=150, bbox_inches="tight")
plt.close(fig)
for tmp in ("_before.png", "_after.png"):
    (HERE / tmp).unlink(missing_ok=True)
print("[gallery] wrote examples/gallery_before_after.png")
