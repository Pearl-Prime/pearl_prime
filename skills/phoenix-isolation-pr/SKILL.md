---
name: phoenix-isolation-pr
description: "Phoenix Omega isolation PR workflow. Use for a small WRITE_SCOPE off origin/main: worktree bootstrap (LFS-skip + read-tree + checkout-index), explicit-path staging, safety gate vs origin/main cached diff, preflight, commit, push, and gh pr create. Pearl_Conductor subagents invoke this instead of embedding git boilerplate."
---

# phoenix-isolation-pr — Isolation PR Skill (Phoenix Omega)

## 1. PURPOSE

This skill produces a **single, reviewable isolation PR** for a small **WRITE_SCOPE** of paths, always based on **origin/main**. It centralizes the worktree-add → branch → copy from source locations (if any) → safety gate → preflight → commit → push → PR pattern that has been used successfully across isolation PRs **#966, #969, #970, #971, #972, #973, #974, #975, #976, #977, #978, #979, #988, #801**. The goal is to shrink subagent prompts by referencing this skill instead of re-stating ~300 lines of git/worktree/PR boilerplate each spawn, reducing token waste and drift risk.

**Authority / coordination context:** `docs/SESSION_UNITY_PROTOCOL.md`, `CLAUDE.md`, `skills/pearl-github/SKILL.md`, `skills/pearl-int/SKILL.md` (read for repo policy; this skill does not replace them — it operationalizes the isolation slice).

---

## 2. INVOCATION

A subagent (or router) opens this file and follows it end-to-end. Invoke explicitly in the task prompt, for example:

> Use **phoenix-isolation-pr** skill with:
> - **WRITE_SCOPE**=`comma-separated repo-relative paths` (exact list that must appear in the commit and nothing else)
> - **SOURCE_LOCATIONS**=`map: dest_path <- source_abs_or_repo_path` (optional; if empty, you author directly in the worktree)
> - **PR_TITLE**=`conventional-commit style title`
> - **PR_BODY_TEMPLATE**=`heredoc or path to body template` (must include scope checkboxes)
> - **COMMIT_MSG**=`type(scope): summary` (matches PR intent)

**Non-negotiable:** Never expand WRITE_SCOPE without operator approval. Never stage paths outside WRITE_SCOPE.

---

## 3. WORKTREE BOOTSTRAP — LFS-skip + read-tree + checkout-index

Run from the **primary repo** (`/Users/ahjan/phoenix_omega` or your canonical clone). Use a dedicated worktree path per task.

```bash
export GIT_LFS_SKIP_SMUDGE=1
export GIT_OPTIONAL_LOCKS=0

cd /Users/ahjan/phoenix_omega

git fetch origin

# Remove stale worktree path if reusing the same directory name
if [ -d /path/to/YOUR_TASK_WT ]; then
  git worktree remove --force /path/to/YOUR_TASK_WT 2>/dev/null || rm -rf /path/to/YOUR_TASK_WT
fi

git worktree add --no-checkout /path/to/YOUR_TASK_WT origin/main

cd /path/to/YOUR_TASK_WT

git read-tree HEAD
git checkout-index -a -f

git checkout -B agent/<task-summary>-YYYYMMDD
```

**Why this shape:** `GIT_LFS_SKIP_SMUDGE=1` avoids LFS smudge failures during materialization; `GIT_OPTIONAL_LOCKS=0` reduces optional lock contention with IDE git workers; `read-tree` + `checkout-index` after `--no-checkout` avoids the mass-checkout failure modes from an incomplete tree state (see Known Pitfalls).

---

## 4. EXPLICIT-PATH ADD (staging)

After edits/copies exist on disk **only** for paths in WRITE_SCOPE:

```bash
cd /path/to/YOUR_TASK_WT

# Example — replace with your exact WRITE_SCOPE paths, one per line:
git add skills/example/SKILL.md docs/example/spec.md
```

**FORBIDDEN:** `git add .`, `git add -A`, `git add -u` without explicit paths, or directory adds that pull in unintended files.

If SOURCE_LOCATIONS maps external files into the worktree, copy with explicit `cp`/`install` per path, then `git add` **only** those destinations.

---

## 5. SAFETY GATE — cached diff vs origin/main

Before committing, the staged set must match WRITE_SCOPE **exactly** (same paths, same cardinality, no extras, no omissions).

```bash
cd /path/to/YOUR_TASK_WT

git fetch origin

git diff origin/main --name-only --cached | sort > /tmp/staged.txt
printf "%s\n" <WRITE_SCOPE lines one per path> | sort > /tmp/expected.txt

diff -u /tmp/expected.txt /tmp/staged.txt
```

