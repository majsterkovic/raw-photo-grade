---
name: phone-dng-grade
description: Develop phone RAW DNG files (iPhone ProRAW, Pixel, Samsung) into finished photos with color grade, crop, and export. Use when the user mentions DNG, ProRAW, RAW from a phone, color grading, cropping phone photos, or editing like a photographer.
license: MIT
compatibility: Requires Python 3.10+ with rawpy numpy pillow. Optional exiftool and ImageMagick. Works on macOS and Linux.
metadata:
  version: "1.0"
  type: workflow
---

# Phone DNG Grade

Finish phone RAW (DNG / ProRAW) the way a working photographer would — inspect the file, make a small preview, look at it, then grade and crop. Do not dump a random filter and walk away.

Scripts live next to this file. Resolve them with `$SKILL_DIR` if set, otherwise the directory that contains this `SKILL.md`.

```bash
SKILL_DIR="${SKILL_DIR:-$(cd "$(dirname "$0")" && pwd)}"   # when unsure, ask the user where they installed the skill
python3 "$SKILL_DIR/scripts/inspect_dng.py" photo.dng
python3 "$SKILL_DIR/scripts/develop.py" photo.dng -o out.jpg --look natural --preview
```

## Hard rules

1. Never overwrite the original DNG. Write JPEG/TIFF next to it or into an `edited/` folder.
2. Always make a small preview first (`--preview` or `--long-edge 1600`) and **look at that image** with the Read tool before a final export.
3. Phone DNG is not a DSLR RAW. Small sensor, more noise, often some computational tone-mapping already in the file (especially iPhone ProRAW). Prefer modest moves.
4. Use camera white balance as the starting point (`use_camera_wb`). Only shift temperature/tint after you have seen a preview.
5. Lift shadows less than you would on a full-frame file. Noise lives in the shadows.
6. After each meaningful change, regenerate the preview and look again. Iterate 2–4 rounds, then export full-res.
7. If `rawpy` is missing, run `pip install -r "$SKILL_DIR/requirements.txt"` (needs libraw on the system). Do not invent a fake develop pipeline from JPEG.

## Workflow

### 1. Inventory

Find the files. Typical names: `IMG_1234.DNG`, `PXL_20260828_....dng`, `YYYYMMDD_HHMMSS.dng`.

```bash
python3 "$SKILL_DIR/scripts/inspect_dng.py" path/to/file.dng
python3 "$SKILL_DIR/scripts/inspect_dng.py" path/to/folder --json
```

Read make/model, ISO, shutter, aperture (often missing on phones), orientation, and whether an embedded preview exists. Note if it is iPhone ProRAW vs Pixel HDR+ DNG — that changes how hard you push highlights.

### 2. Neutral develop + preview

```bash
python3 "$SKILL_DIR/scripts/develop.py" photo.dng -o preview.jpg --look neutral --preview
```

Read `preview.jpg`. Describe what you actually see — exposure, color cast, crop problems, blown sky, muddy shadows, skin, horizon. Then pick a look.

### 3. Grade

Apply a named look, then override individual sliders. Values are Lightroom-style-ish, not 1:1 Lightroom.

```bash
python3 "$SKILL_DIR/scripts/develop.py" photo.dng -o graded.jpg \
  --look warm-golden \
  --exposure 0.25 --highlights -25 --shadows 18 \
  --temperature 8 --vibrance 12 --clarity 8 \
  --preview
```

Or write a params file and reuse it on a batch:

```bash
python3 "$SKILL_DIR/scripts/develop.py" photo.dng -o graded.jpg --params grade.json
python3 "$SKILL_DIR/scripts/develop.py" ./raw_folder --out-dir ./edited --look travel --preview
```

See `references/look-recipes.md` for starting recipes and slider ranges.

### 4. Crop like a photographer

Crop **after** you know the picture, not before. Prefer fewer pixels of emptiness over aggressive zoom that makes phone noise obvious.

