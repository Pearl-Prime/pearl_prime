# Freebie Post-Experience Capture Launch

## Launch Checklist

- Run `python3 scripts/freebies/validate_post_experience_capture.py`.
- Run `python3 scripts/freebies/validate_campaign_plan.py --brand-id way_stream_sanctuary`.
- Dry-run report delivery for WhatsApp, Telegram, email, LINE, and Messenger.
- Confirm GHL custom fields include all new report unlock fields.
- Confirm no full webhook URLs or credentials exist in changed docs, artifacts, tests, or static pages.

## Rollback

Revert the shared JS/CSS and restore the previous static HTML body attributes. Keep generated report specs; they are inert without the JS flow.
