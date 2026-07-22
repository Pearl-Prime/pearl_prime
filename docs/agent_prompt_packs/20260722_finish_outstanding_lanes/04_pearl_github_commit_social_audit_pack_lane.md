# Lane 4 — Pearl_GitHub: Commit the social-media-audit prompt pack; reconcile with Lane 1's #53 split

EXECUTE. This lane has two parts: a trivial docs commit, and a dependency check against
Lane 1's work that must not be skipped.

## STARTUP_RECEIPT

Re-verify live:
```
ls docs/agent_prompt_packs/20260722_social_media_audit_100pct_plan/
ls -la .git/index.lock
git status --short docs/agent_prompt_packs/20260722_social_media_audit_100pct_plan/
```
Confirm the 4 pack files exist (`00_MASTER_DISPATCH_PROMPT.md` +
`01_pearl_github_land_social_package_lane.md`,
`02_pearl_research_verify_social_research_currency_lane.md`,
`03_pearl_pm_social_100pct_production_plan_lane.md`), that no `.git/index.lock` is
blocking, and that these files are untracked/uncommitted.

## Task

**Part A — commit the pack.** This is docs-only, no code. Commit exactly these 4 files
via the standard plumbing pattern (temp index off `origin/main^{tree}`, explicit
paths — do not `git add -A` given this repo's large dirty working tree). Push and open
a PR, or fold into whatever branch is live at commit time per standard flow.

**Part B — reconcile with Lane 1.** This pack's own lane 1
(`01_pearl_github_land_social_package_lane.md`, inside the social-audit pack, NOT this
outer pack's Lane 1) was written describing the #53/#55 collision as still-open and
recommending #53 get untangled. By the time this lane runs, the outer pack's Lane 1
(`01_pearl_github_unbreak_main_ci_lane.md`) may have already resolved that collision
(merged #55, split #53 into a new social-schema-only PR). Before dispatching the
social-audit pack's own 3 lanes to a Pearl_PM session:
   - Check `gh pr list` for the current state of #53/#55 and any new split-out PR.
   - If Lane 1 already landed the social-schema PR, update the social-audit pack's
     lane 1 file to point at the new PR number instead of #53/#55, and note in its
     text that the collision is resolved rather than open.
   - If Lane 1 hasn't run yet or is still in progress, leave the social-audit pack's
     lane 1 as-is (it correctly describes live BLOCKED state) but add a one-line note
     at its top: "Superseded once docs/agent_prompt_packs/
     20260722_finish_outstanding_lanes/01_... lands — check PR state before executing
     this lane's PR-untangling instructions verbatim."

## Landing

Docs-only commit: MERGED or BLOCKED. The pack itself is not executed by this lane —
that's a separate operator decision (paste its own `00_MASTER_DISPATCH_PROMPT.md` into
a lead agent once Lane 1 upstream is confirmed resolved).

## CLOSEOUT_RECEIPT (required, exact)

Commit SHA for the pack. Confirmation of whether Part B found the collision already
resolved or still open, and what (if anything) was edited in the social-audit pack as a
result. Signal token: `LANE4_SOCIAL_AUDIT_PACK_COMMITTED_<SHA>`.
