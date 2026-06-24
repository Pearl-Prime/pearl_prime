# GHL Admin Handoff — Interactive Funnel Lead Capture

> **Part of the GHL package.** Admin should read [ghl/GHL_ADMIN_START_HERE.md](./ghl/GHL_ADMIN_START_HERE.md) first. This doc is the **inbound webhook** for all **15 interactive funnel pages** (quizzes, timers, audits, script kits, templates).

**Forward this entire document to your GoHighLevel administrator.**

---

## Email you can copy/paste to your GHL admin

**Subject:** GHL setup — inbound webhook for interactive funnel lead capture

Hi — we need a simple **Inbound Webhook** workflow in GoHighLevel for our **15 free interactive funnel pages**. When someone completes a tool (quiz, breath timer, audit, script kit, etc.) and enters their email, our site sends a JSON payload to your webhook. You create the workflow, map the fields, and send us back the webhook URL.

**What we need back from you:** the full Inbound Webhook URL (starts with `https://services.leadconnectorhq.com/hooks/...`).

**Full instructions:** see the checklist below (or attach this file).

Thanks!

---

## What this is (plain English)

- **15 live interactive funnel pages** on our website — breath timers, scored assessments, reflection audits, script kits, letter templates, and more (see table below).
- User completes the tool → enters name + email at the capture gate → our page **POSTs JSON** to your GHL Inbound Webhook.
- GHL should **create or update a contact**, **apply tags**, and optionally store answers in **custom fields**.
- No API key needed for this path — **webhook URL only**.

**Not all pages are scored quizzes.** Reflection prompts and somatic timers may send `score: null` and `score_band: null` — map those fields as optional.

**Separate project (not this handoff):** the Burnout Reset funnel app uses the GHL Contacts API (`GHL_API_KEY` + `GHL_LOCATION_ID`). See `funnel/burnout_reset/GHL_HANDBOFF.md` if you also own that funnel.

---

## GHL admin checklist

### A. Create the workflow

1. Log in: https://app.gohighlevel.com/
2. Open the correct **sub-account / location** (where marketing contacts should live).
3. Go to **Automation** → **Workflows** → **Create workflow**.
4. Name it something like: `Interactive Funnel — Inbound Capture`.
5. **Trigger:** choose **Inbound Webhook**.
6. **Copy the webhook URL** GHL shows you — this is what you send back to us.  
   Example shape: `https://services.leadconnectorhq.com/hooks/XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX`
7. Leave the workflow open — you will map fields next.

### B. Map incoming JSON → contact

Our site sends **JSON** (`Content-Type: application/json`). In the webhook trigger, map each incoming field to a GHL contact field:

| Incoming JSON key | Put on GHL contact as | Required? | Notes |
|-------------------|----------------------|-----------|--------|
| `email` | Email | **Yes** | Primary identifier |
| `first_name` | First name | Recommended | May be empty |
| `quiz_id` | Custom field | Recommended | e.g. `capacity_assessment`, `breath_timer` |
| `topic` | Custom field | Recommended | e.g. `compassion_fatigue`, `anxiety` |
| `funnel_slug` | Custom field | Optional | URL slug, e.g. `compassion-fatigue-audit` |
| `score` | Custom field | Optional | Numeric quiz score; **null** on reflection/somatic pages |
| `score_band` | Custom field | Optional | `low`, `medium`, or `high`; **null** when not scored |
| `answers_json` | Custom field | Optional | Stringified quiz answers (if present) |
| `tags` | Tags | Recommended | Array of tag strings — see § Tags below |

**Custom fields:** In GHL go to **Settings → Custom Fields**. Create fields with clear names (e.g. `Quiz ID`, `Topic`, `Score Band`). When mapping in the workflow, use each field’s **UUID** (GHL shows this in custom field settings). Do **not** use human labels like `"topic"` as the API id on Contacts API calls — UUID only.

### C. Apply tags

The payload may include a `tags` array. Add a workflow step to **add tags** from the webhook payload (or map known tags manually).

**Tags you will see:**

| Pattern | When |
|---------|------|
| `source_freebie_quiz`, `freebie_captured` | All 15 funnel pages |
| `quiz_{topic}` | e.g. `quiz_anxiety`, `quiz_burnout`, `quiz_grief` |
| `severity_low` / `severity_medium` / `severity_high` | Scored assessments only |

### D. Publish and test

1. **Publish** the workflow.
2. In GHL, use the webhook **“Send test”** or submit a test from our side once the URL is wired.
3. Confirm a **new contact** appears with email + tags.
4. Send the webhook URL to the project owner (see § What to send back).

### E. Optional — nurture sequence

After contact is created, you may attach your existing **email/SMS automations** (welcome, nurture, book offer). Our dev team does **not** send E1–E5 from the static pages — that is your lane in GHL if we use `email_mode: ghl` on funnel apps.

---

## Sample JSON payloads (what hits your webhook)

**Scored assessment** (compassion fatigue audit):

