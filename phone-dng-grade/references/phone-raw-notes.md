# Phone DNG notes

## Families

### iPhone ProRAW (.DNG)

- Computational RAW: demosaic + a local tone operator may already be in the file.
- Highlights can look recoverable on the phone preview and still collapse if you add exposure first. Pull `--highlights` before `--exposure`.
- Portrait mode is not ProRAW. If the user thinks a Portrait photo is RAW, inspect — it is usually HEIC.
- 48 MP files are slow. Always `--preview` first.
- Skin: keep `--clarity` ≤ 6 and `--saturation` ≤ 0 unless the shot is not a person.

### Google Pixel DNG

- Written by HDR+. As-shot WB tags in EXIF are sometimes inconsistent with what libraw applies. Trust the first preview, not the tag.
- Files may live in `Pictures/Raw` while JPEG sits in `DCIM/Camera`. GPS and some EXIF may be missing on the DNG.
- Color can swing magenta/green between software versions. Correct with `--tint`, not saturation.

### Samsung / other Android DNG

- Quality varies by app (stock camera vs Open Camera vs Lightroom mobile capture).
- Stock Samsung often runs warm. Check white shirts and teeth before adding `--temperature`.

## Shared phone limits

- Tiny pixels. Shadow lift of +30 looks clean at 200 px and dirty at 100%. Judge NR on the preview at 100% crop if the user cares about print.
- Rolling shutter and focus errors are not fixable here. If the frame is soft, do not add `--sharpen 30`.
- Ultrawide edges stretch faces. Prefer a tighter `--aspect` over "fixing" geometry.
- Do not apply DSLR landscape recipes (clarity 40, dehaze 30, sat 20). They read as HDR from 2016 on a phone file.

## Color order that actually works

1. Camera WB
2. Temperature / tint by eye on a neutral or a face
3. Exposure for the subject
4. Highlights / shadows
5. Contrast
6. Vibrance, then saturation
7. Clarity / sharpen / NR
8. Crop / vignette last

If the picture still looks cheap after that, the crop or the moment is the problem, not the grade.
