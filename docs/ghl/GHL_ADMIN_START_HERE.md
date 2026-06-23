# GHL Admin — Start Here

**Audience:** Your GoHighLevel administrator (48 Social or agency).  
**You (brand owner):** Forward this file + [GHL_INTEGRATION_GUIDE.md](../GHL_INTEGRATION_GUIDE.md) + [PROOF_LOOP_WORKFLOW_TEMPLATE.md](./PROOF_LOOP_WORKFLOW_TEMPLATE.md). You do not configure GHL yourself.

---

## The whole story (60 seconds)

1. **Phoenix** builds books, free tools, videos, and a weekly **content feed** (JSON file on the web).
2. **You (GHL admin)** connect GHL once: import email workflows, paste the feed URL, map three fields.
3. **Every Monday** Phoenix publishes a new feed. GHL reads it. **You do not re-enter links or rewrite emails.**
4. **The funnel:** Social post → free tool/quiz → capture email → **3 nurture emails** (two exercises + a story) → **paid offer** on pearlprime.shop (only when the feed says an item is ready) → optional series upsell.

**Psychology rule (non-negotiable):** Two felt exercises **before** any book offer. Story **before** price. See [Proof Loop](#the-proof-loop-what-contacts-experience).

---

## What you do NOT do

- Hand-type Amazon / Google Play / shop URLs each week  
- Write email copy from scratch (merge tags pull from the feed)  
- Build landing pages (Phoenix hosts them)  
- Pick which book to promote (the feed decides)

---

## What you do (one-time setup)

| Step | Action | Time |
|------|--------|------|
| 1 | Create or open the brand **GHL sub-account**; connect social accounts (or Metricool). | ~30 min |
| 2 | **Import workflows** WF1–WF4 from [PROOF_LOOP_WORKFLOW_TEMPLATE.md](./PROOF_LOOP_WORKFLOW_TEMPLATE.md). | ~45 min |
| 3 | **Paste the weekly feed URL** we give you (one URL per brand × locale). | 2 min |
| 4 | **Map 3 fields** on each feed item: `cta_url`, `pricing` (free/paid), `content_type`. | 10 min |
| 5 | **Quiz capture webhook** (5 flagship quiz pages) — [separate checklist](../GHL_ADMIN_HANDOFF_FREEBIE_CAPTURE.md); send us back one URL. | ~20 min |
| 6 | (Optional) **Burnout funnel app** — Contacts API if engineering enables `funnel/burnout_reset/` — [GHL_HANDBOFF.md](../../funnel/burnout_reset/GHL_HANDBOFF.md). | Dev-led |

**Send back to project owner:**

```
PHOENIX_GHL_FUNNEL_WEBHOOK=https://services.leadconnectorhq.com/hooks/...
Feed URL (confirm): https://.../marketing_feed.json
Sub-account name: ...
Workflow published: yes/no
Test contact created: yes/no
```

---

## Weekly routine

**Do nothing.** Phoenix replaces `marketing_feed.json` every Monday. Your GHL automation should **re-fetch or use the stable URL** we configured (same path, new file contents).

If a week shows no paid item in the feed, **E4 (paid offer) is skipped automatically** — contacts still get E1–E3.

---

## The Proof Loop (what contacts experience)

```
Social / ad
    ↓
Free quiz or free tool (landing page — Phoenix hosted)
    ↓
Email captured → GHL contact + tags
    ↓
E1 (now)     — First exercise / tool link
E2 (+24h)    — Second exercise (different technique)
E3 (+72h)    — Story only (no pitch)
E4 (+120h)   — Paid offer → pearlprime.shop (ONLY if feed has ready paid item)
E5 (+5d)     — Series / more books (optional)
    ↓
Post-purchase — Buyer tag unlocks workbooks; Series Upsell workflow (WF3)
```

**Wrong:** Freebie → story → immediate book pitch.  
**Right:** Exercise → Exercise → Story → Offer.

Canonical copy lives in `docs/email_sequences/proof_loop_sequence.md`. Workflows use **merge tags** filled from the feed.

---

## The weekly feed (what you paste)

**One URL per brand**, updated in place each week. Shape:

```text
https://<cdn-or-r2-public>/pearl-prime-content/{brand_id}/{locale}/{week}/marketing_feed.json
```

Example week folder: `2026-W26`. Your project owner gives the exact URL.

### You only map these 3 fields in GHL

| Feed field | GHL use |
|------------|---------|
| `cta_url` | Link in email / SMS / social automation |
| `pricing` | `free` → nurture only; `paid` → eligible for E4 offer step |
| `content_type` | Pick template (exercise, story, book, audio, etc.) |

Everything else (titles, body snippets, shop links, exercise URLs) is **pre-filled in the JSON** — use merge tags listed in the integration guide.

Full schema: [config/marketing/marketing_feed_schema.yaml](../../config/marketing/marketing_feed_schema.yaml).

---

## Four workflows (import once)

| ID | Name | Trigger | Purpose |
|----|------|---------|---------|
| **WF1** | Proof Loop | Contact tagged `freebie_captured` or feed trigger | E1–E5 spine |
| **WF2** | Tier bonus drip | After E3, before E4 | Extra free assets (audio/PDF) from feed `email_slot` |
| **WF3** | Series upsell | Buyer tag or post-E5 | Book 2 / Book 3 path |
| **WF4** | Re-engagement | 90 days no open | Win-back |

Step-by-step import: [PROOF_LOOP_WORKFLOW_TEMPLATE.md](./PROOF_LOOP_WORKFLOW_TEMPLATE.md).  
Slot timing detail: [FUNNEL_EMAIL_AUTOMATION_MAP.md](../FUNNEL_EMAIL_AUTOMATION_MAP.md).

---

## Quiz pages (inbound webhook — separate from feed)

Five interactive quizzes POST JSON when someone submits email. No API key — **inbound webhook URL only**.

Full checklist: [GHL_ADMIN_HANDOFF_FREEBIE_CAPTURE.md](../GHL_ADMIN_HANDOFF_FREEBIE_CAPTURE.md).

---

## What Phoenix builds vs what you touch

| Layer | In Phoenix repo | You (GHL admin) |
|-------|-----------------|-----------------|
| E1–E4 Proof Loop spine | WF1 template + email copy | **Import WF1 once** |
| E5 + series upsell | Config + copy | **Import WF3 once** |
| Tier bonus drip | `email_slot` in weekly feed | **Import WF2** (optional) |
| Re-engagement 90d | WF4 template | **Import WF4 once** |
| Welcome & Depth variant | Auto in feed (`funnel_variant`) | WF1 branch — no extra setup |
| Japan LINE m1–m7 | ja_JP only | **Ignore** (not US GHL) |
| Phoenix Protocol 3 sequences | Doc only | **Ignore** (future) |

**Mental model:** WF1 is the spine. WF2–WF4 are optional layers. Everything else is Phoenix engineering.

---

## Docs package (give admin #1–#3)

| # | Document | Purpose |
|---|----------|---------|
| **1** | **This file** | Story + one-time checklist + weekly “do nothing” |
| **2** | [GHL_INTEGRATION_GUIDE.md](../GHL_INTEGRATION_GUIDE.md) | Feed format, merge tags, custom fields, diagrams |
| **3** | [PROOF_LOOP_WORKFLOW_TEMPLATE.md](./PROOF_LOOP_WORKFLOW_TEMPLATE.md) | Import WF1–WF4; timing; variant branch |
| 4 | [GHL_ADMIN_HANDOFF_FREEBIE_CAPTURE.md](../GHL_ADMIN_HANDOFF_FREEBIE_CAPTURE.md) | Quiz webhook only |
| 5 | [FUNNEL_EMAIL_AUTOMATION_MAP.md](../FUNNEL_EMAIL_AUTOMATION_MAP.md) | Optional — tier bundles & extra sequences |

**Not for day-to-day admin:** [48_SOCIAL_GHL_BRAND_ADMIN_SPEC.md](../48_SOCIAL_GHL_BRAND_ADMIN_SPEC.md) (full 48 Social context).

---

## Status (what’s live vs template)

| Piece | Status |
|-------|--------|
| Proof Loop email **copy** | Ready in repo |
| WF1–WF4 workflow **template** | Import into GHL |
| `marketing_feed.json` **builder** | `scripts/marketing/build_marketing_feed.py` — Mondays |
| **Public feed URL** | R2 `pearl-prime-content` + CDN (operator gives URL) |
| Quiz **inbound webhook** | Code live — you return one URL |
| Burnout funnel **Contacts API** | Optional — dev-led |

---

**Version:** 2026-06-23 · Phoenix Omega / SpiritualTech Systems
