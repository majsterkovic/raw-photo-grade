#!/usr/bin/env python3
"""Develop a DSLR/mirrorless RAW into a graded JPEG/TIFF.

Thin CLI over the shared engine in ../../shared/scripts/raw_develop.py —
this file only owns the camera-tuned LOOKS presets and accepted suffixes.
Defaults assume a larger sensor than a phone: less noise reduction by
default, a bit more shadow headroom, no computational tone-mapping baked
into the file already.
"""

from __future__ import annotations

import sys
from pathlib import Path

_SHARED = Path(__file__).resolve().parent.parent.parent / "shared" / "scripts"
if not (_SHARED / "raw_develop.py").exists():
    sys.exit(
        "shared/ not found next to this skill.\n"
        "Install shared/ alongside camera-raw-grade/ (and phone-dng-grade/ if you use it) "
        "— see the repo README's install section."
    )
sys.path.insert(0, str(_SHARED))
from raw_develop import run  # noqa: E402

LOOKS = {
    "neutral": {
        "exposure": 0.0,
        "contrast": 0,
        "highlights": 0,
        "shadows": 0,
        "whites": 0,
        "blacks": 0,
        "temperature": 0,
        "tint": 0,
        "vibrance": 0,
        "saturation": 0,
        "clarity": 0,
        "vignette": 0,
        "sharpen": 10,
        "noise_luma": 0,
    },
    "natural": {
        "exposure": 0.1,
        "contrast": 12,
        "highlights": -12,
        "shadows": 16,
        "whites": 4,
        "blacks": -6,
        "temperature": 2,
        "tint": -1,
        "vibrance": 10,
        "saturation": 2,
        "clarity": 10,
        "vignette": -4,
        "sharpen": 20,
        "noise_luma": 4,
    },
    "warm-golden": {
        "exposure": 0.15,
        "contrast": 14,
        "highlights": -18,
        "shadows": 18,
        "whites": 2,
        "blacks": -8,
        "temperature": 16,
        "tint": 4,
        "vibrance": 14,
        "saturation": 6,
        "clarity": 8,
        "vignette": -8,
        "sharpen": 18,
        "noise_luma": 4,
    },
    "cool-cinematic": {
        "exposure": -0.05,
        "contrast": 18,
        "highlights": -15,
        "shadows": 10,
        "whites": -4,
        "blacks": -14,
        "temperature": -12,
        "tint": -2,
        "vibrance": 6,
        "saturation": -4,
        "clarity": 12,
        "vignette": -12,
        "sharpen": 16,
        "noise_luma": 5,
    },
    "portrait": {
        "exposure": 0.2,
        "contrast": 8,
        "highlights": -10,
        "shadows": 22,
        "whites": 2,
        "blacks": -4,
        "temperature": 8,
        "tint": 3,
        "vibrance": 8,
        "saturation": -2,
        "clarity": 4,
        "vignette": -6,
        "sharpen": 12,
        "noise_luma": 6,
    },
    "food": {
        "exposure": 0.15,
        "contrast": 16,
        "highlights": -8,
        "shadows": 12,
        "whites": 8,
        "blacks": -8,
        "temperature": 10,
        "tint": 2,
        "vibrance": 18,
        "saturation": 8,
        "clarity": 16,
        "vignette": -6,
        "sharpen": 24,
        "noise_luma": 3,
    },
    "travel": {
        "exposure": 0.12,
        "contrast": 16,
        "highlights": -16,
        "shadows": 16,
        "whites": 6,
        "blacks": -10,
        "temperature": 6,
        "tint": 0,
        "vibrance": 16,
        "saturation": 6,
        "clarity": 14,
        "vignette": -6,
        "sharpen": 22,
        "noise_luma": 4,
    },
    "night": {
        "exposure": 0.2,
        "contrast": 10,
        "highlights": -25,
        "shadows": 10,
        "whites": -6,
        "blacks": -12,
        "temperature": -4,
        "tint": -2,
        "vibrance": 8,
        "saturation": 2,
        "clarity": 6,
        "vignette": -8,
        "sharpen": 12,
        "noise_luma": 12,
    },
    "editorial-flat": {
        "exposure": 0.2,
        "contrast": -8,
        "highlights": -6,
        "shadows": 20,
        "whites": -6,
        "blacks": 8,
        "temperature": 0,
        "tint": 0,
        "vibrance": 4,
        "saturation": -6,
        "clarity": 0,
        "vignette": 0,
        "sharpen": 10,
        "noise_luma": 3,
    },
}

SUFFIXES = {
    ".nef", ".NEF",
    ".cr2", ".CR2", ".cr3", ".CR3",
    ".arw", ".ARW",
    ".raf", ".RAF",
    ".orf", ".ORF",
    ".rw2", ".RW2",
    ".pef", ".PEF",
    ".srw", ".SRW",
    ".dng", ".DNG",
}

if __name__ == "__main__":
    raise SystemExit(run(LOOKS, "natural", SUFFIXES, "Develop DSLR/mirrorless RAW into a graded JPEG/TIFF"))
