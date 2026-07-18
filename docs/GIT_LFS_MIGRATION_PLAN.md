# Git LFS Migration Plan — phoenix_omega_v4.8

**Date:** 2026-04-10
**Author:** Pearl_Dev + Pearl_GitHub
**PROJECT_ID:** proj_state_convergence_20260328
**Authority:** artifacts/audit/repo_size_audit.md

---

## What Will Be Tracked by LFS

| Pattern | Current Count | Current Size | Reason |
|---------|--------------|-------------|--------|
| *.mp3 | 611 | 320 MB | Audio assets (audiobook samples, SFX, podcast), binary, can't diff |
| *.wav | 48 | 87 MB | Raw audio, reference clips, binary |
| *.m4a | 0 | 0 | Future audio format |
| *.ogg | 0 | 0 | Future audio format |
| *.flac | 0 | 0 | Future lossless audio |
| *.mp4 | 47 | 21 MB | Video renders (YouTube, TikTok), binary |
| *.mov | 0 | 0 | Future video format |
| *.avi | 0 | 0 | Future video format |
| *.webm | 0 | 0 | Future web video format |
| *.png | 406 | 179 MB | Cover art, manga panels, screenshots, binary |
| *.jpg | 38 | 0.5 MB | Cover art, artwork, binary |
| *.jpeg | 4 | 0.8 MB | Same as jpg |
| *.zip | 44 | 0.3 MB | Archives, binary |
| *.lpf | 1 | 290 MB | Logic Pro project files, binary |
| *.pdf | 3 | 9 MB | Generated documents, binary |
| *.xlsx | 1 | 0.03 MB | Spreadsheets (investor DD), binary |
| *.xls | 0 | 0 | Future spreadsheet format |
| *.docx | 28 | 0.8 MB | Word documents (specs), binary |
| *.safetensors | 0 | 0 | Guard against model weight commits |
| *.bin | 0 | 0 | Guard against binary blob commits |
| *.onnx | 0 | 0 | Guard against ML model commits |
| *.pt | 0 | 0 | Guard against PyTorch model commits |
| *.iso | 0 | 0 | Guard against OS image commits (pearl_star incident) |
| *.deb | 0 | 0 | Guard against package commits (pearl_star incident) |

**Total LFS-eligible in working tree:** ~908 MB across 1,231 files

---

## What Will NOT Be Tracked by LFS

| Pattern | Reason |
|---------|--------|
| *.yaml / *.yml | Text config, diffable, small |
| *.json | Data files, text, diffable |
| *.jsonl | Log/data files, text |
| *.py | Python code |
| *.md | Documentation |
| *.html | Web pages (text, even if large) |
| *.js / *.jsx | JavaScript code |
| *.ts / *.mts / *.cts | TypeScript code |
| *.css | Stylesheets |
| *.txt | Text files |
| *.sh | Shell scripts |
| *.toml | Config files |
| *.swift | Swift code |
| *.csv | Data files, text, diffable |
| *.rtf | Text-ish (gitignored anyway) |
| *.svg | XML-based vector graphics (text, diffable) |
| *.webp | Only 5 files, 0.3 MB total — too small to matter |
| *.gif | 0 files currently |

---

## Expected Impact

### Immediate (this PR — no history rewrite)

| Metric | Before | After |
|--------|--------|-------|
| New binary commits use LFS? | No | **Yes** |
| Working tree size | 1.4 GB | 1.4 GB (unchanged) |
| Clone size | ~56 GB | ~56 GB (unchanged — history not rewritten) |
| Future growth rate | Linear with binaries | Reduced (LFS pointers only) |

### After History Rewrite (scheduled maintenance)

| Metric | Before | After (estimated) |
|--------|--------|-------------------|
| Clone size | ~56 GB | **~1.5 GB** (text only) |
| `.git/` size | 59 GB | ~2 GB |
| pearl_star/ blobs removed | 0 | ~7 GB freed |
| Video render blobs migrated | 0 | ~2 GB to LFS |
| Cover art blobs migrated | 0 | ~500 MB to LFS |
| Audio blobs migrated | 0 | ~1 GB to LFS |

### After Worktree Cleanup (separate action)

| Metric | Before | After |
|--------|--------|-------|
| .claude/worktrees/ | 33 GB | ~0 (or 1-2 GB if keeping active) |
| Total repo on disk | 93 GB | ~3-4 GB |

---

## Migration Steps

### Phase A: Immediate — LFS Forward-Tracking (this PR)

1. Install Git LFS: `brew install git-lfs && git lfs install`
2. Create `.gitattributes` with LFS patterns (see below)
3. Commit `.gitattributes` — all future binary commits automatically use LFS
4. No history rewrite, no force push, no disruption

### Phase B: Scheduled — History Rewrite (requires maintenance window)

**Prerequisites:**
- All open PRs merged or closed
- All collaborators notified — they must re-clone after
- Backup: `cp -r .git .git.backup`

**Steps:**

```bash
# 1. Dry run — see what would change
git lfs migrate info --everything \
  --include="*.mp3,*.mp4,*.wav,*.png,*.jpg,*.jpeg,*.zip,*.lpf,*.pdf,*.xlsx,*.docx,*.iso,*.deb,*.m4a,*.ogg,*.flac,*.mov,*.avi,*.webm"

# 2. Execute migration
git lfs migrate import --everything \
  --include="*.mp3,*.mp4,*.wav,*.png,*.jpg,*.jpeg,*.zip,*.lpf,*.pdf,*.xlsx,*.docx,*.iso,*.deb,*.m4a,*.ogg,*.flac,*.mov,*.avi,*.webm"

# 3. Aggressive GC to reclaim space
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 4. Force push (DANGEROUS — owner approval required)
git push --force-with-lease origin main

# 5. All collaborators must re-clone
```

### Phase C: Worktree Cleanup (owner action)

```bash
# List worktrees
git worktree list

# Remove stale worktrees
git worktree prune

# Or manually remove Claude worktrees
rm -rf .claude/worktrees/recursing-lalande/
rm -rf .claude/worktrees/dazzling-germain/
rm -rf .claude/worktrees/unruffled-sanderson/
# ... etc.
```

---

## History Bloat Root Causes (for prevention)

| Incident | Size | What Happened | Prevention |
|----------|------|---------------|------------|
| pearl_star/ ISO commit | 6 GB | Ubuntu ISO committed to repo | `.gitignore` + LFS + pre-commit hook |
| pearl_star/ .deb packages | ~700 MB | Linux packages committed | `.gitignore` + LFS |
| Video renders (YouTube/TikTok) | ~2 GB | MP4 files committed, revised, deleted | `.gitignore` for artifacts/videos/ + LFS |
| Cover art revisions | ~500 MB | Large PNGs committed across revisions | LFS (already tracked going forward) |
| Multiple revisions of same binary | Compounds | Same file committed 2-3 times = 2-3× storage | LFS stores 1 copy per version efficiently |

---

## .gitignore Additions Recommended

```
# OS images and packages (never commit)
*.iso
*.deb
*.rpm
pearl_star/
```
