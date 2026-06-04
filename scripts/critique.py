#!/usr/bin/env python3
"""Figure critique — turn the §0b four-axis quality bar from exhortation into a gate.

The cookbook *describes* the acceptance test ("cover the caption — is the claim
still readable?"); this script *runs* the part of it a machine can decide, by
static analysis of a figure script plus checks on its rendered artifacts. It does
NOT execute the script (untrusted/slow); it parses the source (``ast`` + regex)
and inspects ``outputs/figures/<name>.{pdf,png,svg}`` if present.

    python scripts/critique.py scripts/fig2_main_result.py
    python scripts/critique.py scripts/fig2_main_result.py --strict   # WARN -> failure

Two layers, by design:
  * MECHANICAL (this script): reproducibility (§F), units/uncertainty/N on the
    figure (axis 3), colormap/style/anti-patterns (§G), equal-grid (axis 2),
    three-format vector export + dpi + editable SVG (artifacts).
  * JUDGMENT (printed as prompts for the author/model): does the figure argue a
    *mechanism* (axis 1)? does one hero panel dominate (axis 2)? is it legible in
    grayscale (axis 3)? — the script flags what it cannot decide instead of
    pretending to score it. See ``references/figure-critique.md`` for the rubric.

Exit code: 0 if no FAIL (and no WARN under --strict), else 1 — so it can gate CI
or a pre-submit hook.
"""
from __future__ import annotations

import argparse
import ast
import re
import struct
import sys
from dataclasses import dataclass, field
from pathlib import Path

LEVELS = {"PASS": 0, "INFO": 1, "WARN": 2, "FAIL": 3}
MARK = {"PASS": "ok ", "INFO": "i  ", "WARN": "!  ", "FAIL": "XXX"}

AXES = {
    "depth": "Axis 1 — Depth (TikZ hero: embeds a real method object, not text-in-boxes)",
    "reproducible": "Reproducibility (§F)",
    "unimpeachable": "Axis 3 — Unimpeachable (uncertainty / N / units / B&W)",
    "elegance": "Axis 2 — Elegance (one hero, maximal data-ink)",
    "visible-gap": "Axis 4 — Visible gap (journal-grade craft)",
    "artifact": "Rendered artifacts (vector three-format)",
}

# Signals that a TikZ hero embeds a *real method object* (§K) rather than being a
# generic boxes-and-arrows flowchart. Any one is enough.
TIKZ_REAL_OBJECT = {
    "plotted curve / density (plot coordinates / addplot / axis)":
        r"plot\s+coordinates|\\addplot|\\begin\{axis\}",
    "scatter / point cloud / drawn network (\\foreach + circle/fill)":
        r"\\foreach[\s\S]{0,160}?(?:circle\s*\(|\\fill\b)",
    "random point cloud (rand / rnd)":
        r"\brnd\b|\brand\b",
    "shaded decision regions (\\fill[...] ... rectangle)":
        r"\\fill\[[^\]]*\][\s\S]{0,90}?\brectangle\b",
    "graphical-model structure (latent / obs / plate / factor)":
        r"\\node\[[^\]]*\b(?:latent|obs|const)\b[^\]]*\]|\\plate\b|\\factor\b",
    "smooth distribution curve":
        r"\bsmooth\b",
}

BAD_CMAPS = ("jet", "rainbow", "hsv", "gist_rainbow", "nipy_spectral", "gist_ncar")


@dataclass
class Finding:
    axis: str
    check: str
    level: str
    msg: str
    fix: str = ""


@dataclass
class Report:
    path: Path
    fig_names: list[str] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)

    def add(self, axis, check, level, msg, fix=""):
        self.findings.append(Finding(axis, check, level, msg, fix))

    @property
    def worst(self) -> str:
        return max((f.level for f in self.findings), key=lambda l: LEVELS[l], default="PASS")

    def count(self, level) -> int:
        return sum(1 for f in self.findings if f.level == level)


# --------------------------------------------------------------------------- #
# static source analysis
# --------------------------------------------------------------------------- #
def _call_tail(node: ast.Call) -> str:
    """Final name of a call's func: ax.set_xlabel -> 'set_xlabel', save -> 'save'."""
    f = node.func
    if isinstance(f, ast.Attribute):
        return f.attr
    if isinstance(f, ast.Name):
        return f.id
    return ""


