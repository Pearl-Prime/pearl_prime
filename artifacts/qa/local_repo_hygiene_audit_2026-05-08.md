# Local Repo Hygiene Audit — 2026-05-08

**Agent:** Pearl_DevOps
**Project:** PRJ-PEARL-DEVOPS-LOCAL-HYGIENE
**Subsystem:** pearl_devops
**Authority docs:** `docs/GITHUB_OPERATIONS_FRAMEWORK.md`, `docs/SESSION_UNITY_PROTOCOL.md`, `skills/pearl-github/references/git_system.md`, `skills/pearl-github/references/repo_memory.md`, `CLAUDE.md`
**Local host:** Ahjan's Mac (`/Users/ahjan/phoenix_omega`)
**Audit window (UTC):** 2026-05-08 ~01:50Z – 03:25Z
**Snapshot caveat:** Live operations from at least 4 concurrent agent sessions (other `git worktree add`, `git checkout -B`, `git reset --hard`) and the IDE-driven git workers (74+ concurrent `git status --porcelain` processes via Cursor/Xcode plugins) were active during the audit. Worktree state may have changed after this snapshot.

---

## Scope

This audit covers two local-repo hygiene issues on the canonical checkout at `/Users/ahjan/phoenix_omega`:

- **PART 1** — Stale `.git/index.lock`
- **PART 2** — Stray worktrees under `/Users/ahjan/phoenix_omega_*_wt` not visible to `git worktree list` from the canonical repo

This audit is **read-mostly**: PART 1 removed exactly one stale empty lock file. PART 2 only inspected — **no worktree was deleted in this session**. Removals are deferred to operator approval in a follow-up turn.

---

## PART 1 — `.git/index.lock`

### Pre-removal observations

| Probe | Result |
|---|---|
| `lsof /Users/ahjan/phoenix_omega/.git/index.lock` | exit 1, **no holder** (no open file handle from any process) |
| `ls -la` | `-rw-r--r--@ 1 ahjan staff 0 May 8 02:57 .git/index.lock` (size 0, perms 644) |
| `stat` mtime | `2026-05-08 02:57:45` local (epoch `1778176665`) |
| Now | `2026-05-08 10:54` local (epoch `1778205266`) |
| Lock age | **≈ 7h 56m** (well over the 30-minute stale threshold) |
| Live `git` processes referencing canonical repo | 157 (74 of which are `git status --porcelain` issued by Cursor/Xcode `gitWorker.js`) — none holding the lock per `lsof` |

**Verdict:** Empty, abandoned lock with no holder, age ~8 hours → **stale**. Safe to remove per the criteria in the task plan.

### Removal action

```text
$ rm -f /Users/ahjan/phoenix_omega/.git/index.lock
REMOVED_OK
$ ls -la /Users/ahjan/phoenix_omega/.git/index.lock
ls: /Users/ahjan/phoenix_omega/.git/index.lock: No such file or directory
```

### Post-removal verification

| Probe | Result | Latency |
|---|---|---|
| `git rev-parse HEAD` (canonical) | `e078e3e968d4e7faef4010bc73e53da6cc2c74ea` | < 1s |
| `git rev-parse --abbrev-ref HEAD` | `agent/teacher-showcase-names-video-carousel` | < 1s |
| `git stash list` | returned 20+ entries (sample: `stash@{0}: On docs/session-handoff-2026-05-04: qi brand_lora direction B`, …, `stash@{19}: On agent/free-tier-tts-hardening-20260427: tts-parallel-agent-files-do-not-touch`) | ≈ 4s |
| `git fetch origin --dry-run` | exit 0 | ≈ 16s |
| `git status --short --branch \| head -50` | **inconclusive** — backgrounded, killed at 532s without producing output | n/a |

**Why `git status` was inconclusive:** the canonical working tree is being scanned by 74 concurrent IDE-driven `git status --porcelain` invocations (PPID = `76215`, the Cursor `gitWorker.js`). My single `git status --short --branch` was queued behind them on filesystem and `index.lock`-acquisition contention. This is **IDE load**, not a lock pathology — `git rev-parse`, `git stash list`, and `git fetch --dry-run` (which do not need the index lock) all returned promptly.

### Post-removal lock churn (informational, not stale)

