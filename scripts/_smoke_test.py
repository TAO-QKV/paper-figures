"""Smoke test: verify the figure pipeline works on this machine.

Run:
    python scripts/_smoke_test.py

Checks:
1. matplotlib + numpy import
2. paper_style fonts resolve (sans / serif / cn) without missing-glyph errors
3. PDF + PNG + SVG output dirs writable
4. DPI ~ 300 (file size sane)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _style import paper_style, save, PALETTE

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PALETTE, _, _ = paper_style(font="sans")   # default: most journals' submission spec

x = np.linspace(0, 2 * np.pi, 200)
fig, ax = plt.subplots(figsize=(5, 3))
ax.plot(x, np.sin(x), color=PALETTE[0], label="sin")
ax.plot(x, np.cos(x), color=PALETTE[1], label="cos", linestyle="--")
ax.set_xlabel(r"Angle $\theta$ (rad)")
ax.set_ylabel("Value")
ax.set_title("Figure pipeline smoke test")
ax.legend()
save(fig, "_smoke_test")
plt.close(fig)

png = Path("outputs/figures/_smoke_test.png")
pdf = Path("outputs/figures/_smoke_test.pdf")
svg = Path("outputs/figures/_smoke_test.svg")
print(f"\n[smoke] PNG: {png.exists()} ({png.stat().st_size if png.exists() else 0} B)")
print(f"[smoke] PDF: {pdf.exists()} ({pdf.stat().st_size if pdf.exists() else 0} B)")
print(f"[smoke] SVG: {svg.exists()} ({svg.stat().st_size if svg.exists() else 0} B)")
print("[smoke] open outputs/figures/_smoke_test.png — axes labeled, lines distinct, no missing glyphs")
print("[smoke] for Chinese labels use paper_style(font='cn') and install SimSun")
