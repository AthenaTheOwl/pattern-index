"""Root compatibility package for factory module path contracts.

The code lives in src/pattern_index/. Pointing __path__ only there lets
`python -m pattern_index` run from the repo root against that single copy.
"""

from __future__ import annotations

from pathlib import Path

__version__ = "0.1.0"

__path__ = [str(Path(__file__).resolve().parent.parent / "src" / "pattern_index")]
