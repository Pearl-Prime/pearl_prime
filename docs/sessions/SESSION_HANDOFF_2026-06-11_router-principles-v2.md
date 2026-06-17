# Session Handoff — 2026-06-11 (Router Operating Principles v2 — encode + ship; recover from `--no-checkout` worktree poison)

**Author:** Pearl_GitHub (Claude) · **Branch base:** `origin/main` · **Operator:** ahjan
**Thread:** "Append a verbatim *Router Operating Principles v2* block to `docs/agent_brief.txt` BELOW the unchanged 9-line bootstrap; add one pointer line to `docs/SESSION_UNITY_PROTOCOL.md` §'Universal router prompt'; single small docs-only PR; preserve the bootstrap as the byte-identical file head; do not merge — operator reviews."

---

## 0. TL;DR

- **Shipped [PR #1502](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1502)** — docs-only, **2 files, +46 / −0**, the 9-line bootstrap byte-identical at the file head, **NOT merged** (operator reviews). Commit `bf71767f533f9f5cb447eb93ab596c5665990b3a`.
- **Hit and fully recovered from a 57,101-file commit poison.** Root cause: `origin/main` *tracks* ~57k `.claude/worktrees/**` files and `.claude/` is not gitignored, so a `git worktree add --no-checkout` left them absent → they staged as **57,099 phantom deletions** alongside the 2 real edits. **Nothing was pushed**; the bad commit + branch + worktree were torn down and rebuilt clean with **sparse-checkout**.
- **New durable lesson** saved to memory (`feedback_worktree_no_checkout_poison.md`) + indexed. This handoff doc is shipped as its **own** small PR (kept out of #1502 to preserve that clean diff).
- **NEXT_ACTION:** operator merges #1502 anytime — **no cascade dependency**. Separately flagged a real repo-hygiene landmine (§8) for an operator-tier decision.

---

## 1. The task (verbatim intent)

The operator pasted a fully-specified Pearl_GitHub router prompt. Goal: encode the router's hard-won operating reflexes (deconfliction, default-decision posture, worktree discipline, decision-batching) into `docs/agent_brief.txt` as a **versioned, revertable section below the unchanged 9-line bootstrap**, so any future router session inherits them via the protocol pointer instead of re-learning them by colliding live sessions. Plus a one-line pointer in `SESSION_UNITY_PROTOCOL.md`. Docs-only, collision-safe, single small PR, do not merge.

**Hard constraints honored:** bootstrap text untouched and byte-identical at the file head; principles block appended **verbatim** (no paraphrase); no coordination TSV / SSOT / gap-matrix / cap / code touched; no paid-LLM references; clean standalone PR.

---

## 2. STARTUP_RECEIPT

```
AGENT:              Pearl_GitHub
TASK:               Append "Router Operating Principles v2" to docs/agent_brief.txt (below 9-line bootstrap) + 1 pointer line in SESSION_UNITY_PROTOCOL.md
PROJECT_ID:         none (router/protocol docs infra)
SUBSYSTEM:          session-unity / router bootstrap (docs)
AUTHORITY_DOCS:     docs/SESSION_UNITY_PROTOCOL.md; CLAUDE.md; docs/agent_brief.txt
READ_PATH_COMPLETE: yes
WRITE_SCOPE:        docs/agent_brief.txt (append-only); docs/SESSION_UNITY_PROTOCOL.md (1 line)
OUT_OF_SCOPE:       all coordination TSVs, SSOT, gap matrix, cap entries, PEARL_ARCHITECT_STATE.md, operator_decisions_log.tsv, any code
BLOCKERS:           none
READY_STATUS:       ready
```

---

## 3. Discovery findings (pre-work)

| Check | Result |
|-------|--------|
| `docs/agent_brief.txt` head | 9-line bootstrap confirmed (lines 1–9), file ends after line 9 — the verbatim head to preserve |
| `SESSION_UNITY_PROTOCOL.md` §"Universal router prompt" | line 130 = the `**Canonical full text:** ./agent_brief.txt …` anchor; pointer goes directly below it |
| Sibling-PR search | `gh pr list --search "Router Operating Principles" --state all` **empty**; `agent_brief` **empty** → no collision (re-checked again pre-push, still empty) |
| Git state | main tree on divergent branch `agent/gold-reference-7tier-redirect-20260530` (40↑/111↓) → **must use a worktree from origin/main**, not this tree |
| Disk | 44 GB free (> 20 GB precheck threshold) — OK |
| `git check-attr filter` on both docs | `unspecified` → not LFS, safe to materialize without smudge |

---

## 4. What shipped — PR #1502

| PR | SHA | What | Type |
|----|-----|------|------|
| [#1502](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1502) | `bf71767f5` | Append *Router Operating Principles v2* below the 9-line bootstrap in `agent_brief.txt` + 1 pointer paragraph in `SESSION_UNITY_PROTOCOL.md` | docs |

**Files:**
- `docs/agent_brief.txt` — **+44 / −0**, `9 → 53` lines. Pure append below a `---` divider. First 9 lines **byte-identical** to `origin/main` (verified `diff` of `show origin/main:…|head -9` vs edited head → identical).
- `docs/SESSION_UNITY_PROTOCOL.md` — **+2 / −0**, `130 → 132` lines. One pointer paragraph (blank-line-separated, matching the section's existing paragraph style) under the canonical-text line.
- Net: **2 files changed, 46 insertions(+), 0 deletions.**

**The appended block** (verbatim, below the divider) carries: §0 the router's job · §1 deconflict-before-authoring · §2 default-decision posture · §3 batch operator decisions · §4 worktree/disk discipline · §5 CLOSEOUT discipline · §6 git-first drift recovery · §7 auto-open + verify · §8 standard prompt skeleton · Revert instructions. The 9-line bootstrap above the divider is explicitly never in the blast radius.

**Gates (all green):**
- `push_guard.py` → `status: ok` (1 commit, 2 files, 0.0097 MB total, 0.005 MB max single; limits 30/300/25/8).
- `preflight_push.sh` → `Preflight OK.` (surfaced current max OPD-154 — irrelevant; no OPD added).
- 0 behind / 1 ahead origin/main; no merge/rebase/cherry-pick in progress.
- Push: `lfs.locksverify false` set; new branch pushed clean.
- Remote verification: `gh pr view` → `additions 46, deletions 0, changedFiles 2, base main, MERGEABLE, OPEN`; remote branch head 9 lines byte-identical to main.
- CI at handoff time: pending (Governance review / Verify governance / docs-governance queued). `Workers Builds: pearl-prime` red is **known OPD-153 noise**, non-blocking. Verify governance (ruleset-required) expected PASS — 2 docs, no code, no coordination-file touch.

---

## 5. THE INCIDENT — 57,101-file commit poison (and recovery)

**This is the load-bearing lesson of the session.** Documented in full because it will bite any future worktree-based session in this repo.

### 5.1 What happened
First commit attempt (`13ccb7bee`, never pushed) contained **57,101 files**: my 2 real doc edits **+ 57,099 deletions** of `.claude/worktrees/**` and friends. Caught immediately when `git diff --cached --name-only` returned a 13.9 MB list instead of 2 paths.

### 5.2 Root cause
- **`.claude/` is NOT gitignored** — the root `.gitignore` only excludes `.claude/cloudflare_credentials.txt`.
- **`origin/main` actually tracks ~57,000 `.claude/worktrees/**` files** as regular blobs (a past session committed the worktree mega-tree into the repo).
- The worktree was created with `git worktree add --no-checkout` (correct, to avoid the ~3.2 GB/worktree LFS smudge — see `project_worktree_disk_constraint`). But `--no-checkout` leaves every tracked file absent from the working tree → git reads all 57k tracked files as **deletions**, and they get captured by the commit.
- Confirmed nature: `git diff --name-status origin/main...HEAD | awk … | uniq -c` → **`57099 D` + `2 M`**.

### 5.3 Recovery (all local — nothing pushed)
1. Read-only topology check first (there are live cascades; a wrong `reset --hard`/`clean` could destroy a sibling session): confirmed the worktree was **properly isolated** (own `--show-toplevel`, own git-dir under `.git/worktrees/…`, registered, main tree untouched at `0d0fc9b06`, poison commit on **no** remote).
2. `git worktree remove --force <wt>` + `git branch -D <branch>` → poison gone.
3. `git fetch origin` + recreate worktree `--no-checkout` from current `origin/main`.
4. **`git sparse-checkout init --no-cone` + `git sparse-checkout set docs/agent_brief.txt docs/SESSION_UNITY_PROTOCOL.md` + `git checkout`** → only the 2 target files materialize; the 57k mega-tree files get the **SKIP_WORKTREE** bit and become invisible to `git add` / un-stageable.
5. Verified the rebuild: `find` → exactly 2 files; `git status --short` → **0 lines** (no phantom deletions); `git diff --cached` → 0.
6. Re-applied both edits, staged the 2 explicit paths, and **gated the commit** on `diff --cached --name-only` == exactly 2 before committing. Result: `bf71767f5` — *2 files changed, 46 insertions(+), 0 deletions.*

### 5.4 Prevention (now in memory)
For **any** worktree-based commit in this repo: after `git worktree add --no-checkout`, immediately `git sparse-checkout set <target paths>` **before touching anything**, then gate the commit on `git status --short` == 0 AND `git diff --cached --name-only` == your exact intended file set. `push_guard.py` is the backstop (it would have hard-blocked the 57k push at the 300-file limit), but sparse-checkout prevents the wasted cycle entirely. Saved as `feedback_worktree_no_checkout_poison.md` and indexed in `MEMORY.md`.

---

## 6. Verification summary (remote truth, not just local)

- PR #1502 JSON: `additions=46, deletions=0, changedFiles=2, baseRefName=main, mergeable=MERGEABLE, state=OPEN`.
- Remote branch `docs/agent_brief.txt` first 9 lines **byte-identical** to `origin/main` (`diff` empty).
- Appended block is verbatim (applied exactly as supplied; no paraphrase).

---

## 7. CLOSEOUT_RECEIPT

```
AGENT:          Pearl_GitHub
TASK:           Append "Router Operating Principles v2" to docs/agent_brief.txt (below 9-line bootstrap) + 1 pointer line in SESSION_UNITY_PROTOCOL.md
COMMIT_SHA:     bf71767f533f9f5cb447eb93ab596c5665990b3a
PR:             https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1502  (base main, OPEN, MERGEABLE — NOT merged)
FILES_WRITTEN:  docs/agent_brief.txt (+44/-0, 9->53 lines); docs/SESSION_UNITY_PROTOCOL.md (+2/-0, 130->132 lines) => 2 files, 46 insertions(+), 0 deletions
FILES_READ:     docs/SESSION_UNITY_PROTOCOL.md; docs/agent_brief.txt; CLAUDE.md; scripts/git/push_guard.py; scripts/ci/preflight_push.sh; scripts/git/health_check.sh; memory/feedback_message_terseness.md
STATUS:         completed
HANDOFF_TO:     none
NEXT_ACTION:    Operator reviews + merges #1502 whenever convenient (no cascade dependency). After merge, every future router session inherits v2 via the SESSION_UNITY pointer. Revert anytime: `git revert` the PR or delete from the `---` divider down in agent_brief.txt.
```

---

## 8. DEFERRED — needs operator decision (latent repo-health landmine)

**`.claude/worktrees/**` (~57k files) is tracked in `origin/main`, and `.claude/` is not gitignored.** This is the root of the poison in §5 and a standing hazard for every worktree/agent session:

- Every `--no-checkout` worktree inherits 57k phantom deletions (mitigated now by the sparse-checkout reflex, but the underlying cause remains).
- The mega-tree inflates clones, `git status`, and any `git add -A` (which is exactly why the router principles ban `git add -A` in this tree).

**Recommended fix (operator-tier — NOT done this session):** add `.claude/` (or at least `.claude/worktrees/`) to `.gitignore` and `git rm -r --cached .claude/worktrees/`. **Caveat:** that deletion touches > 50k files → it is hard-blocked by the governance ruleset (>500 files) and must be an **operator atomic ruleset-bypass PR** (same 2X.4 pattern as #696/#727). This is a genuine business/ops call about repo hygiene, so it is surfaced here rather than executed.

---

## 9. Where the operator was, returning to live work

This ws was explicitly **zero-urgency / collision-safe** and run in a quiet moment. The live cascades remain the priority:
- master session's **atom-coverage settle**
- **storefront unpark**
- **Pearl Star install** fire

Both PRs from this session (#1502 router-principles; this handoff doc PR) are **do-not-merge / operator-review** and have **no cascade dependency** — they can be merged or closed anytime without affecting the live work.

---

## 10. Memory written this session

- **`feedback_worktree_no_checkout_poison.md`** (new) — the §5 lesson, with the sparse-checkout procedure + commit gate. Cross-links `feedback_git_worktree_for_lock_contention` and `project_worktree_disk_constraint`.
- **`MEMORY.md`** — one index line added under the existing worktree entries.

---

*Generated by Pearl_GitHub (Claude Code) · session 2026-06-11.*
