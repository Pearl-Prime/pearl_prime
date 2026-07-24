EXECUTE. Do not stop at "I found the files" or "here's a partial list" — produce
the complete reference doc and findings TSV for this lane's full scope, then land it.
Do not stop at "PR open" — drive to green and merge (or BLOCKED with evidence).

# Lane 03 — CLI Audit: Video Pipeline

## STARTUP_RECEIPT (emit before reading any code)

```
STARTUP_RECEIPT
AGENT:              Pearl_Video
TASK:               CLI command audit + reference doc — Video Pipeline
PROJECT_ID:         proj_cli_command_audit_20260722
SUBSYSTEM:          video_pipeline
AUTHORITY_DOCS:     config/video/;scripts/video/README.md;docs/specs/PEARL_VIDEO_BEAT_DRIVEN_NARRATIVE_PIPELINE_V1_SPEC.md;docs/specs/PEARL_VIDEO_FRAME_SELECTOR_BEST_OF_V1_SPEC.md
READ_PATH_COMPLETE: yes
WRITE_SCOPE:        docs/cli_reference/video_pipeline.md; docs/cli_reference/findings/video_pipeline_FINDINGS.tsv; one row in artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
OUT_OF_SCOPE:       any edit, rename, move, or delete of any .py/.sh file; any other lane's paths; docs/CLI_COMMAND_REFERENCE.md (owned by the synthesis lane)
PROVENANCE:         research: NONE (documentation/audit task); documents: config/video/;scripts/video/README.md;docs/specs/PEARL_VIDEO_BEAT_DRIVEN_NARRATIVE_PIPELINE_V1_SPEC.md;docs/specs/PEARL_VIDEO_FRAME_SELECTOR_BEST_OF_V1_SPEC.md; builds_on: N/A; inventory: UNCHANGED — read-only audit, zero code changes
BLOCKERS:           none known
READY_STATUS:       ready
```

## Live-truth reconciliation

```
git fetch origin
git checkout -b agent/cli-audit-video_pipeline-20260722 origin/main
gh pr list --state open --search "cli_reference video_pipeline"
```
If a sibling PR already covers this lane's scope, STOP and reconcile rather than
duplicating (sibling-session collision protocol).

## Read first

1. `docs/agent_prompt_packs/20260722_cli_command_audit/INDEX.md`
2. This lane's authority docs (above)
3. `artifacts/coordination/CANONICAL_ARTIFACTS_REGISTRY.tsv` — grep it for any script
   path in your scope; a registry hit means that script is ALREADY canonical (edit_not_recreate=YES)
   and should be marked KEEP with a citation, not re-evaluated from scratch.

## Scope

Files under: `scripts/video/ (41 files)`

## Lane-specific caution

Check scripts/video/README.md first — it may already document some of these commands; do not duplicate, cross-reference and correct instead.

## Mission

For every `.py` file in scope that matches `argparse.ArgumentParser(`, `click.command`,
or a `def main()` gated by `if __name__ == "__main__":`:

1. **Identify the command.** File path, one-line purpose (from module docstring / the
   argparse `description=` / `--help` text — read the file, do not guess from the
   filename alone).
2. **Find its callers.** `grep -rn "<basename>" --include="*.py" --include="*.yml" --include="*.sh" .`
   (excluding the file itself) to find: other scripts that import/exec it, CI workflow
   references, doc references, cron/scheduled-task references. Record a caller count.
3. **Check last-touched.** `git log -1 --format="%ai %h" -- <path>` for a freshness
   signal (not a verdict by itself — a stable canonical script can be untouched for
   months and still be load-bearing).
4. **Cluster near-duplicates.** Within this lane's scope, group commands that appear to
   solve the same job (same verb + same target entity, e.g. two "render X" or two
   "validate Y" commands). For each cluster, name the canonical one (registry hit, most
   callers, most recent authority-doc citation) and flag the others.
5. **Recommend a verdict per command:**
   - `KEEP` — canonical, wired, no better alternative.
   - `MERGE-CANDIDATE` — overlaps with another command in this lane; name the target it
     should merge into.
   - `DEPRECATE-CANDIDATE` — superseded but still has live callers; needs a migration
     step before deletion, not immediate deletion.
   - `DELETE-CANDIDATE` — zero callers found beyond itself, no registry citation, no CI
     reference, no doc reference. Note explicitly that this is a *candidate*, not an
     executed deletion.
   - `KEEP-CRITICAL` — anything found to be a CI-required gate, a Mandatory Preflight
     script, or (lane 12 only) an LLM-policy-relevant finding — call these out loudly.

## Deliverables

1. `docs/cli_reference/video_pipeline.md` — one row/section per command: path, one-line
   purpose, key flags (2-4 most important, not the full `--help` dump), caller count,
   last-touched date, verdict, and (if MERGE/DEPRECATE/DELETE) the evidence.
2. `docs/cli_reference/findings/video_pipeline_FINDINGS.tsv` — machine-readable, columns:
   `path\tlane\tpurpose\tcaller_count\tlast_touched\tverdict\tcluster_id\tnotes`
   (tab-separated, header row, one row per command — this feeds the Wave-3 synthesis).

## Do not

- Do not delete, rename, or move any file.
- Do not execute any CLI flag that performs a live write (network call, file mutation
  outside this lane's two deliverable files, GPU dispatch, credential use). `--help` /
  reading source is sufficient; do not run the pipelines themselves.
- Do not touch another lane's `docs/cli_reference/*` file.
- Do not mark something DELETE-CANDIDATE on a caller-count of zero alone if it is cited
  in CANONICAL_ARTIFACTS_REGISTRY.tsv, a CI workflow, or CLAUDE.md — those are callers
  too even if grep for the bare filename misses them (check for the module import path
  as well as the filename).

## Landing

Open a PR titled `docs(cli-audit): video_pipeline CLI reference + findings`. Merge it yourself
once checks are green (this is a docs-only PR touching two new files — low risk,
authorized for self-merge under the router's trivial-landing allowance). If checks
cannot go green, land as BLOCKED with the two files pushed on the branch and the exact
blocker recorded.

## CLOSEOUT_RECEIPT

```
CLOSEOUT_RECEIPT
AGENT:          Pearl_Video
TASK:           CLI command audit — Video Pipeline
COMMIT_SHA:     <full merge SHA>
FILES_WRITTEN:  docs/cli_reference/video_pipeline.md; docs/cli_reference/findings/video_pipeline_FINDINGS.tsv
FILES_READ:     <authority docs actually opened>
PROVENANCE:     research: NONE; documents: config/video/;scripts/video/README.md;docs/specs/PEARL_VIDEO_BEAT_DRIVEN_NARRATIVE_PIPELINE_V1_SPEC.md;docs/specs/PEARL_VIDEO_FRAME_SELECTOR_BEST_OF_V1_SPEC.md; builds_on: N/A; inventory: UNCHANGED
STATUS:         completed | partial | blocked
HANDOFF_TO:     Pearl_PM (synthesis lane 13)
NEXT_ACTION:    <if partial/blocked: exact resume point>
```

Signal token: `CLI_AUDIT_VIDEO_PIPELINE_COMPLETE: <n_commands> commands, <n_flagged> flagged, SHA <full_sha>`
