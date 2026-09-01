#!/usr/bin/env python3
"""Shared RAW develop engine — decode, grade, crop-friendly export.

Not a skill by itself. Each skill's own scripts/develop.py imports `run()`
from here and supplies its own LOOKS presets, default look, and accepted
file suffixes. The image-processing math (exposure, tone, color, clarity,
noise reduction, sharpen, vignette) is camera-agnostic; only the LOOKS
numbers and the RAW decode call should differ per camera family.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from raw_common import collect_inputs, linear_to_srgb, luma, require_rawpy, srgb_to_linear  # noqa: E402

SLIDER_KEYS = [
    "exposure",
    "contrast",
    "highlights",
    "shadows",
    "whites",
    "blacks",
    "temperature",
    "tint",
    "vibrance",
    "saturation",
    "clarity",
    "vignette",
    "sharpen",
    "noise_luma",
]


def parse_args(looks: dict, default_look: str, description: str) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=description)
    p.add_argument("inputs", nargs="+", help="RAW file(s) or folder")
    p.add_argument("-o", "--output", help="Output file (single input only)")
    p.add_argument("--out-dir", help="Output directory for batch")
    p.add_argument("--look", default=default_look, choices=sorted(looks))
    p.add_argument("--params", help="JSON with slider overrides")
    p.add_argument("--preview", action="store_true", help="Long edge 1600 JPEG")
    p.add_argument("--full", action="store_true", help="Full resolution")
    p.add_argument("--long-edge", type=int, default=0)
    p.add_argument("--tiff", action="store_true")
    p.add_argument("--quality", type=int, default=90)
    p.add_argument("--bright", type=float, default=1.0, help="rawpy bright")
    p.add_argument("--no-auto-bright", action="store_true")
    p.add_argument("--orient", default="auto", help="auto|0|90|180|270")
    for key in SLIDER_KEYS:
        typ = float if key == "exposure" else int
        p.add_argument(f"--{key.replace('_', '-')}", type=typ, default=None)
    return p.parse_args()


def merge_params(args: argparse.Namespace, looks: dict) -> dict:
    params = dict(looks[args.look])
    params["look"] = args.look
    if args.params:
        with open(args.params, encoding="utf-8") as fh:
            extra = json.load(fh)
        if isinstance(extra, dict):
            params.update({k: extra[k] for k in extra if k in SLIDER_KEYS or k == "look"})
    for key in SLIDER_KEYS:
        cli = getattr(args, key)
        if cli is not None:
            params[key] = cli
    return params


def decode_raw(path: Path, bright: float, no_auto_bright: bool) -> np.ndarray:
    require_rawpy()
    import rawpy

    with rawpy.imread(str(path)) as raw:
        rgb = raw.postprocess(
            use_camera_wb=True,
            bright=bright,
            no_auto_bright=no_auto_bright,
            output_bps=16,
            output_color=rawpy.ColorSpace.sRGB,
            highlight_mode=rawpy.HighlightMode.Blend,
            four_color_rgb=False,
        )
    return rgb.astype(np.float32) / 65535.0


def apply_orientation(img: np.ndarray, how: str, path: Path) -> np.ndarray:
    if how == "0":
        return img
    degrees = None
    if how in {"90", "180", "270"}:
        degrees = int(how)
    elif how == "auto":
        degrees = _exif_orientation_degrees(path)
    if not degrees:
        return img
    k = {90: 3, 180: 2, 270: 1}.get(degrees, 0)
    return np.rot90(img, k) if k else img


def _exif_orientation_degrees(path: Path) -> int:
    try:
        from PIL import Image

        with Image.open(path) as im:
            exif = im.getexif()
            orient = exif.get(274, 1) if exif else 1
        return {3: 180, 6: 90, 8: 270}.get(int(orient), 0)
    except Exception:
        return 0


def apply_grade(rgb: np.ndarray, p: dict) -> np.ndarray:
    lin = srgb_to_linear(np.clip(rgb, 0, 1))

    if p["exposure"]:
        lin *= 2.0 ** float(p["exposure"])

    # Temperature / tint in linear-ish RGB
    temp = float(p["temperature"]) / 100.0
    tint = float(p["tint"]) / 100.0
    if temp or tint:
        lin = lin.copy()
        lin[..., 0] *= 1.0 + 0.35 * temp + 0.12 * tint
        lin[..., 1] *= 1.0 - 0.08 * temp - 0.22 * tint
        lin[..., 2] *= 1.0 - 0.40 * temp + 0.12 * tint

    lin = np.clip(lin, 0, None)
    y = luma(lin)

    # Highlights / shadows via luminance masks
    hi = float(p["highlights"]) / 100.0
    sh = float(p["shadows"]) / 100.0
    if hi or sh:
        hi_mask = np.clip((y - 0.45) / 0.55, 0, 1)[..., None]
        sh_mask = np.clip((0.40 - y) / 0.40, 0, 1)[..., None]
        if hi < 0:
            lin = lin / (1.0 + hi_mask * (-hi) * 1.4)
        elif hi > 0:
            lin = lin * (1.0 + hi_mask * hi * 0.35)
        if sh:
            lin = lin + sh_mask * sh * 0.12
            lin *= 1.0 + sh_mask * sh * 0.15

    # Whites / blacks — pivot near ends
    wh = float(p["whites"]) / 100.0
    bl = float(p["blacks"]) / 100.0
    if wh:
        lin = lin * (1.0 + wh * 0.25)
    if bl:
        lin = lin + bl * 0.04
        lin = np.clip(lin, 0, None)

    # Contrast around mid-grey in linear
    contrast = float(p["contrast"]) / 100.0
    if contrast:
        mid = 0.18
        lin = (lin - mid) * (1.0 + contrast * 0.9) + mid
        lin = np.clip(lin, 0, None)

    srgb = np.clip(linear_to_srgb(lin), 0, 1)

    sat = float(p["saturation"]) / 100.0
    vib = float(p["vibrance"]) / 100.0
    if sat or vib:
        gray = luma(srgb)[..., None]
        if sat:
            srgb = gray + (srgb - gray) * (1.0 + sat)
        if vib:
            # Vibrance protects already-saturated pixels
            mx = srgb.max(axis=2, keepdims=True)
            mn = srgb.min(axis=2, keepdims=True)
            already = np.clip((mx - mn) * 1.6, 0, 1)
            srgb = gray + (srgb - gray) * (1.0 + vib * (1.0 - already))

    srgb = np.clip(srgb, 0, 1)

    if p["clarity"]:
        srgb = _clarity(srgb, float(p["clarity"]) / 100.0)
    if p["noise_luma"]:
        srgb = _luma_nr(srgb, float(p["noise_luma"]) / 100.0)
    if p["vignette"]:
        srgb = _vignette(srgb, float(p["vignette"]) / 100.0)
    if p["sharpen"]:
        srgb = _sharpen(srgb, float(p["sharpen"]) / 100.0)

    return np.clip(srgb, 0, 1)


def _box_blur(img: np.ndarray, radius: int) -> np.ndarray:
    if radius < 1:
        return img
    # Separable box via cumulative sum — fast enough for previews and full-res stills
    pad = radius
    x = np.pad(img, ((pad, pad), (pad, pad), (0, 0)), mode="edge")
    c = np.cumsum(x, axis=0)
    v = c[2 * radius :, :, :] - c[: -2 * radius, :, :]
    c = np.cumsum(v, axis=1)
    h = c[:, 2 * radius :, :] - c[:, : -2 * radius, :]
    area = float((2 * radius) * (2 * radius))
    return h / area


def _clarity(img: np.ndarray, amount: float) -> np.ndarray:
    # Mid-frequency contrast (unsharp with large radius)
    h, w = img.shape[:2]
    radius = max(3, int(min(h, w) * 0.012))
    blur = _box_blur(img, radius)
    return img + (img - blur) * amount * 1.4


def _sharpen(img: np.ndarray, amount: float) -> np.ndarray:
    radius = 1 if min(img.shape[:2]) < 2000 else 2
    blur = _box_blur(img, radius)
    return img + (img - blur) * amount * 1.8


def _luma_nr(img: np.ndarray, amount: float) -> np.ndarray:
    y = luma(img)
    radius = 1 if amount < 0.15 else 2
    # blur only luma, keep chroma
    y3 = np.repeat(y[..., None], 3, axis=2)
    yb = _box_blur(y3, radius)[..., 0]
    chroma = img - y[..., None]
    y_mix = y * (1.0 - amount * 0.7) + yb * (amount * 0.7)
    return np.clip(chroma + y_mix[..., None], 0, 1)


def _vignette(img: np.ndarray, amount: float) -> np.ndarray:
    h, w = img.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cy, cx = (h - 1) / 2.0, (w - 1) / 2.0
    r = np.sqrt(((yy - cy) / cy) ** 2 + ((xx - cx) / cx) ** 2)
    r = np.clip(r, 0, 1.6) / 1.6
    falloff = r * r
    return np.clip(img * (1.0 + amount * falloff[..., None]), 0, 1)


def resize_long_edge(img: np.ndarray, long_edge: int) -> np.ndarray:
    from PIL import Image

    h, w = img.shape[:2]
    m = max(h, w)
    if m <= long_edge:
        return img
    scale = long_edge / m
    nh, nw = max(1, int(h * scale)), max(1, int(w * scale))
    pil = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8), mode="RGB")
    pil = pil.resize((nw, nh), Image.Resampling.LANCZOS)
    return np.asarray(pil).astype(np.float32) / 255.0


def save_image(img: np.ndarray, dest: Path, quality: int, tiff: bool) -> None:
    from PIL import Image

    dest.parent.mkdir(parents=True, exist_ok=True)
    arr = (np.clip(img, 0, 1) * 255.0 + 0.5).astype(np.uint8)
    pil = Image.fromarray(arr, mode="RGB")
    if tiff or dest.suffix.lower() in {".tif", ".tiff"}:
        pil.save(dest, format="TIFF", compression="tiff_deflate")
    else:
        pil.save(dest, format="JPEG", quality=quality, optimize=True, subsampling=2)


def dest_path(src: Path, args: argparse.Namespace) -> Path:
    ext = ".tif" if args.tiff else ".jpg"
    if args.output and not args.out_dir:
        return Path(args.output).expanduser()
    folder = Path(args.out_dir).expanduser() if args.out_dir else src.parent / "edited"
    tag = "preview" if args.preview and not args.full else "edit"
    return folder / f"{src.stem}_{tag}{ext}"


def process_one(src: Path, dest: Path, args: argparse.Namespace, params: dict) -> dict:
    rgb = decode_raw(src, args.bright, args.no_auto_bright)
    rgb = apply_orientation(rgb, args.orient, src)
    long_edge = args.long_edge
    if args.preview and not args.full and not long_edge:
        long_edge = 1600
    if long_edge:
        rgb = resize_long_edge(rgb, long_edge)
    graded = apply_grade(rgb, params)
    save_image(graded, dest, args.quality, args.tiff)
    return {
        "input": str(src),
        "output": str(dest),
        "pixels": list(graded.shape[:2]),
        "params": params,
    }


def run(looks: dict, default_look: str, suffixes: set[str], description: str) -> int:
    """Entry point a skill's own develop.py calls with its LOOKS/suffixes."""
    args = parse_args(looks, default_look, description)
    files = collect_inputs(args.inputs, suffixes)
    if args.output and len(files) > 1:
        sys.stderr.write("-o only works for a single file. Use --out-dir for batches.\n")
        return 1
    params = merge_params(args, looks)
    reports = []
    for src in files:
        dest = dest_path(src, args)
        print(f"develop  {src.name}  ->  {dest}", file=sys.stderr)
        reports.append(process_one(src, dest, args, params))
    json.dump(reports if len(reports) > 1 else reports[0], sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0
