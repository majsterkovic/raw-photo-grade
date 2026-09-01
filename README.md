# phone-dng-grade

A [Claude Code](https://code.claude.com) skill that develops phone RAW files (DNG / iPhone ProRAW / Pixel / Samsung) the way a working photographer would: inspect, preview, color grade, crop, export.

## Install

```bash
# Personal skill (all projects)
mkdir -p ~/.claude/skills
cp -R phone-dng-grade ~/.claude/skills/phone-dng-grade

# Or project-local
mkdir -p .claude/skills
cp -R phone-dng-grade .claude/skills/phone-dng-grade
```

### System dependencies

**macOS**

```bash
brew install libraw
pip3 install -r ~/.claude/skills/phone-dng-grade/requirements.txt
```

**Debian / Ubuntu**

```bash
sudo apt-get install -y libraw-dev python3-pip
pip3 install -r ~/.claude/skills/phone-dng-grade/requirements.txt
```

Optional: `exiftool` (richer metadata) and ImageMagick (`convert`).

## Use in Claude Code

Drop `.dng` files into your project folder and ask, e.g.:

- "develop these DNGs like a photographer, warm tones, 4:5 crop"
- "make a preview of IMG_1234.DNG and dial in white balance and contrast"
- `/phone-dng-grade ./DCIM`

Claude should make a small preview first, **look at it**, iterate on the sliders, and only then export at full resolution — see `SKILL.md` for the full workflow and hard rules.

Manual / direct use:

```bash
SKILL=~/.claude/skills/phone-dng-grade
python3 "$SKILL/scripts/inspect_dng.py" photo.dng
python3 "$SKILL/scripts/develop.py" photo.dng -o preview.jpg --look warm-golden --preview
python3 "$SKILL/scripts/crop.py" preview.jpg -o cropped.jpg --aspect 4:5 --anchor subject
python3 "$SKILL/scripts/develop.py" photo.dng -o final.jpg --look warm-golden --full
```

## Looks

`neutral` `natural` `warm-golden` `cool-cinematic` `portrait` `food` `travel` `night` `editorial-flat`

Descriptions and slider ranges: `references/look-recipes.md`.

## Important

- The original DNG is never overwritten.
- iPhone ProRAW already carries some tone mapping — don't max out shadow lift and clarity.
- Small sensor = shadow noise. Nail exposure and white balance first; saturation last.

## License

MIT — see [LICENSE](LICENSE).