```bash
python3 "$SKILL_DIR/scripts/crop.py" graded.jpg -o cropped.jpg --aspect 4:5 --anchor subject
python3 "$SKILL_DIR/scripts/crop.py" graded.jpg -o cropped.jpg --box 0.08,0.04,0.94,0.96
python3 "$SKILL_DIR/scripts/crop.py" graded.jpg -o cropped.jpg --aspect 3:2 --straighten --horizon
```

`--straighten` levels a tilted horizon first (gradient-orientation estimate, max ±10°, returns the angle in JSON); `--horizon` then places it on a third. If the straighten result looks worse, assume angle 0 and use `--box`.

Allowed aspects: `original`, `3:2`, `4:3`, `4:5`, `5:4`, `1:1`, `16:9`, `9:16`, `2:3`.

`subject` uses a simple attention heuristic (contrast + saturation + center bias). If the crop cuts a face or a limb, undo and pass `--box`. Never crop through a head.

### 5. Compare, then final export

```bash
python3 "$SKILL_DIR/scripts/preview.py" photo.dng graded.jpg -o compare.jpg
python3 "$SKILL_DIR/scripts/develop.py" photo.dng -o final.jpg --params grade.json --full
```

Final export defaults: sRGB JPEG q=90, longest edge unchanged, chroma 4:2:0, metadata preserved when possible. Use `--tiff` only if the user asked for a print master.

## How to look at a phone photo (checklist)

Work in this order. Do not start with saturation.

1. **Straighten and crop** — horizon, verticals, leftover edge pixels from the sensor, accidental fingers.
2. **White balance** — faces and neutrals first. Phone auto-WB is often too cold in shade and too green under LED.
3. **Exposure** — set the subject, not the average. On ProRAW, highlights clip in a different way than classic RAW; pull highlights before you add exposure.
4. **Contrast / curve** — one global contrast move, then highlights/shadows. Avoid the "HDR halo" look.
5. **Color** — vibrance before saturation. Skin — hold back orange/red saturation; lift luminance a touch if muddy.
6. **Presence** — clarity 5–15 for landscapes and food; 0–8 for portraits. Texture lives in `--clarity`; do not oversharpen.
7. **Noise and sharpen** — default NR is already on for ISO ≥ 250. Do not stack extra NR unless the preview is crunchy.
8. **Vignette** — optional, −4 to −12. Never so dark that corners look like a tunnel.

## Phone-specific traps

Read `references/phone-raw-notes.md` and `references/mobile-linear-dng.md` when the file is iPhone, Pixel, or Samsung.

- iPhone ProRAW already has local tone mapping. Extra shadow lift + extra clarity quickly looks fake.
- Pixel DNG white-balance tags are sometimes wrong; trust the camera as-shot multipliers from libraw, then correct by eye.
- 48 MP / 50 MP modes are huge. Always preview on a long edge of 1600 before full-res.
- Rotation is often in EXIF only. The scripts apply orientation; if a preview is sideways, pass `--orient auto` (default) or a 90/180/270.

## What "good" looks like

A finished phone photo should look like a careful edit of that scene, not a preset. Skin stays skin-colored. Skies keep gradient, not a flat cyan slab. Blacks are deep but not crushed to a silhouette unless the picture is a silhouette. If you would not show it in a client gallery, change it.

When the user asks for a style (film, cinematic, dirty Japan, clean Scandinavian, wedding, food), map it to a look in `references/look-recipes.md` and then tune from the preview — do not stop at the preset name.

## Batch

Same look across a set from one shoot is correct. Do not invent a new grade per frame unless lighting changed.

```bash
python3 "$SKILL_DIR/scripts/develop.py" ./DCIM --out-dir ./edited --look natural --preview
```

After previews exist, spot-check 3–5 frames (brightest, darkest, a face, a sky). Adjust the shared params, then `--full`.
