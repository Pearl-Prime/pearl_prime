# Q2 — In-Flight Workstream Survey

**Date:** 2026-04-29

## A. PR state

Source: `gh pr list --state open --limit 100`.

| metric | value |
|---|---|
| open PRs | **42** |
| MERGEABLE | 17 |
| CONFLICTING | 25 |
| age ≤2d | 10 |
| age 3-7d | 10 |
| age 8-14d | 11 |
| age >14d | **11 (all CONFLICTING — abandonment candidates)** |

**Stale-conflicting cohort (>14d, mergeable=CONFLICTING):**
PRs `#326`, `#328`, `#336`, `#344`, `#363`, `#369`, `#377`, `#393`, `#407`, `#416`, `#419`, `#426`, `#427`, `#430`, `#444`, `#445`, `#446`, `#450`, `#495`, `#544`, `#545`, `#546`, `#568`. Most are predecessor-superseded by post-#700 work. Recommend close-or-rebase pass — see `q10_repo_cruft.md`.

**Active mergeable cohort (≤7d, mergeable=MERGEABLE):**
`#787`, `#797`, `#798` (showcase format-grid overhaul, 985 files), `#801` (JP freebie funnel — paper-only), `#802` (drift autopsy 1 of 2), `#803` (manga community-assets research). These are the live work.

## B. Workstream registry state

Source: `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` (104 data rows, all 15-column schema-conformant — earlier malformed-row issue is resolved).

| status | count |
|---|---|
| completed | 66 |
| active | 16 |
| proposed | 13 |
| in_progress | 4 |
| pending | 3 |
| blocked | 2 |

**In-flight footprint:** 16 active + 4 in_progress + 13 proposed = **33 workstreams in motion or queued**. 2 explicitly blocked.

## C. Project state

Source: `artifacts/coordination/ACTIVE_PROJECTS.tsv` (4 active projects):

| project | owner | last_updated | dominant subsystem |
|---|---|---|---|
| `proj_state_convergence_20260328` | Pearl_PM | 2026-04-07 | repo coordination — STALE 22 days |
| `proj_pearl_prime_bestseller_rebase_20260425` | Pearl_PM | 2026-04-28 | pearl_prime + core_pipeline |
| `proj_manga_first_ship_20260425` | Pearl_PM | 2026-04-25 | manga_pipeline + integrations + video + translation — pending GATE-OP-1 (operator R2 secrets) + GATE-OP-2 (Pearl Star marker) |
| `proj_manga_catalog_reconciliation_20260426` | Pearl_Architect | 2026-04-26 | manga_pipeline + manga_catalog |

`proj_state_convergence_20260328` is the oldest active project, last updated 2026-04-07. Either close it or refresh it — 22-day gap with no signal.

## D. The chronic open PRs (Pearl News + Pearl Prime work that won't land)

These warrant individual operator attention; they're not abandonment candidates but they're not landing either:

- **PR #393** ("Pearl News: first live WP cycle + quality report") — open since 2026-04-12, **CONFLICTING**. The cycle DID succeed (81 publish_log rows, articles live on site) — the PR documentation is stale, not the code. Needs rebase or scope-close.
- **PR #407** ("Pearl News: Gemma3:27b EN expansion on Pearl Star; retire qwen3:14b") — open since 2026-04-12, CONFLICTING. Same shape: the model swap likely already happened; the PR is the trailing receipt.
- **PR #623** ("first real book assembled + LoRA training VRAM blocker") — open since 2026-04-24, CONFLICTING. **The first-book-assembled artifact AND the VRAM blocker are both load-bearing**; this PR's content needs to land or the findings need to be re-captured elsewhere.
- **PR #587** ("wire deterministic teacher slots into v52 render") — open since 2026-04-23. Likely shipped via subsequent direct commits to teacher_showcase (PRs #781, #785).
- **PR #589** ("align injection_resolver tests") — open since 2026-04-23, MERGEABLE. Should just merge.

Recommendation: **48-hour PR triage sweep** — close-or-rebase the 11 oldest CONFLICTING PRs after a single owner-judgment pass.

## E. The 4 P0 work-streams that gate everything else

Synthesized from active workstreams + open PRs:

1. **`proj_manga_first_ship_20260425` GATE-OP-1 + GATE-OP-2 + queue_panel_renders** — until operator adds `R2_*` to GitHub Actions secrets, installs Pearl Star marker, AND `scripts/manga/queue_panel_renders.py` is committed (PR #725 for the script exists, runbook still references it as uncommitted), the manga pipeline cannot ship a single episode.
2. **Pearl Prime EPUB packager** — no PR currently in flight to package chapter prose into deliverable EPUB. This is the missing piece between authored content and KDP. A single scripts/publish/build_epub.py + flow into pipeline would unlock book ship. **Phase 1 critical path.**
3. **Translation atom coverage closure** — zh_CN ~2,200 atoms pending, ja_JP ~366 remaining (see `proj_manga_first_ship` blockers). Until closed, ja_JP/zh_TW/zh_CN locale ship is held for both books and manga.
4. **Storefront distribution layer** — `kdp_comics_upload.py` and `webtoon_canvas_upload.py` exist as upload-package builders (manual-paste). No KDP for books, no Apple Books, no LINE Manga. **Phase 1 cliff.**

## F. Cross-cutting risk

Every active project depends on multiple subsystems. `proj_manga_first_ship_20260425` alone names **manga_pipeline + integrations + video_pipeline + translation** as its subsystem set. The 4-project active set covers 8 of the 19 subsystems. The other 11 subsystems (audiobook_pipeline, podcast_pipeline, video_pipeline, ei_v2, brand_admin, marketing, freebie, recommendations, dashboard, trend_feeds, storefront_distribution) **have no active project shepherding them** — they accrue spec/code without a project-level coordination owner.

This is the structural failure that produced 24,820 lines/week and 0 ships/week.
