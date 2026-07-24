# Handoff — Lane 02 manga video pose-bank capability research

**Date:** 2026-07-24  
**Agent:** Pearl_Research  
**Status:** MERGED (see CLOSEOUT / SIGNAL after land)

## Deliverables

| Path | Purpose |
|------|---------|
| `docs/research/MANGA_VIDEO_POSE_BANK_CAPABILITY_RESEARCH_2026-07-24.md` | Full capability research + decision matrix + RECOMMENDATIONS |
| `artifacts/research/manga_video_pose_bank_2026-07-24/` | Evidence dumps (SOURCES, quotas, selfhost, method) |

## Decisions Lane 03/04/05 must honor

1. Pilot = **wan2.7-i2v + canonical external still** (URL/base64).  
2. **Skip r2v** unless `burn_summary`/preflight proves free seconds on `ahjansamvara`.  
3. Scale = **VACE-1.3B Apache** on Pearl Star (off-manga queue windows).  
4. Free-quota outputs = **INTERIM**; Apache Wan/VACE = REAL-eligible after QA.  
5. Re-verify remaining ~45s t2v / ~50s i2v before burn; do not assume ~1650s fresh trial.

## Upstream landed

- `dashscope-free-media-landed=1a683254959710ec85033dce0a164ee18ace4cb2`

## Next actions

- **Lane 03:** cite RECOMMENDATIONS 1–10 + decision matrix for vbank contract spec.  
- **Lane 04:** tooling — extend exempt client `media[]` for i2v first; r2v optional/gated.  
- **Lane 05:** operator-present burn; INTERIM provenance; sunset 2026-10-18.

## Cleanup ledger (Lane 02)

- Stage dir: `/private/tmp/manga_vbank_l02_stage/` — delete after merge confirmed.  
- Stale worktree `/private/tmp/wt-manga-vbank-l02` — remove/prune if still locked.  
- Branch `agent/manga-video-capability-research-20260724` — delete after squash-merge.  
- No code/config/governance touched.
