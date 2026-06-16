# Local launchd agents for Phoenix Omega operations

## com.ahjan.phoenix_omega.worktree_cleanup

Daily auto-cleanup of stale local worktrees. Runs every day at **06:00 local time**.

### What it does

- Calls `scripts/ops/worktree_cleanup_audit.sh` to inventory worktrees
- Auto-deletes the SAFE class only:
  - `pushed=synced AND uncommit=0` (work is on origin)
  - `pushed=LOCAL_ONLY AND merged-to-main=yes AND uncommit=0` (work is in main)
- **NEVER touches:** current worktree, main repo, uncommitted work, LOCAL_ONLY with unpushed commits, diverged worktrees, or locked worktrees
- Tag-archives each deleted branch as `archive/<branch>-YYYY-MM-DD` (pushed to origin) so the work is recoverable
- Logs every run to `artifacts/cleanup_logs/YYYY-MM-DD.log`

### Recover an archived branch

```bash
# List archives
git tag -l 'archive/*'

# Restore as a fresh branch
git fetch origin
git checkout -b recovered/<name> archive/<branch>-<date>
```

### Install

```bash
cp scripts/ops/launchd/com.ahjan.phoenix_omega.worktree_cleanup.plist \
   ~/Library/LaunchAgents/

# Load it (modern syntax)
launchctl bootstrap gui/$(id -u) \
   ~/Library/LaunchAgents/com.ahjan.phoenix_omega.worktree_cleanup.plist

# Confirm
launchctl print gui/$(id -u)/com.ahjan.phoenix_omega.worktree_cleanup
```

### Test manually before trusting the schedule

```bash
# Dry-run inspection
bash scripts/ops/worktree_cleanup_audit.sh
cat /tmp/wt_cleanup.verify.txt

# Full daily run (will actually delete safe worktrees)
bash scripts/ops/worktree_cleanup_daily.sh
tail -50 artifacts/cleanup_logs/$(date -u +%Y-%m-%d).log
```

### Disable

```bash
launchctl bootout gui/$(id -u)/com.ahjan.phoenix_omega.worktree_cleanup
rm ~/Library/LaunchAgents/com.ahjan.phoenix_omega.worktree_cleanup.plist
```

### Trigger manually (force run now)

```bash
launchctl kickstart -k gui/$(id -u)/com.ahjan.phoenix_omega.worktree_cleanup
```

### Logs

- `artifacts/cleanup_logs/YYYY-MM-DD.log`     — per-day run log (script output)
- `artifacts/cleanup_logs/launchd.stdout.log` — launchd stdout (rare; for diagnostics)
- `artifacts/cleanup_logs/launchd.stderr.log` — launchd stderr (rare; for diagnostics)

### Safety guarantees

This automation will not delete a worktree if:
- It is the current working tree
- It is `/Users/ahjan/phoenix_omega` (the main repo)
- It has ANY uncommitted file changes (`git status --porcelain` non-empty)
- Its branch is LOCAL_ONLY with commits not in `origin/main`
- Its branch has diverged from origin
- It is `locked` (run the audit script manually if you want to clean locked worktrees)

For the cloud side (origin branches), see `.github/workflows/cleanup-stale-worktrees.yml`.
