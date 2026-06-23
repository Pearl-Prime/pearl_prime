# Manga Recovery Audit — Scorched-Earth Branch/Worktree Scan

**AUDIT_DATE:** 2026-06-23  
**AUDITOR:** Pearl_GitHub (Cursor agent session)  
**MAIN_SHA:** `06d588fb904720aa17eebc1ead34159a52b456b9` (`origin/main`)  
**PROGRAM_STATE:** Manga ja_JP = **TITLED** (273 `manga_series_plans/ja_JP` on main)

## Executive Summary

| Metric | Count |
|---|---|
| Total branches scanned (manga/panel/series keywords) | 32 |
| Branches with drift vs `origin/main` | 12 |
| Open manga PRs (do not delete branches) | 8 |
| Salvaged in Gold Master PR (this recovery) | 27 files (8 scripts + 18 distribution + manifest) |
| Render panels on main (`stillness_press` v4 ep_001) | 82 PNG |
| Render panels on branch only (`v31-stillness-en-01-ship`) | 304 JPG (PR #1236) |
| ja_JP series plans on main | 273 |
| en_US series plans on main | 272 |
| Local untracked ep_002 panels (operator clone) | 5 PNG (~7.1 MB) |

**Verdict:** `origin/main` is **not** the production ceiling. Titled catalog (273 ja_JP) is on main, but **PRODUCED** state (scripts, panel renders, distribution) lives on stale branches, open PRs, active worktrees, and untracked operator-clone artifacts.

---

## Worktree Inventory

| Path | Branch / HEAD | SHA | Manga artifacts | Status |
|---|---|---|---|---|
| `/Users/ahjan/phoenix_omega` | `agent/ghl-admin-simple-package-20260623` | `b30e3e813c` | 290M `artifacts/manga/`; ep_002 panels **untracked** | Active operator clone |
| `/Users/ahjan/phoenix_omega/.worktrees/manga-dist` | `agent/manga-distribution-v1` | `a94b4810a7` | 191M manga artifacts; **18-file distribution pipeline** ahead of main | **Salvaged → Gold Master** |
| `/private/tmp/ws-runtime-fix` | `agent/waystream-epub-runtime-fix-clean` | `91d4fd9d2b` | 191M (mirror of main-era manga tree) | No unique drift |
| `/Users/ahjan/.cursor/phoenix_canary_wt` | detached | `4aa14983d8` | 652K manga | Stale canary; no unique production |
| `/Users/ahjan/wt-drain` | `agent/pearl-architect-amendment-locale-parallel-relax-20260611` | `b4b33caf74` | — | **LOCKED — do not prune** |
| `/Users/ahjan/pp_doctrine_wt` | `agent/pearl-prime-doctrine-intro-stitch-20260611` | `0cdbaf5ab5` | — | Active worktree |
| `.claude/worktrees/` | — | — | 8 KB (empty) | Already cleared |

---

## Branch Drift Matrix (manga-keyword branches vs `origin/main`)

| Branch | SHA | Diff files | Renders | ja_JP plans | Category | Action |
|---|---|---|---|---|---|---|
| `agent/v31-stillness-en-01-ship` | `d282e921dcd9` | 317 | 304 JPG | 0 | **PRODUCED** (composed v3 Qwen, 10 eps) | Open PR **#1236** — merge path |
| `agent/series-1-image-side-render-20260518` | `087c1d853c7f` | 0 | — | — | Absorbed into main | Close PR **#1195** after verify |
| `agent/series-1-ep-003-to-010-scripts-20260518` | `3436e38f3708` | 16 | 0 | 0 | **SCRIPTS** (ep_003–010 YAML) | Open PR **#1189** |
| `agent/manga-distribution-v1` | `a94b4810a7` | 18 | 0 | 0 | **PIPELINE** (EPUB3/PDF/CBZ/webtoon) | **Salvaged → Gold Master** |
| `agent/manga-story-wave1-20260620` | `7628bd76d56d` | 9 | 0 | 0 | **SCRIPTS** (8 wave1 ep_001 pilots) | **Salvaged → Gold Master** |
| `agent/manga-en_US-titles-20260620` | `e14e5de313dd` | 274 | 0 | 0 | TITLED (en_US title refresh) | Local-only; push + PR |
| `agent/manga-ko_KR-titles-20260620` | `00aa73883c1b` | 271 | 0 | 0 | TITLED (ko_KR titles) | Local-only; push + PR |
| `agent/manga-zh_CN-titles-20260620` | `5ac48dcec0ac` | 275 | 0 | 0 | TITLED (zh_CN titles) | Local-only; push + PR |
| `agent/manga-ja_JP-mecha-titles-20260620` | `466ac2dd7982` | 3 | 0 | 3 | TITLED (mecha ja_JP fixes) | Local-only; push + PR |
| `agent/manga-v2-phase-a-character-designs-20260612` | `6c4699576df9` | 15 | 0 | 0 | CONFIG (character design blocks) | Review + PR |
| `agent/devotion-manga-webtoon-ep001-20260618` | `3b1b6fa22688` | 12 | 1 | 0 | PRODUCED (devotion webtoon ep001) | Local-only; push + PR |
| `agent/devotion-manga-gpu-real-flux-render-20260618` | `7014622188f4` | 5 | 1 | 0 | PRODUCED (GPU flux render) | Local-only; push + PR |
| `agent/manga-renderer-retire-workaround-20260618` | `2fae08940378` | 9 | 1 | 0 | PIPELINE (retire workaround) | Local-only; push + PR |
| `agent/v51-2stage-architecture` | `d03c64c01b35` | 2 | 0 | 0 | SPEC (V5.1 2-stage arch) | Open PR **#1276** |
| `agent/japan-manga-only-amendment-q1-q4-20260511` | `63d5a5901cf2` | — | — | — | ARCH (Japan Q1–Q4) | Open PR **#1034** |
| `agent/en-zh-manga-sku-map-ssot-reconcile-20260620` | `42ff08611214` | 5 | 0 | 0 | STOREFRONT SKU map | Open PR **#1778** |
| `agent/manga-doc-accuracy-banners-20260529` | `9fd9a957b60a` | — | — | — | DOCS | Open PR **#1385** |
| `agent/manga-workflow-env-override-20260606` | `9414a5b59ccf` | 0 | — | — | Merged into main | **Deleted** (hygiene) |

### Critical recovery branch (historical)

`agent/manga-sdf-revision-workspace` — pen-name/author recovery (ACTIVE_WORKSTREAMS `ws_pen_name_recovery_20260328`, **completed**). No remaining manga production drift; author configs landed on main.

---

## Production State on `origin/main` (baseline)

| Asset class | Path pattern | Count on main |
|---|---|---|
| ja_JP series plans | `config/source_of_truth/manga_series_plans/ja_JP/` | 273 |
| en_US series plans | `config/source_of_truth/manga_series_plans/en_US/` | 272 |
| Chapter scripts | `artifacts/manga/chapter_scripts/` | 2 eps (`stillness_press` ep_001–002) |
| Panel prompts | `artifacts/manga/panel_prompts/` | 2 eps |
| Composed renders (v4) | `artifacts/manga/stillness_press__ahjan__/composed_v4_qwen/ep_001/` | 82 PNG |
| Manga pilot scripts | `artifacts/manga/pilots/wave1/` | **0** (salvaged in Gold Master) |

---

## Untracked Operator-Clone Artifacts (not on any branch)

| Path | Files | Notes |
|---|---|---|
| `artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/panels/` | 5 PNG | ep_002 render in progress (watchdog PID files in `artifacts/qa/`) |
| `artifacts/qa/ep_002_*` | logs + PIDs | Active render session 2026-06-23 |

**Action:** Commit ep_002 panels to ship branch after render completes; do not lose before hygiene pass.

---

## Open PRs — Do Not Delete Branches

| PR | Branch | Production content |
|---|---|---|
| #1236 | `agent/v31-stillness-en-01-ship` | 304 composed segments, 10 episodes |
| #1195 | `agent/series-1-image-side-render-20260518` | 304 panels (verify absorbed) |
| #1189 | `agent/series-1-ep-003-to-010-scripts-20260518` | ep_003–010 chapter scripts |
| #1276 | `agent/v51-2stage-architecture` | V5.1 architecture spec |
| #1034 | `agent/japan-manga-only-amendment-q1-q4-20260511` | Japan Q1–Q4 ratification |
| #1778 | `agent/en-zh-manga-sku-map-ssot-reconcile-20260620` | Storefront SKU reconcile |
| #1385 | `agent/manga-doc-accuracy-banners-20260529` | Image-bank coverage docs |

---

## Gap Analysis: TITLED → PRODUCED

| Stage | ja_JP (273 series) | en_US pilot (`stillness_press`) |
|---|---|---|
| TITLED (series plan YAML) | 273 / 273 (100%) | 1 / 272 (0.4%) |
| SCRIPTED (chapter_script) | ~0% catalog-wide | 2 / 10 eps (20%) |
| PANEL_PROMPTS | ~0% | 2 / 10 eps (20%) |
| RENDERED | ~0% | ep_001 v4: 82 panels; ep_002 in progress |
| COMPOSED / LETTERED | ~0% | v3 ship on PR #1236 only (304 segs) |
| DISTRIBUTED (EPUB/CBZ) | 0% | Pipeline on Gold Master PR |

---

## NEXT_ACTION (bridge to 100% production)

1. **Merge Gold Master PR** — wave1 scripts + distribution pipeline land on main.
2. **Merge PR #1236** — 304 composed v3 segments become canonical render reference.
3. **Finish ep_002 render** — commit untracked `panels/` + `composed_v4_qwen/ep_002/` to ship branch.
4. **Fan-out wave1 scripts** — use `artifacts/manga/pilots/wave1/` as gold-reference for 8 genre×mode pilots.
5. **Locale title PRs** — push `manga-en_US/ko_KR/zh_CN-titles` branches (274 files each).
6. **Queue-first renders** — all panel work via `pscli enqueue` per RAP (`docs/ROBUST_AGENT_PROTOCOL.md`).
7. **Weekly rollout** — `scripts/weekly_manga_rollout.py --dry-run` then Pearl Star self-hosted lane.

---

*Machine-readable manifest: `artifacts/coordination/MANGA_GOLD_MASTER_MANIFEST.tsv`*
