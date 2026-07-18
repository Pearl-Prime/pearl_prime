# BEFORE / AFTER — manga mode + genre wiring

Base SHA: `a08403fa93dd21dc7e8625c51e3a4093ae3cebea`

## Before (live origin/main)

| Surface | Behavior |
|---|---|
| `emit_series_setup` / `build_series_artifact_bundle` | No `mode` parameter; never called `build_story_architecture_internal(..., mode=...)` |
| Default `run_series_setup.py` | Emitted `story_architecture_*.json` with **no** `mode` / `mode_vessel` |
| `run_manga_pipeline.py` | No `--mode`; real path could not select teacher/music vessels |
| Story architecture | Forced M4 helper proved vessel injection; operator path did not |
| Chapter script | Stub/LLM writer did **not** stamp `genre` / `genre_id` |
| `run_manga_pipeline ... --genre iyashikei` | Hard-failed `MANGA.BESTSELLER.GENRE_ENGINE` → `GENRE_ENGINE_UNDECLARED` |
| CI smoke / e2e replay | Dishonestly patched `script["genre_id"] = ...` after generation |

## After (this branch)

| Surface | Behavior |
|---|---|
| `emit` / `build_series_artifact_bundle` | Accept `mode=`; pass through to architect |
| `build_story_architecture_internal` | Always stamps `genre_id` + `genre`; stamps `mode`/`mode_vessel` when mode set |
| `transmission` | Preserves `genre_id`/`genre`/`story_engine_genre` + `mode`/`mode_vessel` onto handoff |
| `writer_stub` + `writer._normalize_pair` | Propagate declared genre (+ mode) onto `chapter_script_writer_handoff` |
| CLIs | `--mode {teacher,music}` on `run_series_setup.py` and `run_manga_pipeline.py` |
| CI smoke / e2e | Assert genre present; **no** post-generation mutation |
| Real pipeline teacher+music | EXIT 0; declared genre present; **no** `GENRE_ENGINE_UNDECLARED` |

## Proof snapshots

- Teacher vessel: `the tea-house hands`
- Music vessel: `the wind-chime that keeps the season`
- Declared genre on chapter script (both modes): `iyashikei`
- Bestseller gate genre findings: none (`clearance=pass` on genre engine axis; image hold is noop-backend only)
