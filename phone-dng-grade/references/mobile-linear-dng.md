# Mobile / Linear DNG — what to know before you develop

Sources: Gemini analysis ("Tworzenie Skilla Claude Code DNG.md", 2026-08-28, verified),
rawpy/LibRaw docs, Halide's "Understanding ProRAW", hands-on experience from the
phone-dng-grade repo.

## Why phone DNG isn't classic Bayer RAW

| Trait | DSLR/mirrorless Bayer RAW | Mobile Linear DNG (ProRAW, Pixel RAW+, Samsung) |
|---|---|---|
| Data state | raw Bayer mosaic | multi-frame fusion, partially processed, linear |
| Noise reduction | done later, in post | partly done by the ISP before the file is written |
| Tonal metadata | static camera profiles | gain maps (ISO-21496-1 / Apple gain map), gain tables |
| White point | fixed ADC ceiling (e.g. 16383) | variable after frame fusion |
| Output space | camera matrix → sRGB | pre-profiled Linear sRGB / Display P3 |

## Hard develop rules (confirmed, implemented in develop.py)

1. `use_camera_wb=True` — the phone records accurate WB multipliers at capture time;
   ignoring them causes a color cast (Pixel in particular can go cold in shade / green under LED).
2. `no_auto_bright=True` — LibRaw's default is to linearly boost brightness toward a mean;
   on a mobile DNG that already has tone-mapping baked in, that crushes blacks and highlights.
   Correct exposure deliberately (`--exposure`), not via auto-bright.
3. Don't lift shadows as hard as you would on a full-frame file — noise lives in the shadows of a small sensor.
4. ProRAW already carries local tone-mapping: `--shadows` + `--clarity` maxed out reads as fake immediately.
5. 48/50 MP files: always preview on a ~1600 px long edge before a full-res export.
6. Orientation sometimes lives only in EXIF — `--orient auto` (the scripts' default) applies it;
   for manual operations outside the scripts, check rotation before cropping.
7. Gain maps (HDR DNG, iPhone 15+/Android Ultra HDR): the base JPEG is an SDR baseline;
   full HDR needs a gain-map parser — currently out of scope for this skill. If EXIF suggests
   HDR (Ultra HDR / gain map), tell the user rather than pretending you saw the full range.

## Simple crop geometry (implemented in crop.py)

- `--straighten` — a histogram of strong-edge orientations (a numpy equivalent of a Hough
  transform) finds the dominant near-horizontal line; rotation is capped at ±10°, then an
  inscribed rectangle keeps black corners out of the result. The angle comes back in JSON —
  if the crop looks MORE tilted after rotation, assume angle 0 and use `--box` or fix it by hand.
- `--horizon` — places the detected horizon at the 1/3 or 2/3 line (rule of thirds).

## When NOT to use this path

- Files with heavy retouching/layers already applied → start from the app's JPEG/TIFF instead.
- HDR gain-map as the final deliverable → needs a dedicated tool (e.g. ImageMagick ≥7.1 has partial HDR JPEG support).
- Local masking / object retouching needed → darktable/RawTherapee GUI, not this skill.
