# Full Repo Audit Baseline — 2026-04-26

**Branch:** `agent/full-repo-reconciliation-20260426`
**Baseline SHA:** `1f4f8a28fc0e09163b4a88653074114c337ca1ea` (origin/main HEAD at session start)
**Session date:** 2026-04-26
**Audit owner:** Pearl_Architect (lead) + Pearl_PM (coordination)
**Companion CSVs (this PR):**
- `full_repo_file_inventory_2026-04-26.csv.gz` — 42,257 rows (one per tracked file); `gunzip` to read (gzipped to satisfy `.github/workflows/no-binary-blobs.yml` 1 MB-per-file size policy: raw 6.9 MB → 426 KB)
- `full_repo_git_history_index_2026-04-26.csv` — 2,006 commits + 11 PRs (333 KB; under threshold, kept as plain CSV)
- `full_repo_doc_status_matrix_2026-04-26.csv.gz` — 19,879 rows (one per doc-like file); `gunzip` to read (raw 3.2 MB → 122 KB)
- `full_repo_pipeline_matrix_2026-04-26.csv` — 1,053 rows (27 pipelines + 760 modules + 238 orphans + 28 reqs) (120 KB; under threshold, kept as plain CSV)

---

## Why this audit exists

PR #680 (manga pipeline audit, merged 2026-04-26 00:43 UTC) used narrow filename patterns
like `docs/MANGA_*.md` and **missed five load-bearing strategic docs**:

- `artifacts/manga/MANGA_FULL_CATALOG_PLAN.md` (303 lines) — outside `docs/`
- `docs/GENRE_PORTFOLIO_PLAN.md` (563 lines) — different prefix
- `docs/CJK_CATALOG_PLAN.md` (300 lines) — CJK, not MANGA
- `docs/US_CATALOG_PLAN.md` (279 lines) — US, not MANGA
- `docs/MANGA_MODE_STRATEGY.docx` → `.md` — wrong extension

