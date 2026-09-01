#!/usr/bin/env python3
"""Crop a developed image with photographer-style aspect and anchors."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ASPECTS = {
    "original": None,
    "3:2": 3 / 2,
    "2:3": 2 / 3,
    "4:3": 4 / 3,
    "3:4": 3 / 4,
    "4:5": 4 / 5,
    "5:4": 5 / 4,
    "1:1": 1.0,
    "16:9": 16 / 9,
    "9:16": 9 / 16,
}


def parse_box(raw: str) -> tuple[float, float, float, float]:
    parts = [float(x.strip()) for x in raw.split(",")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("box = left,top,right,bottom in 0–1")
    left, top, right, bottom = parts
    if not (0 <= left < right <= 1 and 0 <= top < bottom <= 1):
        raise argparse.ArgumentTypeError("box must satisfy 0 ≤ L < R ≤ 1 and 0 ≤ T < B ≤ 1")
    return left, top, right, bottom


def attention_center(arr: np.ndarray) -> tuple[float, float]:
    """Rough subject point — contrast + saturation with mild center bias."""
    img = arr.astype(np.float32) / 255.0
    h, w = img.shape[:2]
    # downsample for speed
    step = max(1, min(h, w) // 240)
    small = img[::step, ::step]
    sh, sw = small.shape[:2]
    mx = small.max(axis=2)
    mn = small.min(axis=2)
    sat = mx - mn
    gray = small @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    gy = np.abs(np.diff(gray, axis=0, prepend=gray[:1]))
    gx = np.abs(np.diff(gray, axis=1, prepend=gray[:, :1]))
    edge = gx + gy
    yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
    cy, cx = (sh - 1) / 2.0, (sw - 1) / 2.0
    dist = np.sqrt(((yy - cy) / max(cy, 1)) ** 2 + ((xx - cx) / max(cx, 1)) ** 2)
    center = np.clip(1.0 - dist * 0.55, 0.15, 1.0)
    score = (0.55 * edge + 0.45 * sat) * center
    score = score - score.min()
    total = float(score.sum()) + 1e-8
    y = float((score * yy).sum() / total)
    x = float((score * xx).sum() / total)
    return x / max(sw - 1, 1), y / max(sh - 1, 1)


def tilt_angle_deg(arr: np.ndarray) -> float:
    """Estimate horizon tilt in degrees (y-down image coords) via a compact Hough vote.

    Strong edge pixels vote for (theta, rho); theta is deviation from a perfectly
    horizontal line's normal. Robust to quantization where gradient histograms fail.
    """
    gray = np.asarray(Image.fromarray(arr).convert("L"), dtype=np.float32) / 255.0
    h, w = gray.shape
    step = max(1, min(h, w) // 800)
    g = gray[::step, ::step]
    sh, sw = g.shape
    gy, gx = np.gradient(g)
    mag = np.hypot(gx, gy)
    thr = float(np.quantile(mag, 0.97))
    mask = mag >= max(thr, 1e-4)
    ys, xs = np.nonzero(mask)
    if xs.size < 200:
        return 0.0
    xs = xs.astype(np.float32) - sw / 2.0
    ys = ys.astype(np.float32) - sh / 2.0
    thetas = np.arange(-10.0, 10.001, 0.25)  # deviation from horizontal, degrees
    rad = np.radians(90.0 + thetas)  # normal angle of a near-horizontal line
    rho = xs[:, None] * np.cos(rad)[None, :] + ys[:, None] * np.sin(rad)[None, :]
    rho_bin = np.floor(rho * (2.0 / step)).astype(np.int32)
    scores = np.zeros(thetas.shape, dtype=np.float64)
    wts = mag[mask].astype(np.float64)
    for i in range(thetas.shape[0]):
        col = rho_bin[:, i] - rho_bin[:, i].min()
        scores[i] = float(np.bincount(col, weights=wts).max())
    a = float(thetas[int(np.argmax(scores))])
    return a if abs(a) <= 10.0 else 0.0


def inscribe_rect(w: int, h: int, angle_deg: float) -> tuple[int, int, int, int]:
    """Largest centered rectangle with original orientation inside w×h rotated by angle."""
    if abs(angle_deg) < 0.05:
        return 0, 0, w, h
    rad = abs(math.radians(angle_deg))
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    nw = int(math.floor(w * cos_a - h * sin_a))
    nh = int(math.floor(h * cos_a - w * sin_a))
    if nw <= w * 0.5 or nh <= h * 0.5 or nw < 16 or nh < 16:
        return 0, 0, w, h
    x0 = (w - nw) // 2
    y0 = (h - nh) // 2
    return x0, y0, x0 + nw, y0 + nh


def horizon_offset(arr: np.ndarray) -> float:
    """Estimate horizon row 0–1 using strongest horizontal edges in the middle third."""
    img = arr.astype(np.float32) / 255.0
    gray = img @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    step = max(1, min(arr.shape[:2]) // 400)
    g = gray[::step, ::step]
    dy = np.abs(np.diff(g, axis=0, prepend=g[:1])).mean(axis=1)
    # prefer middle 60%
    n = dy.shape[0]
    lo, hi = int(n * 0.2), int(n * 0.8)
    idx = lo + int(np.argmax(dy[lo:hi]))
    return idx / max(n - 1, 1)


def crop_rect(
    w: int,
    h: int,
    aspect: float | None,
    anchor: str,
    box: tuple[float, float, float, float] | None,
    arr: np.ndarray,
) -> tuple[int, int, int, int]:
    if box:
        left, top, right, bottom = box
        return (
            int(round(left * w)),
            int(round(top * h)),
            int(round(right * w)),
            int(round(bottom * h)),
        )

    if aspect is None:
        return 0, 0, w, h

    target = aspect
    src = w / h
    if src > target:
        nw = int(round(h * target))
        nh = h
    else:
        nw = w
        nh = int(round(w / target))
    nw = min(nw, w)
    nh = min(nh, h)

    if anchor == "center":
        cx, cy = 0.5, 0.5
    elif anchor == "subject":
        cx, cy = attention_center(arr)
    elif anchor == "top":
        cx, cy = 0.5, 0.35
    elif anchor == "bottom":
        cx, cy = 0.5, 0.65
    else:
        cx, cy = 0.5, 0.5

    x0 = int(round(cx * w - nw / 2))
    y0 = int(round(cy * h - nh / 2))
    x0 = max(0, min(x0, w - nw))
    y0 = max(0, min(y0, h - nh))
    return x0, y0, x0 + nw, y0 + nh


def main() -> int:
    p = argparse.ArgumentParser(description="Crop developed photo")
    p.add_argument("input")
    p.add_argument("-o", "--output", required=True)
    p.add_argument("--aspect", default="original", choices=sorted(ASPECTS))
    p.add_argument("--anchor", default="center", choices=["center", "subject", "top", "bottom"])
    p.add_argument("--box", type=parse_box, help="left,top,right,bottom in 0-1")
    p.add_argument("--horizon", action="store_true", help="Bias crop so estimated horizon sits on a third")
    p.add_argument("--straighten", action="store_true", help="Rotate to level dominant near-horizontal edge, then trim borders")
    p.add_argument("--quality", type=int, default=92)
    args = p.parse_args()

    src = Path(args.input).expanduser()
    dest = Path(args.output).expanduser()
    if not src.exists():
        sys.stderr.write(f"Not found: {src}\n")
        return 1

    im = Image.open(src).convert("RGB")
    straighten_angle = 0.0

    if args.straighten and args.box is None:
        straighten_angle = tilt_angle_deg(np.asarray(im))
        if abs(straighten_angle) >= 0.1:
            im = im.rotate(straighten_angle, resample=Image.BICUBIC, expand=False, fillcolor=(0, 0, 0))
            x0, y0, x1, y1 = inscribe_rect(im.width, im.height, straighten_angle)
            im = im.crop((x0, y0, x1, y1))

    arr = np.asarray(im)
    h, w = arr.shape[:2]
    aspect = ASPECTS[args.aspect]
    box = args.box

    if args.horizon and box is None:
        hy = horizon_offset(arr)
        # place horizon on upper or lower third, whichever is closer
        target_y = 1 / 3 if hy < 0.5 else 2 / 3
        if aspect is None:
            aspect = w / h
        # height of crop
        if w / h > aspect:
            nh = h
            nw = int(round(h * aspect))
        else:
            nw = w
            nh = int(round(w / aspect))
        y0 = int(round(hy * h - target_y * nh))
        y0 = max(0, min(y0, h - nh))
        x0 = (w - nw) // 2
        left, top, right, bottom = x0, y0, x0 + nw, y0 + nh
    else:
        left, top, right, bottom = crop_rect(w, h, aspect, args.anchor, box, arr)

    cropped = im.crop((left, top, right, bottom))
    dest.parent.mkdir(parents=True, exist_ok=True)
    suffix = dest.suffix.lower()
    if suffix in {".tif", ".tiff", ".png"}:
        cropped.save(dest)
    else:
        cropped.save(dest, format="JPEG", quality=args.quality, optimize=True)

    json.dump(
        {
            "input": str(src),
            "output": str(dest),
            "src_size": [w, h],
            "crop_px": [left, top, right, bottom],
            "crop_norm": [
                round(left / w, 4),
                round(top / h, 4),
                round(right / w, 4),
                round(bottom / h, 4),
            ],
            "aspect": args.aspect,
            "anchor": args.anchor,
            "straighten_angle": round(straighten_angle, 2),
        },
        sys.stdout,
        ensure_ascii=False,
        indent=2,
    )
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
