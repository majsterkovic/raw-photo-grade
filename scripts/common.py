#!/usr/bin/env python3
"""Shared helpers for phone-dng-grade."""

from __future__ import annotations

import json
import sys
from pathlib import Path


DNG_SUFFIXES = {".dng", ".DNG"}
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp", ".JPG", ".JPEG", ".PNG"}


def require_rawpy():
    try:
        import rawpy  # noqa: F401
    except ImportError as exc:
        sys.stderr.write(
            "Brak pakietu rawpy. Zainstaluj libraw, potem:\n"
            "  pip3 install rawpy numpy Pillow\n"
            f"Szczegóły: {exc}\n"
        )
        sys.exit(2)


def collect_inputs(paths: list[str]) -> list[Path]:
    files: list[Path] = []
    for raw in paths:
        p = Path(raw).expanduser()
        if not p.exists():
            sys.stderr.write(f"Nie znaleziono: {p}\n")
            sys.exit(1)
        if p.is_dir():
            found = sorted(
                q
                for q in p.rglob("*")
                if q.is_file() and q.suffix in DNG_SUFFIXES
            )
            files.extend(found)
        else:
            files.append(p)
    if not files:
        sys.stderr.write("Brak plików DNG do przetworzenia.\n")
        exit(1)
    return files


def dump_json(data) -> None:
    json.dump(data, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


def srgb_to_linear(x):
    import numpy as np

    a = 0.055
    return np.where(x <= 0.04045, x / 12.92, ((x + a) / (1 + a)) ** 2.4)


def linear_to_srgb(x):
    import numpy as np

    a = 0.055
    x = np.clip(x, 0.0, None)
    return np.where(x <= 0.0031308, 12.92 * x, (1 + a) * np.power(x, 1 / 2.4) - a)


def luma(rgb):
    import numpy as np

    return rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722
