# Handoff — Lane 03 manga video pose-bank contract (spec + schemas)

**Date:** 2026-07-24  
**Agent:** Pearl_Architect(+Pearl_Dev)  
**Status:** MERGED (see CLOSEOUT / SIGNAL after land)  
**Acceptance layer:** SPECCED

## Deliverables

| Path | Purpose |
|------|---------|
| `docs/specs/MANGA_VIDEO_POSE_BANK_SUPPLY_SPEC.md` | NEW — supply-lane authority (demand→capture, gates, provenance, ladder, quota) |
| `schemas/manga/character_capture_manifest.schema.json` | NEW — capture manifest schema; golden in supply spec §2.5 validates |
| `docs/specs/MANGA_LAYER_RENDER_CONTRACT_SPEC.md` | EDIT in place — §4.6 A-claim + §19 cross-ref (no renumber of existing §§) |
| `artifacts/coordination/handoffs/manga_video_pose_bank_lane03_2026-07-24.md` | This handoff |

## Gates verified

- `dashscope-free-media-landed=1a683254959710ec85033dce0a164ee18ace4cb2`
- `manga-video-capability-research-merged=763439e36e0ffa6bbeb2898fd1aa5a954c120018`
- Uplift 09/11 NOT started → supply spec uses **bank_contracts fallback** for demand→capture

## Lane 02 RECOMMENDATIONS cited (binding)

1. Pilot = `wan2.7-i2v` + canonical external still  
2. Skip r2v unless free seconds proven  
3. Scale = VACE-1.3B Apache on Pearl Star  
4. DashScope = INTERIM; Apache Wan/VACE = REAL-eligible after gates  
5. Sunset 2026-10-18

## Discovery (extension points)

- Continuity cardinality: `MANGA_CONTINUITY_STATE_SPEC.md` §8 (former layer-contract §6.8)
- INTERIM pattern: `scripts/manga/make_object_sprite.py`
- Panel ingress: `assembly_manifest.schema.json` L0–L4 only — assembler untouched
- Pose inventory EXISTS on stillness / warrior_calm / cognitive_clarity — EXTEND only

## Registry REQUEST (Lane 07)

- NEW: `MANGA_VIDEO_POSE_BANK_SUPPLY_SPEC.md`
- NEW: `character_capture_manifest.schema.json`
- EDIT note: layer-contract §19 / §4.6 A-claim
- Do **not** add gate_registry rows this pack

## Next actions

- **Lane 04:** implement `scripts/manga/video_bank/` from this contract; fixture from §2.5 golden; extend exempt client `media[]` for i2v first  
- **Lane 05:** operator burn; INTERIM provenance  
- **Lane 06:** ratify identity-ladder + §15.A.1 wording after verdict  

## Cleanup ledger (Lane 03)

- Stage dir: `/private/tmp/manga_vbank_l03_stage/` — delete after merge confirmed  
- Temp index / `GIT_INDEX_FILE` leftovers under `/private/tmp/manga_vbank_l03_*` — remove  
- Branch `agent/manga-video-pose-bank-spec-20260724` — delete after squash-merge  
- No code / config/manga / gate_registry / V5 architecture / registry TSV touched  
