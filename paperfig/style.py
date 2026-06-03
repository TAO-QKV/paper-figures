"""Publication-grade matplotlib style preset.

    from paperfig import paper_style, save
    paper_style(font="sans", journal="ieee")   # journal: None | 'ieee' | 'nature' | 'pnas'
    ...
    save(fig, "fig1_main_result")               # PDF + PNG + SVG

Pure-matplotlib users (no API) can also just:
    import paperfig                              # registers the style name
    import matplotlib.pyplot as plt
    plt.style.use("paperfig")

The base look lives in ``paperfig.mplstyle`` (single source of truth);
``paper_style`` applies it, then layers the font family, an optional journal
preset, and an optional LaTeX-text flag on top. Unlike SciencePlots, LaTeX is
NOT required — it's opt-in via ``tex=True``.
"""
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.style as _mstyle
from pathlib import Path

# Colorblind-safe 6-color palette (Wong-2011-derived, B&W-discriminable via marker)
PALETTE = ["#1f77b4", "#d62728", "#2ca02c", "#ff7f0e", "#9467bd", "#8c564b"]
MARKERS = ["o", "s", "^", "D", "v", "P"]
LINESTYLES = ["-", "--", "-.", ":", (0, (3, 1, 1, 1)), (0, (5, 1))]

STYLE_PATH = Path(__file__).resolve().parent / "paperfig.mplstyle"

# Journal presets: single-column figure size + font sizes (public submission specs).
# Borrowed in spirit from SciencePlots' cascading journal styles; values original.
_JOURNAL = {
    "ieee":   {"figure.figsize": (3.5, 2.6), "font.size": 8, "axes.titlesize": 8.5,
               "axes.labelsize": 8, "xtick.labelsize": 7, "ytick.labelsize": 7,
               "legend.fontsize": 7},
    "nature": {"figure.figsize": (3.5, 2.7), "font.size": 7, "axes.titlesize": 8,
               "axes.labelsize": 7, "xtick.labelsize": 6, "ytick.labelsize": 6,
               "legend.fontsize": 6},
    "pnas":   {"figure.figsize": (3.42, 2.6), "font.size": 8, "axes.titlesize": 8.5,
               "axes.labelsize": 8, "xtick.labelsize": 7, "ytick.labelsize": 7,
               "legend.fontsize": 7},
}


def register_style():
    """Register the bundled style so ``plt.style.use('paperfig')`` works."""
    try:
        lib = _mstyle.core.read_style_directory(str(STYLE_PATH.parent))
        _mstyle.library.update(lib)
        _mstyle.available[:] = sorted(_mstyle.library.keys())
    except Exception:
        pass  # registration is a convenience; paper_style still works via path


def paper_style(font: str = "sans", journal: str = None, tex: bool = False,
                chinese: bool = None):
    """Apply publication-grade rcParams. Call once at the top of a figure script.

    Args:
        font: 'sans' (Arial/Helvetica, most journals' spec; DEFAULT), 'serif'
              (Times), or 'cn' (SimSun, Chinese papers).
        journal: None, or 'ieee' / 'nature' / 'pnas' — sets single-column figure
              size + font sizes for that journal.
        tex: if True, render text with LaTeX (``text.usetex``). Off by default —
              paperfig does NOT require a LaTeX install.
        chinese: deprecated back-compat; chinese=True maps to font='cn'.

    Returns:
        (PALETTE, MARKERS, LINESTYLES).
    """
    if chinese is True:
        font = "cn"
    plt.style.use(str(STYLE_PATH))  # base look (single source of truth)

    if font == "cn":
        mpl.rcParams["font.family"] = ["serif"]
        mpl.rcParams["font.serif"] = ["SimSun", "Times New Roman", "DejaVu Serif"]
    elif font == "serif":
        mpl.rcParams["font.family"] = ["serif"]
        mpl.rcParams["font.serif"] = ["Times New Roman", "Nimbus Roman", "DejaVu Serif"]
    else:  # 'sans' — default
        mpl.rcParams["font.family"] = ["sans-serif"]
        mpl.rcParams["font.sans-serif"] = ["Arial", "Helvetica", "Nimbus Sans", "DejaVu Sans"]

    if journal is not None:
        key = journal.lower()
        if key not in _JOURNAL:
            raise ValueError(f"unknown journal {journal!r}; choose from {list(_JOURNAL)}")
        mpl.rcParams.update(_JOURNAL[key])

    if tex:
        mpl.rcParams["text.usetex"] = True

    return PALETTE, MARKERS, LINESTYLES


def save(fig, name: str, outdir: str = "outputs/figures",
         formats=("pdf", "png", "svg")):
    """Save a figure as PDF (vector) + PNG (raster) + SVG (editable text)."""
    Path(outdir).mkdir(parents=True, exist_ok=True)
    for ext in formats:
        fig.savefig(f"{outdir}/{name}.{ext}")
    print(f"[fig] saved {outdir}/{name}.{{{','.join(formats)}}}")
