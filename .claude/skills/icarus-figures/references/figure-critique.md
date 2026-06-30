# Figure critique — operationalizing the §0b four-axis bar

The cookbook *states* the quality bar; this file *runs* it. A figure is not "done"
when it plots correctly — it is done when it clears a **mechanical floor** and
survives a **judgment pass**. Two layers, run in order:

1. **Mechanical floor** — `python scripts/critique.py scripts/figN_<name>.py`.
   Static analysis catches the hard-rule misses a machine can decide
   (units / uncertainty / N on the figure, colormap, style preset, equal grid,
   vector three-format, dpi). **A `FAIL` here is non-negotiable — fix it.** This
   is the §F checklist + §G anti-patterns, enforced instead of exhorted.
2. **Judgment pass** — the four questions below. The script *cannot* decide these
   (they need the rendered image + the scientific claim), so it prints them as
   prompts and you answer them honestly. This is where ordinary becomes
   publication-grade. **Most figures clear layer 1 and still fail layer 2** — that
   gap is exactly what "shallow vs deep" means.

> The trap this file exists to close: a figure that passes every mechanical check
> can still be a flat, mechanism-blind, equal-grid homework plot. The mechanical
> layer buys "nothing to attack" (defense); only the judgment layer buys "a reader
> stops on the page" (offense). You need both.

---

## How to run the critique

```
python scripts/critique.py scripts/fig2_main_result.py          # report + judgment prompts
python scripts/critique.py scripts/fig2_main_result.py --strict  # WARN also fails (pre-submit)
python scripts/critique.py examples/hero_tikz/framework_hero.tex # a TikZ hero — axis-1 gate
```

Exit code 0 = mechanical floor cleared (no FAIL); 1 = a hard rule is violated.
Wire it into CI or a pre-submit hook so no figure ships below the floor. Then —
every time — answer the four judgment prompts before writing the caption.

**It also gates TikZ heroes (`.tex`).** For a hero figure the script makes the one
axis-1 call a machine can: does the `.tex` embed a **real method object** (a drawn
distribution / scatter / decision region / graphical-model structure), or is it a
generic boxes-and-arrows flowchart? Bare nodes + arrows with no embedded object →
`FAIL` (the §G/§K red line). A math-bearing node map with no drawn object → `WARN`
(fine as a §K5/T4c structure-map only if the cells carry real formulas/numbers).

---

## The judgment pass — four questions the script cannot answer for you

### Axis 1 — Depth: does the figure argue a *mechanism*?

**The one test**: *cover the caption. Is the figure's claim still readable from the
figure alone?* If a reader needs the caption to know what you're claiming, the
figure is displaying data, not arguing.

**Failure signatures (deep-blind even when mechanically clean):**
- The figure shows *points* where the science is about a *shape* — plotting fitted
  means but not the distribution / CI / the curvature that is the actual finding.
- The critical event is in the data but not **on** the figure: no line at the
  phase transition, no marker at the inflection, no shading of the decision region,
  no annotation at the threshold crossing.
- It answers "what" (here is a curve) but not "why + so what" (the curve crosses
  the failure line at t*; the band widens in the extrapolation region *because*
  data runs out there).

**The lift**: draw the generating mechanism. Mark the critical point with a line
and its *meaning* ("$i_f=1.4$ A failure threshold"), annotate the inflection, shade
the regions, draw the real distribution shape — so the figure carries its own
conclusion without the caption.

### Axis 2 — Elegance: one hero, one claim, maximal data-ink

**The one test**: *the drop test* — delete each panel in turn. Did the headline
claim get much weaker? If not, that panel was decoration; delete it.

**Failure signatures:**
- An equal 2×2 (or 3×3) grid of co-equal panels — the eye has no entry point, the
  reader doesn't know where to look. (The script flags this as `E1`.)
- Four loosely related views with no hero; the headline is diluted across all of
  them instead of carried by one.
- Ink that encodes nothing: a gridded background behind a 5-point line, a legend
  for one series, a decorative border.

**The lift**: pick the **one** panel that carries the headline, make it visually
heaviest (≈60–70% of the area, `gridspec_kw={'width_ratios':[2,1]}`), shrink the
rest to context, and lead the eye to the one signal with an arrow/annotation.

### Axis 3 — Unimpeachable: survives a skeptic + a B&W printer

