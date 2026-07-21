# Handoff — Lane 03 Pearl_Writer: Evergreen Social Atom Bank Scale-Up, Wave 2

**Date:** 2026-07-21
**Agent:** Pearl_Writer (Claude, Tier-1 per CLAUDE.md LLM Tier Policy)
**Lane:** lane03_social_atom_bank_scaleup
**Prior wave:** [lane03_social_atom_scaleup_wave1_2026-07-21.md](lane03_social_atom_scaleup_wave1_2026-07-21.md)

## Wave 2 — `entrepreneurs` x `burnout`

- **Atoms added:** 22 (`HOOK_COVER` x3, `SOMATIC_SETUP` x2, `PROBLEM_AGITATION` x2, `MECHANISM_EXPLAINER` x2,
  `REFRAME` x2, `TOOL_STEP` x3, `SAVEABLE_PAYOFF` x2, `CTA_ANCHOR` x3, `BRIDGE` x3) — same 9-family mix as wave 1.
- **Cell newly covered:** `entrepreneurs` x `burnout` (previously zero atoms).
- **`brand_id`/`author_id`:** omitted (universal/house-voice default).
- **`review_status`:** `draft_operator_review_required`.
- **`source_refs`:** existing `SRC_*` codes plus a real quoted claim from `docs/research_social_media.txt` per row.
  Grounding claims used: "high-performers often mistake chronic hyper-vigilance for high productivity" (line 2687),
  the 24/7-accessibility/silent-boundary mechanism (line 3141), the "hustle" biological-cost claim (line 2906), the
  "you aren't lazy" sympathetic-activation claim (line 3191), the somatic-boundary turning-point story (line 3524),
  the identity-based share CTA (line 3249), and the save-checklist CTA (line 3252).
- **Running total:** 1,664 rows (1,642 after wave 1 + 22 new).

### Sample rows (3 of 22, full JSON)

