---
name: camera-raw-grade
description: Develop DSLR/mirrorless camera RAW files (Nikon NEF, Canon CR2/CR3, Sony ARW, Fujifilm RAF, Olympus/OM ORF, Panasonic RW2, Pentax PEF, Leica/generic DNG) into finished photos with color grade, crop, and export. Use when the user mentions a RAW from a dedicated camera, a lustrzanka/mirrorless shoot, NEF/CR2/CR3/ARW/RAF/ORF/RW2/PEF, or editing like a photographer for a full-frame/APS-C/MFT sensor.
license: MIT
compatibility: Requires Python 3.10+ with rawpy numpy pillow. Optional exiftool and ImageMagick. Works on macOS and Linux.
metadata:
  version: "1.0"
  type: workflow
---

# Camera RAW Grade

Finish DSLR/mirrorless RAW the way a working photographer would — inspect the file, make a small preview, look at it, then grade and crop. Do not dump a random filter and walk away.

This is the sibling of `phone-dng-grade`: same workflow shape, but tuned for a real camera sensor instead of a phone. No baked-in computational tone-mapping, more dynamic range headroom, brand-specific color science and RAW-format quirks to watch for.

Scripts live next to this file, plus a shared engine one level up. Resolve them with `$SKILL_DIR` if set, otherwise the directory that contains this `SKILL.md`.

```bash
SKILL_DIR="${SKILL_DIR:-$(cd "$(dirname "$0")" && pwd)}"   # when unsure, ask the user where they installed the skill
python3 "$SKILL_DIR/scripts/inspect_raw.py" photo.nef
python3 "$SKILL_DIR/scripts/develop.py" photo.nef -o out.jpg --look natural --preview
```

## Hard rules

1. Never overwrite the original RAW. Write JPEG/TIFF next to it or into an `edited/` folder.
2. Always make a small preview first (`--preview` or `--long-edge 1600`) and **look at that image** with the Read tool before a final export.
3. There is no computational tone-mapping baked into a camera RAW the way there is on a phone — you have real headroom in highlights and shadows, but that also means nothing has been done for you yet.
4. Use camera white balance as the starting point (`use_camera_wb`). Only shift temperature/tint after you have seen a preview.
5. Color science differs by brand: Canon leans warm/skin-friendly, Nikon leans neutral-cool, Sony can show a magenta cast in shadows at high ISO. Don't fight the brand's baseline before you've seen the preview.
6. After each meaningful change, regenerate the preview and look again. Iterate 2–4 rounds, then export full-res.
7. If `rawpy` is missing, run `pip install -r "$SKILL_DIR/requirements.txt"` (needs libraw on the system; Canon CR3 needs a recent libraw). Do not invent a fake develop pipeline from JPEG.

## Workflow

### 1. Inventory

Find the files. Typical names: `IMG_1234.CR2`, `IMG_1234.CR3` (Canon), `DSC_1234.NEF` (Nikon), `DSC01234.ARW` (Sony), `DSCF1234.RAF` (Fujifilm), `P1234567.RW2` (Panasonic), `_1234.ORF` (Olympus/OM), `IMG1234.PEF` (Pentax), `L1234567.DNG` (Leica).

```bash
python3 "$SKILL_DIR/scripts/inspect_raw.py" path/to/file.nef
python3 "$SKILL_DIR/scripts/inspect_raw.py" path/to/folder --json
```

Read make/model/lens, ISO, shutter, aperture, focal length (35mm-equivalent tells you the real crop factor) and orientation. Note the brand family — it changes color science expectations and which traps in `references/camera-raw-notes.md` apply.

### 2. Neutral develop + preview

```bash
python3 "$SKILL_DIR/scripts/develop.py" photo.nef -o preview.jpg --look neutral --preview
```

Read `preview.jpg`. Describe what you actually see — exposure, color cast, crop problems, blown sky, muddy shadows, skin, horizon. Then pick a look.

### 3. Grade

Apply a named look, then override individual sliders. Values are Lightroom-style-ish, not 1:1 Lightroom.

```bash
python3 "$SKILL_DIR/scripts/develop.py" photo.nef -o graded.jpg \
  --look warm-golden \
  --exposure 0.25 --highlights -25 --shadows 18 \
  --temperature 8 --vibrance 12 --clarity 8 \
  --preview
```

Or write a params file and reuse it on a batch:

```bash
python3 "$SKILL_DIR/scripts/develop.py" photo.nef -o graded.jpg --params grade.json
python3 "$SKILL_DIR/scripts/develop.py" ./raw_folder --out-dir ./edited --look travel --preview
```

