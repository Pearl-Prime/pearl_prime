# Music mode V1 — smoke notes (2026-05-06)

## Automated verification (this session)

- `pytest tests/test_music_overlay.py tests/test_music_composer.py tests/test_intro_conclusion_2p.py tests/test_book_companion_song.py tests/test_music_manuscript_overlay.py tests/test_musician_survey_derivation.py` — pass.
- `python3 scripts/ci/audit_llm_callers.py` — pass on scoped roots (`phoenix_v4`, `scripts/music`, `scripts/brand_admin`, `scripts/run_pipeline.py`).

## Full `deep_book_6h` spine smoke (operator)

Not executed here (long runtime / word-count gates). Canonical commands from the implementation receipt:

```bash
python3 scripts/run_pipeline.py \
  --topic anxiety \
  --persona gen_z_professionals \
  --arc config/source_of_truth/master_arcs/gen_z_professionals__anxiety__overwhelm__F013.yaml \
  --teacher ahjan \
  --seed 42 \
  --out artifacts/tmp/music_smoke_plan.json \
  --atoms-root atoms/ \
  --atoms-model cluster \
  --locale en-US \
  --pipeline-mode spine \
  --render-book \
  --render-dir artifacts/books/gen_z_professionals/anxiety/deep_book_6h_test_artist_alpha_lyrics_20260506/ \
  --quality-profile production \
  --no-job-check \
  --no-generate-freebies \
  --format deep_book_6h \
  --exercise-journeys \
  --music-mode with-lyrics \
  --musician-id test_artist_alpha
```

Repeat with `--music-mode no-lyrics` into a sibling `--render-dir`.

**Expected in `book.txt`:** `A note from your reader` (2P intro), `Closing note` (2P outro), per-chapter `--- Music` blocks (with-lyrics: lyric + reflection stacks; no-lyrics: reflections only). **`music_overlay_audit.json`** and **`section_packet_audit.json`** → `musician_overlay` when spine render runs with music flags.

**Companion prompt:** after a successful render,

```bash
python3 scripts/music/generate_book_companion_song.py \
  --book-output artifacts/books/gen_z_professionals/anxiety/deep_book_6h_test_artist_alpha_lyrics_20260506/book.txt \
  --musician-id test_artist_alpha \
  --out artifacts/books/gen_z_professionals/anxiety/deep_book_6h_test_artist_alpha_lyrics_20260506/companion_song_prompt.json
```

**Packaging:**

```bash
python3 scripts/brand_admin/package_book_with_music.py \
  --render-dir artifacts/books/gen_z_professionals/anxiety/deep_book_6h_test_artist_alpha_lyrics_20260506/ \
  --dest artifacts/books/gen_z_professionals/anxiety/package_test_artist_alpha_lyrics_20260506/ \
  --musician-id test_artist_alpha \
  --companion-json artifacts/books/gen_z_professionals/anxiety/deep_book_6h_test_artist_alpha_lyrics_20260506/companion_song_prompt.json
```

## Survey template (operator send)

Canonical YAML schema: `artifacts/musician_survey/SURVEY_TEMPLATE.yaml` (paste-ready prose lives in the operator chat / PR body).
