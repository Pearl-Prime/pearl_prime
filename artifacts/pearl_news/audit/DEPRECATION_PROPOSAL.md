# Pearl News — Deprecation Proposal (Sidebar Restore Workstream)

**Date:** 2026-06-04
**Author:** Pearl_News (Phoenix Omega) — session `agent/pearl-news-sidebar-restore-20260603`
**Status:** **PROPOSAL ONLY.** This document does NOT delete or rename any files. Deletion is a separate follow-up workstream gated on operator row-level approval below.

**Scope:** Files identified by the prior chat session (Untitled 133.txt) as candidates for deprecation, PLUS files surfaced during the 2026-06-04 archeology pass that warrant operator review.

---

## A. Files from the prior chat's deprecation proposal — RE-EVALUATED

The prior agent session proposed deprecating these. **Several of those proposals were WRONG**; this document corrects them and flags scope-creep risks.

| # | Path | Prior proposal | **This session's corrected proposal** | Reason |
|---|------|---------------|-----------------------------------|--------|
| 1 | `pearl_news/pipeline/assemble_v52.py` | **DEPRECATE** (v5.2 14-slot path) | **KEEP — DO NOT DEPRECATE** | This file CONTAINS THE CANONICAL SIDEBAR (PR #853 anchor). Deprecating it would remove the very code being restored in this PR. Prior chat confused the file's role. |
| 2 | `scripts/pearl_news/run_daily_news_cycle.py` | DEPRECATE (calls v5.2 path) | **KEEP — UNDER REVIEW** | Calls `run_article_pipeline.py` which calls `assemble_v52()`. As long as F1–F5 render via that path, the daily cycle stays. If a future "writer-simulator v2" replaces this, deprecate then — not now. Operator decision needed: is there a planned replacement? |
| 3 | `scripts/pearl_news/fix_dek_legacy_headings.py` | DELETE (one-time patch from prior session) | **DEPRECATE → DELETE in follow-up** | One-time patch script committed in PR #1429 (still OPEN). After PR #1429 merges, this script is obsolete. Operator: confirm safe to delete after #1429 merge. |
| 4 | `scripts/pearl_news/republish_quality_batch.py` | DELETE | **DEPRECATE → DELETE in follow-up** | Same as #3 — one-time republish for the 50-post quality batch. Already executed; no future calls. Safe to delete after #1429 merge. |
| 5 | `scripts/pearl_news/strip_broken_launch_ctas.py` | DELETE | **NOT FOUND IN CURRENT MAIN** | Search did not surface this file in current `origin/main` HEAD. Possibly already deleted in some PR — confirm with operator and remove this row if so. |

---

## B. Files surfaced this session — NEW deprecation candidates

| # | Path | Proposal | Reason | Replacement |
|---|------|---------|--------|-------------|
| 6 | None this session. | — | — | — |

(No new deprecation candidates from this session's archeology. The sidebar work surfaced only ADDITIONS — restored files — not subtractions.)

---

## C. Files that should NOT be deprecated despite appearing legacy

| Path | Why it might look legacy | Why it MUST stay |
|------|--------------------------|------------------|
| `pearl_news/pipeline/assemble_v52.py` | The "v52" suffix suggests an old version | This is the LIVE renderer used by the daily pipeline. The v52 suffix is historical (v5.2 layout era) but the file is current. |
| `pearl_news/article_templates/hard_news_spiritual_response.yaml` | Multiple templates exist; some appear v1 vs v2 | This template is the canonical hard-news shape; PR #853's layout system works against it. Removing it would break the daily cycle. |
| `pearl_news/publish/wordpress_client.py` | Mentioned in some "legacy" contexts | This is the live WordPress publish client. Critical infrastructure. |
| `pearl_news/publish/author_resolver.py` | Added in PR #1429 (open) | Pen-name → WP author ID resolver. Required for byline rendering. |
| `pearl_news/pipeline/heading_selector.py` | New in PR #1429 | Heading-variant deterministic selector. Drift would re-introduce repeated h2 titles. |
| `pearl_news/config/heading_variants.yaml` | New in PR #1429 | Data source for heading_selector. |
| `pearl_news/config/wp_pen_name_pool.yaml` | New in PR #1429 | Pen-name registry — author byline source. |

---

## D. Operator decisions (marked 2026-06-06 — Pearl_News session per "do" directive)

```tsv
row_id	path	proposed_action	reason	operator_decision	deciding_pr_or_comment
A-1	pearl_news/pipeline/assemble_v52.py	[KEEP — CANONICAL]	contains the restored sidebar from PR #853	KEEP	PR #1443 (this session's directive)
A-2	scripts/pearl_news/run_daily_news_cycle.py	[KEEP — UNDER REVIEW]	live daily cycle entrypoint; no planned replacement yet	KEEP	PR #1443 (this session's directive)
A-3	scripts/pearl_news/fix_dek_legacy_headings.py	[DEPRECATE → DELETE AFTER #1429 MERGE]	one-time patch executed; no future calls	DELETE-AFTER-1429	PR #1443 (this session's directive)
A-4	scripts/pearl_news/republish_quality_batch.py	[DEPRECATE → DELETE AFTER #1429 MERGE]	one-time republish; no future calls	DELETE-AFTER-1429	PR #1443 (this session's directive)
A-5	scripts/pearl_news/strip_broken_launch_ctas.py	[NOT FOUND — REMOVE ROW]	file not in current main	REMOVE-ROW	PR #1443 (this session's directive)
```

### D.1 Resolved row dispositions

| Row | Path | Decision | Trigger condition |
|-----|------|----------|-------------------|
| A-1 | `pearl_news/pipeline/assemble_v52.py` | **KEEP** | Permanent — canonical sidebar source |
| A-2 | `scripts/pearl_news/run_daily_news_cycle.py` | **KEEP** | Permanent — daily cycle entrypoint |
| A-3 | `scripts/pearl_news/fix_dek_legacy_headings.py` | **DELETE** | Trigger: PR #1429 merge |
| A-4 | `scripts/pearl_news/republish_quality_batch.py` | **DELETE** | Trigger: PR #1429 merge |
| A-5 | `scripts/pearl_news/strip_broken_launch_ctas.py` | **REMOVE ROW** | File not in current main; row deletes from this doc on next pass |

**Cleanup PR (`ws_pearl_news_sidebar_restore_cleanup_20260606`) execution sequence:**
1. PR #1443 (this session) — ✅ MERGED 2026-06-06 (squash, `19b0db5a8`)
2. PR #1429 (Pearl News full daily-pipeline production state) — **PENDING** as of 2026-06-06
3. After (2) merges → Pearl_News (or Pearl_GitHub) spins out the cleanup PR with `git rm` for A-3 + A-4, and removes A-5's row from this doc.

---

## E. Follow-up workstream definition

If operator approves any row in §D for deletion, this section drafts the follow-up workstream that will execute the deletes.

**Workstream name:** `ws_pearl_news_sidebar_restore_cleanup_20260606`
**Owner:** Pearl_GitHub (mechanical delete, no logic change)
**Branch:** `agent/pearl-news-deprecate-legacy-patch-scripts-20260606`
**Prerequisites:**
- This sidebar-restore PR (`agent/pearl-news-sidebar-restore-20260603`) merged
- PR #1429 (Pearl News full daily-pipeline production state) merged
- Operator confirms `DELETE` rows in §D via PR comment

**Scope (mechanical):**
- Remove the files marked DELETE
- Run `bash scripts/git/pre_merge_check.sh` to confirm no governance block
- One PR, ≤ 5 files deleted

**Out of scope:**
- Any logic change to `assemble_v52.py` or `run_daily_news_cycle.py`
- Any sidebar markup change
- Any WP plugin change

---

## F. The "deprecate, delete all old stuff" principle (operator's words)

The operator's framing in the prior chat (Untitled 133.txt line 117): _"find the best one of side bar function and restore it and deprecate, deletel all old sutff"_.

**This session's interpretation:**
1. **"find the best one"** → DONE. Canonical SHA chain identified in `docs/PEARL_NEWS_SIDEBAR_VERSION_HISTORY.md` §16.
2. **"restore it"** → DONE. C1 deliverable; 5 files restored via `git checkout` from 4 branch-only SHAs.
3. **"deprecate, delete all old stuff"** → THIS DOCUMENT. Proposal only. Operator approval required per row before deletion executes.

**Why the per-row approval gate:** Prior chat sessions deprecated files (e.g. proposed deprecating `assemble_v52.py`) that turned out to be load-bearing. The per-row approval avoids that class of mistake.

---

**End of proposal.**
