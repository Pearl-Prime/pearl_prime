# CI hygiene — complete session record (PR governance + LLM audit scoping)

**Project ID:** PRJ-PEARL-DEVOPS-CI-HYGIENE (add row to `artifacts/coordination/ACTIVE_PROJECTS.tsv` if tracking is desired)  
**Subsystem:** pearl_devops  
**Authority:** `docs/GITHUB_OPERATIONS_FRAMEWORK.md`; `docs/GITHUB_GOVERNANCE.md`  
**Last updated:** 2026-05-08

---

## 1. Executive summary

Two CI hygiene issues were targeted:

1. **`pr_governance_review.py`** must not rely on `gh pr diff … --name-status` alone (the flag is invalid on current `gh`, yielding empty parses and a trivial pass).
2. **`audit_llm_callers.py`** must support **scoped roots** for PR gates and an optional **wall-clock cap**; full-tree scans on this repository have been reported at **55–92 minutes** per run.

This document records **requirements**, **intended code shape**, **workflow callers**, **validation runs** (including PRs #940–#946), **git / shell failures** encountered in session, and **current tree reconciliation status** (tests vs scripts).

---

## 2. BUG-1 — `pr_governance_review.py` and `gh pr diff`

### Problem

`gh pr diff <PR> --name-status` returns non-zero on current CLI (`unknown flag: --name-status`). Older logic that only parsed **successful** `gh pr diff` stdout saw **zero files**, so governance checks did not reflect the real PR.

### Intended behavior (acceptance)

1. Primary: try `gh pr diff <pr> --name-status`.
2. On **non-zero exit**, **empty/whitespace-only stdout**, or **stdout that does not parse as name-status lines** when non-empty → fall back to `gh pr view <pr> --json files` and map `changeType` to `A`/`M`/`D`/`R`.
3. Emit stderr telemetry, e.g.  
   `[pr_governance_review] changed_files_source=gh_pr_diff_name_status`  
   or  
   `[pr_governance_review] changed_files_source=gh_pr_view_json_files detail=…`
4. PR-specific helper naming in the spec: `get_changed_files(pr_number)` for the `gh` path; umbrella `get_changed_files_for_review(pr_number=None)` for `git diff origin/main...HEAD` when `--pr` is not used.

### GitHub Actions note

`.github/workflows/pr-governance-review.yml` runs **without** `--pr`; it uses **local git** (`origin/main…HEAD` on the checkout). The **BUG-1** failure mode primarily affects **local/CLI** use: `python3 scripts/ci/pr_governance_review.py --pr <N>`.

### Re-validation: PRs #940 / #941 / #943 / #944 / #945 / #946

Using `gh pr view <N> --json files` (and post-fix review script), non-empty file lists were recorded:

| PR | File count | Notes |
|----|------------|--------|
| #940 | 5 | Coordination TSVs, QA artifact, PEARL_ARCHITECT_STATE, TEACHER_MANGA spec |
| #941 | 4 | Refrain allowlist migration, config, book_quality_gate, test |
| #943 | 1 | Audiobook prose sample |
| #944 | 2 | Qi foundation QA artifact, PEARL_ARCHITECT_STATE |
| #945 | 11 | Manga lettering / bubble stack (fonts, phoenix_v4/manga, schemas, scripts, tests) |
| #946 | 6 | Pearl Star install log, credentials doc, runbook, integration_env_registry, ComfyUI JSON, skill ref |

On a host where `gh pr diff … --name-status` fails, stderr showed  
`changed_files_source=gh_pr_view_json_files` with `gh_pr_diff_rc=1` and text starting `unknown flag: --name-status`.

**Example (#941):** 4 files — `artifacts/qa/refrain_allowlist_migration_2026-05-08.md`, `config/quality/refrain_allowlist.yaml`, `phoenix_v4/quality/book_quality_gate.py`, `tests/quality/test_refrain_allowlist.py`.

---

## 3. BUG-2 — `audit_llm_callers.py` — `--roots` and `--max-runtime-seconds`

### Problem

Full-repo scan wall time is unsuitable for PR-level gates on this tree (reported **55–92 min** in the 2026-05-08 wave).

### Intended behavior (acceptance)

- **`--roots PATH [PATH …]`** — When provided, scan only those roots (repo-relative or absolute). When **omitted**, behavior remains **full-tree** (safety default). Prefer **`nargs='+'`** so `--roots` cannot be accidentally empty.
- **`--max-runtime-seconds N`** — Optional; if elapsed wall time during discovery or rule scanning exceeds **N**, exit **2** with stderr diagnostics. If unset, no limit.

### Recommended usage

- **PR-paths gate (fast):**  
  `--roots $(gh pr view $PR --json files --jq '.files[].path' | xargs -n1 dirname | sort -u)`  
  (adjust for very large PRs.)
- **Nightly / policy enforcement:** run **without** `--roots` (full tree).

### Timings (recorded in session)

| Mode | Command (representative) | Approx. wall time |
|------|---------------------------|-------------------|
| Scoped | `python3 scripts/ci/audit_llm_callers.py --roots scripts/ci tests/ci` | ~**10–14 s** real (violations 0 on smoke host) |
| Full tree | `python3 scripts/ci/audit_llm_callers.py` | **55–92 min** (reported; not re-run to completion in session) |

---

## 4. Files touched by the workstream

| Path | Role |
|------|------|
| `scripts/ci/pr_governance_review.py` | BUG-1 implementation |
| `scripts/ci/audit_llm_callers.py` | BUG-2 `--roots` tightening + `--max-runtime-seconds` |
| `tests/ci/test_pr_governance_review_fallback.py` | Unit tests (mock `gh`) |
| `tests/ci/test_audit_llm_callers_roots.py` | Unit tests (temp tree, roots + max runtime) |
| `artifacts/qa/ci_hygiene_fixes_2026-05-08.md` | This document |

**Out of scope (per charter):** branch protection changes, workflow trigger edits (except compatibility notes), other CI scripts, removing full-tree default behavior.

---

## 5. Workflow compatibility (`.github/workflows`)

| Workflow | Script invocation | Notes |
|----------|-------------------|--------|
| `pr-governance-review.yml` | `python3 scripts/ci/pr_governance_review.py --json` | No `--pr`; uses checkout git range |
| `llm-policy-enforcement.yml` | `audit_llm_callers.py` with pattern files, `--fail-on-violation` | No `--roots`; full scan unchanged |
| `llm-callers-audit.yml` | `audit_llm_callers.py … --roots "${ROOTS[@]}" …` | Compatible with `--roots` requiring one or more paths |

---

## 6. Unit tests (design and current status)

**Design:**  
- Governance tests: mock `subprocess.run`; assert primary path, fallback, and stderr telemetry.  
- Audit tests: monkeypatch `REPO_ROOT` to a minimal tree with a test-only banned rule; assert **1** violation with `--roots` and **2** without; assert `--max-runtime-seconds 0` → exit **2**; assert aggressive monotonic clock → exit **2** during scan.

**Current status (2026-05-08, local):**  

```text
pytest tests/ci/test_pr_governance_review_fallback.py tests/ci/test_audit_llm_callers_roots.py
# Observed: 6 failed, 1 passed (implementation in scripts does not yet match tests)
```

**Reconciliation:** Either re-apply the intended patches to `scripts/ci/pr_governance_review.py` and `scripts/ci/audit_llm_callers.py`, or revert/adjust the tests. The tests encode the accepted behavior above.

---

## 7. Git and shell operations log

| Event | Outcome |
|-------|---------|
| Worktree `…/phoenix_omega_ci_hygiene_wt` | Created then **removed** (`git worktree remove -f -f`); branch **`agent/ci-hygiene-pr-gov-llm-roots-20260508`** deleted during cleanup |
| `git checkout` feature branch from `origin/main` | **Blocked** — unrelated dirty files and untracked paths would be overwritten |
| `git commit` (scoped files) | **Blocked** — `.git/index.lock` / competing git activity |
| `git status` (full repo) | **Risky** — very slow; one run **SIGKILL (exit 137)** on huge repo |
| `git status -sb` + `git diff origin/main …` (task 306041) | **Exit 128** — `status died of signal 15`; submodule/worktree:  
  `fatal: 'git status --porcelain=2' failed in submodule .claude/worktrees/eager-jepsen-f008e5` |
| Path-scoped `git diff origin/main -- <files>` | **Works** — prefer this over full `git status` |

**Recommendation:** Use **path-scoped** `git add`/`git diff`/`git commit`; avoid full `git status` until submodule/worktree issues are resolved; ensure no concurrent **git** holds **index.lock**.

---

## 8. Background shell tasks (session notifications)

| Task | Description | Result |
|------|-------------|--------|
| Worktree add | Create `phoenix_omega_ci_hygiene_wt` + branch | **Exit 128** (large checkout / contention) |
| Force remove worktree + delete branch | Cleanup | **Success** |
| Governance + `gh` for PRs 940–946 | Capture stderr + file lists | **Success** |
| Git status for commit | Full status | **Exit 137** (process killed) |
| Branch vs main for target scripts | Status + diff | **Exit 128** (submodule status failure) |

---

## 9. Commit, PR, and handoff

- **Commit SHA / PR URL:** Not produced in-session (git lock, dirty tree, branch checkout blocked).
- **Suggested commit message:**  
  `ci(hygiene): pr_governance_review fallback + audit_llm_callers --roots flag`
- **HANDOFF_TO: Pearl_GitHub** — After merge: re-validate governance and LLM gates on the 2026-05-08 PR train; use scoped `--roots` for fast PR-path audits where appropriate; keep nightly full audit **without** `--roots`.

---

## 10. Quick reference — commands

```bash
# Governance for a specific PR (requires gh)
PYTHONPATH=. python3 scripts/ci/pr_governance_review.py --pr 941

# Scoped LLM audit (example)
python3 scripts/ci/audit_llm_callers.py --roots scripts/ci tests/ci

# Tests (after scripts match acceptance)
PYTHONPATH=. python3 -m pytest tests/ci/test_pr_governance_review_fallback.py \
  tests/ci/test_audit_llm_callers_roots.py -v

# Preflight (when ready to push — per CLAUDE.md)
git branch --show-current
git status --short   # avoid on broken submodules; use path-scoped status if needed
git fetch origin
git rev-list --left-right --count origin/main...HEAD
PYTHONPATH=. python3 scripts/git/push_guard.py
scripts/ci/preflight_push.sh
bash scripts/git/health_check.sh
```

---

## 11. Related documentation index

- `CLAUDE.md` — LLM policy; `audit_llm_callers.py` reference  
- `docs/GITHUB_OPERATIONS_FRAMEWORK.md`  
- `docs/GITHUB_GOVERNANCE.md`  
- `.github/workflows/pr-governance-review.yml`  
- `.github/workflows/llm-policy-enforcement.yml`  
- `.github/workflows/llm-callers-audit.yml`  
- `config/governance/banned_llm_patterns.yaml` — audit rules source
