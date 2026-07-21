# Operator — GHL handoff (you do not touch GHL)

## Per-brand packages (2026-06-24)

| Brand | Total handoff | Forward email | Feed items (2026-W26) |
|-------|---------------|---------------|------------------------|
| **Stillness Press** | [GHL_TOTAL_INTEGRATION_HANDOFF_20260623.md](./GHL_TOTAL_INTEGRATION_HANDOFF_20260623.md) | [GHL_ADMIN_FORWARD_EMAIL_20260623.txt](./GHL_ADMIN_FORWARD_EMAIL_20260623.txt) | ~109 |
| **Open Vessel Press (Devotion Path)** | [GHL_TOTAL_INTEGRATION_HANDOFF_DEVOTION_PATH_20260624.md](./GHL_TOTAL_INTEGRATION_HANDOFF_DEVOTION_PATH_20260624.md) | [GHL_ADMIN_FORWARD_EMAIL_DEVOTION_PATH_20260624.txt](./GHL_ADMIN_FORWARD_EMAIL_DEVOTION_PATH_20260624.txt) | 120 |
| **Waystream Sanctuary** | [GHL_TOTAL_INTEGRATION_HANDOFF_WAYSTREAM_20260624.md](./GHL_TOTAL_INTEGRATION_HANDOFF_WAYSTREAM_20260624.md) | [GHL_ADMIN_FORWARD_EMAIL_WAYSTREAM_20260624.txt](./GHL_ADMIN_FORWARD_EMAIL_WAYSTREAM_20260624.txt) | 109 |

Each brand uses a **separate GHL sub-account** and **separate inbound webhook** env var:

| Brand | Webhook env var | Funnel base path |
|-------|-----------------|------------------|
| Stillness Press | `PHOENIX_GHL_FUNNEL_WEBHOOK_STILLNESS` | `/free/{slug}/` |
| Devotion Path | `PHOENIX_GHL_FUNNEL_WEBHOOK_DEVOTION` | `/free/devotion_path/{slug}/` |
| Waystream Sanctuary | `PHOENIX_GHL_FUNNEL_WEBHOOK_WAYSTREAM` | `/free/way_stream_sanctuary/{slug}/` |

---

## Complete package — Stillness Press (recommended template)

Forward the **total integration handoff** — covers feed (E1–E5) **and** 15-page webhook:

- **[GHL_TOTAL_INTEGRATION_HANDOFF_20260623.md](./GHL_TOTAL_INTEGRATION_HANDOFF_20260623.md)** — cover sheet + checklist + 15-topic table
- **[GHL_ADMIN_FORWARD_EMAIL_20260623.txt](./GHL_ADMIN_FORWARD_EMAIL_20260623.txt)** — copy/paste email to GHL admin

Attach these **4 files** (listed inside the total handoff):

1. **[ghl/GHL_ADMIN_START_HERE.md](../ghl/GHL_ADMIN_START_HERE.md)** — whole story + 6-step checklist  
2. **[GHL_INTEGRATION_GUIDE.md](../GHL_INTEGRATION_GUIDE.md)** — feed format + merge tags  
3. **[ghl/PROOF_LOOP_WORKFLOW_TEMPLATE.md](../ghl/PROOF_LOOP_WORKFLOW_TEMPLATE.md)** — import WF1–WF4  
4. **[GHL_ADMIN_HANDOFF_FREEBIE_CAPTURE.md](../GHL_ADMIN_HANDOFF_FREEBIE_CAPTURE.md)** — 15 funnel pages, inbound webhook  

Optional reference for them: [FUNNEL_EMAIL_AUTOMATION_MAP.md](../FUNNEL_EMAIL_AUTOMATION_MAP.md)

---

## What you wait for back

```
PHOENIX_GHL_FUNNEL_WEBHOOK=<REDACTED_GHL_WEBHOOK_URL>
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

Build locally (auto-discovers all **15 topics** — no `--topic` flags):

```bash
python3 scripts/marketing/build_marketing_feed.py --brand-id stillness_press --locale en_US
```

---

## What Phoenix does (you don't)

- Publishes new `marketing_feed.json` every **Monday**
- Hosts quiz + free tool landing pages
- Builds email copy and shop links into the feed

## What GHL admin does (they do)

- One-time: import workflows, paste feed URL, map 3 fields, funnel webhook
- Weekly: **nothing**

---

**Burnout funnel (separate):** [funnel/burnout_reset/GHL_HANDBOFF.md](../../funnel/burnout_reset/GHL_HANDBOFF.md)
