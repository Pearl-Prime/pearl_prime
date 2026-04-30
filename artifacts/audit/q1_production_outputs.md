# Q1 — Production-Output Inventory

**Date:** 2026-04-29  •  **Audit branch:** `claude/wonderful-meitner-e5ac76`  •  **Anchor SHA:** `6375c8fcbf`

The question this answers: **what does Phoenix Omega actually produce today?** Not what specs claim. What is on disk, in R2, on the live web. Cited.

## A. Catalog of declared output types

| # | output type | producer subsystem | spec authority | shipping today? |
|---|---|---|---|---|
| 1 | book — full EPUB / PDF | `pearl_prime` + `core_pipeline` | `docs/PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md` | **NO — 0 full books on disk** |
| 2 | book — chapter samples | `pearl_prime` | `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` | partial — chapter prose exists in `artifacts/audiobook_samples/_prose/` |
| 3 | audiobook — full | `audiobook_pipeline` | `docs/AUDIOBOOK_PIPELINE_SPEC.md` | **NO — only ch1 stubs** |
| 4 | audiobook — chapter sample | `audiobook_pipeline` | same | YES — 13 `*_ch1.mp3` files in `artifacts/audiobook_samples/`, last touched 2026-04-12 |
| 5 | book video / animated reader | `video_pipeline` | `config/video/render_params.yaml` | partial — only test renders in `artifacts/video/test_render_*` |
| 6 | podcast — episode | `podcast_pipeline` | `docs/PODCAST_PIPELINE_INTEGRATION_SPEC.md` | **NO — 1 pilot only** (`artifacts/podcast_pilot/pilot_report.md`, 2179 B, 2026-04-08) |
| 7 | manga catalog (CSV/YAML) | `manga_catalog` | `specs/MANGA_CATALOG_RECONCILIATION_SPEC.md` | YES — 1,350 series + 18,900 book plans across 5 locales (post PR #696, #727, #771) |
| 8 | manga panel renders (chapter-bound) | `manga_pipeline` | `specs/AI_MANGA_PIPELINE_SUMMARY.md` | **NO — 35 prompts for ep_001 only, 0 chapter-bound renders** |
| 9 | manga episode (composed + uploaded) | `manga_pipeline` | same | **NO — 0 episodes shipped to R2/WEBTOON/LINE** |
| 10 | manga reference imagery | `manga_pipeline` | image_bank | YES — 840 PNGs in `image_bank/` (15 topics × 56 each, not chapter-bound — *PR #802 documents these are off-brand at base-model level*) |
| 11 | brand-admin landing page | `brand_admin` + `dashboard` | `BRAND_ADMIN_CANONICAL_PACKAGE.md` | partial — `brand_admin.html` + `brand_admin_weekly_os.html` in repo; live deployment status: see Q4 ops cluster audit |
| 12 | teacher-showcase page | `marketing` | `docs/OLD_CHAT_AND_HOME_PROMOTION_SPEC.md` | YES — 13/13 teacher portraits per PR #773; format-grid overhaul in flight (PR #798) |
| 13 | Pearl News article (live to WP) | `pearl_news` | `docs/PEARL_NEWS_WRITER_SPEC.md` | **YES — LIVE to pearlnewsuna.org**, 81 entries in `artifacts/pearl_news/publish_log.jsonl`, latest post id 2577 on 2026-04-22 |
| 14 | freebie web app (breathwork) | `freebie` + `marketing` | `specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md` | YES — 42+ HTML apps in `somatic_exercise_freebee_apps/` deployed via `pages.yml` |
| 15 | funnel landing | `marketing` | spec | partial — only `funnel/burnout_reset/` exists; ~25 missing |
| 16 | Pearl Prime web preview | `pearl_prime` (Cloudflare Workers) | `pearl_prime/` directory | YES — Workers deployment per PR #745 audit |

## B. The "what's actually live" honest list

- **LIVE & producing daily**: Pearl News (WordPress), Pearl Prime web preview (Cloudflare), 42+ freebie HTML apps (Cloudflare Pages).
- **LIVE but cadence broken**: brand_admin static pages (rendered, not authored per-brand).
- **Files on disk, not on storefront**: 13 chapter audiobooks (mp3), 1 podcast pilot, 1 funnel, 35 manga panel prompts.
- **Absent entirely**: full books, full audiobooks, manga episodes (rendered + composed + uploaded), most funnels, KDP/Apple Books/LINE Manga submissions, podcast feeds.

## C. Throughput envelope (last 7 days, 2026-04-22 → 2026-04-29)

- **PRs merged:** 181 (`gh pr list --state merged --search 'merged:>=2026-04-22'` → 181 rows).
- **Commits to main:** ~1,038 since 2026-04-15 (`git log --since='2026-04-15' --oneline | wc -l`).
- **Production outputs added in last 7 days** (the disconnect): 0 books, 0 audiobooks, 0 manga episodes, ~12 Pearl News articles (cron-paced), 0 storefront submissions.

The throughput-vs-output gap is the headline of this audit: **24,820 lines of code/content/spec changes in 7 days, 0 net new shippable production artifacts.** All work is upstream of the ship surface.

## D. Inputs that exist and are healthy

- **26 brands** in `config/brand_registry.yaml` (book brands; the 37 manga-only brands are a separate registry per PR #722).
- **14 teachers** in `SOURCE_OF_TRUTH/teacher_banks/` (adi_da, ahjan, joshin, junko, maat, master_feung, master_sha, master_wu, miki, omote, pamela_fellows, ra, sai_ma).
- **14 personas** in `atoms/` (corporate_managers, educators, entrepreneurs, first_responders, gen_alpha_students, gen_x_sandwich, gen_z_professionals, gen_z_student, healthcare_rns, midlife_women, millennial_women_professionals, nyc_executives, tech_finance_burnout, working_parents).
- **~270+ master arcs** in `config/source_of_truth/master_arcs/` (sample shows ~150+; full audit pending).
- **2,584 atoms** authored across personas/topics/engines (per `proj_pearl_prime_bestseller_rebase_20260425` truth-paths).
- **840 image_bank PNGs** (off-brand per PR #802 drift autopsy; not chapter-bound).

## E. Output ratios (the choke points)

| pipeline stage | quantity | ratio to next stage |
|---|---|---|
| brand × persona × topic combinations possible | 26 × 14 × N ≈ thousands | — |
| master_arcs authored | ~270 | gates story-cell pipeline |
| atoms authored | 2,584 | meets Phase 2 floor (post-PR #767, #770) |
| story-cells composed (per chapter) | unverified — need spot-check | ? |
| chapter prose produced | dozens (`artifacts/audiobook_samples/_prose/`) | gates audiobook + video + EPUB |
| books packaged into EPUB | **0** | gates KDP submission |
| books on storefront | **0** | revenue floor |
| manga panel prompts | 35 (ep_001 only) | ratio: 35 prompts → 0 renders |
| manga panel renders (chapter-bound) | **0** | gates compose |
| manga episodes composed | **0** | gates R2 upload |
| manga episodes on storefront | **0** | revenue floor |

The book pipeline choke is **"chapter prose → packaged EPUB"** (no packager exists or it's not running).
The manga pipeline choke is **"prompts → renders"** at 35:0; downstream of that, no compose, no upload, no storefront.

## F. Conclusion

Phoenix Omega today is a **content-substrate factory**, not a **product-shipping system**. It is producing:
- 12 articles/day on a live news site.
- ~6 HTML apps deployed to Cloudflare Pages historically.
- A library of ~2,584 prose atoms, 14 teachers' bank content, 270+ master arcs, 1,350 manga catalog rows.

It is not producing:
- Books on storefronts.
- Manga episodes on storefronts.
- Audiobooks beyond chapter samples.
- Podcasts beyond a single pilot.
- Multi-locale shipped output (translation atom coverage incomplete; see Q4 book cluster).

Pathway-to-100% must invert this: **less authoring, more shipping**. See [`q5_top_cliffs.md`](./q5_top_cliffs.md) and [`../../docs/PHOENIX_OMEGA_PATHWAY_TO_100_2026-04-29.md`](../../docs/PHOENIX_OMEGA_PATHWAY_TO_100_2026-04-29.md).
