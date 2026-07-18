# L8 — Pearl_PM — Final production audit + operator packet (Wave 4)

Paste this whole block into the lane agent chat.

~~~text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_PM (auditor) for Phoenix Omega.

Repo: Ahjan108/phoenix_omega_v4.8
Start from a clean checkout of latest origin/main.

STARTUP_RECEIPT:
- AGENT=Pearl_PM
- LANE=social-L8-audit
- EXECUTION_MODE=github_actions (read-only audit + PROGRAM_STATE doc update)
- BACKGROUND_SAFE=yes
- RUNTIME_HOST=cloud
- PERSISTENCE_SURFACES=branch/pr/artifact
- RESUME_SURFACE=artifacts/qa/social_pipeline_audit_2026-07-14.md

READ FIRST:
- docs/PROGRAM_STATE.md
- docs/SESSION_UNITY_PROTOCOL.md
- docs/agent_brief.txt
- docs/specs/SOCIAL_MEDIA_PIPELINE_MASTER_SPEC.md + INDEX.md of this pack
- every lane handoff under artifacts/coordination/handoffs/social-L*_2026-07-14.md

LIVE STATE RECONCILIATION:
- verify ALL lane signals exist on origin/main: social-arch-merged, social-extractor-merged,
  social-captions-metricool-merged, social-image-lane-merged, social-canva-lane-merged (or
  -blocked), social-video-lane-merged, social-orchestrator-merged, social-qa-gates-merged.
- verify whether social-look-approved=<sha> exists. If NOT, the visual system stays labelled
  CODE-WIRED/EXECUTED-REAL — you may NOT label it PROVEN-AT-BAR. Surface the pending look-gate.

PRE-REQUISITE CHECKS:
- all lane signals present (Canva may be -blocked, which is acceptable and must be recorded).

DISCOVERY REPORT BEFORE ACTION:
- current origin/main SHA;
- the one-book proof: re-run scripts/social/run_social_pipeline.py --book <id> --dry-run yourself
  and confirm it emits a valid, gate-passing, safe manifest + draft payloads (autoPublish=false).

PROVENANCE:
- research: the whole provenance chain (research → docs → code) — verify it holds end to end
- documents: all pack specs + lane handoffs
- builds_on: every lane's merged output
- inventory: verify UNCHANGED — no existing subsystem regressed; the dictionary-diff / golden gates are green

MISSION (narrow):
Run the honest production audit. Verify the chain works on ONE real book end-to-end, that the
QA/ethics gates are RED-on-violation (spot-check L7's mutation evidence), that no lane claimed
"done" on gate-PASS alone, that nothing auto-publishes, and that the acceptance layer of EVERY
lane is labelled correctly. Assemble the operator packet and `open` the sample assets for the
Layer-4 look-read. Update PROGRAM_STATE.

DELIVERABLES:
- artifacts/qa/social_pipeline_audit_2026-07-14.md — per-lane acceptance-layer table
  (SPECCED/CODE-WIRED/EXECUTED-REAL/PROVEN-AT-BAR), the one-book proof result, gate mutation
  spot-check, auto-publish-OFF confirmation, Canva credential status, the pending look-gate, and
  the exact follow-up dispatch needed to scale (1-book → 1-brand).
- docs/PROGRAM_STATE.md — add a "Social Media Pipeline" track with the honest layer status and merge SHAs.
- an operator packet: the sample manifest + pilot images/canva/video paths, `open`ed for review.

SMALLEST SAFE BATCH:
- smoke: verify one signal + re-run the one-book dry-run.
- pilot: full per-lane audit table + gate mutation spot-check.
- scale: N/A (audit lane). Explicitly do NOT authorize a scale run — recommend it as a follow-up dispatch with the look-gate as its prerequisite.

HANG PREVENTION:
- poll interval: CI every 2-3 min for the PROGRAM_STATE PR.
- no-progress rule: inspect after two unchanged polls.
- hard stall: BLOCKED after three.
- max window: 90 min.

TESTS/PROOFS:
- scripts/social/run_social_pipeline.py --book <id> --dry-run  → valid gate-passing manifest, all payloads autoPublish=false
- python scripts/ci/check_social_content_gates.py <manifest>  → exit 0
- proof root: artifacts/qa/social_pipeline_audit_2026-07-14.md

DO NOT:
- do NOT label the visual system PROVEN-AT-BAR without social-look-approved;
- do NOT report the pipeline "done/shippable" on gate-PASS alone — name the layer every time;
- do NOT authorize scaling to a full brand / thousands in this lane;
- do NOT edit 48_SOCIAL / ghl docs;
- no fake proof; no local-only finish.

LANDING CONTRACT:
- MERGED: PR (audit doc + PROGRAM_STATE track), checks green, squash-merged,
  `social-pipeline-audit-complete=<full-sha>` emitted; operator packet `open`ed.
- BLOCKED: exact blocker (e.g. a lane signal missing / a gate false-green) + evidence + pushed branch + handoff.

CLEANUP LEDGER REQUIRED:
- worktree / local+remote branch / scratch files / background jobs / held artifacts;
- confirm every OTHER lane's cleanup ledger is complete (worktrees pruned, branches deleted, Pearl Star queue ids closed); flag any lane that left a mess.

HANDOFF REQUIRED:
- artifacts/coordination/handoffs/social-pipeline-final_2026-07-14.md (program-level closeout).

CLOSEOUT_RECEIPT:
- AGENT: Pearl_PM
- LANE: social-L8-audit
- STATUS=MERGED|BLOCKED
- BRANCH / PR / MERGE_SHA:
- SIGNAL: social-pipeline-audit-complete=<full-sha>
- ACCEPTANCE_LAYER (program): <the honest per-lane table's summary — e.g. engine CODE-WIRED, one-book EXECUTED-REAL, visual PROVEN only after look-approval>
- LOOK_GATE: social-look-approved present? yes/no
- NEXT_ACTION: the exact follow-up scale dispatch (1-book → 1-brand), gated on look-approval
- TOKEN: CLOSEOUT_RECEIPT::social-L8-audit
~~~
