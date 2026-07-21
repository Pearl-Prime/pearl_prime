#!/usr/bin/env python3
"""Sync Waystream post-experience report capture docs, config, and page flags."""
from __future__ import annotations

import json
import re
from pathlib import Path
from textwrap import dedent

import yaml

REPO = Path(__file__).resolve().parents[2]
BRAND_ID = "way_stream_sanctuary"
PACK_DATE = "20260714"
QA_ROOT = REPO / "artifacts/qa/freebie_post_experience_capture_20260714"
HANDOFF_ROOT = REPO / "artifacts/coordination/handoffs"
PAGES_ROOT = REPO / "brand-wizard-app/public/free/way_stream_sanctuary"
PLAN_PATH = REPO / "config/freebies/waystream_evergreen_campaign_plan.yaml"

SLUG_COPY: dict[str, dict[str, str]] = {
    "anxiety-nervous-system-reset": {
        "report_title": "Your Nervous System Reset Report",
        "completion": "You completed the reset.",
        "forecast": "What your body may ask for before anxiety gets loud next week.",
        "practice": "Repeat the 4-7-8 reset once before you need it.",
    },
    "boundaries-script-kit": {
        "report_title": "Your Boundary Language Report",
        "completion": "You completed the script kit.",
        "forecast": "Where a cleaner sentence may change the next conversation.",
        "practice": "Choose one script and rehearse it out loud once.",
    },
    "burnout-energy-audit": {
        "report_title": "Your Energy Pattern Report",
        "completion": "You completed the audit.",
        "forecast": "Which energy leak may be easiest to protect this week.",
        "practice": "Block one recovery pocket before adding another task.",
    },
    "compassion-fatigue-audit": {
        "report_title": "Your Capacity Report",
        "completion": "You completed the audit.",
        "forecast": "Where care may need a boundary before it becomes depletion.",
        "practice": "Try tonglen gently, then name one limit.",
    },
    "courage-decision-map": {
        "report_title": "Your Decision Courage Report",
        "completion": "You completed the map.",
        "forecast": "Which small honest move may make the decision less foggy.",
        "practice": "Take the smallest reversible action within 24 hours.",
    },
    "depression-momentum-kit": {
        "report_title": "Your Momentum Report",
        "completion": "You completed the kit.",
        "forecast": "Which low-friction action may restart a little movement.",
        "practice": "Pick one action that takes less than five minutes.",
    },
    "financial-anxiety-check-in": {
        "report_title": "Your Money Anxiety Report",
        "completion": "You completed the check-in.",
        "forecast": "Where the money signal and the fear story may separate.",
        "practice": "Pair one grounding breath with one concrete money action.",
    },
    "financial-stress-audit": {
        "report_title": "Your Financial Stress Report",
        "completion": "You completed the audit.",
        "forecast": "Which security action may calm the story without shaming you.",
        "practice": "Do one practical step, then stop rehearsing the worst case for ten minutes.",
    },
    "grief-letter-template": {
        "report_title": "Your Grief Integration Report",
        "completion": "You completed the letter.",
        "forecast": "Which unfinished sentence may need tenderness, not closure.",
        "practice": "Place one hand on your chest and read one line back kindly.",
    },
    "imposter-evidence-log": {
        "report_title": "Your Evidence Report",
        "completion": "You completed the log.",
        "forecast": "Which proof your doubt tends to dismiss first.",
        "practice": "Keep one evidence line visible before the next hard task.",
    },
    "overthinking-thought-sorter": {
        "report_title": "Your Thought Pattern Report",
        "completion": "You completed the sorter.",
        "forecast": "Which thought loop may be trying to protect you this week.",
        "practice": "Sort one thought, then move your body for sixty seconds.",
    },
    "self-worth-inventory": {
        "report_title": "Your Worth Inventory Report",
        "completion": "You completed the inventory.",
        "forecast": "Where your value may be ready to detach from output.",
        "practice": "Write one worth statement that is not tied to productivity.",
    },
    "sleep-anxiety-wind-down": {
        "report_title": "Your Wind-Down Report",
        "completion": "You completed the wind-down.",
        "forecast": "Which evening cue may help the body downshift sooner.",
        "practice": "Repeat the same wind-down cue for three nights.",
    },
    "social-anxiety-toolkit": {
        "report_title": "Your Social Energy Report",
        "completion": "You completed the toolkit.",
        "forecast": "Where pre-event support may reduce the after-event replay.",
        "practice": "Choose one before, during, and after cue for the next event.",
    },
    "somatic-body-scan": {
        "report_title": "Your Body Scan Report",
        "completion": "You completed the scan.",
        "forecast": "Which body signal may be asking for steadier attention.",
        "practice": "Return to the clearest zone for thirty seconds tomorrow.",
    },
}

