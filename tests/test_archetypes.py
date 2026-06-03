"""Smoke tests: every archetype runs and save() writes three vector formats."""
import importlib.util
import matplotlib
matplotlib.use("Agg")
import numpy as np
import pytest
import paperfig as pf

pf.paper_style(font="sans")
RNG = np.random.default_rng(0)


def test_imports_and_palette():
    assert len(pf.PALETTE) == 6 and len(pf.MARKERS) == 6 and len(pf.LINESTYLES) == 6
    assert pf.__version__


def test_timeseries_ci():
    t = np.linspace(0, 10, 30); y = np.sin(t)
    fig, ax = pf.timeseries_ci(t, y + RNG.normal(0, 0.1, 30), y, y - 0.2, y + 0.2)
    assert fig is not None and ax.has_data()


def test_sorted_and_grouped_bar():
    fig, _ = pf.sorted_bar(list("abcde"), RNG.random(5)); assert fig
    fig, _ = pf.grouped_bar(["A", "B"], {"x": [1, 2], "y": [2, 1]}); assert fig


def test_residual_diag():
    fig, axes = pf.residual_diag(RNG.random(40), RNG.normal(0, 0.1, 40))
    assert fig is not None and len(axes) == 2


def test_heatmap_and_confusion():
    fig, _ = pf.heatmap(np.corrcoef(RNG.normal(0, 1, (30, 4)).T)); assert fig
    fig, _ = pf.confusion(np.array([[10, 2], [3, 9]]), labels=["a", "b"]); assert fig


def test_scatter_fit_degrees():
    x = np.sort(RNG.uniform(0, 10, 30))
    for deg in (1, 2):
        fig, ax = pf.scatter_fit(x, 0.5 * x + RNG.normal(0, 1, 30), degree=deg)
        assert fig is not None and ax.has_data()


def test_pareto_and_tornado():
    o1, o2 = RNG.random(20), RNG.random(20)
    fig, _ = pf.pareto(o1, o2, o1 + o2 < 0.6); assert fig
    fig, _ = pf.tornado(["p1", "p2"], [1, 2], [3, 4], 2.0); assert fig


def test_alignment_scatter():
    s = RNG.normal(0, 1, (30, 2))
    fig, _ = pf.alignment_scatter(s, s + 2, s + 0.1, metric_before="0.4", metric_after="0.05")
    assert fig is not None


@pytest.mark.skipif(importlib.util.find_spec("scipy") is None, reason="scipy not installed")
def test_phase_portrait():
    fig, ax = pf.phase_portrait(lambda t, z: [z[1], -0.3 * z[1] - np.sin(z[0])])
    assert fig is not None and ax.has_data()


def test_journal_presets():
    import matplotlib.pyplot as plt
    pf.paper_style(journal="ieee")
    assert tuple(plt.rcParams["figure.figsize"]) == (3.5, 2.6)
    pf.paper_style(journal="nature")
    assert plt.rcParams["font.size"] == 7
    with pytest.raises(ValueError):
        pf.paper_style(journal="not-a-journal")
    pf.paper_style()  # reset


def test_style_registered_and_tex_off():
    import matplotlib.pyplot as plt
    pf.paper_style()
    assert "paperfig" in plt.style.available
    assert plt.rcParams["text.usetex"] is False  # LaTeX not required


def test_save_three_formats(tmp_path):
    t = np.linspace(0, 1, 10)
    fig, _ = pf.timeseries_ci(t, t, t, t - 0.1, t + 0.1)
    pf.save(fig, "t", outdir=str(tmp_path))
    for ext in ("pdf", "png", "svg"):
        assert (tmp_path / f"t.{ext}").exists()
