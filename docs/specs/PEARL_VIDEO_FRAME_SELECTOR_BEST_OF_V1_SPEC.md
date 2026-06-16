# Pearl Video — Frame-Selector / Human Best-Of Curation v1 Spec

**Status:** Authored 2026-06-16 from the verified implementation; promoted to `docs/specs/`. Documents the previously-undocumented Stage 6 (human best-of curation) of the beat-driven method, rebuilt around the **"1 section = 1 picture"** section model. **Bundle with cap `PEARL-VIDEO-BEAT-DRIVEN-V1-01`** (serial governance lane).

**Extends:** `docs/specs/PEARL_VIDEO_BEAT_DRIVEN_NARRATIVE_PIPELINE_V1_SPEC.md` (Stage 6).
**Reference implementation:** `scripts/video/build_frame_selector_v2.py` → `frame_selector_v2.html`; consumed by `scripts/video/assemble_v3_8.py`. Currently **local-only + hardcoded** (CSV path, frames dir, version→base map baked in; see `CSV_PATH` / `FRAMES_DIR` / `MANGA_DIR` / `OUT_HTML` / `VERSION_BASES` at the top of the builder).

---

## Purpose

After the AI-judge gate (Stage 5) produces candidate frames across multiple versions (v3.1–v3.7), let the operator pick the single best frame **per picture across all versions** — a true multi-version best-of — and export that selection deterministically for assembly. This is the human-in-the-loop quality ceiling above the automated judge.

## Section model — "ONE SECTION = ONE PICTURE"

The builder's controlling invariant (`build_frame_selector_v2.py` module docstring): each HTML row is a single picture slot the operator chooses one image for. Beats are normalized into **sections** so that a row never crams multiple picture inputs together:

- **Split long beats.** A beat longer than `MAX_SEC` (**3.0s**) is split into N sections, one per sub-frame, so a long beat that needs 2–4 pictures becomes 2–4 sections. `n_pics_for(dur)` returns the fewest parts that keep every part `<= MAX_SEC` (and therefore each part stays well above the floor).
- **Merge short / zero beats.** A beat shorter than `MIN_SEC` (**0.5s**) — and zero-duration tail beats — is merged forward into a neighbour so **no section is ever shorter than half a second**. `MIN_SEC` is a hard floor.
- **Per-section image choices.** Every section shows its own choices: the chosen frame plus the natural alternative for each render version (v3.1–v3.7 via `VERSION_BASES`), and for every frame BOTH its REGULAR render and its MANGA counterpart. `manga_name()` mirrors `assemble_manga_v3_8.py::manga_path` (`manga_{base}`, `jpg`/`jpeg` → `png`).
- **Two-axis pick per section:** (a) WHICH frame (version), (b) REGULAR vs MANGA style.

## Workflow

1. **Generate selector** — `build_frame_selector_v2.py` reads the beat CSV, normalizes beats into sections (split/merge per the section model), and emits an HTML grid: per section, the chosen frame + all version alternatives, each shown as a REGULAR + MANGA pair.
2. **Flag problems** — the grid surfaces section status: `OK` (single), `SPLIT` (long beat broken into multiple pictures), `MERGED` (sub-`MIN_SEC` / zero beat coalesced forward), plus a "needs pick" filter; missing files are flagged.
3. **Operator selects** — two axes per section: which frame (version) and which style (REGULAR / MANGA).
4. **Export CSV** — a flat per-picture manifest, one row per section (schema below).
5. **Assemble** — `assemble_v3_8.py` reads the CSV and builds the final cut with **absolute-start-sec timing** (eliminates accumulated drift); each row is already one picture, so no further beat-splitting is required at assembly time.

## Export schema (flat per-picture manifest — verbatim)

The builder writes one row per section. Header (exact, from `build_frame_selector_v2.py` `exportCSV()`):

```
section,beat_num,beat_id,slot,start_sec,end_sec,duration_sec,chosen_frame,chosen_style,chosen_render
```

Column semantics:

| column | meaning |
| --- | --- |
| `section` | section index (one picture) |
| `beat_num` | source beat number the section came from |
| `beat_id` | source beat id |
| `slot` | slot letter within a split beat (`A`–`H`; `SLOT_LETTERS`) |
| `start_sec` | absolute start, seconds (3-dp) |
| `end_sec` | absolute end, seconds (3-dp) |
| `duration_sec` | section duration, seconds (3-dp) |
| `chosen_frame` | chosen frame filename |
| `chosen_style` | `regular` or `manga` |
| `chosen_render` | **resolved relative render path** — `manga` → `manga_frames/manga_{fname}`, regular → `frames/{fname}` |

**`chosen_render` is the resolved relative path** (computed by `renderPath(fname, style)` in the builder). A mixed regular/manga assembler can key off `chosen_render` directly without re-deriving the manga path. The downloaded file is `frame_selection_v2.csv`.

## Why it matters

v3.8 (the operator-curated best output) pulls frames from v3.1, v3.2, v3.4, v3.5 **and** v3.6 simultaneously — impossible without this tool. The section model additionally guarantees the assembler receives a clean flat manifest where every row is exactly one picture between `MIN_SEC` and `MAX_SEC`, so timing is deterministic and no row ever bundles multiple images. It is the step that turns "best automated cut" into "best achievable cut."

## Generalization target (W4)

De-hardcode: `build_frame_selector_v2.py --frames-dir --manga-dir --versions --out-csv` (drop the `~/Downloads` CSV and baked frame-base map). Once generalized, the *same tool* can back a **manga panel-selector** (Part B #4): operator picks the best panel variant per section. The two-axis (frame × style) picker already generalizes to (variant × engine).

## Open items

- Register with the beat-driven spec in `SUBSYSTEM_AUTHORITY_MAP.tsv`.
- Capture the `_compat` re-encode (Consolidation W6) so the post-assembly playback-compatibility step is no longer tacit.
- Mixed regular/manga assembler consumes the export schema above (`chosen_render` as the per-row source path).
