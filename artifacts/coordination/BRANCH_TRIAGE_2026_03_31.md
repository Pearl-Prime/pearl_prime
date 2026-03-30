# Branch Triage — 2026-03-31

Owner: Pearl_GitHub  
Inventory time: after `git fetch origin --prune`  
Authority for `codex/*`: `docs/BRANCH_DISPOSITION_2026_03_20.md`  
Active workstreams: `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`

## Summary

| Metric | Count |
|--------|------:|
| Total remote branches inventoried (including `origin/main`) | 41 |
| `agent/*` at inventory | 38 |
| `codex/*` at inventory | 1 |
| Other (`claude/*`, etc.) at inventory | 1 |
| **Deleted (merged PR confirmed)** | **33** |
| Deleted (closed/orphan) | 0 |
| Deleted (NEEDS-REVIEW deep review, superseded) | **4** |
| Kept (open PR) | 1 |
| Kept (active / preserved workstream) | 1 |
| Needs review | 0 (resolved 2026-03-31) |

**Post-cleanup (after deletions + `git fetch --prune`):** 8 remote refs total (`origin/main` + 7 topic branches). Remaining `agent/*`: 6. Remaining `codex/*`: 1.

**After NEEDS-REVIEW deletions:** remote `agent/*` count drops by 4 (see deep-review table below); re-run `git fetch origin --prune` to refresh.

**Rules applied:** Only deleted remotes where every PR returned by `gh pr list --state all --head <branch>` was in state `MERGED`. No open PR branches deleted. No `codex/*` deleted except where disposition explicitly says `delete` (only `codex/runtime-consolidation` existed remotely; disposition is `keep-open` → left in place). `DELETE-CLOSED` and `DELETE-ORPHAN` were not used where unique commits or ambiguity remained.

## agent/* branches

