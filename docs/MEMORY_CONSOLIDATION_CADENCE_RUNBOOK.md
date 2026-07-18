# Memory Consolidation Cadence Runbook

**Spec:** `docs/specs/AGENT_SYSTEM_IMPROVEMENT_V2_SPEC.md` → **P0-6** ("Add a
`consolidate-memory` cadence for `MEMORY.md`").
**Owner:** Pearl_PM (repo_coordination).
**Status:** runnable (non-🏛 P0 batch).

## Purpose

The Claude Code auto-memory (`MEMORY.md` + its sibling topic files) is a *reflective*
store: agents append lessons over time. Reflective memory has a documented failure
mode — a **self-reinforcing error**, where a once-true or never-quite-true "lesson"
ossifies and keeps steering decisions after it has gone stale. P0-6 mitigates that by
running the existing **`consolidate-memory`** skill on a **periodic cadence** to
challenge, merge, and prune memory entries.

This runbook is the human-facing half of the cadence. The machine half is the
scheduled reminder workflow `.github/workflows/memory-consolidation-reminder.yml`.

## What the cadence is (and deliberately is NOT)

| | |
|---|---|
| **Cadence trigger** | Scheduled GitHub workflow `memory-consolidation-reminder.yml` — quarterly cron (`0 9 1 1,4,7,10 *`) + `workflow_dispatch`. It opens ONE dedup'd operator-action issue per quarter. |
| **Consolidation engine** | The **existing** packaged skill `anthropic-skills:consolidate-memory`. **Reused, never reimplemented.** |
| **Where it runs** | An **operator-present Claude Code session** (Tier-1). |
| **Where it does NOT run** | **Not in CI.** The runner has no `MEMORY.md`, and reflective LLM consolidation must not run unattended (CLAUDE.md LLM Tier policy). CI only *reminds*. |
| **Pre-flight helper** | `scripts/memory/memory_cadence_preflight.py` — read-only freshness snapshot. No LLM call. Optional, for triage. |

### Why CI reminds instead of executing

1. **The data is local.** `MEMORY.md` lives at
   `~/.claude/projects/<project-slug>/memory/MEMORY.md` on the operator's machine —
   e.g. `~/.claude/projects/-Users-ahjan-phoenix-omega/memory/MEMORY.md`. It is not
   checked into the repo and is not present on a GitHub Actions runner.
2. **The skill is Tier-1.** `consolidate-memory` does a reflective English-prose pass
   (challenge/merge/prune). Per the CLAUDE.md LLM Tier policy, that is operator-present
   Claude work — it must **not** run as an unattended pipeline step, and it must never
   call a paid LLM API. Running it in CI would violate both the data-locality reality
   and the Tier policy.

So the only correct cadence mechanism here is a **scheduled nudge**: CI opens the
issue; the operator runs the skill.

## Operator procedure (per reminder issue)

When the `operator-action-required` issue titled
`Operator: run consolidate-memory cadence on MEMORY.md (<year>-Q<n>)` appears (or
whenever you want to run the cadence ad hoc):

1. **Open a Claude Code session in this project** (so the auto-memory dir resolves to
   this project's memory).

2. **(Optional) Pre-flight freshness snapshot.** Read-only, no model call — just tells
   you which entries are oldest and whether the index has drifted:
   ```bash
   python3 scripts/memory/memory_cadence_preflight.py --stale-days 45
   # JSON form for tooling:
   python3 scripts/memory/memory_cadence_preflight.py --json
   # Point at a specific memory dir if auto-resolve picks the wrong one:
   CLAUDE_MEMORY_DIR=~/.claude/projects/<slug>/memory \
     python3 scripts/memory/memory_cadence_preflight.py
   ```
   Use the "stale review candidates" and "files not linked from MEMORY.md" lists to
   decide where to focus.

3. **Run the existing consolidate-memory skill** in the session:
   ```
   Skill consolidate-memory
   ```
   This invokes `anthropic-skills:consolidate-memory` — the reflective pass that
   merges duplicate entries, fixes stale facts, prunes the index, and surfaces
   entries that may encode a wrong/ossified lesson. **Do not** write a new
   consolidation routine; this skill is the canonical engine.

4. **Review and apply.** Read the skill's proposed edits. Accept the sound merges /
   corrections / prunes; reject anything that would drop a still-true lesson. Pay
   special attention to any entry the skill flags as possibly-wrong — that is the
   self-reinforcing-error case this cadence exists to catch.

5. **Close the issue** with a one-line note of what changed (e.g. "merged 3 dup
   campaign-pacing entries, corrected stale duration label note, pruned 2 obsolete
   anchors"). This keeps an audit trail of each cadence pass.

## Adjusting the cadence

- **Frequency:** edit the `schedule.cron` in
  `.github/workflows/memory-consolidation-reminder.yml`. Default is quarterly
  (`0 9 1 1,4,7,10 *`). For a monthly cadence use `0 9 1 * *`.
- **Run on demand:** trigger the workflow via the Actions tab (`workflow_dispatch`) or
  just run the operator procedure above without waiting for the issue.
- **Staleness threshold:** the pre-flight `--stale-days` flag (default 45) only changes
  *which files are highlighted*; it does not change what the skill consolidates.

## Operator wiring still required (first-increment)

The scheduled workflow opens issues only after it is on `main` and GitHub Actions is
enabled for scheduled runs on this repo. Until the orchestrator merges it and the
operator confirms the schedule is active, run the cadence manually via the operator
procedure above. The default `GITHUB_TOKEN` with `issues: write` is sufficient — no new
secret is needed.

## Related

- `docs/specs/AGENT_SYSTEM_IMPROVEMENT_V2_SPEC.md` — P0-6 source.
- `.github/workflows/manga-stash-reminder.yml`,
  `.github/workflows/branch-hygiene-sweep.yml` — the reminder-issue pattern this
  cadence reuses.
- `artifacts/coordination/CANONICAL_ARTIFACTS_REGISTRY.tsv` — registers this cadence's
  canonical assets so future agents EDIT them rather than fork a parallel cadence.
