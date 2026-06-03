"""Extended scientific chart types across fields — ML, statistics, omics,
medical, physics, and richer multi-axes figures.

All numpy + matplotlib + Python stdlib (no sklearn/scipy). Each returns
``(fig, ax)`` (or ``(fig, axes)`` for multi-axes figures).
"""
from __future__ import annotations
from statistics import NormalDist
import numpy as np
import matplotlib.pyplot as plt
from .style import PALETTE


def _fig(ax, figsize):
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure
    return fig, ax


def _as_groups(g):
    return g if isinstance(g, dict) else {"": np.asarray(g, float)}


# ============================ ML / diagnostics ============================

def roc_curve(y_true, y_score, *, label=None, figsize=(4.2, 3.9), ax=None):
    """ROC curve with AUC (binary labels + scores). No sklearn needed."""
    yt = np.asarray(y_true).astype(int)
    order = np.argsort(-np.asarray(y_score, float))
    yt = yt[order]
    P, N = yt.sum(), (yt == 0).sum()
    tpr = np.concatenate([[0], np.cumsum(yt) / max(P, 1)])
    fpr = np.concatenate([[0], np.cumsum(1 - yt) / max(N, 1)])
    auc = float(np.sum(np.diff(fpr) * (tpr[1:] + tpr[:-1]) / 2))  # trapezoid, version-agnostic
    fig, ax = _fig(ax, figsize)
    lab = (f"{label} " if label else "") + f"AUC = {auc:.3f}"
    ax.plot(fpr, tpr, color=PALETTE[0], lw=2, label=lab)
    ax.plot([0, 1], [0, 1], ls="--", color="#888", lw=0.8)
    ax.set_xlabel("False positive rate"); ax.set_ylabel("True positive rate")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1.02); ax.legend(loc="lower right")
    return fig, ax


def calibration(y_true, y_prob, *, n_bins=10, figsize=(4.2, 3.9), ax=None):
    """Reliability diagram: predicted probability vs observed frequency."""
    yt = np.asarray(y_true, float); yp = np.asarray(y_prob, float)
    edges = np.linspace(0, 1, n_bins + 1)
    idx = np.clip(np.digitize(yp, edges) - 1, 0, n_bins - 1)
    xs, ys = [], []
    for b in range(n_bins):
        m = idx == b
        if m.any():
            xs.append(yp[m].mean()); ys.append(yt[m].mean())
    fig, ax = _fig(ax, figsize)
    ax.plot([0, 1], [0, 1], ls="--", color="#888", lw=0.8, label="perfect")
    ax.plot(xs, ys, "o-", color=PALETTE[0], ms=4, label="model")
    ax.set_xlabel("Predicted probability"); ax.set_ylabel("Observed frequency")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.legend(loc="upper left")
    return fig, ax


# ============================ statistics ============================

def ecdf(groups, *, xlabel="Value", figsize=(5, 3.4), ax=None):
    """Empirical CDF (step), one curve per group."""
    groups = _as_groups(groups)
    fig, ax = _fig(ax, figsize)
    for i, (k, v) in enumerate(groups.items()):
        v = np.sort(np.asarray(v, float))
        y = np.arange(1, v.size + 1) / v.size
        ax.step(np.concatenate([v[:1], v]), np.concatenate([[0], y]),
                where="post", color=PALETTE[i % len(PALETTE)], lw=1.6, label=k or None)
    ax.set_xlabel(xlabel); ax.set_ylabel("Cumulative probability"); ax.set_ylim(0, 1.02)
    if any(groups):
        ax.legend()
    return fig, ax


def box(groups, *, ylabel="Value", jitter=True, figsize=(5, 3.4), ax=None):
    """Grouped box plots, optionally with jittered raw points overlaid."""
    fig, ax = _fig(ax, figsize)
    labels = list(groups); data = [np.asarray(groups[k], float) for k in labels]
    bp = ax.boxplot(data, patch_artist=True, showfliers=not jitter, widths=0.5,
                    medianprops=dict(color="#222"))
    for i, b in enumerate(bp["boxes"]):
        c = PALETTE[i % len(PALETTE)]
        b.set(facecolor=c, alpha=0.4, edgecolor=c)
    if jitter:
        rng = np.random.default_rng(0)
        for i, v in enumerate(data):
            ax.scatter(i + 1 + rng.uniform(-0.12, 0.12, len(v)), v, s=6,
                       color=PALETTE[i % len(PALETTE)], alpha=0.4, edgecolor="none")
    ax.set_xticks(range(1, len(labels) + 1)); ax.set_xticklabels(labels)
    ax.set_ylabel(ylabel)
    return fig, ax


