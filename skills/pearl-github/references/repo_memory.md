# Pearl_GitHub Repo Memory

This is lived operational memory, not theory. Read this before risky git work.

## Incident Memory

### 2026-03-20 — Wrong-base branch triggered push-guard hard block

What happened:

- `agent/manga-mode` was created from `codex/runtime-consolidation`, not from `origin/main`
- Push attempt was blocked by pre-push guard with:
  - `commits=200`
  - `files=22573`
  - `total_mb=2716.5`
  - `max_blob_mb=37.3`
- The actual intended change was small, but ancestry made the push look enormous

What this means:

- Branch name is not enough
- Small staged diff is not enough
- Pearl_GitHub must inspect ancestry against `origin/main` before any push

Recovery pattern that worked:

```bash
git fetch origin
git checkout -b agent/<task>-clean origin/main
git cherry-pick <good-commit>
git push -u origin agent/<task>-clean
```

Permanent lesson:

- Never create agent branches from `codex/*`
- Always verify with `git rev-list --left-right --count origin/main...HEAD`
- If ahead count is unexpectedly large, stop immediately

### 2026-03-20 — Branch existed on GitHub but local worktree did not actually contain Pearl_GitHub

What happened:

- Local branch `agent/pearl-github` existed but matched `origin/main`
- The intended Pearl_GitHub commit existed in history (`d7971156`) but was not present in the checked-out branch files
- `ps.txt` was missing on the branch
- `CLAUDE.md` was also missing on the branch

Recovery pattern that worked:

- Cherry-pick the intended commit onto the real branch
- Resolve `CLAUDE.md` conflict
- Create branch-valid `ps.txt`
- Push the repaired branch

Permanent lesson:

- Do not assume a branch name means the branch contains the feature
- Verify with:

```bash
git log --oneline --decorate -n 5
git status --short --branch
find skills -maxdepth 2 -type f
```

### 2026-03-20 — Tooling mismatch across branches

What happened:

- `ps.txt` instructed Pearl_GitHub to run `python scripts/git/push_guard.py`
- On this branch:
  - `python` was not available, only `python3`
  - `scripts/git/push_guard.py` did not exist
  - `scripts/ci/preflight_push.sh` existed but required `bash` invocation

Permanent lesson:

- Pearl_GitHub must check repo reality before following a command literally
- Health checks must degrade gracefully when branch-specific tooling is absent
- Preferred pattern:
  - use `python3` when available
  - check file existence before invoking tooling
  - invoke shell scripts with `bash ...`

### 2026-03-30 — Sandbox file loss: D1/D3 voice re-localization + deep-research skill (×3)

What happened:

- Pearl_Writer agents in Cowork sandbox wrote D1 (4 files) and D3 (4 files) voice
  re-localization SCENE content — 240 scenes total
- Sandbox could not push (no GitHub credentials, no network access to github.com)
- `.git/index.lock` was stuck and could not be removed (permission denied in sandbox)
- Agent sessions ended. Files existed only in sandbox memory. Content was lost.
- Same pattern hit Pearl_Research deep-research skill files 3 times earlier in the day
- D2 survived because it got a git commit through before the lock appeared

Root cause:

- Cowork sandbox ≠ user's local filesystem for agent operations
- Files written to sandbox are ephemeral unless committed or dumped
- No protocol existed to ensure content persistence when git is blocked

Recovery:

- D1/D3 were rewritten from scratch via Cowork session (which HAS disk access)
- Deep-research files were recreated 3 times before finally being committed

Permanent lesson:

- All content-writing agents MUST run `scripts/agent/persist_or_dump.sh` after writing
- If git is blocked, agent MUST dump full file contents in CLOSEOUT_RECEIPT
- Never report "done" without commit SHA or file dump
- See `docs/AGENT_FILE_PERSISTENCE_PROTOCOL.md` for the full protocol
- Prefer Cowork direct-write (Option A) for critical content over sandbox agents

