# Camera RAW notes

## Families

### Nikon NEF

- Usually compressed lossless; some older/high-speed modes use lossy compression — check `Compression` in EXIF if banding shows up in flat skies.
- Color science leans neutral-to-cool out of the box. Push warmth deliberately rather than assuming daylight WB nails it.
- Full-frame (Z6/Z7/D-series full-frame) vs APS-C/DX (Z50, Zfc, D7xxx) changes noise and DOF expectations — check `FocalLengthIn35mmFormat` vs `FocalLength` for the real crop factor.

### Canon CR2 / CR3

- CR3 needs a reasonably recent libraw/rawpy. An old install can fail to decode it entirely — treat that as a dependency problem, not a develop problem, and tell the user to update libraw.
- Color science leans warm and skin-friendly by default — often needs *less* warmth correction than other brands, not more.
- Dual Pixel RAW variants carry extra AF data; rawpy reads the image plane fine, the AF data is unused here.

### Sony ARW

- Older bodies can write lossy-compressed ARW (a menu setting: compressed vs uncompressed/lossless). Lossy mode shows visible highlight banding and, on long exposures, "star-eating" — faint stars or fine highlights get denoised away in-camera before the file is even written. No develop setting recovers detail that was never saved.
- Shadows at high ISO can carry a slight magenta cast — correct with `--tint`, not blanket desaturation.

### Fujifilm RAF

- X-Trans sensor, not a Bayer array — the color filter pattern is 6×6, not 2×2. Some demosaic algorithms produce a "watercolor" or maze-like smear in fine repeating detail (foliage, fabric, brick) especially when clarity or sharpen is pushed. Keep both modest and inspect at 100% before calling it done.
- Fuji's in-camera film simulations (Velvia, Classic Chrome, Acros, …) apply to the JPEG, not the RAF. Don't expect the RAW preview to look like the camera's screen.

### Olympus / OM System ORF, Panasonic RW2

- Micro Four Thirds sensor — smaller than APS-C. More depth of field at a given aperture (roughly 2 stops "slower" equivalent), and more visible noise at a given ISO than APS-C/full-frame. Don't apply full-frame high-ISO confidence here.
- Panasonic also ships APS-C bodies (some S-series) writing RW2 — check `FocalLengthIn35mmFormat` to know which sensor size you actually have.

### Pentax PEF / DNG

- In-body sensor-shift stabilization (and pixel-shift resolution modes) can leave faint micro-blur or a soft edge on some frames even on a tripod. Not a develop issue — don't chase it with sharpening.

### Leica DNG

- Native DNG, often shot on manual M-mount lenses with no in-camera correction profile. Wide-angle lenses can show a color shift (magenta/green) toward the corners from the lens's steep ray angles — check corners before trusting a center-biased subject crop.

### Generic / Adobe DNG Converter

- A RAW converted through Adobe DNG Converter carries the original sensor data but the Make/Model hints in this skill's classifier may be unreliable. Trust the raw pixel data and the preview over the brand-family hint.

## Shared camera limits

- A lens's own vignetting, distortion, and chromatic aberration are not corrected by this pipeline. Grading sliders fix exposure and color, not optics — don't chase a lens flaw with `--vignette` or `--clarity`.
- Sensor dust shows up as soft, repeating dark spots at small apertures (f/11 and smaller), especially in clear skies. Don't mistake it for noise or a grading artifact — it needs spot removal, which this skill doesn't do.
- Rolling-shutter skew (electronic shutter, silent mode) on fast motion or LED flicker banding under artificial light are capture-time problems. If the frame is warped or banded, do not try to fix it with sliders — reshoot or tell the user why it can't be salvaged.
- A 24–60 MP file shows sharpening halos far more readily on a real screen than a phone shot ever does on a phone screen. Default sharpen values here are calibrated conservative for that reason.

## Color order that actually works

1. Camera WB
2. Temperature / tint by eye on a neutral or a face
3. Exposure for the subject
4. Highlights / shadows
5. Contrast
6. Vibrance, then saturation
7. Clarity / sharpen / NR
8. Crop / vignette last

If the picture still looks flat after that, the light or the moment is the problem, not the grade.
