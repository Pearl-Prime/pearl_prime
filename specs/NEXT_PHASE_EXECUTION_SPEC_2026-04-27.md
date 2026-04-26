# Next-Phase Execution Spec — 2026-04-27

**Authority**: synthesis of (a) the audit + 27-PR session (PR #691-#727); (b) operator's prior-session shares 2026-04-27 covering Pearl_Int env check, Pearl News article shape, manga dashboard PR #525/#569, translation/DashScope blocker, pamela_fellows website query, SQLite indexer; (c) the 5 explicit gaps from `docs/FULL_REPO_IMPLEMENTATION_GAP_PLAN_2026-04-26.md` not yet executed.

**Operator status approved 2026-04-27**: catalog regen Path A (per-brand × per-genre %); rebrand mecha to canonical brand; Pearl Star ComfyUI render pipeline live.

---

## 1. Verified state (current PR queue)

| PR | What | State | Risk |
|---|---|---|---|
| #722 | Pearl_Brand Path X — 37 manga canon list + book/manga split + DASH-02 fold-in | OPEN | low |
| #724 | `build_pre_render_script_preview.py` — pre-render editorial HTML | ✅ MERGED earlier | n/a |
| #725 | `queue_panel_renders.py` + Pearl Star runbook + `_meta`-strip fix | OPEN | low |
| #726 | mecha → warrior_calm_cultivation rebrand | OPEN | low |
| #727 | **Catalog regen** spec-compliant per-brand × per-genre % (24,730-file diff; mass-delete pre-approved) | OPEN | **high — load-bearing** |

## 2. Verified Pearl Star + integration state

- Pearl Star ComfyUI **reachable** at `pearlstar.tail7fd910.ts.net:8188` (RTX 5070 Ti, 16 GB VRAM, FLUX-schnell-fp8 loaded, Tailscale up)
- Operator's session's GEMMA_BASE_URL fix landed in `scripts/ci/load_integration_env_from_keychain.py` (synthesizes from QWEN_BASE_URL when Gemma uses same Ollama)
- 33/78 env vars set; 1 required (GEMMA_BASE_URL) was missing pre-fix; now resolved via the Keychain loader fix
- Translation pipeline blocked on DashScope account standing (PR #537 merged the tooling; account billing prevents batch runs)

## 3. Verified existing work referenced by operator

| Source | What | Status |
|---|---|---|
| PR #525 | `scripts/catalog_visibility/extract_manga_series_index.py` + `build_dashboard.py` + Brand 1 US English manga dashboard at `artifacts/catalog_visibility/brand1_us_eng_manga_dashboard.html` + RunComfy character image generator | ✅ landed |
| PR #569 | `manga_asset_estimator.py` + `build_manga_catalog.py` (CSV per market) + `exec_catalog_dashboard.html` Run Full Pipeline panel | ✅ landed |
| PR #537 | Translation pipeline (DashScope-only, --dashscope-only flag, budget cap, checkpoint/log) | ✅ landed; runs blocked on DashScope account |
| Pearl News pipeline | `pearl_news.pipeline.run_article_pipeline` + `scripts/pearl_news/run_daily_news_cycle.py` + `scripts/pearl_news/qa_local_article.py --publish` + `docs/PEARL_NEWS_CONTRACT.md` invariants | ✅ live (pearlnewsuna.org/) |
| Pearl_Int integration | `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` canonical env list + `scripts/ci/check_integration_env.py` validator + `scripts/integrations/setup_all_local_integrations.sh` | ✅ live |

## 4. Five explicit gaps still NOT executed (from FULL_REPO_IMPLEMENTATION_GAP_PLAN_2026-04-26.md)

| # | Gap | Owner | Effort |
|---|-----|-------|--------|
| G1 | `docs/PIPELINE_DASHBOARD_INDEX.md` — single-page dashboard linking everything (spec PR 6) | Pearl_Architect | 1-2h |
| G2 | Brand Wizard YAML → catalog +5% weight wire-up | Pearl_Brand + Pearl_Dev | 3-5h |
| G3 | Teacher pages render teacher videos (GAP-T1 video binding) | Pearl_Video + Pearl_Dev | 4-6h |
| G4 | **Pearl News teacher truth from Pearl Prime resolver** | Pearl_News + Pearl_Prime | 3-5h |
| G5 | Marketing lower-average conversion-rate updates + `marketing_assumptions.yaml` | Pearl_Marketing | 1-2h |

**Note on G4 specifically** (from operator's Pearl_Int share): Pearl News article schema currently embeds teacher attribution but the `teacher_id: junko` slot in the QA preview pulls from a pearl_news-local guess. Per `docs/PEARL_NEWS_WRITER_SPEC.md`, the truth source should be Pearl Prime's `config/teachers/teacher_registry.yaml` + `teacher_background.yaml`. This wiring doesn't exist as a resolver script yet.

**Note on G3** (from operator's pamela_fellows query): teachers exist in `config/teachers/teacher_registry.yaml` with display name + topics + lane but **no website URL field** and no video binding. Adding both is a pre-req for the teacher page work.

## 5. Three NEW items surfaced by operator's pasted content

| # | Item | Source | Effort |
|---|------|--------|--------|
| N1 | **Brand 1 US English manga marketing-data backfill** — operator's PR #525 Phase 0 found Brand 1 manga profiles missing `series_title`, `series_logline`, `marketing_angle`, `hook_lines`, `launch_priority`, `main_character_name/role/image_path` (all null). Author these fields per series in YAML | Pearl_Brand + Pearl_Editor | 2-3h |
| N2 | **SQLite atom indexer + coverage report** — operator's session was implementing `scripts/build_atom_index.py` (sqlite-utils) + `scripts/coverage_report.py` + CI shell gate; depth-bounded scan with skip-list. Status: in-progress, not yet PR'd | Pearl_Dev | 4-6h to land |
| N3 | **Add `RUNCOMFY_TOKEN` alias to `integration_env_registry.py`** for Keychain parity with the task brief naming. Tiny follow-up. | Pearl_Int | 15 min |

## 6. Recommended execution order

**Wave 1 — clear the in-flight PR queue (today)**
1. Operator review + merge PR #722 (Pearl_Brand Path X) — low risk
2. Operator review + merge PR #725 (Pearl Star runbook) — low risk; already has its `_meta` fix
3. Operator review + merge PR #726 (mecha rebrand) — low risk; cosmetic YAML diff
4. **Operator final review + merge PR #727 (catalog regen, 24,730 files)** — high risk, biggest impact; mass-delete pre-approved

**Wave 2 — quick-win in-session gap fills (~4-6h total)**
5. G1 dashboard index (1-2h, Pearl_Architect, single doc PR)
6. G5 marketing assumptions (1-2h, Pearl_Marketing, small config + presentation patches)
7. N3 RUNCOMFY_TOKEN alias (15 min, trivial)

**Wave 3 — substantive gap execution (~12-20h total; spawned subagents in sequence)**
8. G4 Pearl News teacher truth resolver (3-5h, focused Pearl_News session — most operator-visible improvement)
9. G2 Brand Wizard YAML → catalog +5% wire-up (3-5h, Pearl_Brand + Pearl_Dev)
10. G3 Teacher video binding + page render (4-6h, Pearl_Video + Pearl_Dev)
11. N1 Brand 1 manga marketing backfill (2-3h, Pearl_Brand + Pearl_Editor)

**Wave 4 — long-tail (deferred unless operator pushes)**
12. N2 SQLite indexer completion (4-6h)
13. DashScope account fix → re-run blocked translation batches (operator-side billing)
14. Audiobook ja_JP rollout (operator-side platform credentials)
15. Marketing buildout multi-week (operator-side platform credentials + priority)
16. Podcast 12-16d execution (`docs/PODCAST_PIPELINE_INTEGRATION_SPEC.md`)

## 7. Hard rules

- All gap subagents MUST push PRs but NOT merge — operator review before merge
- All deletions still require operator pre-approval per CLAUDE.md mass-delete rule
- Tier 1 LLM only (no banned paid APIs)
- `pr_governance_review.py` BLOCKED status is a STOP (except for pre-approved mass-delete)
- Workers Builds: pearl-prime is the only orthogonal CI failure (mergeable with `--admin`)

## 8. Definition of done for this next phase

- ✅ All 4 in-flight PRs (#722, #725, #726, #727) merged
- ✅ All 5 gap items (G1-G5) have PRs landed
- ✅ All 3 new items (N1-N3) have PRs landed OR explicit deferral
- ✅ Pearl News article shape matches spec (G4 closes the teacher_id pull from Pearl Prime)
- ✅ One dashboard index links everything (G1)
- ✅ Marketing presentations use lower-average conversion (G5)

## 9. Open operator questions (no decision blocks today's execution but informs sequencing)

| Q | Why it matters |
|---|---|
| Q1 | **DashScope account** — fix billing so translation can resume? Translation tooling is ready; just blocked on account standing |
| Q2 | **Locale extension to es_LA + hu_HU + zh_HK** — operator wants these per "all markets" earlier ask; planner needs new CATALOG_PLAN.md per locale |
| Q3 | **Render mecha (now warrior_calm_cultivation) full 35 panels** — Pearl Star is up; ~30-50 min wall-clock; just operator approval to fire |
| Q4 | **Pearl_Int RUNCOMFY_TOKEN alias** — confirm the env var name preferred (RUNCOMFY_API_KEY today; RUNCOMFY_TOKEN in task briefs); trivial fix either way |

---

This spec is the consolidated execution plan for the next phase. All in-flight PRs and gap items are tracked. Operator can execute Wave 1 (review + merge) at any time; Wave 2-3 spawn-on-demand.
