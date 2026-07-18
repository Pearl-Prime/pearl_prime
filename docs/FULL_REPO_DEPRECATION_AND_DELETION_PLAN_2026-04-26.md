# Full Repo Deprecation & Deletion Plan — 2026-04-26

**This is a PLAN, not an execution.** No file is deleted by this PR.
Operator review gates each PR D1-D6 below. Per `CLAUDE.md` rule 0,
no PR may delete >50 files without explicit owner approval; PR D1 batches into
≤50-file segments accordingly.

**Audit baseline:** `1f4f8a28f`
**Inventory source:** `artifacts/inventory/full_repo_pipeline_matrix_2026-04-26.csv` (orphan_module rows)
**Companion docs:** `docs/FULL_REPO_SYSTEM_AUDIT_2026-04-26.md` §6, `docs/FULL_REPO_CANONICAL_SYSTEM_MAP_2026-04-26.md` §3

---

## 1. Deletion class table

| Class | Definition | Risk | Action |
|-------|------------|-----:|--------|
| **L1 — Safe delete** | Zero references in code; explicit deletion-artifact naming (`del_*/`); duplicate of existing canonical file | low | Stage in PR D1 |
| **L2 — Configuration-correctable** | Should be gitignored not committed (e.g., `node_modules/`, `dist/`) | low | Stage in PR D1 alongside `.gitignore` update |
| **L3 — Likely safe but needs runtime check** | Module shows `imported_by_count=0` AND `has_main=0` but may be imported via dynamic loading (`importlib`, `getattr`, plugin systems) | medium | PR D3 — gated on runtime verification |
| **L4 — Superseded canonical** | Older canonical with explicit successor (e.g., `.docx` after `.md` migration) | low-medium | PR D2 — archive, don't delete |
| **L5 — Conflicting / deduplication** | Two files claim authority on same topic; one is provably stale | medium | PR D2 — pick winner; archive loser |
| **L6 — Subsystem-orphaned** | Whole subsystem has no entry point or no authority row | medium-high | Pearl_Architect routing decision first; deletion gated on routing |

## 2. Per-cluster proposals

### 2.1 PR D1 — Safe deletes (L1 + L2)

**Target: ~7,000+ files; segment into ≤50-file PRs per CLAUDE.md mass-delete rule.**

| Sub-batch | Cluster | Files | Class | Rationale |
|-----------|---------|------:|-------|-----------|
| D1.a | `brand-wizard-app/node_modules/` | 6,984 | L2 | Should never have been committed; add to `.gitignore`; will need ~140 segmented PRs at 50 files each, OR a single mass-delete PR with explicit operator sign-off (recommended path for this single coherent cluster) |
| D1.b | `pearl_news copy/` | 7+ | L1 | PR #245 accidental restore; per Phase 3 reviewer code+pipelines report |
| D1.c | `del_files/` | 2+ | L1 | Naming declares intent |
| D1.d | `del_location_plan/` | 2+ | L1 | Naming declares intent |
| D1.e | `del_intake_planner/` | 2+ | L1 | Naming declares intent |
| D1.f | `del_exta_stories/` | 2+ | L1 | Naming declares intent |
| D1.g | `deli/`, `delf/` | misc | L1 | Likely typo/staging; verify before |
| D1.h | `files-4/` | 1+ | L1 | Duplicate validation module |

**D1.a special handling**: 6,984 files in one PR exceeds CLAUDE.md's 50-file rule for "without explicit owner approval". Two options:
- **Option A** — single PR with explicit operator approval up front: cleanest, fastest, single CI run, single LFS-pointer hazard check.
- **Option B** — segment into 140 × 50-file PRs: slow, expensive, but conforms to default rule.
- **Recommendation**: Option A. The cluster is a single homogeneous category (npm dependencies under one prefix); operator approval is straightforward.

### 2.2 PR D2 — Superseded canonicals (L4 + L5)

