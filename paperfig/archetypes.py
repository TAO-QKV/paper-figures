"""Callable archetype figures — the A1-A10 templates as functions.

Every function returns ``(fig, ax)`` so you can tweak and then ``save(fig, name)``.
Call ``paper_style(...)`` once before using these. Data comes in as arrays or
1-D sequences; nothing is plotted from inline literals.

    from paperfig import paper_style, save, timeseries_ci
    paper_style()
    fig, ax = timeseries_ci(t, y_obs, y_hat, lo, hi, ylabel="Signal $y$")
    save(fig, "fig1_timeseries")
"""
from __future__ import annotations
import numpy as np
import matplotlib.pyplot as plt
from .style import PALETTE


def timeseries_ci(t, y_obs=None, y_hat=None, lo=None, hi=None, *,
                  xlabel="Time $t$", ylabel="Value $y$",
                  obs_label="Observations", fit_label="Fit", ci_label="95% CI",
                  figsize=(6.4, 3.4), ax=None):
    """A1 — time series / fitted curve with a confidence band."""
    fig, ax = _fig(ax, figsize)
    if lo is not None and hi is not None:
        ax.fill_between(t, lo, hi, color=PALETTE[1], alpha=0.18, zorder=1, label=ci_label)
    if y_hat is not None:
        ax.plot(t, y_hat, color=PALETTE[1], lw=2, zorder=3, label=fit_label)
    if y_obs is not None:
        ax.scatter(t, y_obs, s=14, color=PALETTE[0], alpha=0.5, edgecolor="white",
                   linewidth=0.3, zorder=2, label=obs_label)
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel); ax.legend()
    return fig, ax


def sorted_bar(names, values, *, xlabel="Value", fmt="{:.2f}",
               figsize=None, ax=None):
    """A2 — horizontal bar sorted by value (ranking)."""
    order = np.argsort(values)
    names = np.asarray(names)[order]; values = np.asarray(values)[order]
    fig, ax = _fig(ax, figsize or (5, max(2.4, 0.26 * len(values))))
    ax.barh(range(len(values)), values, color=PALETTE[0], edgecolor="white", linewidth=0.5)
    ax.set_yticks(range(len(values))); ax.set_yticklabels(names)
    for i, v in enumerate(values):
        ax.text(v, i, " " + fmt.format(v), va="center", fontsize=8)
    ax.set_xlabel(xlabel)
    return fig, ax


def grouped_bar(group_labels, metrics: dict, *, ylabel="Value",
                figsize=(6, 3.3), ax=None):
    """A3 — grouped bars for multi-series comparison.

    metrics: {series_name: [values per group]}.
    """
    fig, ax = _fig(ax, figsize)
    keys = list(metrics); n = len(keys); x = np.arange(len(group_labels))
    w = 0.8 / n
    for i, k in enumerate(keys):
        ax.bar(x + (i - (n - 1) / 2) * w, metrics[k], w, label=k,
               color=PALETTE[i % len(PALETTE)], edgecolor="white", lw=0.4)
    ax.set_xticks(x); ax.set_xticklabels(group_labels)
    ax.set_ylabel(ylabel); ax.legend(ncol=min(n, 3))
    return fig, ax


def residual_diag(y_hat, resid, *, figsize=(7, 3), ax=None):
    """A4 — residual scatter + histogram (model diagnostic)."""
    if ax is not None:
        raise ValueError("residual_diag creates its own 2-panel figure")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    ax1.scatter(y_hat, resid, s=10, color=PALETTE[0], alpha=0.6)
    ax1.axhline(0, color="k", lw=0.6, ls="--")
    ax1.set_xlabel(r"Fitted $\hat y$"); ax1.set_ylabel("Residual $e$")
    ax2.hist(resid, bins=30, color=PALETTE[0], edgecolor="white")
    ax2.set_xlabel("Residual"); ax2.set_ylabel("Count")
    fig.tight_layout()
    return fig, (ax1, ax2)