def bar_err(groups, *, ylabel="Value", ci=0.95, brackets=None, figsize=(5, 3.4), ax=None):
    """Mean bar + confidence-interval error bars, with optional significance brackets.

    brackets: list of (i, j, text) — draws a bracket between bars i and j.
    """
    fig, ax = _fig(ax, figsize)
    labels = list(groups); data = [np.asarray(groups[k], float) for k in labels]
    means = np.array([v.mean() for v in data])
    z = 2.576 if ci >= 0.99 else 1.96
    errs = np.array([z * v.std(ddof=1) / np.sqrt(len(v)) for v in data])
    x = np.arange(len(labels))
    ax.bar(x, means, color=[PALETTE[i % len(PALETTE)] for i in range(len(labels))],
           alpha=0.55, edgecolor="white", yerr=errs, capsize=3,
           error_kw=dict(lw=1, ecolor="#333"))
    ax.set_xticks(x); ax.set_xticklabels(labels); ax.set_ylabel(ylabel)
    if brackets:
        top = float((means + errs).max()); h = top * 0.05
        for n, (i, j, txt) in enumerate(brackets):
            y = top + h * (1.6 + 2.4 * n)
            ax.plot([i, i, j, j], [y, y + h, y + h, y], color="#333", lw=0.9)
            ax.text((i + j) / 2, y + h, txt, ha="center", va="bottom", fontsize=8)
    return fig, ax


def qq(data, *, figsize=(4, 3.9), ax=None):
    """Normal Q-Q plot (standardized sample vs theoretical normal quantiles)."""
    v = np.sort(np.asarray(data, float)); n = v.size
    nd = NormalDist()
    theo = np.array([nd.inv_cdf((i + 0.5) / n) for i in range(n)])
    z = (v - v.mean()) / v.std(ddof=1)
    fig, ax = _fig(ax, figsize)
    ax.scatter(theo, z, s=10, color=PALETTE[0], alpha=0.6)
    lim = [min(theo.min(), z.min()) - 0.2, max(theo.max(), z.max()) + 0.2]
    ax.plot(lim, lim, ls="--", color="#888", lw=0.8)
    ax.set_xlabel("Theoretical quantiles"); ax.set_ylabel("Sample quantiles ($z$)")
    return fig, ax


# ============================ omics / bio ============================

def volcano(log2fc, pvals, *, fc_thresh=1.0, p_thresh=0.05, labels=None, top=0,
            figsize=(5, 4.2), ax=None):
    """Volcano plot: log2 fold-change vs -log10 p, with thresholds + sig coloring."""
    lfc = np.asarray(log2fc, float); pv = np.asarray(pvals, float)
    nlp = -np.log10(np.clip(pv, 1e-300, 1.0))
    sig = (np.abs(lfc) >= fc_thresh) & (pv <= p_thresh)
    up, down = sig & (lfc > 0), sig & (lfc < 0)
    fig, ax = _fig(ax, figsize)
    ax.scatter(lfc[~sig], nlp[~sig], s=6, color="lightgray", alpha=0.6)
    ax.scatter(lfc[up], nlp[up], s=9, color=PALETTE[1], alpha=0.75, label="up")
    ax.scatter(lfc[down], nlp[down], s=9, color=PALETTE[0], alpha=0.75, label="down")
    for xv in (fc_thresh, -fc_thresh):
        ax.axvline(xv, ls="--", color="#bbb", lw=0.7)
    ax.axhline(-np.log10(p_thresh), ls="--", color="#bbb", lw=0.7)
    ax.set_xlabel(r"$\log_2$ fold change"); ax.set_ylabel(r"$-\log_{10}\,p$")
    ax.legend(loc="upper center", ncol=2)
    if top and labels is not None:
        for i in np.argsort(-(nlp * sig))[:top]:
            ax.annotate(labels[i], (lfc[i], nlp[i]), fontsize=7,
                        xytext=(3, 3), textcoords="offset points")
    return fig, ax


def manhattan(chrom, pos, pvals, *, genomewide=5e-8, suggestive=1e-5,
              labels=None, top=0, figsize=(6.4, 3.8), ax=None):
    """Manhattan plot for genome-wide association signals."""
    chrom = np.asarray(chrom)
    pos = np.asarray(pos, float)
    pv = np.asarray(pvals, float)
    if not (chrom.size == pos.size == pv.size):
        raise ValueError("chrom, pos, and pvals must have the same length")
    if chrom.size == 0:
        raise ValueError("manhattan requires at least one point")

    def _chrom_key(value):
        try:
            return (0, int(value))
        except (TypeError, ValueError):
            return (1, str(value))

    chroms = sorted(dict.fromkeys(chrom.tolist()), key=_chrom_key)
    x = np.zeros(chrom.size, dtype=float)
    ticks, ticklabels, offset = [], [], 0.0
    fig, ax = _fig(ax, figsize)

    for i, c in enumerate(chroms):
        idx = np.where(chrom == c)[0]
        idx = idx[np.argsort(pos[idx])]
        p = pos[idx]
        span = float(p.max() - p.min()) if p.size > 1 else 1.0
        gap = max(span * 0.03, 1.0)
        x[idx] = offset + (p - p.min())
        ticks.append(offset + span / 2)
        ticklabels.append(str(c))
        y = -np.log10(np.clip(pv[idx], 1e-300, 1.0))
        ax.scatter(x[idx], y, s=7, color=PALETTE[i % 2], alpha=0.72,
                   edgecolor="none")
        offset += span + gap

    y_all = -np.log10(np.clip(pv, 1e-300, 1.0))
    if suggestive is not None:
        ax.axhline(-np.log10(suggestive), color="#888", lw=0.7, ls=":",
                   label=f"suggestive {suggestive:g}")
    if genomewide is not None:
        ax.axhline(-np.log10(genomewide), color=PALETTE[1], lw=0.9, ls="--",
                   label=f"genome-wide {genomewide:g}")
    if labels is not None and top:
        labels = np.asarray(labels)
        for i in np.argsort(-y_all)[:top]:
            ax.annotate(str(labels[i]), (x[i], y_all[i]), fontsize=7,
                        xytext=(3, 3), textcoords="offset points")
    ax.set_xticks(ticks); ax.set_xticklabels(ticklabels)
    ax.set_xlabel("Chromosome"); ax.set_ylabel(r"$-\log_{10}\,p$")
    ax.set_xlim(x.min() - 1, x.max() + 1)
    ax.legend(loc="upper right", fontsize=7)
    return fig, ax


