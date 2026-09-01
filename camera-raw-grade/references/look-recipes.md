# Look recipes

Named looks are starting points. After the first preview, change 2–4 sliders, not all of them.

## Slider ranges (develop.py)

| slider | typical | too far |
| --- | --- | --- |
| exposure | −0.4 … +0.6 EV | +1 unless it's a deliberate night lift |
| contrast | −10 … +20 | +35 (crunchy, halo) |
| highlights | −45 … +10 | +30 on a bright sky |
| shadows | 0 … +28 | +42 (flat, HDR look) |
| whites | −15 … +10 | |
| blacks | −20 … +8 | |
| temperature | −20 … +20 | ±40 unless mixed neon |
| tint | −8 … +8 | |
| vibrance | 0 … +20 | |
| saturation | −10 … +10 | +20 on skin |
| clarity | 0 … +16 landscape/architecture, 0 … +6 portrait | +25 |
| vignette | 0 … −12 | −25 |
| sharpen | 10 … 24 | 40 |
| noise_luma | 0 … 8 base-to-moderate ISO, 10–16 high ISO | 30 (plastic) |

Units: exposure is EV. Everything else is roughly −100…+100 like Lightroom, but the implementation is simpler — treat numbers as taste, not as a Lightroom match. Note the shadow/highlight/noise ranges are wider (and default noise reduction lower) than the phone version — a real sensor at base ISO earns that headroom.

## When to pick which look

- **neutral** — diagnostic. Use this for the first preview if the scene is unknown.
- **natural** — default client-safe finish. Daylight, family, documentary, anything without a gimmick.
- **warm-golden** — golden hour, interiors with tungsten, autumn light, skin in warm sun.
- **cool-cinematic** — blue hour, concrete, rain, night streets. Skin will go pale; add +temperature if a face is the subject.
- **portrait** — people close. Low clarity, gentle shadows, slight warm tint. Do not add food-level vibrance.
- **food** — plates, product, markets. Extra clarity and vibrance. Watch specular highlights on glossy surfaces.
- **travel** — punch without looking like a postcard filter. Good default for mixed outdoor sets.
- **night** — city lights, astro, long exposures. Pull highlights hard on light sources, modest shadow lift — a real sensor rarely needs the noise reduction a phone night mode needs.
- **editorial-flat** — fashion / lookbook / further grading later. Do not add vignette.

## Scene recipes (overrides on top of a look)

Overcast landscape, flat sky:

```
--look natural --contrast 18 --clarity 14 --highlights -10 --vibrance 8
```

Backlit portrait / rim light:

```
--look portrait --exposure 0.3 --highlights -30 --shadows 24 --whites -6
```

Golden hour sky hero:

```
--look warm-golden --highlights -30 --vibrance 16 --saturation 4 --clarity 10
```

Studio / mixed indoor white:

```
--look natural --temperature -6 --tint 4 --saturation -4 --vibrance 8
```

Astro / Milky Way:

```
--look night --exposure 0.15 --shadows 6 --noise-luma 10 --clarity 8 --vibrance 6
```

## Batch discipline

One shoot, one grade. If half the set is sun and half is shade, split into two param files rather than averaging a look that fits neither.
