# Handoff — Lane 03 Pearl_Writer: Evergreen Social Atom Bank Scale-Up, Wave 1

**Date:** 2026-07-21
**Agent:** Pearl_Writer (Claude, Tier-1 per CLAUDE.md LLM Tier Policy)
**Lane:** lane03_social_atom_bank_scaleup
**Prompt pack:** docs/agent_prompt_packs/20260721_evergreen_social_atom_bank_brand_author_scale/03_Pearl_Writer_atom_bank_scaleup.md

## Pre-requisite check (lane01 signal)

`social-atom-schema-v2=<sha>` was NOT found (no `artifacts/coordination/handoffs/lane01_social_atom_schema_registry_2026-07-21.md`,
no `brand_id`/`author_id`/`vibe_ref` in `docs/PEARL_SOCIAL_MEDIA_WRITER_AGENT_SPEC_2026-07-18.md`). Per the operator's
routing note, this lane authors `brand_id: null` (house-voice/universal) atoms by default regardless, so the new
schema fields are not required for these rows — they are simply omitted, which is forward-compatible with an
additive/nullable schema extension whenever Lane 01/02 (Cursor) lands. Proceeding was explicitly authorized by the
operator's routing message; not proceeding on Lane 03's own STOP clause would have idled this lane needlessly.

## Structural finding (bigger than this wave)

