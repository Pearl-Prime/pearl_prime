# Session Handoff — 2026-04-08

**Agent:** Claude Sonnet 4.6 via Claude Code  
**Session:** Worktree `nervous-jepsen` (branch `agent/design-tokens`)  
**Date:** 2026-04-08  
**Status:** Complete — exercise template expansion + pipeline wiring + PhoenixControl UI update

---

## Summary

Three interconnected workstreams completed this session:

1. **Exercise anti-spam expansion** — `component_templates.yaml` expanded from 4 → 12 items per dimension, reaching ~3M unique wrapper combinations per exercise type
2. **Pipeline wiring audit** — confirmed full end-to-end wiring from templates through CLI, registry resolver, chapter composer, and CI
3. **PhoenixControl UI** — added Teacher, Arc, and Seed fields to PipelineView so teacher-mode books can be triggered from the Mac app

---

## Work Done

### 1. Expand component_templates.yaml (4 → 12 per dimension)

**File:** `config/pearl_practice/component_templates.yaml`  
**Branch:** `agent/design-tokens` (worktree `nervous-jepsen`)

**Why:** The 5-dimension exercise wrapper system (bridge + intro + aha + integration) only had 4 items per dimension per category. With 9 categories × 3 dimensions × 4 items = ~20,736 combinations total — not enough to pass CTSS fingerprint / cosine-similarity anti-spam checks (0.90 threshold) across multiple brands on the same platform.

**What was added:** 8 new items per dimension per category = 232 new single-sentence template items total.

**Dimensions expanded:**

| Dimension | Scope | Items before | Items after |
|---|---|---|---|
| `bridge` | universal | 12 | 12 (already done) |
| `intro_mechanism` | per category × 9 | 4 | 12 |
| `aha_observation` | per category × 9 | 4 | 12 |
| `aha_permission` | universal | 4 | 12 |
| `integration_takeaway` | per category × 9 | 4 | 12 |
| `integration_closing` | universal | 4 | 12 |

**Categories covered:** `body_awareness`, `sensory_grounding`, `meditations`, `affirmations`, `reflections`, `self_inquiry`, `integration_bridges`, `thought_experiments`, `breath_regulation`

**Result:** **2,985,984 unique wrapper combinations per category** (12 bridge × 12 intro × 12 obs × 12 perm × 12 takeaway × 12 closing).

**Voice rules applied to all new items:**
- Second person, present tense
- 5–15 words per item
- No promises, no resolution language, no rhetorical questions
- Observation-first, not prescriptive

---

### 2. Pipeline Wiring Audit

Traced the full data path for `component_templates.yaml` across all pipeline surfaces:

**Complete wiring (confirmed working):**

```
run_pipeline.py
  └── registry_resolver.py (resolve_book)
        └── practice_library_loader.get_exercise_for_chapter()
              └── load_component_templates() → component_templates.yaml
                    └── compose_exercise() → bridge + intro + desc + aha + integration

run_pipeline.py
  └── book_renderer.render_book()
        └── chapter_composer.compose_chapter_prose()
              ├── get_exercise_for_chapter() [placeholder fallback]
              └── compose_exercise() + load_component_templates() [direct path]
```

**GitHub Actions:** `.github/workflows/catalog-book-pipeline.yml` — weekly cron + manual dispatch, runs full catalog generator. Templates flow through automatically.

**Surfaces NOT triggering book generation (by design):**
- `server/app.py` (FastAPI) — read-only catalog/admin API only
- `brand-wizard-app/` (React/Vite) — brand positioning wizard, no backend pipeline calls
- `dashboard.py` (Streamlit) — observability/gates viewer, no book generation (shows output artifacts only)

---

### 3. PhoenixControl PipelineView — Teacher Mode Fields

**File:** `PhoenixControl/Views/PipelineView.swift`  
**Commit:** `84d222a446` on `main`

**Before:** Only `topic` and `persona` fields. No way to trigger teacher mode, select arc, or set seed from the UI.

**After:** Three new optional fields added:

| Field | Flag passed | Default |
|---|---|---|
| Teacher | `--teacher` | empty (regular mode) |
| Arc | `--arc` | empty (auto-detect) |
| Seed | `--seed` | empty (pipeline default) |

**UX additions:**
- Orange **"Teacher mode"** badge appears when Teacher field is non-empty
- Run button disabled when topic is empty (prevents accidental blank runs)
- All three fields optional — existing topic/persona-only runs unchanged

**Layout:** Three rows (Topic+Persona / Teacher+Arc / Seed) with label alignment and placeholder text.

---

## Files Modified This Session

| File | Branch | What changed |
|---|---|---|
| `config/pearl_practice/component_templates.yaml` | `agent/design-tokens` | 232 new template items, all dimensions 4→12 |
| `PhoenixControl/Views/PipelineView.swift` | `main` (direct) | Teacher + Arc + Seed fields, teacher mode badge |

---

## Prior Work in This Branch (agent/design-tokens)

Three commits already on this branch before this session:

| Commit | What |
|---|---|
| `3decc665a2` | `feat: wire 311-exercise practice library into pipeline` |
| `6959c0b9d3` | `feat: wrap ALL exercises with 5-dimension template (including teacher)` |
| `1c2492e74b` | `fix: exercise seed includes text hash for cross-book uniqueness` |

