# Content bank wiring implementation
_Exported on 4/16/2026 at 19:27:10 GMT+8 from Cursor (3.1.15)_

---

**User**

══════════════════════════════════════════════════════════════════════
STARTUP_RECEIPT — Pearl_Dev
══════════════════════════════════════════════════════════════════════
AGENT:              Pearl_Dev
TASK:               Wire config content banks into renderer/composer/selector;
                    remove hard-coded locale/flow fallbacks; enforce doctrine
                    quarantine, publishable CONTENT GAP hard-fail, variant logging;
                    validate via anxiety/gen_z_professionals spine pilot + gates.
PROJECT_ID:         proj_state_convergence_20260328
SUBSYSTEM:          core_pipeline (primary); teacher_mode (doctrine/atoms touchpoints)
AUTHORITY_DOCS:     docs/CONTENT_FRAGMENT_VARIATION_WRITER_SPEC.md;
                    specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md;
                    specs/PHOENIX_V4_5_WRITER_SPEC.md;
                    docs/SESSION_UNITY_PROTOCOL.md;
                    artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv (core_pipeline row)
READ_PATH_COMPLETE: no — read spec + 8 YAMLs + affected modules before coding
WRITE_SCOPE:        phoenix_v4/rendering/*; phoenix_v4/planning/* (if selector lives there);
                    any module defining _LOC_VAR_FALLBACKS, _LOC_VAR_ROTATIONS,
                    _FLOW_GLUE_VARIANTS; new YAML loader package under phoenix_v4/ or
                    config/content_banks/* (read-only if already landed);
                    tests/*; scripts/run_pipeline.py only if wiring required;
                    artifact logger path TBD under artifacts/ (see §8)
OUT_OF_SCOPE:       unrelated refactors; Pearl News; video; marketing HTML;
                    changing gate thresholds unless spec requires
BLOCKERS:           none known — verify commit 0f8e4c65bc / PR #426 present locally
READY_STATUS:       ready after READ_PATH_COMPLETE = yes

Pearl_PM (before or in parallel): register or update ACTIVE_WORKSTREAMS row for this
implementation; branch agent/content-bank-wiring-<date>; base origin/main; no duplicate
workstream if one already tracks PR #426 follow-up.

Pearl_GitHub: preflight + push_guard before push; PR references workstream id; no mass deletes.

══════════════════════════════════════════════════════════════════════
MANDATORY READS (Pearl_Dev — complete before implementation)
══════════════════════════════════════════════════════════════════════
1) docs/CONTENT_FRAGMENT_VARIATION_WRITER_SPEC.md — full read; treat as contract.
2) The eight files under config/content_banks/*.yaml as introduced in commit:
      git show 0f8e4c65bc --stat
      git show 0f8e4c65bc:config/content_banks/
   (or checkout PR #426 branch and read on disk)
3) Grep the codebase for:
      _LOC_VAR_FALLBACKS
      _LOC_VAR_ROTATIONS
      _FLOW_GLUE_VARIANTS
      [CONTENT GAP:
   Map every call site; no orphan hard-coded lists after wiring.
4) Composer/renderer paths that inject:
      mechanism bridge, integration/practice glue, chapter takeaway
   (chapter_composer.py, book_renderer.py, enrichment_select.py or equivalents per repo).

Re-emit STARTUP_RECEIPT with READ_PATH_COMPLETE: yes once done.

══════════════════════════════════════════════════════════════════════
IMPLEMENTATION CHECKLIST
══════════════════════════════════════════════════════════════════════

(1) YAML loader for content banks
- Load all config/content_banks/*.yaml (or single index YAML if spec says so).
- Validate schema per CONTENT_FRAGMENT_VARIATION_WRITER_SPEC (required keys, types).
- Cache per process/run; clear errors on malformed bank (fail fast in CI/tests).

(2) Bank-aware selector
- API e.g. select_fragment(bank_id | slot_type, context) where context includes at minimum:
  topic_id, persona_id, frame (or frame_context), runtime_format_id, slot role
  (mechanism_bridge | integration_practice | chapter_takeaway | locale_var | flow_glue, etc. per spec).
- Filter: exclude entries that do not match any declared dimension in the YAML.
- Deterministic tie-break: stable hash from (book_id, chapter_index, slot_key, seed) or spec rule.

(3) Collision-family avoidance
- Spec likely defines collision_family or similar — track recently used families per chapter
  and/or per book; do not repeat within window; if exhausted, fail or WARN per spec (do not
  silently reuse if spec says hard-fail).

(4) Replace _LOC_VAR_FALLBACKS, _LOC_VAR_ROTATIONS, _FLOW_GLUE_VARIANTS
- Delete or reduce to thin shims that delegate to the bank selector only if spec allows
  backward compatibility during migration; end state: no duplicate prose source of truth.
- Grep gate: repository must not contain stale multi-line fallback literals that bypass banks
  (allow constants only for keys/ids if spec permits).

(5) Composer fallback selection (three targets)
- Mechanism bridge: use bank + context; same for integration/practice and chapter takeaway.
- Preserve existing ordering/section contracts from composer; only swap string source.

(6) Doctrine quarantine enforcement before enrichment slot fill
- Before enrichment fills slots, run quarantine check per spec (frame/doctrine rules).
- Block or strip disallowed fragments; log decision path for QA artifact.

(7) Hard failure for [CONTENT GAP: ...] in publishable runs
- When pipeline mode / quality profile indicates publishable (or non-draft), any remaining
  [CONTENT GAP: ...] token in composed text → raise or exit non-zero with clear message.
- Draft profile may WARN only if spec explicitly allows — default to spec wording.

(8) Artifact logging of selected variant_id values
- Per run, write JSONL or JSON under artifacts/ (path in spec or e.g.
  artifacts/pilots/<run_id>/content_variant_selection_log.json) listing:
  chapter_index, slot_key, bank_id, variant_id, collision_family, filters matched.
- Ensure log is written even on partial failure if useful for debug (or spec rule).

══════════════════════════════════════════════════════════════════════
VERIFICATION — spine pilot + gates
══════════════════════════════════════════════════════════════════════
Rerun anxiety / gen_z_professionals spine pilot (match repo’s canonical arc and flags), e.g.:

  PYTHONPATH=. python3 scripts/run_pipeline.py \
    --topic anxiety \
    --persona gen_z_professionals \
    --arc <canonical arc yaml from config/source_of_truth/master_arcs/> \
    --teacher ahjan \
    --pipeline-mode spine \
    --runtime-format standard_book \
    --render-book \
    --render-dir artifacts/pilots/content_bank_wiring_verify/ \
    --quality-profile draft   # or publishable if testing §7 hard-fail — run both if needed
    --no-job-check \
    --no-generate-freebies

Report explicitly:
- scene-anchor gate (or scene_anti_genericity / anchor density per repo naming): PASS | WARN | FAIL
- doctrine / frame gate: PASS | WARN | FAIL
- duplicate / semantic dedup / uniqueness: PASS | WARN | FAIL
- quality_summary.json: list each gate; note any SKIPPED

Attach paths: render dir, quality_summary.json, content_variant_selection log.

Tests: add pytest coverage for loader, selector filters, collision avoidance, and CONTENT GAP
detection on a minimal fixture chapter.

══════════════════════════════════════════════════════════════════════
CLOSEOUT_RECEIPT (Pearl_Dev — required)
══════════════════════════════════════════════════════════════════════
COMMIT_SHA:     <sha or PR link>
FILES_WRITTEN:  <list>
PILOT_RESULT:   <gate table + artifact paths>
STATUS:         completed | partial | blocked
HANDOFF_TO:     Pearl_PM / Pearl_GitHub / none
NEXT_ACTION:    <if partial: what blocks merge>

---

**Cursor**

Executing Pearl_Dev startup: reading the spec and content banks, grepping for hard-coded fallbacks, and mapping composer/renderer modules.



Locating the writer spec and content banks; workspace may lack PR #426 changes.



Checking out content banks from commit 0f8e4c65bc (not on current branch) and reading the spec from that commit.



Checking out `config/content_banks` from the commit, inspecting YAML slot types, and reading the rest of `chapter_composer` and `enrichment_select`.



Implementing the content-banks package, adding `global_locale_np_bank.yaml` (NP-shaped fragments for `{weather_detail}`-style placeholders; scene-anchor sentences don’t fit atom grammar), and wiring renderer, composer, and enrichment.



Creating `global_locale_np_bank.yaml` and the `content_banks` package via a short generator script, then wiring modules.



Implementing the core package files.



Updating `book_renderer.py`: removing hard-coded dicts and wiring bank helpers.



══════════════════════════════════════════════════════════════════════  
STARTUP_RECEIPT — Pearl_Dev (updated)  
══════════════════════════════════════════════════════════════════════  
AGENT: Pearl_Dev  
TASK: (same as prior message)  
READ_PATH_COMPLETE: **yes** — read `docs/CONTENT_FRAGMENT_VARIATION_WRITER_SPEC.md` (from commit `0f8e4c65bc` when absent on branch), all `config/content_banks/*.yaml`, grepped legacy symbols, and traced `book_renderer` / `chapter_composer` / `enrichment_select` / spine `run_pipeline` path.  
READY_STATUS: implementation delivered; spine pilot run was started in background and had not finished in-session (see CLOSEOUT).  
══════════════════════════════════════════════════════════════════════  

## What was implemented

### 1) YAML loader (`phoenix_v4/content_banks/loader.py`)
- Loads every `config/content_banks/*.yaml`.
- Handles multi-section scene banks (e.g. `anxiety_genz_scene_recognition_bank.yaml`) by merging list-valued sections that contain `variant_id`.
- Loads `spiritual_doctrine_quarantine_rewrite_bank.yaml` into `quarantine_entries` + `secular_replacements` (not validated as normal variant rows).
- Validates writer-spec §4 fields on standard variants; exposes `locale_np_keys()` for `{placeholder}` resolution.

### 2) Selector + collision + logging
- `selector.py`: `FragmentContext`, `select_fragment`, `select_locale_np`, `select_scene_anchor_replace`, `select_flow_glue`, `reflection_band_window`.
- Runtime aliasing (e.g. `standard_book` ↔ `standard_book_1h`), frame tags from `somatic_first`, list-based filters.
- `session.py`: `ContentBankSession` (flow-glue per-chapter caps / family spacing; book-level scene-anchor IDs).
- `variant_log.py`: JSONL append for `chapter_index`, `slot_key`, `bank_id`, `variant_id`, `collision_family`, `filters_matched`.

### 3) Removed hard-coded renderer/composer prose sources
- **`book_renderer.py`**: Dropped `_LOC_VAR_FALLBACKS`, `_LOC_VAR_ROTATIONS`, `_FLOW_GLUE_VARIANTS`. Locals use `global_locale_np_bank.yaml`; gray-window normalization and flow glue use `global_scene_anchor_bank` / `global_flow_glue_bank`. `strengthen_rendered_spine_manuscript(..., plan=...)` threads bank context.
- **`chapter_composer.py`**: Scene polish uses scene-anchor bank; mechanism bridge uses `mechanism_bridge_anxiety_nervous_system_bank` only after specific reflection branches (keeps regret/comparison/etc. prose); integration gap uses `anxiety_genz_practice_integration_bank` (INTEGRATION); takeaway fallback uses `chapter_takeaway_deep_book_bank` when runtime matches, else legacy template.

### 4) Doctrine quarantine + gap repair (`enrichment_select.py`)
- After registry resolution, runs `apply_doctrine_quarantine` (substring + secular replacement pick) and records `doctrine_quarantine_events` on the enrichment audit.
- Late-book **REFLECTION** gaps for `anxiety` + `gen_z_professionals`, ch ≥ 7: fills from `anxiety_genz_reflection_late_book_bank` with band window + JSONL logging when `content_variant_log_path` is set.

### 5) Publishable **CONTENT GAP** hard-fail
- `clean_for_delivery`: raises `DeliveryContractError` if `quality_profile == "production"` and `[CONTENT GAP:` remains.
- `delivery_contract_gate(..., plan=...)`: same check; `BookTxtWriter` passes `plan`.

### 6) Spine pipeline wiring (`scripts/run_pipeline.py`)
- Creates `render_dir` **before** enrichment; passes `content_variant_log_path` in `spine_context` and a richer `plan` into `clean_for_delivery` (topic/persona/quality/frame/seed).

### 7) New bank file
- **`config/content_banks/global_locale_np_bank.yaml`** — NP-shaped fragments migrated from the old `_LOC_*` literals so atom grammar like `{weather_detail} slides…` stays valid (scene-anchor **sentences** are not drop-in substitutes).

### 8) Tests
- **`tests/test_content_banks.py`** — loader/locale determinism, reflection filter, flow-glue session, production CONTENT GAP, JSONL logger, doctrine smoke. **8 passed** (~123s wall time; dominated by full bank YAML loads).

### Grep gate
- `phoenix_v4` has **no** `_LOC_VAR_FALLBACKS`, `_LOC_VAR_ROTATIONS`, or `_FLOW_GLUE_VARIANTS`.

---

══════════════════════════════════════════════════════════════════════  
CLOSEOUT_RECEIPT — Pearl_Dev  
══════════════════════════════════════════════════════════════════════  
COMMIT_SHA: **not committed** (working tree changes only; create branch `agent/content-bank-wiring-20260415` and commit when ready).  

FILES_WRITTEN / TOUCHED (high level):  
- `phoenix_v4/content_banks/__init__.py`, `loader.py`, `selector.py`, `session.py`, `variant_log.py`, `quarantine.py`  
- `config/content_banks/global_locale_np_bank.yaml`  
- `phoenix_v4/rendering/book_renderer.py`, `phoenix_v4/rendering/chapter_composer.py`  
- `phoenix_v4/planning/enrichment_select.py`, `scripts/run_pipeline.py`  
- `tests/test_content_banks.py`  
- Plus checked-out from `0f8e4c65bc`: existing eight writer banks + `docs/CONTENT_FRAGMENT_VARIATION_WRITER_SPEC.md` under `config/content_banks/` and `docs/`  

PILOT_RESULT: **not finalized here** — `scripts/run_pipeline.py` spine verify was launched toward `artifacts/pilots/content_bank_wiring_verify/` but the job was still running without further stdout after several minutes in this environment. Re-run locally and read:
- `artifacts/pilots/content_bank_wiring_verify/quality_summary.json` (chapter_flow, doctrine/frame via existing reports, dedup/uniqueness gates as named there)
- `artifacts/pilots/content_bank_wiring_verify/content_variant_selection_log.jsonl`
- `artifacts/pilots/content_bank_wiring_verify/chapter_flow_report.json` (and any scene-anchor sidecar your pipeline emits, e.g. under `scene_gate/`)

STATUS: **partial** — code + tests complete; pilot gate table and artifact paths need your local run confirmation.  

HANDOFF_TO: Pearl_GitHub (branch, `push_guard`, PR), Pearl_PM (workstream / ACTIVE_WORKSTREAMS).  

NEXT_ACTION: Commit on a clean branch from `origin/main`; run the spine command from your brief with `--quality-profile draft` then `production` to confirm §7 hard-fail; if the background pilot PID is stuck, stop it and rerun with logging.  
══════════════════════════════════════════════════════════════════════

