# Lane 07 — Pearl_PM — Final audit + SSOT update

EXECUTE. The turn ends only on `manga-video-pose-bank-audited=<full merge SHA>` or one concrete
BLOCKER with pushed work.

GATE CHECK: signals for Lanes 01–06 all exist (`dashscope-free-media-landed`,
`manga-video-capability-research-merged`, `manga-video-pose-bank-spec-merged`,
`manga-video-bank-tooling-merged`, `manga-video-pose-bank-pilot-executed-real`,
`manga-lora-lane-disposition-merged`). A BLOCKED lane with pushed work + declared HOLD counts as
terminal for audit purposes — audit it as BLOCKED, never paper over it.

STARTUP_RECEIPT: AGENT=Pearl_PM, SUBSYSTEM=manga_pipeline + coordination,
WRITE_SCOPE=`docs/PROGRAM_STATE.md` (manga row), `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`
(pack rows → completed/blocked), `artifacts/coordination/CANONICAL_ARTIFACTS_REGISTRY.tsv`
(REQUESTED rows from Lanes 03/04: supply spec, capture-manifest schema, video_bank package —
with edit_not_recreate flags), `docs/DOCS_INDEX.md` (two rows: supply spec + research doc),
audit doc `artifacts/qa/manga_video_pose_bank_audit_2026-07-24/AUDIT.md`, handoff.
ALL of these are SERIAL hot files — one writer; if uplift Lane 12 is mid-write, serialize.
PROVENANCE: none (audit/coordination).

## Mission
1. **Re-verify every lane's claims against live `origin/main`** — byte-level where claimed:
   merge SHAs resolve; clips/frames/panels in the pilot proof root exist at the byte floors;
   the quota ledger's arithmetic matches burn_summary.json; the key-fallback regression test
   exists and fails under mutation; Lane 04's package contains zero banned endpoint patterns
   (`grep` + `python3 scripts/ci/audit_llm_callers.py`); the assembler was NOT modified
   (`git diff <pack-start-sha>..origin/main -- scripts/manga/assemble_from_bank.py` = empty);
   `banned_llm_patterns.yaml` exempt_paths gained NO new entries beyond Lane 01's scope note.
2. **Acceptance-layer table** in AUDIT.md — one row per deliverable, honest labels:
   research=RESEARCHED, spec/schema=SPECCED, tooling=CODE-WIRED, pilot assets=EXECUTED-REAL,
   LoRA disposition=governance. Nothing PROVEN-AT-BAR; state explicitly that blind-10 (M6) is
   untouched and the capture bank feeds it.
3. **PROGRAM_STATE manga row**: append the V-Bank subsection — signals + SHAs, pilot verdict,
   quota remaining + sunset date, the INTERIM/REAL provenance posture, LoRA disposition, and the
   declared follow-ons (self-hosted scale lane per Lane 02 matrix; catalog blocked_lora taxonomy
   migration; gate promotion for the frame gate chain after the uplift waves settle; deferred
   ingest HOLD if Lane 05 left one).
4. **Coordination closure**: workstream rows to terminal states; OPD rows complete
   (VBANK-00..04); registry + DOCS_INDEX rows landed; stale-premise correction — if any pack
   premise proved false (e.g. r2v quota), correct THE SOURCE doc in the same pass (banner, not
   buried).
5. Auto-open the audit doc + pilot proof root for the operator (`open <paths>`) as the last step.

## DO NOT
- Never report a lane done without its re-verified SHA. Never say "all checks pass" — name them.
- Never upgrade an acceptance layer to make the closeout read better.

## Landing contract
MERGED (coordination PR, plumbing, staged-diff gate) or BLOCKED-with-pushed-work. Cleanup ledger
covering the WHOLE pack (every lane's declared HOLDs re-listed — silence = mess). Handoff:
`artifacts/coordination/handoffs/manga_video_pose_bank_lane07_2026-07-24.md`.
CLOSEOUT_RECEIPT + `SIGNAL: manga-video-pose-bank-audited=<full merge SHA>`.
