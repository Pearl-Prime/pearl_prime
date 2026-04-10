# Teacher Bank Content Audit

**Date:** 2026-04-10
**Project:** proj_state_convergence_20260328
**Scope:** SOURCE_OF_TRUTH/teacher_banks/ — 13 teachers x 13 slot types

---

## Summary

| Metric | Value |
|--------|-------|
| Total teachers | 13 |
| Slot types audited | 13 (HOOK, SCENE, STORY, REFLECTION, EXERCISE, INTEGRATION, PERMISSION, PIVOT, QUOTE, TAKEAWAY, TEACHING, THREAD, COMPRESSION) |
| Total approved atoms | **2,426** |
| Teachers with all 13 slots filled | **1** (ahjan) |
| Teachers missing QUOTE | **12** (all except ahjan) |
| Teachers missing TEACHING | **12** (all except ahjan) |
| Teachers with candidate_atoms | **1** (ahjan: 190) |
| Teachers with kb/ files | **4** (ahjan, master_wu, miki, ra — 1 each) |
| Teachers with localized atoms | **1** (adi_da: 570) |

---

## Teacher x Slot Type Matrix (approved_atoms .yaml count)

| Teacher | HOOK | SCENE | STORY | REFL | EXER | INTEG | PERM | PIVOT | QUOTE | TAKE | TEACH | THREAD | COMP | Total |
|---------|------|-------|-------|------|------|-------|------|-------|-------|------|-------|--------|------|-------|
| adi_da | 30 | 20 | 20 | 30 | 40 | 20 | 20 | 20 | **0** | 20 | **0** | 20 | 20 | 260 |
| ahjan | 12 | 12 | 20 | 12 | 65 | 12 | 15 | 15 | 9 | 15 | 100 | 15 | 12 | 314 |
| joshin | 12 | 12 | 20 | 12 | 12 | 12 | 15 | 15 | **0** | 15 | **0** | 15 | 12 | 152 |
| junko | 12 | 12 | 20 | 12 | 12 | 12 | 15 | 15 | **0** | 15 | **0** | 15 | 12 | 152 |
| maat | 12 | 12 | 20 | 12 | 12 | 12 | 15 | 15 | **0** | 15 | **0** | 15 | 12 | 152 |
| master_feung | 12 | 12 | 20 | 12 | 12 | 12 | 15 | 15 | **0** | 15 | **0** | 15 | 12 | 152 |
| master_sha | 12 | 12 | 20 | 12 | 12 | 12 | 15 | 15 | **0** | 15 | **0** | 15 | 12 | 152 |
| master_wu | 12 | 12 | 20 | 12 | 12 | 12 | 15 | 15 | **0** | 15 | **0** | 15 | 12 | 152 |
| miki | 12 | 12 | 20 | 12 | 12 | 12 | 15 | 15 | **0** | 15 | **0** | 15 | 12 | 152 |
| omote | 12 | 12 | 20 | 12 | 12 | 12 | 15 | 15 | **0** | 15 | **0** | 15 | 12 | 152 |
| pamela_fellows | 12 | 12 | 20 | 12 | 12 | 12 | 15 | 15 | **0** | 15 | **0** | 15 | 12 | 152 |
| ra | 12 | 12 | 20 | 12 | 12 | 12 | 15 | 15 | **0** | 15 | **0** | 15 | 12 | 152 |
| sai_ma | 12 | 12 | 20 | 12 | 12 | 12 | 15 | 15 | **0** | 15 | **0** | 15 | 12 | 152 |
| **TOTAL** | **174** | **164** | **260** | **174** | **237** | **164** | **195** | **195** | **9** | **195** | **100** | **195** | **164** | **2,426** |

---

## Per-Teacher Infrastructure

