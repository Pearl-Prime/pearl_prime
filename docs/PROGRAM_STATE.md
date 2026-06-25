# Program State — Single Source of Truth

**LAST VERIFIED:** 2026-06-24 @ `origin/main` `a5b7c06a0d`

> **RULE:** Verify against `origin/main`, never git date or the working tree (shared-tree branch-churn shows
> other-branch/stale state). This is the entry point — if another doc disagrees with this, this wins or that doc is stale.

> **GLOSSARY (read this — it has caused repeated confusion):**
> **Listing** = catalog metadata (title/subtitle/description/cover/dashboard — what a book is *about*).
> **EPUB** = the actual readable, sellable file a customer downloads.
> We have **~1,519 listings** and **~0 catalog EPUBs assembled.** "Books" in most docs means *listings* —
> do NOT read it as "readable/sellable books."

## Current Status by Track

### en_US Listings
- **Status:** **DONE**
- **Details:** **1,519 LISTINGS** (storefront metadata — NOT readable EPUBs) across 26 brands + Waystream (800),
  on `main` (PR #1801–#1839). **Total counts:** 2,187 `book_plans_en_us` + 28 brand dashboards.

### Waystream titles / cover↔title
- **Status:** **OPEN (duplication live on main)**
- **Details:** Waystream titles are **186 distinct / 800**, subtitles **398 / 800** on main — a prior dedup
  **stranded** on an unmerged branch. Fix = the amended SEO/title-repoint plan (hard-gate distinct titles + unique
  (title,subtitle) pairs; persona-scenario form over the colliding `Topic:{angle}`; **re-composite covers** keyed by
  plan book_id — covers are two-stage PIL-over-FLUX, so re-titling is **zero-GPU**). Run on Sonnet; land on main.

### Production-Gate / Real-EPUBs
- **Status:** **IN PROGRESS — first pilot gate-passed LOCALLY, not yet durable**
- **Details:** Book assembly is **deterministic atom-composition** (no LLM at build; thin pools must raise
  `InsufficientVariantsError` → fix by adding atoms, never LLM-expand — verify `pearl_writer_expand.py` is NOT on the
  spine/production path). First Waystream pilot (`corporate_managers × burnout × overwhelm`) reached **register PASS /
  BUILD_EXIT=0** via the F6/F7/F13 + F1/F4 register strengthening, **now LIVE on `main` as `8e21b6ce1c`**
  (`dedupe_register_f1_paragraphs` + `ensure_unique_chapter_closings` present, with more F4 passes than the old local
  branch). ✅ **The previously-stranded `4474753be9` is fully SUPERSEDED — its F1/F4 fix re-landed cleanly as
  `8e21b6ce1c`; do NOT cherry-pick the local commit (it predates newer F7 work and would regress main).** Residual
  F-classes for the next cells: F2 (phrasal-verb precision), F7 (composer-output cap). **0 catalog EPUBs are
  assembled/sellable yet.**

### GHL marketing feed
- **Status:** **LIVE**
- **Details:** `marketing_feed.json` published on brand-admin Pages (public HTTPS) (#1866/#1867/#1875/#1882); R2
  provisioned; 15-topic integration; all 15 funnel landings → GHL capture. Design: paid items gate on **real attached
  asset** (`pending_asset` until then), free items on **asset-exists**; **free-content-first** — paid auto-promotes on
  attach. Funnel is live on free content + listings; paid lights up as real EPUBs attach.

### Localization
- **Status:** **NEXT (0%)** — hold until Waystream titles are distinct (so 13 locales inherit clean titles, not
  multiplied duplication). Planning established; execution not started.

### Manga ja_JP
- **Status:** **TITLED + PILOT PRODUCED**
- **Details:** 273 `series_plans_ja_JP` on `main`. Pilot: 304 composed v3 segments (#1236), wave1 ep_001 + pipeline
  (#1860), ep_003–010 scripts (#1189). Unattended-render frontier = the Pearl Star queue (ratified canonical for
  renders; the GitHub Actions self-hosted runner is fragile — 403 + 1800s timeouts). Audit: `docs/MANGA_RECOVERY_AUDIT.md`.

### Pearl Prime — Canonical CLI + Spec Surface
- **Status:** **CONSOLIDATED (2026-06-25)**
- **Details:** Single craft + runtime authority = `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md`. Canonical
  release build = `scripts/run_pipeline.py --pipeline-mode spine --quality-profile production --exercise-journeys
  --render-book` (documented at top of `run_pipeline.py`; argparse defaults stay `--pipeline-mode registry`,
  `--quality-profile production`; **spine is NOT the default** — Pearl Prime callers pass it explicitly). HOLISTIC
  chapter-architecture v2 (8-role doctrine) + ONE-PATH LOCKDOWN (D1–D20 canonical-path matrix + gold-reference combo)
  are folded into the OVERLAY under dated "Added from" sections; both source specs ⛔ SUPERSEDED. `evaluate_register →
  register_gate_report.json` wiring active; `pearl_writer_expand.py` confirmed NOT on the spine+production path
  (`section_packet_composer.expand_thin_sections` default-False, unwired to any CLI flag).

### Storefront
- **Status:** **LIVE** — renders sample/listing data; real downloadable files = 0 (gated on assembled EPUBs + the
  attach pipeline; GHL feed auto-promotes on attach).

---
*Supersedes all previous status reports and planning baselines (incl. the May 2026 worldwide plan). Latest session
detail: `docs/sessions/SESSION_HANDOFF_2026-06-24_advisory_router_session.md`.*
