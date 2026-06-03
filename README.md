# paper-figures — a publication-grade figure system for scientific papers

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![matplotlib](https://img.shields.io/badge/matplotlib-%E2%89%A53.6-11557c.svg)
![figures](https://img.shields.io/badge/output-PDF%20%2B%20PNG%20%2B%20SVG-success.svg)

Turn "a dataset + a claim" into a **publication-grade figure** — the kind a top-journal editor accepts with no revision request. A self-contained Claude skill: reproducible matplotlib/seaborn plots for data figures, and original TikZ for hero/method figures.

## Quickstart (with Claude)

1. Put your data in `data/processed/your_data.csv`.
2. Open Claude in this folder and say:
   > Plot a figure from `data/processed/your_data.csv`; the claim is "Y declines linearly with X".
3. The `paper-figure-generation` skill triggers and produces:
   - a reproducible script `scripts/figN_<name>.py`
   - the figure in three formats `outputs/figures/figN_<name>.{pdf,png,svg}`
   - a caption that states the conclusion
   - a row in `outputs/figures/figure_manifest.csv`

## Use it without the skill

```python
import sys; sys.path.insert(0, 'scripts')
from _style import paper_style, save, PALETTE, MARKERS, LINESTYLES
PALETTE, MARKERS, LS = paper_style(font='sans')   # 'sans' (default, most journals) | 'serif' | 'cn'
import pandas as pd, matplotlib.pyplot as plt
df = pd.read_csv('data/processed/your_data.csv')
fig, ax = plt.subplots(figsize=(7, 3.2))
# ... plot ...
save(fig, 'fig1_main_result')   # → outputs/figures/fig1_main_result.{pdf,png,svg}
```

## The idea

Publication-grade = the cookbook's **§0b four axes**, all true at once: **Depth** (the figure argues a mechanism) × **Elegance** (one figure, one claim) × **Unimpeachable** (carries its own uncertainty + reproducible) × **Visible gap** (reads journal-grade at a glance). Archetypes A1–A13 are the floor, not the ceiling.

## Layout

| Path | What |
|---|---|
| `.claude/skills/paper-figure-generation/SKILL.md` | the skill (triggers, hard rules) |
| `.../references/figure-cookbook.md` | **main reference**: §0b quality bar · §0a contract · §0 style · §A archetypes A1–A13 · §I composition paradigms P1–P6 · §J craft spec · §K original TikZ · §L external template library · §M Origin front-end |
| `.../references/caption-and-quality.md` | caption writing + final quality checklist |
| `scripts/_style.py` | `paper_style()` + `save()` (three-format export) |
| `scripts/_smoke_test.py` | font / pipeline smoke test |
| `data/processed/` | input data (figures read from here) |
| `outputs/figures/` | output + `figure_manifest.csv` |
| `CLAUDE.md` | project role + `<TEMPLATE_LIB>` convention |

## Hard rules

Reproducible (a script reads data from a file; no inline data > 20 rows; no AI-generated images) · vector three-format (PDF + PNG + SVG) · style preset called once · colorblind- and grayscale-safe · units / N / uncertainty on the figure · pass the §0b four axes + §F reproducibility checklist before "done".

## Requirements

Python 3.9+, `matplotlib`, `numpy`, `pandas`; `seaborn` for heatmaps; a LaTeX install with TikZ for §K hero figures (optional). See `requirements.txt`.

## License

[MIT](LICENSE) © 2026 TAO-QKV. Use it, fork it, adapt it for your papers.