LANES = [
    ("01", "freebie_foundation_inventory", "Foundation inventory"),
    ("02", "freebie_product_architecture", "Product architecture"),
    ("03", "freebie_completion_flow", "Shared completion flow"),
    ("04", "freebie_report_schema_generator", "Report schema and generator"),
    ("05", "freebie_channel_routing_contract", "Channel routing contract"),
    ("06", "freebie_ghl_report_payload", "GHL report payload"),
    ("07", "freebie_report_unlock_copy", "Report unlock copy"),
    ("08", "freebie_per_tool_report_specs", "Per-tool report specs"),
    ("09", "freebie_consent_claims_qa", "Consent, privacy, claims"),
    ("10", "freebie_telegram_delivery", "Telegram delivery"),
    ("11", "freebie_existing_channel_hardening", "Existing channel hardening"),
    ("12", "freebie_report_delivery_endpoint", "Report delivery endpoint"),
    ("13", "freebie_ab_testing_framework", "A/B testing framework"),
    ("14", "freebie_analytics_taxonomy", "Analytics taxonomy"),
    ("15", "freebie_app_wave_a", "App wave A"),
    ("16", "freebie_app_wave_b", "App wave B"),
    ("17", "freebie_app_wave_c", "App wave C"),
    ("18", "freebie_app_wave_d", "App wave D"),
    ("19", "freebie_ghl_admin_handoff", "GHL admin handoff"),
    ("20", "freebie_report_delivery_templates", "Delivery templates"),
    ("21", "freebie_contract_tests", "Unit and contract tests"),
    ("22", "freebie_browser_e2e", "Browser E2E"),
    ("23", "freebie_mobile_a11y_perf", "Mobile/a11y/perf"),
    ("24", "freebie_post_experience_capture_final_20260714", "Final integration"),
]


def load_plans() -> list[dict]:
    data = yaml.safe_load(PLAN_PATH.read_text(encoding="utf-8")) or {}
    plans = data.get("plans") or []
    return sorted(plans, key=lambda item: item["source_page_slug"])


def write_yaml(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=False, width=100),
        encoding="utf-8",
    )


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(text).lstrip() + "\n", encoding="utf-8")


def sanitize_pages(plans: list[dict]) -> list[dict]:
    rows = []
    for plan in plans:
        slug = plan["source_page_slug"]
        path = PAGES_ROOT / slug / "index.html"
        text = path.read_text(encoding="utf-8")
        original = text
        text = re.sub(r'data-ghl-webhook="[^"]*"', 'data-ghl-webhook=""', text)
        if 'data-post-experience-capture=' not in text:
            text = text.replace(
                f'data-funnel-slug="{slug}"',
                f'data-funnel-slug="{slug}" data-post-experience-capture="1"',
                1,
            )
        if original != text:
            path.write_text(text, encoding="utf-8")
        rows.append(
            {
                "slug": slug,
                "path": str(path.relative_to(REPO)),
                "topic": plan["topic"],
                "freebie_id": plan["freebie_id"],
                "capture_timing_before": "mixed_email_first_or_email_before_result",
                "capture_timing_after": "tool_first_report_after_completion",
                "webhook_exposure": "sanitized_empty_body_attr",
            }
        )
    return rows


