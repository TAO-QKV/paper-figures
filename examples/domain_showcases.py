"""Domain showcase galleries: complex composites across major paper categories.

Run: python examples/domain_showcases.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import paperfig as pf

pf.paper_style(font="sans")
rng = np.random.default_rng(47)
HERE = Path(__file__).resolve().parent


def tag(ax, text):
    ax.text(-0.045, 1.08, text, transform=ax.transAxes, fontweight="bold",
            ha="right", va="top", fontsize=9)


def save_domain(fig, name):
    pf.save(fig, name, outdir=str(HERE))
    plt.close(fig)


def statistics_domain():
    fig = plt.figure(figsize=(12.8, 7.4))
    gs = fig.add_gridspec(2, 4, width_ratios=[1.35, 1.0, 1.0, 1.0],
                          left=0.055, right=0.975, top=0.91, bottom=0.08,
                          wspace=0.38, hspace=0.50)
    ax_rain = fig.add_subplot(gs[:, 0])
    ax_ecdf = fig.add_subplot(gs[0, 1])
    ax_qq = fig.add_subplot(gs[0, 2])
    ax_ba = fig.add_subplot(gs[0, 3])
    ax_bar = fig.add_subplot(gs[1, 1])
    ax_ridge = fig.add_subplot(gs[1, 2:])
    fig.suptitle("Statistical inference panel: distribution, agreement, uncertainty",
                 x=0.055, y=0.985, ha="left", fontsize=13, fontweight="bold")

    groups = {
        "baseline": rng.normal(0.0, 0.85, 180),
        "dose low": rng.normal(0.42, 0.78, 180),
        "dose high": rng.normal(0.92, 0.72, 180),
    }
    pf.raincloud(groups, ylabel="Biomarker concentration (a.u.)", ax=ax_rain)
    ax_rain.set_title("Distribution shift with raw observations", loc="left")
    pf.ecdf({"baseline": groups["baseline"], "dose high": groups["dose high"]},
            xlabel="Biomarker concentration (a.u.)", ax=ax_ecdf)
    ax_ecdf.set_title("ECDF")
    pf.qq(groups["dose high"], ax=ax_qq); ax_qq.set_title("normality check")
    m1 = rng.normal(10, 1.8, 90)
    m2 = m1 + rng.normal(0.25, 0.65, 90)
    pf.bland_altman(m1, m2, ax=ax_ba); ax_ba.set_title("method agreement")
    pf.bar_err(groups, brackets=[(0, 2, "***")], ylabel="Mean response (a.u.)", ax=ax_bar)
    ax_bar.set_title("mean + 95% CI")
    pf.ridgeline({
        "batch 1": rng.normal(0.0, 0.8, 160),
        "batch 2": rng.normal(0.4, 0.7, 160),
        "batch 3": rng.normal(0.8, 0.6, 160),
        "batch 4": rng.normal(1.15, 0.55, 160),
    }, xlabel="Normalized score", ax=ax_ridge)
    ax_ridge.set_title("batch-wise density drift")
    for a, t in zip([ax_rain, ax_ecdf, ax_qq, ax_ba, ax_bar, ax_ridge], "abcdef"):
        tag(a, f"({t})")
    save_domain(fig, "gallery_domain_statistics")


def ml_domain():
    fig = plt.figure(figsize=(12.8, 7.5))
    gs = fig.add_gridspec(2, 4, width_ratios=[1.45, 1.0, 1.0, 1.0],
                          left=0.055, right=0.975, top=0.91, bottom=0.08,
                          wspace=0.40, hspace=0.48)
    ax_emb = fig.add_subplot(gs[:, 0])
    ax_conf = fig.add_subplot(gs[0, 1])
    ax_roc = fig.add_subplot(gs[0, 2])
    ax_pr = fig.add_subplot(gs[0, 3])
    ax_conv = fig.add_subplot(gs[1, 1])
    ax_attn = fig.add_subplot(gs[1, 2])
    ax_imp = fig.add_subplot(gs[1, 3])
    fig.suptitle("Machine-learning audit: discrimination, calibration, representation, saliency",
                 x=0.055, y=0.985, ha="left", fontsize=13, fontweight="bold")

    xy = np.vstack([
        rng.normal([-1.0, 0.0], 0.45, (110, 2)),
        rng.normal([1.2, 0.3], 0.45, (110, 2)),
        rng.normal([0.2, 1.65], 0.38, (85, 2)),
    ])
    labs = np.repeat(["class A", "class B", "OOD"], [110, 110, 85])
    pf.embedding_scatter(xy, labs, ax=ax_emb)
    ax_emb.set_title("Representation manifold + OOD region", loc="left")
    pf.confusion(np.array([[86, 8, 3], [6, 91, 5], [4, 7, 42]]),
                 labels=["A", "B", "OOD"], ax=ax_conf)
    ax_conf.set_title("confusion")
    y_true = (rng.random(260) > 0.55).astype(int)
    y_score = np.clip(0.60 * y_true + rng.beta(2, 4, 260), 0, 1)
    pf.roc_curve(y_true, y_score, ax=ax_roc); ax_roc.set_title("ROC")
    pf.pr_curve(y_true, y_score, ax=ax_pr); ax_pr.set_title("PR")
    pf.convergence_curve({"train": np.exp(-np.linspace(0, 4.0, 80)) + 0.04,
                          "validation": np.exp(-np.linspace(0, 3.3, 80)) + 0.12},
                         ylabel="Loss", ax=ax_conv)
    ax_conv.set_title("convergence")
    A = rng.random((9, 9)); A = A / A.sum(axis=1, keepdims=True)
    pf.attention_map(A, ax=ax_attn); ax_attn.set_title("attention")
    pf.feature_importance(["texture", "marker", "age", "dose", "gene", "site"],
                          [0.72, 0.64, 0.22, 0.37, 0.55, 0.18], ax=ax_imp)
    ax_imp.set_title("feature attribution")
    for a, t in zip([ax_emb, ax_conf, ax_roc, ax_pr, ax_conv, ax_attn, ax_imp], "abcdefg"):
        tag(a, f"({t})")
    save_domain(fig, "gallery_domain_ml")


def spatial_domain():
    fig = plt.figure(figsize=(12.8, 7.5))
    gs = fig.add_gridspec(2, 4, width_ratios=[1.0, 1.0, 1.15, 1.15],
                          left=0.055, right=0.975, top=0.91, bottom=0.08,
                          wspace=0.38, hspace=0.48)
    ax_stream = fig.add_subplot(gs[0, 0])
    ax_contour = fig.add_subplot(gs[0, 1])
    ax_surf = fig.add_subplot(gs[0, 2:], projection="3d")
    ax_traj = fig.add_subplot(gs[1, 0])
    ax_spec = fig.add_subplot(gs[1, 1])
    ax_img = fig.add_subplot(gs[1, 2:])
    fig.suptitle("Spatial, physical, and imaging evidence: fields, trajectories, surfaces, spectra",
                 x=0.055, y=0.985, ha="left", fontsize=13, fontweight="bold")

    x = np.linspace(-3, 3, 50)
    y = np.linspace(-3, 3, 50)
    X, Y = np.meshgrid(x, y)
    R = X ** 2 + Y ** 2 + 0.5
    U = -Y / R + 0.08 * np.cos(Y)
    V = X / R + 0.08 * np.sin(X)
    Z = np.sin(X) * np.cos(Y) * np.exp(-(X ** 2 + Y ** 2) / 17)
    pf.streamplot_field(X, Y, U, V, ax=ax_stream); ax_stream.set_title("streamlines")
    pf.contour_field(X, Y, Z, cbar_label="field", ax=ax_contour); ax_contour.set_title("contour field")
    pf.surface3d(X, Y, Z, cbar_label="response", ax=ax_surf); ax_surf.set_title("3-D response surface")
    t = np.linspace(0, 1, 140)
    pf.trajectory(np.cos(8.5 * t) * (1 + t), np.sin(8.5 * t) * (1 + t), t=t, ax=ax_traj)
    ax_traj.set_title("trajectory")
    wl = np.linspace(100, 900, 550)
    inten = (1.15 * np.exp(-((wl - 226) / 25) ** 2)
             + 0.72 * np.exp(-((wl - 515) / 43) ** 2)
             + 0.50 * np.exp(-((wl - 704) / 31) ** 2)
             + 0.02 * rng.random(wl.size))
    pf.spectrum(wl, inten, top=3, xlabel="Wavelength (nm)", ax=ax_spec)
    ax_spec.set_title("spectrum")
    yy, xx = np.mgrid[-1:1:100j, -1:1:100j]
    imgs = [
        np.exp(-((xx + 0.15) ** 2 + (yy - 0.05) ** 2) * 8) + 0.06 * rng.random((100, 100)),
        np.sin(12 * xx) * np.cos(10 * yy) + 0.12 * rng.random((100, 100)),
        np.exp(-((xx - 0.25) ** 2 + (yy + 0.2) ** 2) * 16) + 0.12 * np.sin(12 * yy),
    ]
    fig_i, _ = pf.image_panel(imgs, titles=["confocal", "MRI", "remote"],
                              cmaps=["gray", "magma", "viridis"],
                              scalebars=[(22, "20 um"), None, None], cols=3,
                              figsize=(6.2, 2.2))
    tmp = HERE / "_domain_spatial_images.png"
    fig_i.savefig(tmp, dpi=180, bbox_inches="tight")
    plt.close(fig_i)
    ax_img.imshow(mpimg.imread(tmp)); ax_img.set_axis_off(); ax_img.set_title("image plate")
    tmp.unlink(missing_ok=True)
    for a, tlabel in zip([ax_stream, ax_contour, ax_surf, ax_traj, ax_spec, ax_img], "abcdef"):
        if getattr(a, "name", "") == "3d":
            a.text2D(-0.06, 1.08, f"({tlabel})", transform=a.transAxes,
                     fontweight="bold", ha="right", va="top", fontsize=9)
        else:
            tag(a, f"({tlabel})")
    save_domain(fig, "gallery_domain_spatial")


def structure_domain():
    fig = plt.figure(figsize=(12.8, 7.5))
    gs = fig.add_gridspec(2, 4, width_ratios=[1.18, 1.0, 1.0, 1.0],
                          left=0.055, right=0.975, top=0.91, bottom=0.08,
                          wspace=0.38, hspace=0.48)
    ax_net = fig.add_subplot(gs[:, 0])
    ax_sank = fig.add_subplot(gs[0, 1])
    ax_chord = fig.add_subplot(gs[0, 2])
    ax_venn = fig.add_subplot(gs[0, 3])
    ax_den = fig.add_subplot(gs[1, 1])
    ax_tern = fig.add_subplot(gs[1, 2])
    ax_flow = fig.add_subplot(gs[1, 3])
    fig.suptitle("Structure, process, and mechanism: networks, flows, sets, hierarchies",
                 x=0.055, y=0.985, ha="left", fontsize=13, fontweight="bold")

    pos = {
        "data": np.array([-0.95, 1.25]), "QC": np.array([-0.95, 0.25]),
        "model": np.array([-0.05, 0.85]), "assay": np.array([-0.05, -0.25]),
        "risk": np.array([0.82, 0.35]), "decision": np.array([1.12, -0.85]),
    }
    edges = [("data", "model", 2), ("QC", "model", 1), ("assay", "risk", 1.6),
             ("model", "risk", 2.5), ("risk", "decision", 2.0),
             ("QC", "assay", 1.2)]
    pf.network_graph(edges, nodes=list(pos), pos=pos, directed=True, labels=False, ax=ax_net)
    ax_net.set_xlim(-1.35, 1.42)
    ax_net.set_ylim(-1.20, 1.58)
    label_offsets = {
        "data": (0.0, -0.17, "center", "top"),
        "QC": (0.0, 0.13, "center", "bottom"),
        "model": (0.0, 0.13, "center", "bottom"),
        "assay": (0.0, 0.13, "center", "bottom"),
        "risk": (0.0, 0.13, "center", "bottom"),
        "decision": (0.0, 0.13, "center", "bottom"),
    }
    for name, p in pos.items():
        dx, dy, ha, va = label_offsets[name]
        ax_net.text(p[0] + dx, p[1] + dy, name, ha=ha, va=va, fontsize=8,
                    bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.75))
    ax_net.set_title("mechanism graph", loc="left", pad=12)
    pf.sankey([12, -5.8, -3.4, -2.8],
              ["input", "train", "validate", "deploy"],
              orientations=[0, 1, -1, 0], gap=0.62,
              pathlengths=[0.45, 0.95, 0.95, 0.75], ax=ax_sank)
    ax_sank.set_title("Sankey")
    M = np.array([[0, 5, 2, 1], [5, 0, 3, 4], [2, 3, 0, 5], [1, 4, 5, 0]], float)
    pf.chord(M, labels=["omics", "clinic", "image", "model"], ax=ax_chord)
    ax_chord.set_title("chord")
    pf.venn2((42, 35, 18), labels=("screen A", "screen B"), ax=ax_venn)
    ax_venn.set_title("set overlap")
    pf.dendrogram(rng.normal(0, 1, (9, 4)), labels=[f"s{i}" for i in range(9)], ax=ax_den)
    ax_den.set_title("hierarchy")
    aa, bb, cc = rng.dirichlet([2.0, 2.6, 4.5], 90).T
    pf.ternary(aa, bb, cc, values=cc, labels=("A", "B", "C"), ax=ax_tern)
    ax_tern.set_title("ternary phase")
    pf.slopegraph([0.22, 0.35, 0.41, 0.58], [0.51, 0.46, 0.63, 0.78],
                  ["A", "B", "C", "D"], left="draft", right="final", ax=ax_flow)
    ax_flow.set_title("state transition")
    for a, tlabel in zip([ax_net, ax_sank, ax_chord, ax_venn, ax_den, ax_tern, ax_flow], "abcdefg"):
        tag(a, f"({tlabel})")
    save_domain(fig, "gallery_domain_structure")


if __name__ == "__main__":
    statistics_domain()
    ml_domain()
    spatial_domain()
    structure_domain()
    print("[gallery] wrote domain showcase galleries")