See `references/look-recipes.md` for starting recipes and slider ranges.

### 4. Crop like a photographer

Crop **after** you know the picture, not before.

```bash
python3 "$SKILL_DIR/scripts/crop.py" graded.jpg -o cropped.jpg --aspect 4:5 --anchor subject
python3 "$SKILL_DIR/scripts/crop.py" graded.jpg -o cropped.jpg --box 0.08,0.04,0.94,0.96
python3 "$SKILL_DIR/scripts/crop.py" graded.jpg -o cropped.jpg --aspect 3:2 --straighten --horizon
```

`--straighten` levels a tilted horizon first (gradient-orientation estimate, max ±10°, returns the angle in JSON); `--horizon` then places it on a third. If the straighten result looks worse, assume angle 0 and use `--box`.

Allowed aspects: `original`, `3:2`, `4:3`, `4:5`, `5:4`, `1:1`, `16:9`, `9:16`, `2:3`. `3:2` is the native sensor ratio for most full-frame/APS-C bodies — prefer it unless the user asked for something else.

`subject` uses a simple attention heuristic (contrast + saturation + center bias). If the crop cuts a face or a limb, undo and pass `--box`. Never crop through a head.

### 5. Compare, then final export

```bash
python3 "$SKILL_DIR/scripts/preview.py" photo.nef graded.jpg -o compare.jpg
python3 "$SKILL_DIR/scripts/develop.py" photo.nef -o final.jpg --params grade.json --full
```

Final export defaults: sRGB JPEG q=90, longest edge unchanged, chroma 4:2:0, metadata preserved when possible. Use `--tiff` only if the user asked for a print master.

## How to look at a photo (checklist)

Work in this order. Do not start with saturation.

1. **Straighten and crop** — horizon, verticals, distracting edge elements.
2. **White balance** — faces and neutrals first. Trust camera WB more than on a phone; correct only what you can see is wrong.
3. **Exposure** — set the subject, not the average. RAW headroom means you can often recover a blown sky rather than re-shoot; pull highlights before adding exposure.
4. **Contrast / curve** — one global contrast move, then highlights/shadows. Avoid the "HDR halo" look from pushing both too hard.
5. **Color** — vibrance before saturation. Skin — hold back orange/red saturation; lift luminance a touch if muddy.
6. **Presence** — clarity 8–16 for landscapes/architecture, 0–6 for portraits. Do not oversharpen — a 24–60 MP sensor shows sharpening halos more readily than a phone screen ever will.
7. **Noise and sharpen** — default NR is light; a real sensor at base-to-moderate ISO needs far less than a phone. Only add more if a high-ISO frame is visibly gritty.
8. **Vignette** — optional, −4 to −12. Some lenses already vignette wide open; check before stacking more.

## Camera-specific traps

Read `references/camera-raw-notes.md` for brand/format detail and `references/sensor-format-notes.md` for full-frame vs APS-C vs Micro Four Thirds behavior.

- Fujifilm X-Trans (RAF) is not a Bayer sensor. High clarity or sharpening on some demosaic paths gives a "watercolor"/maze artifact in fine detail (foliage, fabric) — check at 100% before committing.
- Canon CR3 needs a reasonably recent libraw/rawpy; an old install may fail to decode it at all — that's a dependency problem, not a develop problem.
- Sony's older lossy-compressed ARW mode can show highlight banding and long-exposure "star-eating" (dim/soft stars vanish). If a night frame looks over-processed by the camera itself, that's baked in — no develop setting fixes it.
- A lens's own vignetting and distortion are not corrected here. Don't chase a lens flaw with grading sliders meant for exposure/color.
- Sensor dust shows up as soft dark spots at small apertures, especially in skies — don't mistake it for noise or a develop artifact.

## What "good" looks like

A finished photo should look like a careful edit of that scene, not a preset. Skin stays skin-colored. Skies keep gradient, not a flat cyan slab. Blacks are deep but not crushed to a silhouette unless the picture is a silhouette. If you would not show it in a client gallery, change it.

When the user asks for a style (film, cinematic, dirty Japan, clean Scandinavian, wedding, editorial), map it to a look in `references/look-recipes.md` and then tune from the preview — do not stop at the preset name.

## Batch

Same look across a set from one shoot is correct. Do not invent a new grade per frame unless lighting changed.

```bash
python3 "$SKILL_DIR/scripts/develop.py" ./DCIM --out-dir ./edited --look natural --preview
```

After previews exist, spot-check 3–5 frames (brightest, darkest, a face, a sky). Adjust the shared params, then `--full`.
