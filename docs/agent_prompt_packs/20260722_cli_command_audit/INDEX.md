# CLI Command Audit — Prompt Pack Index

**Created:** 2026-07-22
**Router:** Piper (this session)
**Live-truth anchor:** `origin/main` after `git fetch origin` on 2026-07-22; local branch
`agent/bestseller-atom-flow-lanes-20260721` is 23 ahead / 2 behind origin/main (unrelated
work — do not branch this pack from the local dirty branch; branch each lane fresh from
`origin/main` per `docs/agent_brief.txt` §10). `gh pr list --state open` showed ~10 open
offline-triage LAND PRs, none touching CLI documentation/audit — no collision found.

## Program goal

Audit and document **every CLI-shaped entrypoint** (`argparse.ArgumentParser`,
`click.command`, or a `def main()` driven by `if __name__ == "__main__"`) across the
repo's production pipeline subsystems. For each command: what it does, who owns it,
whether it is still wired to anything (callers, CI, docs), and — where two or more CLIs
overlap in purpose — a KEEP / MERGE / DEPRECATE-CANDIDATE / DELETE-CANDIDATE
recommendation with evidence. Deliver a per-subsystem CLI reference doc and a findings
TSV; do **not** delete or move any script in this pack — deletion is an operator-tier
call gated at the end (see L-SYNTH below).

## Source request

> "prompts for documentation of the main cli commands for all major repo pipeline
> functions. audit all. and if there's multi cli commands and .py desc and analyze if
> it needs to stay or be deleted."

## Scale (discovered, 2026-07-22)

`grep -rl "argparse.ArgumentParser\|click.command\|def main("` across the repo (excluding
`.git`, `node_modules`, `venv`, `__pycache__`) returns **1,121 files**. Excluding stray
`.worktrees/*` copies (~150), the real population is on the order of **~970 CLI-shaped
`.py` files**. This is why the work is split into 12 subsystem lanes below rather than
one prompt — no single agent should hold ~1,000 files of live-truth context.

Top populations found (file count with argparse/click, by directory):
`scripts/manga` 117 · `scripts/ci` 101 · `scripts/video` 41 · `scripts/qa` 38 ·
`scripts/catalog` 30 · `scripts/localization` 18 · `scripts/publish` 17 ·
`scripts/release` 15 · `scripts/image_generation` 15 · `scripts/social` 13 ·
`phoenix_v4/ops` 13 · `scripts/social_media` 11 · `scripts/onboarding` 10 ·
`tools/teacher_mining` 9 · `scripts/research` 9 · `scripts/marketing` 9 ·
`scripts/catalog_visibility` 9 · `phoenix_v4/qa` 9 · `artifacts/qa` 9 ·
`scripts/integrations` 8 · `scripts/brand` 8 · `scripts/audit` 8 · `scripts/music` 7 ·
`scripts/podcast` 6 · `scripts/observability` 6 · `scripts/ml_editorial` 6 ·
`scripts/git` 6.

## Prompt count

**14** — 12 audit lanes (`01`–`12`) + `00_MASTER_DISPATCH_PROMPT.md` (Pearl_PM,
dispatches waves 1–2 and runs synthesis) + `13_SYNTHESIS_PROMPT.md` (wave 3, single
serial actor, only after all 12 lanes are MERGED-or-BLOCKED).

## Wave order

- **Wave 1 (parallel, no shared files):** lanes 01–12 all write to disjoint paths
  (`docs/cli_reference/<lane_slug>.md` + `docs/cli_reference/findings/<lane_slug>_FINDINGS.tsv`)
  — safe to run fully concurrently, one PR per lane.
- **Wave 2:** none — Wave 1 lanes are independent by construction (see Dependencies).
- **Wave 3 (serial, single actor):** `13_SYNTHESIS_PROMPT.md` — reads all 12 merged
  findings TSVs, builds `docs/CLI_COMMAND_REFERENCE.md` (index) and
  `docs/CLI_AUDIT_DELETE_CANDIDATES.md` (Q-CLI-NN operator questions with recommended
  defaults for anything rated DELETE-CANDIDATE). This is the only lane that touches a
  program-wide file and therefore must run after all 12 land, one actor at a time.

## Dependencies

Lanes 01–12 have zero file-scope overlap (see per-lane WRITE_SCOPE) and zero
sequencing dependency on each other — this is why they can all run in Wave 1. Lane 13
(synthesis) depends on all 12 lanes reaching MERGED or a documented BLOCKED with
partial findings pushed.

## Owners and subsystem authority (from `SUBSYSTEM_AUTHORITY_MAP.tsv`)

