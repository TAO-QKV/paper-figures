"""paperfig — a publication-grade figure toolkit for scientific papers.

    from paperfig import paper_style, save, timeseries_ci
    paper_style(font="sans")
    fig, ax = timeseries_ci(t, y_obs, y_hat, lo, hi)
    save(fig, "fig1_main_result")   # PDF + PNG + SVG

The opinionated guidance (the §0b quality bar, §I composition paradigms,
§J craft spec, §K original TikZ) lives in
``.claude/skills/paper-figure-generation/references/figure-cookbook.md``.
"""
from .style import paper_style, save, PALETTE, MARKERS, LINESTYLES
from .archetypes import (
    timeseries_ci, sorted_bar, grouped_bar, residual_diag, heatmap,
    scatter_fit, pareto, tornado, confusion, phase_portrait, alignment_scatter,
)

__version__ = "0.1.0"
__all__ = [
    "paper_style", "save", "PALETTE", "MARKERS", "LINESTYLES",
    "timeseries_ci", "sorted_bar", "grouped_bar", "residual_diag", "heatmap",
    "scatter_fit", "pareto", "tornado", "confusion", "phase_portrait",
    "alignment_scatter",
]
