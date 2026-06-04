"""Complex paper-style showcase panels.

Run: python examples/complex_panels.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, FancyArrowPatch, FancyBboxPatch, Rectangle, Circle, Polygon
import paperfig as pf

pf.paper_style(font="sans")
rng = np.random.default_rng(113)
HERE = Path(__file__).resolve().parent


def panel_label(ax, text, x=-0.055, y=1.04):
    ax.text(x, y, text, transform=ax.transAxes, fontweight="bold",
            ha="right", va="top", fontsize=9)


def save_complex(fig, name):
    pf.save(fig, name, outdir=str(HERE))
    plt.close(fig)


def norm01(a):
    a = np.asarray(a, float)
    return (a - a.min()) / (a.max() - a.min() + 1e-12)


def add_ellipse(ax, pts, color):
    cen = pts.mean(axis=0)
    cov = np.cov(pts.T)
    vals, vecs = np.linalg.eigh(cov)
    ang = np.degrees(np.arctan2(vecs[1, -1], vecs[0, -1]))
    ax.add_patch(Ellipse(cen, 3.25 * np.sqrt(vals[-1]), 3.25 * np.sqrt(vals[0]),
                         angle=ang, facecolor=color, alpha=0.10,
                         edgecolor=color, lw=1.0, zorder=1))


def complex_biomed():
    fig = plt.figure(figsize=(14.2, 8.6))
    gs = fig.add_gridspec(
        3, 5, width_ratios=[1.45, 1.45, 1.0, 1.0, 1.08],
        height_ratios=[1.0, 1.0, 1.0],
        left=0.052, right=0.982, top=0.91, bottom=0.075,
        wspace=0.38, hspace=0.50,
    )
    ax_hero = fig.add_subplot(gs[:, :2])
    ax_volcano = fig.add_subplot(gs[0, 2])
    ax_manhattan = fig.add_subplot(gs[0, 3:])
    ax_image = fig.add_subplot(gs[1, 2])
    ax_surv = fig.add_subplot(gs[1, 3:])
    ax_heat = fig.add_subplot(gs[2, 2])
    ax_forest = fig.add_subplot(gs[2, 3])
    ax_net = fig.add_subplot(gs[2, 4])
    fig.suptitle("Integrated biomedical discovery figure: representation, omics, imaging, prognosis",
                 x=0.052, y=0.985, ha="left", fontsize=13, fontweight="bold")

    # Hero: latent patient manifold with decision field, uncertainty ellipses, and diagnostics insets.
    n0, n1, nb = 150, 145, 85
    low = rng.multivariate_normal([-1.35, -0.45], [[0.38, 0.08], [0.08, 0.30]], n0)
    high = rng.multivariate_normal([1.15, 0.40], [[0.42, -0.05], [-0.05, 0.31]], n1)
    border = rng.multivariate_normal([0.05, 1.45], [[0.28, 0.03], [0.03, 0.22]], nb)
    xy = np.vstack([low, high, border])
    labs = np.repeat(["control-like", "responder", "ambiguous"], [n0, n1, nb])
    xx = np.linspace(-2.7, 2.55, 220)
    yy = np.linspace(-1.75, 2.65, 220)
    X, Y = np.meshgrid(xx, yy)
    S = 1.15 * X - 0.58 * Y + 0.28 * np.sin(2.2 * X) + 0.34
    P = 1 / (1 + np.exp(-S))
    ax_hero.contourf(X, Y, P, levels=[0, 0.35, 0.50, 0.65, 1],
                     colors=["#cfe4f2", "#eef2f3", "#f7f1e6", "#f2d4d1"],
                     alpha=0.55, zorder=0)
    ax_hero.contour(X, Y, P, levels=[0.50], colors="#333", linewidths=1.1,
                    linestyles="--", zorder=2)
    colors = [pf.PALETTE[0], pf.PALETTE[1], pf.PALETTE[2]]
    for color, lab in zip(colors, ["control-like", "responder", "ambiguous"]):
        pts = xy[labs == lab]
        add_ellipse(ax_hero, pts, color)
        ax_hero.scatter(pts[:, 0], pts[:, 1], s=17, color=color, alpha=0.62,
                        edgecolor="white", linewidth=0.25, label=lab, zorder=3)
    ax_hero.add_patch(FancyArrowPatch((-1.65, -1.20), (1.25, 1.28),
                                      arrowstyle="-|>", mutation_scale=15,
                                      lw=1.25, color="#444", alpha=0.85))
    ax_hero.text(-1.68, -1.42, "baseline state", ha="right", fontsize=8,
                 bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.78))
    ax_hero.text(1.12, 1.55, "therapy-sensitive\nstate", ha="left", fontsize=8,
                 bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.78))
    ax_hero.text(0.02, 0.03, "N = 380 patients; shaded field = predicted response probability",
                 transform=ax_hero.transAxes, fontsize=8, color="#444",
                 bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="#ddd", alpha=0.86))
    ax_hero.set_title("A  Multimodal response manifold and decision transition",
                      loc="left", fontweight="bold")
    ax_hero.set_xlabel("Latent axis 1"); ax_hero.set_ylabel("Latent axis 2")
    ax_hero.set_xlim(-3.35, 4.55)
    ax_hero.set_ylim(-2.65, 2.85)
    ax_hero.legend(loc="upper left", fontsize=8, frameon=True)
    y_true = np.r_[np.zeros(n0), np.ones(n1), rng.integers(0, 2, nb)]
    score = np.clip(P[np.clip(((xy[:, 1] - yy.min()) / (yy.max() - yy.min()) * 219).astype(int), 0, 219),
                      np.clip(((xy[:, 0] - xx.min()) / (xx.max() - xx.min()) * 219).astype(int), 0, 219)]
                    + rng.normal(0, 0.06, xy.shape[0]), 0, 1)
    diag_box = FancyBboxPatch((0.705, 0.105), 0.265, 0.625,
                              boxstyle="round,pad=0.012,rounding_size=0.012",
                              transform=ax_hero.transAxes, fc="white", ec="#dddddd",
                              lw=0.8, alpha=0.96, zorder=7)
    ax_hero.add_patch(diag_box)
    ax_hero.text(0.725, 0.712, "model diagnostics", transform=ax_hero.transAxes,
                 fontsize=8, fontweight="bold", zorder=9, clip_on=False)
    ax_roc = ax_hero.inset_axes([0.725, 0.145, 0.235, 0.235], zorder=8)
    pf.roc_curve(y_true, score, ax=ax_roc)
    ax_roc.set_title("ROC", fontsize=7, pad=1); ax_roc.tick_params(labelsize=6)
    ax_roc.set_xlabel("FPR", fontsize=6); ax_roc.set_ylabel("TPR", fontsize=6)
    ax_cal = ax_hero.inset_axes([0.725, 0.430, 0.235, 0.205], zorder=8)
    pf.calibration(y_true, score, n_bins=8, ax=ax_cal)
    ax_cal.set_title("calibration", fontsize=7, pad=1); ax_cal.tick_params(labelsize=6)
    ax_cal.set_xlabel(""); ax_cal.set_ylabel("obs.", fontsize=6)

    # Omics: volcano + Manhattan evidence.
    lfc = rng.normal(0, 1.18, 1200)
    pvals = 10 ** (-(0.45 + np.abs(lfc) * rng.gamma(1.5, 0.9, 1200)))
    genes = np.array([f"G{i}" for i in range(1200)])
    pf.volcano(lfc, pvals, labels=genes, top=4, ax=ax_volcano)
    ax_volcano.set_title("B  differential pathway gate", loc="left", fontweight="bold")
    chrom = np.repeat(np.arange(1, 11), 90)
    pos = np.tile(np.linspace(0, 120, 90), 10)
    gwas_p = 10 ** (-rng.gamma(1.2, 1.2, chrom.size))
    for idx, exp in zip([72, 360, 714, 841], [9.5, 7.2, 8.3, 6.8]):
        gwas_p[idx] = 10 ** (-exp)
    labels = np.array([f"rs{i}" for i in range(chrom.size)])
    pf.manhattan(chrom, pos, gwas_p, labels=labels, top=4, ax=ax_manhattan)
    ax_manhattan.set_title("C  genome-wide association peaks", loc="left", fontweight="bold")

    # Imaging plate with spectral inset.
    ax_image.set_axis_off()
    ax_image.set_title("D  image phenotype", loc="left", fontweight="bold")
    yy2, xx2 = np.mgrid[-1:1:120j, -1:1:120j]
    imgs = [
        (np.exp(-((xx2 + 0.18) ** 2 + (yy2 - 0.08) ** 2) * 12)
         + 0.10 * rng.random((120, 120)), "confocal", "gray"),
        (np.sin(16 * xx2) * np.cos(13 * yy2) + 0.20 * rng.random((120, 120)), "MRI texture", "magma"),
        (np.exp(-((xx2 - 0.28) ** 2 + (yy2 + 0.12) ** 2) * 18)
         + 0.18 * np.sin(10 * yy2), "remote", "viridis"),
    ]
    for i, (img, title, cmap) in enumerate(imgs):
        iax = ax_image.inset_axes([0.04 + 0.32 * i, 0.26, 0.29, 0.58])
        iax.imshow(img, cmap=cmap)
        iax.set_axis_off()
        iax.set_title(title, fontsize=7, pad=2)
    ax_image.plot([0.12, 0.31], [0.20, 0.20], transform=ax_image.transAxes,
                  color="#222", lw=2.2, solid_capstyle="butt")
    ax_image.text(0.215, 0.13, "50 um", transform=ax_image.transAxes,
                  ha="center", fontsize=7)
    ax_sp = ax_image.inset_axes([0.08, 0.02, 0.84, 0.20])
    wl = np.linspace(120, 850, 420)
    inten = (0.9 * np.exp(-((wl - 232) / 23) ** 2)
             + 0.55 * np.exp(-((wl - 515) / 44) ** 2)
             + 0.35 * np.exp(-((wl - 704) / 35) ** 2)
             + 0.025 * rng.random(wl.size))
    pf.spectrum(wl, inten, top=2, xlabel="", ylabel="", ax=ax_sp)
    ax_sp.tick_params(labelsize=6); ax_sp.set_title("spectral confirmation", fontsize=7)

    pf.survival({
        "signature low": (rng.weibull(1.18, 135) * 15, (rng.random(135) > 0.22).astype(int)),
        "signature high": (rng.weibull(1.55, 135) * 25, (rng.random(135) > 0.25).astype(int)),
    }, xlabel="Follow-up time (months)", ax=ax_surv)
    ax_surv.set_title("E  prospective survival validation", loc="left", fontweight="bold")
    ax_surv.text(0.05, 0.10, "log-rank p = 0.004\nN = 270", transform=ax_surv.transAxes,
                 fontsize=8, bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="#ddd"))

    H = rng.normal(0, 0.55, (6, 6))
    H += np.linspace(-0.8, 0.8, 6)[:, None] * np.linspace(0.6, -0.6, 6)[None, :]
    pf.heatmap(H, row_labels=["DNA", "RNA", "met", "img", "clin", "risk"],
               col_labels=["S1", "S2", "S3", "S4", "S5", "S6"],
               cbar_label="z", annot=False, ax=ax_heat)
    ax_heat.set_title("F  cross-modal covariance", loc="left", fontweight="bold")
    est = np.array([-0.42, -0.28, -0.51, -0.39])
    lo = est - np.array([0.12, 0.18, 0.15, 0.09])
    hi = est + np.array([0.13, 0.19, 0.14, 0.08])
    pf.forest(["site A", "site B", "site C", "pooled"], est, lo, hi,
              xlabel="log HR", ax=ax_forest)
    ax_forest.set_title("G  external sites", loc="left", fontweight="bold")
    pos = {
        "DNA": np.array([-1.0, 0.75]), "RNA": np.array([-1.0, 0.10]),
        "IMG": np.array([-1.0, -0.55]), "KIN": np.array([0.05, 0.45]),
        "IMM": np.array([0.05, -0.25]), "RSP": np.array([1.0, 0.02]),
    }
    edges = [("DNA", "KIN", 2.4), ("RNA", "KIN", 1.5), ("RNA", "IMM", 2.0),
             ("IMG", "IMM", 1.2), ("KIN", "RSP", 2.6), ("IMM", "RSP", 2.1)]
    pf.network_graph(edges, nodes=list(pos), pos=pos, directed=True, labels=False, ax=ax_net)
    ax_net.set_xlim(-1.3, 1.28); ax_net.set_ylim(-0.88, 1.04)
    ax_net.set_title("H  mechanism graph", loc="left", fontweight="bold")
    for name, p in pos.items():
        ax_net.text(p[0], p[1] + 0.13, name, ha="center", va="bottom", fontsize=7,
                    bbox=dict(boxstyle="round,pad=0.10", fc="white", ec="none", alpha=0.78))

    for ax, lab in zip([ax_hero, ax_volcano, ax_manhattan, ax_image, ax_surv, ax_heat, ax_forest, ax_net],
                       list("abcdefgh")):
        panel_label(ax, f"({lab})")
    save_complex(fig, "gallery_complex_biomed")


def complex_physics():
    fig = plt.figure(figsize=(14.2, 8.6))
    gs = fig.add_gridspec(
        3, 5, width_ratios=[1.35, 1.35, 1.0, 1.0, 1.0],
        height_ratios=[1.05, 1.0, 1.0],
        left=0.052, right=0.982, top=0.91, bottom=0.075,
        wspace=0.40, hspace=0.50,
    )
    ax_field = fig.add_subplot(gs[:2, :2])
    ax_surface = fig.add_subplot(gs[0, 2:4], projection="3d")
    ax_spectrum = fig.add_subplot(gs[0, 4])
    ax_ts = fig.add_subplot(gs[1, 2:4])
    ax_qq = fig.add_subplot(gs[1, 4])
    ax_phase = fig.add_subplot(gs[2, 0])
    ax_traj = fig.add_subplot(gs[2, 1])
    ax_zoom = fig.add_subplot(gs[2, 2])
    ax_image = fig.add_subplot(gs[2, 3:])
    fig.suptitle("Integrated spatial-physical evidence figure: fields, dynamics, spectra, imaging",
                 x=0.052, y=0.985, ha="left", fontsize=13, fontweight="bold")

    x = np.linspace(-3.2, 3.2, 70)
    y = np.linspace(-3.0, 3.0, 70)
    X, Y = np.meshgrid(x, y)
    Z = (np.sin(1.25 * X) * np.cos(1.05 * Y)
         + 0.42 * np.exp(-((X - 0.9) ** 2 + (Y + 0.55) ** 2) / 0.55)
         - 0.55 * np.exp(-((X + 1.15) ** 2 + (Y - 0.85) ** 2) / 0.75))
    R = X ** 2 + Y ** 2 + 0.55
    U = -Y / R + 0.11 * np.cos(1.4 * Y)
    V = X / R + 0.11 * np.sin(1.2 * X)
    im = ax_field.contourf(X, Y, Z, levels=16, cmap="viridis", alpha=0.92)
    ax_field.streamplot(X, Y, U, V, color=np.hypot(U, V), cmap="cividis",
                        density=1.25, linewidth=0.85, arrowsize=0.8)
    t = np.linspace(0, 1, 180)
    tx = -2.4 + 5.0 * t
    ty = 1.35 * np.sin(2.25 * np.pi * t) - 0.6 * t
    ax_field.plot(tx, ty, color="white", lw=3.0, alpha=0.85, zorder=4)
    ax_field.scatter(tx[::8], ty[::8], c=t[::8], cmap="plasma", s=30,
                     edgecolor="white", linewidth=0.35, zorder=5)
    sensors = rng.uniform([-2.7, -2.3], [2.7, 2.4], (18, 2))
    ax_field.scatter(sensors[:, 0], sensors[:, 1], marker="^", s=42,
                     color="#222", edgecolor="white", linewidth=0.35, zorder=6,
                     label="sensors")
    ax_field.add_patch(Rectangle((-0.55, -0.45), 1.1, 0.90, fc="none",
                                 ec="white", lw=1.2, ls="--"))
    ax_field.text(0.02, 0.04, "trajectory over measured vector field; N = 18 sensors",
                  transform=ax_field.transAxes, fontsize=8,
                  bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="#ddd", alpha=0.86))
    ax_field.set_title("A  Flow field with trajectory, sensors, and zoomed anomaly",
                       loc="left", fontweight="bold")
    ax_field.set_xlabel("$x$ (mm)"); ax_field.set_ylabel("$y$ (mm)")
    cb = fig.colorbar(im, ax=ax_field, fraction=0.035, pad=0.02)
    cb.set_label("field amplitude")

    pf.surface3d(X, Y, Z, cbar_label="response", ax=ax_surface)
    ax_surface.set_title("B  response surface", loc="left", fontweight="bold")
    wl = np.linspace(110, 930, 650)
    inten = (1.0 * np.exp(-((wl - 218) / 22) ** 2)
             + 0.62 * np.exp(-((wl - 503) / 38) ** 2)
             + 0.50 * np.exp(-((wl - 732) / 27) ** 2)
             + 0.02 * rng.random(wl.size))
    pf.spectrum(wl, inten, top=3, xlabel="nm", ylabel="intensity", ax=ax_spectrum)
    ax_spectrum.set_title("C  spectrum peaks", loc="left", fontweight="bold")

    tt = np.linspace(0, 12, 90)
    yhat = 0.18 * tt + 0.62 * np.sin(tt / 1.4)
    lo = yhat - (0.22 + 0.035 * tt)
    hi = yhat + (0.22 + 0.035 * tt)
    obs = yhat + rng.normal(0, 0.22 + 0.028 * tt, tt.size)
    pf.timeseries_ci(tt, obs, yhat, lo, hi, xlabel="time (s)",
                     ylabel="response (a.u.)", ax=ax_ts)
    ax_ts.axvspan(4.0, 7.4, color=pf.PALETTE[3], alpha=0.10)
    ax_ts.annotate("forcing window", xy=(5.7, hi.max() * 0.78),
                   xytext=(7.5, hi.max() * 0.98),
                   arrowprops=dict(arrowstyle="->", lw=0.8), fontsize=8)
    ax_ts.set_title("D  dynamic response with widening uncertainty",
                    loc="left", fontweight="bold")
    pf.qq(obs - yhat, ax=ax_qq)
    ax_qq.set_title("E  residual normality", loc="left", fontweight="bold")

    # Lower-row focused evidence.
    px = np.linspace(-2.2, 2.2, 24)
    py = np.linspace(-2.0, 2.0, 24)
    PX, PY = np.meshgrid(px, py)
    PU = PY - 0.25 * PX * (PX ** 2 + PY ** 2)
    PV = -PX - 0.20 * PY * (PX ** 2 + PY ** 2)
    ax_phase.streamplot(PX, PY, PU, PV, color=np.hypot(PU, PV), cmap="viridis",
                        density=1.15, arrowsize=0.8)
    ax_phase.set_title("F  phase portrait", loc="left", fontweight="bold")
    ax_phase.set_xlabel("$x$"); ax_phase.set_ylabel("$\\dot{x}$")
    pf.trajectory(np.cos(8.4 * t) * (1 + t), np.sin(8.4 * t) * (1 + t),
                  t=t, ax=ax_traj)
    ax_traj.set_title("G  tracked trajectory", loc="left", fontweight="bold")
    zmask = (X >= -0.55) & (X <= 0.55) & (Y >= -0.45) & (Y <= 0.45)
    ax_zoom.contourf(X, Y, Z, levels=12, cmap="viridis")
    ax_zoom.contour(X, Y, Z, levels=7, colors="white", linewidths=0.45, alpha=0.75)
    ax_zoom.scatter(sensors[:, 0], sensors[:, 1], marker="^", s=28,
                    color="#222", edgecolor="white", linewidth=0.3)
    ax_zoom.set_xlim(-0.75, 0.75); ax_zoom.set_ylim(-0.65, 0.65)
    ax_zoom.set_title("H  anomaly zoom", loc="left", fontweight="bold")
    ax_zoom.set_xlabel("$x$ (mm)"); ax_zoom.set_ylabel("$y$ (mm)")
    _ = zmask  # documents that the zoom bounds are matched to the hero anomaly.

    ax_image.set_axis_off()
    ax_image.set_title("I  aligned imaging readouts", loc="left", fontweight="bold")
    yy3, xx3 = np.mgrid[-1:1:110j, -1:1:110j]
    plates = [
        (norm01(np.exp(-((xx3 + 0.2) ** 2 + (yy3 - 0.05) ** 2) * 7)
                + 0.06 * rng.random((110, 110))), "thermal", "inferno"),
        (norm01(np.sin(13 * xx3) * np.cos(11 * yy3) + 0.10 * rng.random((110, 110))),
         "micrograph", "gray"),
        (norm01(np.exp(-((xx3 - 0.35) ** 2 + (yy3 + 0.15) ** 2) * 15)
                + 0.16 * np.sin(10 * yy3)), "remote", "viridis"),
    ]
    for i, (img, title, cmap) in enumerate(plates):
        iax = ax_image.inset_axes([0.03 + i * 0.32, 0.14, 0.29, 0.72])
        iax.imshow(img, cmap=cmap)
        iax.set_axis_off()
        iax.set_title(title, fontsize=8, pad=2)
    ax_image.text(0.04, 0.03, "same field registered across modalities",
                  transform=ax_image.transAxes, fontsize=8)

    for ax, lab in zip([ax_field, ax_surface, ax_spectrum, ax_ts, ax_qq,
                        ax_phase, ax_traj, ax_zoom, ax_image], list("abcdefghi")):
        if getattr(ax, "name", "") == "3d":
            ax.text2D(-0.055, 1.04, f"({lab})", transform=ax.transAxes,
                      fontweight="bold", ha="right", va="top", fontsize=9)
        else:
            panel_label(ax, f"({lab})")
    save_complex(fig, "gallery_complex_physics")


def draw_box(ax, xy, wh, title, subtitle, color):
    x, y = xy
    w, h = wh
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.025",
                         fc=color, ec="#3d3d3d", lw=0.8, alpha=0.92)
    ax.add_patch(box)
    ax.text(x + 0.03, y + h - 0.055, title, fontsize=9, fontweight="bold",
            ha="left", va="top")
    ax.text(x + 0.03, y + h - 0.115, subtitle, fontsize=7.5,
            ha="left", va="top", color="#333")
    return box


def arrow(ax, xy0, xy1, rad=0.0):
    ax.add_patch(FancyArrowPatch(xy0, xy1, arrowstyle="-|>", mutation_scale=11,
                                 lw=1.0, color="#444",
                                 connectionstyle=f"arc3,rad={rad}"))


def complex_systems():
    fig = plt.figure(figsize=(14.2, 8.7))
    gs = fig.add_gridspec(
        3, 5, width_ratios=[1.28, 1.28, 1.28, 1.0, 1.0],
        height_ratios=[1.05, 1.0, 1.0],
        left=0.052, right=0.982, top=0.91, bottom=0.075,
        wspace=0.40, hspace=0.50,
    )
    ax_flow = fig.add_subplot(gs[:2, :3])
    ax_sankey = fig.add_subplot(gs[0, 3])
    ax_chord = fig.add_subplot(gs[0, 4])
    ax_state = fig.add_subplot(gs[1, 3])
    ax_gantt = fig.add_subplot(gs[1, 4])
    ax_net = fig.add_subplot(gs[2, 0])
    ax_den = fig.add_subplot(gs[2, 1])
    ax_venn = fig.add_subplot(gs[2, 2])
    ax_tern = fig.add_subplot(gs[2, 3])
    ax_slope = fig.add_subplot(gs[2, 4])
    fig.suptitle("Integrated method/system figure: architecture, workflow, evidence flow, validation state",
                 x=0.052, y=0.985, ha="left", fontsize=13, fontweight="bold")

    ax_flow.set_axis_off()
    ax_flow.set_title("A  Reproducible scientific-figure skill architecture",
                      loc="left", fontweight="bold")
    ax_flow.set_xlim(0, 1); ax_flow.set_ylim(0, 1)
    lanes = [("data sources", 0.70, "#eaf3fb"), ("figure engine", 0.38, "#f7f0e8"),
             ("journal QA", 0.08, "#eef7ed")]
    for title, y, color in lanes:
        ax_flow.add_patch(Rectangle((0.02, y), 0.96, 0.24, fc=color, ec="none", alpha=0.9))
        ax_flow.text(0.035, y + 0.215, title, fontsize=8, fontweight="bold",
                     color="#333", va="top")
    # three column-aligned tracks x three lanes -> clean orthogonal grid
    cols, bw, bh = [0.19, 0.50, 0.80], 0.21, 0.13
    grid = [
        (0.75, "#dcecf8", [("data / processed", "CSV, matrices, images"),
                           ("figure contract", "claim, N, uncertainty"),
                           ("archetype router", "ML / omics / spatial")]),
        (0.45, "#f4dfc9", [("matplotlib API", "48 callable charts"),
                           ("TikZ method layer", "mechanism, hero"),
                           ("composition", "hero + insets + panels")]),
        (0.15, "#dff0df", [("style preset", "journal fonts, CVD-safe"),
                           ("quality checklist", "depth, elegance, proof"),
                           ("PDF / PNG / SVG", "editable, reproducible")]),
    ]
    for y, color, items in grid:
        for cx, (t, s) in zip(cols, items):
            draw_box(ax_flow, (cx - bw / 2, y), (bw, bh), t, s, color)
    # 6 vertical arrows (per track, between lanes) — no diagonals, no crossings
    for cx in cols:
        arrow(ax_flow, (cx, 0.75), (cx, 0.58))   # data sources -> figure engine
        arrow(ax_flow, (cx, 0.45), (cx, 0.28))   # figure engine -> journal QA
    ax_flow.text(0.035, 0.025, "hard guardrails: no inline data > 20 rows  ·  one style preset  ·  three-format vector export",
                 fontsize=8, color="#444")

    # a clean centered funnel reads better than a single-node Sankey in a small cell
    ax_sankey.set_axis_off(); ax_sankey.set_xlim(0, 1); ax_sankey.set_ylim(0, 1)
    ax_sankey.set_title("B  request funnel", loc="left", fontweight="bold")
    funnel = [("requests", 1.00), ("drafts", 0.74), ("revisions", 0.58), ("exports", 0.49)]
    n = len(funnel); ytop, ybot = 0.82, 0.05; band = (ytop - ybot) / n
    fr = [f for _, f in funnel] + [funnel[-1][1] * 0.82]
    for i, (name, frac) in enumerate(funnel):
        y1 = ytop - i * band; y0 = y1 - band * 0.80
        w0, w1 = fr[i] * 0.80, fr[i + 1] * 0.80
        ax_sankey.add_patch(Polygon(
            [(0.5 - w0 / 2, y1), (0.5 + w0 / 2, y1), (0.5 + w1 / 2, y0), (0.5 - w1 / 2, y0)],
            closed=True, fc=pf.PALETTE[i % len(pf.PALETTE)], ec="white", lw=1.0, alpha=0.85))
        ax_sankey.text(0.5, (y0 + y1) / 2, f"{name}  {int(frac * 100)}", ha="center",
                       va="center", fontsize=7.2, color="white", fontweight="bold")
    M = np.array([[0, 6, 4, 2], [6, 0, 3, 5], [4, 3, 0, 4], [2, 5, 4, 0]], float)
    pf.chord(M, labels=["stats", "ML", "image", "mechanism"], ax=ax_chord)
    ax_chord.set_title("C  chart-family coupling", loc="left", fontweight="bold")

    ax_state.set_axis_off()
    ax_state.set_title("D  state machine", loc="left", fontweight="bold")
    state_pos = {"contract": (0.22, 0.70), "draft": (0.70, 0.70),
                 "QA": (0.70, 0.28), "export": (0.22, 0.28)}
    for i, (name, p) in enumerate(state_pos.items()):
        ax_state.add_patch(Circle(p, 0.13, fc=pf.PALETTE[i % len(pf.PALETTE)],
                                  ec="white", lw=1.0, alpha=0.85))
        ax_state.text(*p, name, ha="center", va="center", color="white",
                      fontsize=8, fontweight="bold")
    for a, b, rad in [("contract", "draft", 0), ("draft", "QA", 0),
                      ("QA", "export", 0), ("QA", "draft", -0.30)]:
        arrow(ax_state, state_pos[a], state_pos[b], rad=rad)
    ax_state.text(0.08, 0.05, "fail any axis -> revise", fontsize=8, color="#444")

    ax_gantt.set_title("E  production timeline", loc="left", fontweight="bold")
    tasks = ["contract", "data", "draw", "QA", "export"]
    starts = np.array([0.0, 0.7, 1.4, 2.6, 3.2])
    dur = np.array([0.8, 1.1, 1.4, 0.9, 0.5])
    for i, (s, d) in enumerate(zip(starts, dur)):
        ax_gantt.barh(i, d, left=s, color=pf.PALETTE[i % len(pf.PALETTE)],
                      alpha=0.72, edgecolor="white")
    ax_gantt.set_yticks(range(len(tasks))); ax_gantt.set_yticklabels(tasks)
    ax_gantt.set_xlabel("iteration")
    ax_gantt.invert_yaxis()

    pos = {"data": np.array([-1.0, 0.65]), "style": np.array([-0.75, -0.55]),
           "chart": np.array([0.0, 0.15]), "caption": np.array([0.70, -0.55]),
           "paper": np.array([1.0, 0.65])}
    pf.network_graph([("data", "chart", 2), ("style", "chart", 1.6),
                      ("chart", "caption", 1.2), ("chart", "paper", 2.2),
                      ("caption", "paper", 1.4)],
                     nodes=list(pos), pos=pos, directed=True, labels=False, ax=ax_net)
    ax_net.set_title("F  dependency graph", loc="left", fontweight="bold")
    ax_net.set_xlim(-1.3, 1.3); ax_net.set_ylim(-0.9, 1.0)
    for name, p in pos.items():
        ax_net.text(p[0], p[1] + 0.12, name, ha="center", fontsize=7,
                    bbox=dict(boxstyle="round,pad=0.10", fc="white", ec="none", alpha=0.78))
    pf.dendrogram(rng.normal(0, 1, (10, 5)), labels=[f"fig{i}" for i in range(10)], ax=ax_den)
    ax_den.set_title("G  figure clustering", loc="left", fontweight="bold")
    pf.venn2((48, 13, 16), labels=("API", "TikZ"), ax=ax_venn)
    ax_venn.set_title("H  coverage overlap", loc="left", fontweight="bold")
    aa, bb, cc = rng.dirichlet([2.6, 2.2, 4.8], 120).T
    pf.ternary(aa, bb, cc, values=cc, labels=("data", "method", "claim"), ax=ax_tern)
    ax_tern.set_title("I  composition trade-space", loc="left", fontweight="bold", pad=14)
    pf.slopegraph([0.28, 0.42, 0.33, 0.51], [0.78, 0.72, 0.69, 0.88],
                  ["depth", "elegance", "proof", "gap"],
                  left="ordinary", right="paperfig", ax=ax_slope)
    ax_slope.set_title("J  quality lift", loc="left", fontweight="bold")

    for ax, lab in zip([ax_flow, ax_sankey, ax_chord, ax_state, ax_gantt,
                        ax_net, ax_den, ax_venn, ax_tern, ax_slope], list("abcdefghij")):
        panel_label(ax, f"({lab})")
    save_complex(fig, "gallery_complex_systems")


if __name__ == "__main__":
    complex_biomed()
    complex_physics()
    complex_systems()
    print("[gallery] wrote complex integrated showcase panels")
