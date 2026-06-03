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
