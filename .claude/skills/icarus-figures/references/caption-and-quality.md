# Captions & Final Quality Check

Companion to `figure-cookbook.md`. Use after a figure renders.

## A. Writing the caption (journal style)

**A caption states the conclusion, not the contents.** The reader should get the takeaway from caption alone.

- ❌ "Figure 3 shows the relationship between X and Y."
- ✅ "Y declines linearly with X (slope −0.42, 95% CI [−0.48, −0.36]; n = 184); the trend reverses above the dashed threshold."

Structure (1–4 sentences):
1. **Headline finding** — the one sentence the figure defends (mirror the figure's `core_claim`).
2. **What the elements are** — only what isn't obvious: "Shaded band = 95% CI; points = individual replicates."
3. **Stats / N** — test, n, error definition (SD vs SEM vs CI — say which).
4. **Panel keys** — "(a) … (b) …" for multi-panel.

Rules:
- Define every non-obvious symbol, color, line, and the error-bar meaning.
- State **n** and the **uncertainty definition** explicitly (reviewers reject "error bars" with no definition).
- In the body text reference figures as "as in Fig. 3" / "Fig. 3a" — **never** "the figure below/above" (float placement moves it).
- Units in caption match units on axes.
- Significance: report the actual p / effect size, not just asterisks; define asterisk thresholds if used.

## B. Final quality checklist (run before "done")

**§0b four axes** (the bar):
- [ ] **Depth** — the figure argues *why/so-what*, not just *what*; mechanism/threshold/critical point is marked, not left implicit.
- [ ] **Elegance** — one claim, one hero; no decorative panel survives the drop test; eye is led to the one signal.
- [ ] **Unimpeachable** — uncertainty shown (CI/error bars, defined); N annotated; reproducible (script + data + seed).
- [ ] **Visible gap** — journal-grade composition + typography; reads as paper-quality at a glance.

**Mechanical (§F + §J):**
- [ ] reads data from a file path (no inline data > 20 rows)
- [ ] `paper_style()` called once; palette colors (not raw names)
- [ ] PDF + PNG + SVG saved via `save()`; text editable in SVG/PDF
- [ ] colorblind-safe AND grayscale-legible (redundant marker/linestyle)
- [ ] axis labels carry units + symbol; bars start at 0; no rainbow colormap; no 3D
- [ ] font matches target journal (`sans` default); ≤ 2 font families
- [ ] figure size = column width (single ≈ 8.4 cm / double ≈ 17.4 cm); in-figure font ≥ ~80% of body size after scaling
- [ ] rerun-stable (seed set if randomness); registered in `outputs/figures/figure_manifest.csv`
- [ ] every figure is interpreted in the body text (2–3 sentences), not left as decoration

**One-line gate**: hand it to the most demanding reviewer — if they can find one "yes, but…", it is not done (return to §0b).
