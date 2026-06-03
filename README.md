# paper-figures — a publication-grade figure system for scientific papers

[![CI](https://github.com/TAO-QKV/paper-figures/actions/workflows/ci.yml/badge.svg)](https://github.com/TAO-QKV/paper-figures/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![matplotlib](https://img.shields.io/badge/matplotlib-%E2%89%A53.6-11557c.svg)
![figures](https://img.shields.io/badge/output-PDF%20%2B%20PNG%20%2B%20SVG-success.svg)

Turn "a dataset + a claim" into a **publication-grade figure** — the kind a top-journal editor accepts with no revision request. A self-contained Claude skill: reproducible matplotlib/seaborn plots for data figures, and original TikZ for hero/method figures.

## Example output

The point is not "many chart thumbnails"; it is complex paper figures with hierarchy, insets, cross-panel evidence, and honest uncertainty.

**Journal-style composite showcase** — a multi-modal response-signature figure with a hero manifold, embedded PR/calibration diagnostics, omics evidence, imaging readout, survival validation, forest inset, and a mechanistic evidence graph ([`examples/showcase_gallery.py`](examples/showcase_gallery.py)):

![Showcase gallery](examples/gallery_showcase.png)

**Best-fit coverage atlas** — common paper scenarios rendered as composite panels: ML audit, experimental signal/mixture space, cohort/evidence structure, and image/spatial/attention evidence ([`examples/coverage_gallery.py`](examples/coverage_gallery.py)):

![Coverage gallery](examples/gallery_coverage.png)

Additional smoke/demo galleries are kept as reproducible API checks rather than the visual front door: [`gallery.py`](examples/gallery.py), [`archetypes_gallery.py`](examples/archetypes_gallery.py), [`paradigms_gallery.py`](examples/paradigms_gallery.py), [`modern_gallery.py`](examples/modern_gallery.py), [`scientific_gallery.py`](examples/scientific_gallery.py), [`advanced_gallery.py`](examples/advanced_gallery.py), [`rich_gallery.py`](examples/rich_gallery.py), [`before_after.py`](examples/before_after.py).

## Quickstart (with Claude)

1. Put your data in `data/processed/your_data.csv`.
2. Open Claude in this folder and say:
   > Plot a figure from `data/processed/your_data.csv`; the claim is "Y declines linearly with X".
3. The `paper-figure-generation` skill triggers and produces:
   - a reproducible script `scripts/figN_<name>.py`
   - the figure in three formats `outputs/figures/figN_<name>.{pdf,png,svg}`
   - a caption that states the conclusion
   - a row in `outputs/figures/figure_manifest.csv`

## Use it as a library (no Claude needed)

```bash
pip install -e .          # or: pip install -e ".[extras]"  for pandas/seaborn/scipy
```

```python
import numpy as np
from paperfig import paper_style, save, timeseries_ci, scatter_fit, heatmap

paper_style(font='sans', journal='ieee')   # font: 'sans'|'serif'|'cn'; journal: None|'ieee'|'nature'|'pnas'

t = np.linspace(0, 10, 50); y = 1 - np.exp(-0.3 * t)
fig, ax = timeseries_ci(t, y + np.random.normal(0, .05, 50), y, y - .06, y + .06,
                        ylabel='Signal $y$')
ax.set_title('My result')                  # tweak the returned fig/ax freely
save(fig, 'fig1_main_result')              # → outputs/figures/fig1_main_result.{pdf,png,svg}
```

**48 callable chart types**, each returning `(fig, ax)` or `(fig, axes)`:

| Domain | Functions |
|---|---|
| core | `timeseries_ci`, `sorted_bar`, `grouped_bar`, `scatter_fit`, `heatmap`, `pareto`, `tornado` |
| distributions | `violin`, `raincloud`, `ridgeline`, `histogram`, `box`, `ecdf`, `qq`, `jointplot`, `hexbin_density` |
| ML / diagnostics | `roc_curve`, `pr_curve`, `calibration`, `confusion`, `residual_diag`, `feature_importance`, `convergence_curve`, `embedding_scatter`, `attention_map` |
| stats / comparison | `bar_err` (+ significance brackets), `bubble`, `forest`, `bland_altman`, `slopegraph`, `radar` |
| omics / genomics / medical | `volcano`, `manhattan`, `survival` (Kaplan-Meier) |
| fields / dynamics / spectra | `contour_field`, `streamplot_field`, `surface3d`, `phase_portrait`, `trajectory`, `spectrum`, `ternary` |
| structure / set / flow | `sankey`, `chord`, `dendrogram`, `network_graph`, `venn2` |
| imaging plates | `image_panel` (microscopy / medical / remote-sensing image panels with scalebars) |
| transfer / method | `alignment_scatter` (P5 motif) |

Best-fit route: quantitative and ML panels use the callable matplotlib API; mechanism / architecture / workflow figures use the TikZ composition paradigms; image-heavy evidence uses `image_panel` plus quantitative subpanels. Pie/donut charts are intentionally not highlighted because the cookbook treats them as low data-ink defaults; prefer sorted bars unless composition is the point.

- **Journal presets** — `paper_style(journal=...)` sets that publisher's single-column figure size + font sizes:

  | journal | 1-col width | journal | 1-col width | journal | 1-col width |
  |---|---|---|---|---|---|
  | `nature` | 89 mm | `cell` | 85 mm | `acs` | 3.33 in |
  | `science` | 57 mm | `pnas` | 87 mm | `rsc` | 83 mm |
  | `ieee` | 3.5 in | `elsevier` | 90 mm | `aps` | 86 mm |

  (From each publisher's public author guidelines — verify against the current guidelines, specs drift.)
- **LaTeX is optional** — figures render without a LaTeX install; opt in with `paper_style(tex=True)` for true LaTeX typography.

### Or just a matplotlib style (no API)

```python
import paperfig                 # registers the style name
import matplotlib.pyplot as plt
plt.style.use('paperfig')       # now any plt.* plot is publication-grade
```

## The idea

Publication-grade = the cookbook's **§0b four axes**, all true at once: **Depth** (the figure argues a mechanism) × **Elegance** (one figure, one claim) × **Unimpeachable** (carries its own uncertainty + reproducible) × **Visible gap** (reads journal-grade at a glance). Archetypes A1–A13 are the floor, not the ceiling.

## Relation to SciencePlots

[SciencePlots](https://github.com/garrettj403/SciencePlots) is the excellent, popular toolkit for matplotlib *styles* — and paperfig borrows its best ideas: a `plt.style.use('paperfig')` `.mplstyle`, cascading **journal presets**, and citability. The differences:

- **paperfig does not require LaTeX** (SciencePlots does); LaTeX is opt-in (`tex=True`).
- paperfig adds what a style sheet can't: a **quality bar** (§0b four axes), **hero/method-figure composition paradigms** (§I P1–P6), **callable archetype functions** (`timeseries_ci`, `alignment_scatter`, …), and **original TikZ** for method figures (§K).

Think of it as: *SciencePlots-style presets, plus the judgment and building blocks to make the figure itself publication-grade.* If you only want journal styles, SciencePlots is great; if you want the figure's content held to a bar, use paperfig.

## Layout

| Path | What |
|---|---|
| `paperfig/` | the installable package: `style.py` (preset) + `archetypes.py` (callable A1–A10 + P5) |
| `examples/` | runnable galleries (`showcase_gallery.py`, `coverage_gallery.py`, `scientific_gallery.py`, `advanced_gallery.py`, `archetypes_gallery.py`, `paradigms_gallery.py`) + a complete TikZ hero (`hero_tikz/pipeline_hero.tex`) |
| `tests/` | pytest smoke tests (every archetype + three-format `save`) |
| `.claude/skills/paper-figure-generation/SKILL.md` | the Claude skill (triggers, hard rules) |
| `.../references/figure-cookbook.md` | **main reference**: §0b quality bar · §0a contract · §0 style · §A archetypes A1–A13 · §I composition paradigms P1–P6 · §J craft spec · §K original TikZ · §L external template library · §M Origin front-end |
| `.../references/caption-and-quality.md` | caption writing + final quality checklist |
| `scripts/_style.py` | back-compat shim → `paperfig.style` |
| `data/processed/` · `outputs/figures/` | input data · output + `figure_manifest.csv` |
| `CLAUDE.md` · `pyproject.toml` | project role + `<TEMPLATE_LIB>` convention · packaging |

## Hard rules

Reproducible (a script reads data from a file; no inline data > 20 rows; no AI-generated images) · vector three-format (PDF + PNG + SVG) · style preset called once · colorblind- and grayscale-safe · units / N / uncertainty on the figure · pass the §0b four axes + §F reproducibility checklist before "done".

## Requirements

Python 3.9+, `matplotlib`, `numpy`, `pandas`; `seaborn` for heatmaps; a LaTeX install with TikZ for §K hero figures (optional). See `requirements.txt`.

## License

[MIT](LICENSE) © 2026 TAO-QKV. Use it, fork it, adapt it for your papers.
