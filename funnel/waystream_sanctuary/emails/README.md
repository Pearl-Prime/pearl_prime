# Waystream Sanctuary Evergreen Email Templates

These are the branded GoHighLevel HTML templates for the evergreen freebie
funnel. They are not landing pages and they do not fetch RSS.

Import one template per workflow email:

- `email_1_tool_delivery.html`
- `email_2_second_practice.html`
- `email_bonus_pre_story.html` (send before E3 when `welcome_depth` is blank or missing)
- `email_3_transformation_story.html`
- `email_4_book_recommendation.html`
- `email_5_more_books.html`
- `email_6_book_two_recommendation.html`
- `email_7_book_three_bundle.html`
- `email_8_last_chance.html`
- `email_9_still_here.html`

The freebie form webhook stores merge fields on the contact:

- `phoenix_e1_title`, `phoenix_e1_url`, `phoenix_e1_cta`
- `phoenix_e1_tool_name`, `phoenix_e1_short_description`, `phoenix_e1_benefit`, `phoenix_e1_microcopy`
- same pattern through `phoenix_e9_*`
- special fields: `phoenix_e3_story_body`, `phoenix_e4_book_title`,
  `phoenix_e5_book1_*`, `phoenix_e5_book2_*`, `phoenix_e5_book3_*`,
  `phoenix_e6_book_title`, `phoenix_e7_bundle_title`,
  `phoenix_e8_last_chance_note`
- bonus-before-E3 fields: `phoenix_bonus_pre_e3_title`,
  `phoenix_bonus_pre_e3_url`, `phoenix_bonus_pre_e3_cta`,
  `phoenix_bonus_pre_e3_tool_name`,
  `phoenix_bonus_pre_e3_short_description`,
  `phoenix_bonus_pre_e3_benefit`, `phoenix_bonus_pre_e3_microcopy`,
  `phoenix_bonus_pre_e3_html_template`,
  `phoenix_bonus_pre_e3_send_if_welcome_depth_missing`

WF2 rule: send `email_bonus_pre_story.html` before Email 3 only when
`welcome_depth` is blank or missing, then return to the normal E3 story email.

Admin rule: if any field renders blank in a test contact, stop the live test and
rerun `python3 scripts/freebies/validate_campaign_plan.py --brand-id way_stream_sanctuary`.
