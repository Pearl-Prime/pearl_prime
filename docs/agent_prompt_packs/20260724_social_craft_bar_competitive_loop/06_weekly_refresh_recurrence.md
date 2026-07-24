# Lane 06 — Weekly Research-Refresh Recurrence (plan gap #4, owned-never-executed)

~~~text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_DevOps for Phoenix Omega.

Repo: Pearl-Prime/pearl_prime. Substrate: fresh branch off latest origin/main
(agent/social-weekly-refresh-cron-20260724). Explicit-path staging; poison protocol.

STARTUP_RECEIPT:
- AGENT=Pearl_DevOps
- LANE=social_weekly_refresh_recurrence_20260724
- EXECUTION_MODE=github_actions (the deliverable) authored from local_fallback
- PERSISTENCE_SURFACES=branch/PR/workflow-file
- RESUME_SURFACE=artifacts/coordination/handoffs/social_weekly_refresh_recurrence_2026-07-24.md

READ FIRST:
- docs/specs/SOCIAL_MEDIA_100PCT_PRODUCTION_PLAN_2026-07-22.md gap #4 (this lane EXECUTES it — cite
  the gap ID, do not re-scope it)
- docs/PEARL_SOCIAL_MEDIA_WRITER_AGENT_SPEC_2026-07-18.md §Weekly Research Refresh (the process
  being scheduled — it already ran correctly twice, manually: 2026-07-18 and 2026-07-22 via #114)
- artifacts/qa/social_research_currency_audit_20260722/RESEARCH_CURRENCY_AUDIT.md (CADENCE_GAP_FOUND
  = yes; S5 content items to fold into the next digest)
- CLAUDE.md LLM Tier Policy (scheduled/unattended = Tier 2 Pearl Star or non-LLM ONLY; NO paid
  APIs; NO ANTHROPIC_API_KEY in workflows — llm-policy-enforcement.yml blocks it)
- .github/workflows/pearl-news-daily.yml + marketing-briefs-and-proposals.yml (the house pattern
  for scheduled content workflows — mirror, do not invent)

PRE-REQUISITE CHECK: none (Wave 1 — independent). But verify live whether ANY recurrence mechanism
appeared since 2026-07-24 (grep .github/workflows + scripts/scheduled_tasks + crontabs for the
refresh entrypoint) — if one exists, STAND DOWN and report the delta (already-done = SUCCESS).

LIVE STATE RECONCILIATION: fetch; identify the exact refresh entrypoint script(s) used by the two
manual runs (from the 07-18 handoff + PR #114's diff) — the digest builder + delta-atom promoter.
Re-verify the CLAIM that no .github/workflows file references them.

DISCOVERY REPORT before action: current SHA; entrypoint inventory with exact commands the manual
runs used; which steps require an LLM (if any step does, it must route Tier-2 via pscli/RAP or be
descoped to open-a-digest-issue-for-operator instead — read docs/ROBUST_AGENT_PROTOCOL.md before
wiring any Pearl Star dispatch).

PROVENANCE:
- research: RESEARCH_CURRENCY_AUDIT.md (cadence gap evidence)
- documents: SOCIAL_MEDIA_100PCT plan gap #4; writer spec §refresh
- builds_on: the existing refresh scripts (schedule them, never re-author); house scheduled-workflow
  pattern
- inventory: EXTENDS (adds scheduling; changes no refresh logic)

MISSION (narrow):
1. Author .github/workflows/social-weekly-research-refresh.yml — weekly cron (pick a quiet UTC slot
   consistent with house patterns), concurrency group, runner preflight, fail-closed on missing
   creds, artifact upload of the digest, and an auto-opened ISSUE (or PR comment) delivering the
   digest for operator review. The workflow must be inert-safe: if a step cannot run unattended
   within LLM policy, it emits the worklist as an issue instead of silently skipping.
2. Fold the audit's S5 content items (IG hashtag-count guidance, LinkedIn ~140-char tune, Meta
   caption-link watch-item) into the refresh config/checklist so the NEXT digest carries them.
3. actionlint the workflow (GHA startup_failure class: PyYAML-valid ≠ GHA-valid — lint before
   push).
4. Trigger one workflow_dispatch smoke run post-merge and poll it to terminal state — EXECUTED-REAL
   requires one real unattended-path firing, not just the file existing.

DELIVERABLES: the workflow file; refresh-config S5 additions; smoke-run URL + conclusion in the
handoff; PR.

SMALLEST SAFE BATCH: smoke = actionlint + workflow_dispatch dry-run (digest-build step may run in
--dry-run mode if supported); pilot = full dispatch run; scale = the cron itself (verified next
scheduled firing — name it as a wake-signal in NEXT_ACTION, do not park a watcher).

HANG PREVENTION: poll the dispatched run every 5 min via gh run watch/gh run view; 2/3 rules; max
window 3 h.

TESTS/PROOFS: actionlint clean; smoke run conclusion=success (or failure diagnosed + fixed same
turn); python3 scripts/ci/audit_llm_callers.py clean; grep proof that no paid-LLM env var enters
the workflow.

DO NOT: put any paid-LLM key or ANTHROPIC_API_KEY in the workflow; re-author the refresh logic;
schedule Tier-1 (Claude) work unattended; leave the workflow merged-but-never-fired; touch
coordination hot files.

LANDING CONTRACT: MERGED (PR "feat(social): weekly research-refresh recurrence — plan gap #4",
checks green, squash-merged, smoke run fired, signal) or BLOCKED.

CLEANUP LEDGER + HANDOFF: artifacts/coordination/handoffs/social_weekly_refresh_recurrence_2026-07-24.md

CLOSEOUT_RECEIPT: standard fields + full MERGE_SHA + smoke-run URL.
SIGNAL: social-weekly-refresh-wired=<full merge SHA>
ACCEPTANCE LAYER: CODE-WIRED at merge; EXECUTED-REAL after the dispatch smoke; claim "recurring
system working" only after the first UNATTENDED cron firing (name the date it is expected).
~~~
