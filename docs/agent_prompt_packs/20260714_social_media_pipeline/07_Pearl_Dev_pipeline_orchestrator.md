# L6 — Pearl_Dev — Pipeline orchestrator + weekly-package wiring (Wave 2)

Paste this whole block into the lane agent chat.

~~~text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_Dev for Phoenix Omega.

Repo: Ahjan108/phoenix_omega_v4.8
Start from a clean checkout of latest origin/main.

STARTUP_RECEIPT:
- AGENT=Pearl_Dev
- LANE=social-L6-orchestrator
- EXECUTION_MODE=github_actions (dry-run end-to-end; no live schedule/publish)
- BACKGROUND_SAFE=yes
- RUNTIME_HOST=cloud
- PERSISTENCE_SURFACES=branch/pr/artifact
- RESUME_SURFACE=scripts/social/run_social_pipeline.py

READ FIRST:
- docs/PROGRAM_STATE.md
- docs/SESSION_UNITY_PROTOCOL.md
- docs/agent_brief.txt
- docs/specs/SOCIAL_MEDIA_PIPELINE_MASTER_SPEC.md
- schemas/social/*.schema.json + the example manifest fixture
- scripts/build_weekly_brand_package.py (existing weekly R2/brand-admin package builder — you wire INTO it, reuse don't duplicate)
- the merged modules from L1/L2 (and L3/L4/L5 where landed)

LIVE STATE RECONCILIATION:
- verify BOTH social-extractor-merged=<sha> AND social-captions-metricool-merged=<sha> exist.
- check which of L3/L4/L5 have merged; the orchestrator must run with whatever is present and
  degrade gracefully for absent lanes (e.g. Canva BLOCKED → skip Canva variants, still emit plans+captions+payloads).

PRE-REQUISITE CHECKS:
- social-extractor-merged=<sha>  → if missing, STOP BLOCKED.
- social-captions-metricool-merged=<sha>  → if missing, STOP BLOCKED.
- (L3/L4/L5 optional — orchestrator handles their absence gracefully.)

DISCOVERY REPORT BEFORE ACTION:
- current origin/main SHA;
- which lanes are merged; what each module's entrypoint signature is (read the code live);
- how scripts/build_weekly_brand_package.py assembles the weekly manifest, so the social package slots in cleanly.

PROVENANCE:
- research: docs/research_social_media.txt (Part 10 — repurposing system: one chapter → full campaign)
- documents: SOCIAL_MEDIA_PIPELINE_MASTER_SPEC
- builds_on: L1 extractor/generator; L2 caption/validator/payload; L3 image; L4 canva; L5 video contract; scripts/build_weekly_brand_package.py
- inventory: EXTENDS (new orchestrator + weekly wiring); UNCHANGED for existing weekly package builder

MISSION (narrow):
Build scripts/social/run_social_pipeline.py — the end-to-end DRY-RUN orchestrator that chains:
extractor (L1) → static_generator (L1) → caption_adapter + media_validator + metricool_payload (L2)
→ image_render (L3, if present) → canva_render (L4, if present) → video_manifest (L5, if present),
emitting a complete per-book social_media_manifest.json + the Metricool draft payloads + rendered
pilot media. Wire the social package into the weekly R2/brand-admin manifest. autoPublish=false,
nothing scheduled live.

DELIVERABLES:
- scripts/social/run_social_pipeline.py — `--book <id> --dry-run` runs the whole chain, writes
  artifacts/social/pilot/<book_id>/social_media_manifest.json + metricool payloads + pilot media refs;
  `--platforms` selects the first-proof set; degrades gracefully for absent lanes.
- wiring into scripts/build_weekly_brand_package.py (add the social package to the weekly manifest, behind a flag, non-breaking).
- tests/test_run_social_pipeline.py — end-to-end fixture run asserts a valid manifest + all payloads autoPublish=false.
- artifacts/social/pilot/<book_id>/ — the one-book end-to-end proof.

SMALLEST SAFE BATCH:
- smoke: ONE book, --dry-run, STATIC-only path (skip image/video) → valid manifest + printed payload counts.
- pilot: ONE book, full chain with whatever lanes are present → complete manifest + pilot media + payloads. `open` the folder.
- scale: HOLD past one book until the operator look-approval + a follow-up scale dispatch. Do NOT loop over a catalog.

HANG PREVENTION:
- poll interval: CI every 2-3 min; the orchestrator itself is synchronous dry-run (no network).
- no-progress rule: if the chain errors on a lane boundary twice, isolate that lane with a fixture and inspect.
- hard stall: BLOCKED after three chain failures with the failing stage + error captured.
- max window: 120 min.
- HARD RULE: the orchestrator must NOT call live Metricool/Canva/publish paths in --dry-run; assert this in a test.

TESTS/PROOFS:
- pytest tests/test_run_social_pipeline.py -x
- assert: emitted manifest validates; every payload autoPublish=false; absent-lane degradation works.
- proof root: artifacts/social/pilot/<book_id>/

DO NOT:
- do NOT publish or schedule anything live;
- do NOT loop over the full catalog / attempt volume;
- do NOT duplicate the weekly package builder — extend it;
- do NOT edit 48_SOCIAL / ghl docs or coordination TSVs;
- no fake proof; no local-only finish; no giant batch first.

LANDING CONTRACT:
- MERGED: PR (orchestrator + weekly wiring + tests + one-book proof), checks green, squash-merged,
  `social-orchestrator-merged=<full-sha>` emitted.
- BLOCKED: exact blocker (which stage) + evidence + pushed branch + handoff.

CLEANUP LEDGER REQUIRED:
- worktree / local+remote branch / scratch files / background jobs / held artifacts (declare the pilot dir).

HANDOFF REQUIRED:
- artifacts/coordination/handoffs/social-L6-orchestrator_2026-07-14.md

CLOSEOUT_RECEIPT:
- AGENT: Pearl_Dev
- LANE: social-L6-orchestrator
- STATUS=MERGED|BLOCKED
- BRANCH / PR / MERGE_SHA:
- SIGNAL: social-orchestrator-merged=<full-sha>
- ACCEPTANCE_LAYER: EXECUTED-REAL for the one-book dry-run; NOT PROVEN (no live schedule; look-approval pending)
- PROOF_ROOT: artifacts/social/pilot/<book_id>/social_media_manifest.json
- TESTS / CLEANUP / HANDOFF / NEXT_ACTION:
- TOKEN: CLOSEOUT_RECEIPT::social-L6-orchestrator
~~~