`SOURCE_OF_TRUTH/social_media_atoms/evergreen_en_us_atoms.jsonl` (and the rest of `SOURCE_OF_TRUTH/social_media_atoms/`)
has **never been committed to git** on any reachable `origin/main` lineage — it is a long-standing untracked file in
the working tree (1,620 pre-existing rows, ~2.95MB, `acceptance_layer` values already say "system working — promoted
SSOT" as if landed). This wave's commit is therefore the first time this canonical bank enters git history: it lands
the full 1,642-row file (1,620 pre-existing + 22 new), not a diff against a tracked baseline. No existing row content
was altered — verified by row count and a spot diff against the working-tree copy before staging.

## Discovery report

- **Current atom bank coverage:** 3 personas (`corporate_managers`, `gen_z_professionals`, `healthcare_rns`) x 20
  topics, ~27 atoms/cell, 1,620 rows total, using 9 of the 15 canonical atom families (`HOOK_COVER`, `SOMATIC_SETUP`,
  `PROBLEM_AGITATION`, `MECHANISM_EXPLAINER`, `REFRAME`, `TOOL_STEP`, `SAVEABLE_PAYOFF`, `CTA_ANCHOR`, `BRIDGE`).
- **Full persona matrix (SSOT: `config/catalog_planning/canonical_personas.yaml`):** 13 personas —
  `millennial_women_professionals`, `tech_finance_burnout`, `entrepreneurs`, `working_parents`, `gen_x_sandwich`,
  `corporate_managers`, `gen_z_professionals`, `healthcare_rns`, `gen_alpha_students`, `first_responders`,
  `gen_z_student`, `educators`, `midlife_women`. (A broader ad hoc grep across `config/**/*.yaml` surfaces ~40 more
  persona-like strings from teacher/duration/marketing configs, but those are book-planning personas, not the social
  writer's canonical persona list — out of scope for this lane's matrix.)
- **Gap:** 10 of 13 canonical personas have **zero** atoms today: `millennial_women_professionals`,
  `tech_finance_burnout`, `entrepreneurs`, `working_parents`, `gen_x_sandwich`, `gen_alpha_students`,
  `first_responders`, `gen_z_student`, `educators`, `midlife_women`. Matrix = 13 personas x 20 topics = 260 cells;
  200 are zero-coverage.
- **Thinnest families across the matrix:** `MICRO_STORY`, `CASE_PROOF`, `CAROUSEL_SLIDE`, `THREAD_UNIT`,
  `VIDEO_BEAT`, `LOCALIZATION_ADAPTER` — 0 atoms in any cell, English or otherwise, in this bank file.
- **Wave plan:** Wave A (this wave) = 1 zero-coverage cell, highest-frequency persona (`working_parents`) x
  highest-volume existing topic (`burnout`). Wave B+ = remaining 9 zero-coverage personas x `burnout`, then repeat
  across the other 19 topics, prioritizing topics already proven out for the 3 seeded personas.

## Wave 1 — `working_parents` x `burnout`

- **Atoms added:** 22 (`HOOK_COVER` x3, `SOMATIC_SETUP` x2, `PROBLEM_AGITATION` x2, `MECHANISM_EXPLAINER` x2,
  `REFRAME` x2, `TOOL_STEP` x3, `SAVEABLE_PAYOFF` x2, `CTA_ANCHOR` x3, `BRIDGE` x3).
- **Cell newly covered:** `working_parents` x `burnout` (previously zero atoms).
- **Families touched:** the 9 families already used in this bank (see above); the 6 unused families are an
  OPEN OPERATOR QUESTION below, not silently extended.
- **`brand_id`/`author_id`:** omitted (universal/house-voice default, per mission scope — brand-specific atoms are
  explicitly out of scope for this lane).
- **`review_status`:** `draft_operator_review_required` (honest — these rows are freshly authored, not yet reviewed;
  existing rows in this file use `reviewed_candidate`, which would misrepresent wave-1 rows' actual review state).
- **`source_refs`:** each row carries the existing `SRC_*` code convention plus an appended real quoted claim from
  `docs/research_social_media.txt` (line cited in each row), per this lane's stricter provenance requirement. Grounding
  claims used: the nervous-system/cortisol mechanism (line 3092), the "silent boundary" practice (line 3393), the
  "somatic check-in for parents" hook (line 3437), the "save this checklist... chest feels tight" CTA pattern (line
  3252), the identity-based share CTA pattern (line 3249), and the Scenario→Turning Point→Lesson→CTA story formula
  (line 3449).
- **Running total:** 1,642 rows (1,620 pre-existing + 22 new).

### Sample rows (3 of 22, full JSON)

```json
{"acceptance_layer": "authored candidate — evergreen extension, unscheduled", "atom_family": "HOOK_COVER", "atom_id": "EVG-ENUS-BURN-WKPR-HC-01", "awareness_stage": "problem_aware", "char_count": 104, "claim_risk": "low_no_medical_claim", "compatible_next": "SOMATIC_SETUP;PROBLEM_AGITATION;MECHANISM_EXPLAINER;REFRAME;TOOL_STEP;SAVEABLE_PAYOFF;CTA_ANCHOR;BRIDGE", "compatible_previous": "HOOK_COVER;SOMATIC_SETUP;PROBLEM_AGITATION;MECHANISM_EXPLAINER;REFRAME;TOOL_STEP;SAVEABLE_PAYOFF;BRIDGE", "cta_policy": "none", "culture_risk": "low_en_us_general", "draft_only": true, "first_fold_chars": 104, "hook_family": "identity_based", "incompatible_with": "medical_cure_claims;shame_language;unsupported_statistics;caption_clone_reuse", "link_policy": "no_main_body_external_link", "locale": "en-US", "market_fit": "en-US", "objective": "trust_authority", "persona": "working_parents", "platform_fit": "instagram;facebook;linkedin;tiktok_reels_shorts;youtube;pinterest;x;threads;google_business", "reuse_cooldown_days": 14, "review_status": "draft_operator_review_required", "source_refs": "SRC_ENGLISH_RESEARCH — the \"that is exactly what I am experiencing\" self-relevance effect determines whether a reader pauses on a hook. (docs/research_social_media.txt:220-253)", "surface_fit": "static_caption;carousel;thread;short_video_script;business_update", "text": "working parents: the second shift starts the second the car door closes, and nobody clocks you in for it.", "tone": "direct honest", "topic": "burnout", "word_count": 20}
{"acceptance_layer": "authored candidate — evergreen extension, unscheduled", "atom_family": "TOOL_STEP", "atom_id": "EVG-ENUS-BURN-WKPR-TS-02", "awareness_stage": "ready_to_act", "char_count": 148, "claim_risk": "low_no_medical_claim", "compatible_next": "SOMATIC_SETUP;PROBLEM_AGITATION;MECHANISM_EXPLAINER;REFRAME;TOOL_STEP;SAVEABLE_PAYOFF;CTA_ANCHOR;BRIDGE", "compatible_previous": "HOOK_COVER;SOMATIC_SETUP;PROBLEM_AGITATION;MECHANISM_EXPLAINER;REFRAME;TOOL_STEP;SAVEABLE_PAYOFF;BRIDGE", "cta_policy": "none", "culture_risk": "low_en_us_general", "draft_only": true, "first_fold_chars": 125, "hook_family": "practical_tool", "incompatible_with": "medical_cure_claims;shame_language;unsupported_statistics;caption_clone_reuse", "link_policy": "no_main_body_external_link", "locale": "en-US", "market_fit": "en-US", "objective": "trust_authority", "persona": "working_parents", "platform_fit": "instagram;facebook;linkedin;tiktok_reels_shorts;youtube;pinterest;x;threads;google_business", "reuse_cooldown_days": 14, "review_status": "draft_operator_review_required", "source_refs": "SRC_ENGLISH_RESEARCH — \"The moment I created a 'silent boundary'—turning off all inputs at 7 PM—my health began to recover.\" (docs/research_social_media.txt:3393)", "surface_fit": "static_caption;carousel;thread;short_video_script;business_update", "text": "Run a silent boundary tonight: pick one 20-minute window after the kids are down where every input stays off. Not the whole evening, one window, protected on purpose.", "tone": "direct honest", "topic": "burnout", "word_count": 30}
{"acceptance_layer": "authored candidate — evergreen extension, unscheduled", "atom_family": "CTA_ANCHOR", "atom_id": "EVG-ENUS-BURN-WKPR-CA-02", "awareness_stage": "ready_to_act", "char_count": 68, "claim_risk": "low_no_medical_claim", "compatible_next": "SOMATIC_SETUP;PROBLEM_AGITATION;MECHANISM_EXPLAINER;REFRAME;TOOL_STEP;SAVEABLE_PAYOFF;CTA_ANCHOR;BRIDGE", "compatible_previous": "HOOK_COVER;SOMATIC_SETUP;PROBLEM_AGITATION;MECHANISM_EXPLAINER;REFRAME;TOOL_STEP;SAVEABLE_PAYOFF;BRIDGE", "cta_policy": "platform_native_only", "culture_risk": "low_en_us_general", "draft_only": true, "first_fold_chars": 68, "hook_family": "practical_tool", "incompatible_with": "medical_cure_claims;shame_language;unsupported_statistics;caption_clone_reuse", "link_policy": "no_main_body_external_link", "locale": "en-US", "market_fit": "en-US", "objective": "lead_generation", "persona": "working_parents", "platform_fit": "instagram;facebook;linkedin;tiktok_reels_shorts;youtube;pinterest;x;threads;google_business", "reuse_cooldown_days": 14, "review_status": "draft_operator_review_required", "source_refs": "SRC_ENGLISH_RESEARCH — \"Save this checklist to refer back to next time your chest feels tight.\" Directly influences the most heavily weighted metric for reference content. (docs/research_social_media.txt:3252)", "surface_fit": "static_caption;carousel;thread;short_video_script;business_update", "text": "Save this for the next time your chest feels tight before you walk in the door.", "tone": "calm professional", "topic": "burnout", "word_count": 16}
```

## Test-chain proof

54 distinct assemblable `HOOK_COVER -> SOMATIC_SETUP -> TOOL_STEP -> CTA_ANCHOR` chains exist within the 22 new
rows (script-verified against each row's `compatible_previous`/`compatible_next` values), well above the "at least 3"
bar in the mission.

## Tests run (per wave)

- `python3 -c "import json; [json.loads(l) for l in open(...)]"` — 1,642 rows parse clean, 0 duplicate `atom_id`s.
- Test-chain script (see above) — 54 chains found.
- `generate_copy_package('working_parents', 'burnout', 'instagram_carousel', format_family='carousel')` in
  `phoenix_v4/social/deterministic_social.py` — returns a non-error, non-empty package. **Caveat, reported honestly:**
  this composer does not currently read `SOURCE_OF_TRUTH/social_media_atoms/*.jsonl` at all — it synthesizes copy from
  a separate `persona_profile`/`topic_profile` bank (falls back to a generic template for personas/topics not in that
  bank, which is why it doesn't error on `working_parents`). Wiring the atom bank into this composer is the Lane
  02/04 (Cursor) wiring gap, not something this wave could close from the authoring side.
- `PYTHONPATH=. python3 scripts/git/push_guard.py` — Push-guard OK.
- `scripts/ci/preflight_push.sh` — Preflight OK.

## OPEN OPERATOR QUESTION

Six of the 15 canonical atom families (`MICRO_STORY`, `CASE_PROOF`, `CAROUSEL_SLIDE`, `THREAD_UNIT`, `VIDEO_BEAT`,
`LOCALIZATION_ADAPTER`) have zero rows anywhere in this bank, English or otherwise. Recommended default: treat this
as a known, pre-existing gap (not something wave 1 needs to fill) and let future waves add these families
per-cell once the 9-family baseline covers more of the matrix — flagging per the mission's "do not unilaterally
extend the taxonomy" instruction, since this is a coverage gap within the existing 15, not a request for a 16th
family.

## NEXT_ACTION (remaining cells)

Wave 2+: the other 9 zero-coverage personas x `burnout` (`millennial_women_professionals`, `tech_finance_burnout`,
`entrepreneurs`, `gen_x_sandwich`, `gen_alpha_students`, `first_responders`, `gen_z_student`, `educators`,
`midlife_women`), then the same 10-persona set across the remaining 19 topics (`anxiety`, `overthinking`,
`imposter_syndrome`, `grief`, `self_worth`, `shame`, `depression`, `relationship_anxiety`, `social_anxiety`,
`sleep_anxiety`, `boundaries`, `courage`, `financial_anxiety`, `compassion_fatigue`, `body_image`, `money`,
`addiction`, `adhd`, `divorce`). 190 zero-coverage cells remain after this wave.
