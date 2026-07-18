# Freebie Post-Experience Capture Prompt Pack

## Program

- Goal: refactor Waystream freebie funnels so the visitor completes the interactive tool first, then opts in to receive a personalized report by WhatsApp, Telegram, email, and regionally LINE/Messenger where configured.
- Pack date: 2026-07-14.
- Prompt count: 25 prompt files total, including one master dispatcher and 24 child lanes.
- Master dispatcher: `00_MASTER_DISPATCH_PROMPT.md`.

## Product Doctrine

The user should not land on a capture wall first. They should enter the actual interactive experience, complete it, feel investment, then see a strong report unlock offer:

- "You did it" completion moment.
- Valuable, specific report promise.
- Benefit-driven marketing copy spanning somatic, nervous-system, psychological, and spiritual benefits, without medical overclaims.
- Channel choice biased to WhatsApp first, with Telegram after integration, email fallback, and LINE/Messenger routing for Japan where integrations exist.
- Full consent and privacy clarity before sending messages.

## Wave Order

- Wave 0: 01 foundation audit, 02 product architecture.
- Wave 1: 03 shared completion flow, 04 report schema, 05 channel routing, 06 CRM/GHL payload, 07 marketing copy system, 08 per-tool report specs, 09 consent/privacy.
- Wave 2: 10 Telegram integration, 11 existing channel hardening, 12 Cloudflare/report delivery endpoint, 13 A/B testing, 14 analytics.
- Wave 3: 15-18 HTML app refactor waves across the 15 Waystream tools.
- Wave 4: 19 GHL/admin docs, 20 delivery templates and nurture.
- Wave 5: 21 contract tests, 22 browser E2E, 23 mobile/a11y/perf, 24 final integration and deploy readiness.

## Lane Matrix

| Prompt | Owner | Scope | Depends on | Hot files |
| --- | --- | --- | --- | --- |
| 01 | Pearl_PM | inventory and workstream registration | none | docs/artifacts only |
| 02 | Pearl_Architect | product and system architecture | 01 | docs/specs only |
| 03 | Pearl_Dev | shared post-completion flow engine | 02 | `brand-wizard-app/public/free/js/**` |
| 04 | Pearl_Dev | report schema and local generator | 02 | `scripts/freebies/**`, config |
| 05 | Pearl_Int | delivery-channel routing contract | 02,03 | shared JS/config |
| 06 | Pearl_Int | GHL payload and CRM fields | 02,04,05 | `phoenix_lead.js`, docs/ghl |
| 07 | Pearl_Marketing | unlock copy framework | 02 | config/docs copy |
| 08 | Pearl_Writer | per-tool report promise/specs | 02,07 | config/freebies |
| 09 | Pearl_Legal/QA | consent, claims, privacy | 02,05,07 | docs/config |
| 10 | Pearl_Int | Telegram integration | 05,09 | integration scripts/docs |
| 11 | Pearl_Int | WhatsApp/LINE/Messenger hardening | 05,09 | integration scripts/docs |
| 12 | Pearl_DevOps | Cloudflare/report delivery endpoint | 04,05,09,10,11 | worker/scripts/docs |
| 13 | Pearl_Dev | A/B test framework | 03,05,07,09 | shared JS/config |
| 14 | Pearl_QA | analytics/event taxonomy | 03,05,13 | shared JS/docs |
| 15 | Pearl_Dev | app wave A | 03,04,05,07,08 | selected HTML pages |
| 16 | Pearl_Dev | app wave B | 03,04,05,07,08 | selected HTML pages |
| 17 | Pearl_Dev | app wave C | 03,04,05,07,08 | selected HTML pages |
| 18 | Pearl_Dev | app wave D | 03,04,05,07,08 | selected HTML pages |
| 19 | Pearl_Int | GHL admin handoff update | 06,10,11,12 | docs/ghl |
| 20 | Pearl_Writer/Int | delivery templates/nurture | 06,07,08,10,11,12 | funnel/waystream_sanctuary |
| 21 | Pearl_QA | unit/contract tests | 03-14 | tests/scripts |
| 22 | Pearl_QA | browser E2E | 15-18,21 | QA artifacts |
| 23 | Pearl_QA | mobile/a11y/perf | 15-18,21 | QA artifacts |
| 24 | Pearl_PM | final integrator/deploy readiness | all prior | docs/artifacts |

## Deconfliction Rules

- Lanes 03, 05, 06, 13, and 14 all touch shared JS/config. Run them in dependency order, not parallel.
- Lanes 15-18 can run in parallel only after lanes 03-09 are merged and each lane owns disjoint HTML pages.
- No lane may paste live webhook URLs, API keys, bot tokens, or channel secrets into docs or PR text.
- No lane may claim production readiness until browser E2E proves the tool-first flow on all 15 Waystream pages.

## Final Status

Status: prompt pack prepared, not executed.
