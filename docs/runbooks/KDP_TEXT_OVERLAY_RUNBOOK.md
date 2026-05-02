# KDP Text Overlay Runbook

## §1 What this pipeline does

FLUX produces a bare illustration. KDP requires a finished cover with title,
subtitle, and author rendered cleanly on top — at bestseller-grade typography.
Diffusion models cannot reliably render readable text, so the pipeline
splits the job:

1. **Illustration stage (FLUX)** — produces a bare 1600x2560 portrait.
2. **Typography stage (this pipeline)** — composites title + subtitle +
   author using Pillow (`PIL.ImageDraw.text` over `PIL.ImageFont.truetype`)
   from per-genre layout rules in YAML.

The output is the KDP-shipped cover: `cover_<book_id>_FINAL.png`.

Entry points:
- Library: `scripts/publish/render_kdp_cover.py::render_kdp_cover`
- CLI: `python3 scripts/publish/render_kdp_cover.py …`
- Batch: `python3 scripts/publish/render_kdp_cover.py --batch`

## §2 Composition: per-genre typography rules

Per-genre layouts live in `config/publishing/kdp_cover_typography.yaml`.
Each of the 9 production genres has its own block:
`anxiety`, `self_worth`, `overthinking`, `boundaries`, `burnout`, `grief`,
`courage`, `imposter_syndrome`, `sleep_anxiety`.

Each genre defines:
- `title_zone` — position (`top|center|bottom`), anchor, max-width %,
  max-height %, vertical offset.
- `title_style` — font family (`serif|sans_serif|display|script`), weight,
  size at canonical 1600x2560 canvas, tracking, case, color, drop shadow.
- `subtitle_style` — same shape as title_style.
- `palette_hints` — `prefer_light_text_if_dark_zone` flag and
  `hex_palette_fallback` colors used by auto-color.

**R1 status (as of 2026-04-30):** R1's
`artifacts/research/kdp_bestseller_cover_analysis_2026-05-02.md` was not yet
published when this pipeline shipped. Every genre block is currently flagged
`# REVISIT_AFTER_R1`. The defaults follow well-established bestseller
heuristics — large, clean serif title at top (or near-center for grief), small
caps author at bottom in sans-serif, generous negative space — but operators
should refine them after R1 lands by editing the YAML in place. The pipeline
needs no Python changes for that.

Auto-color uses Rec. 601 perceived luminance:
`L = 0.299 R + 0.587 G + 0.114 B`. The illustration's title-zone average
luminance is sampled; if `< 0.5` the pipeline picks the light fallback color,
otherwise the dark one.

## §3 CLI usage and library API

### Single render

```bash
python3 scripts/publish/render_kdp_cover.py \
    --illustration artifacts/pipeline_examples/ahjan/cover_ahjan_anxiety_v2_dev.png \
    --title "The Alarm Is Lying" \
    --subtitle "A Nervous System Guide to Anxiety Recovery" \
    --author "Ahjan" \
    --genre anxiety \
    --output artifacts/pipeline_examples/ahjan/cover_ahjan_anxiety_FINAL.png
```

Stdout includes the layout used, fitted title size, and contrast ratio:
```
wrote 1600x2560 → .../cover_ahjan_anxiety_FINAL.png
  layout=anxiety title_size=150px contrast=0.846
```

### Batch render (all teacher books)

```bash
python3 scripts/publish/render_kdp_cover.py --batch
```

For each `TEACHER_BOOKS` entry in `scripts/release/build_epub.py`, the batch
locates the most-recent `cover_<id>_*_v2_dev.png` (then `_v2_schnell.png`)
illustration in `artifacts/pipeline_examples/<id>/` and writes
`cover_<id>_FINAL.png` to the same directory. Books with no illustration are
reported as skipped without crashing the batch.

### Library

```python
from pathlib import Path
from scripts.publish.render_kdp_cover import render_kdp_cover

meta = render_kdp_cover(
    illustration_path=Path("…/cover_ahjan_v2_dev.png"),
    title="The Alarm Is Lying",
    author="Ahjan",
    subtitle="A Nervous System Guide to Anxiety Recovery",
    genre="anxiety",
    output_path=Path("…/cover_ahjan_FINAL.png"),
    publisher="Inner Light Press",            # optional
    typography_overrides={"title_style": {"color": "#FFFFFF"}},  # optional
)
# meta = {"output_path": …, "layout_used": "anxiety",
#         "title_size_px": 150, "contrast_ratio": 0.846, …}
```

`typography_overrides` is shallowly merged on top of the genre block, so
operators can pin a specific color or font family per render without editing
the YAML.

## §4 Genre layout customization

Operators edit `config/publishing/kdp_cover_typography.yaml`, **not** the
Python. Common edits:

- **Move title down** for a genre — change `title_zone.position` to
  `center` and bump `vertical_offset_pct`.
- **Force a hex color** for a genre — set `title_style.color: "#FFFFFF"`
  instead of `auto`.
- **Change font family** — flip `font_family` between `serif`,
  `sans_serif`, `display`, or `script`. Bundled fonts ship for the first
  three; `script` falls back to `Apple Chancery` on macOS.
- **Tighter letter-spacing** — set `tracking_pct` negative (e.g. `-1`).
- **Refine after R1** — replace each `# REVISIT_AFTER_R1` block with
  R1-derived font / size / position rules; remove the comment when done.

The YAML is hot-loadable: the next CLI/library call picks up changes
without a process restart.

## §5 Known limitations

- **9 production genres only** (`anxiety`, `self_worth`, `overthinking`,
  `boundaries`, `burnout`, `grief`, `courage`, `imposter_syndrome`,
  `sleep_anxiety`). Unknown genres raise `ValueError`. Add a new entry to
  the YAML to expand coverage.
- **Latin-script v1.** The bundled fonts (EB Garamond, Inter, Playfair
  Display) cover Latin and basic Latin-Extended. CJK is **not supported**:
  fragment teacher books `master_feung` (zh-CN) and `master_wu` (zh-TW)
  will need a separate non-Latin pipeline (Noto CJK or similar) before
  their finals ship.
- **No outline/stroke styling yet** — only fill + drop shadow. Add a
  `stroke` field to the YAML schema if needed later.
- **Font shrink is reactive, not predictive.** When a title is too long
  for its zone the renderer steps the size down by 4 px until it fits.
  For very long titles the result may be smaller than designed.

## §6 References

- **Source code:** `scripts/publish/render_kdp_cover.py`
- **Config:** `config/publishing/kdp_cover_typography.yaml`
- **Tests:** `tests/test_publish_render_kdp_cover.py`
- **Bundled fonts:** `assets/fonts/kdp_overlay/{eb_garamond,inter,playfair_display}/`
  (each with its `OFL.txt` license alongside)
- **TEACHER_BOOKS manifest:** `scripts/release/build_epub.py`
- **R1 typography analysis (when available):**
  `artifacts/research/kdp_bestseller_cover_analysis_2026-05-02.md`
- **Companion runbook:** `docs/runbooks/COVER_REGENERATION_PLAN_2026-04-30.md`
- **KDP cover spec:** Amazon Help G200645690 (1600x2560 portrait, 1.6:1).
