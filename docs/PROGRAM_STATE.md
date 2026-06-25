# Program State — Single Source of Truth

**LAST VERIFIED:** 2026-06-25 @ `origin/main` `4ecf3a67fd`

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
- **Wave 2026-06-25:** +462 buildable books from arc seeding (educators 1→11 arcs, nyc_executives 4→13 arcs;
  PR #1913). **Total buildable: 12,138.**

### Waystream titles / cover↔title
- **Status:** **DONE (deduped + hard-gated on main)**
- **Details:** Waystream is **800 distinct titles / 800 distinct subtitles / 800 distinct (title,subtitle) pairs** on
  `main` (verified from `config/source_of_truth/book_plans_en_us/way_stream_sanctuary__*.yaml` → catalog CSV/JSON →
  covers). The previously-stranded dedup landed; the prior "186/800" figure was stale SSOT carryover. A **hard-gate**
  now blocks regression: `scripts/ci/check_waystream_catalog_uniqueness.py` (asserts 800 distinct titles + subtitles +
  pairs against the plan SSOT, with a dry-run achievability path for template-only PRs) is wired as **gate #20** in
  `scripts/run_production_readiness_gates.py`. **Covers are 100% resynced** to current titles — verified by
  `scripts/publish/waystream_covers/verify_resync.py` (`plans=800 csv=800 covers=800 dashboard=800`, 0 structural
  errors, `--ocr` confirms cover text matches title); covers are gitignored local artifacts (slug-keyed, two-stage
  PIL-over-FLUX), not committed. Localization can inherit clean titles.

### Production-Gate / Real-EPUBs
- **Status:** **IN PROGRESS — first pilot gate-passed LOCALLY, not yet durable**
- **Details:** Book assembly is **deterministic atom-composition** (no LLM at build; thin pools must raise
  `InsufficientVariantsError` → fix by adding atoms, never LLM-expand — verify `pearl_writer_expand.py` is NOT on the
  spine/production path). First Waystream pilot (`corporate_managers × burnout × overwhelm`) reached **register PASS /
  BUILD_EXIT=0** via `cc4056b259` (F6/F7/F13) + the F1/F4 fix. ✅ **F1/F4 now RESOLVED on `main` via PR #1919
  (`ae4991bd3a`, consolidates competing specs + wires canonical CLI + lands the previously-stranded `4474753be9`
  fix) — the first EPUB is reproducible from `main`.** Residual F-classes for the next cells: F2 (phrasal-verb
  precision), F7 (composer-output cap).
  **0 catalog EPUBs are assembled/sellable yet.**
- **Wave 2026-06-25 (teacher-bank unblock):** 12 teachers now have `TEACHER_DOCTRINE` atoms (PR #1914) — all 26
  brands unblocked from the `library_34` fallback. 29 `CANONICAL.txt` files backfilled for educators + nyc_executives
  thin slots (PR #1915); 69/69 tests pass.
- **Known infra gaps (separate lane):** `sai_ma` missing `positioning_profile`; `kenjin` missing from
  `teacher_persona_matrix`.

### GHL marketing feed
- **Status:** **LIVE**
- **Details:** `marketing_feed.json` published on brand-admin Pages (public HTTPS) (#1866/#1867/#1875/#1882); R2
  provisioned; 15-topic integration; all 15 funnel landings → GHL capture. Design: paid items gate on **real attached
  asset** (`pending_asset` until then), free items on **asset-exists**; **free-content-first** — paid auto-promotes on
  attach. Funnel is live on free content + listings; paid lights up as real EPUBs attach.

### Localization
- **Status:** **NEXT (0%)** — Waystream titles are now distinct + hard-gated on `main` (see above), so the prior
  blocker is cleared; 13 locales can inherit clean titles without multiplied duplication. Planning established;
  execution not started.

### Manga ja_JP
- **Status:** **TITLED + PILOT PRODUCED**
- **Details:** 273 `series_plans_ja_JP` on `main`. Pilot: 304 composed v3 segments (#1236), wave1 ep_001 + pipeline
  (#1860), ep_003–010 scripts (#1189). Unattended-render frontier = the Pearl Star queue (ratified canonical for
  renders; the GitHub Actions self-hosted runner is fragile — 403 + 1800s timeouts). Audit: `docs/MANGA_RECOVERY_AUDIT.md`.

### Storefront
- **Status:** **LIVE** — renders sample/listing data; real downloadable files = 0 (gated on assembled EPUBs + the
  attach pipeline; GHL feed auto-promotes on attach).

---
*Supersedes all previous status reports and planning baselines (incl. the May 2026 worldwide plan). Latest session
detail: `docs/sessions/SESSION_HANDOFF_2026-06-24_advisory_router_session.md`.*
