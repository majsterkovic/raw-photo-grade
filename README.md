# raw-photo-grade

Two Claude Code skills that develop RAW photos like a photographer would: inspect the file, make a preview, actually look at it, then grade, crop, and export. Not a one-shot filter.

- **[phone-dng-grade](phone-dng-grade/)** — iPhone ProRAW, Google Pixel RAW+, Samsung Expert RAW DNG. Tuned for computational/linear DNG: baked-in tone-mapping, small-sensor noise, gain maps.
- **[camera-raw-grade](camera-raw-grade/)** — DSLR/mirrorless RAW: Nikon NEF, Canon CR2/CR3, Sony ARW, Fujifilm RAF, Olympus/OM ORF, Panasonic RW2, Pentax PEF, Leica/generic DNG. Tuned for real sensor headroom and brand color science.

Both skills share one RAW-processing engine (`shared/`) so the develop/crop/preview math is written and tested once. Each skill's own `SKILL.md` and `references/` stay focused on what's actually different for that camera type — see [writing-skills SDO guidance](https://github.com/obra/superpowers) on why the docs don't repeat themselves.

## Install

Copy all three folders — the skill(s) you want **and** `shared/` — as siblings into your skills directory. `shared/` is not a skill itself; it's imported by the skill scripts via a relative path, so it must sit next to them.

```bash
# personal skills (Claude Code)
cp -r phone-dng-grade camera-raw-grade shared ~/.claude/skills/

# or project-local
cp -r phone-dng-grade camera-raw-grade shared /path/to/project/.claude/skills/
```

Only need one camera type? Copy just that skill folder plus `shared/`:

```bash
cp -r camera-raw-grade shared ~/.claude/skills/
```

Then install the Python dependencies (same for both skills):

```bash
pip3 install -r phone-dng-grade/requirements.txt   # or camera-raw-grade/requirements.txt — identical
```

Needs `rawpy` (LibRaw binding), `numpy`, `Pillow`, and libraw itself on the system (`brew install libraw` / `apt install libraw-dev`). Canon CR3 needs a reasonably recent libraw.

## Usage

Once installed, mention what you're working with and Claude Code should pick up the right skill on its own — "grade this iPhone ProRAW" or "develop these NEF files from my D850 shoot." You can also invoke a skill's scripts directly:

```bash
python3 phone-dng-grade/scripts/inspect_dng.py photo.dng
python3 camera-raw-grade/scripts/inspect_raw.py photo.nef
```

See each skill's `SKILL.md` for the full workflow.

## Repo layout

```
phone-dng-grade/    skill: phone/computational DNG
camera-raw-grade/   skill: DSLR/mirrorless RAW
shared/              RAW decode + grade engine, imported by both skills' scripts (not a skill itself)
```

## License

MIT — see [LICENSE](LICENSE).