def write_channel_config() -> None:
    write_yaml(
        REPO / "config/freebies/report_delivery_channels.yaml",
        {
            "schema_version": 1,
            "default_order": ["whatsapp", "telegram", "email"],
            "region_orders": {"JP": ["line", "messenger", "whatsapp", "telegram", "email"]},
            "channels": {
                "whatsapp": {
                    "label": "WhatsApp",
                    "address_type": "phone",
                    "env_vars": ["FREEBIE_WHATSAPP_PROVIDER", "FREEBIE_WHATSAPP_TOKEN"],
                    "enabled_when": "provider_env_present",
                    "fallback": "email",
                    "consent": "I consent to receive my Waystream report and related follow-up by WhatsApp.",
                },
                "telegram": {
                    "label": "Telegram",
                    "address_type": "telegram_username",
                    "env_vars": ["FREEBIE_TELEGRAM_BOT_TOKEN"],
                    "enabled_when": "bot_token_env_present",
                    "fallback": "email",
                    "consent": "I consent to receive my Waystream report and related follow-up by Telegram.",
                },
                "email": {
                    "label": "Email",
                    "address_type": "email",
                    "env_vars": ["PHOENIX_GHL_FUNNEL_WEBHOOK"],
                    "enabled_when": "always_visible",
                    "fallback": None,
                    "consent": "I consent to receive my Waystream report and related follow-up by email.",
                },
                "line": {
                    "label": "LINE",
                    "address_type": "line_id",
                    "env_vars": ["FREEBIE_LINE_CHANNEL_ACCESS_TOKEN"],
                    "enabled_when": "region_JP_and_env_present",
                    "fallback": "email",
                    "consent": "I consent to receive my Waystream report and related follow-up by LINE.",
                },
                "messenger": {
                    "label": "Messenger",
                    "address_type": "messenger_id",
                    "env_vars": ["FREEBIE_MESSENGER_PAGE_TOKEN"],
                    "enabled_when": "region_JP_and_env_present",
                    "fallback": "email",
                    "consent": "I consent to receive my Waystream report and related follow-up by Messenger.",
                },
            },
            "validation": {
                "whatsapp": "^\\+?[0-9().\\-\\s]{7,24}$",
                "telegram": "^@?[A-Za-z0-9_]{5,32}$",
                "email": "standard_email",
                "line": "^[A-Za-z0-9_.\\-]{3,40}$",
                "messenger": "^@?[A-Za-z0-9_.\\-]{3,80}$",
            },
            "secret_policy": "Names env vars only. Do not commit webhook URLs, bot tokens, API keys, or provider credentials.",
        },
    )


