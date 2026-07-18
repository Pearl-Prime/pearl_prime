# P1 Health Audit — Next Steps

**Date:** 2026-04-10
**Project:** proj_state_convergence_20260328
**Source:** artifacts/audit/P1_HEALTH_REPORT_2026_04_10.md (PR #343, merged SHA 33c99eacbd0654aa10da19b1356147e5063a6299)
**Author:** Pearl_PM + Pearl_GitHub
**Scope:** Actionable work items derived from the P1 health audit. This document is PLANNING ONLY — no content, atoms, configs, or code generated.

---

## Spot-Check Verification (conducted before writing this doc)

All findings confirmed against live disk state:

| Check | Finding | Verified |
|-------|---------|---------|
| 5 unindexed docs exist on disk | `AGENT_FILE_PERSISTENCE_PROTOCOL.md`, `CONTENT_INVENTORY_WORKSTREAM_SPEC.md`, `FULL_FUNNEL_PLAN.md`, `SESSION_UNITY_PROTOCOL.md`, `PEARL_PM_STATE.md` all present | PASS |
| QUOTE = 0 for 12 teachers | All 12 confirmed 0 files in `approved_atoms/QUOTE/` | PASS |
| ahjan TEACHING present | 100 files in `approved_atoms/TEACHING/` | PASS |
| educators × burnout = 0 | `atoms/educators/burnout/` missing | PASS |
| gen_z_student × compassion_fatigue = 0 | `atoms/gen_z_student/compassion_fatigue/` missing | PASS |
| 480 profiles, 0 empty fields | Python cross-check: 480 profiles, 0 empty topic_scores/voice_signature/scenario_seeds | PASS |
| 15/15 registries present | `registry/*.yaml` count = 15 | PASS |

---

## What's Blocking Production RIGHT NOW

### BLOCK 1: QUOTE + TEACHING Atoms Missing (12/13 teachers)

**WHO:** Pearl_Editor (atom generation from doctrine files via Qwen on Pearl Star)

**WHAT:** Generate QUOTE and TEACHING atoms for these 12 teachers:
- `adi_da`, `joshin`, `junko`, `maat`, `master_feung`, `master_sha`, `master_wu`, `miki`, `omote`, `pamela_fellows`, `ra`, `sai_ma`

**TARGET PATHS:**
- `SOURCE_OF_TRUTH/teacher_banks/{teacher}/approved_atoms/QUOTE/`
- `SOURCE_OF_TRUTH/teacher_banks/{teacher}/approved_atoms/TEACHING/`

**HOW MANY:** Minimum 12 atoms per slot per teacher × 2 slots × 12 teachers = **288 atoms**
- Baseline: 12 QUOTE + 12 TEACHING per teacher (matching minimum slot threshold)
- Reference: `ahjan` has 9 QUOTE (below threshold) + 100 TEACHING — QUOTE also needs 6 more

**REFERENCE FORMAT:** `SOURCE_OF_TRUTH/teacher_banks/ahjan/approved_atoms/QUOTE/ahjan_QUOTE_000_mined.yaml`
- atom_id, body (96+ words), slot_type: QUOTE, teacher_id, tags

**INPUT FILES:** Each teacher has 1 doctrine file in `SOURCE_OF_TRUTH/teacher_banks/{teacher}/doctrine/`. `adi_da` has 2. `ahjan` has 8 (reference model).

**PRIORITY:** P0 — blocks ALL book assembly for teacher-mode books using QUOTE or TEACHING slots

**EFFORT:** ~2 hours (Qwen generation + quality review)

**DEPENDENCY:** None — doctrine files exist for all 12 teachers

**ALSO:** Increase ahjan QUOTE from 9 to ≥15 (6 additional atoms needed in `ahjan/approved_atoms/QUOTE/`)

---

### BLOCK 2: 17 Persona × Topic Zero-Atom Combos

**WHO:** Pearl_Writer (persona atom generation via Qwen on Pearl Star)

**WHAT:** Create CANONICAL.txt atom files for these 17 missing combos:

| Persona | Missing Topics | Atom Count Needed |
|---------|---------------|------------------|
| `educators` | burnout, financial_anxiety, imposter_syndrome, overthinking, sleep_anxiety, social_anxiety, somatic_healing | 7 × 21 = **147 atoms** |
| `nyc_executives` | burnout, financial_anxiety, imposter_syndrome, overthinking, sleep_anxiety, social_anxiety, somatic_healing | 7 × 21 = **147 atoms** |
| `gen_z_student` | compassion_fatigue, financial_anxiety, financial_stress | 3 × 21 = **63 atoms** |
| **Total** | 17 combos | **357 atoms** |

**TARGET PATHS:** `atoms/{persona}/{topic}/` — create directory and populate with atoms matching existing persona voice

**REFERENCE FORMAT:** Examine `atoms/educators/anxiety/` (46 atoms) and `atoms/nyc_executives/anxiety/` (51 atoms) for voice calibration

**IMPORTANT NOTE:** `educators` and `nyc_executives` are NOT in `config/catalog_planning/canonical_personas.yaml` (only 11 canonical personas listed). They exist on disk as extended personas. Confirm with owner whether to add them to canonical_personas.yaml as part of this work or treat as extended-only.

**PRIORITY:** P0 — these combos produce zero output in assembly pipeline

**EFFORT:** ~1.5 hours (Qwen generation + directory creation)

**DEPENDENCY:** None — can start immediately; no upstream blockers

---

## What's Degrading Quality But Not Blocking

### QUALITY 1: 80 Files Not Indexed in DOCS_INDEX (54 docs + 26 specs)

**WHO:** Pearl_Architect (DOCS_INDEX refresh)

**WHAT:** Add 80 unindexed files to `docs/DOCS_INDEX.md` and fix 17 dead links

**P1 priority unindexed files (require immediate indexing):**
- `docs/PEARL_ARCHITECT_STATE.md` — agent coordination doc
- `docs/PEARL_PM_STATE.md` — project coordination doc
- `docs/SESSION_UNITY_PROTOCOL.md` — agent session protocol
- `docs/AGENT_FILE_PERSISTENCE_PROTOCOL.md` — agent persistence
- `docs/FULL_FUNNEL_PLAN.md` — active workstream doc
- `docs/AUDIOBOOK_PIPELINE_COMPLETE_GUIDE.md`, `docs/EBOOK_PIPELINE_COMPLETE_GUIDE.md`, `docs/PODCAST_PIPELINE_COMPLETE_GUIDE.md`, `docs/VIDEO_PIPELINE_COMPLETE_GUIDE.md` — pipeline guides
- `docs/CONTENT_INVENTORY_WORKSTREAM_SPEC.md`, `docs/CONTENT_PRODUCTION_PLAN_100PCT.md`
- `docs/EI_V2_REGISTRY_LEARNING_SPEC.md`, `docs/anxiety_fear_writer_spec.md`
- `specs/EXPERIENCE_LAYER_ANTI_SPAM_SPEC.md`, `specs/IMPLICIT_THERAPEUTIC_ENGINE_DEV_SPEC.md`
- `specs/QC_AGENT_SPEC.md`, `specs/VIDEO_CONTENT_ENGINE_DEV_SPEC.md`
- `specs/PHOENIX_V4_5_WRITER_SPEC_TTS_v1.3.md`, `specs/PHOENIX_V4_5_CHINESE_WRITER_SPEC_v2.5.md`

**P2 priority:** 12 unindexed manga specs — batch as "Manga spec suite" section

**Dead links (17):** These reference planned-but-not-created files. No removal needed — mark as `[planned]` in index or remove stale references. See `artifacts/audit/docs_index_gap_report.md` for full list.

**ALSO:** Update `SUBSYSTEM_AUTHORITY_MAP.tsv` recommender status from `backlog` → `active` (7/9 files are present and functional on main)

**PRIORITY:** P1/P2 — doesn't block production but causes agent routing failures when authority docs can't be found via DOCS_INDEX

**EFFORT:** ~1 hour

**DEPENDENCY:** None

**NOTE:** P2 prompt pre-exists from earlier session — can be executed directly

---

### QUALITY 2: gen_z_student Thin Atom Density (143 atoms, 12/15 topics at 11 atoms each)

**WHO:** Pearl_Writer (persona expansion)

**WHAT:** After BLOCK 2 fills the 3 missing topics (adding ~63 atoms), expand all 12 populated topics from 11 atoms to ≥21 atoms for parity with other canonical personas

**TARGET PATH:** `atoms/gen_z_student/{topic}/` — add atoms to existing populated topics

**HOW MANY:** 12 existing topics × 10 additional atoms = **~120 atoms**; 3 new topics already covered by BLOCK 2

**PRIORITY:** P2 — assembly works but produces repetitive output (11 atoms per topic = thin diversity)

**EFFORT:** ~2 hours

**DEPENDENCY:** After BLOCK 2 (fills 3 missing topics first to get clean baseline)

---

### QUALITY 3: 9 Teachers Have 0 KB Files (Limits Doctrine-Aware Generation)

**WHO:** Pearl_Editor

**WHAT:** Create at least 1 KB file per teacher in `SOURCE_OF_TRUTH/teacher_banks/{teacher}/kb/`

**AFFECTED TEACHERS:** `adi_da`, `joshin`, `junko`, `maat`, `master_feung`, `master_sha`, `omote`, `pamela_fellows`, `sai_ma`

**REFERENCE FORMAT:** `SOURCE_OF_TRUTH/teacher_banks/master_wu/kb/` and `SOURCE_OF_TRUTH/teacher_banks/ahjan/kb/` (reference model with 1 file each)

**PRIORITY:** P1 — doesn't block atom generation but limits quality of generated atoms for these teachers

**EFFORT:** ~3 hours (requires mining raw material from doctrine files or raw_atoms)

**DEPENDENCY:** After BLOCK 1 (QUOTE/TEACHING generation — may use same session context)

---

## What's Already Good (No Action Needed)

| Area | Status | Evidence |
|------|--------|---------|
| 480 author profiles | ALL COMPLETE | 0 empty fields across topic_scores, voice_signature, scenario_seeds |
| 15/15 topic registries | ALL PRESENT | registry/*.yaml = 15 files |
| 72 brands | ALL COMPLETE | No SKELETON or PARTIAL brands |
| Teacher banks (11 slot types) | ADEQUATE | HOOK, SCENE, STORY, REFLECTION, EXERCISE, INTEGRATION, PERMISSION, PIVOT, TAKEAWAY, THREAD, COMPRESSION all populated across 13 teachers |
| ahjan reference teacher | COMPLETE | 314 atoms, all 13 slots, 8 doctrine files, 190 candidates |
| adi_da localization | PRESENT | 570 ja-JP atoms |
| 10/13 personas | FULL COVERAGE | 15/15 topics with adequate density |

---

## Execution Order (Dependency-Aware)

### WEEK 1 — Clear All Hard-Fails

**Day 1–2: BLOCK 1 — QUOTE + TEACHING atoms (Pearl_Editor)**
- Generate 12 QUOTE + 12 TEACHING atoms per teacher for 12 teachers
- Generate 6 additional ahjan QUOTE atoms (9→15)
- Target: 294 atoms total; zero QUOTE/TEACHING hard-fails
- Input: doctrine files in `SOURCE_OF_TRUTH/teacher_banks/{teacher}/doctrine/`

**Day 2–3: BLOCK 2 — 17 Persona × Topic gaps (Pearl_Writer)**
- Fill educators: 7 topics × 21 atoms = 147 atoms
- Fill nyc_executives: 7 topics × 21 atoms = 147 atoms
- Fill gen_z_student: 3 topics × 21 atoms = 63 atoms
- Clarify canonical_personas.yaml status for educators + nyc_executives with owner
- Target: 357 atoms total; zero persona×topic hard-fails

**Day 3: Verification**
- Re-run `python3 scripts/inventory/scan_content_inventory.py` or equivalent
- Confirm all 17 persona×topic combos now have atoms
- Confirm all 12 teachers now have QUOTE + TEACHING atoms
- Spot-check atom quality (body length ≥50 words, valid atom_id, correct slot_type)

### WEEK 2 — Quality and Navigation

**Day 1–2: QUALITY 3 — KB file population (Pearl_Editor)**
- Create 1+ KB file for 9 teachers with 0 KB files
- Dependency: BLOCK 1 complete (same teacher bank context)

**Day 2–3: QUALITY 1 — DOCS_INDEX refresh (Pearl_Architect)**
- Index 54 docs + 26 specs in DOCS_INDEX.md
- Fix/annotate 17 dead links
- Update recommender subsystem status backlog→active in SUBSYSTEM_AUTHORITY_MAP.tsv

**Day 3: Re-run full golden set scoring**
- Measure quality lift from atom additions

### WEEK 3+ — Density and Scale

**QUALITY 2 — gen_z_student expansion (Pearl_Writer)**
- Expand 12 populated topics from 11→21 atoms each (~120 atoms)
- Dependency: BLOCK 2 complete

**CJK translation pipeline** — expand localized atoms beyond adi_da
- Dependency: QUALITY 3 complete (teachers need KB files first)

---

## Prompt Ready?

| Block | Prompt Status |
|-------|--------------|
| BLOCK 1 (QUOTE + TEACHING) | NEEDS: Pearl_Editor prompt to generate atoms from doctrine files per teacher |
| BLOCK 2 (Persona × Topic gaps) | NEEDS: Pearl_Writer prompt with persona voice calibration from existing atoms |
| BLOCK 3 (KB files) | NEEDS: Pearl_Editor prompt with raw mining from doctrine → kb format |
| QUALITY 1 (DOCS_INDEX) | READY: P2 prompt pre-exists from earlier session |
| QUALITY 2 (gen_z_student density) | NEEDS: Pearl_Writer expansion prompt after BLOCK 2 |

---

## Work Items Summary

| ID | Block | Action | WHO | Files Affected | Atom Count | Priority | Effort | Dependency |
|----|-------|--------|-----|---------------|------------|----------|--------|------------|
| A1 | BLOCK 1 | Generate QUOTE atoms for 12 teachers | Pearl_Editor | `SOURCE_OF_TRUTH/teacher_banks/{teacher}/approved_atoms/QUOTE/` × 12 | 144 atoms | P0 | ~1h | None |
| A2 | BLOCK 1 | Generate TEACHING atoms for 12 teachers | Pearl_Editor | `SOURCE_OF_TRUTH/teacher_banks/{teacher}/approved_atoms/TEACHING/` × 12 | 144 atoms | P0 | ~1h | None |
| A3 | BLOCK 1 | Increase ahjan QUOTE to ≥15 | Pearl_Editor | `SOURCE_OF_TRUTH/teacher_banks/ahjan/approved_atoms/QUOTE/` | 6 atoms | P0 | ~15min | None |
| B1 | BLOCK 2 | Fill educators 7 topic gaps | Pearl_Writer | `atoms/educators/{burnout,financial_anxiety,imposter_syndrome,overthinking,sleep_anxiety,social_anxiety,somatic_healing}/` | 147 atoms | P0 | ~45min | None |
| B2 | BLOCK 2 | Fill nyc_executives 7 topic gaps | Pearl_Writer | `atoms/nyc_executives/{burnout,financial_anxiety,imposter_syndrome,overthinking,sleep_anxiety,social_anxiety,somatic_healing}/` | 147 atoms | P0 | ~45min | None |
| B3 | BLOCK 2 | Fill gen_z_student 3 topic gaps | Pearl_Writer | `atoms/gen_z_student/{compassion_fatigue,financial_anxiety,financial_stress}/` | 63 atoms | P0 | ~30min | None |
| B4 | BLOCK 2 | Clarify educators/nyc_executives canonical status | Pearl_PM | `config/catalog_planning/canonical_personas.yaml` | — | P1 | ~15min | Owner decision |
| C1 | QUALITY 1 | Index 54 docs + 26 specs in DOCS_INDEX | Pearl_Architect | `docs/DOCS_INDEX.md` | — | P1 | ~1h | None |
| C2 | QUALITY 1 | Update recommender status backlog→active | Pearl_PM | `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv` | — | P1 | ~5min | None |
| D1 | QUALITY 2 | Expand gen_z_student density 11→21 per topic | Pearl_Writer | `atoms/gen_z_student/*/` (12 topics) | ~120 atoms | P2 | ~2h | B3 |
| E1 | QUALITY 3 | Create KB files for 9 teachers | Pearl_Editor | `SOURCE_OF_TRUTH/teacher_banks/{teacher}/kb/` × 9 | — | P1 | ~3h | A1+A2 |

**Total P0 atoms needed: ~494 atoms** (144 QUOTE + 144 TEACHING + 6 ahjan + 357 persona×topic)