def _str_args(node: ast.Call) -> list[str]:
    return [a.value for a in node.args if isinstance(a, ast.Constant) and isinstance(a.value, str)]


def _has_unit_or_symbol(label: str) -> bool:
    # a unit in parentheses "(s)", "(mm)", or a math symbol "$y_t$", or a slash unit "kg/m^2"
    return bool(re.search(r"\(.+\)|\$.+\$|/[A-Za-z]", label))


def analyse_source(src: str, report: Report) -> None:
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        report.add("reproducible", "PARSE", "FAIL", f"script does not parse: {e}")
        return

    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)]
    tails = [_call_tail(c) for c in calls]
    tail_set = set(tails)

    def has(*names) -> bool:
        return any(t in names for t in tails)

    def n_calls(name) -> int:
        return tails.count(name)

    # ---- figure names from save(fig, "name") ----
    for c in calls:
        if _call_tail(c) in ("save", "savefig_three"):
            sargs = _str_args(c)
            if sargs:
                report.fig_names.append(sargs[0])

    # ---- Reproducibility (§F) ----
    reads_file = has("read_csv", "read_table", "read_excel", "load", "loadtxt",
                     "genfromtxt", "read_parquet", "load_npz", "open")
    uses_rng = bool(re.search(r"np\.random|default_rng|\brandom\.", src))
    seeded = bool(re.search(r"default_rng\(\s*\d|np\.random\.seed\(|\brandom\.seed\(|seed\s*=\s*\d", src))
    if reads_file:
        report.add("reproducible", "R1", "PASS", "reads data from a file path")
    elif uses_rng and seeded:
        report.add("reproducible", "R1", "WARN",
                   "no file read; uses seeded synthetic data",
                   "fine for a demo, but a paper figure reads real data from data/processed/*.csv")
    else:
        report.add("reproducible", "R1", "FAIL",
                   "no data file read and no seeded RNG — data is inline or nondeterministic",
                   "read from a file path (or seed the RNG for a demo)")

    # inline data > 20 rows
    big = max((len(n.elts) for n in ast.walk(tree)
               if isinstance(n, (ast.List, ast.Tuple))
               and len(n.elts) > 20
               and all(isinstance(e, ast.Constant) or
                       (isinstance(e, ast.UnaryOp) and isinstance(e.operand, ast.Constant))
                       for e in n.elts)), default=0)
    if big:
        report.add("reproducible", "R2", "FAIL",
                   f"inline literal with {big} numeric elements (> 20)",
                   "move the data to a CSV and read it (hard rule: no inline data > 20 rows)")

    n_style = n_calls("paper_style") + len(re.findall(r"style\.use\(\s*['\"]paperfig['\"]", src))
    if n_style == 1:
        report.add("reproducible", "R3", "PASS", "paper_style() called once")
    elif n_style == 0:
        report.add("reproducible", "R3", "FAIL", "paper_style() never called",
                   "call paper_style(...) once at the top (or plt.style.use('paperfig'))")
    else:
        report.add("reproducible", "R3", "WARN", f"paper_style()/style.use called {n_style}x",
                   "call the preset once; do not re-apply per figure")

    if has("save"):
        report.add("reproducible", "R4", "PASS", "save() used (three-format export)")
    elif has("savefig"):
        report.add("reproducible", "R4", "WARN", "uses fig.savefig directly, not save()",
                   "use save(fig, name) so PDF+PNG+SVG are all written")
    else:
        report.add("reproducible", "R4", "FAIL", "no save()/savefig call — figure is never written")

    if uses_rng and not seeded:
        report.add("reproducible", "R5", "WARN", "randomness without a fixed seed",
                   "seed it (default_rng(SEED)) so the figure is rerun-stable")

    # ---- Axis 3 — Unimpeachable ----
    xlabels = re.findall(r"set_xlabel\(\s*[rf]?['\"](.*?)['\"]", src)
    ylabels = re.findall(r"set_ylabel\(\s*[rf]?['\"](.*?)['\"]", src)
    if xlabels and ylabels:
        report.add("unimpeachable", "U1", "PASS", "x and y axes labelled")
    elif xlabels or ylabels:
        report.add("unimpeachable", "U1", "WARN", "only one axis labelled",
                   "label both axes (every quantitative axis carries a label)")
    else:
        report.add("unimpeachable", "U1", "FAIL", "no axis labels found",
                   "set_xlabel / set_ylabel with unit + symbol")
    labels = xlabels + ylabels
    if labels and not any(_has_unit_or_symbol(l) for l in labels):
        report.add("unimpeachable", "U2", "WARN", "no axis label carries a unit or symbol",
                   'write "Time $t$ (s)", not a bare "Time" (§J J6)')

    if has("fill_between", "errorbar") or re.search(r"\byerr\b|\bxerr\b|fill_betweenx|axhspan|axvspan", src) \
            or re.search(r"\bCI\b|confidence", src, re.I):
        report.add("unimpeachable", "U3", "PASS", "uncertainty drawn (CI band / error bars)")
    else:
        report.add("unimpeachable", "U3", "WARN", "no uncertainty drawn on the figure",
                   "add a CI band / error bars, or state on the figure why none (axis 3)")

    if re.search(r"[Nn]\s*=\s*\{?\d|[Nn]\s*=\s*\{|\$[Nn]\$\s*=|n\s*=\s*len", src):
        report.add("unimpeachable", "U4", "PASS", "N annotated")
    else:
        report.add("unimpeachable", "U4", "WARN", "N not annotated on the figure",
                   "a skeptic asks 'N=?': annotate the sample size per series")

    bad = [c for c in BAD_CMAPS if re.search(rf"cmap\s*=\s*['\"]{c}['\"]|['\"]{c}['\"]\s*\)|\.set_cmap\(\s*['\"]{c}", src)]
    if bad:
        report.add("unimpeachable", "U5", "FAIL", f"perceptually non-uniform colormap: {bad[0]}",
                   "use viridis (sequential) or RdBu_r (diverging) — never jet/rainbow (§G)")

    # ---- Axis 2 — Elegance ----
    for c in calls:
        if _call_tail(c) == "subplots":
            nums = [a.value for a in c.args if isinstance(a, ast.Constant) and isinstance(a.value, int)]
            kw = {k.arg for k in c.keywords}
            ratio = ("gridspec_kw" in kw) or re.search(r"width_ratios|height_ratios", src)
            if len(nums) >= 2 and nums[0] >= 2 and nums[1] >= 2 and not ratio:
                report.add("elegance", "E1", "WARN",
                           f"equal {nums[0]}x{nums[1]} grid, no width/height ratios",
                           "pick ONE hero panel and shrink the rest "
                           "(gridspec_kw={'width_ratios':[2,1]}) — equal grids are usually wrong (axis 2)")
            break

    # ---- Axis 4 — Visible gap ----
    if n_style == 0:
        report.add("visible-gap", "V1", "FAIL", "default matplotlib style (no preset)",
                   "call paper_style(): default blue/orange + top-right spines reads as homework")
    else:
        report.add("visible-gap", "V1", "PASS", "style preset applied")
    if has("twinx", "twiny"):
        report.add("visible-gap", "V2", "WARN", "dual axis (twinx/twiny)",
                   "only if the two quantities are physically linked; else split into two panels (§J J6)")
    if has("pie"):
        report.add("visible-gap", "V3", "FAIL", "pie chart",
                   "low data-ink, hard to compare angles (§G) — use a sorted bar (A2)")
    if re.search(r"projection\s*=\s*['\"]3d['\"]|Axes3D|plot_surface|bar3d", src):
        report.add("visible-gap", "V4", "INFO", "3D axes",
                   "justify the third dimension; a flat heatmap/contour is usually more legible (§J J3)")