A new `index.lock` reappeared at `2026-05-08 11:05:15` local (≈ 8 minutes after removal). It was held by a **live** holder:

```text
$ lsof /Users/ahjan/phoenix_omega/.git/index.lock
COMMAND  PID  USER  FD  TYPE  DEVICE  SIZE/OFF  NODE      NAME
git      28791 ahjan 3u  REG   1,16    0         52058231  /Users/ahjan/phoenix_omega/.git/index.lock

$ ps -p 28791
 PID  PPID ELAPSED STAT COMMAND
28791 76215  04:34   S   git -c core.quotepath=false ... status --porcelain
```

PPID `76215` is Cursor's `gitWorker.js`. The IDE periodically refreshes the index, which legitimately holds `index.lock` for the duration of the refresh. A second observation at `11:13` showed yet another lock held by a different live `git` PID, then released. This churn is **expected and normal** — the IDE creates and releases the lock continuously. Pearl_DevOps left this active lock alone.

### PART 1 disposition

- **Original stale lock:** ✅ removed.
- **No active git process was disturbed.**
- **Repo lock health post-removal:** Light operations (`rev-parse`, `stash list`, `fetch --dry-run`) all OK. Index-touching operations remain bounded by IDE contention but no longer blocked by an abandoned holder.

---

## PART 2 — Worktree audit (`/Users/ahjan/phoenix_omega_*_wt`)

### Methodology

1. `git -C /Users/ahjan/phoenix_omega worktree list --porcelain` → captured the canonical repo's tracked worktrees.
2. `ls -d /Users/ahjan/phoenix_omega_*_wt` → captured all on-disk paths matching the `_wt` glob.
3. Diff: any on-disk path not in the canonical worktree list is an **orphan-relative-to-canonical**.
4. For each orphan, inspected the `.git` pointer (gitfile) to see whether it is genuinely abandoned or simply tracked by a different repo.
5. For the orphan, ran `git status --short` to determine clean vs. dirty.

### Canonical `git worktree list` (filtered to `/Users/ahjan/phoenix_omega_*_wt` paths)

Nine paths are tracked by the canonical repo:

| # | Path | Branch | Notes |
|---|---|---|---|
| 1 | `phoenix_omega_cosyvoice_audit_wt` | (detached, `fc905c95`) | `locked initializing` — checkout in progress at audit time |
| 2 | `phoenix_omega_genre_lora_skip_wt` | `agent/genre-lora-cross-test-skip-20260507` | active |
| 3 | `phoenix_omega_lettering_v2_wt` | `agent/manga-lettering-v2-20260507` | active |
| 4 | `phoenix_omega_loc_30s_batch_wt` | `agent/loc-30s-batch-12-20260508` | `locked initializing` |
| 5 | `phoenix_omega_loc_s7_wt` | `agent/localization-s7-clean-isolation-20260507` | active |
| 6 | `phoenix_omega_maat_prose_wt` | `agent/maat-audiobook-ch1-prose-20260508` | active |
| 7 | `phoenix_omega_overlay_phase1_wt` | `agent/overlay-enforcement-phase-1-20260508` | `locked initializing` |
| 8 | `phoenix_omega_pearl_github_wt` | `agent/manga-v2-scope-supersede-header` | active |
| 9 | `phoenix_omega_qi_foundation_recon_wt` | `agent/qi-foundation-canonical-reconciliation-20260508` | active |

(Other entries in `git worktree list` — under `phoenix_omega/.claude/worktrees/...` and `~/.cursor/phoenix_canary_wt` — are out of scope for this audit, which is restricted to the `/Users/ahjan/phoenix_omega_*_wt` glob.)

### On-disk paths matching `/Users/ahjan/phoenix_omega_*_wt`

Ten paths exist on disk:

```
/Users/ahjan/phoenix_omega_cosyvoice_audit_wt
/Users/ahjan/phoenix_omega_genre_lora_skip_wt
/Users/ahjan/phoenix_omega_lettering_v2_wt
/Users/ahjan/phoenix_omega_loc_30s_batch_wt
/Users/ahjan/phoenix_omega_loc_s7_wt
/Users/ahjan/phoenix_omega_maat_prose_wt
/Users/ahjan/phoenix_omega_overlay_phase1_wt
/Users/ahjan/phoenix_omega_pearl_github_wt
/Users/ahjan/phoenix_omega_pearl_star_install_prep_wt    ← not in canonical worktree list
/Users/ahjan/phoenix_omega_qi_foundation_recon_wt
```

