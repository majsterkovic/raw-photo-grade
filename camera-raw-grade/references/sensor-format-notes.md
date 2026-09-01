# Sensor format notes

What changes with sensor size, independent of brand. Check `FocalLengthIn35mmFormat` vs `FocalLength` in the inspect report to know which of these applies.

## Full frame (~36×24mm)

- Most dynamic range and cleanest high ISO of the group. Shadow lift up to the top of the ranges in `look-recipes.md` is usually safe through ISO 3200–6400.
- Shallow depth of field at wide apertures — a face can be sharp while an ear is soft. Don't "fix" that with sharpening; it's the lens doing its job.
- Vignetting wide open on fast primes is normal and often flattering — don't reflexively correct it away.

## APS-C (~23.5×15.6mm, Canon APS-C ~22.3×14.9mm)

- Roughly 1.5× (1.6× Canon) crop versus full frame — a 35mm lens frames like a 50–56mm. Use `FocalLengthIn35mmFormat` for the real angle of view, not the printed focal length.
- Noise shows up about a stop earlier than full frame at the same ISO. Treat ISO 1600 on APS-C roughly like ISO 3200 on full frame for how much you push shadows and NR.
- Depth of field is deeper at the same aperture/framing than full frame — less separation, so clarity does more of the "pop" work than shadow-lift portrait tricks.

## Micro Four Thirds (~17.3×13mm)

- 2× crop factor — a 25mm lens frames like a 50mm.
- About 2 stops more depth of field than full frame at the same f-number and framing, and roughly 2 stops more visible noise at a given ISO. A "high ISO" MFT frame (ISO 1600+) needs the upper end of the noise_luma range in `look-recipes.md`; don't grade it with full-frame confidence.
- In-body/lens stabilization is aggressive on this format and can occasionally leave a faintly soft frame even at safe shutter speeds — check a preview at 100% before blaming the develop settings.

## Medium format (larger than full frame, e.g. Fujifilm GFX, Hasselblad X)

- Very shallow depth of field at typical apertures and very high resolution — sharpening halos are more visible than on any smaller format. Keep sharpen and clarity conservative and inspect at 100%.
- Exceptional shadow recoverability at base ISO; still respect the "too far" column in `look-recipes.md` rather than assuming the sensor makes any push safe.

## Rule of thumb across formats

Bigger sensor → more headroom, less noise per ISO step, shallower depth of field, more forgiving push on shadows/highlights. Smaller sensor → less headroom, treat every ISO step as costing more, lean on clarity/contrast instead of aggressive shadow lift for "pop". None of this changes brand color science — see `camera-raw-notes.md` for that.
