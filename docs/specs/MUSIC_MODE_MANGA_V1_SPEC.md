# MUSIC_MODE_MANGA_V1_SPEC — Music × Manga (R4)

**Status:** SPECCED (M4) · **Owner:** Pearl_Dev + Pearl_Research  
**NEW-ARTIFACT-JUSTIFIED:** vision-conformance audit R4 found **zero** music×manga treatment
on main. This spec applies existing music-mode infrastructure to the 15 music vessels.

## Lineage (reuse — do not greenfield)

| Prior art | What we reuse |
|---|---|
| PR #1580 lineage | data-driven mix + first-person wrapper patterns for music-mode books |
| `config/music/music_brand_registry.yaml` | active music brands (`mode: music`); Ahjan reference kit `ahjan_music` |
| `docs/specs/MUSIC_MODE_BRAND_INTEGRATION_V1_SPEC.md` | brand integration contract |
| `docs/specs/MUSIC_MODE_V2_PRODUCTION_READINESS_SPEC.md` | production readiness / open Qs |
| `config/manga/manga_mode_vessels.yaml` → `*.music` | 15 genre-native music vessels |
| `artifacts/manga/pilots/MANGA_MODE_WRAPPER_DESIGN.md` | XOR rule: music-mode has **no** sage/doctrine vessel |

## Contract

A music-mode manga series:

1. Sets `mode: music` on the series plan / story architecture.
2. Carries a `musician_id` (or music `brand_id` from the registry) — **never** a `teacher_id`.
3. Uses the genre's **music vessel** (opening→mid→closing), not the teacher vessel.
4. Makes the reader **feel** (anchor, motif, score) — never **instruct** (no doctrine captions).
5. Uses an **EI character-author** byline (manga convention), not the musician's legal name as
   author-of-record unless operator-ratified disclosure says otherwise.

## Data-driven mix (from #1580 lineage)

Book music-mode selects motif/lyric pools from musician banks. Manga applies the same idea
at the **vessel layer**:

- Series genre → `load_vessel(genre, "music")` → `{vessel, vessel_desc, beats}`.
- Story architect injects opening / mid / closing carrier beats (M4 wiring).
- Chapter-writer prompt receives the vessel block (M4 wiring).
- Panel craft: motif recurrence is visual + SFX + sparse lyric-sense captions — not essays.

## First-person wrapper (manga adaptation)

Books can use a musician's "note from your reader." Manga cannot narrate at the reader.
The first-person wrapper becomes:

- **Diegetic motif ownership:** a character hums, plays, or hears the vessel (shared song,
  sync-song, pirate frequency, etc.).
- **No fourth-wall musician monologue.**
- **Closing beat:** the motif resolves in-world (song finishes, armor hum steadies).

## Pilot (gated on M3 Wave 1)

| Field | Default (Q-M4-01) |
|---|---|
| Music brand | `ahjan_music` (first **active** entry in `music_brand_registry.yaml`) |
| Genre | `romance_josei_drama` (music vessel: "the shared song") |
| Locale | `en_US` |
| Path | through M3 chapter_script lane (`artifacts/manga/chapter_scripts/…/ep_001.yaml`) |
| Gate | `check_manga_story_authored.py` PASS + craft_notes cite music vessel |

**HOLD:** pilot script authoring waits for M3 Wave 1 pattern to land (#4614). Spec ships now;
pilot is a follow-PR (`agent/manga-m4-music-pilot-…`) once M3 is on main.

## Non-goals (V1)

- No new music brand registry fields.
- No GPU / render path.
- No teacher+music hybrid series (XOR is absolute).
- No paid LLM APIs.

## Exit proof (this PR)

- Spec file + CANONICAL_ARTIFACTS_REGISTRY row.
- Vessels wired for `mode=music` in story_architect + writer (same path as teacher).
- Pilot script: **HELD** on M3 Wave 1 (see CLOSEOUT ledger).
