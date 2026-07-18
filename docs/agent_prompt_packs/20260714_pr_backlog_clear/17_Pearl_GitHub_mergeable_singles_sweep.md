# Lane 17 — Mergeable substantive singles sweep

```text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_GitHub for Phoenix Omega, lane 17 (Wave 1) of the PR Backlog Clear pack.

Repo: Ahjan108/phoenix_omega_v4.8
Start from a clean checkout of latest origin/main.

STARTUP_RECEIPT:
- AGENT=Pearl_GitHub
- LANE=mergeable-singles-sweep
- EXECUTION_MODE=github_actions
- BACKGROUND_SAFE=yes
- RUNTIME_HOST=cloud-agent
- PERSISTENCE_SURFACES=PRs #4502,#4565,#4641,#4669,#4724,#4744,#4861,#5612; artifacts/coordination/handoffs/
- RESUME_SURFACE=artifacts/coordination/handoffs/mergeable-singles-sweep_2026-07-14.md

READ FIRST:
- docs/PROGRAM_STATE.md
- docs/agent_brief.txt (Router v3 §1 sibling-PR search, §9 reuse-before-authoring)
- docs/GITHUB_GOVERNANCE.md
- artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv

PRE-REQUISITE CHECKS:
- foundation-triage-complete=<signal from lane 01> must exist. If missing, STOP, BLOCKED.

LIVE STATE RECONCILIATION:
- Re-check each PR's live mergeable/CI state — the snapshot below is from
  pack-authoring time and WILL have drifted:
  `for n in 4502 4565 4641 4669 4724 4744 4861 5612; do gh pr view $n --json number,title,mergeable,statusCheckRollup; done`
- Snapshot at authoring time (all reported MERGEABLE):
  - #4502 content(atoms): Waystream atom-deficit fill — practice-shaped EXERCISE banks + gen_alpha REFLECTION shape
  - #4565 feat(pearl_star): queue reaper in git + ntfy starvation alerts
  - #4641 content(registry): purpose-seeded pool regen for 16 topics (#4619)
  - #4669 docs(bestseller): current-authoritative system inventory + banner 51 superseded docs
  - #4724 docs(manga): July 2026 closeout handoff — merge lane complete, 100pct=NO
  - #4744 audit(catalog): 14-market completeness + localized metadata truth
  - #4861 audit(governance): system-wide best-path enforcement plan [manga+book canaries]
  - #5612 add claude translation dispatcher agents
- These PRs range from late June to mid-July 2026 — some may already be
  functionally superseded by work that landed on main since (e.g. #5612 adds
  `.claude/agents/translate-*.md` files; if those agents already exist on
  main under a different mechanism, treat this as a stale-check, not a blind merge).

DISCOVERY REPORT BEFORE ACTION, per PR (do this for all 8 before merging any):
- diff each PR's file list against current main — for any file the PR adds
  that ALREADY EXISTS on main with different content, this is a genuine
  conflict/overlap requiring inspection, not a routine merge;
- for #5612 specifically: check whether `.claude/agents/translate-*.md` files
  already exist on main (they may — this session's own tool list already shows
  translate-de, translate-ja, translate-zh-cn, etc. as available agents). If
  they already exist and are IDENTICAL or a superset of #5612's content, this
  PR is likely already-landed-equivalent — verify via `git diff origin/main...5612branch -- .claude/agents/` and report whichever is true; do not merge a PR that would regress an already-improved file;
- for #4573-adjacent items (not in this lane, but #4641/#4669 touch registry/
  inventory docs that may reference it) — check for overlap with the "Book
  peak-requirements SSOT" work (memory: lives on OPEN #4573, edit-in-place,
  do not treat as separate).

PROVENANCE:
- research: NONE (each PR carries its own — verify at the PR level, not here)
- documents: each PR's own diff and description
- builds_on: existing registries/docs each PR extends — verify via CANONICAL_ARTIFACTS_REGISTRY.tsv reuse-first check
- inventory: EXTENDS per PR — any PR whose diff reduces existing wired functionality gets escalated, not merged

MISSION:
- Merge each of the 8 PRs independently, in any order, after per-PR verification
  that: (a) CI is green, (b) it does not net-delete >50 files (Rule 0), (c) it
  is not already superseded by current main, (d) it does not silently overlap/
  duplicate another PR in this same list (check pairwise before merging — e.g.
  #4669 and #4744 both touch inventory/completeness claims; read both before
  merging either, in case they conflict on a shared doc).

DELIVERABLES:
- Per-PR verdict: MERGED (with SHA) or BLOCKED (with reason) or
  ALREADY-SUPERSEDED (closed with a comment citing the superseding SHA/PR).

SMALLEST SAFE BATCH:
- smoke: merge the single lowest-risk PR first (#4669, docs-only banner PR) and
  confirm no downstream doc-link or CI check breaks.
- pilot: merge 3 more (#4565, #4641, #4744), re-verify CI.
- scale: merge the remainder (#4502, #4724, #4861, #5612) after confirming no
  pairwise overlap issues found in discovery.

HANG PREVENTION:
- checkpoint: after each PR merge attempt.
- no-progress rule: if a PR's CI has been failing for a reason unrelated to
  this program (e.g. a pre-existing flaky test), do not spend more than one
  retry chasing it — mark BLOCKED with the failing check name.
- hard stall rule: 3 unresolved PRs in a row with the same class of failure →
  stop, report BLOCKED for the whole remaining batch, escalate.
- max window: 45 minutes for all 8 PRs.

TESTS/PROOFS:
- Each PR's own required CI checks green pre-merge.
- `git diff origin/main...<pr-branch> --stat` captured per PR as the overlap-check evidence.

DO NOT:
- no force-merge over an unresolved file-overlap between two PRs in this batch;
- no closing a PR as "superseded" without citing the exact SHA/PR that supersedes it;
- no `--admin` merge, no `--no-verify`;
- no local-only finish.

LANDING CONTRACT:
- MERGED: every PR in this list is either merged, closed-as-superseded (with
  citation), or explicitly BLOCKED with a reason — no PR left in limbo.
- BLOCKED: name the exact PR(s) and reason.

CLEANUP LEDGER REQUIRED:
- worktree: none-needed
- local branch: none-needed
- remote branch: deleted on merge for each landed PR
- scratch files: remove diff-capture scratch files
- background jobs: none expected
- held artifacts: none expected

HANDOFF REQUIRED:
- artifacts/coordination/handoffs/mergeable-singles-sweep_2026-07-14.md with a
  per-PR verdict table (number, title, verdict, SHA or reason).

CLOSEOUT_RECEIPT:
- AGENT=Pearl_GitHub
- LANE=mergeable-singles-sweep
- STATUS=MERGED|BLOCKED
- MERGED=<list of PR#:SHA>
- SUPERSEDED=<list of PR#:citing-SHA>
- BLOCKED=<list of PR#:reason>
- SIGNAL=mergeable-singles-sweep-complete=<merged>/<8>
- PROOF_ROOT=<per-PR diff-stat evidence>
- TESTS=<CI results per PR>
- CLEANUP=<ledger above, filled in>
- HANDOFF=artifacts/coordination/handoffs/mergeable-singles-sweep_2026-07-14.md
- NEXT_ACTION=<report to Pearl_PM dispatcher>
```
