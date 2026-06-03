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
    fig, ax = pf.pr_curve(yt, ys); assert fig and ax.has_data()
    fig, ax = pf.calibration(yt, ys); assert fig and ax.has_data()
    fig, ax = pf.feature_importance(["a", "b", "c"], [0.2, 0.7, 0.4])
    assert fig and ax.has_data()
    fig, ax = pf.convergence_curve({"loss": np.linspace(1, 0.2, 20), "val": np.linspace(1.1, 0.35, 20)})
    assert fig and ax.has_data()
    xy = RNG.normal(0, 1, (90, 2)) + np.repeat([[0, 0], [3, 0], [0, 3]], 30, axis=0)
    fig, ax = pf.embedding_scatter(xy, np.repeat(["A", "B", "C"], 30))
    assert fig and ax.has_data()
    fig, ax = pf.attention_map(RNG.random((6, 6))); assert fig and ax.has_data()


def test_stats_charts():
    g = {"a": RNG.normal(0, 1, 80), "b": RNG.normal(1, 1, 80)}
    for fn in (pf.ecdf, pf.box, pf.histogram):
        fig, ax = fn(g); assert fig and ax.has_data()
    fig, ax = pf.bar_err(g, brackets=[(0, 1, "*")]); assert fig and ax.has_data()
    fig, ax = pf.qq(RNG.normal(0, 1, 100)); assert fig and ax.has_data()
    fig, ax = pf.bubble(RNG.normal(0, 1, 20), RNG.normal(0, 1, 20), RNG.random(20))
    assert fig and ax.has_data()


def test_omics_medical():
    fig, ax = pf.volcano(RNG.normal(0, 2, 200), 10 ** (-RNG.random(200) * 5))
    assert fig and ax.has_data()
    chrom = np.repeat(np.arange(1, 5), 40)
    pos = np.tile(np.arange(40), 4)
    pvals = 10 ** (-RNG.random(160) * 7)
    fig, ax = pf.manhattan(chrom, pos, pvals, top=2)
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
    U, V = -Y, X
    fig, ax = pf.streamplot_field(X, Y, U, V); assert fig and ax.has_data()
    fig, ax = pf.surface3d(X, Y, np.sin(X) * np.cos(Y)); assert fig and ax.name == "3d"
    t = np.linspace(0, 1, 60)
    fig, ax = pf.trajectory(np.cos(8 * t), np.sin(8 * t), t=t); assert fig and ax.has_data()
    x = np.linspace(100, 500, 120)
    fig, ax = pf.spectrum(x, np.exp(-((x - 250) / 25) ** 2), top=1)
    assert fig and ax.has_data()
    fig, ax = pf.ternary(RNG.random(30), RNG.random(30), RNG.random(30))
    assert fig is not None


def test_rich_multiaxes():
    fig, axes = pf.jointplot(RNG.normal(0, 1, 200), RNG.normal(0, 1, 200))
    assert fig is not None and len(axes) == 3
    fig, ax = pf.radar({"m": [0.8, 0.6, 0.9]}, ["a", "b", "c"]); assert fig is not None
    fig, ax = pf.slopegraph([1, 2], [2, 1], ["p", "q"]); assert fig and ax.has_data()
    fig, ax = pf.sankey([10, -5, -3, -2], ["input", "A", "B", "C"])
    assert fig is not None and len(ax.texts) > 0
    fig, ax = pf.venn2((4, 5, 2)); assert fig is not None and len(ax.texts) >= 3
    fig, ax = pf.network_graph([("a", "b"), ("b", "c"), ("c", "a")])
    assert fig is not None and len(ax.collections) > 0
    fig, ax = pf.dendrogram(RNG.normal(0, 1, (6, 3)))
    assert fig is not None and ax.has_data()
    fig, ax = pf.chord(np.array([[0, 2, 1], [2, 0, 3], [1, 3, 0]]))
    assert fig is not None and len(ax.patches) > 0
    fig, axes = pf.image_panel([RNG.random((20, 20)), RNG.random((20, 20))],
                               scalebars=[(5, "5 um"), None])
    assert fig is not None and len(axes) == 2


def test_roc_auc_perfect():
    # a perfectly separable classifier -> AUC very close to 1
    y = np.array([0, 0, 0, 1, 1, 1]); s = np.array([0.1, 0.2, 0.3, 0.7, 0.8, 0.9])
    fig, ax = pf.roc_curve(y, s)
    auc_label = [t for t in ax.get_legend().get_texts()][0].get_text()
    assert "1.00" in auc_label or "0.99" in auc_label
