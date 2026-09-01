#!/usr/bin/env python3
"""Crop a developed image with photographer-style aspect and anchors.

Shim — the implementation is camera-agnostic and lives in
../../shared/scripts/crop.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

_SHARED = Path(__file__).resolve().parent.parent.parent / "shared" / "scripts"
if not (_SHARED / "crop.py").exists():
    sys.exit(
        "shared/ not found next to this skill.\n"
        "Install shared/ alongside phone-dng-grade/ (and camera-raw-grade/ if you use it) "
        "— see the repo README's install section."
    )
sys.path.insert(0, str(_SHARED))
from crop import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
