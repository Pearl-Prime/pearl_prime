# Lane 06 — Pearl_Architect — LoRA-lane disposition (verdict-gated cleanup)

EXECUTE. The turn ends only on `manga-lora-lane-disposition-merged=<full merge SHA>` or one
concrete BLOCKER with pushed work.

GATE CHECK: `manga-video-pose-bank-pilot-executed-real=<sha> verdict=<v>` exists. The lane runs
on ANY verdict — the verdict selects the branch below. STOP only if the signal is absent.

STARTUP_RECEIPT: AGENT=Pearl_Architect, SUBSYSTEM=manga_pipeline,
WRITE_SCOPE=`docs/PEARL_ARCHITECT_STATE.md` (cap amendment — SERIAL hot file, claim via
dispatcher), `docs/specs/MANGA_100PCT_PRODUCTION_ROADMAP_2026-07-03.md` (M5 clause),
`docs/specs/MANGA_LAYER_RENDER_CONTRACT_SPEC.md` (§15.A.2 wording — coordinate with Lane 03's
earlier edit; re-read at HEAD), `config/manga/brand_lora_plans.yaml` (header banner ONLY),
`artifacts/coordination/operator_decisions_log.tsv`, workstream-row REQUEST via closeout.
OUT_OF_SCOPE=catalog scripts (`generate_manga_catalog.py`, `v1_1_allocation_to_batch_plan.py`,
`build_final_launch_report.py`) and their `blocked_lora` status taxonomy — migrating those
columns is a DECLARED FOLLOW-ON, not this lane; `main_character_lora_id` in ~1,771 book-plan
YAMLs (identity token only, no asset behind it — leave alone); all research artifacts (never
delete research). PROVENANCE: research=Lane 05 scorecard; documents=MANGA-LAYERED-PIPELINE-V2-01
cap (PEARL_ARCHITECT_STATE lines ~818–857), Q-MANGA-04 record; builds_on=those; inventory=
**REDUCED for the LoRA phases — authorized by operator ruling Q-VBANK-04 (log the OPD row in the
same commit)**; everything else UNCHANGED.

## Ground truth you inherit (verified 2026-07-24 — re-verify)
Zero trained `.safetensors` anywhere; zero LoraLoader nodes in any ComfyUI workflow; no training
code; the 140 lora_refs reference PNGs from the 2026-04-24 manifest absent. LoRA is already
fallback-only per Q-MANGA-04 + roadmap M5. Retirement is spec/status surgery, not code removal.

## Branch on verdict
**verdict=method_better (expected):**
1. **Cap amendment** `MANGA-LAYERED-PIPELINE-V2-01-AMENDMENT-2026-07-24-VBANK`: phases C6
   (per-character LoRAs), C7 (brand-style LoRAs), B8 (i2L eval) → status **retired-conditional**
   ("not planned; last-resort only if PuLID + capture-bank fails a flagship blind-read bar");
   identity ladder recorded as PuLID + video-capture pose bank (primary) → LoRA (last resort).
   Cite the pilot scorecard path + SHAs. Close `ws_manga_v2_phase_c_register_genre_loras_20260507`
   (REQUEST the row update via dispatcher).
2. **Roadmap M5**: update the LoRA fallback clause to point at the capture-bank supply lane +
   supply spec; add the supply spec to M5's reference list.
3. **§15.A.2**: identity-gate precondition becomes `{PuLID-active OR capture-bank-validated OR
   per-character-LoRA-trained}` — surgical wording edit, consistent with Lane 03's new §.
4. **`brand_lora_plans.yaml`**: prepend a header banner — `status: planning-frozen (2026-07-24)`,
   superseded-for-identity-by pointer to the supply spec, catalog-metadata consumers explicitly
   still valid (the file stays; columns keep working). Do NOT restructure the YAML body.
5. OPD rows: `OPD-20260724-VBANK-04` (retirement ruling applied) + verdict citation.
6. Declared follow-on (in handoff + closeout): catalog `blocked_lora` status-taxonomy migration
   to capture-bank equivalents — scoped, not executed here.

**verdict=method_worse or inconclusive:** NO retirement. Land instead: a dated addendum on the
cap entry recording the pilot result + why LoRA phases stay as-is + what would re-trigger the
question (specific metric bars). OPD row logging the outcome. The signal still emits — the
disposition IS the deliverable, whichever way it goes.

## DO NOT
- Do not delete brand_lora_plans.yaml, any research artifact, or any catalog column.
- Do not touch check_manga_wiring exemptions or `anatomical_correction_loras.yaml` (declared
  research-only — out of scope).
- Do not edit PEARL_ARCHITECT_STATE while another session holds it — dispatcher arbitrates;
  re-root on race.

## Landing contract
MERGED or BLOCKED-with-pushed-work; plumbing substrate; staged-diff gate shows exactly the
intended files. Cleanup ledger. Handoff:
`artifacts/coordination/handoffs/manga_video_pose_bank_lane06_2026-07-24.md`.
CLOSEOUT_RECEIPT + `SIGNAL: manga-lora-lane-disposition-merged=<full merge SHA>`.