### Diff: orphan-relative-to-canonical

**One** on-disk `_wt` path is absent from `git worktree list` run inside `/Users/ahjan/phoenix_omega`:

- `/Users/ahjan/phoenix_omega_pearl_star_install_prep_wt`

### Orphan deep-dive: `phoenix_omega_pearl_star_install_prep_wt`

| Field | Value |
|---|---|
| Path | `/Users/ahjan/phoenix_omega_pearl_star_install_prep_wt` |
| `.git` (gitfile) contents | `gitdir: /Users/ahjan/phoenix_omega_gitops_tmp/.git/worktrees/phoenix_omega_pearl_star_install_prep_wt` |
| Backing admin dir | `/Users/ahjan/phoenix_omega_gitops_tmp/.git/worktrees/phoenix_omega_pearl_star_install_prep_wt` (exists; HEAD, commondir, gitdir, index, FETCH_HEAD, ORIG_HEAD all present) |
| Branch | `refs/heads/agent/pearl-star-install-prep-20260507` |
| HEAD | `58de6ff22eb4f22f90adad6975b60369b1315aff` |
| Last mtime (working tree root) | `May 7 22:00:44` (≈ 13h before audit) |
| `git status --short` from inside the path | exit 0, **empty output → CLEAN** |
| `git -C /Users/ahjan/phoenix_omega_gitops_tmp worktree list` | **lists this worktree** (it is tracked by the *secondary* repo at `phoenix_omega_gitops_tmp`, not by canonical) |

**Classification:** **tracked-by-secondary-repo** (NOT a true orphan, NOT safe-to-prune without coordinating the secondary repo).

The reason it doesn't appear in `git worktree list` from `/Users/ahjan/phoenix_omega` is that it was created from a *separate* clone at `/Users/ahjan/phoenix_omega_gitops_tmp` (whose own `origin` points at the local canonical repo, not GitHub). It is fully wired up as a worktree of that secondary clone. No git data is lost; this is functioning normally relative to its actual owner repo.

### Reported orphan from operator: `phoenix_omega_catalog_800_v2_wt`

| Probe | Result |
|---|---|
| `ls -la /Users/ahjan/phoenix_omega_catalog_800_v2_wt` | `No such file or directory` |
| `git worktree list` (canonical) | absent |
| Disposition | **already gone** — nothing to prune |

**Classification:** **already-removed** (no action required).

### Quick clean/dirty status of tracked `_wt` paths (advisory, not in mandatory scope)

To give the operator a complete picture, the table below combines the canonical `git worktree list` output with the on-disk metadata captured during the audit. Per task spec, only orphans require a `git status` probe; tracked worktrees were not actively probed for dirty state to avoid further lock contention. `locked initializing` is a git-managed lock used by `git worktree add` while the checkout is still being unpacked — those wts were mid-creation by other agents during the audit window.

| Path (under `/Users/ahjan/`) | Classification | Tracked by | Last mtime | Recommendation |
|---|---|---|---|---|
| `phoenix_omega_cosyvoice_audit_wt` | tracked, init-locked | canonical | May 8 11:00 | leave alone (in-flight checkout by another agent) |
| `phoenix_omega_genre_lora_skip_wt` | tracked, active | canonical | May 8 02:40 | leave alone (active workstream) |
| `phoenix_omega_lettering_v2_wt` | tracked, active | canonical | May 8 03:14 | leave alone (active workstream) |
| `phoenix_omega_loc_30s_batch_wt` | tracked, init-locked | canonical | May 8 10:58 | leave alone (in-flight checkout by another agent) |
| `phoenix_omega_loc_s7_wt` | tracked, active | canonical | May 8 03:02 | leave alone (active workstream) |
| `phoenix_omega_maat_prose_wt` | tracked, active | canonical | May 8 02:42 | leave alone (active workstream) |
| `phoenix_omega_overlay_phase1_wt` | tracked, init-locked | canonical | May 8 10:59 | leave alone (in-flight checkout by another agent) |
| `phoenix_omega_pearl_github_wt` | tracked, active | canonical | May 7 14:41 | leave alone (active workstream) |
| `phoenix_omega_pearl_star_install_prep_wt` | **orphan-vs-canonical / tracked-by-secondary** | `phoenix_omega_gitops_tmp` (clean) | May 7 22:00 | **DO NOT prune unilaterally**: this is an active worktree of the secondary `gitops_tmp` clone. If `gitops_tmp` is itself disposable, prune both together via `git -C /Users/ahjan/phoenix_omega_gitops_tmp worktree remove /Users/ahjan/phoenix_omega_pearl_star_install_prep_wt`. |
| `phoenix_omega_catalog_800_v2_wt` (operator-reported) | **already removed** | — | — | nothing to do |