# ============================ medical ============================

def survival(groups, *, xlabel="Time", figsize=(5, 3.6), ax=None):
    """Kaplan-Meier survival curves. groups: {label: (times, events)},
    events 1 = event, 0 = censored. Censoring shown as tick marks."""
    fig, ax = _fig(ax, figsize)
    for i, (k, (t, e)) in enumerate(groups.items()):
        t = np.asarray(t, float); e = np.asarray(e, int)
        order = np.argsort(t); t, e = t[order], e[order]
        n = len(t); surv = 1.0; xs, ys = [0.0], [1.0]; cx, cy = [], []
        for j in range(n):
            at_risk = n - j
            if e[j] == 1:
                surv *= (1 - 1 / at_risk)
                xs += [t[j], t[j]]; ys += [ys[-1], surv]
            else:
                cx.append(t[j]); cy.append(surv)
        c = PALETTE[i % len(PALETTE)]
        ax.plot(xs, ys, color=c, lw=1.8, label=k)
        ax.scatter(cx, cy, marker="|", s=28, color=c, lw=1)
    ax.set_xlabel(xlabel); ax.set_ylabel("Survival probability")
    ax.set_ylim(0, 1.02); ax.legend()
    return fig, ax


def forest(labels, est, lo, hi, *, ref=0.0, xlabel="Effect size", figsize=None, ax=None):
    """Forest plot: point estimates + CI per row, with a reference line."""
    est = np.asarray(est, float); lo = np.asarray(lo, float); hi = np.asarray(hi, float)
    n = len(labels); fig, ax = _fig(ax, figsize or (5, max(2.4, 0.42 * n)))
    y = np.arange(n)[::-1]
    ax.errorbar(est, y, xerr=[est - lo, hi - est], fmt="s", color=PALETTE[0],
                ms=5, capsize=2.5, lw=1.1, ecolor="#555")
    ax.axvline(ref, ls="--", color="#888", lw=0.8)
    ax.set_yticks(y); ax.set_yticklabels(labels); ax.set_xlabel(xlabel)
    ax.set_ylim(-0.6, n - 0.4); ax.grid(axis="y", visible=False)
    return fig, ax


def bland_altman(method1, method2, *, figsize=(4.9, 3.5), ax=None):
    """Bland-Altman agreement plot: difference vs mean, with limits of agreement."""
    m1 = np.asarray(method1, float); m2 = np.asarray(method2, float)
    mean = (m1 + m2) / 2; diff = m1 - m2
    md, sd = diff.mean(), diff.std(ddof=1)
    fig, ax = _fig(ax, figsize)
    ax.scatter(mean, diff, s=12, color=PALETTE[0], alpha=0.6)
    for val, ls, lab in [(md, "-", "mean"), (md + 1.96 * sd, "--", "+1.96 SD"),
                         (md - 1.96 * sd, "--", "-1.96 SD")]:
        ax.axhline(val, ls=ls, color="#666", lw=0.9)
        ax.text(0.99, val, f" {lab}", transform=ax.get_yaxis_transform(),
                fontsize=7, va="center", ha="right")
    ax.set_xlabel("Mean of two methods"); ax.set_ylabel("Difference (method1 - method2)")
    return fig, ax


# ============================ physics / fields ============================

def contour_field(X, Y, Z, *, levels=12, cbar_label="value", xlabel="$x$",
                  ylabel="$y$", figsize=(4.9, 3.9), ax=None):
    """Filled contour field + contour lines + colorbar."""
    fig, ax = _fig(ax, figsize)
    cf = ax.contourf(X, Y, Z, levels=levels, cmap="viridis")
    ax.contour(X, Y, Z, levels=levels, colors="white", linewidths=0.4, alpha=0.5)
    fig.colorbar(cf, ax=ax, label=cbar_label)
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel); ax.grid(False)
    return fig, ax


def hexbin_density(x, y, *, xlabel="$x$", ylabel="$y$", gridsize=30,
                   figsize=(4.9, 3.9), ax=None):
    """2-D density via hexbin — for scatter too dense to read as points."""
    fig, ax = _fig(ax, figsize)
    hb = ax.hexbin(x, y, gridsize=gridsize, cmap="viridis", mincnt=1)
    fig.colorbar(hb, ax=ax, label="count")
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel); ax.grid(False)
    return fig, ax


def _grid_1d(X, Y):
    X = np.asarray(X, float)
    Y = np.asarray(Y, float)
    if X.ndim == 2 and Y.ndim == 2:
        return X[0, :], Y[:, 0]
    return X, Y


