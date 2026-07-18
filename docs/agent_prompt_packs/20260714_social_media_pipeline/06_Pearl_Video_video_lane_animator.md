# L5 — Pearl_Video — Video lane: Pearl Animator wiring + contract (Wave 1)

Paste this whole block into the lane agent chat.

~~~text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_Video for Phoenix Omega (video lane; drives the pearl-animator agent for renders).

Repo: Ahjan108/phoenix_omega_v4.8
Start from a clean checkout of latest origin/main.

STARTUP_RECEIPT:
- AGENT=Pearl_Video
- LANE=social-L5-video
- EXECUTION_MODE=github_actions (in-repo contract) + local Remotion (operator-run pilot render)
- BACKGROUND_SAFE=yes for the in-repo contract; NO for the render (Tier-1 operator-present)
- RUNTIME_HOST=cloud (contract) + local ~/<brand>_video (render)
- PERSISTENCE_SURFACES=branch/pr/artifact
- RESUME_SURFACE=phoenix_v4/social/video_manifest.py

READ FIRST:
- docs/PROGRAM_STATE.md
- docs/SESSION_UNITY_PROTOCOL.md
- docs/agent_brief.txt
- docs/specs/SOCIAL_MEDIA_PIPELINE_MASTER_SPEC.md
- schemas/social/social_media_asset.schema.json + example manifest fixture
- ~/.claude/agents/pearl-animator.md (the animator agent's scope + hard Remotion rules)
- config/video/ + docs/specs/PEARL_VIDEO_BEAT_DRIVEN_NARRATIVE_PIPELINE_V1_SPEC.md (existing video subsystem — reuse, don't duplicate)

CRITICAL SCOPE CONSTRAINT (read twice):
Pearl Animator is Tier-1, OPERATOR-PRESENT, lives OUTSIDE this repo (~/<brand>_video Remotion
projects), and is explicitly NOT a cloud-scale batch renderer. Therefore in THIS cloud dispatch
you deliver: (a) the in-repo CONTRACT that maps manifest video-asset rows → Remotion input props;
(b) the scene TEMPLATE spec + template components; (c) a documented ONE-video PILOT that the
OPERATOR runs locally and reviews. You do NOT batch-render video in the cloud, and you do NOT
claim any video "done" without the operator having seen a render (per the animator agent's rules).

LIVE STATE RECONCILIATION:
- verify social-arch-merged=<sha>; read schemas live.
- confirm whether an existing video pipeline (config/video/, scripts/video/) already produces the
  60s/Shorts/TikTok MP4s referenced by the 48_SOCIAL spec — if so, your job is the SOCIAL-CLIP
  wiring on top (trim/caption/CTA-overlay props), NOT a new renderer. Reconcile before building.

PRE-REQUISITE CHECKS:
- social-arch-merged=<sha>  → if missing, STOP BLOCKED.

DISCOVERY REPORT BEFORE ACTION:
- current origin/main SHA;
- does ~/<brand>_video exist for the pilot brand? (pearl_prime_video exists per router discovery.)
- which video assets are in first proof (Q-SOCIAL-04 default: IG Reels + YT Shorts + TikTok, 9:16, per platform_specs durations);
- reuse map: existing video pipeline outputs vs. new social-clip props.

PROVENANCE:
- research: docs/research_social_media.txt (Part 5 — short-form video production, first-frame, script structure)
- documents: SOCIAL_MEDIA_PIPELINE_MASTER_SPEC + pearl-animator agent spec + existing video pipeline spec
- builds_on: existing config/video pipeline; the Remotion project ~/<brand>_video; L0 schemas
- inventory: EXTENDS (social-clip contract + templates); UNCHANGED for the existing video pipeline

MISSION (narrow):
Build the video CONTRACT + templates that connect the pipeline's manifest to Pearl Animator,
and prove ONE operator-run pilot render per first-proof format.

DELIVERABLES:
- phoenix_v4/social/video_manifest.py — emits schema-valid social_video_manifest rows (per asset:
  platform, format=reel/short/tiktok, duration, 9:16, source_clip or scene-template id, on-screen
  hook text, caption, CTA-overlay text, safe-zone spec) from a social_media_manifest.
- docs/specs/SOCIAL_VIDEO_ANIMATOR_WIRING_SPEC.md — exact mapping: manifest row → Remotion input
  props → composition; the first-frame + script-structure defaults from research Part 5; the
  operator run commands. Add NEW-ARTIFACT-JUSTIFIED (new social-video wiring, distinct from beat-driven pipeline).
- Remotion scene template(s) in ~/<brand>_video (local project) — a parametric social-clip
  composition driven entirely by input props (per animator hard rules: useCurrentFrame/interpolate only).
- tests/test_social_video_manifest.py — the contract emitter is CI-tested (fixture manifest → valid video manifest).
- artifacts/social/pilot/<book_id>/video/PILOT_RENDER_INSTRUCTIONS.md — the exact operator steps + 1 rendered sample path.

SMALLEST SAFE BATCH:
- smoke: emit ONE social_video_manifest row from the example manifest; validate it; assert 9:16 + duration within platform_specs.
- pilot: render ONE IG Reel (operator-run, local) from the template + that row; operator reviews it. Capture the sample path.
- scale: HOLD. Batch/multi-format video is operator-present work in a follow-up, NOT this cloud dispatch. State this.

HANG PREVENTION:
- poll interval: CI every 2-3 min for the contract; the render is operator-run (not a cloud wait).
- no-progress rule: if the contract emitter fails twice, reduce to the single-row smoke.
- hard stall: BLOCKED after three contract failures with the error captured.
- max window: 90 min for the in-repo contract. Do NOT block the cloud turn waiting on a local render — hand the render to the operator with instructions and land the contract.

TESTS/PROOFS:
- pytest tests/test_social_video_manifest.py -x
- the emitted video manifest validates against its schema; durations/aspect within platform_specs.
- proof root: artifacts/social/pilot/<book_id>/video/ (contract + instructions; the actual MP4 is operator-produced).

DO NOT:
- do NOT batch-render video in the cloud or claim a video is final without an operator-seen render;
- do NOT mix brands in one Remotion project (one brand = one ~/<brand>_video);
- do NOT fabricate a rendered MP4 you did not produce (stub-as-done);
- do NOT edit 48_SOCIAL / ghl docs or coordination TSVs;
- no fake proof; no local-only finish for the IN-REPO contract (that must land MERGED).

LANDING CONTRACT:
- MERGED: PR (video_manifest.py + wiring spec + tests + pilot instructions) MERGED, checks green,
  `social-video-lane-merged=<full-sha>` emitted. The Remotion template + rendered sample are declared
  as the local/HELD artifacts (outside repo git — reference by path).
- BLOCKED: exact blocker + evidence + pushed branch + handoff.

CLEANUP LEDGER REQUIRED:
- worktree / local+remote branch / scratch files / background jobs / held artifacts
  (declare ~/<brand>_video social-clip template + the pilot MP4 path).

HANDOFF REQUIRED:
- artifacts/coordination/handoffs/social-L5-video_2026-07-14.md

CLOSEOUT_RECEIPT:
- AGENT: Pearl_Video
- LANE: social-L5-video
- STATUS=MERGED|BLOCKED
- BRANCH / PR / MERGE_SHA:
- SIGNAL: social-video-lane-merged=<full-sha>
- ACCEPTANCE_LAYER: CODE-WIRED (contract + templates); EXECUTED-REAL only for the one operator-reviewed pilot render; NOT batch-proven
- PROOF_ROOT: artifacts/social/pilot/<book_id>/video/ + ~/<brand>_video template path
- TESTS / CLEANUP / HANDOFF / NEXT_ACTION:
- TOKEN: CLOSEOUT_RECEIPT::social-L5-video
~~~
