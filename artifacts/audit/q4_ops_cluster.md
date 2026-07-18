# Q4 Audit — OPS / Surfaces / Integrations Cluster

**Audit date:** 2026-04-29
**Branch:** `claude/wonderful-meitner-e5ac76`
**Scope:** 10 subsystems (pearl_news, brand_admin, dashboard, marketing, trend_feeds, recommendations, integrations, pearl_devops, freebie, storefront_distribution)
**Method:** Read-only. Authority docs verified, real outputs counted, CI runs queried via `gh`, tests counted, branch protection probed.

---

## Summary readiness table

| subsystem | owner | authority_doc | config | observable_output | last_real_output | tests | CI_workflows | active_workstreams | % complete | phase |
|---|---|---|---|---|---|---|---|---|---|---|
| pearl_news | Pearl_News | YES (`docs/PEARL_NEWS_WRITER_SPEC.md`, 29.3KB) | YES (`pearl_news/config/`, `pearl_news/prompts/`) | YES — 81 published rows in `artifacts/pearl_news/publish_log.jsonl`, 2026-04-22 most recent log; daily workflow run 2026-04-29 SUCCESS | 2026-04-29 (workflow), 2026-04-22 (log file) | 10+ test files (`tests/test_pearl_news_*.py`) | 5 (`pearl-news-daily.yml`, `pearl-news-assemble.yml`, `pearl-news-fill-qwen.yml`, `pearl-news-full-qa.yml`, `pearl-star-health.yml`) | PR #393 (open since 2026-04-12), PR #732 G4 teacher resolver (open) | **75%** | OPERATING (with open hardening PRs) |
| brand_admin | Pearl_Brand | YES (`BRAND_ADMIN_CANONICAL_PACKAGE.md`, 6.4KB) + DASH-02 ratification | YES (`config/brand_registry.yaml`, 26 brand entries) | PARTIAL — HTML surfaces exist (`brand_admin.html` 45KB, `brand_admin_weekly_os.html` 39KB, `brand-wizard-app/public/brand_admin.html`); deploy target `brand-admin-onboarding.pages.dev` via Cloudflare Pages | recent (workflow `brand-admin-onboarding-pages.yml` builds on each push to brand-wizard-app/) | partial — wizard UI not unit-tested; brand registry lint in `brand-guards.yml` | 2 (`brand-admin-onboarding-pages.yml`, `brand-guards.yml`) | DASH-02 ratified 2026-04-27 (Pearl_Brand owns dashboard) | **55%** | SHIPPING (live Pages, content gaps remain) |
| dashboard | Pearl_Brand (per DASH-02) | PARTIAL — `docs/PEARL_ARCHITECT_STATE.md` DASH-02 entry; `docs/PIPELINE_DASHBOARD_INDEX.md` is the operator entry point | NO standalone `dashboard/` directory | DOC-ONLY — `PIPELINE_DASHBOARD_INDEX.md` is an index document (18 sections), not an interactive UI; static HTMLs (`brand_admin.html`, `exec_catalog_dashboard.html`, `brand_handoff_dashboard.html`, `content_inventory.html`) live under `brand-wizard-app/public/` | 2026-04-27 (PIPELINE_DASHBOARD_INDEX.md last updated) | none | shares `brand-admin-onboarding-pages.yml` | DASH-02 just-ratified, build phase | **30%** | DOCS-FIRST — interactive dashboard is a markdown index, not a live UI |
| marketing | Pearl_Marketing | YES (`docs/OLD_CHAT_AND_HOME_PROMOTION_SPEC.md`, 13.5KB) | PARTIAL — `marketing_deep_research/` (8 patch YAMLs + report); `funnel/` exists but only contains **1** funnel (`burnout_reset/`) — spec implies "5 funnels per brand × 26 brands"; `platform_marketing/` does NOT exist | YES — `marketing_continuous.yml` runs hourly (`*/15 * * * *`) on self-hosted runner | continuous (hourly) | `tests/test_marketing_config_integration.py` (1 file) | 3 (`marketing-briefs-and-proposals.yml`, `marketing-config-gate.yml`, `marketing_continuous.yml`) | funnel-per-brand expansion not started | **20%** | EARLY — 1/130 funnels built |
| trend_feeds | Pearl_Int | YES (`docs/TREND_FEED_INTEGRATION_STRATEGY.md`, 17.4KB) | YES (`config/trend_keywords/` — tier1–4 + 4 locale YAMLs; `scripts/feeds/` 4 scripts) | YES — `research_feeds_ingest.yml` last green run 2026-04-27 14:04Z (5 consecutive successful weekly runs) | 2026-04-27 | implicit via workflow-run smoke; no dedicated unit tests located | 1 (`research_feeds_ingest.yml`, weekly Mon 12:00 UTC) | none active | **70%** | OPERATING (weekly cadence, success rate 5/5) |
| recommendations | (backlog) | NO authority doc | YES (`config/recommender/` — `constraints.yaml`, `hard_gates.yaml`, `scoring_weights.yaml`, `topic_mapping.yaml`) | NO observable output found; no scheduled workflow | n/a | `tests/test_phoenix_recommender.py` (1 file) | 0 | none | **15%** | BACKLOG — config skeleton only |
| integrations | Pearl_Int | YES (`docs/INTEGRATION_CREDENTIALS_REGISTRY.md`, 22.6KB; updated 2026-04-19) | YES (`scripts/ci/integration_env_registry.py`, 9.1KB; `skills/pearl-int/SKILL.md`, 15KB) | YES — registry tracks **23** services (`### ` count); `check_integration_env.py` operational; HTTP-calling scripts under `scripts/` ≈ 9 files | 2026-04-19 (last registry update) | implicit (`check_integration_env.py`); LLM-policy enforcement live | 2 (`llm-callers-audit.yml`, `llm-policy-enforcement.yml`) | none active | **80%** | OPERATING (well-maintained) |
| pearl_devops | Pearl_GitHub | YES (`docs/GITHUB_OPERATIONS_FRAMEWORK.md` 11.3KB, `docs/GITHUB_GOVERNANCE.md` 3.1KB, `docs/BRANCH_PROTECTION_REQUIREMENTS.md` 3.0KB, `CLAUDE.md` 5.6KB) | YES (`.github/workflows/`, **78** workflow files) | YES — `pr-governance-review.yml` posting verdicts; ruleset "Protect main" id 13451138 active since 2026-03-03 | continuous | many CI tests | **78** workflows (notable: `branch-hygiene-sweep.yml`, `change-impact.yml`, `github-governance-check.yml`, `pr-governance-review.yml`, `production-alerts.yml`) | none | **85%** | OPERATING (see branch-protection nuance below) |
| freebie | Pearl_Marketing | YES (`specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md`, 18.4KB / 239 lines) | PARTIAL — 42 standalone HTML apps in `somatic_exercise_freebee_apps/` (free breathwork tools); JP LINE funnel **plan-only** (PR #801, +2,884 / -0, OPEN) | YES — 42 HTML apps deployed via `pages.yml` to GitHub Pages (`/breathwork/` path on root site) | n/a — static, deployed | none | shared (`pages.yml`) | **PR #801 OPEN** — 12 LINE OAs, ¥180k/mo plan, no implementation yet | **35%** | PARTIAL (apps live, JP funnel paper-only) |
| storefront_distribution | (proposed/no spec) | NO spec; PROPOSED gap | PARTIAL — `scripts/publish/kdp_comics_upload.py` + `scripts/publish/webtoon_canvas_upload.py` (package-builders, not API uploaders); `scripts/release/build_epub.py`, `build_manga_webtoon.py`, `export_brand_admin_data.py`; `scripts/distribution/pre_export_check.py` | NO live output — package builders produce upload-ready folders for **manual** human upload to KDP/WEBTOON | n/a — manual-upload posture | none | 0 dedicated workflows | none | **15%** | PRE-LAUNCH SCAFFOLDING (see gap section) |

---

## P0 — Branch protection nuance (corrected)

The legacy REST endpoint `gh api repos/Ahjan108/phoenix_omega_v4.8/branches/main/protection` returns **404 "Branch not protected"**. This was flagged in the audit prompt as the P0 gap. **Verified actual state via the rulesets API**:

```
GET /repos/Ahjan108/phoenix_omega_v4.8/rulesets
→ id 13451138, name "Protect main", target=branch, enforcement=active
   rules: deletion, non_fast_forward, pull_request, required_status_checks, required_linear_history
   created 2026-03-03, last updated 2026-04-17
```

**Verdict:** main IS protected — but via the modern **Repository Ruleset** layer, not the classic branch-protection layer. The two systems do not interoperate; tools / docs / runbooks that probe `branches/main/protection` will see 404 and may falsely report "unprotected."

**Recommended follow-up (out of scope for this audit, do NOT execute):**
- Update `docs/BRANCH_PROTECTION_REQUIREMENTS.md` to specify ruleset-vs-classic-protection (currently the doc references protection rules in the legacy framing).
- Add a `gh api .../rulesets` smoke check to `scripts/git/health_check.sh` so future agents do not re-flag this.
- The 5 active rules cover the protections required by `BRANCH_PROTECTION_REQUIREMENTS.md`; no actual security gap exists.

---

## H2 — Per-subsystem detail

### 1. pearl_news

- **Authority:** `docs/PEARL_NEWS_WRITER_SPEC.md` (29,306 bytes) — present and substantial.
- **Real output:** `artifacts/pearl_news/publish_log.jsonl` has **81 lines**. Sample tail row (2026-04-22T01:48:45Z) shows successful WordPress publish with `wp_post_id: 2577` and live URL `https://pearlnewsuna.org/...`.
- **PR #393 ("first live WP cycle"):** **STILL OPEN** since 2026-04-12 (1,665 additions). The cycle code did successfully run (publish_log proves WP posts), but the wrapper PR has not been merged.
- **PR #732 ("teacher truth resolver / closes G4"):** **STILL OPEN** since 2026-04-26.
- **CI:** 5 dedicated workflows. `pearl-news-daily.yml` has cron at 22:00 and 10:00 UTC (Taiwan 6 AM / 6 PM). Last 5 runs: 3 success, 2 failure (2026-04-28 morning + evening both failed; 2026-04-29 morning passed).
- **Daily cycle progress (2026-04-22):** 8 teachers completed, 2 failed (`miki`, `maat`).
- **Tests:** 10+ `tests/test_pearl_news_*.py` files.
- **Top blockers:** (a) PR #393 + #732 unmerged — work shipping out of branch; (b) 2 teacher routes failing (`miki`, `maat`); (c) 2-of-5 recent daily runs failing.

### 2. brand_admin

- **Authority:** `BRAND_ADMIN_CANONICAL_PACKAGE.md` (6,439 bytes); DASH-02 decision ratified 2026-04-27 in `docs/PEARL_ARCHITECT_STATE.md` (Pearl_Brand owns dashboard).
- **Config:** `config/brand_registry.yaml` — 26 brand entries (matches "5 brands × multiple surfaces" framing if "5" referred to flagship EN brands; full registry has 12 JP + 8 TW + 6 HK and EN flagships).
- **Surfaces:** `brand_admin.html` (45.5KB), `brand_admin_weekly_os.html` (39.3KB), `brand-wizard-app/` full Vite app with `wrangler.toml` configured, `_redirects` and `_routes.json` present.
- **Live deploy:** `.github/workflows/brand-admin-onboarding-pages.yml` deploys to Cloudflare Pages project `brand-admin-onboarding` (likely `https://brand-admin-onboarding.pages.dev`). Triggers on push to brand-wizard-app/, config/onboarding/, brand_*.html.
- **Top blockers:** (a) Pearl_Brand handoff just-unblocked (2026-04-27) — content authoring not started; (b) per-brand landing pages content gaps for the 26 brands; (c) wizard tests are zero.

### 3. dashboard

- **Authority:** DASH-02 entry in `docs/PEARL_ARCHITECT_STATE.md`. Owner = Pearl_Brand.
- **Reality check:** "the dashboard" today is a **markdown index** (`docs/PIPELINE_DASHBOARD_INDEX.md`, last updated 2026-04-27), not an interactive web UI. There is no `dashboard/` directory. Static HTML dashboards exist under `brand-wizard-app/public/` (`exec_catalog_dashboard.html`, `brand_handoff_dashboard.html`, `content_inventory.html`).
- **Top blockers:** (a) decision-just-made, no implementation; (b) ambiguity on whether the dashboard is the static HTMLs in brand-wizard or a new app; (c) no dedicated CI workflow.

### 4. marketing

- **Authority:** `docs/OLD_CHAT_AND_HOME_PROMOTION_SPEC.md` (13,506 bytes).
- **Reality:** `marketing_deep_research/` has 8 patch YAMLs + a deep research report. `funnel/` directory has **only one funnel built** (`funnel/burnout_reset/` with `app.py`, `emails/`, `stories/`, `templates/`, `data/`). `platform_marketing/` directory does NOT exist (referenced in scope but absent). `somatic_exercise_freebee_apps/` has 42 HTML apps (counted — see freebie).
- **CI:** `marketing_continuous.yml` runs every hour at `:15` on a **self-hosted** runner.
- **Top blockers:** (a) **1 funnel built vs implied 26+ brand funnels**, (b) `platform_marketing/` absent, (c) only 1 integration test file.

### 5. trend_feeds

- **Authority:** `docs/TREND_FEED_INTEGRATION_STRATEGY.md` (17,407 bytes).
- **Config:** complete tier1–4 keywords + 4 locale files (`ja_JP`, `ko_KR`, `zh_CN`, `zh_TW`).
- **CI:** `research_feeds_ingest.yml` cron `0 12 * * 1` (Mondays 12:00 UTC). Last 5 runs all SUCCESS (2026-03-30, 2026-04-06, 2026-04-13, 2026-04-20, 2026-04-27). Output to `artifacts/research/raw/<date>` as artifact upload.
- **Top blockers:** (a) downstream consumer of feeds not yet wired (artifacts persist as workflow artifacts, not into `artifacts/research/` in main); (b) no dedicated unit tests; (c) Qwen3-local consumption pipeline unfinished.

### 6. recommendations

- **Authority:** none — `config/recommender/` has 4 YAMLs (`constraints`, `hard_gates`, `scoring_weights`, `topic_mapping`). No spec doc.
- **Tests:** `tests/test_phoenix_recommender.py` (one file).
- **Status per authority map:** **backlog** — config skeleton only. No CI workflow, no observable output.
- **Top blockers:** (a) no authority doc, (b) no producer, (c) no consumer.

### 7. integrations

- **Authority:** `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` (22,555 bytes; updated 2026-04-19, recent).
- **Coverage:** **23** distinct services documented (counted by `### ` headers): Pearl Star, Together AI, Qwen/DashScope, Anthropic, OpenAI, ElevenLabs, Cloudflare, GitHub, WordPress, GoHighLevel, Plaid, SMTP, GA4, Ollama, Groq, xAI/Grok, video platforms, SerpApi, messaging channels (5 ops channels), GitHub Actions secrets section.
- **HTTP-calling scripts:** ≈9 scripts under `scripts/` use `requests.{get,post}` or `httpx.` — modest surface area, easily auditable.
- **CI:** `llm-callers-audit.yml` + `llm-policy-enforcement.yml` enforce paid-LLM ban from CLAUDE.md.
- **Top blockers:** (a) registry-vs-code drift not auto-checked beyond LLM ban, (b) per-integration smoke tests sparse, (c) `check_integration_env.py` exits 1 only when Qwen unset — could expand "required" set.

### 8. pearl_devops

- **Authority:** `CLAUDE.md`, `docs/GITHUB_OPERATIONS_FRAMEWORK.md`, `docs/GITHUB_GOVERNANCE.md`, `docs/BRANCH_PROTECTION_REQUIREMENTS.md` — all present.
- **Workflows:** **78** in `.github/workflows/` (counted). Governance ones include `pr-governance-review.yml`, `github-governance-check.yml`, `branch-hygiene-sweep.yml`, `change-impact.yml`, `production-alerts.yml`, `production-observability.yml`, `cleanup-stale-worktrees.yml`, `llm-callers-audit.yml`, `llm-policy-enforcement.yml`, `no-binary-blobs.yml`, `release-gates.yml`.
- **Branch protection:** active via Ruleset id 13451138 (5 rules) — see P0 section above.
- **Top blockers:** (a) docs reference legacy branch-protection API but reality is rulesets-based — confusing for new agents; (b) 2 of 5 recent pearl-news daily runs failed (governance does not block them, but observability matters); (c) 78 workflows is large — workflow-pruning audit would be useful but out of scope.

### 9. freebie

- **Authority:** `specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md` (18,409 bytes / 239 lines).
- **Built:** **42** standalone HTML breathwork apps in `somatic_exercise_freebee_apps/` (478 breathing, box, coherence, three-part, tonglen, breath-of-fire, buteyko, cyclic-hyperventilation, cyclic-sighing, HRV-coherence, holotropic, kapalabhati, laughing-buddha, monster, moon, wim-hof, etc.). Deployed via `pages.yml` to root GitHub Pages site (`/breathwork/`).
- **PR #801 (JP LINE freebie):** **OPEN, plan-only** — +2,884 / -0. 8 files: 1 plan doc (624 lines), 4 YAMLs (funnel state machine, OA registry, JP microcopy, rich-menu), 2 research docs (52 + ? citations), 1 LINE_HANDOFF.md. Cost-recommended floor ¥180k/month for 12 OAs at Standard tier. NO LINE OA / Ads / Pay accounts created. NO webhook code.
- **Tests:** zero `tests/*freebie*` or `*somatic*` test files.
- **Top blockers:** (a) PR #801 is paper-only, awaiting operator decision on 12-OA vs 3-hub fallback; (b) zero engineering done (webhook receiver, LIFF endpoint, APScheduler extension all "separate PRs"); (c) brand-name discrepancies (`body_memory`, `solar_return`, `devotion_path`) noted in PR #801 description for separate cleanup.

### 10. storefront_distribution

- **Spec status:** **NO authority doc**. The audit prompt assumed near-zero — that is partially wrong. See gap section below.
- **What exists:**
  - `scripts/publish/kdp_comics_upload.py` — KDP package builder (per-book PDF interior, EPUB, cover, metadata.json, upload_checklist.md, ai_disclosure.txt). Explicitly notes: "Amazon KDP requires manual upload via the KDP Dashboard web UI — there is no public KDP upload API."
  - `scripts/publish/webtoon_canvas_upload.py` — WEBTOON Canvas package builder (vertical-scroll PNGs 800px, episode_metadata.json, ai_disclosure.txt). Notes: "WEBTOON Canvas requires manual upload via the WEBTOON creator dashboard — there is no public upload API."
  - `scripts/publish/_policy_loader.py` — references `config/publishing/ai_policy_blockers.yaml` (BLOCKED-status gating per platform).
  - `scripts/release/build_epub.py`, `build_manga_webtoon.py`, `export_brand_admin_data.py`, `export_wave.py`.
  - `scripts/distribution/pre_export_check.py`, `distribute_to_brand_admins.py`.
  - `scripts/ci/PREPUBLISH_CHECKLIST.md` (referenced).
- **What is missing:** no Apple Books / iBooks workflow, no LINE Manga path, no ISBN registry integration, no automated upload, no live submission record, no dedicated CI workflow, no spec doc tying these scripts together.

---

## Storefront distribution gap — Phase 1 sketch

The audit assumed "almost certainly nothing exists." Correction: **package-builder layer exists for KDP + WEBTOON Canvas**, but it is intentionally manual-upload because neither Amazon KDP nor WEBTOON Canvas exposes a public submission API. Apple Books / LINE Manga have **zero coverage**.

A Phase 1 storefront pipeline spec (out of scope to author here, but the gap shape):

1. **Authority doc** — `specs/PHOENIX_STOREFRONT_DISTRIBUTION_SPEC.md` covering: (a) which storefronts (KDP, Apple Books, WEBTOON Canvas, LINE Manga, Kobo Writing Life, Google Play Books); (b) per-storefront submission posture (API vs scripted-browser vs human-paste); (c) ISBN policy (KDP-issued vs Bowker-purchased vs platform-issued).
2. **EPUB validation gate** — `scripts/publish/epub_validate.py` wrapping `epubcheck` (Java) into CI. Block any storefront package whose EPUB fails epubcheck.
3. **KDP automation** — either `kdspy`-style browser automation (legally murky, ToS risk) **or** keep the manual-paste posture and add a submission-tracking state machine (`artifacts/storefront/submissions/<book_id>/state.json`).
4. **Apple Books** — `iTMSTransporter` CLI is the only sanctioned path; requires Apple iTunes Connect publisher account + sandbox manifest. Add `scripts/publish/apple_books_transporter.py` wrapping iTMSTransporter.
5. **LINE Manga / WEBTOON Canvas** — both manual-upload only; extend the existing package-builder to LINE Manga vertical-scroll format.
6. **ISBN registry** — `config/publishing/isbn_registry.yaml` mapping book_id → ISBN-13 (KDP-issued vs purchased) + barcode generation.
7. **Submission state machine** — table tracking per-platform submission status (DRAFT → SUBMITTED → IN_REVIEW → LIVE → REJECTED), feeding a dashboard panel.
8. **CI workflow** — `storefront-package-build.yml` triggered on book/series readiness; uploads packages as build artifacts; manual operator step to submit.
9. **AI disclosure compliance** — `config/publishing/ai_policy_blockers.yaml` already exists; expand per-platform disclosure templates.
10. **Sales-back ingestion** — KDP Reports API exists; pull weekly sales into `artifacts/storefront/sales/<week>/...` for marketing/recommendations consumers.

**Estimated effort to Phase 1 minimum-viable:** authority doc (1 day) + EPUB validate gate (1 day) + Apple Books transporter wrapper (3 days) + ISBN registry + submission state machine (2 days) + CI wiring (1 day) = ~8 engineering days on top of the existing package-builder scaffolding.

---

## Cluster rollup

- **Operating subsystems (≥70% complete):** pearl_news (75%), trend_feeds (70%), integrations (80%), pearl_devops (85%).
- **Shipping but content-light (~50%):** brand_admin (55%).
- **Early phase (<40%):** dashboard (30%), marketing (20%), recommendations (15%), freebie (35%), storefront_distribution (15%).
- **Cluster average:** ~48%. Half the cluster has live infrastructure; the other half is spec-and-config without producers.
- **Strongest evidence of operating reality:** pearl_news (81 logged WordPress posts, daily cron, 10+ tests), trend_feeds (5/5 weekly runs green), pearl_devops (78 workflows, ruleset enforcing), integrations (23 services documented, recent update).
- **Weakest:** recommendations (no spec, no producer), storefront_distribution (no spec, only package-builders), dashboard (a markdown index file).

## Top 3 cross-subsystem risks

1. **Decision-to-implementation lag.** DASH-02 (dashboard owner) was ratified 2026-04-27 — only 2 days before this audit. PR #801 (freebie JP) is plan-only, opened today. PR #393 (pearl_news first WP cycle) has been OPEN since 2026-04-12. Ratified decisions are accumulating faster than they ship.
2. **Manual-step single-points-of-failure for revenue surfaces.** Storefront distribution is by-design manual-paste. Freebie JP funnel is by-design 12-OA at ¥180k/month. Both gate revenue but require operator action no agent can complete unattended. There is no dashboard tracking "submitted vs live vs rejected" per book per storefront.
3. **Test coverage cliffs in revenue-adjacent code.** Marketing has 1 integration test; freebie has 0; recommendations has 1; storefront has 0. Pearl_news (which IS shipping) has 10+. The cluster's revenue-producing subsystems are the least tested.