def streamplot_field(X, Y, U, V, *, density=1.15, color_by="speed",
                     cbar_label="speed", xlabel="$x$", ylabel="$y$",
                     figsize=(4.9, 3.9), ax=None):
    """Vector field streamplot, optionally colored by local speed."""
    U = np.asarray(U, float)
    V = np.asarray(V, float)
    speed = np.sqrt(U ** 2 + V ** 2)
    x, y = _grid_1d(X, Y)
    fig, ax = _fig(ax, figsize)
    if color_by == "speed":
        vmax = max(float(speed.max()), 1e-12)
        lw = 0.45 + 1.25 * speed / vmax
        sp = ax.streamplot(x, y, U, V, density=density, color=speed,
                           cmap="viridis", linewidth=lw)
        fig.colorbar(sp.lines, ax=ax, label=cbar_label)
    else:
        ax.streamplot(x, y, U, V, density=density, color=PALETTE[0],
                      linewidth=0.9)
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel); ax.grid(False)
    return fig, ax


def surface3d(X, Y, Z, *, cmap="viridis", cbar_label="value", xlabel="$x$",
              ylabel="$y$", zlabel="$z$", elev=28, azim=-55,
              figsize=(5.2, 4.3), ax=None):
    """3-D surface plot for scalar fields."""
    X = np.asarray(X, float); Y = np.asarray(Y, float); Z = np.asarray(Z, float)
    if ax is None:
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection="3d")
    else:
        fig = ax.figure
    surf = ax.plot_surface(X, Y, Z, cmap=cmap, linewidth=0, antialiased=True,
                           alpha=0.96)
    fig.colorbar(surf, ax=ax, shrink=0.68, pad=0.08, label=cbar_label)
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel); ax.set_zlabel(zlabel)
    ax.view_init(elev=elev, azim=azim)
    return fig, ax


# ============================ richer / multi-axes ============================

