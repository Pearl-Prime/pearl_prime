# Program State — Single Source of Truth

**LAST VERIFIED:** 2026-06-25 @ `origin/main` `233397671e`

> **RULE:** Verify against `origin/main`, never git date or the working tree (shared-tree branch-churn shows
> other-branch/stale state). This is the entry point — if another doc disagrees with this, this wins or that doc is stale.

> **GLOSSARY (read this — it has caused repeated confusion):**
> **Listing** = catalog metadata (title/subtitle/description/cover/dashboard — what a book is *about*).
> **EPUB** = the actual readable, sellable file a customer downloads.
> We have **~1,519 listings** and **1 catalog EPUB assembled** (first Waystream EPUB, #1923 — see Production-Gate).
> "Books" in most docs means *listings* — do NOT read it as "readable/sellable books."

## Current Status by Track

### en_US Listings
- **Status:** **DONE**
- **Details:** **1,519 LISTINGS** (storefront metadata — NOT readable EPUBs) across 26 brands + Waystream (800),
  on `main` (PR #1801–#1839). **Total counts:** 2,187 `book_plans_en_us` + 28 brand dashboards.
- **Wave 2026-06-25:** +462 **plannable** books from arc seeding (educators 1→11 arcs, nyc_executives 4→13 arcs;
  PR #1913). **Total plannable: 12,138.** ⚠ "Buildable" here = *arc + listing exist*, NOT spine-buildable: a 4-cell
  rebuild (#1922) shows these educators/nyc_executives cells still **fail tuple-viability preflight** (see
  Production-Gate caveat) — they are not yet renderable EPUBs.

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
- **Status:** **FIRST EPUB SHIPPED — durable on `main` (1 EPUB); validated brand generalizes across 4 cells**
- **Details:** Book assembly is **deterministic atom-composition** (no LLM at build; thin pools must raise
  `InsufficientVariantsError` → fix by adding atoms, never LLM-expand — verify `pearl_writer_expand.py` is NOT on the
  spine/production path). ✅ **F1/F4 + F2/F7 precision all on `main`** via PR #1919 (`ae4991bd3a`). **First gate-passing
  Waystream EPUB SHIPPED** (PR #1923, `4e6320b19c`): `corporate_managers × burnout × overwhelm`, register **PASS**,
  ei_v2 0.62, 13,759 words, 1.7 MB → `artifacts/epubs/way_stream_sanctuary/`. **3 generalization cells**
  (anxiety/false_alarm, boundaries/shame, boundaries/comparison) all register-PASS, ei_v2 0.62–0.64 — corporate_managers
  scales with **zero engine work** (loop spine CLI over the F006 arc matrix + `build_epub.py`).
  **1 catalog EPUB assembled** (was 0).
- ⚠ **Thin-persona caveat (the next lane):** the +462 arc-seeded educators/nyc_executives cells are **NOT spine-buildable
  yet** — a 4-cell rebuild (#1922) shows all 4 **HARD-FAIL tuple-viability preflight** before Stage 1. P1/P2 seeded arcs
  + **slot-keyed** pools (`atoms/<p>/<t>/STORY/`) but NOT the **engine-keyed** pools (`atoms/<p>/<t>/<engine>/CANONICAL.txt`)
  the spine builder reads → `NO_STORY_POOL`. Also: `educators/nyc × *_false_alarm` needs a **binding-governance call**
  (`false_alarm` not in `imposter_syndrome.allowed_engines`); `nyc × anxiety/false_alarm` needs **one band-1 STORY atom**.
  Next = engine-keyed STORY-pool seeding (≥12 banded variants/cell) + the binding decision — NOT gate/engine work.
- **Wave 2026-06-25 (teacher-bank unblock):** 12 teachers now have `TEACHER_DOCTRINE` atoms (PR #1914) — all 26
  brands unblocked from the `library_34` fallback. 29 `CANONICAL.txt` files backfilled for educators + nyc_executives
  thin slots (PR #1915); 69/69 tests pass.
- **Infra gaps RESOLVED (#1924, `68163beab1`):** `sai_ma` `positioning_profile` was a **dangling ref** — added the
  `devotional_companion` profile to `author_positioning_profiles.yaml`. `kenjin` added to
  `config/catalog_planning/teacher_persona_matrix.yaml` (mirrors joshin's guardrails). **Q-KENJIN-01 OPEN:** the matrix
  has no `active`/`tier` field, so kenjin is a first-class entry = active-by-presence — **operator to confirm**.

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
- **Status:** **LIVE** — renders sample/listing data; **1 real EPUB now exists** in `artifacts/epubs/way_stream_sanctuary/`
  (#1923) but is **not yet attached** to the storefront/GHL feed. Remaining downloadable files = 0 until the attach
  pipeline runs (GHL feed auto-promotes paid items on attach).

---
*Supersedes all previous status reports and planning baselines (incl. the May 2026 worldwide plan). Latest session
detail: `docs/sessions/SESSION_HANDOFF_2026-06-24_advisory_router_session.md`.*
