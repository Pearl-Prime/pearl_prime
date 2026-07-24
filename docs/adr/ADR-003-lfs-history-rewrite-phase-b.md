# ADR-003: LFS→R2 Phase B history rewrite

**Status:** proposed
**Date:** 2026-07-24
**Deciders:** operator (Ahjan)
**Related:** `docs/decisions/PHASE_B_HISTORY_REWRITE_DECISION_PACKET.md` (full packet — read that first;
this ADR is the short-form record), `docs/GIT_LFS_MIGRATION_PLAN.md` §Phase B,
`docs/specs/LFS_TO_R2_OFFLOAD_V1_SPEC.md` §0/Q-LFS-05, `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`
→ `ws_lfs_setup_20260410`

---

## Context

The LFS→R2 offload program (`ws_lfs_setup_20260410`) shipped forward-only: `.gitattributes` now routes
new binary commits through LFS/R2, and Waves 3–4 (346 files) have already been offloaded and reconciled
onto `main` (PR #151, #161, reconciled by PR #336). The one item that program never resolved is that
every blob offloaded or LFS-tracked **historically** still lives in git history — reclaiming that space
requires a `git lfs migrate import --everything` history rewrite, which is force-push-to-`main` +
mandatory re-clone for every collaborator, agent worktree, and CI checkout. That is an owner-ratification
decision by explicit repo policy (spec §Q-LFS-05: "History rewrite = operator-ratification only").

## Decision

**Not yet made.** This ADR records that the decision was formally packaged (2026-07-24) and is
**PROPOSED**, pending the operator's ruling recorded in the decision packet's §8 `OPERATOR DECISION` field.
The authoring Architect's recommendation is **DEFER**, on the grounds that this session could not produce
a single trustworthy reclaimable-bytes estimate — five measurement attempts across three sessions produced
figures spanning roughly 0.9 GB to 76 GB for what looks like the same underlying repository, an order-of-
magnitude spread too wide to support an honest cost/benefit case today. See the packet §2 for the full
measurement table and the trigger conditions (packet §8) that would make this ADR ripe for a real GO/NO-GO.

## Consequences (if eventually GO)

- One-time force-push to protected `main` (ruleset `19645211`, "Protect main") — requires an owner to
  temporarily adjust the `non_fast_forward` rule for the duration of the push only.
- Every collaborator, every agent worktree (20 found locally as of 2026-07-24), and every CI runner must
  re-clone; a `git pull` into an existing worktree post-rewrite desyncs.
- All open PRs (6 as of 2026-07-24) must land or close first.
- Irreversible once any party re-clones onto the new history (see packet §7 rollback).

## Consequences (of continuing to DEFER)

- `ws_lfs_setup_20260410` stays open indefinitely on this one item; no further action required to keep the
  status quo safe — the repo functions correctly today with the historical bloat unreclaimed (this is a
  disk/clone-time cost, not a correctness or data-loss risk).
- Repeated measurement drift (each session re-estimating a different number) suggests the underlying
  measurement methodology itself needs fixing before this decision can be revisited productively — see
  packet §2's recommendation to re-run `git lfs migrate info` from a clean mirror clone, not a
  worktree-laden laptop checkout.
