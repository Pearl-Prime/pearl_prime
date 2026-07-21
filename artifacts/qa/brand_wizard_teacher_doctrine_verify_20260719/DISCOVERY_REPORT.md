# DISCOVERY REPORT — Lane 02 teacher exclusivity + doctrine fallback

## (a) Onboarding second claimant

`server/routes/brand_onboarding.py` L348–368: when `<lane>__<teacher_tid>` already
claimed by a different email → **HTTP 409** `{"error":"teacher_claimed",...}`.
Does **not** assign generalized mode. Comment: client falls back to a composite brand.

Simulated: `exclusivity_sim_result.json` — claim A submit, claim B 409.

## (b) How decision reaches pipeline

**Before this lane:** no flag forced `teacher_wrapper` into generalized for a second
claimant who still wants that teacher's doctrine. Ledger only blocks named claim.

**After this lane (fix):** `--teacher-attribution=generalized` →
`book_spec.teacher_attribution_mode` → EnrichmentRequest `spine_context` →
`apply_wrapper(..., attribution_mode=...)` / `resolve_wrapper`. Named pre-intro
skipped when generalized. Teacher atom bodies have display-name suppressed.

## (c) Atom source by mode

Same bank: `SOURCE_OF_TRUTH/teacher_banks/<tid>/approved_atoms/`. Mode changes
**wrapper attribution** (+ body name suppress in generalized). There is no separate
tradition-only atom pool (CONFIG-EXISTS tradition slots in templates; EXECUTED via
wrapper + doctrine bodies).

## (d) Proof teacher

`master_feung` / `qi_foundation_en_us` — Taoist energy cultivation
(`teacher_brand_map.yaml` vitality_path; brand_admin_brands.json).