Files affected:

- `atoms/working_parents/{burnout,financial_anxiety}/SCENE/CANONICAL.txt` (D1)
- `atoms/healthcare_rns/{burnout,financial_anxiety}/SCENE/CANONICAL.txt` (D1)
- `atoms/gen_alpha_students/{burnout,financial_anxiety}/SCENE/CANONICAL.txt` (D3)
- `atoms/corporate_managers/{burnout,financial_anxiety}/SCENE/CANONICAL.txt` (D3)
- `skills/deep-research/SKILL.md` and reference files (×3 losses)

### 2026-05-08 — Stale `.git/index.lock` vs live IDE-driven lock churn (Pearl_DevOps)

What happened:

- A `.git/index.lock` was sitting at `/Users/ahjan/phoenix_omega/.git/index.lock`, size 0, mtime ~8 hours old, with `lsof` reporting **no holder**.
- Concurrently, the canonical checkout had **74+ live `git status --porcelain` processes** running, all spawned by Cursor's `gitWorker.js` (PPID `76215`) and Xcode's git plugin (`git-lfs filter-process` siblings). The IDE refreshes the index continuously, which legitimately creates and releases `index.lock` many times per minute.
- Naïve `rm -f` on a lock would, in this environment, race a live IDE git operation and corrupt the index.

Recovery pattern that worked:

```bash
lsof /Users/ahjan/phoenix_omega/.git/index.lock        # MUST return no rows (no holder)
ls -la /Users/ahjan/phoenix_omega/.git/index.lock      # size==0 and age > 30 min => stale
rm -f /Users/ahjan/phoenix_omega/.git/index.lock
# Verify with light probes; do NOT use `git status` as the witness if the IDE is hot:
git -C /Users/ahjan/phoenix_omega rev-parse HEAD       # < 1s — does not need index lock
git -C /Users/ahjan/phoenix_omega stash list           # quick — does not need index lock
GIT_TERMINAL_PROMPT=0 git -C /Users/ahjan/phoenix_omega fetch origin --dry-run
```

Permanent lessons:

- A reappearing `index.lock` after removal is **expected** under heavy IDE load and is **not necessarily stale**. Re-run `lsof` before considering removal again.
- `git status` is a **bad witness** for "lock is healthy" when 70+ concurrent IDE-driven status processes are flooding the working tree. It blocks on filesystem and lock contention even when nothing pathological is happening. Prefer `rev-parse HEAD`, `stash list`, and `fetch --dry-run`.
- Three-way decision rule for an existing lock:
  1. `lsof` shows a holder → **leave alone** (live op, will release).
  2. `lsof` empty + size 0 + mtime > 30 min → **safe `rm -f`**.
  3. `lsof` empty + size > 0 → **escalate**: this is a partially-written index op that may need `git fsck` follow-up; do not remove without operator review.

### 2026-05-08 — `git clone --no-checkout` leaves the index EMPTY (near-miss on Rule #0)

What happened:

- Pearl_DevOps could not commit/push from canonical `phoenix_omega` because the IDE + four other parallel agents had wedged `git worktree add` for 35+ minutes with no progress (see next entry).
- Fallback was a fresh clone: `GIT_LFS_SKIP_SMUDGE=1 git clone --no-checkout --depth 1 --single-branch --branch main https://github.com/Ahjan108/phoenix_omega_v4.8.git /Users/ahjan/phoenix_hyg_v2`.
- After `git checkout -b agent/<branch>` and `git add artifacts/qa/<one-file>.md`, the staged diff showed **55,232 files changed (+234 / −7,728,766)** — the entire repo as deletions plus the one new file.
- Root cause: `git clone --no-checkout` does **not** populate the index from `HEAD`. The index is left effectively empty. Adding a single file then commits a near-empty tree, i.e. a catastrophic mass-deletion identical in shape to the PR #245 incident.

Recovery pattern that worked (caught BEFORE commit):

