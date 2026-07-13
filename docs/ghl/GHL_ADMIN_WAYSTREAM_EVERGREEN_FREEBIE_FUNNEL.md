# GHL Admin Handoff: Waystream Evergreen Freebie Funnel

Audience: GoHighLevel admin for Phoenix Omega / Waystream Sanctuary.

This is evergreen freebie-funnel logic. It is resolved once when a visitor submits a Waystream freebie form. It is not RSS, newsletter, or scheduled weekly content logic.

## What The Site Sends

Each Waystream freebie page sends one JSON payload to the inbound webhook. The payload contains contact context plus all planned fields for emails 1 through 9.

Map these standard/contact fields:

| JSON key | GHL target |
| --- | --- |
| `email` | Contact Email |
| `name` | Contact Full Name, if used |
| `first_name` | Contact First Name |
| `phone` | Contact Phone, if present |
| `tags` | Contact tags |

Create GHL contact custom fields for these context fields:

| JSON key | Custom field name |
| --- | --- |
| `brand_id` | `brand_id` |
| `freebie_id` | `freebie_id` |
| `quiz_id` | `quiz_id` |
| `topic` | `topic` |
| `funnel_variant` | `funnel_variant` |
| `source_page_slug` | `source_page_slug` |
| `campaign_plan_id` | `campaign_plan_id` |
| `score` | `score` |
| `score_band` | `score_band` |
| `answers_json` | `answers_json` |

Create these GHL contact custom fields exactly:

| Email | Title field | URL field | CTA field |
| --- | --- | --- | --- |
| E1 | `phoenix_e1_title` | `phoenix_e1_url` | `phoenix_e1_cta` |
| E2 | `phoenix_e2_title` | `phoenix_e2_url` | `phoenix_e2_cta` |
| E3 | `phoenix_e3_title` | `phoenix_e3_url` | `phoenix_e3_cta` |
| E4 | `phoenix_e4_title` | `phoenix_e4_url` | `phoenix_e4_cta` |
| E5 | `phoenix_e5_title` | `phoenix_e5_url` | `phoenix_e5_cta` |
| E6 | `phoenix_e6_title` | `phoenix_e6_url` | `phoenix_e6_cta` |
| E7 | `phoenix_e7_title` | `phoenix_e7_url` | `phoenix_e7_cta` |
| E8 | `phoenix_e8_title` | `phoenix_e8_url` | `phoenix_e8_cta` |
| E9 | `phoenix_e9_title` | `phoenix_e9_url` | `phoenix_e9_cta` |

## Workflow Mapping

1. Create a GHL Workflow with an Inbound Webhook trigger.
2. Do not paste the webhook URL into docs, tickets, test output, or PR text. Send it only through the agreed secure credential path so the dev/operator can inject it into the static pages.
3. Map incoming JSON fields to the contact fields above.
4. Add tags from the incoming `tags` array. At minimum, expect `source_freebie_quiz`, `freebie_captured`, and a topic tag such as `quiz_anxiety`.
5. Start the 9-email sequence after the contact is created or updated.
6. In each email, use the stored custom values for that slot:
   - Email 1 uses `phoenix_e1_title`, `phoenix_e1_url`, `phoenix_e1_cta`.
   - Continue the same pattern through Email 9.

## Important Operating Rule

The email plan is already resolved by the page before the webhook fires. GHL should store the values it receives and use those stored values in the 9-email sequence. GHL should not fetch a feed, rebuild a weekly newsletter, or infer a replacement campaign plan.

If any `phoenix_e*_title`, `phoenix_e*_url`, or `phoenix_e*_cta` value is missing on a test contact, stop the test and ask dev to run:

```bash
python3 scripts/freebies/validate_campaign_plan.py --brand-id way_stream_sanctuary
```

Plan source: `config/freebies/waystream_evergreen_campaign_plan.yaml`.