**Rule:** `git diff origin/main --name-only --cached` output (sorted) **must equal** WRITE_SCOPE (sorted). If not: **STOP**, reset unintended staging (`git restore --staged …` / fix working tree), fix scope with operator if needed.

**Do not use** `git diff --cached --name-only` alone for this gate on long-lived worktrees — compare against **origin/main** (see Known Pitfalls).

---

## 6. PREFLIGHT

From the worktree, with `PYTHONPATH` including the repo root if required:

```bash
cd /path/to/YOUR_TASK_WT

PYTHONPATH=. python3 scripts/git/push_guard.py
bash scripts/ci/preflight_push.sh
```

**Advisory (hourly / before high-risk git):**

```bash
bash scripts/git/health_check.sh
```

If push_guard or preflight_push **fails**: **STOP** and escalate; do not push.

---

## 7. COMMIT

```bash
cd /path/to/YOUR_TASK_WT

git commit -m "type(scope): summary matching COMMIT_MSG"
```

- Use the repo’s conventional commit style agreed in the task (e.g. `feat`, `fix`, `arch`, `docs`, `ci`).
- **Do not** pass `--no-verify` unless the operator has documented an explicit exception in the task packet and Pearl_GitHub has acknowledged it.

---

## 8. PUSH + PR

```bash
cd /path/to/YOUR_TASK_WT

git push -u origin HEAD

gh pr create --title "$PR_TITLE" --body-file /path/to/body.md
# or: gh pr create --title "$PR_TITLE" --body "$(cat <<'EOF'
# ... PR_BODY_TEMPLATE ...
# EOF
# )"
```

- Confirm PR **base** is `main` (or the operator-declared integration branch after explicit fetch — see Known Pitfalls).
- Fill PR body from **PR_BODY_TEMPLATE**; include scope, validation checklist, and subsystem / project IDs if provided.

---

## 9. CLOSEOUT — CLOSEOUT_RECEIPT fields

Return a **CLOSEOUT_RECEIPT** to the orchestrator containing at minimum:

| Field | Content |
|--------|---------|
| `branch` | Local branch name pushed |
| `pr_url` | `gh pr view --web` URL or `gh pr create` output URL |
| `pr_number` | Numeric PR # |
| `commit_sha` | Full SHA of the tip commit |
| `write_scope` | Exact WRITE_SCOPE list (echoed) |
| `safety_gate` | Confirmed: staged vs `origin/main` diff matched WRITE_SCOPE |
| `preflight` | push_guard + preflight_push outcomes |
| `notes` | Anything the next agent must know (CI quirks, follow-ups) |

If the operator requires file dumps (sandbox persistence risk), follow `docs/AGENT_FILE_PERSISTENCE_PROTOCOL.md`.

---

## 10. ERROR ESCALATION — STOP vs continue

| Situation | Action |
|-----------|--------|
| **Clone / fetch / worktree hang** beyond reasonable wall time | **STOP**; capture logs; do not partial-push; ask operator / try alternate network window. |
| **`.git/index.lock` / lock contention** | **STOP** after one bounded retry with `GIT_OPTIONAL_LOCKS=0` and confirming no concurrent git in IDE; do not `kill -9` git blindly. |
| **LFS smudge / pointer / dirty LFS state** | **STOP** until `GIT_LFS_SKIP_SMUDGE=1` bootstrap pattern is applied; verify no accidental LFS objects staged. |
| **Safety gate mismatch** (staged paths ≠ WRITE_SCOPE) | **STOP**; never commit “near enough”. |
| **push_guard or preflight_push failure** | **STOP**; read JSON from `push_guard.py --json` if available; fix base branch or scope. |
| **Governance / ruleset / `pr_governance_review.py` BLOCKED** for the PR | **STOP**; operator decision — do not merge bypass. |
| **Minor typo in PR title before review** | Continue: `gh pr edit` if available and in-scope. |

---

## 11. KNOWN PITFALLS (this week’s hard lessons)

### 11.1 LFS smudge errors during `git clone --no-checkout` / worktree materialization

**Symptom:** Smudge filter errors, partial objects, or LFS fetch failures during checkout.

**Mitigation:** Always export `GIT_LFS_SKIP_SMUDGE=1` for bootstrap; use **`git read-tree HEAD`** then **`git checkout-index -a -f`** after `--no-checkout` worktree creation.

### 11.2 `.git/index.lock` contention (Cursor `gitWorker`, parallel agents)

**Symptom:** “Unable to create `.git/index.lock`”, intermittent staging failures.

**Mitigation:** `export GIT_OPTIONAL_LOCKS=0`; avoid parallel `git` in the same worktree; back off and retry; never delete locks while another git process is actively running.

### 11.3 “No diff” / wrong staged file list from stale worktree index