These added:
- `phoenix_v4/exercises/practice_library_loader.py` — loads 311 exercises from `SOURCE_OF_TRUTH/practice_library/inbox/*_PRODUCTION_READY.json`, composes with 5-dimension templates
- `phoenix_v4/rendering/chapter_composer.py` — wraps ALL exercises (teacher + practice library) with 5-dimension template
- `phoenix_v4/teacher/coverage_gate.py` — fixed: skip ALL slots for persona fallback (was blocking non-adi_da teachers with TeacherCoverageError)
- `phoenix_v4/planning/slot_resolver.py` — fixed: expanded teacher fallback slots
- `phoenix_v4/planning/registry_resolver.py` — full atom overlay wired: teacher atoms, persona atoms, and practice library fallback for EXERCISE slots
- `scripts/run_pipeline.py` — restored atom assembly compile_plan call, fixed json import shadowing

---

## Architecture: 5-Dimension Exercise Template System

Every exercise (whether from teacher atoms, practice library, or registry) is wrapped with:

```
{bridge}

This is {exercise_name}. {mechanism}

{exercise_description_text}

Now, notice {observation}. {permission}

Before you move on, {takeaway}. {closing}
```

**Selection is deterministic per book** — same seed + chapter index always produces same wrapper, but different books get different combinations.

**Teacher exercises** go through `chapter_composer.py` and get wrapped with the same 5-dimension system as practice library exercises.

**Practice library exercises** (311 items across 9 types) are selected via `practice_library_loader.get_exercise_for_chapter()` — no repeats within a 12-chapter book (pool of 311 >> 12 needed).

---

## What Is NOT Done / Next Steps

### Pending: Merge agent/design-tokens to main
The three prior-session commits (practice library wiring, template wrapping, seed fix) plus the component_templates.yaml expansion are on `agent/design-tokens` worktree. These need a PR to main before they are live in production runs.

**To create PR:**
```bash
cd /Users/ahjan/phoenix_omega/.claude/worktrees/nervous-jepsen
git push -u origin agent/design-tokens
gh pr create --title "feat: exercise template expansion + pipeline wiring" --body "..."
```

### Pending: Re-run atom coverage analysis
After the practice library wiring merges, re-run:
```bash
PYTHONPATH=. python3 scripts/ci/content_coverage_report.py
```

### Optional: TeacherView wiring
`PhoenixControl/Views/TeacherView.swift` currently only runs teacher production gates, not book generation with `--teacher`. Could be extended similarly to PipelineView to trigger a full teacher-mode book directly.

### Optional: Arc picker in PipelineView
The Arc field currently takes a raw path string. A future improvement would auto-list available arcs from `arcs/` directory (via the existing `/api/v1/catalog/arcs` endpoint) and show them in a picker.

---

## How to Test

**CLI — regular mode:**
```bash
cd /Users/ahjan/phoenix_omega
PYTHONPATH=. python3 scripts/run_pipeline.py \
  --topic grief \
  --persona gen_z_professionals \
  --arc arcs/grief_arc.yaml \
  --render-book
```

**CLI — teacher mode:**
```bash
PYTHONPATH=. python3 scripts/run_pipeline.py \
  --topic grief \
  --persona gen_z_professionals \
  --arc arcs/grief_arc.yaml \
  --teacher master_wu \
  --seed grief_genz_wu_001 \
  --render-book
```

**Verify exercise wrappers are unique across chapters:**  
Open the rendered book, compare the bridge sentence on each EXERCISE section — they should all differ (12 unique bridges, rotated by chapter index).

**Verify anti-spam combos:**
```bash
python3 -c "
import yaml
with open('config/pearl_practice/component_templates.yaml') as f:
    data = yaml.safe_load(f)
cat = 'body_awareness'
combos = (len(data['bridge']) * len(data['intro_mechanism'][cat]) *
          len(data['aha_observation'][cat]) * len(data['aha_permission']) *
          len(data['integration_takeaway'][cat]) * len(data['integration_closing']))
print(f'{cat}: {combos:,} combinations')
"
# Expected: 2,985,984 combinations
```

**PhoenixControl — teacher mode book:**
1. Open PhoenixControl Mac app
2. Go to Pipeline tab
3. Enter: Topic=`grief`, Persona=`gen_z_professionals`, Teacher=`master_wu`
4. Optionally enter Arc path and Seed
5. Hit Cmd+Return — watch live log

---

## Key File Locations

| What | Where |
|---|---|
| Exercise templates | `config/pearl_practice/component_templates.yaml` |
| Practice library exercises | `SOURCE_OF_TRUTH/practice_library/inbox/*_PRODUCTION_READY.json` |
| Practice library loader | `phoenix_v4/exercises/practice_library_loader.py` |
| Registry resolver (overlay logic) | `phoenix_v4/planning/registry_resolver.py` |
| Chapter composer (exercise wrapping) | `phoenix_v4/rendering/chapter_composer.py` |
| Teacher coverage gate | `phoenix_v4/teacher/coverage_gate.py` |
| Slot resolver | `phoenix_v4/planning/slot_resolver.py` |
| CLI entry point | `scripts/run_pipeline.py` |
| PhoenixControl pipeline UI | `PhoenixControl/Views/PipelineView.swift` |
| Streamlit dashboard | `dashboard.py` |
| CI pipeline workflow | `.github/workflows/catalog-book-pipeline.yml` |
