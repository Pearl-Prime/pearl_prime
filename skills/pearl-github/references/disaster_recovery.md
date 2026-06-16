# Pearl_GitHub — Disaster Recovery Runbook

Recovery procedures for the most common git failure modes in the Phoenix Omega
repo. This runbook is the extracted, full-length version of `SKILL.md` STEP 6;
the skill keeps a one-line pointer here. Work top-to-bottom: identify the
scenario, run the listed commands, then re-run preflight (STEP 0) before any
push. When in doubt, prefer cherry-picking to a clean branch from `origin/main`
over force-fixing the current branch.

### Scenario: Push hangs / times out
```bash
# Kill and retry with safe_push (has exponential backoff)
scripts/git/safe_push.sh origin <branch>
```

### Scenario: Branch diverged from main
```bash
git fetch origin
git rev-list --left-right --count origin/main...HEAD
# If diverged: rebase or cherry-pick to clean branch
git checkout -b agent/<task>-clean origin/main
git cherry-pick <commit1> <commit2> ...
```

### Scenario: Accidentally committed on main
```bash
# DO NOT push. Create a branch with your commit, then reset main.
git branch rescue-$(date +%Y%m%d)
git checkout main
git reset --hard origin/main
git checkout rescue-$(date +%Y%m%d)
# Push the rescue branch instead
```

### Scenario: Corrupted index
```bash
rm -f .git/index.lock .git/index
git read-tree HEAD
git checkout -f HEAD
```

### Scenario: Need to split an oversized commit
```bash
# Soft reset to unstage
git reset --soft HEAD~1
# Stage and commit in smaller chunks (max 15 files, 1000 lines per commit)
git add file1.py file2.py
git commit -m "feat(scope): first chunk"
git add file3.py file4.py
git commit -m "feat(scope): second chunk"
```
