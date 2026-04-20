from __future__ import annotations

"""Ensure the src/ layout is importable in local shells before installation."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if SRC.exists():
    sys.path.insert(0, str(SRC))
