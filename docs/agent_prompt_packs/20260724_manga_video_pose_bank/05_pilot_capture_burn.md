# Lane 05 — Pearl_Dev — Pilot: one character through the whole loop on real free quota

EXECUTE. The turn ends only on
`manga-video-pose-bank-pilot-executed-real=<full merge SHA> verdict=<method_better|method_worse|inconclusive>`
or one concrete BLOCKER with pushed work. A scorecard with no assembled panels is NOT terminal;
"clips generated" is NOT terminal.

GATE CHECK: `manga-video-bank-tooling-merged=<sha>` exists AND `OPD-20260724-VBANK-01` (quota-GO)
is logged. The physical burn additionally requires the operator-present env
(`PHOENIX_DASHSCOPE_FREE_MEDIA_ALLOW=1` + `DASHSCOPE_FREE_QUOTA_API_KEY` — Keychain loader per
CLAUDE.md; the key gate hard-fails if the free key is absent, by design). If the env gate cannot
be satisfied in this session, package the EXACT burn command block for the operator, run
everything up to the burn in `--preflight-only`, and land as BLOCKED with that as the named
blocker + NEXT_ACTION — that is the one legitimate BLOCKED shape for this lane.

STARTUP_RECEIPT: AGENT=Pearl_Dev, SUBSYSTEM=manga_pipeline,
WRITE_SCOPE=`artifacts/qa/manga_video_pose_bank_pilot_2026-07-24/` (proof root — clips, frames,
scorecard, SUMMARY.md), quota ledger, handoff; **series-bank ingest is a SEPARATE serialized
step** (below). OUT_OF_SCOPE until the ingest step's own gate: `config/source_of_truth/
manga_profiles/series/*.character_pose_inventory.yaml`, `artifacts/manga/<series>/image_bank/`.
PROVENANCE: research=Lane 02; documents=Lane 03 spec; builds_on=Lane 04 tooling + existing
stillness anchors; inventory=EXTENDS.

DISCOVERY REPORT before any spend: live quota remaining (burn_summary + preflight), anchor
assets byte-verified, uplift Lane 11 liveness (sets the ingest protocol), tooling SHAs.

## Pilot definition (Q-VBANK-02 default: mira_aoki / stillness_press, one outfit)
- **Demand:** compile the capture manifest from the stillness golden master plan (uplift Lane 06
  PR #331 / merged main) + existing `bank_contracts/` — via Lane 04's compiler, recording
  `demand_source`. If `manga-bank-demand-rollup-merged` exists by now, use the rollup.
- **Anchors:** existing PuLID reference / model-sheet assets for mira_aoki (byte-verify they
  exist; if the outfit reference is missing, render it on Pearl Star via the existing
  Qwen-Image/PuLID path, RAP queue-first — NOT cloud stills).
- **Budget:** ≤ 85 seconds of cloud video total (t2v+i2v+r2v combined), ≥10s reserve for
  retakes; live-check remaining quota first (burn_summary + a 1-clip preflight). Batch ALL clip
  prompts before the first real submit. Per-clip 5s default.
- **Capture program:** 3–4 action families from the manifest (identity/dialogue reel, locomotion,
  seated, one genre beat) — i2v from the same anchor for every clip (r2v/VACE-reference instead
  if Lane 04 landed it). Neutral background, locked camera, full body, per Lane 03 prompt rules.
- **Harvest:** extract → gate chain → curated INTERIM pose slice (target 15–25 validated pose
  assets, ONLY demanded pose_ids). Every clip and frame byte-verified (≥50KB clips; real PNGs).
- **Assembly proof:** 3–5 panels via `scripts/manga/assemble_from_bank.py` using the new pose
  assets (INTERIM-labeled, offline, no GPU), from real episode manifests where possible.
- **Scorecard (the deliverable that decides Lane 06):** pairwise `qa_face_distance` across the
  pose slice + vs anchor; outfit-conformance count; gate-chain yield (frames in → validated out);
  quota spent per validated pose; side-by-side vs the EXISTING baseline (current PuLID-stills L2
  poses for mira_aoki) on the same metrics; assembled-panel visual set. Honest verdict:
  `method_better` only if identity+outfit metrics beat baseline AND yield makes the quota math
  work at scale; else `method_worse` or `inconclusive` with the specific failure.

## Serialized ingest step (after scorecard, before closeout)
Registering curated pose_ids into `stillness_en_01.character_pose_inventory.yaml` + copying
assets into the series `image_bank/L2/mira_aoki/` collides with uplift Lane 11's write scope.
Protocol: check whether Lane 11 is live (branch/PR per its pack). If live → DEFER ingest,
declare it in the closeout as a HOLD with exact paths + resume command; the proof root already
preserves everything. If not live → land the ingest as its own small PR (pose-inventory rows +
assets + sidecars; plumbing pattern; §6.8 budget respected), then proceed to closeout.

## Watchdog
Poll async video tasks synchronously (the client's poller); per-clip timeout 600s; 3 consecutive
no-progress clips = stop burning, preserve, report. Never park a watcher. `open` the proof root
for the operator as the last step (auto-open rule).

## DO NOT
- Never exceed the budget or drain the quota to zero. Never spend cloud STILL quota on anchors.
- Never present INTERIM assets as final art; every asset carries provenance + note.
- Never write the series bank/inventory outside the serialized ingest step.
- Never repair a failed frame downstream — reject and (budget permitting) retake.

## Landing contract
MERGED (proof root + scorecard + SUMMARY.md landed by PR; ingest landed or HOLD-declared) or the
one legitimate BLOCKED shape above. Cleanup ledger (tmp frames deleted; clips retained in proof
root are DECLARED). Handoff: `artifacts/coordination/handoffs/manga_video_pose_bank_lane05_2026-07-24.md`.
CLOSEOUT_RECEIPT + quota ledger +
`SIGNAL: manga-video-pose-bank-pilot-executed-real=<full merge SHA> verdict=<...>`.
Acceptance layer: at most **EXECUTED-REAL** — never claim more.
