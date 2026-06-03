"""Publication-grade matplotlib style preset for scientific paper figures.

Usage in a figure script:

    from _style import paper_style, save, PALETTE, MARKERS, LINESTYLES
    PALETTE, MARKERS, LS = paper_style(font='sans')   # 'sans'(EN journals) | 'serif' | 'cn'
    # ... plot ...
    save(fig, 'fig1_main_result')   # writes PDF + PNG + SVG to outputs/figures/

See .claude/skills/paper-figure-generation/references/figure-cookbook.md
for archetype templates (A1-A13) + the §0b quality bar.
"""
import matplotlib as mpl
import matplotlib.pyplot as plt
from pathlib import Path

# Colorblind-safe 6-color palette (Wong 2011-derived, B&W-discriminable via marker)
PALETTE = ['#1f77b4', '#d62728', '#2ca02c', '#ff7f0e', '#9467bd', '#8c564b']
MARKERS = ['o', 's', '^', 'D', 'v', 'P']
LINESTYLES = ['-', '--', '-.', ':', (0, (3, 1, 1, 1)), (0, (5, 1))]


def paper_style(font: str = 'sans', chinese: bool = None):
    """Apply publication-grade rcParams. Call once at the top of every figure script.

    Args:
        font: typography family —
            'sans'  : Arial/Helvetica (most journals' submission spec). DEFAULT.
            'serif' : Times New Roman (serif journals / when body text is serif).
            'cn'    : SimSun + Times fallback (Chinese-language papers).
        chinese: deprecated back-compat flag. chinese=True maps to font='cn'.

    Returns:
        (PALETTE, MARKERS, LINESTYLES) for convenience.
    """
    if chinese is True:
        font = 'cn'
    mpl.rcParams.update({
        # Editable-vector rule (per Nature-figure standard): text stays as text in
        # SVG/PDF outputs so editors can fix labels without re-rendering.
        'svg.fonttype': 'none',
        'pdf.fonttype': 42,
        'ps.fonttype': 42,
        'figure.dpi': 120,
        'savefig.dpi': 300,
        'savefig.bbox': 'tight',
        'savefig.pad_inches': 0.04,
        # White canvas (avoids transparent PNG looking grey in Word/PPT)
        'figure.facecolor': 'white',
        'savefig.facecolor': 'white',
        'font.size': 11,
        'axes.titlesize': 11.5,
        'axes.titleweight': 'bold',
        'axes.titlepad': 8,
        'axes.labelsize': 10.5,
        'axes.labelpad': 4,
        'xtick.labelsize': 9,
        'ytick.labelsize': 9,
        'legend.fontsize': 9,
        'axes.linewidth': 0.9,
        # Premium typography/ink: soft near-black ink (not pure #000) reads
        # cleaner on white and matches journal house style.
        'axes.edgecolor': '#3a3a3a',
        'axes.labelcolor': '#1a1a1a',
        'axes.titlecolor': '#111111',
        'text.color': '#1a1a1a',
        'xtick.color': '#3a3a3a',
        'ytick.color': '#3a3a3a',
        'lines.linewidth': 1.7,
        'lines.markersize': 4.5,
        'lines.solid_capstyle': 'round',
        'patch.linewidth': 0.8,
        'xtick.direction': 'in',
        'ytick.direction': 'in',
        'xtick.major.size': 3.5,
        'ytick.major.size': 3.5,
        'xtick.minor.visible': True,
        'ytick.minor.visible': True,
        'xtick.minor.size': 2,
        'ytick.minor.size': 2,
        'axes.spines.top': False,
        'axes.spines.right': False,
        # Uniform subtle grid behind data (was off + manually re-added per script)
        'axes.grid': True,
        'axes.axisbelow': True,
        'grid.color': '#c2c2c2',
        'grid.alpha': 0.22,
        'grid.linewidth': 0.55,
        'grid.linestyle': '-',
        # Legend: semi-opaque white box so legends over data stay readable
        # (fixes q1_t1b_rul legend-over-curve overlap uniformly)
        'legend.frameon': True,
        'legend.framealpha': 0.85,
        'legend.facecolor': 'white',
        'legend.edgecolor': '#cccccc',
        'legend.fancybox': False,
        'legend.borderpad': 0.4,
        'mathtext.fontset': 'cm',
        # Use ASCII hyphen-minus (U+002D) instead of Unicode minus (U+2212) so
        # negative tick/labels never trip a missing-glyph warning under SimSun
        # (applies in BOTH chinese / non-chinese modes).
        'axes.unicode_minus': False,
    })
    if font == 'cn':
        mpl.rcParams['font.family'] = ['serif']
        mpl.rcParams['font.serif'] = ['SimSun', 'Times New Roman', 'DejaVu Serif']
    elif font == 'serif':
        mpl.rcParams['font.family'] = ['serif']
        mpl.rcParams['font.serif'] = ['Times New Roman', 'Nimbus Roman', 'DejaVu Serif']
    else:  # 'sans' — default, most journals' submission requirement
        mpl.rcParams['font.family'] = ['sans-serif']
        mpl.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'Nimbus Sans', 'DejaVu Sans']
    return PALETTE, MARKERS, LINESTYLES


def save(fig, name: str, outdir: str = 'outputs/figures', formats=('pdf', 'png', 'svg')):
    """Save figure in multiple formats.

    Defaults: PDF (vector, paper), PNG (raster, preview/Word), SVG (editable text).
    SVG keeps text as text (svg.fonttype='none') so a non-coder can fix labels
    in Inkscape/Illustrator without re-running the script.
    """
    Path(outdir).mkdir(parents=True, exist_ok=True)
    for ext in formats:
        fig.savefig(f'{outdir}/{name}.{ext}')
    print(f"[fig] saved {outdir}/{name}.{{{','.join(formats)}}}")
