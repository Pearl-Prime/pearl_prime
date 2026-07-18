# System Drift Audit — Executive Summary

**PROJECT_ID:** PRJ-SYSTEM-DRIFT-AUDIT-V1  
**Audit date:** 2026-05-10  
**Agent:** Pearl_Architect  
**Baseline:** `origin/main` @ `515de6cb5e775595e3f32a64cd3dc1a5f36d8798`  
**Method:** Read-only crosswalk of marketing/research → specs → `docs/PEARL_ARCHITECT_STATE.md` cap entries → implementation & config registries; coordination TSV spot-check; `PYTHONPATH=. python3 scripts/ci/audit_llm_callers.py` (Tier policy).

---

## 1. Headline verdict

**The system is approximately 75% aligned with ratified operator intent and cap-backed specifications** — strong on recent integration waves (music-mode SSOT, dual-path image posture, marketing volume YAML, feature-knob catalog serialization, CI governance bypass, RunComfy dry-run wiring) with remaining drift concentrated in **documentation freshness**, **coordination truth vs `main`**, and **partial completion of multi-phase quality gates**.

- **Strength:** Path X **37** manga brands in `config/manga/canonical_brand_list.yaml` matches YAML `total_brands`; music-mode brands isolated in `config/music/music_brand_registry.yaml` with explicit Path X boundary comments (`config/music/music_brand_registry.yaml:48-54`).
- **Strength:** AUTO-PLAN SSOT is implemented in code: `phoenix_v4/planning/book_structure_plan.py:46-64` reads `chapter_count_default` from `config/format_selection/format_registry.yaml` per cap **AUTO-PLAN-SSOT-01-AMENDMENT**.
- **Risk:** Operator-facing specs still declare **“proposed”** while `main` already carries substantial implementation (CI recovery, worldwide program) — creates merge and prioritization ambiguity (`docs/specs/CI_BASELINE_RECOVERY_V1_SPEC.md:8`, `docs/specs/WORLDWIDE_CATALOG_GO_LIVE_V1_PROGRAM_SPEC.md:3`).
- **Risk:** **PER-CHAPTER-OVERLAY-ENFORCEMENT-V1-01** is ratified and partially coded (`phoenix_v4/quality/book_quality_gate.py:30-297`) but **ITEM-2** remains open: `your nervous system` is still present in `config/quality/refrain_allowlist.yaml:281`.
- **Gap:** Operator framing **“555 brand-locale-surface cells (PR #1023)”** has **no corroborating string** in tracked specs/markdown searched on this baseline; current marketing SSOT YAML encodes **37 × 6 surfaces = 222** bounded keys at `brand_targets` grain with locale deferred to V1.1 (`config/marketing/weekly_volumes_per_brand.yaml:36-44`, `docs/specs/MARKETING_VOLUME_SSOT_V1_SPEC.md:137-138`).

---

## 2. What we’ve built (inventory snapshot)

| Layer | Count / fact | Receipt |
|------|----------------|--------|
| **Cap headings** (`###` / `####` in `docs/PEARL_ARCHITECT_STATE.md`) | **41** lines matching `^###` / amendment headings in architect grep pass | `docs/PEARL_ARCHITECT_STATE.md` (grep session 2026-05-10) |
| **`docs/specs/*.md`** | **13** operator-facing spec files | `docs/specs/` glob |
| **Root `specs/*.md`** | **76** additional governed specs (Pearl Prime, manga suite, etc.) | `find specs -maxdepth 1 -name '*.md' \| wc -l` |
| **Commits on `main` (since 2026-05-08)** | **63** | `git log origin/main --since='2026-05-08' --oneline \| wc -l` |
| **Path X manga brands** | **37** | `config/manga/canonical_brand_list.yaml` (parsed `brands` list) |
| **Teachers in `teacher_registry.yaml`** | **13** keys (`adi_da` … `sai_ma`) | `config/teachers/teacher_registry.yaml:8-79` + full parse |
| **Marketing SSOT surfaces / brand** | **6** (`manga`, `ebook`, `audiobook`, `podcast`, `video`, `shorts`) | `docs/specs/MARKETING_VOLUME_SSOT_V1_SPEC.md:39`; `config/marketing/weekly_volumes_per_brand.yaml:66-70` |
| **PNG inventory (audit artifact)** | **6,528** data rows (`6529` lines incl. header) | `wc -l artifacts/qa/image_asset_inventory_2026-05-09.tsv`; aligns with `artifacts/qa/image_asset_inventory_audit_2026-05-09.md:20` |
| **LLM Tier policy scan** | **0** violations | `scripts/ci/audit_llm_callers.py` → `{"violation_count": 0}` |

**Brand × locale × surfaces matrix (operator program framing):** Worldwide program spec states **37 × 4 locales** (`docs/specs/WORLDWIDE_CATALOG_GO_LIVE_V1_PROGRAM_SPEC.md:17`). **Marketing volume V1** currently models **37 brands × 6 surfaces** (locale join deferred) — see §2 table above.

---

## 3. What’s working as planned (top wins)

1. **Registry-backed chapter counts** — eliminates FORMAT_CHAPTER_COUNTS drift; `book_structure_plan.get_format_chapter_count` (`phoenix_v4/planning/book_structure_plan.py:46-64`).
2. **Music mode Path X boundary** — dedicated `music_brand_registry.yaml` with anti-drift invariants (`config/music/music_brand_registry.yaml:48-54`); **37** unchanged in canonical list.
3. **Dual-path image policy ratified and instrumented** — cap **IMG-RENDER-DUAL-PATH-V1-01** (`docs/PEARL_ARCHITECT_STATE.md:1336-1419`); RunComfy modules present (`scripts/image_generation/runcomfy_dispatch.py`, `dispatchers/runcomfy_dispatcher.py`, `runcomfy_cost_tracker.py`); spend TSV scaffold `artifacts/qa/runcomfy_monthly_spend.tsv` (1 line header-only at audit time).
4. **Parallel image plan + inventory** — PR **#988** lineage documented in `artifacts/qa/parallel_image_generation_plan_2026-05-09.md` + audit TSV.
5. **Feature knob catalog variation** — cap **FEATURE-KNOB-CATALOG-VARIATION-V1-01**; merges **#986/#974/#978** referenced in `docs/specs/WORLDWIDE_CATALOG_GO_LIVE_V1_PROGRAM_SPEC.md:99-112`.
6. **CI governance false positive removed** — **#997** per commit history on `main` (`git log` excerpt 2026-05-08+).
7. **Cover art gate relax** — **#1011** “FAIL → WARN” per Phase 2 amendment narrative in architect state (`docs/PEARL_ARCHITECT_STATE.md:1444-1450`).
8. **Worldwide Surface 4 / 6 / 1 P0 wave** — classifier, marketing YAML, catalog variation tied in program spec amendment (`docs/specs/WORLDWIDE_CATALOG_GO_LIVE_V1_PROGRAM_SPEC.md:87-114`).
9. **Pearl Star Qwen-Image completion** — commit message **#1018** on `main` log (shard 08).
10. **LLM caller audit clean** — `audit_llm_callers.py` violation_count 0 (session run).

---

## 4. Where we’re drifting (severity-ranked)

| Sev | Finding | Receipt |
|-----|---------|--------|
| **High** | **CI spec header** still “proposed” / “no remediation authorized” while **Phases 1–2 merged** on `main` | `docs/specs/CI_BASELINE_RECOVERY_V1_SPEC.md:8-10` vs commits **#997/#1011** etc. |
| **High** | **Coordination drift:** `ws_per_chapter_overlay_enforcement_impl_20260508` remains **`proposed`** though `book_quality_gate.py` implements `overlay_rule` paths | `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` rows ~130-131 vs `phoenix_v4/quality/book_quality_gate.py:185-297` |
| **High** | **PER-CHAPTER cap ITEM-2** not closed — phrase still allowlisted | `config/quality/refrain_allowlist.yaml:281`; spec `docs/specs/PER_CHAPTER_OVERLAY_ENFORCEMENT_V1_SPEC.md:13` |
| **Medium** | **WORLDWIDE / GO_LIVE spec** top banner still “proposed” while Phase 1 P0 described as substantively complete | `docs/specs/WORLDWIDE_CATALOG_GO_LIVE_V1_PROGRAM_SPEC.md:3` vs §“Phase 1 P0 progress” `87-114` |
| **Medium** | **MANGA GTM** still states “24 brands, 12 languages” — contradicts Path X **37** and 4-locale program emphasis | `docs/MANGA_GTM_PLAN.md:5` |
| **Medium** | **`docs/specs/WORLDWIDE_…` HEAD anchor** stale inside spec (`e25bd63…`) vs audit `main` `515de6…` | `docs/specs/WORLDWIDE_CATALOG_GO_LIVE_V1_PROGRAM_SPEC.md:91` vs `git rev-parse origin/main` |
| **Medium** | **QI-FOUNDATION-CANONICAL-RECONCILIATION-01** still **proposed** — canonical brand id is `qi_foundation_cultivation` | `docs/PEARL_ARCHITECT_STATE.md:840`; `config/manga/canonical_brand_list.yaml:288` |
| **Low** | **Marketing deep research** tree is thin (`README` + one report) vs “all subdirectories” expectation | `marketing_deep_research/*.md` glob = 2 files |
| **Low** | **Requested spec path** `docs/specs/PEARL_PRIME_WORLDWIDE_CATALOG_PLAN_V1.md` **absent** from repo | Glob `**/PEARL_PRIME_WORLDWIDE*` → 0 files |

---

## 5. Critical gaps (operator must know)

1. **555 cells claim unverified** — No repo-local definition matched “555 brand-locale-surface cells”; marketing SSOT V1 implements **222** brand×surface cells with documented locale deferral.
2. **Multi-phase overlay program incomplete** — Implementation exists but **Phase 3 allowlist removal** not done; workstream status not updated to reflect code landing.
3. **Documentation / cap truth lag** — “Proposed” banners on specs that already drove merged engineering reduce auditability for the next operator session.

---

## 6. Operator decisions needed

- **555 metric:** Confirm definition (PR #1023 body) vs current **222** YAML + future locale expansion — ratify single SSOT formula.
- **PER-CHAPTER ITEM-2:** Authorize removal of `your nervous system` allowlist row once overlay gate proven in CI/book smoke (`config/quality/refrain_allowlist.yaml:281`).
- **QI reconciliation:** Approve or reject **QI-FOUNDATION-CANONICAL-RECONCILIATION-01** (`docs/PEARL_ARCHITECT_STATE.md:840`) to close `qi_foundation` alias drift in downstream plans.
- **CI spec status:** Bump `docs/specs/CI_BASELINE_RECOVERY_V1_SPEC.md` status text to match merged phases (doc-only governance hygiene).

---

## 7. Recommended next steps (prioritized)

1. **Pearl_PM + Pearl_Architect:** Doc-only alignment pass — spec `status` fields + WORLDWIDE HEAD anchor + CI spec banner vs `main` (cap **WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01**, **CI-BASELINE-RECOVERY-V1-01**).
2. **Pearl_Dev:** Close **PER-CHAPTER** Phase 3 per spec; update `ACTIVE_WORKSTREAMS.tsv` for overlay ws to `in_progress`/`complete` with PR SHAs.
3. **Pearl_Research / Pearl_PM:** Archive or refresh **MANGA_GTM_PLAN.md** brand/locale counts vs Path X canon.
4. **Pearl_Int / Pearl_Dev:** Finish **IMG** activation criteria — spend TSV population, batch runner live mode (project **PRJ-DUAL-PATH-IMAGE-RENDER-V1** already `wired_dry_run` in `ACTIVE_PROJECTS.tsv:11`).

---

**Full methodology, per-phase tables, registry pair checks, PR archaeology, and appendices:** `artifacts/qa/system_drift_audit_full_report_2026-05-10.md`.