| Teacher | Approved | Candidate | Doctrine | KB | Raw | Localized |
|---------|----------|-----------|----------|----|----|-----------|
| adi_da | 260 | 0 | 2 | 0 | 0 | 570 (ja-JP) |
| ahjan | 314 | 190 | 8 | 1 | 22 | 0 |
| joshin | 152 | 0 | 1 | 0 | 0 | 0 |
| junko | 152 | 0 | 1 | 0 | 0 | 0 |
| maat | 152 | 0 | 1 | 0 | 0 | 0 |
| master_feung | 152 | 0 | 1 | 0 | 0 | 0 |
| master_sha | 152 | 0 | 1 | 0 | 0 | 0 |
| master_wu | 152 | 0 | 1 | 1 | 2 | 0 |
| miki | 152 | 0 | 1 | 1 | 2 | 0 |
| omote | 152 | 0 | 1 | 0 | 0 | 0 |
| pamela_fellows | 152 | 0 | 1 | 0 | 0 | 0 |
| ra | 152 | 0 | 1 | 1 | 14 | 0 |
| sai_ma | 152 | 0 | 1 | 0 | 0 | 0 |

---

## Atom Quality Spot-Check (ahjan sample)

| Slot | Sample File | Has body? | Has atom_id? | Words | Quality |
|------|-------------|-----------|-------------|-------|---------|
| HOOK | ahjan_HOOK_000.yaml | Yes | Yes | 49 | Non-stub |
| SCENE | ahjan_SCENE_000.yaml | Yes | Yes | 63 | Non-stub |
| STORY | ahjan_STORY_000_mined.yaml | Yes | Yes | 153 | Non-stub |
| REFLECTION | ahjan_REFLECTION_000.yaml | Yes | Yes | 57 | Non-stub |
| EXERCISE | ahjan_EXERCISE_000_mined.yaml | Yes | Yes | 104 | Non-stub |
| INTEGRATION | ahjan_INTEGRATION_000.yaml | Yes | Yes | 65 | Non-stub |
| COMPRESSION | ahjan_COMPRESSION_001.yaml | Yes | Yes | 37 | Non-stub |
| PERMISSION | ahjan_PERMISSION_000.yaml | Yes | Yes | 36 | Non-stub |
| PIVOT | ahjan_PIVOT_000.yaml | Yes | Yes | 31 | Non-stub |
| TAKEAWAY | ahjan_TAKEAWAY_000.yaml | Yes | Yes | 19 | Short (design) |
| THREAD | ahjan_THREAD_000.yaml | Yes | Yes | 35 | Non-stub |
| TEACHING | ahjan_TEACHING_000_mined.yaml | Yes | Yes | 124 | Non-stub |
| QUOTE | ahjan_QUOTE_000_mined.yaml | Yes | Yes | 96 | Non-stub |

All sampled atoms have valid `atom_id`, `body`, and real content.

---

## Flags

### Critical — Zero atoms in slot type

| Teacher(s) | Slot | Impact |
|------------|------|--------|
| 12 teachers (all except ahjan) | QUOTE | Hard-fail for teacher quotes |
| 12 teachers (all except ahjan) | TEACHING | Hard-fail for teaching-voice books |

### Warning — Infrastructure gaps

| Gap | Affected Teachers |
|-----|-------------------|
| kb/ = 0 files | adi_da, joshin, junko, maat, master_feung, master_sha, omote, pamela_fellows, sai_ma (9) |
| candidate_atoms = 0 | All except ahjan (12) |
| localized atoms = 0 | All except adi_da (12) |

---

## Recommendations

1. **P0 — Generate QUOTE atoms** for 12 teachers. Required slot for teacher-mode books.
2. **P0 — Generate TEACHING atoms** for 12 teachers. Required for differentiated teacher voice.
3. **P1 — Populate kb/** for 9 teachers with 0 KB files.
4. **P1 — Generate candidate_atoms** for 12 teachers.
5. **P2 — Expand localized atoms** beyond adi_da.
6. **P2 — Expand adi_da doctrine** from 2 files to match ahjan's 8.
