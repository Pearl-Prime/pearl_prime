# Repo cleanup process for Phoenix Omega
_Exported on 4/16/2026 at 19:23:25 GMT+8 from Cursor (3.1.15)_

---

**User**

You are Pearl_GitHub + Pearl_Dev + Pearl_PM (repo hygiene). Obey docs/SESSION_UNITY_PROTOCOL.md (STARTUP_RECEIPT / CLOSEOUT_RECEIPT), CLAUDE.md, docs/GITHUB_GOVERNANCE.md, docs/GITHUB_OPERATIONS_FRAMEWORK.md, docs/OWNERSHIP_MATRIX.md, docs/DOCS_INDEX.md.
OWNER TASK
Clean up the Phoenix Omega repo: starte with laptop local. remove and delete obvious junk, redundant test files, and  archive decommissioned paths. Prefer **delete** for generated/cache cruft and **zip + remove originals** (or move to `salvage/` / `artifacts/archive/`) for large decommissioned trees you can prove unused. Work **step-by-step with the owner**: present an inventory and get explicit approval before bulk deletes.
PROJECT_ID
proj_state_convergence_20260328
SUBSYSTEM
repo coordination (Pearl_GitHub primary); touch other subsystems only when paths are clearly junk under their trees.
AUTHORITY_DOCS
docs/SESSION_UNITY_PROTOCOL.md; docs/GITHUB_GOVERNANCE.md; docs/GITHUB_OPERATIONS_FRAMEWORK.md; docs/OWNERSHIP_MATRIX.md; docs/DOCS_INDEX.md; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv; artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv
NON-NEGOTIABLES
1) **Mass deletion gate:** Before deleting **>50 files** in one change (or any PR), STOP and get **explicit owner approval** (CLAUDE.md / governance: catastrophic deletion incident). Report `git diff --stat` / file count.
2) **Do not** delete or gut `tests/` that are still referenced by CI or `pytest` discovery without proving zero references and owner OK.
3) **Do not** delete `config/**`, `phoenix_v4/**`, `scripts/ci/**`, `.github/workflows/**`, or authority specs because they “look old” — only after a doc or code reference search shows decommissioned + owner signoff.
4) **Never** delete secrets, Keychain docs, or `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` targets.
5) Prefer **git rm** for tracked junk; for untracked-only, document paths and use owner-approved `rm` / archive zip.
PHASE 0 — Inventory (read-only)
- Scan for: duplicate `test_*.py` outside canonical `tests/`; `*_test.py` orphans; `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `*.pyc`, `*.pyo`; stale `.claude/worktrees/*`, `_wt_*` if repo policy allows; huge `node_modules` if accidentally committed; duplicate logs under `artifacts/**`; obvious `tmp/`, `scratch/`, `old_*`, `deprecated_*` **only if** no imports reference them (`rg` / `pytest --collect-only`).
- Produce **one** machine-readable list: `artifacts/coordination/REPO_CLEANUP_CANDIDATES_2026.tsv` (columns: path, category(cache|duplicate_test|decommissioned|artifact_junk|uncertain), suggested_action(delete|zip_archive|keep|ask_owner), evidence_one_line, tracked_untracked).
PHASE 1 — Owner review
- Paste summary table (top 30 rows + counts by category). Owner replies **approve category X** or **path exceptions**. Do nothing destructive until approved.
PHASE 2 — Safe automatic wins (low risk)
- Delete **untracked** cache dirs only if standard and not in .gitignore by mistake: `__pycache__`, `.pytest_cache` under workspace (not in venv paths). Re-run a **small** pytest slice or `python -m compileall` if you touched Python layout.
- **Do not** run `git clean -fdx` without owner typing the command.
PHASE 3 — Tracked cleanup (approved only)
- **Duplicate / decommissioned tests:** remove only with proof (no collector references, no CI mention). One focused commit per theme.
- **Decommissioned features:** zip tree → `artifacts/archive/<name>_<DATE>.zip` (or `salvage/`) then `git rm` tracked files if owner approved; record zip path in CLOSEOUT.
- **Artifacts:** trim obvious regenerate-able outputs if policy allows; keep pilot/governance evidence paths referenced in ACTIVE_WORKSTREAMS or recent PRs.
PHASE 4 — Git hygiene
- Run push-guard + preflight before push; branch from `origin/main` as `agent/repo-cleanup-<date>`.
- PR description: bullet list of categories removed, file counts, zip locations, risks “none” or documented.
CONFLICT CHECK
Read `ACTIVE_WORKSTREAMS.tsv`; do not delete paths in active `write_scope` rows. If overlap, STOP.
WRITE_SCOPE
artifacts/coordination/REPO_CLEANUP_CANDIDATES_*.tsv; approved paths only under tests/, scripts/, artifacts/, salvage/, docs/ (only if owner approved doc removal); archive zips under artifacts/archive/ or salvage/
OUT_OF_SCOPE
Rewriting product logic; merging unrelated PRs; deleting submodules without owner; touching Pearl News / video flux lanes unless listed as candidates.
STOP / HANDOFF
If uncertain whether something is canonical, mark **ask_owner** — do not delete.
STARTUP_RECEIPT
STARTUP_RECEIPT
AGENT:
TASK:
PROJECT_ID:
SUBSYSTEM:
AUTHORITY_DOCS:
READ_PATH_COMPLETE:
WRITE_SCOPE:
OUT_OF_SCOPE:
BLOCKERS:
READY_STATUS:


---

**Cursor**

Starting Phase 0 (read-only): reading session protocol, active workstreams, and scanning the repo for cleanup candidates.



Gathering inventory: scanning the filesystem and checking git tracking for candidates.



Running targeted inventory scans (git status may be slow on a large repo).



Refining the inventory: 3005 "duplicate_test" entries likely includes legitimate package-local tests. Sampling the TSV and tightening categories.



Regenerating the inventory: rolling up worktree/`_wt_*` test copies into tree-level rows and removing false positives (e.g. `*_test.py` matching scripts).



Regenerating the candidate list: excluding worktree copies (`_wt_*`, `.claude/worktrees/**`) from per-file `duplicate_test` rows and adding tree-level rows with accurate categories.



Calling the missing `walk_tests()` and regenerating.



Writing the final machine-readable TSV from git-backed evidence and disk checks. `__pycache__` count is 0 in the main tree (clean); we still list the pattern for Phase 2.



STARTUP_RECEIPT  
AGENT: Pearl_GitHub + Pearl_Dev + Pearl_PM (repo coordination)  
TASK: Phase 0 repo cleanup inventory + Phase 1 owner review gate (no bulk deletes)  
PROJECT_ID: proj_state_convergence_20260328  
SUBSYSTEM: repo coordination (Pearl_GitHub primary)  
AUTHORITY_DOCS: docs/SESSION_UNITY_PROTOCOL.md; docs/GITHUB_GOVERNANCE.md (required checks / merge rules); docs/GITHUB_OPERATIONS_FRAMEWORK.md (repo identity / workflow map); docs/OWNERSHIP_MATRIX.md; docs/DOCS_INDEX.md (navigation + repo hygiene pointer); artifacts/coordination/ACTIVE_WORKSTREAMS.tsv; artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv; CLAUDE.md (via ps.txt mass-deletion gate)  
READ_PATH_COMPLETE: yes — session minimum set read (SESSION_UNITY_PROTOCOL, ACTIVE_WORKSTREAMS, SUBSYSTEM_AUTHORITY_MAP sample, DOCS_INDEX lead, OWNERSHIP_MATRIX, GITHUB_GOVERNANCE / GITHUB_OPERATIONS_FRAMEWORK headers); deep line-by-line of every governance doc not repeated here  
WRITE_SCOPE: `artifacts/coordination/REPO_CLEANUP_CANDIDATES_2026.tsv` only this session  
OUT_OF_SCOPE: product logic; `config/**`, `phoenix_v4/**`, `scripts/ci/**`, `.github/workflows/**` except coordination notes; Pearl News / video lanes except as listed; any `git rm` / zip / `rm -rf` without owner category approval  
BLOCKERS: none for inventory; `git status` on this workspace can be very slow (large tree) — inventory used `git ls-files`, `du`, and targeted scans  
READY_STATUS: ready — Phase 0 artifact written; Phase 1 awaits your approvals  

---

## Conflict check (`ACTIVE_WORKSTREAMS.tsv`)

No candidate path is slated for **delete** inside an active **`write_scope`** row. **Coordination only:** `brand-wizard-app/node_modules/` touches the same app tree as **`ws_teacher_manga_triptych_20260410`** (active) and **`ws_lfs_setup_20260410`** (active; `.gitignore` / LFS hygiene). Any untrack/remove of `node_modules` must be explicitly approved and planned with those lanes.

---

## Phase 0 — Inventory artifact

Machine-readable list (14 rows + header):

`artifacts/coordination/REPO_CLEANUP_CANDIDATES_2026.tsv`

Evidence highlights:

- **Tracked `test_*.py` outside `tests/`:** exactly **4** files (`git ls-files`), matching a full-repo `find` excluding `.git`, `.claude`, `_wt_*`, venvs → **4** paths.
- **`_test.py` “orphans”:** the only tracked `*_test.py` outside `tests/` are **`scripts/ci/run_rigorous_system_test.py`** and **`scripts/systems_test/run_systems_test.py`** — classified **keep** (harnesses, not pytest orphans).
- **`.claude/worktrees`:** ~**43** subdirs, **`du` ~33G**; **`_wt_beatmap` / `_wt_inj`:** ~**1.2G** each (local snapshots).
- **`brand-wizard-app/node_modules/`:** **6984** tracked files (`git ls-files | wc -l`) — any git removal is **>50 files** → **hard stop** until you explicitly approve (CLAUDE.md / governance).

---

## Phase 1 — Counts by category

| category        | rows | notes |
|-----------------|------|--------|
| artifact_junk   | 4    | includes tracked `node_modules` (needs explicit OK) |
| cache           | 3    | `.pytest_cache`, Vite deps path, `__pycache__` pattern |
| decommissioned  | 2    | `old_chat_specs/`, `old_chats/` — docs still reference `old_chat_specs` |
| duplicate_test  | 4    | alternate test roots only; canonical `tests/` untouched |
| uncertain       | 2    | both **keep** |

---

## Full table (all rows ≤30)

| path | category | suggested_action | tracked_untracked |
|------|----------|------------------|-------------------|
| `.claude/worktrees/` | artifact_junk | ask_owner | untracked |
| `.claude/worktrees/magical-beaver/brand-wizard-app/.vite/deps/` | cache | delete | untracked |
| `_wt_beatmap/` | artifact_junk | zip_archive | untracked |
| `_wt_inj/` | artifact_junk | zip_archive | untracked |
| `.pytest_cache/` | cache | delete | untracked |
| `__pycache__/** (repo main tree)` | cache | delete | mixed |
| `old_chat_specs/` | decommissioned | ask_owner | tracked |
| `old_chats/` | decommissioned | ask_owner | tracked |
| `pearl_prime/tests/test_modular_format_freeze.py` | duplicate_test | ask_owner | tracked |
| `test_pearl_news/test_*.py` (3 files) | duplicate_test | ask_owner | tracked |
| `scripts/ci/run_rigorous_system_test.py` | uncertain | keep | tracked |
| `scripts/systems_test/run_systems_test.py` | uncertain | keep | tracked |
| `brand-wizard-app/node_modules/` | artifact_junk | ask_owner | tracked |

---

## What I did **not** do (by design)

- No **`rm`**, **`git rm`**, **`git clean`**, zips, or commits.
- No changes to **`tests/`** discovery or CI wiring.

---

## What I need from you (Phase 1 approvals)

Reply with explicit lines such as:

- **approve category cache** — I will only remove **untracked** root `.pytest_cache/` and nested `.vite/deps` **after** you confirm worktrees are disposable (or narrow paths).
- **approve category artifact_junk** — specify: **(A)** `.claude/worktrees/` only, **(B)** `_wt_*` only, **(C)** `node_modules` untrack strategy (separate approval; **>50 files**).
- **approve category decommissioned** — only if you accept triage/archival plan for `old_chat_specs/` / `old_chats/` (with doc audit for `old_chat_specs`).
- **approve category duplicate_test** — only after you want migration/consolidation into `tests/` (separate proof PR).

**Path exceptions** — list any row to force **keep**.

---

CLOSEOUT_RECEIPT  
AGENT: Pearl_GitHub + Pearl_Dev + Pearl_PM  
TASK: Repo cleanup Phase 0 inventory + Phase 1 review package  
COMMIT_SHA: no commits  
FILES_WRITTEN: `artifacts/coordination/REPO_CLEANUP_CANDIDATES_2026.tsv`  
FILES_READ: `docs/SESSION_UNITY_PROTOCOL.md`; `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`; `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv`; `docs/DOCS_INDEX.md` (lead); `docs/OWNERSHIP_MATRIX.md`; `docs/GITHUB_GOVERNANCE.md`; `docs/GITHUB_OPERATIONS_FRAMEWORK.md`; `ps.txt` / `CLAUDE.md` (via workspace rules); `docs/REPO_HYGIENE_AND_WORKTREE_CLEANUP.md`  
STATUS: partial — **awaiting owner category/path approvals** before Phase 2–4  
HANDOFF_TO: owner  
NEXT_ACTION: Reply with **approve category X** and **path exceptions**; then I will execute **Phase 2** (low-risk untracked cache only as approved), branch `agent/repo-cleanup-20260414` from `origin/main` if we promote changes to git, and run push-guard + preflight before any push.

---

**User**

How much space did you save me on my laptop local disk?

---

**Cursor**

**None.** That session only produced the inventory file `artifacts/coordination/REPO_CLEANUP_CANDIDATES_2026.tsv` and did not delete, archive, or `git rm` anything. A small amount of disk was **used** for that tiny file (and whatever Cursor/git touched), not freed.

**Potential** space if you later remove what we measured (for your planning only, not done by me):

- `.claude/worktrees/` — about **33 GB** (`du` ~33G)
- `_wt_beatmap/` + `_wt_inj/` — about **1.2 GB** each (~**2.4 GB** total)
- `.pytest_cache/` and nested `.vite/deps` — small unless huge caches

Nothing was reclaimed until you approve categories and run the actual cleanup.

---

**User**

You are Pearl_GitHub + Pearl_Dev. Obey docs/SESSION_UNITY_PROTOCOL.md (STARTUP_RECEIPT / CLOSEOUT_RECEIPT) and CLAUDE.md mass-delete rules.
OWNER TASK — Low-risk repo cleanup only (Brand Wizard in active use)
SCOPE (allowed)
- Delete **untracked** cache only:
  - Repo-root `.pytest_cache/` if present and untracked.
  - **Untracked** `__pycache__/` directories under `phoenix_v4/`, `scripts/`, `tests/`, and `config/` only (no recursion into venvs, `.git`, `node_modules`, or worktrees).
- **Do not** reclaim space from `.claude/worktrees/`, `_wt_*`, or **any path under `brand-wizard-app/`** (including `node_modules/`, `.vite/`, `dist/`, `.cache/`) — owner is actively developing Brand Wizard.
OUT OF SCOPE (hard stop)
- `brand-wizard-app/**` (entire tree — read-only for this session).
- `git rm`, tracked file removal, zip archives, `git clean -fdx`.
- `old_chat_specs/`, `old_chats/`, duplicate test migration, `node_modules` untrack.
- Anything requiring >50 tracked deletes.
VERIFICATION
- Before each delete: `git status --short <path>` must show **??** or path must not be in `git ls-files`.
- After: `du -sh` on removed dirs (optional); list what was removed in CLOSEOUT.
PROJECT_ID: proj_state_convergence_20260328
WRITE_SCOPE: none for git-tracked files; filesystem deletes only as above.
CONFLICT: Respect ws_teacher_manga_triptych_20260410 / ws_lfs_setup_20260410 — zero edits under `brand-wizard-app/`.
CLOSEOUT_RECEIPT: paths removed, approximate MB freed, confirm Brand Wizard tree untouched.
STARTUP_RECEIPT
STARTUP_RECEIPT
AGENT:
TASK:
PROJECT_ID:
SUBSYSTEM:
AUTHORITY_DOCS:
READ_PATH_COMPLETE:
WRITE_SCOPE:
OUT_OF_SCOPE:
BLOCKERS:
READY_STATUS:


---

**Cursor**

Performing scoped untracked cache cleanup: verifying targets with git, then removing only what's safe.



STARTUP_RECEIPT  
AGENT: Pearl_GitHub + Pearl_Dev  
TASK: Low-risk local cleanup — untracked pytest + scoped `__pycache__` only  
PROJECT_ID: proj_state_convergence_20260328  
SUBSYSTEM: repo coordination  
AUTHORITY_DOCS: docs/SESSION_UNITY_PROTOCOL.md; CLAUDE.md (mass-delete / >50 files rule via workspace rules)  
READ_PATH_COMPLETE: yes — SESSION_UNITY_PROTOCOL template; task-specific CLAUDE constraints applied  
WRITE_SCOPE: Filesystem only — repo-root `.pytest_cache/`; `__pycache__/` under `phoenix_v4/`, `scripts/`, `tests/`, `config/` if untracked  
OUT_OF_SCOPE: `brand-wizard-app/**`; `.claude/worktrees/`; `_wt_*`; `git rm`; tracked removal; zip; `git clean -fdx`; `old_chat_specs/`, `old_chats/`; duplicate tests; `node_modules`  
BLOCKERS: none  
READY_STATUS: ready  

---

### Verification (before delete)

| Path | `git ls-files` | Notes |
|------|----------------|--------|
| `.pytest_cache/` | **0** files | Listed in `.gitignore` (line 34); not in index — satisfies “not in `git ls-files`” |
| `__pycache__/` under `phoenix_v4/`, `scripts/`, `tests/`, `config/` | **n/a** | Scan found **0** such directories |

---

### Actions taken

- Removed **repo-root** `.pytest_cache/` only (`du -sh` was **172K** before delete → **~0.17 MB** freed, effectively **&lt;1 MB**).
- **No** `__pycache__/` dirs existed under the allowed roots; nothing else removed.

**`brand-wizard-app/`:** not read, not modified, not scanned for deletes (per your scope).

---

CLOSEOUT_RECEIPT  
AGENT: Pearl_GitHub + Pearl_Dev  
TASK: Low-risk untracked cache cleanup (Brand Wizard excluded)  
COMMIT_SHA: no commits  
FILES_WRITTEN: none  
FILES_READ: docs/SESSION_UNITY_PROTOCOL.md  
STATUS: completed  
HANDOFF_TO: none  
NEXT_ACTION: none  

**Paths removed:** `.pytest_cache/` (repo root only).  
**Approximate space freed:** **~0.2 MB** (172 KiB).  
**Brand Wizard tree:** **untouched** (no changes under `brand-wizard-app/`).

---

**User**

do you have sai_maa_vid.mp4 or ra.mp4 ?
were you helping me move vids? 

---

**Cursor**

Searching the workspace for those filenames.



Here’s what I can say from **this environment** and **this chat**:

**Files**  
I looked under `artifacts/video`, `artifacts`, `docs`, and the repo root for `sai_maa_vid.mp4` and `ra.mp4`. **Nothing turned up** in those places. I did **not** do a full recursive scan of the whole repo (it’s huge and earlier broad searches timed out), so I can’t swear they’re nowhere on disk under `phoenix_omega`—only that they’re **not** in those common locations.

**Moving videos**  
In **our** thread here, the work was **repo cleanup** (inventory TSV, untracked `.pytest_cache`, etc.), **not** moving or organizing video files. If someone helped you move vids, it was likely **another session** or **another agent/chat**; I don’t have that history in this conversation.

If you want a definitive answer for the whole tree, you can run locally:

```bash
find /Users/ahjan/phoenix_omega -name 'sai_maa_vid.mp4' -o -name 'ra.mp4' 2>/dev/null
```

(or Spotlight: `mdfind 'kMDItemFSName == sai_maa_vid.mp4'`).

