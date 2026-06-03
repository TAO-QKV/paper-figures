"""README showcase: an asymmetric journal-style composite figure.

Run: python examples/showcase_gallery.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, FancyArrowPatch
import paperfig as pf

pf.paper_style(font="sans")
rng = np.random.default_rng(23)
HERE = Path(__file__).resolve().parent

fig = plt.figure(figsize=(13.6, 8.4))
gs = fig.add_gridspec(
    2, 4, width_ratios=[1.35, 1.35, 1.05, 1.05], height_ratios=[1, 1],
    left=0.055, right=0.975, top=0.92, bottom=0.08, wspace=0.36, hspace=0.42
)

ax_hero = fig.add_subplot(gs[:, :2])
ax_volcano = fig.add_subplot(gs[0, 2])
ax_image = fig.add_subplot(gs[0, 3])
ax_surv = fig.add_subplot(gs[1, 2])
ax_graph = fig.add_subplot(gs[1, 3])

fig.suptitle("Multi-modal response signature: discovery, mechanism, validation",
             x=0.055, y=0.972, ha="left", fontsize=13, fontweight="bold")

# (a) Hero panel: latent patient manifold, with decision transition and insets.
n = 120
ctrl = rng.multivariate_normal([-1.4, -0.25], [[0.28, 0.05], [0.05, 0.22]], n)
resp = rng.multivariate_normal([1.15, 0.38], [[0.34, -0.03], [-0.03, 0.25]], n)
mixed = rng.multivariate_normal([0.0, 1.2], [[0.24, 0.02], [0.02, 0.18]], 70)
xy = np.vstack([ctrl, resp, mixed])
labs = np.repeat(["non-responder", "responder", "borderline"], [n, n, 70])
colors = [pf.PALETTE[0], pf.PALETTE[1], pf.PALETTE[2]]
for i, lab in enumerate(["non-responder", "responder", "borderline"]):
    pts = xy[labs == lab]
    ax_hero.scatter(pts[:, 0], pts[:, 1], s=18, color=colors[i], alpha=0.58,
                    edgecolor="white", linewidth=0.25, label=lab, zorder=3)
    cen = pts.mean(axis=0)
    cov = np.cov(pts.T)
    vals, vecs = np.linalg.eigh(cov)
    ang = np.degrees(np.arctan2(vecs[1, -1], vecs[0, -1]))
    ax_hero.add_patch(Ellipse(cen, 3.2 * np.sqrt(vals[-1]), 3.2 * np.sqrt(vals[0]),
                              angle=ang, facecolor=colors[i], alpha=0.10,
                              edgecolor=colors[i], lw=1.0, zorder=1))
xx = np.linspace(-2.6, 2.6, 200)
ax_hero.plot(xx, 0.45 * xx + 0.25, color="#333", ls="--", lw=1.0,
             label="decision boundary", zorder=2)
ax_hero.add_patch(FancyArrowPatch((-1.55, -1.2), (1.2, 1.25), arrowstyle="-|>",
                                  mutation_scale=14, lw=1.2, color="#555",
                                  alpha=0.9))
ax_hero.text(-1.62, -1.36, "low-response\nstate", fontsize=8, ha="right")
ax_hero.text(1.26, 1.34, "treatment-sensitive\nstate", fontsize=8, ha="left")
ax_hero.set_xlabel("Latent axis 1"); ax_hero.set_ylabel("Latent axis 2")
ax_hero.set_title("Patient manifold with learned response boundary", loc="left")
ax_hero.legend(loc="upper left", ncol=1, fontsize=8, frameon=True)

y_true = (rng.random(260) > 0.55).astype(int)
y_score = np.clip(0.62 * y_true + rng.beta(2, 4, 260), 0, 1)
ax_pr = ax_hero.inset_axes([0.58, 0.08, 0.36, 0.28])
pf.pr_curve(y_true, y_score, ax=ax_pr)
ax_pr.set_title("PR", fontsize=8); ax_pr.tick_params(labelsize=7)
ax_pr.set_xlabel("R", fontsize=7); ax_pr.set_ylabel("P", fontsize=7)
ax_cal = ax_hero.inset_axes([0.58, 0.43, 0.36, 0.24])
pf.calibration(y_true, y_score, n_bins=8, ax=ax_cal)
ax_cal.set_title("calibration", fontsize=8); ax_cal.tick_params(labelsize=7)
ax_cal.set_xlabel("pred.", fontsize=7); ax_cal.set_ylabel("obs.", fontsize=7)

# (b) Omics evidence: volcano with annotated genes.
lfc = rng.normal(0, 1.35, 900)
p = 10 ** (-(np.abs(lfc) * rng.random(900) * 3.4))
genes = np.array([f"G{i}" for i in range(900)])
pf.volcano(lfc, p, labels=genes, top=5, ax=ax_volcano)
ax_volcano.set_title("Differential pathway activity", loc="left")
ax_volcano.text(0.03, 0.05, "FDR + effect-size gate", transform=ax_volcano.transAxes,
                va="bottom", fontsize=8)

# (c) Imaging evidence: two modality panels plus quantitative spectrum inset.
yy, xxg = np.mgrid[-1:1:120j, -1:1:120j]
lesion = np.exp(-((xxg + 0.18) ** 2 + (yy - 0.08) ** 2) * 13)
texture = np.sin(18 * xxg) * np.cos(14 * yy) + 0.2 * rng.random((120, 120))
ax_image.imshow(np.c_[lesion, np.ones((120, 8)) * np.nan, texture], cmap="magma")
ax_image.set_axis_off()
ax_image.set_title("Imaging phenotype + spectral readout", loc="left")
ax_image.text(25, 12, "confocal", color="white", fontsize=8, ha="center")
ax_image.text(188, 12, "texture map", color="white", fontsize=8, ha="center")
ax_image.plot([18, 50], [104, 104], color="white", lw=2.5, solid_capstyle="butt")
ax_image.text(34, 99, "50 um", color="white", ha="center", fontsize=8)
ax_sp = ax_image.inset_axes([0.50, 0.06, 0.46, 0.34])
x = np.linspace(100, 900, 500)
y = (1.2 * np.exp(-((x - 226) / 25) ** 2) + 0.7 * np.exp(-((x - 515) / 43) ** 2)
     + 0.45 * np.exp(-((x - 705) / 32) ** 2) + 0.025 * rng.random(x.size))
pf.spectrum(x, y, top=3, xlabel="", ylabel="", ax=ax_sp)
ax_sp.tick_params(labelsize=7); ax_sp.set_title("spectrum", fontsize=8)

# (d) Clinical validation: survival plus forest inset.
pf.survival({
    "signature low": (rng.weibull(1.15, 120) * 14, (rng.random(120) > 0.22).astype(int)),
    "signature high": (rng.weibull(1.55, 120) * 24, (rng.random(120) > 0.25).astype(int)),
}, xlabel="Follow-up time (months)", ax=ax_surv)
ax_surv.set_title("Prospective validation", loc="left")
ax_forest = ax_surv.inset_axes([0.48, 0.16, 0.46, 0.38])
est = np.array([-0.35, -0.18, -0.44, -0.29])
lo = est - np.array([0.16, 0.20, 0.18, 0.10])
hi = est + np.array([0.14, 0.22, 0.16, 0.09])
pf.forest(["site 1", "site 2", "site 3", "pooled"], est, lo, hi,
          xlabel="log HR", ax=ax_forest)
ax_forest.tick_params(labelsize=7); ax_forest.set_xlabel("log HR", fontsize=7)

# (e) Mechanism graph: multi-omics evidence into the response state.
edges = [
    ("DNA", "KIN", 2.4), ("DNA", "IMM", 1.4),
    ("MET", "IMM", 1.8), ("IMG", "STR", 1.6),
    ("KIN", "RES", 2.8), ("IMM", "RES", 2.5),
    ("STR", "RES", 1.7), ("TX", "RES", 2.2),
]
pos = {
    "DNA": np.array([-1.0, 0.8]), "MET": np.array([-1.0, 0.05]),
    "IMG": np.array([-1.0, -0.7]), "TX": np.array([-0.1, -1.0]),
    "KIN": np.array([0.15, 0.72]), "IMM": np.array([0.2, 0.05]),
    "STR": np.array([0.18, -0.62]), "RES": np.array([1.15, 0.02]),
}
pf.network_graph(edges, nodes=list(pos), pos=pos, directed=True, labels=False, ax=ax_graph)
ax_graph.set_title("Mechanistic evidence graph", loc="left")
ax_graph.set_xlim(-1.32, 1.48); ax_graph.set_ylim(-1.18, 1.08)
for name, p in pos.items():
    ax_graph.text(p[0], p[1] + 0.14, name, ha="center", va="bottom", fontsize=8,
                  bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.75))
ax_graph.text(0.04, 0.05, "edge width = evidence strength",
              transform=ax_graph.transAxes, fontsize=8, color="#555")

for a, tag in zip([ax_hero, ax_volcano, ax_image, ax_surv, ax_graph], "abcde"):
    a.text(-0.055, 1.035, f"({tag})", transform=a.transAxes, fontweight="bold",
           va="top", ha="right", fontsize=10)

pf.save(fig, "gallery_showcase", outdir=str(HERE))
plt.close(fig)
print("[gallery] wrote examples/gallery_showcase.png")
