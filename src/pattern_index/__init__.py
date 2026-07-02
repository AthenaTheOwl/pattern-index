"""Pattern Index public package."""

from __future__ import annotations

from pathlib import Path

__version__ = "0.1.0"

# The top-level pattern_index/ dir holds model.py and scoring.py. When src/ is
# imported first (pytest puts it on pythonpath), merge that dir onto __path__ so
# both halves resolve as one package, mirroring the root __init__ shim.
_ROOT_PACKAGE = Path(__file__).resolve().parents[2] / "pattern_index"
if _ROOT_PACKAGE.exists() and str(_ROOT_PACKAGE) not in __path__:
    __path__.append(str(_ROOT_PACKAGE))
