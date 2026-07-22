# Manga Wave-2 Items 1/2/4 Closeout — 2026-07-22

Agent: Pearl_Dev. Lane: manga_wave2_items124_20260722.
Spec: `docs/specs/MANGA_DRAWING_TRADITION_WAVE2_REIMPLEMENTATION_SPEC_20260721.md`
(not yet on origin/main as of this session — read from the shared working
tree `agent/bestseller-atom-flow-lanes-20260721`, local-only commit
`9db3b4f01d`; this closeout does not depend on that commit landing).

Base: fresh sparse clone of `origin/main` @ `6f7320fc424b9393f2d4364d0bf485af5207545b`
(the shared working directory was 44 commits behind and had a stray unmerged
untracked file from PR #75 — did not build on it, per instructions).

Item 3 (`assemble_from_bank.py` --bubbles genre-aware wiring) confirmed
already CODE-WIRED on origin/main via `aad5cf2152` — no action taken, per
the spec's own resolution note.

---

## Item 1 — Drawing-tradition backfill, wave 2

**Layer: CODE-WIRED.**

Six genres (`battle`, `sports`, `mystery`, `workplace`, `sci_fi_cyberpunk`,
`supernatural_everyday`) upgraded in
`config/manga/drawing_tradition_per_genre.yaml` from `deferred_phase2` stubs
to full A–H deep blocks (`A_line_tradition`, `B_ink_density_tonal_grammar`,
`C_body_language_expression`, `D_panel_framing`, `E_color_treatment`,
`F_forbidden_drift_patterns`, `G_mangaka_exemplars`, `H_token_mapping` per
`flux_schnell`/`qwen_image`/`animagine_xl_4_0`), matching the schema depth of
the 8 existing `top_8_deep` genres.

Status value used: `wave_2_deep` (not `top_8_deep`) — resolved the spec's own
open question by reading `phoenix_v4/manga/genre_tradition.py::resolve_tradition_genre()`:
it checks `block.get("status") != "deferred_phase2"`, so any non-deferred
status is already active. Confirmed by grep that no other code in the repo
branches on the literal string `"top_8_deep"` (only two config-fixture
occurrences in `tests/manga/test_prompt_builder.py`, unaffected). This was a
pure data change — no code changes were needed, matching the spec's own
prediction.

`psychological_horror` verified untouched (`status: top_8_deep`) and stays
distinct from `horror` (verified untouched, `status: deferred_phase2`) —
regression-tested in `test_psychological_horror_stays_distinct_from_deferred_horror`.

Wire-through check: `phoenix_v4/manga/chapter/visual_from_script.py` and
`scripts/manga/prompt_authority.py` both call `resolve_tradition_genre()` /
`genre_tradition_tokens()` generically for any genre — no hardcoded genre
allowlist found in either, so no changes were needed there (confirmed by
reading both files in full).

**Tests:** `tests/manga/test_genre_tradition_wiring.py` — 11/11 pass. Includes
one pre-existing test fixed (`test_deferred_phase2_genre_yields_nothing` used
`"battle"` as its deferred-genre example; battle is now `wave_2_deep`, so the
fixture genre was switched to `"essay"`, still deferred) plus 3 new tests:
`test_wave_2_deep_genre_resolves_tokens`,
`test_psychological_horror_stays_distinct_from_deferred_horror`,
`test_mystery_resolves_a_positive_and_negative_token_via_resolver`.

---

## Item 2 — Qwen Pearl Star worker

**Layer: CODE-WIRED** (graph-shape verified; **not** EXECUTED-REAL — no live
PNG render was attempted or claimed).

Re-verified the spec's baseline from scratch: `scripts/pearl_star/worker/
qwen_layered_manga_worker.py` (claimed 245 lines in the prior report) **does
not exist** on origin/main — confirmed by `find`, not assumed. Only
`scripts/pearl_star/worker/qwen_manga_worker.py` (207 lines) exists and
needed changes.

Diff against the reference workflow
(`scripts/image_generation/comfyui_workflows/qwen_image_no_pulid_manga.json`,
KSampler node `"5"`):
- **steps:** worker had `24`, reference has `28` → fixed to `28`.
- **cfg:** both `4.0` → unchanged.
- **split loaders** (UNETLoader/CLIPLoader/VAELoader): already present in the
  worker, structurally identical to the reference — no change needed there.
- **negative prompt:** the worker's `_NEG_SUFFIX` lacked the reference's
  CJK-character exclusions (`chinese characters, japanese characters, kanji,
  hiragana, katakana, hangul`) — added.

**Blob-gate added** (new, was absent from every file in
`scripts/pearl_star/worker/` before this PR): `_assert_blob_gate()` raises
`RuntimeError` when the landed PNG is under `MIN_PNG_BYTES = 50_000`,
mirroring the CI-side "stub-as-done" doctrine (CLAUDE.md) at the worker
boundary so Procrastinate's `retry=1` fires on a corrupt/stub render instead
of the task reporting `COMPLETED` silently.

**Stall-timeout machinery** (`STALL_WARN_S=180`, `STALL_KILL_S=600`,
`_poll_history(max_wait_s=900)`) was already present and unchanged — the
spec's "600s/900s" reference matches the kill-timeout / poll-ceiling values
already in place.

**Tests:** `tests/manga/test_qwen_manga_worker_graph.py` — 9/9 pass, real
execution (not a skip). The worker module does `from app import app`
(Procrastinate — pearl_star-host-only, not installed in this environment:
`import procrastinate` fails here on a missing `libpq` wrapper). Rather than
`importorskip` and risk the graph logic going untested in Core CI, the test
installs a minimal fake `app` module into `sys.modules` before import so the
actual changed logic (step count, cfg, negative-prompt shape, blob-gate)
gets always-on coverage. No live GPU or ComfyUI instance was used or needed.

**Live PNG smoke test: not attempted.** ComfyUI + the Qwen model trio
on-box availability on `pearl_star` was not confirmed this session (RAP
queue-first dispatch via `pscli` would be required, and was out of scope for
this lane per the smallest-safe-batch ordering — Item 2 was explicitly
gated on Items 1 and 4 landing first). Do not read this closeout as a
rendered-panel proof; that requires a follow-up session with `pscli`-queued
dispatch and a byte-verified output path.

---

## Item 4 — Style default removal

**Layer: CODE-WIRED.**

New module `phoenix_v4/manga/style_resolution.py` implements the documented
7-layer authority chain: explicit override → script style → request style →
teacher archetype → profile grammar → genre-family signal → `grounded_realism`
fallback (source tag `narrow_fallback`). Every layer fails open; a missing
signal simply falls through to the next layer.

- **Teacher archetype** (`TEACHER_STYLE_MAP`): empty today — no per-teacher
  style convention exists in the repo yet; documented as fail-open by design,
  not a gap in this PR.
- **Profile grammar**: reads `config/manga/format_adaptation_grammars.yaml`
  per `format_id` for an optional `style_id` field. No format currently
  declares one, so this layer is a documented no-op until one does —
  consistent with the fail-open pattern used throughout
  `phoenix_v4/manga/genre_tradition.py`.
- **Genre-family signal** (`GENRE_STYLE_MAP`): an editorially curated mapping
  from all 25 canonical + wave-2 genre ids onto the 13 style archetypes in
  `config/manga/style_archetypes.yaml`. Unmapped genres fall through to the
  narrow fallback rather than guessing.

The 3 CLI entry points (`scripts/manga/run_chapter_production.py`,
`run_chapter_visual.py`, `run_manga_chapter.py`) had their `--style-id`
default changed from `"dark_psychological"` to `None`, and each now calls
`resolve_style_id(...)` and prints the resolved `style_id` + `source` to
stderr before compiling. `run_manga_chapter.py` reuses the existing
`_resolve_chapter_genre(workspace)` helper from
`phoenix_v4/manga/runner/chapter_runner.py` to source its genre signal (no
`chapter_script` dict available at that call site — it's DAG/workspace
driven, not chapter-script driven like the other two scripts).

**Test cases (re-verified against the actual code, not assumed from the
prior report):**
- `healing` → `cozy_iyashikei` (source=`genre_family_signal`) ✓
- `psychological_horror` → `dark_psychological` (source=`genre_family_signal`) ✓
- `mecha` → `power_progression` (source=`genre_family_signal`) ✓
- explicit override wins over script/request/teacher/genre signals ✓
- no-signal → `grounded_realism` (source=`narrow_fallback`) ✓

**Tests:** `tests/manga/test_style_resolution.py` — 10/10 pass, covering all
5 acceptance cases above plus authority-chain ordering (script beats genre
but not explicit override; request beats genre; genre read from
`chapter_script["genre"]` when not passed directly; genre-id normalization
handles case/separators).

All 3 touched CLI scripts import-checked clean
(`python3 -c "import scripts.manga.run_chapter_production"` etc. — no
import-time errors from the new `phoenix_v4.manga.style_resolution` import).

---

## Regression check

Confirmed the following pre-existing, unrelated test failures are **not**
caused by this PR: stashed all 3 commits' changes, re-ran the same failing
test files against clean `origin/main` @ `6f7320fc`, and they failed
identically (sparse-checkout artifacts in this session's narrow clone —
missing font/fixture directories under `tests/fixtures/` and `scripts/ci/` —
not present in the actual origin/main tree). None of the pre-existing
failures touch `style_resolution.py`, `qwen_manga_worker.py`,
`drawing_tradition_per_genre.yaml`, `genre_tradition.py`,
`run_chapter_production.py`, `run_chapter_visual.py`, or
`run_manga_chapter.py`.

Total new/modified test coverage this PR: **30 tests, 30 passing**
(10 style_resolution + 9 qwen_manga_worker_graph + 11 genre_tradition_wiring,
of which 8 pre-existed and 3 are new additions in that file).

## Known pre-existing CI blocker (not this PR's fault)

`origin/main`'s required "Core tests" check is red for every PR due to a
missing `config/manga/main_character_interaction_grammar.yaml` fixture that
`phoenix_v4/manga/story_quality/excellence_gate.py` depends on — confirmed
independently by two sibling lanes and the operator. PRs #53/#55/#75 are
racing to fix this exact gap; this PR does not touch that file and does not
attempt to fix it. If Core tests fails on this PR, verify the failure
signature matches that gap before treating it as this PR's regression.