# --------------------------------------------------------------------------- #
# rendered-artifact checks
# --------------------------------------------------------------------------- #
def _png_dpi(p: Path) -> float | None:
    """Read DPI from a PNG pHYs chunk without PIL. Returns dots-per-inch or None."""
    try:
        data = p.read_bytes()
        i = data.find(b"pHYs")
        if i < 0:
            return None
        x_ppu, _y_ppu, unit = struct.unpack(">IIB", data[i + 4:i + 13])
        if unit != 1:  # 1 = metre
            return None
        return round(x_ppu * 0.0254, 1)
    except Exception:
        return None


def analyse_artifacts(report: Report, outdir: Path) -> None:
    if not report.fig_names:
        report.add("artifact", "A0", "INFO", "no save(fig, NAME) found — cannot locate artifacts")
        return
    for name in report.fig_names:
        present = {ext: (outdir / f"{name}.{ext}").exists() for ext in ("pdf", "png", "svg")}
        missing = [e for e, ok in present.items() if not ok]
        if not any(present.values()):
            report.add("artifact", "A0", "INFO", f"'{name}': not rendered yet",
                       f"run the script, then re-critique to check {outdir}/{name}.{{pdf,png,svg}}")
            continue
        if missing:
            report.add("artifact", "A1", "FAIL", f"'{name}': missing {', '.join(missing)}",
                       "ship vector three-format (PDF + PNG + SVG); never PNG-only")
        else:
            report.add("artifact", "A1", "PASS", f"'{name}': PDF + PNG + SVG all present")
        if present["png"]:
            dpi = _png_dpi(outdir / f"{name}.png")
            if dpi is not None and dpi < 300:
                report.add("artifact", "A2", "WARN", f"'{name}': PNG is {dpi:.0f} dpi (< 300)",
                           "raster export at >= 300 dpi (grainy in print otherwise)")
        if present["svg"]:
            svg = (outdir / f"{name}.svg").read_text(errors="ignore")
            if "<text" not in svg and re.search(r"set_[xy]label|set_title|text\(", "".join(report.fig_names)) is None:
                pass  # no labels expected
            elif "<text" not in svg:
                report.add("artifact", "A3", "WARN", f"'{name}': SVG has no <text> (text was pathified)",
                           "set svg.fonttype='none' so labels stay editable text (paper_style does this)")


