"""paperfig — a publication-grade figure toolkit for scientific papers.

    from paperfig import paper_style, save, timeseries_ci
    paper_style(font="sans")
    fig, ax = timeseries_ci(t, y_obs, y_hat, lo, hi)
    save(fig, "fig1_main_result")   # PDF + PNG + SVG

The opinionated guidance (the §0b quality bar, §I composition paradigms,
§J craft spec, §K original TikZ) lives in
``.claude/skills/paper-figure-generation/references/figure-cookbook.md``.
"""
from .style import (
    paper_style, save, register_style, STYLE_PATH,
    PALETTE, MARKERS, LINESTYLES,
)
from .archetypes import (
    timeseries_ci, sorted_bar, grouped_bar, residual_diag, heatmap,
    scatter_fit, pareto, tornado, confusion, phase_portrait, alignment_scatter,
    violin, raincloud, ridgeline,
)
from .scientific import (
    roc_curve, calibration, ecdf, box, bar_err, qq, volcano, survival,
    manhattan, forest, bland_altman, contour_field, hexbin_density,
    streamplot_field, surface3d, jointplot, radar, slopegraph, sankey,
    histogram, bubble, pr_curve, feature_importance, convergence_curve,
    embedding_scatter, attention_map, trajectory, spectrum, ternary, venn2,
    network_graph, dendrogram, chord, image_panel,
)

# Register the bundled style on import so `plt.style.use("paperfig")` works
# for pure-matplotlib users who don't want the paper_style() API.
register_style()

__version__ = "0.6.0"
__all__ = [
    "paper_style", "save", "register_style", "STYLE_PATH",
    "PALETTE", "MARKERS", "LINESTYLES",
    "timeseries_ci", "sorted_bar", "grouped_bar", "residual_diag", "heatmap",
    "scatter_fit", "pareto", "tornado", "confusion", "phase_portrait",
    "alignment_scatter", "violin", "raincloud", "ridgeline",
    "roc_curve", "calibration", "ecdf", "box", "bar_err", "qq", "volcano",
    "survival", "manhattan", "forest", "bland_altman", "contour_field",
    "hexbin_density", "streamplot_field", "surface3d", "jointplot", "radar",
    "slopegraph", "sankey", "histogram", "bubble", "pr_curve",
    "feature_importance", "convergence_curve", "embedding_scatter",
    "attention_map", "trajectory", "spectrum", "ternary", "venn2",
    "network_graph", "dendrogram", "chord", "image_panel",
]