def jointplot(x, y, *, xlabel="$x$", ylabel="$y$", figsize=(4.7, 4.7)):
    """Scatter with marginal histograms (higher visual density). Returns (fig, axes)."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(2, 2, width_ratios=[4, 1], height_ratios=[1, 4],
                          hspace=0.06, wspace=0.06)
    ax = fig.add_subplot(gs[1, 0])
    axt = fig.add_subplot(gs[0, 0], sharex=ax)
    axr = fig.add_subplot(gs[1, 1], sharey=ax)
    ax.scatter(x, y, s=12, color=PALETTE[0], alpha=0.5, edgecolor="white", linewidth=0.2)
    axt.hist(x, bins=30, color=PALETTE[0], alpha=0.6)
    axr.hist(y, bins=30, orientation="horizontal", color=PALETTE[0], alpha=0.6)
    axt.axis("off"); axr.axis("off")
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    return fig, (ax, axt, axr)


def radar(groups, metrics, *, figsize=(4.7, 4.5)):
    """Radar / spider chart over a set of metrics. groups: {label: [values]}."""
    n = len(metrics)
    ang = np.linspace(0, 2 * np.pi, n, endpoint=False)
    ang = np.concatenate([ang, ang[:1]])
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, polar=True)
    for i, (k, v) in enumerate(groups.items()):
        v = np.concatenate([np.asarray(v, float), [v[0]]])
        c = PALETTE[i % len(PALETTE)]
        ax.plot(ang, v, color=c, lw=1.6, label=k)
        ax.fill(ang, v, color=c, alpha=0.12)
    ax.set_xticks(ang[:-1]); ax.set_xticklabels(metrics)
    ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.1))
    return fig, ax


def slopegraph(before, after, labels, *, left="Before", right="After",
               figsize=(4, 4.2), ax=None):
    """Paired before/after slope graph (a.k.a. slopegraph)."""
    fig, ax = _fig(ax, figsize)
    before = np.asarray(before, float); after = np.asarray(after, float)
    for i, (b, a, lab) in enumerate(zip(before, after, labels)):
        c = PALETTE[i % len(PALETTE)]
        ax.plot([0, 1], [b, a], color=c, marker="o", ms=4, lw=1.5)
        ax.text(-0.04, b, f"{lab}", ha="right", va="center", fontsize=8)
        ax.text(1.04, a, f"{a:.2g}", ha="left", va="center", fontsize=8)
    ax.set_xticks([0, 1]); ax.set_xticklabels([left, right])
    ax.set_xlim(-0.45, 1.45); ax.set_yticks([])
    ax.spines["left"].set_visible(False); ax.grid(False)
    return fig, ax


def sankey(flows, labels=None, *, orientations=None, unit="", fmt="%.2g",
           title=None, gap=0.42, pathlengths=0.68, trunklength=1.15,
           figsize=(5.2, 3.5), ax=None):
    """Single-node Sankey diagram. Positive flows enter; negative flows leave."""
    from matplotlib.sankey import Sankey

    vals = np.asarray(flows, float)
    if vals.size == 0 or not np.any(np.abs(vals) > 0):
        raise ValueError("sankey requires at least one non-zero flow")
    labs = list(labels) if labels is not None else [""] * vals.size
    if len(labs) != vals.size:
        raise ValueError("labels must match flows")
    if not np.isclose(vals.sum(), 0.0, rtol=1e-9, atol=1e-12):
        residual = -float(vals.sum())
        vals = np.concatenate([vals, [residual]])
        labs.append("loss" if residual < 0 else "balance")

    if orientations is None:
        orientations = [0] * vals.size
    else:
        orientations = list(orientations)
        if len(orientations) == len(vals) - 1:
            orientations.append(0)
        if len(orientations) != len(vals):
            raise ValueError("orientations must match balanced flows")

    fig, ax = _fig(ax, figsize)
    scale = 1.0 / max(float(np.max(np.abs(vals))), 1e-12)
    if np.isscalar(pathlengths):
        pathlengths = [float(pathlengths)] * vals.size
    sk = Sankey(ax=ax, unit=unit, format=fmt, scale=scale, gap=gap,
                radius=0.12, offset=0.18)
    sk.add(flows=vals, labels=labs, orientations=orientations,
           trunklength=trunklength, pathlengths=pathlengths,
           facecolor=PALETTE[0], edgecolor="#555", alpha=0.75)
    sk.finish()
    for txt in ax.texts:
        txt.set_fontsize(8)
    if title:
        ax.set_title(title)
    ax.axis("off")
    return fig, ax


# ============================ expanded coverage ============================

def histogram(groups, *, bins=30, density=False, xlabel="Value", ylabel=None,
              alpha=0.45, figsize=(5, 3.4), ax=None):
    """Histogram, overlaid for groups when a dict is supplied."""
    groups = _as_groups(groups)
    fig, ax = _fig(ax, figsize)
    for i, (k, v) in enumerate(groups.items()):
        ax.hist(np.asarray(v, float), bins=bins, density=density, alpha=alpha,
                color=PALETTE[i % len(PALETTE)], edgecolor="white",
                linewidth=0.35, label=k or None)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel or ("Density" if density else "Count"))
    if any(groups):
        ax.legend()
    return fig, ax


def bubble(x, y, size, *, color=None, labels=None, xlabel="$x$", ylabel="$y$",
           size_label=None, cbar_label="value", figsize=(4.9, 3.7), ax=None):
    """Bubble chart: scatter with area encoding for a third variable."""
    x = np.asarray(x, float); y = np.asarray(y, float); s = np.asarray(size, float)
    s_norm = (s - s.min()) / (np.ptp(s) + 1e-12)
    areas = 28 + 520 * s_norm
    fig, ax = _fig(ax, figsize)
    if color is None:
        sc = ax.scatter(x, y, s=areas, color=PALETTE[0], alpha=0.55,
                        edgecolor="white", linewidth=0.5)
    else:
        sc = ax.scatter(x, y, s=areas, c=np.asarray(color, float), cmap="viridis",
                        alpha=0.65, edgecolor="white", linewidth=0.5)
        fig.colorbar(sc, ax=ax, label=cbar_label)
    if labels is not None:
        for xi, yi, lab in zip(x, y, labels):
            ax.annotate(str(lab), (xi, yi), fontsize=7, xytext=(3, 3),
                        textcoords="offset points")
    if size_label:
        ax.text(0.02, 0.98, size_label, transform=ax.transAxes, va="top", fontsize=8)
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    return fig, ax


def pr_curve(y_true, y_score, *, label=None, figsize=(4.2, 3.9), ax=None):
    """Precision-recall curve with average precision (binary labels + scores)."""
    yt = np.asarray(y_true).astype(int)
    order = np.argsort(-np.asarray(y_score, float))
    yt = yt[order]
    tp = np.cumsum(yt)
    fp = np.cumsum(1 - yt)
    recall = tp / max(int(yt.sum()), 1)
    precision = tp / np.maximum(tp + fp, 1)
    recall = np.concatenate([[0.0], recall])
    precision = np.concatenate([[1.0], precision])
    ap = float(np.sum(np.diff(recall) * precision[1:]))
    fig, ax = _fig(ax, figsize)
    lab = (f"{label} " if label else "") + f"AP = {ap:.3f}"
    ax.step(recall, precision, where="post", color=PALETTE[0], lw=2, label=lab)
    ax.set_xlabel("Recall"); ax.set_ylabel("Precision")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1.02); ax.legend(loc="lower left")
    return fig, ax


def feature_importance(names, values, *, err=None, top=None,
                       xlabel="Importance", figsize=None, ax=None):
    """Sorted horizontal feature-importance plot, with optional uncertainty."""
    names = np.asarray(names)
    vals = np.asarray(values, float)
    order = np.argsort(vals)
    if top is not None:
        order = order[-int(top):]
    names, vals = names[order], vals[order]
    err_vals = None if err is None else np.asarray(err, float)[order]
    fig, ax = _fig(ax, figsize or (5, max(2.4, 0.3 * len(vals))))
    ax.barh(np.arange(len(vals)), vals, xerr=err_vals, color=PALETTE[0],
            alpha=0.72, edgecolor="white", linewidth=0.4,
            error_kw=dict(ecolor="#444", lw=0.9, capsize=2))
    ax.set_yticks(np.arange(len(vals))); ax.set_yticklabels(names)
    ax.set_xlabel(xlabel)
    return fig, ax


def convergence_curve(history, *, x=None, xlabel="Epoch", ylabel="Metric",
                      figsize=(5.4, 3.4), ax=None):
    """Training convergence curves for loss, accuracy, or validation metrics."""
    hist = history if isinstance(history, dict) else {"metric": history}
    fig, ax = _fig(ax, figsize)
    for i, (k, vals) in enumerate(hist.items()):
        vals = np.asarray(vals, float)
        xx = np.arange(1, len(vals) + 1) if x is None else np.asarray(x, float)
        ax.plot(xx, vals, color=PALETTE[i % len(PALETTE)], lw=1.8, label=k)
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel); ax.legend()
    return fig, ax


def embedding_scatter(xy, labels=None, *, xlabel="Dim 1", ylabel="Dim 2",
                      title_labels=True, figsize=(4.8, 3.9), ax=None):
    """2-D embedding scatter for t-SNE / UMAP / PCA coordinates."""
    xy = np.asarray(xy, float)
    fig, ax = _fig(ax, figsize)
    if labels is None:
        ax.scatter(xy[:, 0], xy[:, 1], s=14, color=PALETTE[0], alpha=0.62,
                   edgecolor="white", linewidth=0.25)
    else:
        labs = np.asarray(labels)
        for i, lab in enumerate(dict.fromkeys(labs.tolist())):
            m = labs == lab
            c = PALETTE[i % len(PALETTE)]
            ax.scatter(xy[m, 0], xy[m, 1], s=14, color=c, alpha=0.62,
                       edgecolor="white", linewidth=0.25, label=str(lab))
            if title_labels:
                cen = xy[m].mean(axis=0)
                ax.text(cen[0], cen[1], str(lab), fontsize=8, weight="bold",
                        ha="center", va="center")
        ax.legend(loc="best", fontsize=7)
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    return fig, ax


def attention_map(attn, *, row_labels=None, col_labels=None, cmap="magma",
                  cbar_label="attention", annot=False, figsize=(4.8, 4.0), ax=None):
    """Attention heatmap for transformer or alignment weights."""
    A = np.asarray(attn, float)
    fig, ax = _fig(ax, figsize)
    im = ax.imshow(A, cmap=cmap, vmin=0, vmax=max(float(np.nanmax(A)), 1e-12),
                   aspect="auto")
    fig.colorbar(im, ax=ax, label=cbar_label)
    ax.set_xticks(np.arange(A.shape[1])); ax.set_yticks(np.arange(A.shape[0]))
    if col_labels is not None:
        ax.set_xticklabels(col_labels, rotation=45, ha="right")
    if row_labels is not None:
        ax.set_yticklabels(row_labels)
    if annot and A.size <= 100:
        for i in range(A.shape[0]):
            for j in range(A.shape[1]):
                ax.text(j, i, f"{A[i, j]:.2f}", ha="center", va="center",
                        fontsize=7, color="white")
    ax.grid(False)
    return fig, ax


def trajectory(x, y, *, t=None, xlabel="$x$", ylabel="$y$", cbar_label="time",
               figsize=(4.9, 3.8), ax=None):
    """2-D trajectory plot with start/end markers and optional time coloring."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    fig, ax = _fig(ax, figsize)
    ax.plot(x, y, color="#777", lw=0.9, alpha=0.65, zorder=1)
    if t is None:
        ax.scatter(x, y, s=10, color=PALETTE[0], alpha=0.55, zorder=2)
    else:
        sc = ax.scatter(x, y, c=np.asarray(t, float), s=12, cmap="viridis",
                        alpha=0.8, zorder=2)
        fig.colorbar(sc, ax=ax, label=cbar_label)
    ax.scatter([x[0]], [y[0]], marker="o", s=42, color=PALETTE[2],
               edgecolor="white", linewidth=0.6, label="start", zorder=3)
    ax.scatter([x[-1]], [y[-1]], marker="s", s=42, color=PALETTE[1],
               edgecolor="white", linewidth=0.6, label="end", zorder=3)
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel); ax.legend(loc="best")
    return fig, ax


