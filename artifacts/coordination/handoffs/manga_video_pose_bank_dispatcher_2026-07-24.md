# Manga video pose-bank dispatcher handoff — 2026-07-24

## Terminal state
- Lanes 01–04 + pack + Lane 07 audit: MERGED (this PR for 04/07 + OPD)
- Lanes 05–06: BLOCKED (ALLOW/Keychain; awaiting pilot signal)
- Stranded coord PR #339: close superseded by this PR

## Signals
- dashscope-free-media-landed=1a683254959710ec85033dce0a164ee18ace4cb2 (#310)
- manga-video-capability-research-merged=763439e36e0ffa6bbeb2898fd1aa5a954c120018 (#341)
- manga-video-pose-bank-spec-merged=4eca8bf19ca26a2234c4b7b2f1ca24d0f51917f9 (#345)
- manga-video-bank-tooling-merged=<fill-on-merge>
- manga-video-pose-bank-pilot-executed-real=ABSENT (BLOCKED)
- manga-video-pose-bank-dispatched=<fill-on-merge>

## Resume Lane 05 (operator-present)
```bash
eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
export PHOENIX_DASHSCOPE_FREE_MEDIA_ALLOW=1
bash artifacts/qa/manga_video_pose_bank_pilot_2026-07-24/BURN_COMMAND.sh
```
≤85s burn; ≥10s reserve; character mira_aoki; INTERIM provenance.
