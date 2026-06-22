"""Root compatibility package for factory module path contracts."""

from __future__ import annotations

from pathlib import Path

__version__ = "0.1.0"

_SRC_PACKAGE = Path(__file__).resolve().parent.parent / "src" / "pattern_index"
if _SRC_PACKAGE.exists():
    __path__.append(str(_SRC_PACKAGE))