```json
{
  "email": "jane@example.com",
  "first_name": "Jane",
  "quiz_id": "capacity_assessment",
  "topic": "compassion_fatigue",
  "funnel_slug": "compassion-fatigue-audit",
  "score": 12,
  "score_band": "medium",
  "answers_json": null,
  "tags": ["source_freebie_quiz", "quiz_compassion_fatigue", "freebie_captured", "severity_medium"]
}
```

**Somatic timer** (anxiety nervous system reset):

```json
{
  "email": "jane@example.com",
  "first_name": "Jane",
  "quiz_id": "breath_timer_interactive",
  "topic": "anxiety",
  "funnel_slug": "anxiety-nervous-system-reset",
  "score": null,
  "score_band": null,
  "answers_json": null,
  "tags": ["quiz_anxiety"]
}
```

**Reflection audit** (burnout energy audit — no numeric score):

```json
{
  "email": "jane@example.com",
  "first_name": "Jane",
  "quiz_id": "capacity_assessment",
  "topic": "burnout",
  "funnel_slug": "burnout-energy-audit",
  "score": null,
  "score_band": null,
  "answers_json": null,
  "tags": ["source_freebie_quiz", "quiz_burnout", "freebie_captured"]
}
```

**Smoke test payload** (our CI may send once):  
`freebie-smoke-test@example.com`, `quiz_id: capacity_assessment`, `tags: ["smoke_test", "freebie_capture"]` — safe to delete after verifying.

---

## Fifteen funnel capture pages (for your reference)

| Topic | `topic` | `funnel_slug` | `quiz_id` (archetype) | `capture_type` |
|-------|---------|---------------|----------------------|----------------|
| Anxiety | `anxiety` | `anxiety-nervous-system-reset` | `breath_timer_interactive` | somatic |
| Compassion fatigue | `compassion_fatigue` | `compassion-fatigue-audit` | `capacity_assessment` | assessment |
| Overthinking | `overthinking` | `overthinking-thought-sorter` | `thought_sorter_assessment` | assessment |
| Financial anxiety | `financial_anxiety` | `financial-anxiety-check-in` | `financial_checkin` | assessment |
| Courage | `courage` | `courage-decision-map` | `decision_resistance_map` | assessment |
| Burnout | `burnout` | `burnout-energy-audit` | `capacity_assessment` | assessment (reflection) |
| Self-worth | `self_worth` | `self-worth-inventory` | `worth_inventory` | assessment |
| Imposter syndrome | `imposter_syndrome` | `imposter-evidence-log` | `evidence_log` | assessment |
| Boundaries | `boundaries` | `boundaries-script-kit` | `script_practice` | script |
| Depression | `depression` | `depression-momentum-kit` | `micro_action_kit` | kit |
| Social anxiety | `social_anxiety` | `social-anxiety-toolkit` | `pre_event_protocol` | kit |
| Financial stress | `financial_stress` | `financial-stress-audit` | `financial_stress_audit` | assessment (reflection) |
| Sleep anxiety | `sleep_anxiety` | `sleep-anxiety-wind-down` | `wind_down_breath` | somatic |
| Somatic healing | `somatic_healing` | `somatic-body-scan` | `body_scan_timer` | somatic |
| Grief | `grief` | `grief-letter-template` | `grief_letter_template` | template |

Site paths live under `/free/<funnel-slug>/` on our Cloudflare Pages domain (brand wizard app). Authority: `config/freebies/ghl_funnel_capture.yaml`.

---

## What to send back to the project owner

Send **only** this (in email or Slack):

```
PHOENIX_GHL_FUNNEL_WEBHOOK=https://services.leadconnectorhq.com/hooks/YOUR-HOOK-ID-HERE
```

Optional: confirm workflow name, location/sub-account name, and that a test contact was created.

**Do not** send API keys in the same message unless we separately asked for Burnout funnel API setup.

---

## What the dev team does after they receive the URL

(You do not do this — for transparency only.)

1. Store the URL in secure credential storage (Keychain + GitHub secret).
2. Inject the URL into all **15 funnel HTML pages** (`data-ghl-webhook` on `<body>`).
3. Run automated smoke tests.
4. Deploy static pages via GitHub → Cloudflare Pages.

Script reference: `scripts/freebies/setup_ghl_webhook.sh` (dev/operator machine).

---

## Troubleshooting (GHL admin)

| Problem | Likely fix |
|---------|------------|
| No contact created | Workflow not **Published**; email mapping missing |
| Contact created, no tags | Add “Add Tag” step; map `tags` from webhook |
| Custom field empty | Field not mapped in webhook trigger; wrong UUID |
| Duplicate contacts | Enable “update existing” / match on email in workflow |
| Webhook receives nothing | URL not yet deployed on site — owner must inject URL first |

---

## Technical references (dev team)

- Payload contract: `config/freebies/quiz_segment_map.yaml`
- Funnel page list: `config/freebies/ghl_funnel_capture.yaml` (`funnel_pages`, 15 entries)
- Pearl_Int runbook: `skills/pearl-int/references/ghl_freebie_inbound_webhook.md`
- Credentials registry: `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` §8b

---

**Document version:** 2026-06-23 · Phoenix Omega / SpiritualTech Systems