```json
{"acceptance_layer": "authored candidate — evergreen extension, unscheduled", "atom_family": "HOOK_COVER", "atom_id": "EVG-ENUS-BURN-ENTR-HC-01", "awareness_stage": "problem_aware", "char_count": 100, "claim_risk": "low_no_medical_claim", "compatible_next": "SOMATIC_SETUP;PROBLEM_AGITATION;MECHANISM_EXPLAINER;REFRAME;TOOL_STEP;SAVEABLE_PAYOFF;CTA_ANCHOR;BRIDGE", "compatible_previous": "HOOK_COVER;SOMATIC_SETUP;PROBLEM_AGITATION;MECHANISM_EXPLAINER;REFRAME;TOOL_STEP;SAVEABLE_PAYOFF;BRIDGE", "cta_policy": "none", "culture_risk": "low_en_us_general", "draft_only": true, "first_fold_chars": 100, "hook_family": "identity_based", "incompatible_with": "medical_cure_claims;shame_language;unsupported_statistics;caption_clone_reuse", "link_policy": "no_main_body_external_link", "locale": "en-US", "market_fit": "en-US", "objective": "trust_authority", "persona": "entrepreneurs", "platform_fit": "instagram;facebook;linkedin;tiktok_reels_shorts;youtube;pinterest;x;threads;google_business", "reuse_cooldown_days": 14, "review_status": "draft_operator_review_required", "source_refs": "SRC_ENGLISH_RESEARCH — \"If you are accessible 24/7, your body is operating in chronic survival mode...Cortisol spikes, and immune function drops. The solution is the 'silent boundary.'\" (docs/research_social_media.txt:3141)", "surface_fit": "static_caption;carousel;thread;short_video_script;business_update", "text": "founders: being accessible 24/7 is not commitment, it is a nervous system stuck in survival mode.", "tone": "direct honest", "topic": "burnout", "word_count": 17}
{"acceptance_layer": "authored candidate — evergreen extension, unscheduled", "atom_family": "MECHANISM_EXPLAINER", "atom_id": "EVG-ENUS-BURN-ENTR-ME-02", "awareness_stage": "solution_aware", "char_count": 176, "claim_risk": "low_no_medical_claim", "compatible_next": "SOMATIC_SETUP;PROBLEM_AGITATION;MECHANISM_EXPLAINER;REFRAME;TOOL_STEP;SAVEABLE_PAYOFF;CTA_ANCHOR;BRIDGE", "compatible_previous": "HOOK_COVER;SOMATIC_SETUP;PROBLEM_AGITATION;MECHANISM_EXPLAINER;REFRAME;TOOL_STEP;SAVEABLE_PAYOFF;BRIDGE", "cta_policy": "none", "culture_risk": "low_en_us_general", "draft_only": true, "first_fold_chars": 125, "hook_family": "practical_tool", "incompatible_with": "medical_cure_claims;shame_language;unsupported_statistics;caption_clone_reuse", "link_policy": "no_main_body_external_link", "locale": "en-US", "market_fit": "en-US", "objective": "trust_authority", "persona": "entrepreneurs", "platform_fit": "instagram;facebook;linkedin;tiktok_reels_shorts;youtube;pinterest;x;threads;google_business", "reuse_cooldown_days": 14, "review_status": "draft_operator_review_required", "source_refs": "SRC_ENGLISH_RESEARCH — \"Continuous sympathetic activation causes chronic low-grade exhaustion and cognitive fatigue. You aren't lazy; your system is simply running from a digital 'predator' 24/7.\" (docs/research_social_media.txt:3191)", "surface_fit": "static_caption;carousel;thread;short_video_script;business_update", "text": "Founder burnout often persists because continuous sympathetic activation causes chronic low-grade exhaustion and cognitive fatigue. You aren't lazy; your system is running from an always-on threat 24/7.", "tone": "calm professional", "topic": "burnout", "word_count": 32}
{"acceptance_layer": "authored candidate — evergreen extension, unscheduled", "atom_family": "TOOL_STEP", "atom_id": "EVG-ENUS-BURN-ENTR-TS-01", "awareness_stage": "ready_to_act", "char_count": 132, "claim_risk": "low_no_medical_claim", "compatible_next": "SOMATIC_SETUP;PROBLEM_AGITATION;MECHANISM_EXPLAINER;REFRAME;TOOL_STEP;SAVEABLE_PAYOFF;CTA_ANCHOR;BRIDGE", "compatible_previous": "HOOK_COVER;SOMATIC_SETUP;PROBLEM_AGITATION;MECHANISM_EXPLAINER;REFRAME;TOOL_STEP;SAVEABLE_PAYOFF;BRIDGE", "cta_policy": "none", "culture_risk": "low_en_us_general", "draft_only": true, "first_fold_chars": 125, "hook_family": "practical_tool", "incompatible_with": "medical_cure_claims;shame_language;unsupported_statistics;caption_clone_reuse", "link_policy": "no_main_body_external_link", "locale": "en-US", "market_fit": "en-US", "objective": "trust_authority", "persona": "entrepreneurs", "platform_fit": "instagram;facebook;linkedin;tiktok_reels_shorts;youtube;pinterest;x;threads;google_business", "reuse_cooldown_days": 14, "review_status": "draft_operator_review_required", "source_refs": "SRC_ENGLISH_RESEARCH — \"If you are accessible 24/7, your body is operating in chronic survival mode...The solution is the 'silent boundary.' A non-negotiable block of time daily with zero inputs.\" (docs/research_social_media.txt:3141)", "surface_fit": "static_caption;carousel;thread;short_video_script;business_update", "text": "Try this: set one non-negotiable silent-boundary window daily where notifications, Slack, and email are fully off. Not the whole evening, one window, protected on purpose.", "tone": "direct honest", "topic": "burnout", "word_count": 27}
```

## Test-chain proof

54 distinct assemblable `HOOK_COVER -> SOMATIC_SETUP -> TOOL_STEP -> CTA_ANCHOR` chains within the 22 new rows.

## Tests run

- JSONL parses clean: 1,664 rows total, 0 duplicate `atom_id`s.
- Test-chain script: 54 chains found.
- `generate_copy_package('entrepreneurs', 'burnout', 'instagram_carousel', format_family='carousel')` — non-error,
  non-empty. Same caveat as wave 1: this composer still doesn't read the atom-bank JSONL (Lane 02/04 wiring gap,
  unchanged since wave 1).
- `PYTHONPATH=. python3 scripts/git/push_guard.py` — Push-guard OK.
- `scripts/ci/preflight_push.sh` — Preflight OK.
- Note: `phoenix_v4/social/deterministic_social.py` is itself untracked in git (not present in a clean `origin/main`
  checkout) — the smoke test above was run against the main working tree's untracked copy, not the isolated landing
  worktree. This is a pre-existing condition unrelated to this lane; out of scope to land here.

## NEXT_ACTION (remaining cells)

190 → 180 zero-coverage cells remain. Wave 3+: `gen_x_sandwich`, `millennial_women_professionals`,
`tech_finance_burnout`, `gen_alpha_students`, `first_responders`, `gen_z_student`, `educators`, `midlife_women`
x `burnout`, then the same 10-persona set across the other 19 topics.