The script checks units / uncertainty-drawn / N-annotated / vector export
mechanically. **You** check the two it cannot:
- **Grayscale**: desaturate the figure (or print it B&W). Does every series stay
  distinguishable by **marker + linestyle**, not colour alone? Reviewers print B&W;
  a figure that turns to mush there loses an argument it had already won.
- **Honest axes**: a skeptic's eye — does a bar chart start at 0? is a dual axis
  only used when the quantities are physically linked? is a log axis marked as log?
  Is any visual emphasis (a wide CI, a steep slope) an artifact of axis choice?

### Axis 4 — Visible gap: reads a tier above in 0.5 seconds

**The one test**: glance for half a second. Does it read "this came from a paper"
or "this is a homework plot"? The signal fires *before* the content is parsed —
it is typography (size hierarchy, alignment, white space) and composition.

**The single most common failure**: the paper's hero/method figure is a generic
boxes-and-arrows flowchart. A reviewer scores it as filler — indistinguishable
from every other paper. The fix is structural, not cosmetic: embed the **real
method object** (a distribution, a before/after scatter, a decision region), borrow
a journal composition (§I P1–P6), redraw it original (§K TikZ). If the hero figure
has no real method object in it, it is not a hero figure yet.

---

## Worked critiques (before → diagnosis → after)

Taste transfers through worked revisions, not rules. Each case clears the
mechanical floor *before* the revision — the lift is pure judgment.

### Case 1 — "the curve" → "the curve crosses the threshold" (axis 1)

- **Before**: a line plot of predicted current vs time; clean style, labelled axes,
  a CI band. Mechanically: all PASS. *But* cover the caption and you can't tell what
  it argues — it's just "current rises".
- **Diagnosis (axis 1)**: the paper's claim is *when the unit fails*. The failure
  threshold and the predicted crossing — the entire point — are nowhere on the
  figure. It shows "what", not "so what".
- **After**: add a horizontal line at `i_f = 1.4 A` labelled "failure threshold",
  drop a vertical marker where the median trajectory crosses it (RUL = 269 d), and
  shade the CI's crossing interval (the *uncertainty in the answer*). Now the
  caption is redundant: the figure says "fails at 269 d, ± the shaded band".

### Case 2 — "four panels" → "one hero + three witnesses" (axis 2)

- **Before**: a 2×2 grid — raw data, fit, residuals, sensitivity — all equal size.
  Mechanically clean; `E1` warns about the equal grid.
- **Diagnosis (axis 2)**: drop test — removing the sensitivity panel barely dents
  the headline ("the model fits and is stable"). The four co-equal panels give the
  eye no entry; the headline is diluted.
- **After**: promote the fit-with-CI to a hero panel at `width_ratios=[2,1]`,
  shrink residual + sensitivity to a stacked context column, delete the raw-data
  panel (the fit panel already shows the points). One figure, one claim, a clear
  reading order.

### Case 3 — "a colourful method diagram" → "a method figure" (axis 4)

- **Before**: a boxes-and-arrows flowchart of the pipeline (Data → Model →
  Transfer → Result), tidy and colourful. Mechanically there's nothing to flag.
- **Diagnosis (axis 4 + axis 1)**: it reads as filler in 0.5 s — every paper has
  this box-arrow diagram, and it embeds *no* real method object. The word
  "domain adaptation" is written in a box instead of being *shown*.
- **After (§I P1 + P5, §K)**: keep the pipeline backbone, but make the central
  "Transfer" stage a hero band that draws the **actual** source/target scatter
  before and after CORAL alignment, with the arrow labelled "−42% MMD", and put the
  real headline number (RUL 269 d) in the output circle. Same backbone, but now it
  *proves* the method instead of *naming* it.

### Case 4 — "passes in colour" → "survives B&W" (axis 3)

- **Before**: three model curves distinguished only by colour (blue/red/green),
  legend keyed by colour. Units, CI, N all present — mechanically PASS.
- **Diagnosis (axis 3, grayscale)**: printed B&W, the three lines collapse to three
  near-identical grays; the comparison — the whole figure — is unreadable.
- **After**: add redundant encoding — colour **+** marker (`o/s/^`) **+** linestyle
  (`-/--/-.`), and direct-label each line at its end instead of a colour legend.
  Survives the B&W printer; the argument holds in any reproduction.

### Case 5 — "the bar of means" → "the distribution" (axis 1)