JUDGMENT_PROMPTS = [
    ("Axis 1 — Depth", "Cover the caption: is the claim still readable from the figure alone? "
                       "Is the *mechanism* drawn (threshold line, inflection, decision region, the "
                       "actual distribution shape) — not just 'what' but 'why + so what'?"),
    ("Axis 2 — Elegance", "Drop test: delete each panel — is the claim much weaker? If not, delete it. "
                          "Does ONE hero panel carry the headline while the rest visibly shrink?"),
    ("Axis 3 — Grayscale", "Print it in B&W: does every series stay distinguishable by marker/linestyle, "
                           "not colour alone?"),
    ("Axis 4 — 0.5 s test", "Glance for half a second: does it read 'this came from a paper', or 'homework'? "
                            "Hero/method figure must NOT be a generic boxes-and-arrows flowchart (§I)."),
]


# --------------------------------------------------------------------------- #
def render(report: Report, show_pass: bool) -> str:
    out: list[str] = []
    out.append(f"\nFigure critique — {report.path}")
    if report.fig_names:
        out.append(f"  figures: {', '.join(report.fig_names)}")
    out.append("=" * 64)
    for axis, title in AXES.items():
        fs = [f for f in report.findings if f.axis == axis]
        if not fs:
            continue
        shown = [f for f in fs if show_pass or f.level != "PASS"]
        if not shown:
            out.append(f"\n{title}\n  ok  all checks pass")
            continue
        out.append(f"\n{title}")
        for f in shown:
            out.append(f"  {MARK[f.level]} [{f.check}] {f.msg}")
            if f.fix and f.level in ("WARN", "FAIL"):
                out.append(f"        -> {f.fix}")
    out.append("\nJudgment — the script cannot decide these; you must (see figure-critique.md):")
    for tag, q in JUDGMENT_PROMPTS:
        out.append(f"  ?  {tag}: {q}")
    n_fail, n_warn = report.count("FAIL"), report.count("WARN")
    out.append("=" * 64)
    verdict = "FAIL" if n_fail else ("WARN" if n_warn else "PASS")
    out.append(f"Mechanical verdict: {verdict}  ({n_fail} FAIL, {n_warn} WARN, "
               f"{report.count('PASS')} PASS)")
    if verdict != "FAIL":
        out.append("Mechanical floor cleared — now answer the four judgment prompts before 'done'.")
    return "\n".join(out)


