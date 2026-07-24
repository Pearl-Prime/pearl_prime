# Lane 04 — Pearl_Dev — Capture tooling (`scripts/manga/video_bank/`)

EXECUTE. The turn ends only on `manga-video-bank-tooling-merged=<full merge SHA>` or one
concrete BLOCKER with pushed work.

GATE CHECK: `manga-video-pose-bank-spec-merged=<sha>` exists. STOP if missing.

STARTUP_RECEIPT: AGENT=Pearl_Dev, SUBSYSTEM=manga_pipeline,
WRITE_SCOPE=`scripts/manga/video_bank/` (NEW package), `tests/manga/test_video_bank_*.py` (NEW),
`scripts/social/dashscope_free_media.py` (ONLY if Lane 02 confirmed r2v/continuation free quota —
in-place client extension, nothing else), handoff. OUT_OF_SCOPE=assembler, schemas (Lane 03's),
gate_registry + `scripts/run_production_readiness_gates.py` (NO numbered gate in this pack — the
uplift program owns that surface right now; gate promotion is a declared follow-on),
`config/manga/*.yaml` (add NO new config file — parameters live in the capture manifest, which
is an artifact, keeping check_manga_wiring out of play), all uplift-pack paths.
PROVENANCE: research=Lane 02 doc; documents=Lane 03 supply spec + capture-manifest schema;
builds_on=`dashscope_free_media.py` client (exempt path), `make_object_sprite.py` INTERIM
pattern, `manga_cutout_toonout.py`/rembg backends, `bank_layer_blob_gate.py`,
`validate_layer.py`, `qa_face_distance.py`, `generate_bank_contracts_from_script.py` (read-only
consumer); inventory=EXTENDS.

## Read first
Lane 03's `MANGA_VIDEO_POSE_BANK_SUPPLY_SPEC.md` + schema (your implementation contract — zero
design decisions here); `scripts/social/dashscope_free_media.py` (client API);
`scripts/manga/make_object_sprite.py`; `scripts/manga/bank_layer_blob_gate.py`;
`scripts/manga/character_individuation/qa_face_distance.py`; `scripts/ci/audit_llm_callers.py`
usage in CLAUDE.md.

DISCOVERY REPORT before any write: verify the spec/schema landed as described, the client's
current function signatures, and that no sibling session touched `scripts/manga/video_bank/`.

## Mission — implement the spec, module by module

1. `compile_capture_manifest.py` — demand→capture compiler. Inputs per spec (rollup when signal
   exists / bank-contracts fallback — implement BOTH, selected by what exists on disk, recorded
   in the manifest's `demand_source` field). Output validates against Lane 03's schema.
2. `run_capture_burn.py` — capture runner. **Imports the client from
   `scripts.social.dashscope_free_media` — this file must contain ZERO DashScope endpoint
   patterns** (`X-DashScope-Async`, `/services/aigc/`) so the banned-patterns gate stays clean;
   verify with `python3 scripts/ci/audit_llm_callers.py` before push. Honors the same env gates
   (`PHOENIX_DASHSCOPE_FREE_MEDIA_ALLOW=1`, required `DASHSCOPE_FREE_QUOTA_API_KEY` per Lane 01's
   fix), `--preflight-only` mode, per-run quota ledger (seconds requested/spent/remaining written
   to the proof root), stub guard ≥50KB per clip, and a `--max-seconds` hard cap it refuses to
   exceed. Self-hosted engines are OUT of this lane (future work per Lane 02 matrix) — the
   runner's engine field must reject anything but the cloud engines Lane 02 confirmed.
3. `extract_frames.py` — ffmpeg candidate extraction at the spec's sampling rate + near-dup
   clustering + pose-phase tagging stubs per spec (deterministic, no LLM at runtime — Tier
   policy: this pipeline must run unattended later).
4. `make_pose_from_video_frame.py` — sibling of `make_object_sprite.py`: frame → cutout
   (ToonOut primary, rembg fallback per existing backends) → `_INTERIM` RGBA + `.provenance.json`
   (source clip, frame index, extraction command, REAL-replacement path) + `.composition.json`
   skeleton — byte-identical sidecar shapes to the existing precedents.
5. `validate_capture_frames.py` — the spec's ordered gate chain (class-A cutout gates via
   existing validators, blob gate, qa_face_distance ≤0.4 vs anchor, outfit-conformance,
   curation-to-demanded-pose_ids). Emits a per-frame verdict TSV; a REJECT is terminal.
6. Tests: golden-fixture manifest (tiny synthetic clip or checked-in frames ≤50KB total under
   `tests/fixtures/` — no LFS bloat), schema round-trip, banned-pattern absence test (grep own
   package for endpoint patterns = zero), quota-ledger math, gate-chain mutation tests (break a
   fixture frame's alpha → chain goes RED). `pytest -x` the package + touched suites.
7. r2v/continuation client extension in `dashscope_free_media.py` ONLY if Lane 02 confirmed free
   quota + API shape — minimal in-place addition mirroring `submit_video()`, with a test. If not
   confirmed: skip, and record `r2v: not-available` in the handoff.

Smoke→pilot→scale: unit fixtures → one synthetic end-to-end run (no cloud calls, canned clip) →
done. NO real quota spend in this lane (Lane 05's job; preflight-only against live API is allowed).

## DO NOT
- No new DashScope call sites outside the exempt client. No new exempt_paths. No burn.
- No numbered readiness gate, no gate_registry edits, no new config/manga YAML.
- No mass pose-inventory writes — registration happens in Lane 05's curated ingest only.
- No `git add -A`; plumbing/sparse-cone substrate per INDEX; poison protocol on any worktree.

## Landing contract
MERGED or BLOCKED-with-pushed-work. Cleanup ledger (fixtures in-tree or deleted; no scratch in
repo root). Handoff: `artifacts/coordination/handoffs/manga_video_pose_bank_lane04_2026-07-24.md`.
CLOSEOUT_RECEIPT + `SIGNAL: manga-video-bank-tooling-merged=<full merge SHA>`.
