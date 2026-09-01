#!/usr/bin/env python3
"""Inspect phone DNG files — metadata + raw shape, no develop."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import collect_inputs, dump_json, require_rawpy  # noqa: E402


def exiftool_tags(path: Path) -> dict:
    if not shutil.which("exiftool"):
        return {}
    keys = [
        "Make",
        "Model",
        "Software",
        "DateTimeOriginal",
        "ISO",
        "ExposureTime",
        "FNumber",
        "FocalLength",
        "FocalLengthIn35mmFormat",
        "Orientation",
        "ColorMatrix1",
        "ColorMatrix2",
        "AsShotNeutral",
        "UniqueCameraModel",
        "DNGVersion",
        "ImageWidth",
        "ImageHeight",
        "DefaultCropSize",
        "SemanticName",
    ]
    cmd = ["exiftool", "-s", "-s", "-s"] + [f"-{k}" for k in keys] + [str(path)]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True)
    except subprocess.CalledProcessError:
        return {}
    tags = {}
    # exiftool without -json prints one value per requested tag that exists, not labeled.
    # Use JSON instead when available.
    try:
        raw = subprocess.check_output(
            ["exiftool", "-json", "-n"] + [f"-{k}" for k in keys] + [str(path)],
            stderr=subprocess.DEVNULL,
            text=True,
        )
        import json

        arr = json.loads(raw)
        if arr:
            row = arr[0]
            row.pop("SourceFile", None)
            return row
    except Exception:
        return {"exiftool_raw": out.strip()}
    return tags


def inspect_one(path: Path) -> dict:
    require_rawpy()
    import rawpy

    info = {
        "path": str(path.resolve()),
        "size_mb": round(path.stat().st_size / (1024 * 1024), 2),
        "suffix": path.suffix,
    }
    try:
        with rawpy.imread(str(path)) as raw:
            sizes = raw.sizes
            info["raw"] = {
                "raw_width": sizes.raw_width,
                "raw_height": sizes.raw_height,
                "width": sizes.width,
                "height": sizes.height,
                "iwidth": sizes.iwidth,
                "iheight": sizes.iheight,
            }
            try:
                info["num_colors"] = int(raw.num_colors)
            except Exception:
                pass
            try:
                info["camera_whitebalance"] = [float(x) for x in raw.camera_whitebalance]
            except Exception:
                pass
            try:
                info["daylight_whitebalance"] = [float(x) for x in raw.daylight_whitebalance]
            except Exception:
                pass
            try:
                info["black_level"] = int(raw.black_level_per_channel[0])
            except Exception:
                pass
            color_desc = getattr(raw, "color_desc", None)
            if color_desc:
                info["color_desc"] = (
                    color_desc.decode() if isinstance(color_desc, bytes) else str(color_desc)
                )
    except Exception as exc:
        info["error"] = f"{type(exc).__name__}: {exc}"

    extra = exiftool_tags(path)
    if extra:
        info["exif"] = extra

    make = str(extra.get("Make", "")).lower()
    model = str(extra.get("Model", "")).lower()
    software = str(extra.get("Software", "")).lower()
    if "apple" in make or "iphone" in model:
        info["family"] = "iphone-proraw"
        info["hint"] = (
            "ProRAW — ostrożnie z cieniami i clarity; lokalny tone-mapping bywa już w pliku."
        )
    elif "google" in make or "pixel" in model or "hdr+" in software:
        info["family"] = "pixel-dng"
        info["hint"] = (
            "Pixel DNG — WB tagi bywają mylące; startuj z camera WB i koryguj na podglądzie."
        )
    elif "samsung" in make:
        info["family"] = "samsung-dng"
        info["hint"] = "Samsung DNG — często ciepły as-shot; sprawdź skórę i neonowe LED."
    else:
        info["family"] = "generic-dng"

    return info


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect phone DNG metadata")
    parser.add_argument("inputs", nargs="+", help="DNG file or folder")
    parser.add_argument("--json", action="store_true", help="Print JSON")
    args = parser.parse_args()

    files = collect_inputs(args.inputs)
    reports = [inspect_one(p) for p in files]

    if args.json or len(reports) > 1:
        dump_json(reports if len(reports) > 1 else reports[0])
        return 0

    r = reports[0]
    print(f"file        {r['path']}")
    print(f"size        {r['size_mb']} MB")
    print(f"family      {r.get('family', '?')}")
    if "raw" in r:
        raw = r["raw"]
        print(f"raw size    {raw['raw_width']}×{raw['raw_height']}")
        print(f"active      {raw['width']}×{raw['height']}")
    if r.get("camera_whitebalance"):
        print(f"camera WB   {r['camera_whitebalance']}")
    if "exif" in r:
        ex = r["exif"]
        for key in (
            "Make",
            "Model",
            "Software",
            "DateTimeOriginal",
            "ISO",
            "ExposureTime",
            "FNumber",
            "FocalLength",
            "Orientation",
        ):
            if key in ex:
                print(f"{key:<12}{ex[key]}")
    if r.get("hint"):
        print(f"hint        {r['hint']}")
    if r.get("error"):
        print(f"error       {r['error']}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
