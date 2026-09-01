#!/usr/bin/env python3
"""Inspect DSLR/mirrorless RAW files — metadata + raw shape, no develop.

Thin CLI over the shared engine in ../../shared/scripts/raw_inspect.py —
this file only owns the camera-brand classification.
"""

from __future__ import annotations

import sys
from pathlib import Path

_SHARED = Path(__file__).resolve().parent.parent.parent / "shared" / "scripts"
if not (_SHARED / "raw_inspect.py").exists():
    sys.exit(
        "shared/ not found next to this skill.\n"
        "Install shared/ alongside camera-raw-grade/ (and phone-dng-grade/ if you use it) "
        "— see the repo README's install section."
    )
sys.path.insert(0, str(_SHARED))
from raw_inspect import run  # noqa: E402

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


def classify(exif: dict) -> tuple[str, str]:
    make = str(exif.get("Make", "")).lower()
    if "nikon" in make:
        return "nikon-nef", "Nikon NEF — usually compressed lossless; color science leans neutral-cool, push warmth deliberately."
    if "canon" in make:
        return "canon-cr2-cr3", "Canon CR2/CR3 — color science leans warm/skin-friendly out of the box; needs a recent libraw for CR3."
    if "sony" in make:
        return "sony-arw", "Sony ARW — older bodies write lossy-compressed ARW (visible highlight banding, 'star-eating' on long exposures); check ARW type in camera menu if it matters."
    if "fujifilm" in make or "fuji" in make:
        return "fuji-raf", "Fuji RAF — X-Trans sensor, not Bayer. Some demosaic paths produce a 'watercolor'/maze look at high clarity or sharpening; keep both modest and check 100%."
    if "olympus" in make or "om digital" in make or "om system" in make:
        return "olympus-orf", "Olympus/OM ORF — Micro Four Thirds; more depth of field at a given aperture, more visible noise at a given ISO than APS-C/full-frame."
    if "panasonic" in make:
        return "panasonic-rw2", "Panasonic RW2 — Micro Four Thirds or APS-C depending on body; check FocalLengthIn35mmFormat to know the crop factor."
    if "pentax" in make or "ricoh" in make:
        return "pentax-pef", "Pentax PEF/DNG — in-body sensor-shift stabilization can leave slight micro-blur at very slow shutter speeds even on a tripod; not a develop issue but worth noting if sharpening looks weak."
    if "leica" in make:
        return "leica-dng", "Leica DNG — native DNG, often M-mount manual lenses: check for wide-angle color shift (magenta/green corners) before trusting the crop tool's center bias."
    if exif.get("DNGVersion"):
        return "generic-dng", "Generic DNG — likely converted by Adobe DNG Converter or written natively; treat hints from Make/Model as unreliable."
    return "generic-raw", ""


if __name__ == "__main__":
    raise SystemExit(run(SUFFIXES, "Inspect DSLR/mirrorless RAW metadata", classify))