**Orphan count vs canonical worktree list:** **1** (`phoenix_omega_pearl_star_install_prep_wt`).
**Safe-to-prune count (without operator coordination):** **0**. The single orphan is alive in the secondary repo; pruning it without first removing it from `gitops_tmp` would leave a dangling admin entry there.

### Out-of-scope but adjacent dirs (informational)

These sibling paths matched `phoenix_omega_*` but **not** the `_wt` glob, so they are not subject to this audit. Listed only so the operator can decide whether a follow-up audit is needed:

| Path | Last mtime | Notes |
|---|---|---|
| `/Users/ahjan/phoenix_omega_gitops_tmp` | May 7 19:52 | Secondary clone of canonical (its `origin` = `/Users/ahjan/phoenix_omega`). Owns the orphan above. |
| `/Users/ahjan/phoenix_omega_pearl_prime_contract` | Mar 24 08:26 | Old (~6 weeks). Possibly stale. |
| `/Users/ahjan/phoenix_omega_preflight_runtime` | Mar 17 23:40 | Old (~7 weeks). Possibly stale. |

---

## Recommendations (for operator approval)

1. **Lock churn** — no action. The IDE-driven lock churn is normal; the only stale lock at audit start has been removed.
2. **Orphan worktree (`phoenix_omega_pearl_star_install_prep_wt`)** — coordinated cleanup, **not** a unilateral `rm -rf`. Suggested sequence (operator-run, after confirming the secondary is no longer needed):
   ```bash
   git -C /Users/ahjan/phoenix_omega_gitops_tmp status --short
   git -C /Users/ahjan/phoenix_omega_gitops_tmp worktree remove /Users/ahjan/phoenix_omega_pearl_star_install_prep_wt
   # if also retiring the secondary clone:
   rm -rf /Users/ahjan/phoenix_omega_gitops_tmp
   ```
3. **Already-removed report (`phoenix_omega_catalog_800_v2_wt`)** — confirm no admin entry remains:
   ```bash
   git -C /Users/ahjan/phoenix_omega worktree prune --verbose
   ls -la /Users/ahjan/phoenix_omega/.git/worktrees/ | grep -i catalog_800 || echo "no admin entry"
   ```
4. **Out-of-scope siblings** — schedule a follow-up audit for `phoenix_omega_gitops_tmp`, `phoenix_omega_pearl_prime_contract`, `phoenix_omega_preflight_runtime` (mtimes range from 6–7 weeks back).
5. **IDE git contention** — consider lowering Cursor's git-refresh frequency or scoping its watcher; 74 concurrent `git status --porcelain` invocations per minute create real lock contention and slow down all agent git work in this checkout.

---

## Out-of-scope confirmation (per STARTUP_RECEIPT)

This session did **NOT**:

- delete any worktree with uncommitted work (none had uncommitted work; nothing was deleted regardless),
- delete any tracked branch,
- push anything other than this audit branch,
- modify any config (`git config`, repo config, or workflow config).

This session **DID**:

- remove exactly one stale empty `.git/index.lock` file (PART 1),
- read worktree state (PART 2),
- write exactly this single audit document at `artifacts/qa/local_repo_hygiene_audit_2026-05-08.md`.

---

## Hand-off

**HANDOFF_TO:** operator
**NEXT_ACTION:** review recommendations §2 and §4. Approve (or modify) coordinated pruning of `phoenix_omega_pearl_star_install_prep_wt` + (optionally) the secondary `phoenix_omega_gitops_tmp` clone in a follow-up Pearl_DevOps turn.
