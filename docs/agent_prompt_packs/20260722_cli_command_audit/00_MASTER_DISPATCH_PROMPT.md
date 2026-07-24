EXECUTE. Do not stop at a plan, a summary, or "lanes dispatched" — drive every lane to
MERGED or BLOCKED, then run synthesis. This is a multi-hour dispatcher session; if you
are about to end the turn with any lane still open/running, that is a stall, not a
handoff.

# Pearl_PM — CLI Command Audit Dispatcher

## STARTUP_RECEIPT (emit before dispatching anything)

```
STARTUP_RECEIPT
AGENT:              Pearl_PM
TASK:               Dispatch 12-lane CLI command audit + doc pack, then synthesize
PROJECT_ID:         proj_cli_command_audit_20260722 (new — register in ACTIVE_PROJECTS.tsv)
SUBSYSTEM:          cross-cutting (docs/cli_reference/ — new path, no existing authority row)
AUTHORITY_DOCS:     docs/agent_brief.txt; docs/PROMPT_ROUTER_OPERATING_MANUAL.md; docs/SESSION_UNITY_PROTOCOL.md; docs/DOCS_INDEX.md
READ_PATH_COMPLETE: yes
WRITE_SCOPE:        docs/agent_prompt_packs/20260722_cli_command_audit/ (status updates); artifacts/coordination/ACTIVE_PROJECTS.tsv; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
OUT_OF_SCOPE:       any script deletion; any edit inside scripts/, phoenix_v4/, tools/
PROVENANCE:         research: NONE (pure audit/documentation task, no new capability); documents: this pack's INDEX.md; builds_on: N/A; inventory: UNCHANGED (read-only audit, no code touched)
BLOCKERS:           none known
READY_STATUS:       ready
```

## Read first

1. `docs/agent_prompt_packs/20260722_cli_command_audit/INDEX.md` — full pack context, lane table, scale numbers
2. `docs/agent_brief.txt` (Router Operating Principles) and `docs/AGENT_PROMPT_ROUTER_V4.md`
3. `artifacts/coordination/ACTIVE_PROJECTS.tsv`, `ACTIVE_WORKSTREAMS.tsv`, `SUBSYSTEM_AUTHORITY_MAP.tsv`

## Live-truth reconciliation (do this before dispatching, and again before synthesis)

```
git fetch origin
gh pr list --state open --search "cli_reference"
gh pr list --state open --search "CLI audit"
```
If either search returns a hit, STOP that lane and reconcile (sibling-session collision
protocol) instead of dispatching a duplicate.

## Mission

1. Register `proj_cli_command_audit_20260722` in `ACTIVE_PROJECTS.tsv` and one
   `ACTIVE_WORKSTREAMS.tsv` row per lane (`ws_cli_audit_<lane_slug>_20260722`).
2. Dispatch lane prompts `01_...md` through `12_...md` (this pack's directory) — all in
   parallel, each to its own agent session/branch. Each lane prompt is fully
   self-contained and paste-ready as-is.
3. Poll/watchdog every lane to MERGED-or-BLOCKED. A lane that goes silent for longer
   than a normal PR cycle is a stall — re-drive it (SendMessage to resume, do not
   silently wait).
4. Once **all 12** lanes are terminal (merged, or blocked with findings pushed), paste
   `13_SYNTHESIS_PROMPT.md` to yourself (or a fresh Pearl_PM session) and execute it.
5. Update `docs/PROGRAM_STATE.md` with a new entry once synthesis lands (milestone —
   this is the first repo-wide CLI inventory).

## Do not

- Do not delete, move, or rename any `.py` file in this pack. Deletion recommendations
  are the deliverable; actual deletion is a separate, operator-ratified follow-up pack.
- Do not merge two lanes' PRs together — one PR per lane, each independently reviewable.
- Do not skip the sibling-PR search before dispatch.

## Landing contract

Each of the 12 lanes: MERGED (PR opened, checks green, merged, full SHA recorded) or
BLOCKED (exact blocker, partial findings pushed, HOLD path declared). Synthesis (13):
same contract, additionally gated on all 12 being terminal.

## CLOSEOUT_RECEIPT (emit when all 12 + synthesis are terminal)

```
CLOSEOUT_RECEIPT
AGENT:          Pearl_PM
TASK:           CLI command audit — 12-lane dispatch + synthesis
COMMIT_SHA:     <synthesis PR full merge SHA>
FILES_WRITTEN:  docs/CLI_COMMAND_REFERENCE.md; docs/CLI_AUDIT_DELETE_CANDIDATES.md; 12x docs/cli_reference/*.md; 12x docs/cli_reference/findings/*_FINDINGS.tsv
FILES_READ:     <this pack's INDEX.md + all 12 lane closeouts>
PROVENANCE:     research: NONE; documents: this pack; builds_on: N/A; inventory: UNCHANGED
STATUS:         completed | partial
HANDOFF_TO:     owner (operator ratifies Q-CLI-NN delete candidates)
NEXT_ACTION:    Operator reviews docs/CLI_AUDIT_DELETE_CANDIDATES.md and ratifies with "go with defaults" or per-item overrides; a follow-up pack executes ratified deletions.
```

Signal token on full completion: `CLI_AUDIT_SYNTHESIS_COMPLETE: <total> total, <n> delete-candidates, SHA <full_sha>`