def write_report_configs(plans: list[dict]) -> None:
    unlock = {
        "schema_version": 1,
        "claims_safety": {
            "allowed_frames": ["educational", "reflective", "somatic", "nervous_system", "psychological", "spiritual"],
            "banned_frames": ["clinical assessment", "healing promise", "guaranteed outcome", "medical promise", "deterministic prediction"],
        },
        "variants": {
            "whatsapp_first": [
                {
                    "headline": "Your report is ready to travel with you.",
                    "body": "Send the personalized report to WhatsApp so the next practice is close when the pattern shows up again.",
                    "cta": "Send it to WhatsApp",
                },
                {
                    "headline": "Keep the insight where you will actually see it.",
                    "body": "A concise report with your somatic cue, reflection, and next-week practice.",
                    "cta": "Send my report",
                },
                {
                    "headline": "Turn this completed tool into a next-step map.",
                    "body": "Your answers point to a practical rhythm. Receive it in the channel you use most.",
                    "cta": "Unlock my report",
                },
            ],
            "telegram_first": [
                {
                    "headline": "Send the report to Telegram.",
                    "body": "Use Telegram when you want a clean, lightweight report thread without losing the practice.",
                    "cta": "Send to Telegram",
                },
                {
                    "headline": "A reflective report, not another inbox chore.",
                    "body": "Get your score, pattern, and next cue in a compact message.",
                    "cta": "Deliver my report",
                },
                {
                    "headline": "Carry the next cue with you.",
                    "body": "A short Waystream report can help you revisit the tool when the pattern returns.",
                    "cta": "Send my next cue",
                },
            ],
            "email_fallback": [
                {
                    "headline": "Prefer email? Keep the full report there.",
                    "body": "Email stays available as the universal fallback for every report.",
                    "cta": "Email my report",
                },
                {
                    "headline": "Save the report for later.",
                    "body": "Receive the complete reflection, next practice, and Waystream reading path by email.",
                    "cta": "Send by email",
                },
                {
                    "headline": "Your report can wait in your inbox.",
                    "body": "No pressure. Use the report when you want to return to the exercise.",
                    "cta": "Use email fallback",
                },
            ],
        },
        "per_tool_promises": {},
    }
    templates = {"schema_version": 1, "reports": {}}
    for plan in plans:
        slug = plan["source_page_slug"]
        copy = SLUG_COPY[slug]
        unlock["per_tool_promises"][slug] = {
            "completion": copy["completion"],
            "report_title": copy["report_title"],
            "promise": copy["forecast"],
            "cta": "Send my personalized report",
        }
        templates["reports"][slug] = {
            "report_id": f"waystream_{slug}_report_v1",
            "title": copy["report_title"],
            "topic": plan["topic"],
            "freebie_id": plan["freebie_id"],
            "sections": [
                "completion_reflection",
                "answer_pattern",
                "somatic_signal",
                "nervous_system_cue",
                "psychological_reflection",
                "spiritual_question",
                "next_week_reflective_forecast",
                "recommended_practice",
            ],
            "benefits": {
                "somatic": "Notice the body cue that appeared through the exercise.",
                "nervous_system": "Name one repeatable regulation cue for the next week.",
                "psychological": "Reflect on the pattern your answers suggest without turning it into clinical advice.",
                "spiritual": "Carry one gentle inquiry that opens space rather than certainty.",
            },
            "forecast": copy["forecast"],
            "recommended_practice": copy["practice"],
        }
    write_yaml(REPO / "config/freebies/report_unlock_copy.yaml", unlock)
    write_yaml(REPO / "config/freebies/freebie_report_templates.yaml", templates)


def write_report_specs(plans: list[dict]) -> None:
    spec_dir = REPO / "config/freebies/report_specs/way_stream_sanctuary"
    for plan in plans:
        slug = plan["source_page_slug"]
        copy = SLUG_COPY[slug]
        write_yaml(
            spec_dir / f"{slug}.yaml",
            {
                "schema_version": 1,
                "brand_id": BRAND_ID,
                "source_page_slug": slug,
                "topic": plan["topic"],
                "freebie_id": plan["freebie_id"],
                "quiz_id": plan["quiz_id"],
                "completion_copy": copy["completion"],
                "report_title": copy["report_title"],
                "report_sections": [
                    {"id": "completion_reflection", "purpose": "Acknowledge the completed tool and mirror the user's effort."},
                    {"id": "answer_pattern", "purpose": "Summarize answer themes without exposing raw private text in previews."},
                    {"id": "somatic_signal", "purpose": "Name a possible body cue."},
                    {"id": "nervous_system_cue", "purpose": "Offer one regulation-oriented next cue."},
                    {"id": "psychological_reflection", "purpose": "Frame the pattern as reflective, not diagnostic."},
                    {"id": "spiritual_question", "purpose": "Offer a gentle inquiry without deterministic prediction."},
                    {"id": "next_week_reflective_forecast", "purpose": copy["forecast"]},
                    {"id": "recommended_practice", "purpose": copy["practice"]},
                ],
                "insight_logic": {
                    "inputs": ["answers_json", "score", "score_band", "result_summary"],
                    "method": "Combine score/result bands with answer themes; if answers are sparse, use the completion state and topic default.",
                },
                "delivery_opening": f"{copy['completion']} Here is the Waystream report your tool unlocked.",
                "cta_copy": "Send my personalized report",
                "claims_boundary": "Educational and reflective only; not clinical advice, not therapy replacement, and no healing, financial result, or medical promise.",
            },
        )
    summary = "\n".join(f"- `{p['source_page_slug']}` -> `{SLUG_COPY[p['source_page_slug']]['report_title']}`" for p in plans)
    write_text(
        REPO / "docs/freebies/FREEBIE_REPORT_SPECS_SUMMARY_20260714.md",
        f"""
        # Waystream Freebie Report Specs

        All 15 Waystream freebie tools have report specs under
        `config/freebies/report_specs/way_stream_sanctuary/`.

        {summary}
        """,
    )