| Branch | Ahead | Behind | PR | Status | Disposition | Action |
|--------|------:|-------:|----|--------|-------------|--------|
| agent/add-push-guard | 2 | 67 | #57 | MERGED | DELETE-MERGED | `git push origin --delete` |
| agent/adi-da-arc-band-align | 1 | 24 | #102 | MERGED | DELETE-MERGED | deleted |
| agent/adi-da-f006-coverage | 4 | 23 | #99 | MERGED | DELETE-MERGED | deleted |
| agent/adi-da-story-universal-wildcard-clean | 1 | 25 | #101 | MERGED | DELETE-MERGED | deleted |
| agent/adi-da-teacher-bank-only | 3 | 27 | — | none | DELETE-SUPERSEDED | deleted (deep review 2026-03-31) |
| agent/atom-debt-repair-spec | 1 | 33 | #91 | MERGED | DELETE-MERGED | deleted |
| agent/bestseller-100-signoff | 26 | 61 | #64 | CLOSED | DELETE-SUPERSEDED | deleted (deep review 2026-03-31) |
| agent/bestseller-100-signoff-clean | 6 | 61 | #65 | MERGED | DELETE-MERGED | deleted |
| agent/bestseller-grade-pr02 | 1 | 21 | #104 | MERGED | DELETE-MERGED | deleted |
| agent/bestseller-grade-pr04 | 1 | 19 | #114 | MERGED | DELETE-MERGED | deleted |
| agent/bestseller-grade-wiring | 1 | 20 | #106 | MERGED | DELETE-MERGED | deleted |
| agent/brand-admin-enhancement-pr | 1 | 53 | #72 | MERGED | DELETE-MERGED | deleted |
| agent/coastal-california-profile-s0 | 1 | 46 | #78 | MERGED | DELETE-MERGED | deleted |
| agent/docs-trend-truth-repair-pr4 | 1 | 54 | #71 | MERGED | DELETE-MERGED | deleted |
| agent/harvest-refresh | 1 | 34 | #90 | MERGED | DELETE-MERGED | deleted |
| agent/hourly-repo-alignment-workstream-a | 1 | 57 | #69 | MERGED | DELETE-MERGED | deleted |
| agent/manga-chunk-a-writer | 1 | 68 | #56 | MERGED | DELETE-MERGED | deleted |
| agent/manga-chunk-b-series | 1 | 65 | #58 | MERGED | DELETE-MERGED | deleted |
| agent/manga-chunk-cd-chapter-production | 1 | 64 | #59 | MERGED | DELETE-MERGED | deleted |
| agent/manga-chunk-ef-runner | 2 | 63 | — | none | DELETE-SUPERSEDED | deleted (deep review 2026-03-31) |
| agent/manga-chunk-ef-runner-clean | 1 | 63 | #60 | MERGED | DELETE-MERGED | deleted |
| agent/manga-phase0-schemas | 2 | 84 | — | none | DELETE-SUPERSEDED | deleted (deep review 2026-03-31) |
| agent/manga-phase3-visual | 1 | 66 | #55 | MERGED | DELETE-MERGED | deleted |
| agent/manga-pipeline-impl | 1 | 69 | #54 | MERGED | DELETE-MERGED | deleted |
| agent/manga-sdf-revision-workspace | 8 | 62 | — | none | KEEP-ACTIVE | leave (`ACTIVE_WORKSTREAMS.tsv` pen-name recovery) |
| agent/manga-sdf-salvage | 1 | 1 | #63 | MERGED | DELETE-MERGED | deleted |
| agent/overthinking-scene-pr-s1 | 2 | 42 | #79 | MERGED | DELETE-MERGED | deleted |
| agent/pearl-prime-bestseller-runtime | 1 | 50 | #74 | MERGED | DELETE-MERGED | deleted |
| agent/pearl-prime-cloudflare-contract-v2 | 1 | 72 | #51 | MERGED | DELETE-MERGED | deleted |
| agent/pearl-prime-recovery-closeout | 1 | 48 | #76 | MERGED | DELETE-MERGED | deleted |
| agent/pearl-prime-recovery-docs | 1 | 49 | #75 | MERGED | DELETE-MERGED | deleted |
| agent/pr-s2-hollow-compression | 1 | 41 | #81 | MERGED | DELETE-MERGED | deleted |
| agent/pr-s4-sleep-anxiety-hook | 2 | 44 | #82 | MERGED | DELETE-MERGED | deleted |
| agent/pr-s5-location-profiles | 1 | 45 | #80 | MERGED | DELETE-MERGED | deleted |
| agent/repo-alignment-hardening | 1 | 62 | #61 | OPEN | KEEP-OPEN | leave |
| agent/repo-state-refresh | 1 | 62 | #62 | MERGED | DELETE-MERGED | deleted |
| agent/revert-accidental-squash-scope | 1 | 43 | #83 | MERGED | DELETE-MERGED | deleted |
| agent/source-bank-repair-spec | 2 | 47 | #77 | MERGED | DELETE-MERGED | deleted |

## codex/* branches

| Branch | Ahead | Behind | Disposition doc says | Notes | Action |
|--------|------:|-------:|---------------------|-------|--------|
| codex/runtime-consolidation | 165 | 102 | `keep-open` | Matrix row: large branch; PR #21 listed in doc as open vehicle — `gh` shows PR #21 **CLOSED** at triage time; still no `delete` in disposition | **leave** (per doc: not `delete`) |

**Disposition doc branches not present on `origin` at triage:** `codex/ei-v2-gate-fix`, `codex/ei-v2-hybrid-only-clean`, `codex/ei-v2-hybrid-pr`, `codex/governance-100`, `codex/governance-evidence-pack`, `codex/pearl-news-cleanup`, `codex/pearl-news-workflows-clean`, `codex/phoenixcontrol-ui`, `codex/runtime-governance-core`, and addendum entries — no remote action this pass.

## Other branches

| Branch | Ahead | Behind | PR | Notes | Action |
|--------|------:|-------:|----|-------|--------|
| claude/heuristic-wilbur | 2 | 26 | #98 MERGED | — | deleted |

## Post-cleanup verification

Commands run:

- `git fetch origin --prune`
- Remaining remote branch count: **8** (including `origin/main`)
- Remaining `agent/*`: **6**
- Remaining `codex/*`: **1**
- `bash scripts/git/health_check.sh` — completed; reports many “gone upstream” warnings for **deleted** branches (expected until local tracking refs age out or are pruned from other clones).

## Deep review — NEEDS-REVIEW closure (2026-03-31)

Pearl_GitHub reviewed the four branches left as **NEEDS-REVIEW** after the bulk deletion pass. Method: `git log` / `git diff --stat origin/main...<branch>`, spot-check `git diff origin/main origin/<branch> -- <paths>`, PR metadata via `gh`.

| Branch | Commits ahead (pre-review) | Unique content? | Disposition | Action |
|--------|---------------------------|-----------------|-------------|--------|
| `agent/bestseller-100-signoff` | 26 (25× `chore(backup)` + 1× release) | **No** — substantive commit `c8e50257` only adds `artifacts/governance/bestseller_100_signoff_2026-03-26.md`; **byte-identical on `origin/main`**. PR #64 closed 2026-03-26; backups add creds/chat/feed noise. | **DELETE (superseded)** | `git push origin --delete agent/bestseller-100-signoff` |
| `agent/adi-da-teacher-bank-only` | 3 | **No** — `config/teachers/teacher_registry.yaml` and `config/catalog_planning/teacher_persona_matrix.yaml` **match `main`**; `main` has a **strict superset** of `SOURCE_OF_TRUTH/teacher_banks/adi_da/` (e.g. COMPRESSION atoms + README on main, absent or thinner on branch). Aligns with post–source-bank-repair `main`. | **DELETE (superseded)** | `git push origin --delete agent/adi-da-teacher-bank-only` |
| `agent/manga-chunk-ef-runner` | 2 (1× backup + `7b47bbdc`) | **No** — substantive commit’s E+F runner/QC/gate work **landed via later mainline** (e.g. PR #63 manga salvage + `manga-chunk-ef-runner-clean` / #60). `git diff origin/main origin/agent/manga-chunk-ef-runner` on `phoenix_v4/manga/runner/`, `scripts/manga/run_manga_chapter.py` shows **main ahead** (branch would drop workspace/revision/SDF slices present on `main`). | **DELETE (superseded)** | `git push origin --delete agent/manga-chunk-ef-runner` |
| `agent/manga-phase0-schemas` | 2 (1× backup + `7687603c`) | **No** — `schemas/manga/*` on **`main` is richer** (e.g. `panel_prompts.schema.json` includes series/chapter ids, SDF conditioning, token counts); phase0 branch is an **older minimal cut**. `scripts/manga/validate_manga_json.py` and expanded tests already on `main`. | **DELETE (superseded)** | `git push origin --delete agent/manga-phase0-schemas` |

**Bestseller 100 / canary:** The “100 signoff” markdown artifact is already on `main`; ongoing **canary** + **bestseller-grade PRs (#115–#120)** supersede the old PR #64 narrative for runtime gates. No cherry-pick required.

**Harvest:** None — no file-level unique delta remained vs `origin/main` for these four.

---

## CLOSEOUT_RECEIPT

- **Triage artifact:** `artifacts/coordination/BRANCH_TRIAGE_2026_03_31.md`
- **Remote deletions (first pass):** 33 refs (`agent/*` × 32 + `claude/heuristic-wilbur` × 1), all with all-linked PRs in `MERGED` state per `gh pr list --state all --head <branch>`
- **Remote deletions (NEEDS-REVIEW pass, 2026-03-31):** `agent/bestseller-100-signoff`, `agent/adi-da-teacher-bank-only`, `agent/manga-chunk-ef-runner`, `agent/manga-phase0-schemas` (superseded vs `origin/main`; verified before delete)
- **Explicitly not deleted (first pass):** `agent/repo-alignment-hardening` (PR #61 OPEN at triage time; later superseded by PR #123 on `main`), `agent/manga-sdf-revision-workspace` (preserved workstream), the four NEEDS-REVIEW rows above (resolved in deep review), `codex/runtime-consolidation` (disposition `keep-open`)