```bash
git -C <clone> ls-files | wc -l                # if << HEAD tree size, index is empty
git -C <clone> read-tree HEAD                  # populates index from HEAD without touching working tree
git -C <clone> diff --cached --stat            # MUST be empty after read-tree
git -C <clone> add <single-new-file>
git -C <clone> diff --cached --stat            # MUST show only the new file
```

Permanent lessons:

- **Always run `git diff --cached --stat | tail -3` immediately before `git commit`** in any clone or worktree whose state you did not personally hand-craft. If the count is large or shows mass deletions you did not intend, **STOP**.
- After any `git clone --no-checkout` (or any clone where the working tree is not fully populated), run `git read-tree HEAD` before staging anything.
- This is now a Rule #0 sub-rule: **a one-file commit that triggers a 50,000-file deletion diff is the same incident class as PR #245.** Treat it the same way.

### 2026-05-08 — `git worktree add` wedges under heavy concurrent agent + IDE load

What happened:

- Pearl_DevOps ran `git worktree add /Users/ahjan/phoenix_omega_hygiene_audit_wt -b agent/<branch> origin/main` from canonical.
- At the same moment, **at least 4 other agent sessions** were running their own `git worktree add`, `git checkout -B`, `git fetch origin && git checkout -B agent/<branch> origin/main`, and `git reset --hard origin/main` on the same `.git`. Plus Cursor's 74 concurrent `git status --porcelain` workers.
- The worktree's admin dir at `/Users/ahjan/phoenix_omega/.git/worktrees/phoenix_omega_hygiene_audit_wt` was created within seconds (HEAD, commondir, gitdir, index.lock, `locked initializing`), but the working-tree checkout phase **stalled for 35+ minutes** with no admin-dir mtime updates. `lsof` on the git pid showed it endlessly reading pack `.idx` files but never advancing past ~25% of file count.
- A second-line attempted recovery (`git worktree prune` + manual cleanup) also stalled in the sandbox, leaving a partially-checked-out directory at `/Users/ahjan/phoenix_omega_hygiene_audit_wt`.

Recovery pattern that worked:

- Killed the stuck `git worktree add` process.
- Bypassed canonical entirely: `GIT_LFS_SKIP_SMUDGE=1 git clone --no-checkout --depth 1 --single-branch --branch main https://github.com/Ahjan108/phoenix_omega_v4.8.git <fresh dir>` (≈ 8 min including network transfer).
- Did all branch / commit / push work in the fresh clone (after `git read-tree HEAD` per the previous entry).

Permanent lessons:

- When canonical `phoenix_omega` is hot (multiple `git worktree add` / `git reset --hard` from sibling agents + IDE git workers), do **not** attempt yet another `git worktree add` from canonical. It will queue indefinitely on `.git/worktrees/`-level coordination and `index.lock`-class contention.
- Preferred fallback: a fresh `--no-checkout --depth 1 --single-branch GIT_LFS_SKIP_SMUDGE=1` clone outside `~/phoenix_omega` (and outside the sandbox-write boundary you must remember to lift). Combined with the `read-tree HEAD` rule above, this is the safest contention-free path for small documentation PRs.
- Detection signal: if `git worktree add` is still alive after 5 minutes and the admin-dir `mtime` has not advanced in 2 minutes, consider it wedged.

### 2026-05-08 — "Orphan worktree" often means tracked-by-secondary-repo, not abandoned

What happened:

- Operator reported `/Users/ahjan/phoenix_omega_pearl_star_install_prep_wt` was on disk but absent from `git -C /Users/ahjan/phoenix_omega worktree list`. Looked like a classic orphan candidate for `rm -rf`.
- Reading the worktree's `.git` gitfile revealed `gitdir: /Users/ahjan/phoenix_omega_gitops_tmp/.git/worktrees/phoenix_omega_pearl_star_install_prep_wt` — the worktree was tracked by a **secondary clone** at `/Users/ahjan/phoenix_omega_gitops_tmp` (whose own `origin` points at the local canonical), not by canonical itself.
- `git -C /Users/ahjan/phoenix_omega_gitops_tmp worktree list` listed it cleanly. `git status --short` from inside it returned exit 0, empty output (clean).
- Unilateral `rm -rf` would have orphaned an admin entry inside `phoenix_omega_gitops_tmp/.git/worktrees/` and left the secondary clone in a broken state.

