# Operator — GHL handoff (you do not touch GHL)

## Forward these 3 files to your GHL admin

1. **[ghl/GHL_ADMIN_START_HERE.md](../ghl/GHL_ADMIN_START_HERE.md)** — whole story + checklist  
2. **[GHL_INTEGRATION_GUIDE.md](../GHL_INTEGRATION_GUIDE.md)** — feed format + merge tags  
3. **[ghl/PROOF_LOOP_WORKFLOW_TEMPLATE.md](../ghl/PROOF_LOOP_WORKFLOW_TEMPLATE.md)** — import WF1–WF4  

**Also attach** (quiz webhook only): [GHL_ADMIN_HANDOFF_FREEBIE_CAPTURE.md](../GHL_ADMIN_HANDOFF_FREEBIE_CAPTURE.md)

Optional reference for them: [FUNNEL_EMAIL_AUTOMATION_MAP.md](../FUNNEL_EMAIL_AUTOMATION_MAP.md)

---

## What you wait for back

```
PHOENIX_GHL_FUNNEL_WEBHOOK=https://services.leadconnectorhq.com/hooks/...
Feed URL confirmed: https://.../marketing_feed.json
Sub-account: ...
Workflows published: yes
Test contact: yes
```

Paste the webhook line to your dev agent or run:

```bash
./scripts/freebies/setup_ghl_webhook.sh '<webhook-url>'
./scripts/marketing/setup_ghl_feed_stack.sh stillness_press en_US
```

Feed URL shape (after R2 + CDN live):

```text
https://<cdn>/pearl-prime-content/{brand_id}/{locale}/{week}/marketing_feed.json
```

Build locally: `python3 scripts/marketing/build_marketing_feed.py --brand-id stillness_press`

---

## What Phoenix does (you don't)

- Publishes new `marketing_feed.json` every **Monday**
- Hosts quiz + free tool landing pages
- Builds email copy and shop links into the feed

## What GHL admin does (they do)

- One-time: import workflows, paste feed URL, map 3 fields, quiz webhook
- Weekly: **nothing**

---

**Burnout funnel (separate):** [funnel/burnout_reset/GHL_HANDBOFF.md](../../funnel/burnout_reset/GHL_HANDBOFF.md)
