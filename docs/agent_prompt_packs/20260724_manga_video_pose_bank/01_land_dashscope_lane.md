# Lane 01 — Pearl_GitHub — Land the DashScope free-media lane + manga-pilot scope note

EXECUTE. Do not stop at summary, plan, PR-open, or tests-running. The turn ends only on the
signal `dashscope-free-media-landed=<full merge SHA>` or one concrete BLOCKER with evidence and
work pushed.

STARTUP_RECEIPT (SESSION_UNITY format): AGENT=Pearl_GitHub, SUBSYSTEM=pearl_devops+integrations,
WRITE_SCOPE=PR #310 branch (`agent/dashscope-free-quota-exception-20260724`) ONLY: CLAUDE.md,
`config/governance/banned_llm_patterns.yaml`, `scripts/social/dashscope_free_media.py`,
`tests/social/test_dashscope_free_media.py`, `artifacts/coordination/operator_decisions_log.tsv`.
OUT_OF_SCOPE=everything else; especially no other exempt-path edits, no new DashScope call sites.
PROVENANCE: research=`artifacts/research/dashscope_free_media_2026-07-19/REPORT.md`;
documents=CLAUDE.md free-media exception (2026-07-24); builds_on=PR #310 (existing lane);
inventory=EXTENDS (no function dropped).

## Read first
CLAUDE.md §LLM Tier Policy; `config/governance/banned_llm_patterns.yaml` →
`dashscope_free_media_rest_api`; PR #310 diff (`gh pr diff 310`); the pack INDEX collision map.

## Live reconciliation (claims → re-verify) — emit a DISCOVERY REPORT before acting
- `gh pr view 310 --json state,mergeable,statusCheckRollup` — at authoring: OPEN, MERGEABLE.
- If ALREADY MERGED: your mission shrinks to steps 2–3 as a small successor PR off fresh
  `origin/main`. Stand down step 1 and say so.

## Mission
1. **Merge PR #310 on green.** Poll its required checks synchronously (Verify governance,
   parse-sweep; name each check's status — never "all pass"). If it lost an up-to-date race,
   re-root per repo convention and re-poll. Rule 0 diff-stat check before merge.
2. **Scope note (same PR as a follow-up commit if not yet merged; else successor PR):** the
   operator's 2026-07-24 ruling extends the free-quota burn's purpose to include the **manga
   video pose-bank method pilot** (this pack, Lane 05) under the SAME constraints: operator-run
   only, same env gates, same caps, sunset 2026-10-18, output provenance INTERIM per the Manga
   Vision-Conformance Doctrine. Edit the CLAUDE.md exception paragraph (one sentence added, do
   not restructure) + the `banned_llm_patterns.yaml` rule comment to match. Log
   `OPD-20260724-VBANK-00` (scope extension) in `operator_decisions_log.tsv`.
3. **Close the key-fallback drift risk:** `dashscope_free_media.py` `api_key()` silently falls
   back `DASHSCOPE_FREE_QUOTA_API_KEY → DASHSCOPE_API_KEY → QWEN_API_KEY` — the routine paid-risk
   key can be picked up if the free key is unset, contradicting the CLAUDE.md contract. Fix:
   when `PHOENIX_DASHSCOPE_FREE_MEDIA_ALLOW=1`, REQUIRE `DASHSCOPE_FREE_QUOTA_API_KEY` and
   hard-fail with a named blocker message if unset (no fallback). Add a regression test beside
   the existing 13 in `tests/social/test_dashscope_free_media.py`. Mutation-check: unset the var,
   gate goes RED; set it, GREEN.

## DO NOT
- Do not add ANY new file containing DashScope endpoint patterns (`X-DashScope-Async`,
  `/services/aigc/`) — the exempt_paths list is closed; extending it beyond the existing 3
  scripts is out of scope for this lane.
- Do not run any burn (that is Lane 05, operator-gated). Preflight-only invocations are fine.
- Do not touch PR #295, #331, or any uplift-pack path.

## Landing contract
MERGED (PR merged, checks named-green, signal emitted, branch deleted, worktree pruned) or
BLOCKED (blocker + evidence + work pushed). Cleanup ledger required. Handoff:
`artifacts/coordination/handoffs/manga_video_pose_bank_lane01_2026-07-24.md`.

CLOSEOUT_RECEIPT (exact): AGENT/TASK/COMMIT_SHA (full)/FILES_WRITTEN/PROVENANCE/STATUS/
NEXT_ACTION + `SIGNAL: dashscope-free-media-landed=<full merge SHA>`.
