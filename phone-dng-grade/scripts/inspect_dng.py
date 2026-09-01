#!/usr/bin/env python3
"""Inspect phone DNG files — metadata + raw shape, no develop.

Thin CLI over the shared engine in ../../shared/scripts/raw_inspect.py —
this file only owns the phone-family classification.
"""

from __future__ import annotations

import sys
from pathlib import Path

_SHARED = Path(__file__).resolve().parent.parent.parent / "shared" / "scripts"
if not (_SHARED / "raw_inspect.py").exists():
    sys.exit(
        "shared/ not found next to this skill.\n"
        "Install shared/ alongside phone-dng-grade/ (and camera-raw-grade/ if you use it) "
        "— see the repo README's install section."
    )
sys.path.insert(0, str(_SHARED))
from raw_inspect import run  # noqa: E402

SUFFIXES = {".dng", ".DNG"}


def classify(exif: dict) -> tuple[str, str]:
    make = str(exif.get("Make", "")).lower()
    model = str(exif.get("Model", "")).lower()
    software = str(exif.get("Software", "")).lower()
    if "apple" in make or "iphone" in model:
        return "iphone-proraw", "ProRAW — go easy on shadow lift and clarity; local tone mapping may already be baked into the file."
    if "google" in make or "pixel" in model or "hdr+" in software:
        return "pixel-dng", "Pixel DNG — white-balance tags can be misleading; start from camera WB and correct by eye."
    if "samsung" in make:
        return "samsung-dng", "Samsung DNG — often warm as-shot; check skin tones and LED-lit scenes."
    return "generic-dng", ""


if __name__ == "__main__":
    raise SystemExit(run(SUFFIXES, "Inspect phone DNG metadata", classify))