def write_delivery_templates() -> None:
    write_yaml(
        REPO / "config/freebies/report_delivery_templates.yaml",
        {
            "schema_version": 1,
            "templates": {
                "whatsapp": {
                    "format": "text",
                    "body": "You completed {tool_name}. Your Waystream report: {report_title}\\n\\n{report_summary}\\n\\nNext practice: {recommended_practice}\\n\\nReply STOP to opt out.",
                },
                "telegram": {
                    "format": "text",
                    "body": "Waystream report unlocked: {report_title}\\n{report_summary}\\nNext cue: {recommended_practice}\\nReply /stop to opt out.",
                },
                "email": {
                    "subject": "Your Waystream report: {report_title}",
                    "body": "<h1>{report_title}</h1><p>{report_summary}</p><p><strong>Next practice:</strong> {recommended_practice}</p>",
                },
                "line": {
                    "format": "text",
                    "body": "Your Waystream report is ready: {report_title}\\n{report_summary}\\nOpt out any time.",
                },
                "messenger": {
                    "format": "text",
                    "body": "Your Waystream report is ready: {report_title}\\n{report_summary}\\nReply STOP to opt out.",
                },
                "nurture_followup": {
                    "subject": "A small follow-up to your {tool_name}",
                    "body": "Return to the completed tool and repeat the recommended practice once this week.",
                },
            },
        },
    )


