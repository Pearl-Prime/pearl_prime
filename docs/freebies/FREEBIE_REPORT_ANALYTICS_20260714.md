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
