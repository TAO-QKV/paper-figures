"""Publication-grade matplotlib style preset.

    from paperfig import paper_style, save, PALETTE, MARKERS, LINESTYLES
    PALETTE, MARKERS, LS = paper_style(font="sans")   # 'sans' | 'serif' | 'cn'
    ...
    save(fig, "fig1_main_result")   # PDF + PNG + SVG
"""
import matplotlib as mpl
from pathlib import Path

# Colorblind-safe 6-color palette (Wong-2011-derived, B&W-discriminable via marker)
PALETTE = ["#1f77b4", "#d62728", "#2ca02c", "#ff7f0e", "#9467bd", "#8c564b"]
MARKERS = ["o", "s", "^", "D", "v", "P"]
LINESTYLES = ["-", "--", "-.", ":", (0, (3, 1, 1, 1)), (0, (5, 1))]


def paper_style(font: str = "sans", chinese: bool = None):
    """Apply publication-grade rcParams. Call once at the top of a figure script.

    Args:
        font: 'sans' (Arial/Helvetica, most journals' submission spec; DEFAULT),
              'serif' (Times), or 'cn' (SimSun + Times fallback, Chinese papers).
        chinese: deprecated back-compat; chinese=True maps to font='cn'.

    Returns:
        (PALETTE, MARKERS, LINESTYLES).
    """
    if chinese is True:
        font = "cn"
    mpl.rcParams.update({
        "svg.fonttype": "none", "pdf.fonttype": 42, "ps.fonttype": 42,
        "figure.dpi": 120, "savefig.dpi": 300, "savefig.bbox": "tight",
        "savefig.pad_inches": 0.04,
        "figure.facecolor": "white", "savefig.facecolor": "white",
        "font.size": 11, "axes.titlesize": 11.5, "axes.titleweight": "bold",
        "axes.titlepad": 8, "axes.labelsize": 10.5, "axes.labelpad": 4,
        "xtick.labelsize": 9, "ytick.labelsize": 9, "legend.fontsize": 9,
        "axes.linewidth": 0.9,
        "axes.edgecolor": "#3a3a3a", "axes.labelcolor": "#1a1a1a",
        "axes.titlecolor": "#111111", "text.color": "#1a1a1a",
        "xtick.color": "#3a3a3a", "ytick.color": "#3a3a3a",
        "lines.linewidth": 1.7, "lines.markersize": 4.5,
        "lines.solid_capstyle": "round", "patch.linewidth": 0.8,
        "xtick.direction": "in", "ytick.direction": "in",
        "xtick.major.size": 3.5, "ytick.major.size": 3.5,
        "xtick.minor.visible": True, "ytick.minor.visible": True,
        "xtick.minor.size": 2, "ytick.minor.size": 2,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "axes.axisbelow": True,
        "grid.color": "#c2c2c2", "grid.alpha": 0.22, "grid.linewidth": 0.55,
        "grid.linestyle": "-",
        "legend.frameon": True, "legend.framealpha": 0.85,
        "legend.facecolor": "white", "legend.edgecolor": "#cccccc",
        "legend.fancybox": False, "legend.borderpad": 0.4,
        "mathtext.fontset": "cm", "axes.unicode_minus": False,
    })
    if font == "cn":
        mpl.rcParams["font.family"] = ["serif"]
        mpl.rcParams["font.serif"] = ["SimSun", "Times New Roman", "DejaVu Serif"]
    elif font == "serif":
        mpl.rcParams["font.family"] = ["serif"]
        mpl.rcParams["font.serif"] = ["Times New Roman", "Nimbus Roman", "DejaVu Serif"]
    else:  # 'sans' — default, most journals' requirement
        mpl.rcParams["font.family"] = ["sans-serif"]
        mpl.rcParams["font.sans-serif"] = ["Arial", "Helvetica", "Nimbus Sans", "DejaVu Sans"]
    return PALETTE, MARKERS, LINESTYLES


def save(fig, name: str, outdir: str = "outputs/figures",
         formats=("pdf", "png", "svg")):
    """Save a figure as PDF (vector) + PNG (raster) + SVG (editable text)."""
    Path(outdir).mkdir(parents=True, exist_ok=True)
    for ext in formats:
        fig.savefig(f"{outdir}/{name}.{ext}")
    print(f"[fig] saved {outdir}/{name}.{{{','.join(formats)}}}")
