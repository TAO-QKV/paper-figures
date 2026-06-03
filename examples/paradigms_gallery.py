"""Render the §I composition paradigms P3-P6 (examples/gallery_paradigms.png).

These are the differentiator: hero/method-figure compositions that embed the
real method object, not boxes-and-arrows. Run: python examples/paradigms_gallery.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import matplotlib.pyplot as plt
import paperfig as pf
from paperfig.style import PALETTE

pf.paper_style(font="sans")
rng = np.random.default_rng(11)
HERE = Path(__file__).resolve().parent

fig = plt.figure(figsize=(12.5, 9.0))
gs = fig.add_gridspec(2, 2, hspace=0.40, wspace=0.24, left=0.06, right=0.97,
                      top=0.88, bottom=0.06)
TY1, TY2 = 0.955, 0.47   # section-header y positions (clear of subplot titles)

# ---- P3: before/after transform diptych ----------------------------------
sub = gs[0, 0].subgridspec(1, 2, wspace=0.08)
axb = fig.add_subplot(sub[0]); axa = fig.add_subplot(sub[1])
ang = rng.uniform(0, 2 * np.pi, 120)
blob = np.c_[np.cos(ang), np.sin(ang)] * rng.uniform(0.2, 1, (120, 1))
axb.scatter(blob[:, 0], blob[:, 1], s=10, color=PALETTE[0], alpha=0.5)
# "after": a transform unfolds the ring into two separable clusters
lbl = (ang < np.pi)
sep = np.c_[np.where(lbl, -1, 1) + rng.normal(0, 0.25, 120), rng.normal(0, 0.5, 120)]
axa.scatter(sep[lbl, 0], sep[lbl, 1], s=10, color=PALETTE[0], alpha=0.6)
axa.scatter(sep[~lbl, 0], sep[~lbl, 1], s=10, color=PALETTE[2], alpha=0.6)
for a in (axb, axa):
    a.set_xticks([]); a.set_yticks([]); a.grid(False)
axb.set_title("before", fontsize=9); axa.set_title("after", fontsize=9)
axb.annotate("", xy=(1.18, 0.5), xytext=(0.95, 0.5), xycoords="axes fraction",
             arrowprops=dict(arrowstyle="-|>", lw=1.6, color=PALETTE[1]))
axb.text(1.07, 0.62, "transform\n$-42\\%$ overlap", transform=axb.transAxes,
         ha="center", fontsize=7.5, color=PALETTE[1])
fig.text(0.06, TY1, "P3  before/after diptych", fontweight="bold", fontsize=10)

# ---- P4: distribution-flow axis ------------------------------------------
axd = fig.add_subplot(gs[0, 1])
times = np.arange(1, 7)
for i, tm in enumerate(times):
    vals = rng.normal(0.15 * tm, 0.18 + 0.03 * tm, 250)  # widening drift
    vp = axd.violinplot(vals, positions=[tm], widths=0.7, showextrema=False)
    for b in vp["bodies"]:
        b.set_facecolor(PALETTE[0]); b.set_alpha(0.35)
mean = 0.15 * times
axd.plot(times, mean, "-o", color=PALETTE[1], ms=4, lw=1.8, label="mean")
axd.axhline(1.05, color="#3a3a3a", lw=0.9, ls="--")
axd.text(6.2, 1.05, "threshold", fontsize=7.5, va="center", color="#3a3a3a")
axd.set_xlabel("Time $t$"); axd.set_ylabel("Degradation $X$"); axd.legend(loc="upper left")
fig.text(0.55, TY1, "P4  distribution-flow", fontweight="bold", fontsize=10)

# ---- P5: source-target alignment motif -----------------------------------
sub2 = gs[1, 0].subgridspec(1, 2, wspace=0.08)
ax5b = fig.add_subplot(sub2[0]); ax5a = fig.add_subplot(sub2[1])
src = rng.normal([0, 0], 0.5, (80, 2))
tgt = rng.normal([1.6, 1.1], 0.5, (80, 2))
tgt_al = rng.normal([0.1, 0.05], 0.5, (80, 2))
for ax, tg, ttl in [(ax5b, tgt, "before  (MMD 0.41)"), (ax5a, tgt_al, "after  (MMD 0.06)")]:
    ax.scatter(src[:, 0], src[:, 1], s=11, color=PALETTE[0], alpha=0.5, label="source")
    ax.scatter(tg[:, 0], tg[:, 1], s=11, color=PALETTE[1], alpha=0.5, label="target")
    ax.set_xticks([]); ax.set_yticks([]); ax.grid(False); ax.set_title(ttl, fontsize=9)
ax5b.legend(loc="upper left", fontsize=7)
fig.text(0.06, TY2, "P5  source-target alignment", fontweight="bold", fontsize=10)

# ---- P6: decision-region map ---------------------------------------------
ax6 = fig.add_subplot(gs[1, 1])
xx, yy = np.meshgrid(np.linspace(0, 10, 200), np.linspace(0, 10, 200))
score = 0.6 * xx + 0.4 * yy
ax6.contourf(xx, yy, score, levels=[0, 4, 7, 20],
             colors=["#2ca02c", "#ff7f0e", "#d62728"], alpha=0.16)
ax6.contour(xx, yy, score, levels=[4, 7], colors="#3a3a3a", linewidths=0.8, linestyles="--")
pts = rng.uniform(0, 10, (40, 2))
ax6.scatter(pts[:, 0], pts[:, 1], s=14, color="#222", zorder=3)
ax6.text(1.2, 8.4, "negative", fontsize=8, color="#1a6b1a")
ax6.text(4.0, 6.0, "borderline", fontsize=8, color="#a85b00")
ax6.text(7.0, 3.0, "positive", fontsize=8, color="#a01515")
ax6.set_xlabel("Feature 1"); ax6.set_ylabel("Feature 2"); ax6.grid(False)
fig.text(0.55, TY2, "P6  decision-region map", fontweight="bold", fontsize=10)

pf.save(fig, "gallery_paradigms", outdir=str(HERE))
plt.close(fig)
print("[gallery] wrote examples/gallery_paradigms.png")
