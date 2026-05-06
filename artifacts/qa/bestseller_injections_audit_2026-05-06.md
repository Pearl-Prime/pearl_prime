# BESTSELLER-INJECTIONS-MANDATORY-01 Audit — Coverage Verification

**Date:** 2026-05-06  
**Cap entry:** BESTSELLER-INJECTIONS-MANDATORY-01 in docs/PEARL_ARCHITECT_STATE.md  
**Verdict:** PASS (canonical CLI defaults + grid wiring confirmed)

## Methodology

Inspected three load-bearing artifacts on origin/main via GitHub Contents API:
- `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` (canonical CLI)
- `phoenix_v4/planning/beatmap_compile.py` (`SOMATIC_10_SLOT_GRID` +
  `SOMATIC_FULL_RUNTIME_FORMATS`)
- `phoenix_v4/planning/enrichment_select.py` (waterfall + STORY-at-SCENE
  wiring)

## Findings

### Canonical CLI invocation (spec lines 565-585)

The spec declares the canonical invocation pattern:
```
python3 scripts/run_pipeline.py \
  --topic <topic> --persona <persona> \
  --arc <arc.yaml> --pipeline-mode spine \
  --runtime-format <format> \
  --quality-profile flagship \
  --no-job-check --render-book \
  --render-dir <out_dir>
```

Three quality profiles documented:
- `flagship` — verifies core structural gates hold on flow, book quality,
  scene originality
- `production` — every gate must pass for a release
- `draft` — for development iteration

`--exercise-journeys` is the opt-in flag for thesis-aligned exercise
attachment per `run_pipeline.py:618-621`.

### SOMATIC_10_SLOT_GRID (beatmap_compile.py)

Confirmed:
```
SOMATIC_10_SLOT_GRID = [
    "HOOK",          # section_01
    "STORY",         # section_02 — RECOGNITION arc-position
    "REFLECTION",    # section_03
    "EXERCISE",      # section_04 — awareness phase
    "STORY",         # section_05 — MECHANISM_PROOF arc-position
    "TEACHER_DOCTRINE", # section_06
    "REFLECTION",    # section_07
    "EXERCISE",      # section_08 — regulation phase
    "STORY",         # section_09 — TURNING_POINT arc-position
    "INTEGRATION",   # section_10
]
```

`SOMATIC_FULL_RUNTIME_FORMATS = {standard_book, extended_book_2h,
deep_book_4h, deep_book_6h}` use this grid in full.

**STORY at sec 2/5/9 is architecturally mandatory** at the grid level —
applies regardless of `--quality-profile`. This is per BG-PR-09
Phase-2-completed-by-PR-#669 (the canonical-CLI's SCENE-wiring fix).

### Profile-gated injections

`run_pipeline.py:1612-1617`:
```
quality_profile = args.quality_profile  # production | flagship | draft | debug
gates_run  = quality_profile in ("production", "flagship", "draft")
gates_hard = quality_profile == "production"
flagship_mode = quality_profile == "flagship"
```

Confirmed BESTSELLER-INJECTIONS-MANDATORY-01 ruling (option a):
- **Architecturally mandatory across all profiles:** STORY at sec 2/5/9
  via `SOMATIC_10_SLOT_GRID` (cannot be disabled)
- **Profile-gated for production:** quality gates harden via
  `gates_hard = quality_profile == "production"`
- **Opt-in via flag:** `--exercise-journeys` attaches thesis-aligned
  exercises to EXERCISE slots after depth pass

## No drift; no code change required

Canonical CLI defaults + grid wiring + profile-gating all match the
cap-entry ruling. Operator-facing commands in
`PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` align with what
`run_pipeline.py` actually does.

## Followup (informational; no ws spawn needed)

- **Default profile:** Currently `--quality-profile` has no documented
  default in the spec; CLI default is `production` per
  `run_pipeline.py` argparse. Consider explicit default-doc piggyback
  on next spec refresh.

## Closes

- `ws_bestseller_injections_audit_2026-05-06`

🤖 Generated with [Claude Code](https://claude.com/claude-code)
