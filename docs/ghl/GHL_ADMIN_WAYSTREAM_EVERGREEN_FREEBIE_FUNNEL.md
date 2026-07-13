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

Create these GHL contact custom fields for every email slot E1 through E9:

| Pattern | Example |
| --- | --- |
| `phoenix_eN_title` | `phoenix_e1_title` |
| `phoenix_eN_url` | `phoenix_e1_url` |
| `phoenix_eN_cta` | `phoenix_e1_cta` |
| `phoenix_eN_tool_name` | `phoenix_e1_tool_name` |
| `phoenix_eN_short_description` | `phoenix_e1_short_description` |
| `phoenix_eN_benefit` | `phoenix_e1_benefit` |
| `phoenix_eN_microcopy` | `phoenix_e1_microcopy` |

Also create these special content fields:

| JSON key | Custom field name |
| --- | --- |
| `phoenix_e3_story_body` | `phoenix_e3_story_body` |
| `phoenix_e4_book_title` | `phoenix_e4_book_title` |
| `phoenix_e5_book1_title` | `phoenix_e5_book1_title` |
| `phoenix_e5_book1_url` | `phoenix_e5_book1_url` |
| `phoenix_e5_book1_note` | `phoenix_e5_book1_note` |
| `phoenix_e5_book2_title` | `phoenix_e5_book2_title` |
| `phoenix_e5_book2_url` | `phoenix_e5_book2_url` |
| `phoenix_e5_book2_note` | `phoenix_e5_book2_note` |
| `phoenix_e5_book3_title` | `phoenix_e5_book3_title` |
| `phoenix_e5_book3_url` | `phoenix_e5_book3_url` |
| `phoenix_e5_book3_note` | `phoenix_e5_book3_note` |
| `phoenix_e6_book_title` | `phoenix_e6_book_title` |
| `phoenix_e7_bundle_title` | `phoenix_e7_bundle_title` |
| `phoenix_e8_last_chance_note` | `phoenix_e8_last_chance_note` |

There are 63 repeated E1-E9 fields plus 14 special content fields.

## Workflow Mapping

1. Create a GHL Workflow with an Inbound Webhook trigger.
2. Do not paste the webhook URL into docs, tickets, test output, or PR text. Send it only through the agreed secure credential path so the dev/operator can inject it into the static pages.
3. Map incoming JSON fields to the contact fields above.
4. Add tags from the incoming `tags` array. At minimum, expect `source_freebie_quiz`, `freebie_captured`, and a topic tag such as `quiz_anxiety`.
5. Start the 9-email sequence after the contact is created or updated.
6. Import the branded Waystream HTML templates from:
   - `funnel/waystream_sanctuary/emails/email_1_tool_delivery.html`
   - `funnel/waystream_sanctuary/emails/email_2_second_practice.html`
   - `funnel/waystream_sanctuary/emails/email_3_transformation_story.html`
   - `funnel/waystream_sanctuary/emails/email_4_book_recommendation.html`
   - `funnel/waystream_sanctuary/emails/email_5_more_books.html`
   - `funnel/waystream_sanctuary/emails/email_6_book_two_recommendation.html`
   - `funnel/waystream_sanctuary/emails/email_7_book_three_bundle.html`
   - `funnel/waystream_sanctuary/emails/email_8_last_chance.html`
   - `funnel/waystream_sanctuary/emails/email_9_still_here.html`
7. In each email, use the stored custom values for that slot. Email 3 uses `phoenix_e3_story_body`; Email 4 uses `phoenix_e4_book_title`; Email 5 uses the `phoenix_e5_book1_*` through `phoenix_e5_book3_*` fields.

## Important Operating Rule

The email plan is already resolved by the page before the webhook fires. GHL should store the values it receives and use those stored values in the 9-email sequence. GHL should not fetch a feed, rebuild a weekly newsletter, or infer a replacement campaign plan.

If any `phoenix_e*` value is missing on a test contact, stop the test and ask dev to run:

```bash
python3 scripts/freebies/validate_campaign_plan.py --brand-id way_stream_sanctuary
```

Plan source: `config/freebies/waystream_evergreen_campaign_plan.yaml`.