def analyse_tikz(src: str, report: Report) -> None:
    """Static critique of a standalone TikZ hero/method figure (.tex).

    The one check a machine can make here that it cannot for a data figure: does
    the hero embed a REAL method object (a drawn distribution / scatter / decision
    region / graphical-model structure), or is it the generic boxes-and-arrows
    flowchart §G/§K warn against? Bare nodes + arrows with no embedded object is
    the single most common hero-figure failure.
    """
    # reproducible by construction — but a standalone doc is zero compile risk
    if re.search(r"\\documentclass(?:\[[^\]]*\])?\{standalone\}|\\documentclass\[[^\]]*\bstandalone\b", src):
        report.add("reproducible", "TX0", "PASS", "standalone document — zero compile risk to the paper")
    else:
        report.add("reproducible", "TX0", "WARN", "not a standalone document",
                   "compile as \\documentclass[tikz]{standalone} → PDF → \\includegraphics (§K0): "
                   "zero compile risk to the main document")

    n_nodes = len(re.findall(r"\\node\b", src))
    n_arrows = len(re.findall(r"-\{?Latex|->|\\draw\[[^\]]*\barr\b", src))
    n_math = len(re.findall(r"\$[^$]+\$", src))

    found = [name for name, pat in TIKZ_REAL_OBJECT.items() if re.search(pat, src, re.S)]
    if found:
        report.add("depth", "TX1", "PASS", "embeds a real method object — " + "; ".join(found[:2]))
    elif n_math >= 3:
        report.add("depth", "TX1", "WARN",
                   f"no *drawn* method object; {n_math} math expressions in nodes (a §K5/T4c structure-map?)",
                   "OK as a structure/result map IF cells carry real formulas/numbers (not empty labels); "
                   "but a true hero should embed a drawn distribution / scatter / region (§K, framework-figures.md)")
    else:
        report.add("depth", "TX1", "FAIL",
                   f"no embedded method object — {n_nodes} nodes + {n_arrows} arrows read as a generic flowchart",
                   "axis 1: at least one hero node must embed a REAL object (distribution / scatter / decision "
                   "region / before-after), not text-in-boxes (§G, §K, framework-figures.md)")

    # hero must be visually heaviest (§J) — soft check
    if n_nodes >= 3 and not re.search(r"line width|ultra thick|very thick|draw=red|fill=red", src):
        report.add("visible-gap", "TX2", "WARN", "no visually-heaviest hero node detected",
                   "set the contribution node off — heavier border (line width) / saturated colour (§J: hero is heaviest)")


def critique_script(path: str | Path, outdir: str | Path = "outputs/figures") -> Report:
    """Critique one figure script (.py data figure or .tex TikZ hero). Importable for tests."""
    path = Path(path)
    report = Report(path=path)
    src = path.read_text(encoding="utf-8", errors="ignore")
    if path.suffix == ".tex":
        analyse_tikz(src, report)
    else:
        analyse_source(src, report)
        analyse_artifacts(report, Path(outdir))
    return report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Critique a figure against the §0b four-axis bar (matplotlib .py or TikZ .tex).")
    ap.add_argument("script", help="path to a figure script — a matplotlib .py, or a TikZ hero .tex")
    ap.add_argument("--outdir", default="outputs/figures", help="where rendered figures live")
    ap.add_argument("--strict", action="store_true", help="treat WARN as failure (exit 1)")
    ap.add_argument("--show-pass", action="store_true", help="also print passing checks")
    args = ap.parse_args(argv)

    try:  # section marks (§) and dashes render cleanly on UTF-8 terminals
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    p = Path(args.script)
    if not p.exists():
        print(f"error: {p} not found", file=sys.stderr)
        return 2
    report = critique_script(p, args.outdir)
    print(render(report, show_pass=args.show_pass))
    if report.count("FAIL") or (args.strict and report.count("WARN")):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
