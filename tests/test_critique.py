"""Tests for the figure-critique gate (scripts/critique.py).

These pin the *mechanical* layer: a clean script clears the floor, and each
hard-rule violation is caught with the right level. The judgment layer (axis-1
depth etc.) is intentionally not auto-scored, so it is not tested here.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from critique import critique_script, main  # noqa: E402


def _write(tmp_path, body: str) -> Path:
    p = tmp_path / "fig_test.py"
    p.write_text(body, encoding="utf-8")
    return p


CLEAN = """
import pandas as pd, numpy as np, matplotlib.pyplot as plt
from _style import paper_style, save
PALETTE, _, _ = paper_style()
df = pd.read_csv('data/processed/pred.csv')
fig, ax = plt.subplots(figsize=(7, 3.2))
ax.fill_between(df['t'], df['lo'], df['hi'], alpha=0.18, label='95% CI')
ax.plot(df['t'], df['y_hat'], label='Predicted')
ax.set_xlabel('Time $t$ (s)')
ax.set_ylabel('Value $y_t$ (a.u.)')
ax.text(0.1, 0.9, 'N=120', transform=ax.transAxes)
save(fig, 'fig1_clean')
"""


def levels(report, check):
    return [f.level for f in report.findings if f.check == check]


def test_clean_script_clears_mechanical_floor(tmp_path):
    report = critique_script(_write(tmp_path, CLEAN), outdir=tmp_path)
    assert report.count("FAIL") == 0
    assert report.fig_names == ["fig1_clean"]
    assert "PASS" in levels(report, "R1")  # reads from file
    assert "PASS" in levels(report, "U3")  # uncertainty drawn
    assert "PASS" in levels(report, "U4")  # N annotated


def test_missing_style_fails(tmp_path):
    body = "import matplotlib.pyplot as plt\nfig, ax = plt.subplots()\nax.plot([1,2],[3,4])\nplt.savefig('x.png')\n"
    report = critique_script(_write(tmp_path, body), outdir=tmp_path)
    assert "FAIL" in levels(report, "V1")   # no preset
    assert "FAIL" in levels(report, "R3")   # paper_style never called
    assert report.worst == "FAIL"


def test_jet_colormap_fails(tmp_path):
    body = CLEAN + "\nimport seaborn as sns\nsns.heatmap(df, cmap='jet')\n"
    report = critique_script(_write(tmp_path, body), outdir=tmp_path)
    assert "FAIL" in levels(report, "U5")


def test_pie_chart_fails(tmp_path):
    body = CLEAN.replace("save(fig, 'fig1_clean')", "ax.pie([1,2,3])\nsave(fig, 'fig1_clean')")
    report = critique_script(_write(tmp_path, body), outdir=tmp_path)
    assert "FAIL" in levels(report, "V3")


def test_inline_big_data_fails(tmp_path):
    big = "data = [" + ",".join(str(i) for i in range(40)) + "]\n"
    body = big + CLEAN.replace("df = pd.read_csv('data/processed/pred.csv')", "")
    report = critique_script(_write(tmp_path, body), outdir=tmp_path)
    assert "FAIL" in levels(report, "R2")


def test_equal_grid_warns(tmp_path):
    body = CLEAN.replace("fig, ax = plt.subplots(figsize=(7, 3.2))",
                         "fig, axes = plt.subplots(2, 2, figsize=(7, 5.5))\nax = axes[0,0]")
    report = critique_script(_write(tmp_path, body), outdir=tmp_path)
    assert "WARN" in levels(report, "E1")


def test_no_uncertainty_warns(tmp_path):
    body = CLEAN.replace("ax.fill_between(df['t'], df['lo'], df['hi'], alpha=0.18, label='95% CI')", "")
    report = critique_script(_write(tmp_path, body), outdir=tmp_path)
    assert "WARN" in levels(report, "U3")


def test_missing_axis_label_warns_or_fails(tmp_path):
    body = CLEAN.replace("ax.set_xlabel('Time $t$ (s)')", "")
    report = critique_script(_write(tmp_path, body), outdir=tmp_path)
    assert levels(report, "U1") and report.findings  # only y labelled -> WARN
    assert "WARN" in levels(report, "U1")


def test_bare_label_without_unit_warns(tmp_path):
    body = CLEAN.replace("ax.set_xlabel('Time $t$ (s)')", "ax.set_xlabel('Time')")
    body = body.replace("ax.set_ylabel('Value $y_t$ (a.u.)')", "ax.set_ylabel('Value')")
    report = critique_script(_write(tmp_path, body), outdir=tmp_path)
    assert "WARN" in levels(report, "U2")


def test_exit_code_fail(tmp_path):
    body = "import matplotlib.pyplot as plt\nfig, ax = plt.subplots()\nax.plot([1,2],[3,4])\n"
    p = _write(tmp_path, body)
    assert main([str(p), "--outdir", str(tmp_path)]) == 1


def test_exit_code_pass(tmp_path):
    # render dummy artifacts so the clean script also passes artifact checks
    for ext in ("pdf", "png", "svg"):
        (tmp_path / f"fig1_clean.{ext}").write_text("x")
    p = _write(tmp_path, CLEAN)
    assert main([str(p), "--outdir", str(tmp_path)]) == 0