**Symptom:** `git diff --cached --name-only` looks empty or wrong vs what you think you staged.

**Mitigation:** For the safety gate, **`git diff origin/main --name-only --cached`** (always anchor to `origin/main`).

### 11.4 PR base mismatch when work accidentally stacks on another PR branch

**Symptom:** PR shows hundreds of commits / files; push-guard explodes.

**Mitigation:** `git fetch origin`; verify `git merge-base HEAD origin/main` is expected; create a **new branch from `origin/main`** and cherry-pick only your commits if contaminated.

### 11.5 Mass-deletion / empty tree failure after `git clone --no-checkout` without `read-tree`

**Symptom:** Broken index, missing files, or catastrophic deletions in later steps.

**Mitigation:** After any `--no-checkout` clone/worktree, **always** run **`git read-tree HEAD`** followed by **`git checkout-index -a -f`** before editing.

---

## Quick reference — happy path checklist

1. `GIT_LFS_SKIP_SMUDGE=1 GIT_OPTIONAL_LOCKS=0 git fetch origin`
2. `git worktree add --no-checkout … origin/main` → `git read-tree HEAD` → `git checkout-index -a -f` → `git checkout -B agent/…`
3. Author / copy **only** WRITE_SCOPE paths
4. `git add <each path explicitly>`
5. Safety gate: `git diff origin/main --name-only --cached` ≡ WRITE_SCOPE
6. `PYTHONPATH=. python3 scripts/git/push_guard.py` && `bash scripts/ci/preflight_push.sh`
7. `git commit -m "…"` → `git push -u origin HEAD` → `gh pr create …`
8. CLOSEOUT_RECEIPT to orchestrator

---

## Coordination with Pearl_GitHub (human or agent)

When **Pearl_GitHub** is available as a separate agent, **phoenix-isolation-pr** executes in the worktree while Pearl_GitHub owns merge readiness and branch protection interpretation. Division of labor:

| Step | phoenix-isolation-pr executor | Pearl_GitHub reviewer |
|------|------------------------------|------------------------|
| Base branch selection | Uses `origin/main` unless operator names an integration branch | Confirms merge-base |
| Staging / commit | Performs explicit `git add` + safety gate | Audits for EXCLUSIVE files |
| Push | Runs push_guard + preflight | May substitute `scripts/git/safe_push.sh` if policy requires |
| PR body | Fills technical scope from template | Adds governance / risk sections |
| Merge | **Out of scope** — never implicit | Sole owner per `skills/pearl-github/SKILL.md` |

If you **are** Pearl_GitHub executing this skill solo, you still follow the same checklist; the table is about clarity, not permission to skip gates.

---

## WRITE_SCOPE hygiene — examples

**Good — 3-file doc isolation:**

```text
WRITE_SCOPE:
- docs/specs/EXAMPLE_SPEC.md
- artifacts/coordination/EXAMPLE_NOTE.md
- skills/example/SKILL.md
```

**Bad — vague scope:**

```text
WRITE_SCOPE:
- docs/   # NEVER: directory wildcard without explicit enumeration
```

**Good — generated + hand-authored pair:**

```text
WRITE_SCOPE:
- reports/tmp_output.tsv
- docs/DEV_ENTRY.md
```

…where `reports/tmp_output.tsv` was produced by a deterministic script listed in the task packet and copied into the worktree with a single explicit `cp`.

---

## PR title / body alignment

- **Title** and **COMMIT_MSG** should reflect the same intent (type/scope/summary).
- **PR_BODY_TEMPLATE** must call out:
  - PROJECT_ID / SUBSYSTEM (if coordination task)
  - Validation commands actually executed (honest checkboxes)
  - “No unrelated refactors” scope statement
  - Link to orchestrator log row (if spawned from Pearl_Conductor v2)

---

## Reference — isolation PRs that informed this skill

This workflow pattern was exercised successfully across Phoenix Omega isolation PRs **#966, #969, #970, #971, #972, #973, #974, #975, #976, #977, #978, #979, #988, #801**. Treat these as historical proof points, not as bypass for current governance rules.

---

## Optional — splitting work across two PRs

If WRITE_SCOPE naturally splits into disjoint layers (e.g. docs vs CI yaml), prefer **two isolation PRs** with two skill invocations rather than one oversized PR. Pearl_Conductor v2 benefits from smaller WRITE_SCOPE lists per spawn.

---

## Telemetry for orchestrators (v2)

When Pearl_Conductor v2 logs activity, include in `notes`:

- Branch name
- Safety gate command output digest (e.g. `sha256sum /tmp/staged.txt`)
- `push_guard.py --json` key limits if near thresholds

This makes postmortems possible without re-reading entire transcripts.
