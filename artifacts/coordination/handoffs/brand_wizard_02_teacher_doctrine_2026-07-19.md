# Handoff — Lane 02 · Teacher exclusivity + named→doctrine fallback · 2026-07-19

**Agent:** Pearl_Editor (+ Pearl_Dev)  
**STATUS:** partial (pipeline generalized path FIXED + mini EXECUTED proof; full spine
chord production book BLOCKED)  
**Offline parent tip at land:** `9756ebbc8890f7e9fb656ee54d1fee7238d5c454`  
**Shared tree:** `codex/realist-social-samples-20260718` (never switched)

## Routing verdict

| Behavior | Layer | Result |
|---|---|---|
| One-teacher-per-market exclusivity | EXECUTED-REAL (sim) | Second claim → **409 teacher_claimed** |
| Onboarding → generalized assign | ABSENT | Ledger rejects; does not route doctrine mode |
| Pipeline `--teacher-attribution=generalized` | CODE-WIRED + mini EXECUTED | Wrapper+enrichment path proven |
| Full spine chord 2-book production | BLOCKED | G-DEF4 (healthcare_rns) / coverage(20 vs 12) / time |

## Fixes landed (this commit)

1. `phoenix_v4/rendering/teacher_wrapper.py` — `attribution_mode` named|generalized|auto
2. `phoenix_v4/planning/enrichment_select.py` — `_teacher_attribution_mode` +
   `_suppress_named_teacher_in_body` for generalized
3. `scripts/run_pipeline.py` — `--teacher-attribution` + skip named pre-intro when generalized
4. `phoenix_v4/rendering/section_packet_composer.py` — thread attribution_mode
5. `config/catalog_planning/teacher_wrapper_templates.yaml` — master_feung=Taoist,
   master_wu=warrior (was swapped)

**Did not touch** `brand_onboarding.py` / wizard HTML / brand-director (lanes 01/03).

## Evidence

`artifacts/qa/brand_wizard_teacher_doctrine_verify_20260719/`

- `exclusivity_sim_result.json` — A named claim OK; B 409
- `wrapper_mode_smoke.json` — named has Master Feung; gen name=0 + Taoist
- `book_a.txt` / `book_b.txt` (+ named/generalized aliases) — mini proof books
- `name_occurrence_report.json` — A name=2, B name=0, doctrine markers both
- `atom_gap_fill_report.json` — coverage clones were created then **rolled back**
  (not needed for mini proof; not committed)
- `DISCOVERY_REPORT.md`

## name_occurrence_report (summary)

- Book A named: `master_feung_name_count=2`, Taoist markers present
- Book B generalized: `master_feung_name_count=0`, Taoist markers present
- Asserts all true in report JSON

## Atom sufficiency

master_feung TEACHER_DOCTRINE + SCENE/HOOK pools exist and are non-stub
(CONFIG-EXISTS → EXECUTED in mini proof). Full production coverage wants 20/slot
(have 12) — gap for spine chord, not for wrapper mechanism.

## NEXT_ACTION (follow-on render lane)

1. Wire wizard/client on 409 `teacher_claimed` → offer **composite brand with
   `teacher_attribution=generalized` + same `teacher_id`** (or new onboarding field),
   not silent drop to regular mode. Spec: do not mutate brand_onboarding exclusivity
   ledger; add response payload suggesting generalized doctrine route.
2. Full spine chord proof cell: prefer persona matching topic registry (avoid G-DEF4),
   e.g. after registry persona alignment OR use draft gates only for mechanism QA.
3. Either reduce coverage required for modular short formats OR author +8 atoms/slot
   for master_feung (declared bank-fill lane) — do not clone silently for catalog ship.
4. Re-run:  
   `run_pipeline.py --teacher master_feung --teacher-attribution named|generalized
   --pipeline-mode spine --quality-profile production --exercise-journeys
   --output-format five_min_practice --render-book`  
   Save book.txt under evidence dir; refresh name_occurrence_report.

## Cleanup

- Hung `run_pipeline` killed; scratch_render removed
- Synthetic claim data never written to real `artifacts/onboarding/`
- Coverage clone atoms removed (50)
- Disk ~25 GiB free at closeout
- No worktrees; shared branch unchanged
