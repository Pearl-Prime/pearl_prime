EXECUTE. Do not stop at "here is a draft index" — land the merged reference doc and the
delete-candidate ledger with a real PR. This lane runs ONLY after all 12 audit lanes
(`01`–`12` in this pack) are terminal (merged or documented-blocked).

# Lane 13 — CLI Audit Synthesis

## Pre-requisite gate (verify before starting — do not take this on faith)

```
gh pr list --state all --search "cli-audit" --limit 20
```
Confirm all 12 `agent/cli-audit-<slug>-20260722` branches are merged. If any are still
open/unmerged, either wait for them or, for a lane that is genuinely stalled, pull its
findings TSV directly off its branch (`git show <branch>:docs/cli_reference/findings/<slug>_FINDINGS.tsv`)
and proceed with a note in the synthesis doc that lane is partial.

## STARTUP_RECEIPT

```
STARTUP_RECEIPT
AGENT:              Pearl_PM
TASK:               Synthesize 12-lane CLI audit into program-wide reference + delete ledger
PROJECT_ID:         proj_cli_command_audit_20260722
SUBSYSTEM:          cross-cutting
AUTHORITY_DOCS:     docs/agent_prompt_packs/20260722_cli_command_audit/INDEX.md
READ_PATH_COMPLETE: yes
WRITE_SCOPE:        docs/CLI_COMMAND_REFERENCE.md; docs/CLI_AUDIT_DELETE_CANDIDATES.md; artifacts/coordination/operator_decisions_log.tsv (open questions); docs/DOCS_INDEX.md (add nav entries); docs/PROGRAM_STATE.md (milestone note)
OUT_OF_SCOPE:       deleting any script; editing any of the 12 lane docs (append-only reference from here, do not rewrite them)
PROVENANCE:         research: NONE; documents: the 12 lane findings TSVs; builds_on: N/A; inventory: UNCHANGED
BLOCKERS:           <fill from pre-requisite gate check>
READY_STATUS:       ready
```

## Mission

1. Concatenate all 12 `docs/cli_reference/findings/*_FINDINGS.tsv` files into one
   sorted table (by lane, then verdict severity: KEEP-CRITICAL, KEEP, MERGE-CANDIDATE,
   DEPRECATE-CANDIDATE, DELETE-CANDIDATE).
2. Write `docs/CLI_COMMAND_REFERENCE.md` — the program-wide index: total command count,
   per-lane summary table with links to each `docs/cli_reference/<slug>.md`, and a
   top-level "how to find the command you need" section (grouped by pipeline function,
   not by directory — e.g. "Render a manga episode" → link to the right doc/row).
3. Write `docs/CLI_AUDIT_DELETE_CANDIDATES.md` — every `DELETE-CANDIDATE` and
   `MERGE-CANDIDATE` row, each as an open question `Q-CLI-<NN>` with: the command(s) in
   question, the evidence (zero callers / superseded-by), a recommended default action,
   and space for operator ratification. Follow the walkthrough format from
   `docs/agent_brief.txt` §3 (batch operator decisions) — this doc IS that batch.
   **Do not delete anything here** — this is the ratification surface only.
4. Add a `docs/CLI_COMMAND_REFERENCE.md` entry to `docs/DOCS_INDEX.md`'s navigation
   table.
5. Add a milestone entry to `docs/PROGRAM_STATE.md` (first repo-wide CLI inventory:
   `<total>` commands across 12 pipeline subsystems documented on `<date>`, `<n>`
   delete-candidates awaiting operator ratification — link both new docs).
6. Any `KEEP-CRITICAL` row flagged in lane 08 or 12 as an LLM-policy or RAP-compliance
   issue (not just a duplication issue) gets pulled into its own short "Policy flags
   found during audit" section at the top of `CLI_AUDIT_DELETE_CANDIDATES.md`, marked
   for immediate owner attention separately from the deletion ratification batch — these
   are compliance issues, not cleanup candidates, and should not wait on the Q-CLI
   ratification cycle.

## Do not

- Do not delete any script — this pack documents and recommends only.
- Do not silently drop a lane's findings because it was BLOCKED — note the gap
  explicitly in `CLI_COMMAND_REFERENCE.md` ("lane 0X partial: <reason>") so the SSOT
  stays honest about coverage.
- Do not invent a verdict for a command the lane didn't cover — coverage gaps are
  reported, not filled in from guesswork.

## Landing

PR titled `docs(cli-audit): program-wide CLI reference + delete-candidate ledger`.
Merge on green.

## CLOSEOUT_RECEIPT

```
CLOSEOUT_RECEIPT
AGENT:          Pearl_PM
TASK:           CLI audit synthesis
COMMIT_SHA:     <full merge SHA>
FILES_WRITTEN:  docs/CLI_COMMAND_REFERENCE.md; docs/CLI_AUDIT_DELETE_CANDIDATES.md; docs/DOCS_INDEX.md; docs/PROGRAM_STATE.md; artifacts/coordination/operator_decisions_log.tsv
FILES_READ:     12x docs/cli_reference/findings/*_FINDINGS.tsv
PROVENANCE:     research: NONE; documents: the 12 lane docs; builds_on: N/A; inventory: UNCHANGED
STATUS:         completed | partial
HANDOFF_TO:     owner
NEXT_ACTION:    Operator reviews docs/CLI_AUDIT_DELETE_CANDIDATES.md, replies "go with defaults" or per-Q overrides. A follow-up pack (not in this session) executes ratified deletions/merges.
```

Signal token: `CLI_AUDIT_SYNTHESIS_COMPLETE: <total_commands> total, <n_delete_candidates> delete-candidates, SHA <full_sha>`
