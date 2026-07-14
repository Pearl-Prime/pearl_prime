# Freebie Post-Experience Capture Spec

        ## State Machine

        `tool_view -> tool_start -> tool_step_complete -> tool_complete -> report_offer_view -> channel_selected -> report_capture_submit -> report_delivery_success|report_delivery_fail -> fallback_email_used`.

        ## Page Inventory

        | Page | Topic | Freebie | Report |
        | --- | --- | --- | --- |
        | `anxiety-nervous-system-reset` | `anxiety` | `breath_timer_v1` | `Your Nervous System Reset Report` |
| `boundaries-script-kit` | `boundaries` | `conversation_scripts_v1` | `Your Boundary Language Report` |
| `burnout-energy-audit` | `burnout` | `companion_core_v2` | `Your Energy Pattern Report` |
| `compassion-fatigue-audit` | `compassion_fatigue` | `burnout_checklist_v1` | `Your Capacity Report` |
| `courage-decision-map` | `courage` | `resistance_mapping_v1` | `Your Decision Courage Report` |
| `depression-momentum-kit` | `depression` | `thirty_day_tracker_v1` | `Your Momentum Report` |
| `financial-anxiety-check-in` | `financial_anxiety` | `anxiety_assessment_v1` | `Your Money Anxiety Report` |
| `financial-stress-audit` | `financial_stress` | `journal_reflection_v1` | `Your Financial Stress Report` |
| `grief-letter-template` | `grief` | `journal_reflection_v1` | `Your Grief Integration Report` |
| `imposter-evidence-log` | `imposter_syndrome` | `accountability_partner_v1` | `Your Evidence Report` |
| `overthinking-thought-sorter` | `overthinking` | `anxiety_assessment_v1` | `Your Thought Pattern Report` |
| `self-worth-inventory` | `self_worth` | `identity_sheet_v1` | `Your Worth Inventory Report` |
| `sleep-anxiety-wind-down` | `sleep_anxiety` | `breath_timer_v1` | `Your Wind-Down Report` |
| `social-anxiety-toolkit` | `social_anxiety` | `emergency_kit_v1` | `Your Social Energy Report` |
| `somatic-body-scan` | `somatic_healing` | `breath_reset_structured_v1` | `Your Body Scan Report` |

        ## Tool-First Contract

        The visitor lands in the interactive tool. Legacy email gates are hidden for Waystream pages by `PhoenixLead.shouldShowEmailGate()` and `PhoenixFunnel.initPostExperienceCapture()`. The report offer appears only after a completion signal or the bottom-of-tool completion button.

        ## Payload Schema

        Existing campaign fields remain intact, including all `phoenix_e1_*` through `phoenix_e9_*`, `phoenix_e3_story_body`, book recommendation fields, and bonus pre-E3 fields. New report unlock fields are:

        - `delivery_channel`
        - `delivery_address`
        - `channel_consent`
        - `report_id`
        - `report_variant`
        - `report_summary`
        - `answers_json`
        - `completed_at`
        - `completion_duration_seconds`
        - `ab_variant`
        - `source_page_slug`
        - `freebie_id`
        - `result_summary`

        ## Channel Priority

        Default order is WhatsApp, Telegram, email. Japan order is LINE, Messenger, WhatsApp, Telegram, email. Channel credentials are referenced only by environment variable names in `config/freebies/report_delivery_channels.yaml`.

        ## Claims Doctrine

        Benefits may be somatic, nervous-system, psychological, reflective, or spiritual possibilities. Copy must not claim clinical assessment, healing certainty, guaranteed transformation, financial outcome, or deterministic future prediction.
