# L2 — Pearl_Int — Caption adapter + media validator + Metricool payload (Wave 1)

Paste this whole block into the lane agent chat.

~~~text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_Int for Phoenix Omega.

Repo: Ahjan108/phoenix_omega_v4.8
Start from a clean checkout of latest origin/main.

STARTUP_RECEIPT:
- AGENT=Pearl_Int
- LANE=social-L2-captions
- EXECUTION_MODE=github_actions   (fixture-driven; NO live Metricool calls in CI)
- BACKGROUND_SAFE=yes
- RUNTIME_HOST=cloud
- PERSISTENCE_SURFACES=branch/pr
- RESUME_SURFACE=phoenix_v4/social/metricool_payload.py

READ FIRST:
- docs/PROGRAM_STATE.md
- docs/SESSION_UNITY_PROTOCOL.md
- docs/agent_brief.txt
- docs/specs/SOCIAL_MEDIA_PIPELINE_MASTER_SPEC.md
- schemas/social/*.schema.json (esp. metricool_payload + social_media_manifest) + the example manifest fixture
- docs/INTEGRATION_CREDENTIALS_REGISTRY.md (Metricool credential location — do NOT hardcode keys)
- the operator expert brief captured by L0 (platform specs table + PLATFORM_RULES dict)

LIVE STATE RECONCILIATION:
- verify social-arch-merged=<sha>; read schemas live.
- confirm no config/social/platform_specs.yaml or platform_rules.yaml exists yet (this lane authors them).

PRE-REQUISITE CHECKS:
- social-arch-merged=<sha>  → if missing, STOP BLOCKED.

DISCOVERY REPORT BEFORE ACTION:
- current origin/main SHA;
- confirm Metricool credential name in the registry (do not print the value);
- list the platforms in scope for first proof (Q-SOCIAL-04 default: IG, LinkedIn, Pinterest, FB static;
  IG Reels, YT Shorts, TikTok video) — Threads/Bluesky config-ready, X deferred.

PROVENANCE:
- research: docs/research_social_media.txt (Part 8 — technical specs) + operator expert brief
- documents: SOCIAL_MEDIA_PIPELINE_MASTER_SPEC; 48_SOCIAL spec §"Metricool API Integration" (READ-ONLY reference)
- builds_on: L0 schemas; PLATFORM_RULES + platform spec tables from the brief
- inventory: EXTENDS phoenix_v4/social (new caption/validator/payload modules); UNCHANGED elsewhere

MISSION (narrow):
Turn the expert brief into config + three modules: (1) a CAPTION ADAPTER that rewrites the
Instagram-source caption for each target platform per PLATFORM_RULES (char limits, hashtag
count/placement, tone, emoji, length instruction); (2) a MEDIA VALIDATOR that checks each
media_ref against config/social/platform_specs.yaml (format, size, aspect ratio, duration)
BEFORE any upload; (3) a METRICOOL PAYLOAD builder that emits a schema-valid
/v2/scheduler/posts payload with autoPublish=false (draft only) and per-platform *Data blocks.
NO live API calls in this lane — everything is fixture/`--dry-run` and prints the payload.

DELIVERABLES:
- config/social/platform_specs.yaml — image/video/reels/story specs per platform (from the brief's tables), each row "verified_as_of: 2026-07-14".
- config/social/platform_rules.yaml — PLATFORM_RULES caption rules per platform (from the brief).
- phoenix_v4/social/caption_adapter.py — source→per-platform caption adaptation.
- phoenix_v4/social/media_validator.py — validate media_ref vs platform_specs; returns pass/fail + reason.
- phoenix_v4/social/metricool_payload.py — build /v2/scheduler/posts payload (autoPublish=false); credential read from Keychain/env at RUNTIME only, never in code/CI.
- tests/test_social_caption_adapter.py + test_social_media_validator.py + test_social_metricool_payload.py (fixture-driven).

SMALLEST SAFE BATCH:
- smoke: adapt ONE caption IG→LinkedIn (assert char limit + hashtag rules); build ONE Metricool
  payload from the example manifest fixture; print it (autoPublish=false).
- pilot: adapt one asset across all 6 first-proof platforms; validate 6 media_refs; build 6 payloads.
- scale: run the full example manifest through all three modules (still dry-run).

HANG PREVENTION:
- poll interval: CI every 2-3 min.
- no-progress rule: inspect after two unchanged CI polls.
- hard stall: BLOCKED after three.
- max window: 120 min.
- HARD RULE: if any code path would make a LIVE Metricool/network call, it must be behind an
  explicit --live flag that is OFF by default and never set in CI — otherwise BLOCKED. No blind waits on network.

TESTS/PROOFS:
- pytest tests/test_social_caption_adapter.py tests/test_social_media_validator.py tests/test_social_metricool_payload.py -x
- assert every generated payload has autoPublish=false and validates against metricool_payload.schema.json
- proof root: the tests + a printed sample payload saved to artifacts/social/pilot/metricool_payload_sample.json

DO NOT:
- do NOT hardcode or print any API key/token;
- do NOT make live scheduling calls or publish anything;
- do NOT copy the 48_SOCIAL spec's hashtag numbers as gospel — the research file says verify them; encode current values with verified_as_of dates;
- do NOT edit 48_SOCIAL / ghl docs or coordination TSVs;
- no fake proof; no local-only finish; no giant batch first.

LANDING CONTRACT:
- MERGED: PR (2 configs + 3 modules + tests + sample payload), checks green, squash-merged,
  `social-captions-metricool-merged=<full-sha>` emitted.
- BLOCKED: exact blocker (e.g. missing Metricool credential name) + evidence + pushed branch + handoff.

CLEANUP LEDGER REQUIRED:
- worktree / local branch / remote branch / scratch files / background jobs / held artifacts.

HANDOFF REQUIRED:
- artifacts/coordination/handoffs/social-L2-captions_2026-07-14.md

CLOSEOUT_RECEIPT:
- AGENT: Pearl_Int
- LANE: social-L2-captions
- STATUS=MERGED|BLOCKED
- BRANCH / PR / MERGE_SHA:
- SIGNAL: social-captions-metricool-merged=<full-sha>
- ACCEPTANCE_LAYER: CODE-WIRED (dry-run payloads valid; live scheduling NOT proven — that is a later operator step)
- PROOF_ROOT: tests + artifacts/social/pilot/metricool_payload_sample.json
- TESTS / CLEANUP / HANDOFF / NEXT_ACTION:
- TOKEN: CLOSEOUT_RECEIPT::social-L2-captions
~~~