| Lane | Scope | Owner agent | Subsystem |
|---|---|---|---|
| 01 | Core spine/orchestration (`scripts/run_pipeline.py`, `scripts/run_manga_pipeline.py`, `phoenix_v4/ops/`, `scripts/pilot/`) | Pearl_Prime | core_pipeline |
| 02 | Manga (`scripts/manga/`) | Pearl_Dev | manga_pipeline |
| 03 | Video (`scripts/video/`) | Pearl_Video | video_pipeline |
| 04 | Catalog (`scripts/catalog/`, `scripts/catalog_visibility/`) | Pearl_Prime | core_pipeline / brand_admin |
| 05 | Publish & release (`scripts/publish/`, `scripts/release/`) | Pearl_DevOps | pearl_devops |
| 06 | Localization (`scripts/localization/`) | Pearl_Localization | translation |
| 07 | QA & gates (`scripts/qa/`, `phoenix_v4/qa/`, `artifacts/qa/`) | Pearl_Dev | core_pipeline |
| 08 | Media generation (`scripts/image_generation/`, `scripts/music/`, `scripts/podcast/`) | Pearl_Dev | music_mode / podcast_pipeline |
| 09 | Social & marketing (`scripts/social/`, `scripts/social_media/`, `scripts/marketing/`) | Pearl_Int | trend_feeds / marketing |
| 10 | Brand, onboarding, integrations (`scripts/brand/`, `scripts/onboarding/`, `scripts/integrations/`) | Pearl_Int | brand_admin / integrations |
| 11 | CI, git, audit, observability tooling (`scripts/ci/`, `scripts/git/`, `scripts/audit/`, `scripts/observability/`) | Pearl_DevOps | pearl_devops |
| 12 | Editorial, teacher-mode, research tooling (`tools/teacher_mining/`, `scripts/research/`, `scripts/ml_editorial/`) | Pearl_Editor | teacher_mode |
| 13 (synthesis) | Program-wide index + delete-candidate ledger | Pearl_PM | — |

## Substrates

Each lane: fresh branch off `origin/main` (`agent/cli-audit-<lane_slug>-20260722`), no
worktree required (read-heavy audit, small doc writes — a plain checkout is fine; use
`GIT_LFS_SKIP_SMUDGE=1` if the shared tree is used). No GPU/Pearl Star dispatch in this
pack — this is a static-analysis + doc-writing task.

## Write scopes

Each lane writes **only**:
- `docs/cli_reference/<lane_slug>.md` (new)
- `docs/cli_reference/findings/<lane_slug>_FINDINGS.tsv` (new)

No lane edits any script, any existing doc, any CI workflow, or any coordination TSV
except appending its own `ACTIVE_WORKSTREAMS.tsv` row. **No lane deletes any file.**

## Hot-file conflict notes

None between lanes 01–12 (disjoint new-file paths). `ACTIVE_WORKSTREAMS.tsv` is a
shared hot file — each lane appends exactly one row and must follow the plumbing-commit
pattern for hot files (`feedback_plumbing_commit_hot_files` memory) if a concurrent
sibling is mid-edit. Lane 13 is the only writer of
`docs/CLI_COMMAND_REFERENCE.md` / `docs/CLI_AUDIT_DELETE_CANDIDATES.md` and must run
after all 12 are terminal.

## Outputs / proof roots

- `docs/cli_reference/<lane_slug>.md` × 12
- `docs/cli_reference/findings/<lane_slug>_FINDINGS.tsv` × 12
- (Wave 3) `docs/CLI_COMMAND_REFERENCE.md`, `docs/CLI_AUDIT_DELETE_CANDIDATES.md`
- Full merge SHAs for each landed PR, recorded in each lane's CLOSEOUT_RECEIPT

## Signal tokens

Each lane emits `CLI_AUDIT_<LANE_SLUG>_COMPLETE: <n_commands_found> commands, <n_flagged> flagged for review, SHA <full_sha>`
in its CLOSEOUT_RECEIPT. Lane 13 emits
`CLI_AUDIT_SYNTHESIS_COMPLETE: <total_commands> total, <total_delete_candidates> delete-candidates, SHA <full_sha>`.

## Cleanup expectations

Delete local branches/worktrees after merge; no scratch files outside
`docs/cli_reference/`; no credentials touched (this is a read-only static analysis
task, no live API calls).

## Status

**NOT YET DISPATCHED.** This pack is ready to paste. Recommended entry point:
paste `00_MASTER_DISPATCH_PROMPT.md` into the lead agent (Pearl_PM), which will fan out
lanes 01–12, then run 13 once all are terminal.
