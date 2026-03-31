# Onboarding Proof Asset Production Backlog

Purpose: convert onboarding proof from partial to proof-complete using a strict, trackable queue tied to `config/onboarding/example_registry.json`.

Status anchor: `artifacts/onboarding/proof_completion_latest.md` (7 ready / 10 planned / 2 missing).

## Hard done rule (for 100% proof-complete claim)

Do not call the system 100% proof-complete until all are true:

1. Every critical comparison set row listed below is `status: "ready"` with a resolvable non-empty `asset_path`.
2. For each critical path branch (persona-lane-market), at least one real ready proof tile exists.
3. Seed SVGs are either replaced with real pipeline outputs or explicitly retained only as non-critical fallback/demo assets.
4. `python3 scripts/ci/report_onboarding_proof_completion.py` shows no critical-path `planned` or `missing` rows.
5. Pages smoke checks pass for new ready assets.

## Priority order

1. `cmp_burnout_cross_persona_v1` (finish single missing row)
2. `cmp_anxiety_locale_v1` (complete all locale rows)
3. `cmp_burnout_posture_v1` (complete both posture variants)
4. `cmp_manga_style_mode_v1` (complete all five manga style rows)
5. `gal_tool_breath_01` (close key non-set branch gap)

## Per-ticket acceptance criteria (applies to every row)

- Generate or ingest a real pipeline output aligned to `lane`, `format`, `topic`, `persona`, and `market`.
- Update row fields:
  - `status: "ready"`
  - `asset_path`: non-empty, resolvable path/URL
  - `source`: truthful origin (`pipeline` or `pipeline_demo`, never fake)
  - `production_fidelity`: truthful (`production` or `pipeline_demo`)
  - remove `placeholder_reason` if no longer pending
- Keep caption honest to asset type (no persona/support visuals labeled as product covers).
- Run:
  - `PYTHONPATH=. python3 scripts/ci/validate_onboarding_registry.py`
  - `python3 scripts/ci/report_onboarding_proof_completion.py`
- Verify Pages 200 for each newly ready `asset_path`.

## Critical backlog tickets

### P0 — finish `cmp_burnout_cross_persona_v1`

| Ticket | Row ID | Current | Target |
|---|---|---|---|
| P0-1 | `cmp_bp_caregiver_v1` | missing | ready |

Acceptance focus: complete founder/student/caregiver parity for cross-persona burnout comparison.

### P1 — complete `cmp_anxiety_locale_v1`

| Ticket | Row ID | Current | Target |
|---|---|---|---|
| P1-1 | `cmp_anx_us_v1` | planned | ready |
| P1-2 | `cmp_anx_jp_v1` | planned | ready |
| P1-3 | `cmp_anx_tw_v1` | planned | ready |

Acceptance focus: same persona/topic/format across locale variants with truthful market-localized outputs.

### P2 — complete `cmp_burnout_posture_v1`

| Ticket | Row ID | Current | Target |
|---|---|---|---|
| P2-1 | `cmp_pos_premium_v1` | planned | ready |
| P2-2 | `cmp_pos_mainstream_v1` | planned | ready |

Acceptance focus: posture-only variation while holding fixed context.

### P3 — complete `cmp_manga_style_mode_v1`

| Ticket | Row ID | Current | Target |
|---|---|---|---|
| P3-1 | `cmp_mg_cin_v1` | planned | ready |
| P3-2 | `cmp_mg_youth_v1` | planned | ready |
| P3-3 | `cmp_mg_spirit_v1` | planned | ready |
| P3-4 | `cmp_mg_heal_v1` | planned | ready |
| P3-5 | `cmp_mg_civic_v1` | missing | ready |

Acceptance focus: style-mode comparison board complete with anxiety topic parity.

### P4 — close non-set critical branch gap

| Ticket | Row ID | Current | Target |
|---|---|---|---|
| P4-1 | `gal_tool_breath_01` | planned | ready |

Acceptance focus: ensure anxious_student + breathwork_tools + us path has real proof.

## Seed replacement/fallback policy

- Current seed-backed ready rows:
  - `cmp_bp_founder_v1`
  - `cmp_bp_student_v1`
  - `cmp_fmt_cover_v1`
  - `cmp_fmt_manga_v1`
  - `cmp_fmt_article_v1`
  - `support_persona_founder_01`
- Required disposition before 100% claim:
  - Replace critical proof rows with real assets, or
  - mark them explicitly as non-critical fallback/demo and ensure critical paths are covered by real assets.

## Go/No-Go gate for final declaration

Go only when:

- Comparison sets are all fully ready (`cmp_*` rows all `ready`), and
- no critical branch appears in the “no ready proof” section of `proof_completion_latest.md`, and
- Pages smoke tests pass for all newly ready asset URLs.

Otherwise: No-Go (still partially proof-complete).
