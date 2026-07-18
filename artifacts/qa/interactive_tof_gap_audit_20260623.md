# Interactive TOF GHL Capture Gap Audit — 2026-06-23

**Branch baseline:** `origin/main` before `agent/interactive-tof-ghl-full-15-20260623`  
**Method:** grep `brand-wizard-app/public/free/*/index.html` for `phoenix_lead`, `data-ghl-webhook`, `PhoenixLead.captureLead`, `gtag.*lead_submit`

## TOPIC_LANDING_AUDIT (15 rows)

| topic | funnel_slug | primary_archetype | phoenix_lead.js | data-ghl-webhook | captureLead on submit | interactive type (actual vs expected) | Pre-fix |
|-------|-------------|-------------------|-----------------|------------------|----------------------|---------------------------------------|---------|
| anxiety | anxiety-nervous-system-reset | breath_timer_interactive | YES | YES | YES | somatic timer — PASS | PASS |
| compassion_fatigue | compassion-fatigue-audit | capacity_assessment | YES | YES | YES | scored assessment — PASS | PASS |
| overthinking | overthinking-thought-sorter | thought_sorter_assessment | YES | YES | YES | scored assessment — PASS | PASS |
| financial_anxiety | financial-anxiety-check-in | financial_checkin | YES | YES | YES | scored check-in — PASS | PASS |
| courage | courage-decision-map | decision_resistance_map | YES | YES | YES | decision map — PASS | PASS |
| burnout | burnout-energy-audit | capacity_assessment | NO | NO | NO (GA4 only) | reflection assessment — wired in PR | FAIL |
| self_worth | self-worth-inventory | worth_inventory | NO | NO | NO (GA4 only) | multi-part inventory — wired in PR | FAIL |
| imposter_syndrome | imposter-evidence-log | evidence_log | NO | NO | NO (GA4 only) | evidence log table — wired in PR | FAIL |
| boundaries | boundaries-script-kit | script_practice | NO | NO | NO (GA4 only) | script kit — wired in PR | FAIL |
| depression | depression-momentum-kit | micro_action_kit | NO | NO | NO (GA4 only) | micro-action checklist — wired in PR | FAIL |
| social_anxiety | social-anxiety-toolkit | pre_event_protocol | NO | NO | NO (GA4 only) | pre-event protocol tabs — wired in PR | FAIL |
| financial_stress | financial-stress-audit | financial_stress_audit | NO | NO | NO (GA4 only) | reflection prompts — wired in PR | FAIL |
| sleep_anxiety | sleep-anxiety-wind-down | wind_down_breath | NO | NO | NO (GA4 only) | somatic wind-down timer — wired in PR | FAIL |
| somatic_healing | somatic-body-scan | body_scan_timer | NO | NO | NO (GA4 only) | zone body scan timer — wired in PR | FAIL |
| grief | grief-letter-template | grief_letter_template | NO | NO | NO (GA4 only) | letter template builder — wired in PR | FAIL |

**Pre-fix score:** 5 PASS / 10 FAIL on GHL wiring.

---

## Appendix A — Intentional non-quiz behavior

| Page | Scoring | GHL payload |
|------|---------|-------------|
| burnout-energy-audit | 10 reflection prompts, no numeric score | `score: null`, `score_band: null`, tag `format_reflection` optional |
| financial-stress-audit | 5 prompts, no score | null score fields |
| grief-letter-template | Letter builder, no score | null score fields |
| boundaries-script-kit | Script copy kit, no score | null score fields |
| depression-momentum-kit | Checklist, no score | null score fields |
| self-worth-inventory | Multi-part inventory | null score fields |
| imposter-evidence-log | Evidence table | null score fields |
| social-anxiety-toolkit | Tabbed protocol | null score fields |
| somatic-body-scan | Zone timer | null score fields |
| sleep-anxiety-wind-down | 3-phase breath timer | null score fields |

Scored pages (flagship 5) continue sending `score` + `score_band` + `severity_*` tags.

---

## Appendix B — Somatic mini-apps (Phase 2b)

**42 apps** in `somatic_exercise_freebee_apps/` use `initToolPage` footer only — **no email gate** on page load.

**Decision (Q-ITOF-02):** E2 unlock targets only. GHL capture happens on **15 funnel landings**. No batch webhook inject to somatic apps in this PR.

---

## Post-fix validation

Run after merge:

```bash
python3 scripts/freebies/smoke_freebie_capture.py
python3 -m pytest tests/test_ghl_funnel_pages_wired.py -q
```

Expected: 15/15 PASS.
