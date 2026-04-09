from __future__ import annotations

from pathlib import Path

_ROOT = Path(__file__).resolve().parent
_SRC_PACKAGE = _ROOT.parent / "src" / "christian_social_intuition"

__path__ = [str(_ROOT)]
if _SRC_PACKAGE.exists():
    __path__.append(str(_SRC_PACKAGE))
