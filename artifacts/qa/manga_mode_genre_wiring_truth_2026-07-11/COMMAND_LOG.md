# COMMAND_LOG — manga mode/genre wiring (2026-07-11)

Authority base: `origin/main` = `a08403fa93dd21dc7e8625c51e3a4093ae3cebea` (unchanged vs last verified live SHA).

Worktree: `/Users/ahjan/phoenix_omega_worktrees/manga-mode-genre-wiring-20260711`
Branch: `agent/manga-mode-genre-wiring-20260711`

## Preflight

```bash
git fetch origin
git rev-parse origin/main   # a08403fa93dd21dc7e8625c51e3a4093ae3cebea
git worktree add -b agent/manga-mode-genre-wiring-20260711 \
  /Users/ahjan/phoenix_omega_worktrees/manga-mode-genre-wiring-20260711 origin/main
PYTHONPATH=. python3 scripts/git/push_guard.py   # OK
```

## Proofs (all from clean worktree)

### 1. M4 vessel wiring (forced helper)

```bash
PYTHONPATH=. python3 scripts/manga/prove_m4_vessel_wiring.py
# → BEHAVIORAL DIFF: PASS  (see prove_m4.log)
```

### 2. Real series setup — teacher + music

```bash
PYTHONPATH=. python3 scripts/manga/run_series_setup.py \
  --workspace artifacts/qa/manga_mode_genre_wiring_truth_2026-07-11/series_setup_teacher \
  --series-id stillness_anxiety_iyashikei --arc-id arc_anxiety \
  --genre-id iyashikei --topic anxiety --mode teacher

PYTHONPATH=. python3 scripts/manga/run_series_setup.py \
  --workspace artifacts/qa/manga_mode_genre_wiring_truth_2026-07-11/series_setup_music \
  --series-id stillness_anxiety_iyashikei --arc-id arc_anxiety \
  --genre-id iyashikei --topic anxiety --mode music
```

Observed:
- teacher: `mode=teacher`, vessel=`the tea-house hands`, `genre_id=iyashikei` on internal + handoff
- music: `mode=music`, vessel=`the wind-chime that keeps the season`, `genre_id=iyashikei` on internal + handoff

### 3. Real pipeline — GENRE_ENGINE_UNDECLARED cleared

```bash
PYTHONPATH=. python3 scripts/run_manga_pipeline.py \
  --brand stillness_press --topic anxiety --genre iyashikei --mode teacher \
  --output-dir artifacts/qa/manga_mode_genre_wiring_truth_2026-07-11/pipeline_teacher_iyashikei \
  --backend noop --skip-pearl-star-check --chapter-count 1 --min-panel-images 56
# EXIT 0; chapter_script genre_id=iyashikei; no GENRE_ENGINE_UNDECLARED

PYTHONPATH=. python3 scripts/run_manga_pipeline.py \
  --brand stillness_press --topic anxiety --genre iyashikei --mode music \
  --output-dir artifacts/qa/manga_mode_genre_wiring_truth_2026-07-11/pipeline_music_iyashikei \
  --backend noop --skip-pearl-star-check --chapter-count 1 --min-panel-images 56
# EXIT 0; chapter_script genre_id=iyashikei mode=music; no GENRE_ENGINE_UNDECLARED
```

Note: `chapter_clearance=hold` from noop image backend (`PANEL_NOT_OK` / `MISSING_PAGE_PNG`) — expected; not a genre-engine failure.

### 4. CI smoke (honest — no genre patch)

```bash
PYTHONPATH=. python3 scripts/ci/smoke_manga_chapter_runner.py
# → smoke_manga_chapter_runner: OK
```

### 5. Targeted pytest

```bash
PYTHONPATH=. python3 -m pytest \
  tests/test_manga_series_setup.py \
  tests/test_manga_chapter_runner_e2e_replay.py -q
# → 9 passed
```

## Ghost doc

`docs/MANGA_BESTSELLER_STORY_WRITING_GUIDE.md` — **ABSENT** on this SHA; no authoritative recovery attempted (ghost-doc rule).
