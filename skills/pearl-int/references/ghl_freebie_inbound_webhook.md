# GHL — Freebie inbound webhook (phoenix_lead.js)

> **Complete GHL package (feed + 15-page webhook):** [docs/handoffs/GHL_TOTAL_INTEGRATION_HANDOFF_20260623.md](../../docs/handoffs/GHL_TOTAL_INTEGRATION_HANDOFF_20260623.md)  
> **GHL administrator (webhook only):** [docs/GHL_ADMIN_HANDOFF_FREEBIE_CAPTURE.md](../../docs/GHL_ADMIN_HANDOFF_FREEBIE_CAPTURE.md)  
> **Canonical env names:** `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` §8b.

## What this wires

Static funnel landings under `brand-wizard-app/public/free/` (15 pages) POST capture to a **GHL Inbound Webhook** URL via `phoenix_lead.js`. Until `PHOENIX_GHL_FUNNEL_WEBHOOK` is set, capture **skips gracefully** (no crash).

## Operator portal flow (you paste; Pearl_Int stores + validates)

1. Log in: https://app.gohighlevel.com/
2. Open the **sub-account / location** that owns freebie contacts.
3. **Automation → Create workflow** (or open existing freebie capture workflow).
4. Add trigger: **Inbound Webhook**.
5. Copy the webhook URL (pattern: `https://services.leadconnectorhq.com/hooks/...`).
6. Map payload fields from `quiz_segment_map.yaml` → contact fields + tags:
   - `email`, `first_name`, `quiz_id`, `topic`, `score`, `score_band`, `funnel_slug`, `tags`
   - Custom fields: use **UUID** ids from Settings → Custom Fields (not strings like `"topic"`).
7. Paste the URL to Pearl_Int (chat) or run locally:

```bash
./scripts/freebies/setup_ghl_webhook.sh '<inbound-webhook-url>'
```

That script writes Keychain (`phoenix-omega` / `PHOENIX_GHL_FUNNEL_WEBHOOK`), optional `config/local/ghl_funnel_webhook.url`, injects `data-ghl-webhook` on all **15 funnel** `<body>` tags, and runs `verify_ghl_webhook_push.py`.

## GitHub Actions (CI live-push step)

```bash
gh secret set PHOENIX_GHL_FUNNEL_WEBHOOK --body '<inbound-webhook-url>'
```

Workflow: `.github/workflows/freebie-policy.yml` (skips live push when secret unset).

## Validation (non-destructive)

```bash
eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
python3 scripts/freebies/inject_ghl_webhook.py --require-env
python3 scripts/freebies/verify_ghl_webhook_push.py   # POST smoke payload
python3 scripts/freebies/smoke_freebie_capture.py
```

## Deploy static pages

Do **not** laptop-deploy Cloudflare Pages. Push to `main` → `brand-admin-onboarding-pages.yml` builds `brand-wizard-app` (includes `/free/*`). See `skills/pearl-int/references/cloudflare_pages_deploy.md`.

## Known traps

| Trap | Fix |
|------|-----|
| Contacts API custom field `"topic"` string id | Use UUID from GHL Settings → Custom Fields |
| `--require-env` passes via local file only | By design: production gate requires Keychain/env, not gitignored file |
| Empty `config/local/ghl_funnel_webhook.url` | File ignored; use non-empty line or Keychain |
| Webhook works but no contact | Check workflow is **Published** and field mapping matches payload keys |