Recovery pattern that worked:

- Did **not** delete. Documented as "orphan-vs-canonical / tracked-by-secondary-repo, clean".
- Recommended coordinated cleanup to the operator: `git -C /Users/ahjan/phoenix_omega_gitops_tmp worktree remove <path>` first, then optionally retire the secondary clone.

Permanent lessons:

- An on-disk `_wt` directory that is missing from canonical `git worktree list` is **not necessarily orphan**. Always:
  ```bash
  cat <wt>/.git                                       # read the gitfile pointer
  ls -la $(awk -F': ' '{print $2}' <wt>/.git)         # confirm admin dir exists
  ```
  If the gitfile points to **any** repo other than canonical, that repo owns the worktree.
- Sibling secondary clones in `~/phoenix_omega_*` (e.g. `phoenix_omega_gitops_tmp`, `phoenix_omega_pearl_prime_contract`, `phoenix_omega_preflight_runtime`) are part of the local working set and may own `_wt` directories that look orphan from canonical's perspective. Audit them before pruning anything that looks abandoned.

## Branch Memory Snapshot — 2026-03-20

### Healthy / intentional

- `main` tracks `origin/main`
- `agent/manga-mode-clean` is a clean one-commit branch from `origin/main`
- `agent/pearl-github` is a clean one-commit branch from `origin/main`
- `codex/pearl-news-cleanup` is a small diverged branch (`1 behind / 1 ahead` vs `origin/main`)

### High-risk / cleanup candidates

- `agent/manga-mode`
  - `202` commits ahead of `origin/main`
  - wrong-base branch
  - should not be pushed
  - keep only if needed for local recovery/reference; otherwise delete after confirming nothing unique remains

- `codex/runtime-consolidation`
  - `199` commits ahead of `origin/main`
  - local branch is also `34` commits ahead of `origin/codex/runtime-consolidation`
  - not safe for blind merge
  - must be audited before any merge or push

- `codex/pearl-news-full-qa-v2`
  - upstream is gone
  - local branch should be either rehomed, archived, or deleted after review

- `preflight/runtime-merge-check`
  - behind upstream by `144`
  - clearly a worktree/helper branch, not active development truth

### Worktree clutter

- Multiple `worktree-agent-*` branches are fully merged into `origin/main`
- They are likely safe local cleanup candidates once their linked worktrees are no longer needed

### Local dirt observed during audit

- Untracked: `11.txt`
- Untracked directory: `config/musicians/`
- Untracked temp file: `scripts/video/test_write.tmp`

These are not part of Pearl_GitHub, but they do mean the working tree is not pristine.

## Pearl_GitHub Operating Posture

When in doubt:

1. Check ancestry before checking diff size
2. Check branch contents before trusting branch names
3. Check tool existence before following scripted instructions
4. Prefer recovery branches from `origin/main`
5. Treat stale local branches and worktree branches as debt until explicitly cleaned

## Cleanup Memory — 2026-03-20 / 2026-03-21 verification

Verified current end state after cleanup:

- only one live worktree remains: the main repo checkout
- only four local branches remain:
  - `main`
  - `codex/runtime-consolidation`
  - `codex/pearl-news-cleanup`
  - `codex/next-dev-clean`
- the previously merged remote branches were deleted successfully:
  - `origin/codex/fix-wp-site-url-normalization`
  - `origin/codex/harden-pearl-news-pipeline`

Operational lessons:

