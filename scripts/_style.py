"""Back-compat shim. The preset now lives in the installable ``paperfig`` package.

Prefer `from paperfig import paper_style, save`. This shim lets scripts that do
`sys.path.insert(0, 'scripts'); from _style import paper_style, save` keep working.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paperfig.style import paper_style, save, PALETTE, MARKERS, LINESTYLES  # noqa: F401,E402
