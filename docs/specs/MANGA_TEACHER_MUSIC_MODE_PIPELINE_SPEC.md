# Manga Teacher/Music Mode Pipeline Specification

**Status:** implemented contract · **Scope:** catalog planning through chapter writing  
**Authority:** `config/manga/manga_mode_vessels.yaml` and the brand identity registries

## Outcome

A manga brand with a teacher identity produces teacher-mode series. An active
music-registry brand produces music-mode series. The selected identity is not a
decorative byline: its approved source bank is loaded deterministically and
transformed through the genre-native vessel in story architecture and chapter
writing.

Teacher and music are mutually exclusive per series.

| Brand state | Planned series contract | Story contract |
|---|---|---|
| `teacher_id` is non-null | `mode: teacher`, no musician | doctrine is dramatized as wound → turn → renewal |
| active `music_brand_registry` row | `mode: music`, no teacher | sound motif transforms opening → recurrence → resolution |
| neither identity exists | legacy series; no mode injection | existing behavior |

## Required series-plan fields

```yaml
# Teacher
mode: teacher
teacher_id: ahjan
musician_id: null

# Music
mode: music
teacher_id: null
musician_id: ahjan
```

`assert_mode_xor()` is mandatory at catalog resolution and again at chapter
prompt assembly. A declared mode with a missing identity, both identities, a
missing bank, missing required music slot, or unknown genre vessel fails closed.

## Catalog behavior

Teacher brands already present in the strategic manga catalog keep their normal
market/genre allocations; every emitted series plan is stamped teacher-mode.

Music brands remain in `config/music/music_brand_registry.yaml`; they are not
inserted into the frozen 37-brand manga registry. Every active music brand gets
one initial series in each of the 15 supported genres for each requested locale.
This provides full vessel coverage while later performance data can adjust the
mix. Generate explicitly with:

```bash
PYTHONPATH=. python scripts/manga/generate_mode_brand_catalog.py \
  --brand ahjan_music --locale en_US --dry-run
```

`run_m7_wave_a.py` includes active music brands by default. Operators may use
`--exclude-music-brands` only for a deliberately teacher/legacy-only batch.

## Source-bank transformation

### Teacher mode

1. Resolve `teacher_id` from the series plan.
2. Select approved atoms deterministically from
   `SOURCE_OF_TRUTH/teacher_banks/<teacher_id>/approved_atoms/`.
3. Reject missing, empty, or placeholder-only selections.
4. Give the architect compact doctrine excerpts as internal source material.
5. Translate doctrine into genre events: conflict, consequence, a brief mentor
   line or modeled practice, and changed behavior.
6. Never paste an essay, make the teacher a fictional character by default, or
   name the teacher in-world.

Example: Ahjan's body-knows-first teaching becomes a mecha pilot overriding
somatic/synchronization warnings, a mechanic naming the cost, and the pilot
winning by settling into co-regulation with the chassis.

### Music mode

1. Resolve `musician_id` from an active music-brand row.
2. Load `profile.yaml`, `themes.yaml`, and one deterministic approved atom from
   each required slot: `LYRIC_OPENING`, `LYRIC_BESTSELLER_BEAT`, and
   `LYRIC_CLOSING`.
3. Reject inactive brands or incomplete banks.
4. Translate the sound identity into the genre vessel; do not teach doctrine.
5. Introduce the motif, transform it under pressure, and resolve it in-world.
6. Respect avoided themes and never attribute template text to the musician as a
   literal quotation.

Example: a psychological-horror story corrupts a safe lullaby, lets clean notes
return at the pivot, and resolves terror when the melody becomes whole.

## Pipeline contract

```text
brand registry
  → catalog mode resolution + XOR validation
  → series_plan mode/identity
  → identity source packet
  → genre vessel + three carrier beats
  → writer handoff (identity metadata + internal packet)
  → chapter prompt transformation rules
  → authored script
```

The source packet is internal provenance. Published dialogue must be newly
dramatized language, except where a separately approved quotation/license record
explicitly authorizes direct quotation.

## Acceptance gates

- Teacher catalog rows contain `mode=teacher`, a `teacher_id`, and no musician.
- Music catalog rows contain `mode=music`, a `musician_id`, and no teacher.
- Every supported genre has both vessels.
- The same inputs select the same source atoms.
- The architect output and writer handoff preserve mode and identity.
- Writer prompts contain the appropriate doctrine-or-motif transformation rule.
- Invalid identity/mode combinations and incomplete banks raise errors.
- Canonical proofs exist for Mecha+Ahjan Teacher and Horror+Ahjan Music.

Regression coverage: `tests/manga/test_mode_catalog_pipeline.py` and
`tests/manga/test_mode_wrapper.py`.
