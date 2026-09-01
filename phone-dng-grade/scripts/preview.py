#!/usr/bin/env python3
"""Build a before/after contact sheet so the model can judge the grade.

Shim — the implementation is camera-agnostic and lives in
../../shared/scripts/preview.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

_SHARED = Path(__file__).resolve().parent.parent.parent / "shared" / "scripts"
if not (_SHARED / "preview.py").exists():
    sys.exit(
        "shared/ not found next to this skill.\n"
        "Install shared/ alongside phone-dng-grade/ (and camera-raw-grade/ if you use it) "
        "— see the repo README's install section."
    )
sys.path.insert(0, str(_SHARED))
from preview import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