- do not trust pasted cleanup summaries without re-running `git branch -vv`, `git worktree list --porcelain`, and merged/unmerged remote branch checks
- on this repo, `scripts/git/push_guard.py` may be absent even though `ps.txt` references it
- `scripts/ci/preflight_push.sh` should be invoked with `bash`
- `git branch -r --merged origin/main` and `git branch -r --no-merged origin/main` are the fastest safe branch cleanup inventory pair
- local `main` can look "healthy enough" while still being unsuitable for direct work because of autobackup commits and unrelated local modifications

Ongoing state tracking:

- use `docs/PEARL_GITHUB_STATE.md` as the fast resume/checklist file
- update it whenever branch inventory, Colab verification status, or next actions materially change
- for very large QA catalog runs, prefer a shardable GitHub workflow on self-hosted runners instead of one local monolith
- the max-quality catalog path is teacher-shard + regular-shard oriented, with artifacts uploaded per shard
- for continuous repo hygiene, prefer `scripts/git/hourly_repo_alignment.sh` over ad hoc manual cleanup; it writes a report trail under `artifacts/governance/repo_alignment/`

Latest verified state change:

- PR #24 merged on 2026-03-21T07:35:43Z
- local `main` was repaired by saving autobackup commits to `codex/main-autobackup-20260320-2124` and resetting `main` to `origin/main`
- PR #25 merged on 2026-03-21T07:49:08Z
- local `main` was then fast-forwarded again and now matches `origin/main`
- Step 10 PDF export was visibly confirmed in thread, and the user explicitly confirmed Colab Steps 1-13 are done
- the remaining 10 remote `codex/*` branches were dispositioned into `delete`, `harvest`, and `keep-open` buckets in `docs/BRANCH_DISPOSITION_2026_03_20.md`
- a local-only credentials source may exist at `docs/all_credentials.txt`; agents should use `scripts/integrations/intake_all_credentials_local.sh`, avoid echoing secrets, and never try random username/password combinations across services
- for messaging work, agents should run `scripts/integrations/report_messaging_requirements_local.sh` before setup or send attempts so missing API tokens, recipient IDs, and handles are explicit
- PR #31 merged on 2026-03-21T21:34:27Z and placed the AI Manga Dharma system on `main` as a 14-document spec suite under `specs/`; future manga work should start from `specs/AI_MANGA_PIPELINE_SUMMARY.md` and `specs/README.md`
- manga implementation resumed safely on `agent/manga-pipeline-kernel`, a clean branch from `origin/main`, instead of the dirty local `main` checkout
- the first implementation slice is intentionally kernel-first: config-backed archetypes/layouts, deterministic visual prompt compilation, and a seed teaching-library override path
- use `docs/MANGA_IMPLEMENTATION_OUTLINE.md` as the high-level manga implementation map so future agents keep the work slice-based instead of jumping directly into orchestration
- the next safe manga step is reuse-before-render: export `panel_prompts.json`, resolve assets from a manga bank first, and only then send unresolved panels to the free Colab path
- ComfyUI remains planned but not wired; free Colab + diffusers is still the validated render path in repo today
- PR #21 / `codex/runtime-consolidation` was re-audited on 2026-03-22 and confirmed to be a harvest-only branch:
  - about `22,611` changed paths
  - `199 ahead / 12 behind` vs `origin/main`
  - only `17` non-backup commits worth reviewing
  - source of truth for extraction order is `docs/RUNTIME_CONSOLIDATION_HARVEST_PLAN_2026_03_22.md`

Additional operating lesson:

- when a branch is this large, stop using raw PR state as the decision artifact
- compute:
  - ahead/behind
  - top-level changed-path counts
  - non-backup commit list
- then convert the branch into bucketed harvest PRs instead of trying to "fix the conflicts"
- Pearl_GitHub now has an hourly autopilot implementation branch that can:
  - merge clean PRs
  - backup and hard-sync local `main` to `origin/main`
  - prune stale local branches with gone upstreams
  - write JSON and Markdown reports for each cycle
