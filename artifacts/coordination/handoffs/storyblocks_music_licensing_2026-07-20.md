# Handoff — Storyblocks Music Licensing (Lane 04)

**Date:** 2026-07-20  
**Agent:** Pearl_Int  
**Lane:** 04_storyblocks_music_licensing_lane  
**STATUS:** LANDED-OFFLINE (GitHub origin HTTP 403 — account suspended)  
**Layer:** CODE-WIRED + mocked proof. **Not** EXECUTED-REAL (keys absent).

## SIGNAL

```
storyblocks-music-licensing-landed=<SHA>
```

(Replace `<SHA>` with tip after land; stamped below once pushed.)

## What landed

| Deliverable | Path |
|-------------|------|
| Mood → Audio query map | `config/social/mood_register_audio_query_map.yaml` |
| Additive Audio client | `scripts/storyblocks/api_client.py` → `search_audio`, audio download + `pick_hd_url` |
| Mood helpers | `scripts/storyblocks/mood_audio.py` |
| Bank layout | `artifacts/storyblocks_licensed/{work_unit_id}/audio/{asset_id}.{ext}` via `license_store.hd_path(..., media_type="audio")` |
| Confirm path | `confirm_download.confirm_selection` (audio counts toward same MAU) |
| Consumer wiring | `build_video_snippet_bank.build_snippet_bed` / `mux_with_bed` — licensed track when present, **sine fallback kept** |
| Tests | `tests/storyblocks/test_audio_music_licensing.py` (+ existing guards still green) |
| Proof | `artifacts/qa/storyblocks_music_licensing_20260720/` |

## Branch / remote

| Item | Value |
|------|-------|
| BRANCH | `agent/storyblocks-music-licensing-20260720` |
| Base | `agent/storyblocks-pearl-prime-20260720` @ `f0fd0b6fa6251ad4913b047a6a37a3559467d2c4` (origin/main `9e9b9e6067` lacks `scripts/storyblocks/*`) |
| Land remote | `pearlstar_offline` (not origin) |
| PR | Deferred until GitHub account unsuspended |

## Credentials (honest)

Missing: `STORYBLOCKS_PUBLIC_KEY`, `STORYBLOCKS_PRIVATE_KEY` (Keychain empty this session).  
Stage via `docs/storyblocks_keys.env` + `python3 scripts/storyblocks/install_keychain_creds.py`, then:

```bash
eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
```

Do **not** claim EXECUTED-REAL until a real confirm_selection audio download succeeds.

## Lane 03 integrator note

Lane 03 (`agent/storyblocks-video-provider-20260720`) was **not** on `pearlstar_offline` at Lane 04 start. Audio was added as **additive** `search_audio` (no shared generic search refactor). If Lane 03 later lands a generalized search/download, rebase/cherry-pick — do not duplicate.

## Lane 02 contract

Referenced for consumer wiring context:

- `config/social/semantic_keyword_taxonomy.yaml`
- `scripts/social/semantic_asset_selector.py`
- `artifacts/stock_image_bank/way_stream_sanctuary/mental_health_editorial_100x/asset_keywords.tsv`

Audio beds select by `mood_register` via `mood_register_audio_query_map.yaml`, not caption CTQC keywords.

## Proof summary

- pytest `tests/storyblocks/`: **19 passed**
- Smoke: one mood (`tense_anxious`) mocked search+confirm → `.../audio/SBA-tense_anxious.wav`
- Pilot: all 4 mood clusters, one work unit each; MAU distinct count = **1** (same locale-brand)
- Sine bed + mux ffprobe: video+audio streams OK
- Licensed trim path OK (mock WAV)

## CLEANUP LEDGER

- worktree: none retained (`/tmp/sb_lane04_wt` abandoned — full checkout hung; used GIT_INDEX_FILE / staging under `/tmp/sb_lane04_files`)
- local branch: `agent/storyblocks-music-licensing-20260720` (keep until PR)
- remote branch: `pearlstar_offline/agent/storyblocks-music-licensing-20260720`
- scratch files: `/tmp/sb_lane04_files`, `/tmp/sb_lane04_pytest.txt`, `/tmp/sb_lane04.index*` (safe to delete after land)
- background jobs: none
- held artifacts: proof root + this handoff on branch tip

## NEXT_ACTION

1. Operator: stage Storyblocks keys → live smoke one mood cluster.
2. Integrator: if Lane 03 lands generalized client, rebase this branch.
3. Scale only after operator review + keys confirmed.
4. When GitHub unsuspended: open PR from this branch (base should include pearl-prime substrate or squash chain).