- **Before**: a bar chart of group means with an SE whisker ("dynamite plot"),
  comparing treated vs control. Mechanically clean — uncertainty is even drawn.
- **Diagnosis (axis 1)**: the bar height is the *summary*, not the *finding*. Two
  groups can share a mean while one is bimodal and the other tight — the bar hides
  exactly the structure that matters, and the SE whisker makes a tiny difference
  look decisive by shrinking with N.
- **After**: a raincloud (or violin + jittered points), so the reader sees the
  actual spread, the overlap, any bimodality — and the effect is judged against the
  *distribution*, not a bar. The mean becomes one annotation on top, not the figure.

### Case 6 — "a 12 % jump" → "a 2 % wobble" (axis 3)

- **Before**: a bar chart where the bars start at `y = 0.86`; the winning method's
  bar towers over the others. Crisp, labelled, looks convincing.
- **Diagnosis (axis 3, honest axes)**: the truncated baseline manufactures the
  story. Start the axis at 0 and the "decisive" lead is a 2 % nudge inside
  overlapping error bars. A skeptic spots the truncation in a glance and stops
  trusting the rest of the paper.
- **After**: bars from 0 with the error bars shown; if the small-but-real
  difference *is* the point, say so honestly — keep the 0 baseline and annotate
  "+2.1 % (95% CI [0.3, 3.9])" rather than letting a cropped axis do the arguing.

### Case 7 — "every point shouted" → "one thing said" (axis 2)

- **Before**: a scatter where all 40 points are labelled, five arrows point at
  "outliers", three text boxes explain regions, and a gradient background fills the
  panel. Busy, but "informative".
- **Diagnosis (axis 2, data-ink)**: annotation serves *one* claim, not a pile.
  Forty labels and five arrows compete; the eye finds no signal because everything
  is emphasised, so nothing is. The decorative gradient encodes nothing.
- **After**: drop the background, delete 38 labels, keep the one arrow on the one
  point the claim is about ("the lone high-leverage case, removed in the robust
  fit"). Restraint *is* the emphasis — one mark draws the eye because it is alone.

### Case 8 — "legend ping-pong" → "read it where it is" (axis 4)

- **Before**: six time-series lines, a legend in the corner keying line 1…6 to
  names. The reader's eye bounces between legend and curve to decode each line.
- **Diagnosis (axis 4, craft)**: with more than ~3 series a keyed legend taxes the
  reader on every glance; the figure reads as a homework plot because the labelling
  is lazy. (And six similar lines is itself a smell — can you aggregate or split?)
- **After**: label each line at its right end, in the line's colour, no legend.
  The name sits where the data is, so the figure is read in one pass. If six is
  genuinely too many, facet or highlight the two that carry the claim and grey the
  rest to context.

### Case 9 — "error bars" → "± what, over how many" (axis 3)

- **Before**: a comparison with error bars and the caption "error bars show
  variability". Mechanically `U3` passes — uncertainty *is* drawn.
- **Diagnosis (axis 3, unimpeachable)**: drawn-but-undefined uncertainty is not
  unimpeachable. SD, SE, and a 95% CI tell different stories and differ by √N; a
  reviewer cannot judge the claim without knowing which, and N. The bar that looks
  tight might be SE over n=3.
- **After**: state it on the figure — "mean ± 95% CI, n = 28 per group" — and pick
  the interval that matches the claim (CI for "where the mean is", a prediction
  interval for "where a new sample lands"). Same ink, now falsifiable.

---

## Checklist to paste under each figure before "done"

```
[ ] mechanical: scripts/critique.py reports no FAIL  (run it, don't eyeball it)
[ ] axis 1: caption covered — claim still readable? mechanism (threshold/inflection/region) drawn?
[ ] axis 2: drop test passed — one hero panel dominates, no decorative panel survives?
[ ] axis 3: B&W-legible (marker+linestyle redundant)? axes honest (bar from 0, dual only if linked)?
[ ] axis 4: 0.5 s test — reads journal, not homework? hero figure embeds a real method object, not a flowchart?
[ ] caption states the CONCLUSION (see caption-and-quality.md), referenced as "Fig. 3" in text
```

A figure that clears the mechanical floor but cannot honestly tick axes 1–4 is the
"shallow" figure this whole skill exists to prevent. The floor is defense; the four
ticks are the offense. Ship only with both.