| Item | Action | Successor |
|------|--------|-----------|
| `docs/MANGA_MODE_STRATEGY.docx` | Move to `archive/specs_originals/` | `docs/MANGA_MODE_STRATEGY.md` (PR #684) |
| `artifacts/manga/MANGA_FULL_CATALOG_PLAN.md` (hand-edited) | Move to `archive/manga_catalog_handedited/` | auto-generated per spec D-17 (when generator lands) |
| Triple HTML brand-admin | Pick canonical (likely `brand_admin_weekly_os.html`); archive others | TBD by Pearl_Brand session |
| 2 CSV-flagged `superseded` docs | Move to `archive/` | (per CSV `notes` field) |

### 2.3 PR D3 — phoenix_v4/ orphan subset (L3)

**238 orphans total; 153 in `phoenix_v4/`** — biggest single cluster.

**Hard-gate on runtime check**: before any deletion in this cluster, run:

```bash
python3 -c "import importlib.util, ast; \
  for path in $(cat phoenix_v4_orphan_paths.txt); do \
    # check for getattr / importlib / spec_from_file_location references \
    # AND check for fixture-style discoverable test patterns (pytest collection)"
```

If runtime imports exist, downgrade from orphan to live and KEEP. The 24
`pearl_news/pipeline/` orphans flagged by Phase 3 reviewer are likely false
positives by this same heuristic.

| Sub-batch | Cluster | Files | Action |
|-----------|---------|------:|--------|
| D3.a | `phoenix_v4/manga/` orphans | 45 | runtime check; if dead, delete |
| D3.b | `phoenix_v4/` (other) orphans | 108 | runtime check; if dead, delete |
| D3.c | `pearl_news/pipeline/` orphans | 24 | likely FP; verify before any action |
| D3.d | `scripts/` orphans | 21 | per-file judgment |
| D3.e | `server/` orphans | 7 | per-file judgment |

### 2.4 PR D4 — UI / feature unused (L1 minor)

| Item | Files | Notes |
|------|------:|-------|
| `somatic_exercise_freebee_apps/` | 42 HTMLs | Stale at 2026-04-01 (25 days cold); evaluate archive vs. revive per Pearl_Marketing |
| `dashboard/` (no entry point) | 1 pipeline | Pearl_Architect routing decision first; if no canonical home, archive |

### 2.5 PR D5 — Dead pipeline code (L3)

Per pipeline_matrix `status=orphaned`:
- `dashboard` pipeline (no entry point)

Most other pipelines are scheduled or live.

### 2.6 PR D6 — Docs index update

After D1-D5 land:
- Update `docs/DOCS_INDEX.md` to remove deleted paths
- Update `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv` if any subsystem
  changed authority (e.g., dashboard archived)
- Update `docs/PEARL_ARCHITECT_STATE.md` with deletion-PR landed entry

## 3. Deletion-totals summary

| PR | Class | Approx. files |
|----|-------|--------------:|
| D1 | L1 + L2 | ~7,000 (mostly node_modules) |
| D2 | L4 + L5 | ~5 |
| D3 | L3 | up to 238 (gated on runtime check; expect 50-100 actual) |
| D4 | L1 minor | up to 43 |
| D5 | L3 | TBD |
| D6 | docs index | n/a |

**Estimated true deletion total** (after L3 runtime-check filtering): 7,100-7,200 files,
where 6,984 of those is the single homogeneous `brand-wizard-app/node_modules/`
cluster.

## 4. Per-PR governance gating

Every deletion PR must pass:
- `scripts/git/push_guard.py`
- `scripts/ci/preflight_push.sh`
- `scripts/ci/audit_llm_callers.py` (clean)
- `scripts/ci/pr_governance_review.py` — **mass-delete check is the gate**:
  - >50 deletes triggers mandatory operator approval per CLAUDE.md rule 0
  - >500 deletes is auto-blocked unless explicitly waived
- `gh pr view <num> --json mergeCommit` AND `git ls-remote origin main` cross-confirm
  the merge SHA after merge

**LFS-pointer hazard check before each push**: stage explicitly only the files in scope;
if `git diff --cached --stat` shows anything else, STOP and unstage. (See CLAUDE.md.)

## 5. Hard rules for deletion PRs

1. **No deletion in this audit's PR-1 through PR-4.** This file is plan-only.
2. **One coherent cluster per PR** (not mixed). E.g., D1.a is its own PR; D1.b is its own PR.
3. **Operator approval required** for any PR D-* that exceeds 50 deletes.
4. **No `--no-verify` / no hook bypass.**
5. **Capture full 40-char merge SHA** for every deletion PR.
6. **Update DOCS_INDEX.md last** (PR D6) after the deletion PRs settle, so navigation
   doesn't break mid-stream.
7. **Tier 1** for all deletion-PR work (operator-present per CLAUDE.md).

## 6. Open questions before D1 fires

| OQ | Question |
|----|----------|
| Δ-1 | Confirm `brand-wizard-app/node_modules/` was committed accidentally (not deliberately for offline reproducibility) |
| Δ-2 | Confirm `pearl_news copy/` is PR #245's accidental restore (no other revival reason) |
| Δ-3 | Confirm `del_*/` directories are not in-flight migrations |
| Δ-4 | For PR D3.c: are `pearl_news/pipeline/` orphans truly imported across package boundaries? Run the dynamic-import check |
| Δ-5 | For PR D4: does `dashboard/` revive to a canonical home, or is it abandoned? Pearl_Architect call |
| Δ-6 | For PR D2 docx: is `MANGA_MODE_STRATEGY.docx` referenced anywhere outside its `.md` migration note? |

Operator review of this plan is the gate for all D-PRs.