def heatmap(matrix, *, row_labels=None, col_labels=None, cmap="RdBu_r",
            center=0.0, cbar_label="value", annot=True, fmt=".2f",
            xlabel="", ylabel="", figsize=(5.2, 4.2), ax=None):
    """A5 — annotated heatmap (correlation / sensitivity / matrix)."""
    fig, ax = _fig(ax, figsize)
    M = np.asarray(matrix, dtype=float)
    vlim = np.nanmax(np.abs(M - (center or 0))) + (center or 0)
    im = ax.imshow(M, cmap=cmap, vmin=(2 * (center or 0) - vlim) if center is not None else None,
                   vmax=vlim if center is not None else None, aspect="auto")
    ax.set_xticks(range(M.shape[1])); ax.set_yticks(range(M.shape[0]))
    if col_labels is not None: ax.set_xticklabels(col_labels, rotation=45, ha="right")
    if row_labels is not None: ax.set_yticklabels(row_labels)
    if annot:
        for i in range(M.shape[0]):
            for j in range(M.shape[1]):
                ax.text(j, i, format(M[i, j], fmt), ha="center", va="center",
                        fontsize=8, color="#222")
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04); cb.set_label(cbar_label)
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    ax.grid(False)
    return fig, ax


def scatter_fit(x, y, *, xlabel="$x$", ylabel="$y$", degree=1,
                obs_label="Observations", figsize=(4.8, 3.4), ax=None):
    """A6 — scatter with a least-squares polynomial fit + 95% CI band."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    fig, ax = _fig(ax, figsize)
    coef, cov = np.polyfit(x, y, degree, cov=True)
    xs = np.linspace(x.min(), x.max(), 200)
    V = np.vander(xs, degree + 1)
    yh = V @ coef
    se = np.sqrt(np.einsum("ij,jk,ik->i", V, cov, V))
    ax.fill_between(xs, yh - 1.96 * se, yh + 1.96 * se, color=PALETTE[1],
                    alpha=0.18, zorder=1, label="95% CI")
    ax.scatter(x, y, s=12, color=PALETTE[0], alpha=0.55, edgecolor="white",
               linewidth=0.3, zorder=2, label=obs_label)
    lab = "Fit" if degree > 1 else f"$y={coef[0]:.3g}x+{coef[1]:.3g}$"
    ax.plot(xs, yh, color=PALETTE[1], lw=2, zorder=3, label=lab)
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel); ax.legend()
    return fig, ax


def pareto(obj1, obj2, is_pareto, *, xlabel="Objective 1", ylabel="Objective 2",
           figsize=(4.8, 3.6), ax=None):
    """A7 — Pareto frontier over a dominated cloud."""
    obj1 = np.asarray(obj1, float); obj2 = np.asarray(obj2, float)
    m = np.asarray(is_pareto, bool)
    fig, ax = _fig(ax, figsize)
    ax.scatter(obj1[~m], obj2[~m], s=8, color="lightgray", label="Dominated")
    order = np.argsort(obj1[m])
    ax.plot(obj1[m][order], obj2[m][order], "o-", color=PALETTE[1], ms=4,
            label="Pareto frontier")
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel); ax.legend()
    return fig, ax


def tornado(params, low, high, base, *, xlabel="Objective value",
            figsize=None, ax=None):
    """A8 — tornado / one-at-a-time sensitivity ranking."""
    params = np.asarray(params); low = np.asarray(low, float); high = np.asarray(high, float)
    base = float(base)
    span = np.abs(high - low); order = np.argsort(span)
    params, low, high = params[order], low[order], high[order]
    fig, ax = _fig(ax, figsize or (5.2, max(2.4, 0.34 * len(params))))
    y = np.arange(len(params))
    ax.barh(y, high - base, left=base, color=PALETTE[0], label="+ perturbation")
    ax.barh(y, low - base, left=base, color=PALETTE[1], label="- perturbation")
    ax.set_yticks(y); ax.set_yticklabels(params)
    ax.axvline(base, color="k", lw=0.6, ls="--")
    ax.set_xlabel(xlabel); ax.legend()
    return fig, ax


def confusion(cm, labels=None, *, figsize=(3.8, 3.4), ax=None):
    """A9 — confusion matrix (counts), blue colormap."""
    cm = np.asarray(cm)
    fig, ax = _fig(ax, figsize)
    im = ax.imshow(cm, cmap="Blues", aspect="auto")
    n = cm.shape[0]
    ax.set_xticks(range(n)); ax.set_yticks(range(n))
    if labels is not None:
        ax.set_xticklabels(labels); ax.set_yticklabels(labels)
    thr = cm.max() / 2
    for i in range(n):
        for j in range(cm.shape[1]):
            ax.text(j, i, int(cm[i, j]), ha="center", va="center", fontsize=9,
                    color="white" if cm[i, j] > thr else "#222")
    ax.set_xlabel("Predicted"); ax.set_ylabel("True"); ax.grid(False)
    return fig, ax


def phase_portrait(f, xlim=(-4, 4), ylim=(-2.5, 2.5), *, n=(9, 5), t_max=20,
                   xlabel="$x$", ylabel=r"$\dot x$", figsize=(4.6, 3.8), ax=None):
    """A10 — phase portrait of a 2-D ODE ``f(t, [x, y]) -> [dx, dy]``."""
    from scipy.integrate import solve_ivp  # optional dep, only here
    fig, ax = _fig(ax, figsize)
    for x0 in np.linspace(xlim[0] * 0.75, xlim[1] * 0.75, n[0]):
        for y0 in np.linspace(ylim[0] * 0.8, ylim[1] * 0.8, n[1]):
            sol = solve_ivp(f, [0, t_max], [x0, y0], max_step=0.05)
            ax.plot(sol.y[0], sol.y[1], color=PALETTE[0], lw=0.5, alpha=0.6)
    ax.set_xlim(*xlim); ax.set_ylim(*ylim)
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    return fig, ax


def alignment_scatter(source_xy, target_xy, aligned_target_xy=None, *,
                      metric_before=None, metric_after=None,
                      xlabel="Dim 1", ylabel="Dim 2", figsize=(7, 3.3)):
    """§I P5 — source/target distribution alignment motif (before vs after).

    Each ``*_xy`` is an (N, 2) array. The differentiator figure for transfer /
    domain-adaptation / batch-effect papers.
    """
    if aligned_target_xy is None:
        fig, ax = plt.subplots(figsize=(figsize[0] / 2, figsize[1]))
        axes = [ax]
        panels = [(target_xy, "Target")]
    else:
        fig, axes = plt.subplots(1, 2, figsize=figsize)
        panels = [(target_xy, f"Before (MMD {metric_before})" if metric_before else "Before"),
                  (aligned_target_xy, f"After (MMD {metric_after})" if metric_after else "After")]
    s_xy = np.asarray(source_xy)
    for ax, (t_xy, title) in zip(np.atleast_1d(axes), panels):
        t_xy = np.asarray(t_xy)
        ax.scatter(s_xy[:, 0], s_xy[:, 1], s=12, color=PALETTE[0], alpha=0.5,
                   edgecolor="white", linewidth=0.2, label="Source")
        ax.scatter(t_xy[:, 0], t_xy[:, 1], s=12, color=PALETTE[1], alpha=0.5,
                   edgecolor="white", linewidth=0.2, label="Target")
        ax.set_title(title, fontsize=9); ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    np.atleast_1d(axes)[0].legend(loc="best")
    fig.tight_layout()
    return fig, axes


def violin(groups: dict, *, ylabel="Value", showmeans=True,
           figsize=(5.6, 3.4), ax=None):
    """Modern distribution comparison — violins with medians/means.

    groups: {label: 1-D values}. (Popular in current bio/ML papers.)
    """
    fig, ax = _fig(ax, figsize)
    labels = list(groups); data = [np.asarray(groups[k], float) for k in labels]
    vp = ax.violinplot(data, showmeans=showmeans, showextrema=False)
    for i, b in enumerate(vp["bodies"]):
        b.set_facecolor(PALETTE[i % len(PALETTE)]); b.set_alpha(0.45)
        b.set_edgecolor(PALETTE[i % len(PALETTE)])
    if showmeans and "cmeans" in vp:
        vp["cmeans"].set_color("#222"); vp["cmeans"].set_linewidth(1.2)
    ax.set_xticks(range(1, len(labels) + 1)); ax.set_xticklabels(labels)
    ax.set_ylabel(ylabel)
    return fig, ax


def raincloud(groups: dict, *, ylabel="Value", figsize=(5.8, 3.6), ax=None):
    """Raincloud plot: half-violin (cloud) + jittered points (rain) + box.

    groups: {label: 1-D values}. The de-facto modern distribution figure.
    """
    fig, ax = _fig(ax, figsize)
    labels = list(groups)
    rng = np.random.default_rng(0)
    for i, k in enumerate(labels):
        v = np.asarray(groups[k], float)
        c = PALETTE[i % len(PALETTE)]
        xs, dens = _kde(v)
        dens = dens / dens.max() * 0.36
        ax.fill_betweenx(xs, i, i + dens, color=c, alpha=0.4, lw=0)   # cloud (right)
        ax.scatter(i - 0.18 + rng.uniform(-0.06, 0.06, v.size), v, s=6,
                   color=c, alpha=0.5, edgecolor="none")               # rain (left)
        bp = ax.boxplot(v, positions=[i - 0.02], widths=0.06, vert=True,
                        patch_artist=True, showfliers=False,
                        medianprops=dict(color="#222"))
        for box in bp["boxes"]:
            box.set(facecolor="white", edgecolor=c, alpha=0.9)
    ax.set_xticks(range(len(labels))); ax.set_xticklabels(labels)
    ax.set_ylabel(ylabel); ax.grid(axis="x", visible=False)
    return fig, ax


def ridgeline(groups: dict, *, xlabel="Value", overlap=0.7, figsize=(5.6, 4.2), ax=None):
    """Ridgeline / joyplot: stacked offset densities (one row per group)."""
    fig, ax = _fig(ax, figsize)
    labels = list(groups); n = len(labels)
    allv = np.concatenate([np.asarray(groups[k], float) for k in labels])
    grid = np.linspace(allv.min(), allv.max(), 200)
    for i, k in enumerate(reversed(labels)):
        v = np.asarray(groups[k], float)
        _, dens = _kde(v, grid=grid)
        dens = dens / dens.max()
        base = i * (1 - overlap)
        c = PALETTE[(n - 1 - i) % len(PALETTE)]
        ax.fill_between(grid, base, base + dens, color=c, alpha=0.55, lw=0.8,
                        edgecolor="white", zorder=n - i)
        ax.text(grid[0], base + 0.05, list(reversed(labels))[i], fontsize=8, va="bottom")
    ax.set_yticks([]); ax.set_xlabel(xlabel); ax.grid(axis="y", visible=False)
    ax.spines["left"].set_visible(False)
    return fig, ax


def _kde(v, grid=None, n=200):
    """Tiny Gaussian KDE (Silverman bandwidth), numpy-only (no scipy)."""
    v = np.asarray(v, float)
    if grid is None:
        pad = 0.1 * (v.max() - v.min() + 1e-9)
        grid = np.linspace(v.min() - pad, v.max() + pad, n)
    sigma = v.std(ddof=1) if v.size > 1 else 1.0
    h = 1.06 * sigma * v.size ** (-1 / 5) + 1e-9          # Silverman's rule
    u = (grid[:, None] - v[None, :]) / h
    dens = np.exp(-0.5 * u ** 2).sum(axis=1) / (v.size * h * np.sqrt(2 * np.pi))
    return grid, dens


def _fig(ax, figsize):
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure
    return fig, ax