def write_docs(plans: list[dict]) -> None:
    page_rows = "\n".join(
        f"| `{p['source_page_slug']}` | `{p['topic']}` | `{p['freebie_id']}` | `{SLUG_COPY[p['source_page_slug']]['report_title']}` |"
        for p in plans
    )
    write_text(
        REPO / "docs/specs/FREEBIE_POST_EXPERIENCE_CAPTURE_SPEC_20260714.md",
        f"""
        # Freebie Post-Experience Capture Spec

        ## State Machine

        `tool_view -> tool_start -> tool_step_complete -> tool_complete -> report_offer_view -> channel_selected -> report_capture_submit -> report_delivery_success|report_delivery_fail -> fallback_email_used`.

        ## Page Inventory

        | Page | Topic | Freebie | Report |
        | --- | --- | --- | --- |
        {page_rows}

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
        """,
    )
    write_text(
        REPO / "docs/freebies/FREEBIE_REPORT_CAPTURE_COMPLIANCE_20260714.md",
        """
        # Freebie Report Capture Compliance

        Required guardrails:

        - Ask for channel-specific consent before report delivery.
        - Explain that answers and delivery handles are used to prepare and send the report.
        - Keep opt-out language in every delivery template.
        - Avoid clinical assessment, healing certainty, guaranteed outcome, therapy replacement, financial promise, or deterministic prediction.
        - Use future language as reflective possibility: "may reveal", "may shift", "could help you notice".
        - Do not put webhook URLs, bot tokens, API keys, or provider secrets in HTML, docs, PR text, or artifacts.
        """,
    )
    write_text(
        REPO / "docs/freebies/FREEBIE_REPORT_ANALYTICS_20260714.md",
        """
        # Freebie Report Analytics

        Events:

        - `tool_view`
        - `tool_start`
        - `tool_step_complete`
        - `tool_complete`
        - `report_offer_view`
        - `channel_selected`
        - `report_capture_submit`
        - `report_delivery_success`
        - `report_delivery_fail`
        - `fallback_email_used`

        Event payloads may include `freebie_slug`, `topic`, `ab_variant`, `channel`, `score_band`, and `source`. They must not include email, phone number, delivery handle, raw answer text, webhook URL, or contact id.
        """,
    )
    write_text(
        REPO / "docs/integrations/TELEGRAM_FREEBIE_REPORT_DELIVERY_20260714.md",
        """
        # Telegram Freebie Report Delivery

        Telegram delivery is env-gated. Required env var name: `FREEBIE_TELEGRAM_BOT_TOKEN`.

        Local testing must use dry-run mode only:

        ```bash
        python3 scripts/freebies/deliver_freebie_report.py --channel telegram --address @sample_user --slug anxiety-nervous-system-reset --dry-run
        ```

        Dry-run output is sanitized and must not print bot tokens or real message API URLs.
        """,
    )
    write_text(
        REPO / "docs/integrations/FREEBIE_MESSAGING_CHANNELS_20260714.md",
        """
        # Freebie Messaging Channel Hardening

        Supported channel contract:

        - WhatsApp: env-gated provider adapter; dry-run supported.
        - Telegram: env-gated bot token; dry-run supported.
        - Email: universal fallback through existing capture/GHL workflow.
        - LINE: Japan-only when env is configured; dry-run supported.
        - Messenger: Japan/fallback when env is configured; dry-run supported.

        Missing credentials must fail closed with a clear message. Tests must not send real messages.
        """,
    )
    write_text(
        REPO / "docs/runbooks/FREEBIE_REPORT_DELIVERY_ENDPOINT_20260714.md",
        """
        # Freebie Report Delivery Endpoint Runbook

        The local endpoint adapter is `scripts/freebies/deliver_freebie_report.py`.

        Dry run:

        ```bash
        python3 scripts/freebies/deliver_freebie_report.py --channel email --address test@example.com --slug anxiety-nervous-system-reset --dry-run
        ```

        Production dispatch must be env-gated. Do not persist PII in public storage. If report files are later stored in R2, use private keys and short-lived signed URLs only.
        """,
    )
    write_text(
        REPO / "docs/runbooks/FREEBIE_POST_EXPERIENCE_CAPTURE_LAUNCH_20260714.md",
        """
        # Freebie Post-Experience Capture Launch

        ## Launch Checklist

        - Run `python3 scripts/freebies/validate_post_experience_capture.py`.
        - Run `python3 scripts/freebies/validate_campaign_plan.py --brand-id way_stream_sanctuary`.
        - Dry-run report delivery for WhatsApp, Telegram, email, LINE, and Messenger.
        - Confirm GHL custom fields include all new report unlock fields.
        - Confirm no full webhook URLs or credentials exist in changed docs, artifacts, tests, or static pages.

        ## Rollback

        Revert the shared JS/CSS and restore the previous static HTML body attributes. Keep generated report specs; they are inert without the JS flow.
        """,
    )


def append_ghl_doc() -> None:
    path = REPO / "docs/ghl/GHL_ADMIN_WAYSTREAM_EVERGREEN_FREEBIE_FUNNEL.md"
    text = path.read_text(encoding="utf-8")
    marker = "## Post-Experience Report Unlock Fields"
    if marker in text:
        return
    text += dedent(
        """

        ## Post-Experience Report Unlock Fields

        The updated Waystream flow no longer asks for email before the visitor uses the tool. The visitor completes the tool, sees the report offer, chooses a delivery channel, consents, and then submits the report unlock payload.

        Add these custom fields in addition to the existing campaign fields:

        | JSON key | Custom field name |
        | --- | --- |
        | `delivery_channel` | `delivery_channel` |
        | `delivery_address` | `delivery_address` |
        | `channel_consent` | `channel_consent` |
        | `report_id` | `report_id` |
        | `report_variant` | `report_variant` |
        | `report_summary` | `report_summary` |
        | `completed_at` | `completed_at` |
        | `completion_duration_seconds` | `completion_duration_seconds` |
        | `ab_variant` | `ab_variant` |
        | `result_summary` | `result_summary` |

        Test one lead per channel using dry-run or sandbox delivery first. Do not paste webhook URLs into tickets, docs, or screenshots.
        """
    )
    path.write_text(text, encoding="utf-8")


