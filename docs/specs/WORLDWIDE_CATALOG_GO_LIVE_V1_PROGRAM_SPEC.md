# WORLDWIDE-CATALOG-GO-LIVE-V1 — Program Spec (operator-readable)

**Status:** proposed (pending operator approval of phase plan and Q1–Q5)  
**PROJECT_ID:** PRJ-WORLDWIDE-CATALOG-GO-LIVE-V1  
**Last updated:** 2026-05-08  
**Owner:** Pearl_PM  
**Ratified cap:** `docs/PEARL_ARCHITECT_STATE.md` → **WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01**

---

## Purpose

One **durable program record** for worldwide production go-live planning across **catalog, dashboards, brand-admin delivery, author coverage, marketing velocity, spine CLI performance, executive visibility, command-UI alignment, and worktree hygiene** — so remediation fans out from a **single gap matrix**, not ad-hoc sessions.

## Scope (operator request)

- **37 manga brands** × **4 locales** (`en_US`, `ja_JP`, `zh_TW`, `zh_CN`) **as stated** — must be reconciled with **Path X** separation (book pipeline vs manga pipeline) already documented in `BRAND_ADMIN_CANONICAL_PACKAGE.md` and `docs/PEARL_ARCHITECT_STATE.md`.

## Non-scope

- No code, config edits, or merges as part of **this** packet (audit + program scaffolding only).

## Authority (read order for implementers)

See the cap entry — includes: `docs/SESSION_UNITY_PROTOCOL.md`; `docs/PEARL_PM_STATE.md`; `docs/PEARL_ARCHITECT_STATE.md`; `docs/DOCS_INDEX.md`; `specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md`; `specs/PHOENIX_V4_5_WRITER_SPEC.md`; `docs/PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md`; `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md`; `BRAND_ADMIN_CANONICAL_PACKAGE.md`; `docs/OLD_CHAT_AND_HOME_PROMOTION_SPEC.md`.

## Deliverables (already landed by this packet)

| Artifact | Path |
|----------|------|
| Per-surface gap matrix + phased roadmap + Q1–Q5 | `artifacts/qa/go_live_readiness_audit_2026-05-08.md` |
| Architect cap | `docs/PEARL_ARCHITECT_STATE.md` |
| Program + workstreams | `artifacts/coordination/ACTIVE_PROJECTS.tsv`, `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` |
| Operator spec (this file) | `docs/specs/WORLDWIDE_CATALOG_GO_LIVE_V1_PROGRAM_SPEC.md` |

## Phase plan (summary)

1. **Phase 1 — Visibility unlock:** Surfaces **2, 6, 8** (dashboard truth, executive view, marketing SSOT).  
2. **Phase 2 — Active-brand wiring:** Surfaces **3, 4, 7, 9**.  
3. **Phase 3 — Catalog completion:** Surfaces **1, 5** (catalog + authors).  
4. **Phase 4 — Production go-live:** Surface **10** plus cross-cutting hygiene and monitoring.

**Production go-live** is defined **only** by **Phase 4 exit criteria** in the audit Markdown.

## Operator decisions required

Questions **Q1–Q5** are listed verbatim at the **end** of `artifacts/qa/go_live_readiness_audit_2026-05-08.md`.

## Handoff

After operator answers **Q1–Q5**, Pearl_PM routes **Phase 1** implementation prompts against the **`ws_worldwide_gl_*`** rows opened for this project.

---

## AMENDMENT-2026-05-08-PRIORITIES

Operator decisions ratified as the activation gate for `WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01`.

### Q1-Q5 (verbatim)

- Q1 = yes (phase order: visibility -> wiring -> catalog -> go-live)
- Q2 priorities:
  - P0 = Surface 1 (Catalog planning), Surface 4 (Active/inactive brands), Surface 6 (Marketing volume SSOT)  [all 3 RED surfaces]
  - P1 = Surface 2 (Brand dashboard), Surface 8 (Executive dashboard)
  - P2 = Surface 3 (Weekly packaging), Surface 5 (Author/bio), Surface 7 (Spine/CLI perf), Surface 9 (Command UI <-> CLI), Surface 10 (Disk/worktrees)
- Q3 = commit A1 (Pearl_Localization 12 scripts) + A2 (Pearl_Int CosyVoice2 audit TSV) + A5 (Pearl_Dev overlay Phase 1) + Pearl_DevOps CI hygiene (5 files); abandon A6 + stale drafts/contaminated worktree leftovers
- Q4 = brand_wizard YAML confirmed as canonical SSOT for active/inactive brand classification
- Q5 = Weekly cadence: Monday, both email + file delivery

### Per-surface priority lock

| Surface | Name | Priority |
|---|---|---|
| Surface 1 | Catalog planning | P0 |
| Surface 2 | Brand dashboard | P1 |
| Surface 3 | Weekly packaging | P2 |
| Surface 4 | Active/inactive brands | P0 |
| Surface 5 | Author/bio | P2 |
| Surface 6 | Marketing volume SSOT | P0 |
| Surface 7 | Spine/CLI perf | P2 |
| Surface 8 | Executive dashboard | P1 |
| Surface 9 | Command UI <-> CLI | P2 |
| Surface 10 | Disk/worktrees | P2 |
