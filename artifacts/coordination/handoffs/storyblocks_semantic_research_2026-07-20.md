# Handoff — Storyblocks Semantic Research (Lane 01)

**Date:** 2026-07-20  
**Agent:** Pearl_Research  
**Lane:** 01_storyblocks_capability_research  
**STATUS:** LANDED-OFFLINE (GitHub origin HTTP 403 — account suspended)

## SIGNAL

```
storyblocks-taxonomy-recommended=ba3497fccfc97e24fa73caa182922fc9cf97d865
```

Branch tip (includes SIGNAL stamp): `0f37ac11af53503c2c4b6fa562d21be5162a16fd`  
pearlstar_offline: `0f37ac11af53503c2c4b6fa562d21be5162a16fd` (updated by this commit if tip moves)

## RECOMMENDED_TAXONOMY summary (Lane 02 can start)

**Method: Controlled Taxonomy Query Compiler (CTQC)**

Map atom fields `{topic, persona, hook_family, tone}` + `beat_role` → Storyblocks search params:

- `keywords` = topic primary visuals + hook_family boost + persona scene flavor + up to 2 concrete nouns from caption (never full prose)
- `required_keywords` = hard AND anchors (e.g. `anxious,office`)
- `filtered_keywords` = topic traps (festival/concert/party) + tone excludes
- duration from `BEAT_ROLE_DURATIONS`: hook/beat/endcard → short tagged clips; **value** → longer single clip (`min_duration≈6`, `max_duration≈20`)
- Rank: title/keyword overlap + duration proximity + model-release preference (+ optional **local CLIP on thumbnails only**, `embedding_purpose=selection_assist`)
- Audio: map `mood_register` clusters → `/api/v2/audio/search` with BPM/vocals filters

**Do not** send raw caption as `keywords`. **Do not** use paid cloud vision APIs. Extend existing `scripts/storyblocks/api_client.py` HMAC shape.

## Proof root

`artifacts/research/storyblocks_semantic_sourcing_20260720/`

- `RESEARCH_REPORT.md` — 5 mission points, cited
- `RECOMMENDED_TAXONOMY.md` — YAML tables + 3 worked atom examples (anxiety, burnout, boundaries)

## Branch / remote

| Item | Value |
|------|-------|
| BRANCH | `agent/storyblocks-semantic-research-20260720` |
| Base | `origin/main` `9e9b9e606791590337cd7d0f2fb425def2e6f760` |
| Research commit | `ba3497fccfc97e24fa73caa182922fc9cf97d865` |
| Land remote | `pearlstar_offline` (not origin) |
| PR | Deferred until GitHub account unsuspended |

## Locked decisions (do not re-ask)

OPD-SB-PP-01b / 02b / 03b — surface, identity, legal locked.

## CLEANUP LEDGER

- worktree: none retained (`/tmp/sb_lane01_wt` removed; used GIT_INDEX_FILE plumbing instead)
- local branch: `agent/storyblocks-semantic-research-20260720` (keep until PR)
- remote branch: `pearlstar_offline/agent/storyblocks-semantic-research-20260720`
- scratch files: removed `/tmp/sb_lane01.index`, `/tmp/sb_lane01.index2`
- background jobs: none
- held artifacts: research + handoff on branch tip only

## NEXT_ACTION

Lane 02: implement CTQC from `RECOMMENDED_TAXONOMY.md` as `config/social/storyblocks_query_taxonomy.yaml` + query compiler + ranker; extend `search_videos` kwargs + add `search_audio`; golden tests from the 3 examples.
