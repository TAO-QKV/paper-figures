"""Coverage atlas: complex composite figures for common paper scenarios.

Run: python examples/coverage_gallery.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import paperfig as pf

pf.paper_style(font="sans")
rng = np.random.default_rng(31)
HERE = Path(__file__).resolve().parent

fig = plt.figure(figsize=(13.6, 9.0))
outer = fig.add_gridspec(2, 2, left=0.055, right=0.975, top=0.93, bottom=0.07,
                         wspace=0.24, hspace=0.34)
fig.suptitle("Best-fit scientific figure families: composite panels for real papers",
             x=0.055, y=0.985, ha="left", fontsize=13, fontweight="bold")

# A. ML validation composite: embedding hero + PR + convergence.
gs_a = outer[0, 0].subgridspec(2, 2, width_ratios=[1.35, 1], height_ratios=[1, 1],
                               wspace=0.32, hspace=0.42)
ax_emb = fig.add_subplot(gs_a[:, 0])
ax_pr = fig.add_subplot(gs_a[0, 1])
ax_conv = fig.add_subplot(gs_a[1, 1])
xy = np.vstack([
    rng.normal([-1.0, 0.0], 0.42, (95, 2)),
    rng.normal([1.35, 0.35], 0.45, (95, 2)),
    rng.normal([0.2, 1.75], 0.38, (70, 2)),
])
labs = np.repeat(["class 0", "class 1", "uncertain"], [95, 95, 70])
pf.embedding_scatter(xy, labs, ax=ax_emb)
ax_emb.set_title("A  ML model audit", loc="left", fontweight="bold")
ax_emb.text(0.02, 0.03, "latent structure + class overlap", transform=ax_emb.transAxes,
            fontsize=8, va="bottom")
y_true = (rng.random(260) > 0.56).astype(int)
y_score = np.clip(0.58 * y_true + rng.beta(2, 4, 260), 0, 1)
pf.pr_curve(y_true, y_score, ax=ax_pr); ax_pr.set_title("precision-recall")
pf.convergence_curve({"train": np.exp(-np.linspace(0, 4.3, 70)) + 0.035,
                      "validation": np.exp(-np.linspace(0, 3.2, 70)) + 0.12},
                     ylabel="Loss", ax=ax_conv)
ax_conv.set_title("training dynamics")

# B. Molecular/experimental composite: spectrum hero + ternary + bubble.
gs_b = outer[0, 1].subgridspec(2, 2, height_ratios=[1.08, 1], wspace=0.34, hspace=0.45)
ax_spec = fig.add_subplot(gs_b[0, :])
ax_tern = fig.add_subplot(gs_b[1, 0])
ax_bub = fig.add_subplot(gs_b[1, 1])
x = np.linspace(100, 900, 620)
y = (1.2 * np.exp(-((x - 220) / 24) ** 2) + 0.78 * np.exp(-((x - 512) / 42) ** 2)
     + 0.48 * np.exp(-((x - 704) / 30) ** 2) + 0.018 * rng.random(x.size))
pf.spectrum(x, y, top=3, xlabel="Wavelength (nm)", ylabel="Relative intensity", ax=ax_spec)
ax_spec.set_title("B  Experimental signal and mixture space", loc="left", fontweight="bold")
aa, bb, cc = rng.dirichlet([2.1, 2.8, 4.2], 95).T
pf.ternary(aa, bb, cc, values=cc, labels=("polymer", "solvent", "dopant"), ax=ax_tern)
pf.bubble(rng.normal(0, 1, 34), rng.normal(0, 1, 34), rng.gamma(2, 1, 34),
          color=rng.random(34), size_label="bubble area = yield", ax=ax_bub)
ax_bub.set_title("screening map")

# C. Structure composite: chord hero + network, dendrogram, Venn inset.
gs_c = outer[1, 0].subgridspec(2, 2, width_ratios=[1.05, 1], wspace=0.36, hspace=0.42)
ax_chord = fig.add_subplot(gs_c[:, 0])
ax_net = fig.add_subplot(gs_c[0, 1])
ax_den = fig.add_subplot(gs_c[1, 1])
M = np.array([[0, 5, 2, 1], [5, 0, 3, 4], [2, 3, 0, 5], [1, 4, 5, 0]], float)
pf.chord(M, labels=["omics", "clinic", "image", "model"], ax=ax_chord)
ax_chord.set_title("C  Cohort structure and evidence flow", loc="left", fontweight="bold")
ax_venn = ax_chord.inset_axes([0.02, 0.02, 0.36, 0.32])
pf.venn2((42, 35, 18), labels=("A", "B"), ax=ax_venn)
pf.network_graph([("A", "B", 2), ("A", "C", 1), ("B", "D", 2),
                  ("C", "D", 1), ("D", "E", 2), ("C", "E", 1)],
                 ax=ax_net)
ax_net.set_title("topology")
pf.dendrogram(rng.normal(0, 1, (8, 4)), labels=[f"s{i}" for i in range(8)], ax=ax_den)
ax_den.set_title("sample hierarchy")

# D. Imaging/spatial composite: image plate hero + trajectory + attention map.
gs_d = outer[1, 1].subgridspec(2, 2, height_ratios=[1.1, 1], wspace=0.34, hspace=0.42)
ax_img = fig.add_subplot(gs_d[0, :])
ax_traj = fig.add_subplot(gs_d[1, 0])
ax_attn = fig.add_subplot(gs_d[1, 1])
yy, xx = np.mgrid[-1:1:100j, -1:1:100j]
img1 = np.exp(-((xx + 0.15) ** 2 + (yy - 0.05) ** 2) * 8) + 0.06 * rng.random((100, 100))
img2 = np.sin(12 * xx) * np.cos(10 * yy) + 0.12 * rng.random((100, 100))
img3 = np.exp(-((xx - 0.25) ** 2 + (yy + 0.2) ** 2) * 16) + 0.12 * np.sin(12 * yy)
fig_i, _ = pf.image_panel([img1, img2, img3], titles=["confocal", "MRI", "remote"],
                          cmaps=["gray", "magma", "viridis"],
                          scalebars=[(22, "20 um"), None, None],
                          cols=3, figsize=(6.2, 2.1))
tmp = HERE / "_coverage_image_plate.png"
fig_i.savefig(tmp, dpi=180, bbox_inches="tight")
plt.close(fig_i)
ax_img.imshow(mpimg.imread(tmp)); ax_img.set_axis_off()
ax_img.set_title("D  Image evidence, spatial dynamics, and attention", loc="left",
                 fontweight="bold")
tmp.unlink(missing_ok=True)
t = np.linspace(0, 1, 130)
pf.trajectory(np.cos(8.5 * t) * (1 + t), np.sin(8.5 * t) * (1 + t), t=t, ax=ax_traj)
ax_traj.set_title("trajectory")
A = rng.random((8, 8)); A = A / A.sum(axis=1, keepdims=True)
pf.attention_map(A, ax=ax_attn)
ax_attn.set_title("attention")

pf.save(fig, "gallery_coverage", outdir=str(HERE))
plt.close(fig)
print("[gallery] wrote examples/gallery_coverage.png")
