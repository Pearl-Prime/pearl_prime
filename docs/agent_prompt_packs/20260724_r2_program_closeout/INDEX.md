# R2 / LFS Offload Program — Closeout, Durability, Phase-B Decision (Pack INDEX)

**Authored:** 2026-07-24 by Piper (prompt router). **Owners:** Pearl_Int (Lanes A, B) + Pearl_Architect (Lane C).
**Scope:** Cloudflare **R2** storage + git-LFS **architecture/integration** only. **NOT manga authoring/render** — a separate agent owns that; do not touch `artifacts/manga/**` content, render dispatch, or manga specs beyond preserving the byte-gate R2 contract.

---

## Why this pack exists (verified live-state as of origin/main `82ef39572e`)

The prior DevOps session (`artifacts/coordination/handoffs/disk_r2_offload_session_2026-07-23.md`, "2 of 5 PRs merged") **executed** the LFS→R2 offload but left the program in a **half-landed, undocumented, unverified** state. Re-verified topology (do not trust; re-check live — squash-merges hide behind ahead-branches, [[feedback_verify_ahead_branch_not_stale]]):

| Item | Live status (re-verify) | Evidence |
|---|---|---|
| LFS→R2 offload V1 spec + pilot | **ON main** | PR #5306 `5b3f64e299` |
| Wave 3 (manga assembled/ + v4_render_cache/, 267 tracked files) | **ON main** (squash `b702de43f9`) | PR #151 MERGED (owner-approved >50 deletions) |
| Wave 4 (brand-wizard covers, 79 tracked files) | **ON main** (squash `bccb188535`) | PR #161 MERGED (owner-approved >50 deletions) |
| Lane 03 "what-runs-where" policy + RAP artifact detector | **ON main** | PR #73 `e3a7ed715b` |
| Wave 2 (`assets/manga_catalog/**`) | **0 git-tracked files** — no git-surgery target | `git ls-files assets/manga_catalog \| wc -l` → 0 |
| **PROGRAM_STATE DevOps section** | **STALE** — still says "V1 pilot only; Wave-2 remains a follow-on lane" | `docs/PROGRAM_STATE.md:185-190` |
| **Spec §7 status line** | **STALE** — "ACTIVE (pilot landed 2026-07-09)" | `docs/specs/LFS_TO_R2_OFFLOAD_V1_SPEC.md:3` |
| **ws_lfs_setup_20260410 row** | **STALE** — "active", only pilot evidence, no Wave 3/4 SHAs | `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` |
| **Waves-2-4 handoff file** | **MISSING** — pack required it, never written | `artifacts/coordination/handoffs/lfs-r2-offload-waves-2-4_*.md` absent |
| **`deep_verify_r2_offload.py` weekly job** | **UNWIRED** — script exists, no `.github/workflows` schedules it | `grep -rl deep_verify_r2_offload .github/` → empty |
| **Phase B history rewrite** | **OPEN, owner-gated** — never scoped into a decision packet | `docs/GIT_LFS_MIGRATION_PLAN.md:108`; `ws_lfs_setup_20260410` |
| Orphaned pre-squash remote branches | present, prune candidates | `origin/agent/lane02-wave{3,4}-lfs-offload-20260723` (merged) |

**Net:** the bytes moved to R2 and landed on `main`, but (1) the program's own truth surfaces (PROGRAM_STATE / spec / workstream / handoff) still describe a "pilot-only" world, (2) the durability verifier that proves those R2 blobs are actually retrievable has no scheduler, and (3) the one genuinely-owner-gated architecture decision (history rewrite) was never turned into a ratifiable packet. This pack closes all three.

---

## Lanes

| # | File | Owner | One-liner | Depends on |
|---|---|---|---|---|
| 00 | `00_MASTER_DISPATCH_PROMPT.md` | Pearl_PM | Dispatch + sequence the three lanes | — |
| A | `01_R2_PROGRAM_RECONCILIATION.md` | Pearl_Int | Reconcile PROGRAM_STATE/spec/workstream to reality; Wave-2 N/A disposition; write missing waves handoff; prune merged branches | — (start first) |
| B | `02_R2_DURABILITY_VERIFIER_WIRING.md` | Pearl_Int | Wire `deep_verify_r2_offload.py` into a scheduled weekly GHA + prove it fetches real bytes from R2 | Lane A merged (truth first) |
| C | `03_PHASE_B_HISTORY_REWRITE_DECISION_PACKET.md` | Pearl_Architect | Author the go/no-go readiness + blast-radius + rollback packet for owner ratification — **NOT execution** | Lanes A+B (so the packet cites a truthful, verified baseline) |

**Sequencing:** A → B → C. A is pure doc/bookkeeping truth (fast, low-risk). B depends on A being merged so it verifies against reconciled manifests. C is authored last so its "current state" section cites A/B as done. C **ends at a packet + operator decision gate**, never at an executed rewrite.

## Hard rules (all lanes)
- Manga content is **out of scope** — preserve, never modify, the `check_render_progress_bytes.py` manifest-verify R2 contract (spec §4.2); a separate agent owns manga.
- **Forward-only** for Lanes A/B. Only Lane C may *plan* history rewrite, and only as an owner-gated packet.
- Every branch/SHA/count in these prompts is a **CLAIM** — re-verify live (`git fetch`, `gh pr view`) before acting. Squash-merges make branches look unmerged ([[feedback_verify_ahead_branch_not_stale]]).
- Land **MERGED or BLOCKED**. Name the acceptance layer; a gate PASS is not "done."
