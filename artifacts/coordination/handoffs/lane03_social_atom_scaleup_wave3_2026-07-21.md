# Handoff — Lane 03 Pearl_Writer: Evergreen Social Atom Bank Scale-Up, Wave 3

**Date:** 2026-07-21
**Agent:** Pearl_Writer (Claude, Tier-1 per CLAUDE.md LLM Tier Policy)
**Lane:** lane03_social_atom_bank_scaleup
**Prior waves:** [wave1](lane03_social_atom_scaleup_wave1_2026-07-21.md), [wave2](lane03_social_atom_scaleup_wave2_2026-07-21.md)
(both MERGED via [PR #7](https://github.com/Pearl-Prime/pearl_prime/pull/7), sha `1dfc4e6695d419f2d5a60f3c2bf80b9ff846c783`)

## Wave 3 — `gen_x_sandwich` x `burnout`

- **Atoms added:** 22 (`HOOK_COVER` x3, `SOMATIC_SETUP` x2, `PROBLEM_AGITATION` x2, `MECHANISM_EXPLAINER` x2,
  `REFRAME` x2, `TOOL_STEP` x3, `SAVEABLE_PAYOFF` x2, `CTA_ANCHOR` x3, `BRIDGE` x3) — same 9-family mix as waves 1-2.
- **Cell newly covered:** `gen_x_sandwich` x `burnout` (previously zero atoms) — the sandwich-generation persona
  (caring for children and aging parents simultaneously).
- **`brand_id`/`author_id`:** omitted (universal/house-voice default).
- **`review_status`:** `draft_operator_review_required`.
- **`source_refs`:** existing `SRC_*` codes plus a real quoted claim from `docs/research_social_media.txt` per row.
  Grounding claims used: "caring for everyone else... no idea what you actually want" (line 3432), "who is carrying
  the emotional labor" (line 3435), "the hyper-responsible mother" (line 3438), "the hyper-responsible child usually
  grows into an adult who feels personally responsible for the emotional comfort of every room they enter" (line
  2721), "it is safe to let go of the emotional labor today" (line 3757), the save-checklist CTA (line 3252), and
  the identity-based share CTA (line 3249).
- **Running total:** 1,686 rows (1,664 after wave 2 + 22 new).

### Sample rows (3 of 22, full JSON)

```json
{"acceptance_layer": "authored candidate — evergreen extension, unscheduled", "atom_family": "HOOK_COVER", "atom_id": "EVG-ENUS-BURN-GXSW-HC-02", "awareness_stage": "problem_aware", "char_count": 134, "claim_risk": "low_no_medical_claim", "compatible_next": "SOMATIC_SETUP;PROBLEM_AGITATION;MECHANISM_EXPLAINER;REFRAME;TOOL_STEP;SAVEABLE_PAYOFF;CTA_ANCHOR;BRIDGE", "compatible_previous": "HOOK_COVER;SOMATIC_SETUP;PROBLEM_AGITATION;MECHANISM_EXPLAINER;REFRAME;TOOL_STEP;SAVEABLE_PAYOFF;BRIDGE", "cta_policy": "none", "culture_risk": "low_en_us_general", "draft_only": true, "first_fold_chars": 125, "hook_family": "identity_based", "incompatible_with": "medical_cure_claims;shame_language;unsupported_statistics;caption_clone_reuse", "link_policy": "no_main_body_external_link", "locale": "en-US", "market_fit": "en-US", "objective": "trust_authority", "persona": "gen_x_sandwich", "platform_fit": "instagram;facebook;linkedin;tiktok_reels_shorts;youtube;pinterest;x;threads;google_business", "reuse_cooldown_days": 14, "review_status": "draft_operator_review_required", "source_refs": "SRC_ENGLISH_RESEARCH — \"If your home has a constant undercurrent of tension, look at who is carrying the emotional labor.\" (docs/research_social_media.txt:3435)", "surface_fit": "static_caption;carousel;thread;short_video_script;business_update", "text": "sandwich generation: caring for your kids and your parents at the same time is not a scheduling problem, it's a nervous system problem.", "tone": "direct honest", "topic": "burnout", "word_count": 23}
{"acceptance_layer": "authored candidate — evergreen extension, unscheduled", "atom_family": "REFRAME", "atom_id": "EVG-ENUS-BURN-GXSW-R-01", "awareness_stage": "solution_aware", "char_count": 170, "claim_risk": "low_no_medical_claim", "compatible_next": "SOMATIC_SETUP;PROBLEM_AGITATION;MECHANISM_EXPLAINER;REFRAME;TOOL_STEP;SAVEABLE_PAYOFF;CTA_ANCHOR;BRIDGE", "compatible_previous": "HOOK_COVER;SOMATIC_SETUP;PROBLEM_AGITATION;MECHANISM_EXPLAINER;REFRAME;TOOL_STEP;SAVEABLE_PAYOFF;BRIDGE", "cta_policy": "none", "culture_risk": "low_en_us_general", "draft_only": true, "first_fold_chars": 125, "hook_family": "practical_tool", "incompatible_with": "medical_cure_claims;shame_language;unsupported_statistics;caption_clone_reuse", "link_policy": "no_main_body_external_link", "locale": "en-US", "market_fit": "en-US", "objective": "trust_authority", "persona": "gen_x_sandwich", "platform_fit": "instagram;facebook;linkedin;tiktok_reels_shorts;youtube;pinterest;x;threads;google_business", "reuse_cooldown_days": 14, "review_status": "draft_operator_review_required", "source_refs": "SRC_ENGLISH_RESEARCH — \"You aren't needy; your body is simply trying to keep you safe. It is safe to let go of the emotional labor today.\" (docs/research_social_media.txt:3757)", "surface_fit": "static_caption;carousel;thread;short_video_script;business_update", "text": "Reframe it this way: you aren't needy for wanting a limit, your body is simply trying to keep you safe. It is safe to let go of some of the emotional labor today, not all of it, just some.", "tone": "calm professional", "topic": "burnout", "word_count": 32}
{"acceptance_layer": "authored candidate — evergreen extension, unscheduled", "atom_family": "TOOL_STEP", "atom_id": "EVG-ENUS-BURN-GXSW-TS-01", "awareness_stage": "ready_to_act", "char_count": 158, "claim_risk": "low_no_medical_claim", "compatible_next": "SOMATIC_SETUP;PROBLEM_AGITATION;MECHANISM_EXPLAINER;REFRAME;TOOL_STEP;SAVEABLE_PAYOFF;CTA_ANCHOR;BRIDGE", "compatible_previous": "HOOK_COVER;SOMATIC_SETUP;PROBLEM_AGITATION;MECHANISM_EXPLAINER;REFRAME;TOOL_STEP;SAVEABLE_PAYOFF;BRIDGE", "cta_policy": "none", "culture_risk": "low_en_us_general", "draft_only": true, "first_fold_chars": 125, "hook_family": "practical_tool", "incompatible_with": "medical_cure_claims;shame_language;unsupported_statistics;caption_clone_reuse", "link_policy": "no_main_body_external_link", "locale": "en-US", "market_fit": "en-US", "objective": "trust_authority", "persona": "gen_x_sandwich", "platform_fit": "instagram;facebook;linkedin;tiktok_reels_shorts;youtube;pinterest;x;threads;google_business", "reuse_cooldown_days": 14, "review_status": "draft_operator_review_required", "source_refs": "SRC_ENGLISH_RESEARCH — \"The hyper-responsible mother: why she is exhausted, and how she can start setting limits today.\" (docs/research_social_media.txt:3438)", "surface_fit": "static_caption;carousel;thread;short_video_script;business_update", "text": "Try this: pick one recurring task this week — one call, one errand, one check-in — and hand it to someone else or let it wait a day. Notice what happens in your chest when you do.", "tone": "direct honest", "topic": "burnout", "word_count": 32}
```

## Test-chain proof

54 distinct assemblable `HOOK_COVER -> SOMATIC_SETUP -> TOOL_STEP -> CTA_ANCHOR` chains within the 22 new rows.

## Tests run

- JSONL parses clean: 1,686 rows total, 0 duplicate `atom_id`s.
- Test-chain script: 54 chains found.
- NUL-byte check (`od`-based, matching the fixed `.github/workflows/no-binary-blobs.yml` gate from wave 1-2): clean,
  no false positive expected.
- `PYTHONPATH=. python3 scripts/git/push_guard.py` — Push-guard OK.
- `scripts/ci/preflight_push.sh` — Preflight OK.

## NEXT_ACTION (remaining cells)

180 → 170 zero-coverage cells remain. Wave 4+: `millennial_women_professionals`, `tech_finance_burnout`,
`gen_alpha_students`, `first_responders`, `gen_z_student`, `educators`, `midlife_women` x `burnout` (7 personas
left for this topic), then the same 10-persona set across the other 19 topics.
