"""Smoke tests for the extended scientific chart types."""
import matplotlib
matplotlib.use("Agg")
import numpy as np
import paperfig as pf

pf.paper_style()
RNG = np.random.default_rng(0)


def test_ml_charts():
    yt = (RNG.random(150) > 0.5).astype(int)
    ys = np.clip(yt * 0.4 + RNG.random(150) * 0.6, 0, 1)
    fig, ax = pf.roc_curve(yt, ys); assert fig and ax.has_data()
    fig, ax = pf.calibration(yt, ys); assert fig and ax.has_data()


def test_stats_charts():
    g = {"a": RNG.normal(0, 1, 80), "b": RNG.normal(1, 1, 80)}
    for fn in (pf.ecdf, pf.box):
        fig, ax = fn(g); assert fig and ax.has_data()
    fig, ax = pf.bar_err(g, brackets=[(0, 1, "*")]); assert fig and ax.has_data()
    fig, ax = pf.qq(RNG.normal(0, 1, 100)); assert fig and ax.has_data()


def test_omics_medical():
    fig, ax = pf.volcano(RNG.normal(0, 2, 200), 10 ** (-RNG.random(200) * 5))
    assert fig and ax.has_data()
    fig, ax = pf.survival({"A": (RNG.exponential(5, 60), (RNG.random(60) > 0.3).astype(int))})
    assert fig and ax.has_data()
    fig, ax = pf.forest(["s1", "s2"], [0.2, -0.1], [0.0, -0.3], [0.4, 0.1])
    assert fig and ax.has_data()
    m = RNG.normal(10, 2, 50)
    fig, ax = pf.bland_altman(m, m + RNG.normal(0, 1, 50)); assert fig and ax.has_data()


def test_fields_and_density():
    X, Y = np.meshgrid(np.linspace(-3, 3, 30), np.linspace(-3, 3, 30))
    fig, ax = pf.contour_field(X, Y, np.exp(-(X ** 2 + Y ** 2))); assert fig and ax.has_data()
    fig, ax = pf.hexbin_density(RNG.normal(0, 1, 800), RNG.normal(0, 1, 800))
    assert fig and ax.has_data()


def test_rich_multiaxes():
    fig, axes = pf.jointplot(RNG.normal(0, 1, 200), RNG.normal(0, 1, 200))
    assert fig is not None and len(axes) == 3
    fig, ax = pf.radar({"m": [0.8, 0.6, 0.9]}, ["a", "b", "c"]); assert fig is not None
    fig, ax = pf.slopegraph([1, 2], [2, 1], ["p", "q"]); assert fig and ax.has_data()


def test_roc_auc_perfect():
    # a perfectly separable classifier -> AUC very close to 1
    y = np.array([0, 0, 0, 1, 1, 1]); s = np.array([0.1, 0.2, 0.3, 0.7, 0.8, 0.9])
    fig, ax = pf.roc_curve(y, s)
    auc_label = [t for t in ax.get_legend().get_texts()][0].get_text()
    assert "1.00" in auc_label or "0.99" in auc_label