def spectrum(x, intensity, *, peaks=None, top=0, xlabel="m/z",
             ylabel="Intensity", fill=True, figsize=(5.4, 3.3), ax=None):
    """Spectrum / chromatogram line plot with optional peak annotation."""
    x = np.asarray(x, float); y = np.asarray(intensity, float)
    fig, ax = _fig(ax, figsize)
    ax.plot(x, y, color=PALETTE[0], lw=1.4)
    if fill:
        ax.fill_between(x, 0, y, color=PALETTE[0], alpha=0.16)
    if peaks is None and top:
        local = np.where((y[1:-1] >= y[:-2]) & (y[1:-1] >= y[2:]))[0] + 1
        if local.size == 0:
            local = np.arange(y.size)
        keep = []
        min_sep = max(1, y.size // 20)
        for idx in local[np.argsort(-y[local])]:
            if all(abs(idx - j) >= min_sep for j in keep):
                keep.append(int(idx))
            if len(keep) >= int(top):
                break
        peaks = np.asarray(sorted(keep), int)
    if peaks is not None:
        idx = np.asarray(peaks, int)
        ax.scatter(x[idx], y[idx], s=18, color=PALETTE[1], zorder=3)
        for i in idx:
            ax.annotate(f"{x[i]:.3g}", (x[i], y[i]), fontsize=7,
                        xytext=(0, 5), textcoords="offset points", ha="center")
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    return fig, ax


def ternary(a, b, c, *, values=None, labels=("A", "B", "C"),
            cbar_label="value", figsize=(4.8, 4.2), ax=None):
    """Ternary composition scatter for three-part mixtures."""
    a = np.asarray(a, float); b = np.asarray(b, float); c = np.asarray(c, float)
    total = np.maximum(a + b + c, 1e-12)
    a, b, c = a / total, b / total, c / total
    x = b + 0.5 * c
    y = np.sqrt(3) / 2 * c
    fig, ax = _fig(ax, figsize)
    tri = np.array([[0, 0], [1, 0], [0.5, np.sqrt(3) / 2], [0, 0]])
    ax.plot(tri[:, 0], tri[:, 1], color="#333", lw=1)
    for g in np.linspace(0.2, 0.8, 4):
        ax.plot([g, 0.5 + 0.5 * g], [0, np.sqrt(3) / 2 * (1 - g)],
                color="#ddd", lw=0.6)
        ax.plot([1 - g, 0.5 * (1 - g)], [0, np.sqrt(3) / 2 * (1 - g)],
                color="#ddd", lw=0.6)
        ax.plot([0.5 * g, 1 - 0.5 * g], [np.sqrt(3) / 2 * g] * 2,
                color="#ddd", lw=0.6)
    if values is None:
        ax.scatter(x, y, s=18, color=PALETTE[0], alpha=0.65,
                   edgecolor="white", linewidth=0.35)
    else:
        sc = ax.scatter(x, y, c=np.asarray(values, float), cmap="viridis",
                        s=20, alpha=0.75, edgecolor="white", linewidth=0.35)
        fig.colorbar(sc, ax=ax, label=cbar_label, fraction=0.046, pad=0.04)
    ax.text(-0.04, -0.04, labels[0], ha="right", va="top")
    ax.text(1.04, -0.04, labels[1], ha="left", va="top")
    ax.text(0.5, np.sqrt(3) / 2 + 0.05, labels[2], ha="center", va="bottom")
    ax.set_aspect("equal"); ax.axis("off")
    return fig, ax


def venn2(counts, *, labels=("A", "B"), figsize=(4.3, 3.4), ax=None):
    """Two-set Venn diagram. counts=(A only, B only, overlap)."""
    from matplotlib.patches import Circle
    a_only, b_only, both = counts
    fig, ax = _fig(ax, figsize)
    ca = Circle((-0.35, 0), 0.72, facecolor=PALETTE[0], alpha=0.34,
                edgecolor=PALETTE[0], lw=1.2)
    cb = Circle((0.35, 0), 0.72, facecolor=PALETTE[1], alpha=0.34,
                edgecolor=PALETTE[1], lw=1.2)
    ax.add_patch(ca); ax.add_patch(cb)
    ax.text(-0.72, 0, str(a_only), ha="center", va="center", fontsize=11)
    ax.text(0, 0, str(both), ha="center", va="center", fontsize=11, weight="bold")
    ax.text(0.72, 0, str(b_only), ha="center", va="center", fontsize=11)
    ax.text(-0.52, 0.78, labels[0], ha="center", fontsize=9)
    ax.text(0.52, 0.78, labels[1], ha="center", fontsize=9)
    ax.set_xlim(-1.25, 1.25); ax.set_ylim(-0.95, 1.05)
    ax.set_aspect("equal"); ax.axis("off")
    return fig, ax


def network_graph(edges, *, nodes=None, pos=None, directed=False, labels=True,
                  figsize=(4.8, 4.2), ax=None):
    """Network topology plot with deterministic circular layout by default."""
    fig, ax = _fig(ax, figsize)
    if nodes is None:
        nodes = sorted({u for e in edges for u in e[:2]} | {v for e in edges for v in e[:2]})
    nodes = list(nodes)
    if pos is None:
        ang = np.linspace(0, 2 * np.pi, len(nodes), endpoint=False)
        pos = {n: np.array([np.cos(a), np.sin(a)]) for n, a in zip(nodes, ang)}
    degree = {n: 0 for n in nodes}
    for e in edges:
        degree[e[0]] += 1; degree[e[1]] += 1
    for e in edges:
        u, v = e[:2]
        w = float(e[2]) if len(e) > 2 else 1.0
        p, q = pos[u], pos[v]
        if directed:
            ax.annotate("", xy=q, xytext=p,
                        arrowprops=dict(arrowstyle="-|>", lw=0.55 + 0.45 * w,
                                        color="#666", shrinkA=13, shrinkB=13,
                                        alpha=0.72))
        else:
            ax.plot([p[0], q[0]], [p[1], q[1]], color="#666",
                    lw=0.55 + 0.45 * w, alpha=0.65, zorder=1)
    for i, n in enumerate(nodes):
        p = pos[n]
        ax.scatter([p[0]], [p[1]], s=110 + 35 * degree[n],
                   color=PALETTE[i % len(PALETTE)], edgecolor="white",
                   linewidth=0.8, zorder=3)
        if labels:
            ax.text(p[0], p[1], str(n), ha="center", va="center",
                    fontsize=8, color="white", weight="bold", zorder=4)
    ax.set_aspect("equal"); ax.axis("off")
    return fig, ax


def dendrogram(data, *, labels=None, is_linkage=False, ylabel="Distance",
               figsize=None, ax=None):
    """Dendrogram from data matrix or a scipy-like linkage matrix."""
    Z = np.asarray(data, float) if is_linkage else _average_linkage(np.asarray(data, float))
    n = Z.shape[0] + 1
    labs = [str(i) for i in range(n)] if labels is None else list(labels)
    fig, ax = _fig(ax, figsize or (max(4.8, 0.36 * n), 3.4))
    pos = {i: (float(i), 0.0) for i in range(n)}
    for r, (a, b, h, _) in enumerate(Z):
        a, b = int(a), int(b)
        x1, y1 = pos[a]; x2, y2 = pos[b]
        ax.plot([x1, x1, x2, x2], [y1, h, h, y2], color=PALETTE[0], lw=1.1)
        pos[n + r] = ((x1 + x2) / 2, float(h))
    ax.set_xticks(range(n)); ax.set_xticklabels(labs, rotation=45, ha="right")
    ax.set_ylabel(ylabel); ax.grid(axis="x", visible=False)
    return fig, ax


def chord(matrix, *, labels=None, figsize=(4.8, 4.4), ax=None):
    """Chord diagram for symmetric flow/association matrices."""
    from matplotlib.path import Path
    from matplotlib.patches import PathPatch
    M = np.asarray(matrix, float)
    n = M.shape[0]
    labs = [str(i) for i in range(n)] if labels is None else list(labels)
    fig, ax = _fig(ax, figsize)
    ang = np.linspace(0, 2 * np.pi, n, endpoint=False) + np.pi / 2
    pts = np.c_[np.cos(ang), np.sin(ang)]
    vmax = max(float(np.nanmax(M)), 1e-12)
    for i in range(n):
        for j in range(i + 1, n):
            w = M[i, j] + M[j, i]
            if w <= 0:
                continue
            path = Path([pts[i], [0, 0], pts[j]], [Path.MOVETO, Path.CURVE3, Path.CURVE3])
            ax.add_patch(PathPatch(path, facecolor="none", edgecolor=PALETTE[i % len(PALETTE)],
                                   lw=0.5 + 4.5 * w / vmax, alpha=0.35))
    node_w = M.sum(axis=0) + M.sum(axis=1)
    sizes = 80 + 280 * node_w / max(float(node_w.max()), 1e-12)
    ax.scatter(pts[:, 0], pts[:, 1], s=sizes,
               color=[PALETTE[i % len(PALETTE)] for i in range(n)],
               edgecolor="white", linewidth=0.8, zorder=3)
    for p, lab in zip(pts, labs):
        ax.text(p[0] * 1.16, p[1] * 1.16, lab, ha="center", va="center", fontsize=8)
    ax.set_aspect("equal"); ax.axis("off")
    return fig, ax


def image_panel(images, *, titles=None, cmaps=None, scalebars=None,
                cols=None, figsize=None):
    """Image plate for microscopy/medical/remote-sensing panels with scalebars.

    scalebars: optional list of (length_px, label) entries, one per image.
    """
    imgs = [np.asarray(im) for im in images]
    n = len(imgs); cols = cols or min(3, n); rows = int(np.ceil(n / cols))
    fig, axes = plt.subplots(rows, cols, figsize=figsize or (3.0 * cols, 2.6 * rows))
    axes = np.atleast_1d(axes).ravel()
    cmaps = [None] * n if cmaps is None else cmaps
    scalebars = [None] * n if scalebars is None else scalebars
    for i, (ax, im) in enumerate(zip(axes, imgs)):
        ax.imshow(im, cmap=cmaps[i])
        if titles is not None:
            ax.set_title(titles[i], fontsize=9)
        sb = scalebars[i]
        if sb is not None:
            length, label = sb
            h, w = im.shape[:2]
            x0 = w * 0.72; y0 = h * 0.88
            ax.plot([x0, x0 + length], [y0, y0], color="white", lw=2.4,
                    solid_capstyle="butt")
            ax.text(x0 + length / 2, y0 - h * 0.04, label, color="white",
                    ha="center", va="bottom", fontsize=8)
        ax.set_axis_off()
    for ax in axes[n:]:
        ax.set_axis_off()
    fig.tight_layout()
    return fig, axes[:n]


def _average_linkage(X):
    """Small average-linkage clustering helper for dendrogram(), numpy-only."""
    n = X.shape[0]
    D = np.sqrt(((X[:, None, :] - X[None, :, :]) ** 2).sum(axis=2))
    clusters = {i: [i] for i in range(n)}
    active = list(range(n))
    rows = []
    next_id = n
    while len(active) > 1:
        best = None
        for ai, a in enumerate(active[:-1]):
            for b in active[ai + 1:]:
                d = float(D[np.ix_(clusters[a], clusters[b])].mean())
                if best is None or d < best[0]:
                    best = (d, a, b)
        d, a, b = best
        merged = clusters[a] + clusters[b]
        rows.append([a, b, d, len(merged)])
        active = [x for x in active if x not in (a, b)] + [next_id]
        clusters[next_id] = merged
        next_id += 1
    return np.asarray(rows, float)
