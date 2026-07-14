# L3 — Pearl_Int — Image lane: Pearl Star + book covers + PIL overlay (Wave 1, look-gated)

Paste this whole block into the lane agent chat.

~~~text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_Int for Phoenix Omega.

Repo: Ahjan108/phoenix_omega_v4.8
Start from a clean checkout of latest origin/main.

STARTUP_RECEIPT:
- AGENT=Pearl_Int
- LANE=social-L3-image
- EXECUTION_MODE=pearl_star_remote (RAP queue-first for FLUX) + local PIL compositing
- BACKGROUND_SAFE=yes (code + queue dispatch; renders are queued, not blocking)
- RUNTIME_HOST=cloud (dispatch) + Pearl Star (GPU)
- PERSISTENCE_SURFACES=branch/pr/artifact/queue-id
- RESUME_SURFACE=artifacts/social/pilot/<book_id>/images/

READ FIRST:
- docs/PROGRAM_STATE.md
- docs/SESSION_UNITY_PROTOCOL.md
- docs/agent_brief.txt
- docs/ROBUST_AGENT_PROTOCOL.md  (RAP — queue-first mandatory for Pearl Star GPU work >10s)
- docs/specs/SOCIAL_MEDIA_PIPELINE_MASTER_SPEC.md
- schemas/social/social_media_asset.schema.json + the example manifest fixture
- REUSE TARGETS: artifacts/waystream/cover_pilot/compose_cover.py (FLUX+PIL two-stage),
  phoenix_v4/manga/covers/ (cover generator/assembler), scripts/pearl_star/bin/pscli (queue)

LIVE STATE RECONCILIATION:
- verify social-arch-merged=<sha>.
- check Pearl Star queue health (artifacts/coordination/PEARL_STAR_QUEUE_HEALTH_PACKET_*.md);
  if the queue is jammed/down, you may still land CODE + a mock render, and declare the live
  render BLOCKED on queue — do not hang waiting on GPU.

PRE-REQUISITE CHECKS:
- social-arch-merged=<sha>  → if missing, STOP BLOCKED.

DISCOVERY REPORT BEFORE ACTION:
- current origin/main SHA;
- locate the flagship book's EXISTING cover(s) — operator wants imagery SOURCED FROM BOOK COVERS
  where sufficient, not always freshly generated. List what covers exist for the pilot book.
- confirm the two-stage rule (memory): FLUX generates IMAGERY only; PIL composites TEXT. Never bake text via FLUX.
- disk precheck (>=20 GB free) before any worktree; use GIT_LFS_SKIP_SMUDGE=1 + sparse cone if you make one.

PROVENANCE:
- research: docs/research_social_media.txt (Part 6 — quote graphics/carousels/typography)
- documents: SOCIAL_MEDIA_PIPELINE_MASTER_SPEC + STATIC_SOCIAL Visual Direction / Color & Typography
- builds_on: artifacts/waystream/cover_pilot/compose_cover.py; phoenix_v4/manga/covers/; pscli queue
- inventory: EXTENDS (new social image_render module reusing cover compositor); UNCHANGED for covers/manga

MISSION (narrow):
Build the IMAGE renderer for static social assets. For each image media_ref in a manifest,
produce a mobile-legible PNG at the correct per-platform dimensions (IG 1080x1350, Pinterest
1000x1500, LinkedIn, FB, etc.), by either (a) sourcing/adapting an EXISTING book cover, or
(b) queueing a FLUX imagery gen on Pearl Star (RAP queue-first), then compositing text via
PIL (two-stage). Emit the rendered files + update the manifest's media_refs.

DELIVERABLES:
- phoenix_v4/social/image_render.py — resolves each image asset to a PNG (cover-source path OR
  FLUX-queue path), composites text with PIL per platform_specs dimensions, writes to artifacts/social/pilot/<book_id>/images/.
- config/social/image_render_config.yaml — per-platform canvas sizes, safe zones, typography
  system mapping (somatic/strategic/spiritual/warm per STATIC_SOCIAL), brand-mark rules. (L3's file.)
- tests/test_social_image_render.py — deterministic PIL compositing tests (fixed inputs → fixed dimensions/regions; assert file bytes >0 and correct size).
- artifacts/social/pilot/<book_id>/images/ — PILOT renders (proof root).

SMALLEST SAFE BATCH:
- smoke: ONE quote-with-commentary card sourced from an EXISTING flagship cover + PIL text overlay. Byte-verify (>0, correct WxH).
- pilot: ONE 9-slide carousel's images (mix of cover-sourced + 1-2 FLUX-queued). Byte-verify each. `open` the folder for the operator.
- scale: HOLD. Do NOT render the full book's image set or move toward volume until the operator
  emits `social-look-approved=<sha>`. State this explicitly in your closeout.

HANG PREVENTION:
- poll interval: Pearl Star queue every 5 min (check artifact count + queue status via pscli).
- no-progress rule: after two unchanged polls, inspect the queue/worker logs (setfacl/orphaned-'doing' patterns are known — see memory).
- hard stall: after three unchanged polls, mark the live render BLOCKED-on-queue, land CODE + a mock/placeholder render, do NOT keep waiting.
- max window: 90 min for dispatch+pilot; GPU render is async via queue, not a blocking wait.

TESTS/PROOFS:
- pytest tests/test_social_image_render.py -x
- byte-verify: every pilot PNG >0 bytes and matches its platform canvas size (no stub-as-done).
- proof root: artifacts/social/pilot/<book_id>/images/  (declare as HELD for operator look-approval)

DO NOT:
- do NOT bake text into FLUX prompts (two-stage rule: FLUX imagery, PIL text);
- do NOT mark a render "ok/done" with <50KB bytes or a missing file (stub-as-done is CI-blocked elsewhere; do not create the pattern here);
- do NOT scale past the pilot before `social-look-approved`;
- do NOT bypass the Pearl Star queue (RAP queue-first);
- do NOT edit 48_SOCIAL / ghl docs or coordination TSVs;
- no fake proof; no local-only finish.

LANDING CONTRACT:
- MERGED: PR (image_render.py + config + tests + PILOT images), checks green, squash-merged,
  `social-image-lane-merged=<full-sha>` emitted; pilot image dir declared as HELD for look-approval.
- BLOCKED: exact blocker (e.g. Pearl Star queue down) + evidence + pushed branch + handoff;
  land the CODE + mock render even when the live GPU path is blocked.

CLEANUP LEDGER REQUIRED:
- worktree removed/HOLD; local+remote branches; scratch files; Pearl Star queue ids (stopped or declared);
  held artifacts: artifacts/social/pilot/<book_id>/images/ (declared, for operator look-read).

HANDOFF REQUIRED:
- artifacts/coordination/handoffs/social-L3-image_2026-07-14.md
- heartbeat if >15 min: artifacts/coordination/heartbeats/social-L3_2026-07-14.md (queue id, last artifact count, next poll).

CLOSEOUT_RECEIPT:
- AGENT: Pearl_Int
- LANE: social-L3-image
- STATUS=MERGED|BLOCKED
- BRANCH / PR / MERGE_SHA:
- SIGNAL: social-image-lane-merged=<full-sha>
- ACCEPTANCE_LAYER: EXECUTED-REAL for the pilot bytes; NOT PROVEN-AT-BAR (needs operator look-approval)
- PROOF_ROOT: artifacts/social/pilot/<book_id>/images/
- LOOK_GATE: pilot rendered; awaiting social-look-approved before scale
- TESTS / CLEANUP / HANDOFF / NEXT_ACTION:
- TOKEN: CLOSEOUT_RECEIPT::social-L3-image
~~~
