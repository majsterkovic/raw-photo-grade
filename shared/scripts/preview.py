#!/usr/bin/env python3
"""Build a before/after contact sheet so the model can judge the grade."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def load_rgb(path: Path, long_edge: int) -> Image.Image:
    im = Image.open(path).convert("RGB")
    w, h = im.size
    m = max(w, h)
    if m > long_edge:
        scale = long_edge / m
        im = im.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.Resampling.LANCZOS)
    return im


def label(im: Image.Image, text: str) -> Image.Image:
    canvas = Image.new("RGB", (im.width, im.height + 36), (16, 16, 16))
    canvas.paste(im, (0, 36))
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 16)
    except OSError:
        font = ImageFont.load_default()
    draw.text((10, 8), text, fill=(240, 240, 240), font=font)
    return canvas


def main() -> int:
    p = argparse.ArgumentParser(description="Before/after sheet")
    p.add_argument("before")
    p.add_argument("after")
    p.add_argument("-o", "--output", required=True)
    p.add_argument("--long-edge", type=int, default=1200)
    p.add_argument("--labels", nargs=2, default=["BEFORE", "AFTER"])
    args = p.parse_args()

    a = Path(args.before).expanduser()
    b = Path(args.after).expanduser()
    dest = Path(args.output).expanduser()
    if not a.exists() or not b.exists():
        sys.stderr.write("Missing before or after file.\n")
        return 1

    left = label(load_rgb(a, args.long_edge), args.labels[0])
    right = label(load_rgb(b, args.long_edge), args.labels[1])
    # match heights
    h = min(left.height, right.height)
    if left.height != h:
        left = left.resize((int(left.width * h / left.height), h), Image.Resampling.LANCZOS)
    if right.height != h:
        right = right.resize((int(right.width * h / right.height), h), Image.Resampling.LANCZOS)
    gap = 12
    sheet = Image.new("RGB", (left.width + right.width + gap, h), (8, 8, 8))
    sheet.paste(left, (0, 0))
    sheet.paste(right, (left.width + gap, 0))
    dest.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(dest, format="JPEG", quality=88, optimize=True)
    print(dest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
