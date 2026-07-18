# Handoff — Bestseller Pipeline P0/P1 + Teacher Showcase Reels
**Session date:** 2026-04-20  
**Branch base:** `origin/main` (at `e186888ed1` by end of session)  
**Author:** Claude (Pearl_GitHub session)

---

## 1. What Was Done

### 1.1 Bestseller Pipeline — P0 Actions (3 PRs, all merged)

| PR | ACT | BSG | Title | Key file(s) |
|----|-----|-----|-------|-------------|
| #460 | ACT-001 | BSG-002 | Phase-aware bestseller structure assignment | `phoenix_v4/planning/chapter_planner.py` |
| #462 | ACT-002 | BSG-007 | Content gap markers hard-fail in production | `scripts/run_pipeline.py`, `phoenix_v4/planning/enrichment_select.py` |
| #463 | ACT-003 | BSG-015 | Chapter thesis bank connected to composer | `config/planning/chapter_thesis_bank.yaml` (NEW), `phoenix_v4/rendering/chapter_composer.py` |

**ACT-001 detail (PR #460)**  
Replaced hash-based (non-deterministic) bestseller structure assignment with a phase-aware system. Chapters are now bucketed into 5 phases by position percentage, and structures are drawn from phase-appropriate pools (`_PHASE_POOLS`). `MAX_BESTSELLER_RUN=3` enforced within pool, then globally. Fixed a spec/code mismatch: spec said `the_letter` but constant is `letter`.

**ACT-002 detail (PR #462)**  
Added a post-enrichment gap scan in `scripts/run_pipeline.py`. After `select_enrichment()`, iterates all slots and raises `SystemExit` with `[PRODUCTION GATE]` if any `[CONTENT GAP` markers survive. Also tightened `_publishable_book` condition. Gap logger error now explicitly names topic + slot_type so the operator knows exactly what to fill.

**ACT-003 detail (PR #463)**  
Created `config/planning/chapter_thesis_bank.yaml` from `docs/CHAPTER_THESIS_BANK.md` — 20 chapter intents × 4 engine types. Wired a 4-stage thesis chain into `chapter_composer.py`: (1) arc-provided thesis, (2) bank lookup by `(chapter_intent, engine_type)`, (3) `mechanism_thesis_families.yaml`, (4) legacy keyword extractor.

---

### 1.2 Bestseller Pipeline — P1 Actions (5 PRs, all merged)

| PR | ACT | BSG | Title | Key file(s) |
|----|-----|-----|-------|-------------|
| #465 | ACT-007 | BSG-020 | Atom metadata tagging + enrichment scoring | `registry/anxiety.yaml`, `phoenix_v4/planning/enrichment_select.py`, `scripts/tools/tag_atom_metadata.py` (NEW) |
| #466 | ACT-008 | BSG-013 | EMA learner wired into production | `scripts/ci/log_editorial_feedback.py` (NEW), `scripts/ci/run_ema_learner.py` (NEW) |
| #467 | ACT-009 | BSG-005 | All 5 EI V2 dimension gates verified | `tests/test_dimension_gates_integration.py` (NEW) |
| #468 | ACT-010 | BSG-010 | Doctrine quarantine at enrichment selection | `phoenix_v4/planning/enrichment_select.py` |
| #464 | ACT-011 | BSG-011 | Book plan generator — auto-produce valid plans | `phoenix_v4/planning/book_structure_plan.py`, `scripts/run_pipeline.py` |

**ACT-007 detail (PR #465)**  
Tagged all 90 non-STORY sections in `registry/anxiety.yaml` with 6 new metadata fields: `reader_objection`, `proof_mode`, `tension_type`, `propulsion_type`, `shareability`, `collision_family`. Added `_metadata_field_bonus()` (+0.15/+0.10/+0.10/+0.08/+0.05) and `_collision_family_penalty()` (-0.20 if same collision_family in prior 2 chapters) to enrichment scoring. New CLI tool `scripts/tools/tag_atom_metadata.py` for `--dry-run` / `--write` metadata suggestions on any registry YAML.

**ACT-008 detail (PR #466)**  
Two new CI scripts:
- `scripts/ci/log_editorial_feedback.py` — logs grade + notes to `feedback_log_path` from `ei_v2_config.yaml`. Accepted = grade ≥ 7.0.
- `scripts/ci/run_ema_learner.py` — calls `learn_from_feedback()`, logs old→new→delta for composite weights to `artifacts/ei_v2/ema_update_log.jsonl`. Has `--dry-run` mode.

**ACT-009 detail (PR #467)**  
9 integration tests in `tests/test_dimension_gates_integration.py`. Key test `test_no_gate_is_constant_stub()` compares good text vs degenerate stub ("The.") to catch 1.0 constant returns. Verified all 5 gates (uniqueness, cohesion, engagement, somatic_precision, listen_experience) are real implementations. `listen_experience` scores TTS rhythm + paragraph breathing + jargon + repetition.

**ACT-010 detail (PR #468)**  
Added `_SOMATIC_QUARANTINE_TERMS` frozenset (15 terms from `SPIRITUAL_LEXICON` in `frame_governor.py`) and `_is_doctrine_quarantined(atom_text, frame)` function. Quarantine wired into all 4 candidate-selection tiers in `enrichment_select.py` before scoring. Prevents spiritual-frame lexicon from leaking into somatic-first books.

**ACT-011 detail (PR #464)**  
Added `generate_book_plan(topic_id, persona_id, runtime_format, engine_type, *, chapter_count, seed)` to `phoenix_v4/planning/book_structure_plan.py`. Returns a `BookStructurePlan` that passes `validate_book_arc()`. Includes `FORMAT_CHAPTER_COUNTS` (17 formats), phase-based emotional job assignment, ONTGP slot plans, bestseller repeat fixer. Wired auto-fallback in `scripts/run_pipeline.py`: `FileNotFoundError` from `load_book_structure_plan()` now triggers `generate_book_plan()` instead of exiting.

---

### 1.3 Teacher Showcase Reels (PR #494, open → deploy live)

**PR #494** — `agent/teacher-showcase-reels-20260418` → base `main`  
**Commit:** `cca5de0410`  
**Deploy:** https://53efa7f1.phoenix-command.pages.dev  
**Alias:** https://agent-teacher-showcase-reels.phoenix-command.pages.dev

#### What changed

| File | Change |
|------|--------|
| `brand-wizard-app/public/teacher_showcase.html` | CSS `.video-reel-wrap` (9:16 aspect-ratio, max-width 360px) + 3 collapsible "Video — example reel" sections |
| `brand-wizard-app/public/assets/video/teacher_reels/ahjan_reel.mp4` | 4.9 MB · source: `teacher_vid_package/ahjan.mp4` |
| `brand-wizard-app/public/assets/video/teacher_reels/adi_da_reel.mp4` | 3.0 MB · source: cherry-picked from `agent/brand-admin-teacher-example-reels` |
| `brand-wizard-app/public/assets/video/teacher_reels/wu_reel.mp4` | 7.4 MB · source: cherry-picked from `agent/brand-admin-teacher-example-reels` |

#### Video section HTML pattern (same for all 3 teachers)
```html
<div class="section-toggle" onclick="toggleSection('<slug>_video_example')">
  <span class="toggle-arrow" id="arr_<slug>_video_example">▸</span> Video — example reel
</div>
<div id="<slug>_video_example" class="collapsible" style="display:none">
  <p class="listen-meta" style="margin:0 0 12px">Official teacher reel · 9:16 vertical</p>
  <div class="video-reel-wrap">
    <video controls playsinline preload="metadata" poster="assets/covers/kdp/<slug>_audiobook.png">
      <source src="assets/video/teacher_reels/<slug>_reel.mp4" type="video/mp4">
    </video>
  </div>
  <div class="video-label" style="margin-top:8px">Teacher reel</div>
</div>
```

#### Serving strategy
Videos are served **directly from Cloudflare Pages** (`/assets/video/teacher_reels/`) — no R2 required. R2 credentials (`R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, etc.) were never registered in Keychain; the commit that was supposed to do so (`7920979b` on `agent/r2-teacher-sai-ma-loop`) was never merged.

#### QA results (live browser check 2026-04-20)
| Teacher | Video | Duration | Frame content |
|---------|-------|----------|---------------|
| Ahjan | ✅ loads, plays | — | "The Alarm You Learned To Ignore" book cover |
| Adi Da | ✅ loads, plays | 0:28 | "Adi Da / Awakening Press" title card |
| Master Wu | ✅ loads, plays | 1:18 | "IRON GATE · Martial composure under pressure · Iron Gate Press" |

---

## 2. Pipeline Completeness After This Session

| Layer | Before | After |
|-------|--------|-------|
| Structure assignment | Hash-based (random-feeling) | Phase-aware (5 phases, pooled) |
| Production gate | Gap markers silently pass | Hard-fail `SystemExit` on any `[CONTENT GAP` |
| Chapter thesis | Keyword-only fallback | 4-stage chain via thesis bank |
| Atom metadata | 0 fields tagged | 6 fields on all anxiety atoms |
| Enrichment scoring | Flat scoring | +metadata bonus, −collision penalty |
| EMA learner | Not connected | `log_editorial_feedback.py` + `run_ema_learner.py` |
| Dimension gates | Untested (possible stubs) | 9 integration tests, all 5 verified real |
| Doctrine quarantine | Partial | Full — 15 quarantine terms, all 4 tiers |
| Book plan | Manual YAML required | Auto-generated via `generate_book_plan()` |

Estimated pipeline completeness: **~87–90%** (per original BSG spec).

---

## 3. Pending / Not Done

### Missing teacher videos
`ra.mp4` and `sai_ma_vid.mp4` do not exist anywhere — not on disk, not in git history, not in any worktree. These teacher sections have no reels. Must be provided externally before adding to showcase.

### PR #494 not merged
Teacher showcase PR is open. Merge when ready:
```bash
gh pr merge 494 --squash --admin
```

### R2 credentials not in Keychain
The R2 vars (`R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET`) were committed to registry on branch `agent/r2-teacher-sai-ma-loop` (commit `7920979b`) but never merged. Until merged and registered via `scripts/ci/integration_env_registry.py`, R2 uploads will fail silently. For now, teacher videos route around this by serving from Pages.

### P2 actions (future backlog)
| ACT | BSG | Description |
|-----|-----|-------------|
| ACT-012 | — | Rhetorical memory integration |
| ACT-013 | — | 13 new atom types |
| ACT-014 | — | Pearl_Writer LLM expansion audit |
| ACT-015 | — | Catalog buying-trigger |

### Remaining atom registries to tag
Only `registry/anxiety.yaml` was tagged with the 6 new metadata fields (PR #465). All other registries (burnout, shame, grief, corporate_managers, etc.) still have `0` metadata fields. Use `scripts/tools/tag_atom_metadata.py --write` per registry.

---

## 4. Key Commands

```bash
# Load credentials
eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"

# Build + deploy brand-wizard-app
cd brand-wizard-app && npm run build
npx wrangler pages deploy dist/ --project-name phoenix-command

# Merge teacher showcase PR
gh pr merge 494 --squash --admin

# Tag atom metadata on a registry
python3 scripts/tools/tag_atom_metadata.py --registry registry/burnout.yaml --dry-run
python3 scripts/tools/tag_atom_metadata.py --registry registry/burnout.yaml --write

# Log editorial feedback + run EMA update
python3 scripts/ci/log_editorial_feedback.py --grade 7.5 --notes "good arc" --plan path/to/plan.yaml
python3 scripts/ci/run_ema_learner.py

# Run dimension gate tests
pytest tests/test_dimension_gates_integration.py -v

# Health check
bash scripts/git/health_check.sh
```

---

## 5. File Index — New Files Created This Session

| File | Type | PR |
|------|------|----|
| `config/planning/chapter_thesis_bank.yaml` | Config (20 intents × 4 engines) | #463 |
| `scripts/tools/tag_atom_metadata.py` | CLI tool | #465 |
| `scripts/ci/log_editorial_feedback.py` | CI script | #466 |
| `scripts/ci/run_ema_learner.py` | CI script | #466 |
| `tests/test_dimension_gates_integration.py` | Tests (9) | #467 |
| `brand-wizard-app/public/assets/video/teacher_reels/ahjan_reel.mp4` | Video asset | #494 |
| `brand-wizard-app/public/assets/video/teacher_reels/adi_da_reel.mp4` | Video asset | #494 |
| `brand-wizard-app/public/assets/video/teacher_reels/wu_reel.mp4` | Video asset | #494 |
