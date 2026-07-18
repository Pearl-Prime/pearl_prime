# Beat-Driven Builder — run_pipeline Wiring + v3_* Retirement (FOLLOW-ON SPEC)

**Status:** DRAFT / DEFERRED. Authored 2026-06-16 by Pearl_Video (lane E).
**Predecessor PR:** `scripts/video/build_beat_driven.py` + `tests/video/test_build_beat_driven.py`
(the standalone canonical builder — landed first, deliberately NOT wired into `run_pipeline`).

This note specifies the **second, consequential** step that was intentionally kept out of the
builder PR because it flips `run_pipeline.py`'s default path — exactly the change that stalled an
earlier attempt. Treat it as its own scoped PR with its own test sweep.

---

## Why this is a separate PR

`scripts/video/build_beat_driven.py` is a self-contained module:

- It **consumes** the merged `scripts/video/run_frame_judge.py` public API (judge gate, keep-best).
- It emits a `distribution_manifest.json` that `scripts/video/build_daily_batch.py::discover_queue_items`
  already discovers and `score_candidate` already scores (verified — round-trip test passes).
- It has **no** import or runtime dependency on `run_pipeline.py`.

So the builder ships and is fully exercised on its own. Wiring it into `run_pipeline.py` is a
**default-path change** with blast radius across the whole VCE test surface, and must be validated
as its own unit of work.

### Regressions observed in the prior (stalled) attempt — DO NOT REPEAT

An earlier draft modified `run_pipeline.py` in ways that go well beyond "add a beat_driven route":

1. **Default-flip of `--pipeline-mode` to `beat_driven`.** A CLI-default flip breaks every test
   that invokes the entrypoint without the flag (cf. memory: "Default-flip test under-count" — a
   single CI snapshot under-counts the breakage; trust pytest's full-run N-failed count).
2. **Default-flip of `--skip-render` from `False` → `True`.** Same hazard, different flag; silently
   changes what a bare `run_pipeline.py` invocation produces.
3. **Banned-LLM doc/behaviour drift.** The draft rewrote `--voice`/`--music` help text to claim
   **ElevenLabs** ("Generate background music via ElevenLabs (costs $)") and **deleted** the
   CosyVoice2-CJK / Edge-TTS free-TTS locale-routing block. That both regresses behaviour and risks
   tripping `.github/workflows/llm-policy-enforcement.yml` (paid-API policy). The free/local TTS
   path is the SSOT per CLAUDE.md tier policy — keep it.

The builder PR reverts `run_pipeline.py` to `origin/main` entirely. This follow-on re-introduces
ONLY the additive beat-driven route, with NONE of the above default-flips or TTS drift.

---

## Scope of THIS follow-on PR

### A. Additive route in `run_pipeline.py` (no default-flip)

- Add `--pipeline-mode {vce,beat_driven}` with **`default="vce"`** (the established path stays the
  default — additive, not a flip).
- Add `--beats`, `--audio`, `--brand-id`, `--skip-judge` args (beat-driven inputs only).
- Add a `_run_beat_driven(args)` delegation that builds a `BeatVideoConfig` and calls
  `BeatDrivenBuilder(config).build()`. Auto-skip render+judge when `COMFYUI_URL` is unset (CI-safe).
- Activate the route ONLY when `--pipeline-mode beat_driven` AND `--beats` are both given; otherwise
  fall through to the unchanged VCE pipeline.
- **Do not touch** `--skip-render` default, `--voice`/`--music` help text, or the free-TTS routing.

### B. The route test

Re-add `test_run_pipeline_beat_driven_route_emits_manifest` (removed from the builder PR's test
file with a pointer to this spec). It subprocess-invokes `run_pipeline.py --pipeline-mode beat_driven
--beats … --no-job-check` with `COMFYUI_URL=""` and asserts a publish-queue manifest is emitted.

### C. Full default-path regression sweep (gate before merge)

Because even an additive arg can perturb argparse help / mutually-exclusive groups, run the FULL
suite, not a snapshot:

```bash
PYTHONPATH=. python3 -m pytest tests/video -q
PYTHONPATH=. python3 -m pytest tests/test_video_pipeline_regression.py tests/test_vce_stages.py -q
```

Sweep **every** `run_pipeline.py` invocation in the repo (tests + CI workflows + docs) and confirm a
bare invocation still selects the VCE path. Trust pytest's N-failed count over any single diagnosis.

### D. v3_* retirement (sequenced AFTER A–C land green)

Once the canonical builder is the wired path, retire the per-version one-offs:

- `scripts/video/intelligent_v3_6_pipeline.py`, `intelligent_v3_7_pipeline.py` — judge/rewrite/render
  logic is now in `run_frame_judge.py`; orchestration is in `build_beat_driven.py`.
- `scripts/video/build_v3_*_yt_starseed.py` family — superseded by `build_beat_driven.py`
  (beat plan → master-prompt seed-locked render → judge gate → best-of → assemble).
- `scripts/video/assemble_v3_8.py` / `build_frame_selector_v2.py` — keep until the W4 generalized
  operator best-of selector (`--frames-dir --manga-dir --versions --out-csv`, per
  `PEARL_VIDEO_FRAME_SELECTOR_BEST_OF_V1_SPEC.md`) replaces them; that is its own lane.

Retirement = move to an `archive/` or delete with a tombstone, AND update any importers. Check
`grep -rl 'intelligent_v3_\|build_v3_' scripts tests .github` first — these are local-only one-offs
today, but verify no CI/test importer before deleting (cf. the RunComfy decommission lesson: a
"2-driver" footprint was really ~9 importers).

---

## Acceptance for the follow-on PR

- `--pipeline-mode` defaults to `vce`; a bare `run_pipeline.py` is byte-for-byte behaviour-identical
  to pre-PR.
- `--pipeline-mode beat_driven --beats <f>` emits a publish-queue manifest (route test green).
- Full `tests/video` + VCE regression suites green (no default-flip fallout).
- No `ElevenLabs`/paid-API strings introduced; free-TTS routing untouched; LLM-policy CI green.
- v3_* retirement only after the route lands and importer-grep is clean.
