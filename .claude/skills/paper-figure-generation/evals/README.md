# Triggering evals

`trigger-eval.json` — 20 realistic queries (10 should-trigger, 10 tricky
near-miss should-not-trigger) for optimizing the SKILL.md `description` with
Anthropic's `skill-creator` description-optimization loop:

```
python -m scripts.run_loop \
  --eval-set evals/trigger-eval.json \
  --skill-path . \
  --model <your-session-model> --max-iterations 5 --verbose
```

The negatives are deliberately hard — they share keywords with the skill
(plot / chart / matplotlib / diagram / flowchart / heatmap / figure / draw /
dpi) but each actually needs something else (a pptx/xlsx/pdf task, an interactive
dashboard, a UML diagram, a throwaway exploratory plot, a one-step format
conversion, an advice question, decorative art).

**Caveat (2026-06):** the `skill-creator` trigger harness is Unix-oriented and
did not run as-is on Windows + Claude Code 2.1.x: (1) it calls `["claude", …]`
which Windows `CreateProcess` can't resolve to `claude.cmd` (fix: `shutil.which`);
(2) it reads the subprocess pipe with `select`, which is socket-only on Windows
(fix: `communicate`); and (3) it injects the skill as a `.claude/commands/`
slash-command, which current Claude Code surfaces as a *user* command rather than
an autonomously-invokable skill — so the trigger signal never fires and every
query reads as "no trigger". (1) and (2) are one-line ports; (3) is a
core-mechanism mismatch. Until that's reconciled, treat these queries as the
durable asset and the description as validated by construction (it follows the
skill-creator authoring guidance: context-rich, appropriately pushy, names the
real high-value contexts, and is calibrated against the near-misses above).