Subsequent reconciliation (PR #682 catalog reconciliation spec, PR #684 docx→md migration,
PR #685 coordination backfill, PR #686 audiobook docs rename) confirmed the miss and
demanded a permanent fix.

This audit **bans the narrow-pattern-search failure mode**: every classifier here uses
full-tree enumeration (`git ls-files`, `git log --all`, full subsystem grep matrices)
instead of filename prefix shortcuts.

## Verification: strategic-miss test PASSED

All 5 PR #680 misses are present in `full_repo_doc_status_matrix_2026-04-26.csv`,
classified `canonical` under `manga_pipeline` subsystem.

---

## Open PRs at session start (32)

Recent activity-heavy: ep_002 manga ship, Pearl Prime move 5, Pearl News v5.4.

| # | Title | Author | Created | Branch |
|---|---|---|---|---|
| 683 | docs(pearl_prime): coverage + gap analysis 2026-04-26 | Ahjan108 | 2026-04-26 03:42 | agent/pearl-prime-coverage-gap-analysis-20260426 |
| 679 | docs: AGENTS.md — cross-vendor coding-assistant brief | Ahjan108 | 2026-04-26 00:33 | agent/agents-md-coding-assistant-brief-20260426 |
| 678 | fix(manga): lettering_from_script v3-schema awareness | Ahjan108 | 2026-04-25 21:47 | agent/lettering-v3-schema-fix-20260426 |
| 623 | feat(pearl-prime): first real book assembled + LoRA VRAM blocker | Ahjan108 | 2026-04-24 19:06 | agent/first-book-pilot-20260425 |
| 610 | feat(manga): protagonist LoRA specs + character image pipeline | Ahjan108 | 2026-04-24 04:26 | agent/protagonist-lora-pipeline-20260424 |
| 606 | fix(manga): phase 1 — rebuild FLUX prompts as manga art direction | Ahjan108 | 2026-04-24 03:38 | agent/flux-prompt-fix-20260424 |
| 592 | feat(pearl-news + manga): v5.4 sidebar + 13 US manga lead-picks | Ahjan108 | 2026-04-23 13:36 | claude/pensive-hodgkin-3511bd |
| 589 | fix(tests): align injection_resolver tests with current API | Ahjan108 | 2026-04-23 06:31 | claude/frosty-noyce-ea448a |
| 587 | fix(pearl_news): wire deterministic teacher slots into v52 render | Ahjan108 | 2026-04-23 02:22 | agent/fix-pearl-news-deterministic-slots |
| 581 | fix(dashboard): swap card/drawer prominence for series_description | Ahjan108 | 2026-04-22 22:26 | agent/dashboard-card-logline-swap |

(22 more open PRs — see `full_repo_git_history_index_2026-04-26.csv` `state=OPEN` rows)

## Recent merged PRs (precedent for canonical decisions)

| # | Title | Merged | SHA |
|---|---|---|---|
| 686 | docs(audiobook): rename 2 audiobook docs to AUDIOBOOK_ prefix (OQ-9 a) | 2026-04-26 04:30 | 1f4f8a28fc0e09163b4a88653074114c337ca1ea |
| 685 | coord(manga): backfill catalog reconciliation rows (OQ-8 iii) | 2026-04-26 04:23 | 8a8578ba0d414709fa42744887069307da5f6a64 |
| 684 | docs(manga): migrate MANGA_MODE_STRATEGY docx → md (OQ-7) | 2026-04-26 04:00 | 8aaa46aafd81046fe9c5b1702f803e2bbab61c6e |
| 682 | spec(manga): catalog reconciliation — 12-shell × 37-brand | 2026-04-26 01:44 | 7d93ae6c3d0db20178fa07ea3052826efabb591f |
| 680 | docs(manga): Phase 1 pipeline audit deliverable | 2026-04-26 00:43 | 684acbc15ba2d9d8024acd61f09b556b50a8f31a |
| 677 | feat(story-atoms): working_parents anxiety overwhelm — 16 atoms | 2026-04-25 21:03 | 0795235689f1a20daa569fbbfcdd1f9fe192c09a |
| 676 | feat(qa): Move 4 representative sweep — 27/30 (90%) bestseller-grade | 2026-04-25 21:03 | 224cf0cc1d4efb56cc9aeaa31bc77cfbfd5fdb60 |
| 670 | fix(registry-resolver): engine-bank-first selection (FINAL Pearl Prime piece) | 2026-04-25 18:33 | e3399e358a4f837d614b8674845a4f1ce029bc65 |
| 663 | chore(integrations): track R2 account ID + bucket | 2026-04-25 07:19 | 52f5e69874055dff3e1acc46cdf85282d66c348b |

---

## Headline findings

### Repo scale (full_repo_file_inventory)

| Top-level area | File count | % |
|---|---:|---:|
| atoms | 17,090 | 40.5% |
| brand-wizard-app | 7,872 | 18.6% |
| artifacts | 4,679 | 11.1% |
| config | 3,650 | 8.6% |
| SOURCE_OF_TRUTH | 3,177 | 7.5% |
| template_expand2 | 1,012 | 2.4% |
| image_bank | 841 | 2.0% |
| teachers | 590 | 1.4% |
| pearl_news | 503 | 1.2% |
| scripts | 455 | 1.1% |
| docs | 301 | 0.7% |
| (49 other areas) | 2,087 | 4.9% |

### Git history (full_repo_git_history_index)

- 2,006 commits captured across all branches
- 87% of all commits are from April 2026 (1,755 commits) — recent rapid iteration
- Top authors: Nihala (Ma'at) 1,399 (70%); Ahjan108 576 (29%); github-actions[bot] 29
- Top keyword flags in commit subjects:
  - manga: 164 / catalog: 94 / brand: 108 / teacher: 108
  - audit: 61 / wizard: 43 / pearl_news: 28 / pearl_prime: 16
  - reconciliation: 6 / archive: 3 / superseded: 1

### Doc canonicality (full_repo_doc_status_matrix — 19,879 rows)

- canonical: 154 (0.8%) — load-bearing subsystem authority
- current_support: 307 (1.5%) — research/audits/runbooks
- generated_artifact: 17,573 (88.4%) — atoms + templates + fixtures (low audit signal)
- fixture: 520 (2.6%) — teacher banks + story atoms + image bank
- archived: 158 (0.8%) — under archive/, salvage/, old_chat_specs/
- unknown: 1,148 (5.8%) — real docs not matching fast-path patterns
- README: 4 / superseded: 2 / deletion_candidate: 2

### Pipeline + code (full_repo_pipeline_matrix — 1,053 rows)

**27 pipelines** mapped across 10 subsystems:
- 23 scheduled / 2 live / 1 in_dev / 1 orphaned (dashboard)
- Most recent: Brand Admin weekly (2026-04-26)
- Live: Pearl Prime, Pearl News, Manga, Brand Admin, Video, Translation, TTS

**998 Python modules** — 238 orphans (23.8% — 2-3× higher than healthy ratio):
- phoenix_v4/: 153 orphans (64% of all dead code) — experimental branch left in main
- pearl_news/: 24 orphans
- scripts/: 21 orphans
- pearl_news copy/: 7 orphans (PR #245 accidental restore)
- server/: 7 orphans

**28 business requirements** (no transcript found; inferred from repo state):
- 21 implemented (75%) / 5 partial (18%) / 1 missing (4%) / 1 unknown (4%)
- Top concern (missing): Podcast publishing — research exists, no impl found

---

## Dead-code clusters (high-confidence deletion candidates)

| Cluster | File count | Reason | Subsystem |
|---|---:|---|---|
| `phoenix_v4/` orphan subset | 153 | Imported_by=0, has_main=0; experimental branch leftover | core_pipeline |
| `pearl_news/` orphans | 24 | Old pipeline variants alongside active code | pearl_news |
| `scripts/` orphans | 21 | Utilities not wired to CI/workflows | (mixed) |
| `pearl_news copy/` | 7+ | Duplicate from PR #245 accidental restore | pearl_news |
| `del_files/`, `del_location_plan/`, `del_intake_planner/`, `del_exta_stories/` | 8+ | Deletion artifacts (intentional/forgotten) | (mixed) |
| `files-4/` | 1+ | Duplicate validation module | (mixed) |
| `deli/`, `delf/` | misc | Likely typos or staging artifacts | (mixed) |
| `dashboard/` (no entry point) | 1 pipeline | Never instantiated | dashboard |

Detailed deletion plan in `docs/FULL_REPO_DEPRECATION_AND_DELETION_PLAN_2026-04-26.md` (PR-4).

---

## Open questions surfaced

| OQ | Question | Status |
|---|---|---|
| OQ-A | Does a "28 requirements" transcript exist somewhere not found by the audit? Subagent E searched docs/, specs/, artifacts/, old_chat_specs/, git history with no hit. Reqs were inferred from repo state. | unresolved |
| OQ-B | Are the 153 phoenix_v4/ orphans truly dead, or imported via dynamic loading (importlib, getattr) that simple grep misses? | needs runtime check |
| OQ-C | The `dashboard` subsystem entry in SUBSYSTEM_AUTHORITY_MAP is missing; pipeline_matrix shows no entry point. Is dashboard work canonically owned somewhere? | unresolved |
| OQ-D | PEARL_PM_STATE.md last_verified is 2026-04-10 (16 days stale). 5 active projects exist in ACTIVE_PROJECTS.tsv but only 1 is referenced in PEARL_PM_STATE.md. Pearl_PM bump required. | known stale; tracked elsewhere |
| OQ-E | Some 14-field workstream rows in ACTIVE_WORKSTREAMS.tsv have schema drift per proj_manga_first_ship_20260425 next_action notes. | tracked elsewhere |
| OQ-F | `MANGA_MODE_STRATEGY.docx` and `.md` both exist (PR #684 migrated docx→md but docx wasn't deleted). Should the docx be removed? | tracked under proj_manga_catalog_reconciliation OQ-7 |

## Subagent provenance

All four CSVs were produced by parallel subagent runs on 2026-04-26. The reproducible build scripts will land in PR-2 under `scripts/audit/`. This snapshot is point-in-time at SHA `1f4f8a28fc0e09163b4a88653074114c337ca1ea`.

| Source | Subagent | Wall-clock |
|---|---|---|
| `agent_a_inventory.csv` | A — repo inventory (Explore very thorough) | ~30 min |
| `agent_b_history.csv` + `agent_b_pr_index.csv` | B — git history (Explore very thorough) | ~30 min |
| `agent_c_doc_status_full.csv` | C — doc canonicality, two passes | ~75 min total |
| `agent_d_pipeline_full.csv` + `agent_d_code_modules_full.csv` + `agent_d_orphan_candidates.txt` | D — pipeline + modules, two passes | ~90 min total |
| `agent_e_business_reqs.csv` | E — business reqs (Explore medium) | ~25 min |