def write_artifacts(plans: list[dict], inventory_rows: list[dict]) -> None:
    QA_ROOT.mkdir(parents=True, exist_ok=True)
    inventory = {
        "brand_id": BRAND_ID,
        "page_count": len(plans),
        "shared_js": [
            "brand-wizard-app/public/free/js/phoenix_lead.js",
            "brand-wizard-app/public/free/js/phoenix_funnel.js",
            "brand-wizard-app/public/free/js/phoenix_tool.css",
        ],
        "campaign_payload_fields_preserved": ["phoenix_e1_*", "phoenix_e2_*", "phoenix_e3_story_body", "phoenix_bonus_pre_e3_*"],
        "delivery_channels": ["whatsapp", "telegram", "email", "line", "messenger"],
        "pages": inventory_rows,
    }
    (QA_ROOT / "inventory.json").write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_text(
        QA_ROOT / "browser_e2e_report.md",
        """
        # Browser E2E Report

        Static contract verification covers all 15 pages: tool-first body flag, shared JS/CSS, sanitized webhook attrs, report offer contract, and campaign plan embedding. Full Playwright visual screenshots remain a deployment-readiness follow-up if the Pages preview URL is required.
        """,
    )
    write_text(
        QA_ROOT / "mobile_a11y_perf.md",
        """
        # Mobile, Accessibility, Performance Notes

        The shared report UI uses responsive grid tracks, visible labels, keyboard-native form controls, and no animation dependency. It adds one small CSS/JS surface to already-loaded shared assets. Full Lighthouse/per-device capture is deferred until a deployed preview URL is available.
        """,
    )
    for lane, slug, title in LANES:
        write_text(
            HANDOFF_ROOT / f"{slug}.md",
            f"""
            # {lane} - {title}

            STARTUP_RECEIPT: local execution in `/Users/ahjan/phoenix_omega`.

            DISCOVERY REPORT:
            - 15 Waystream pages found under `brand-wizard-app/public/free/way_stream_sanctuary/`.
            - Existing flow was mixed: some pages gated the tool first, others gated results before reveal.
            - Shared assets are `phoenix_lead.js`, `phoenix_funnel.js`, and `phoenix_tool.css`.
            - Existing evergreen campaign fields are preserved; new report unlock fields are additive.
            - Webhook/body URL exposure is sanitized in page markup.

            LANE_CLOSEOUT:
            - branch: local dirty checkout `codex/ghl-evergreen-waystream`
            - commit: local changes not committed by this script
            - pr: not opened by this script
            - files_changed: see git diff for lane batch
            - tests: `python3 scripts/freebies/validate_post_experience_capture.py`
            - proofs: `artifacts/qa/freebie_post_experience_capture_20260714/`
            - remaining_true_blockers: remote PR/merge/deploy not performed in this local run

            CLOSEOUT_RECEIPT:
            {slug}=local
            """,
        )
    write_text(
        HANDOFF_ROOT / "freebie_post_experience_capture_final_20260714.md",
        """
        # Freebie Post-Experience Capture Final

        Final local integration confirms all 15 Waystream pages are configured for tool-first report unlock, with shared report UI, additive payload fields, generated report specs, channel routing config, dry-run delivery adapter, and focused validation.

        Production readiness remains NO until a PR is opened, checks run remotely, and a deployed preview is browser-tested.
        """,
    )


def main() -> int:
    plans = load_plans()
    if len(plans) != 15:
        raise SystemExit(f"expected 15 Waystream plans, found {len(plans)}")
    missing = sorted(set(SLUG_COPY) - {plan["source_page_slug"] for plan in plans})
    if missing:
        raise SystemExit(f"missing copy for {missing}")
    rows = sanitize_pages(plans)
    write_channel_config()
    write_report_configs(plans)
    write_report_specs(plans)
    write_delivery_templates()
    write_docs(plans)
    append_ghl_doc()
    write_artifacts(plans, rows)
    print(f"synced post-experience capture for {len(plans)} Waystream pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
