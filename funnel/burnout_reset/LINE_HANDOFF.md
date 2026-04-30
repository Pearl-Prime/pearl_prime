# LINE Official Account handoff — Burnout Reset funnel (Japan)

**Purpose:** Engineering + operator handoff for the Japan-locale freebie funnel running on LINE Official Account (LINE OA), parallel to the GHL email funnel for non-JP markets. App receives LINE webhooks on friend-add (`follow`), tags the contact, schedules step messages, and routes to LIFF / link cards / coupons. No email push.

**Mirrors:** [funnel/burnout_reset/GHL_HANDBOFF.md](GHL_HANDBOFF.md) (the email/GHL parallel).
**Plan:** [docs/JAPAN_LINE_FREEBIE_FUNNEL_PLAN_2026-04-29.md](../../docs/JAPAN_LINE_FREEBIE_FUNNEL_PLAN_2026-04-29.md).
**State machine:** [config/funnel/line_jp/funnel_definition.yaml](../../config/funnel/line_jp/funnel_definition.yaml).
**Brand registry:** [config/funnel/line_jp/oa_brand_registry.yaml](../../config/funnel/line_jp/oa_brand_registry.yaml).
**Messages (JA):** [config/funnel/line_jp/messages.ja_JP.yaml](../../config/funnel/line_jp/messages.ja_JP.yaml).

---

## Setup

### 1. LINE Developers account + provider + channels

- Operator creates a **LINE Developers** account (one company-level account is fine).
- Inside LINE Developers, create a **Provider** (e.g., "Phoenix Omega JP").
- Under that provider, create one **Messaging API channel per brand OA** (primary model: **12 channels at Standard tier**, one per brand; phased per `docs/JAPAN_LINE_FREEBIE_FUNNEL_PLAN_2026-04-29.md` §10 — first 静心社 only at launch, remaining brands rolled out across Month 1–6).
- Fallback model (hybrid 3-hub): 3 channels — `iyashikei`, `cognitive`, `transformation` — only if launch budget cannot support 12 Standard accounts.
- Note: LIFF apps and LINE Login can be added as separate channels under the same provider; they share the user-ID namespace inside that provider, so `userId` is consistent across channels for the same provider.

### 2. Per-brand channel — credentials

For each brand OA channel, copy from LINE Developers Console → Messaging API tab:

| Field | Source | Env var |
|---|---|---|
| Channel ID | Channel basic settings | `LINE_${BRAND}_CHANNEL_ID` |
| Channel secret | Channel basic settings | `LINE_${BRAND}_CHANNEL_SECRET` |
| Channel access token (long-lived) | Issue under Messaging API tab | `LINE_${BRAND}_ACCESS_TOKEN` |
| Webhook URL | Set to `https://<your-app>/webhook/line/${brand_id}` | — |
| Webhook events | Enable: `follow`, `unfollow`, `message`, `postback` | — |
| Auto-reply messages | **Disable** in OA Manager (overrides our webhook copy otherwise) | — |
| Greeting message | **Disable** — our `m1_welcome` step replaces it | — |
| Tier | **Standard** at launch (research-recommended floor; Light tier broadcast cap saturates at ~5k friends) | — |

`${BRAND}` is `STILLNESS_PRESS`, `SOMATIC_WISDOM`, `BODY_MEMORY`, etc. — uppercase brand_id from `config/funnel/line_jp/oa_brand_registry.yaml`.

### 3. LIFF apps — quiz (with email hedge), interactive exercise, book preview

LIFF endpoints can be **shared across all brand OAs** (deployed once per provider; brand context passed as URL parameter). Three endpoints required at launch:

| LIFF endpoint | Path | Used by state | Notes |
|---|---|---|---|
| `liff_quiz` | `/liff/quiz/${brand}/${topic}` | `m1_welcome` | 3-question persona quiz **+ email capture via LINE Login `email` scope** (research §7.10 channel-risk hedge) |
| `liff_exercise2` | `/liff/exercise/${exercise_id}` | `m2_second_exercise` | Interactive somatic / breathwork tool |
| `liff_book_preview` | `/liff/preview/${book_slug}` | `m4_soft_pitch`, `m5_hard_pitch` | Sample chapter + 1-tap purchase routing |

LIFF apps read `userId` of the LINE friend without re-authentication, so persona/topic signals captured in the quiz attach to the correct contact in our DB.

### 4. LINE Login — `email` scope ENABLED at the LIFF quiz step (research §7.10)

LINE Login OAuth is **enabled** at the LIFF quiz endpoint with the `email` scope requested. Rationale: LINE-Yahoo merger and 2026-04 ad-platform integration create concentration risk; capturing email at the quiz step provides a recoverable contact for every friend should LINE access ever be disrupted. Framing for the user is consent-first: "メールアドレスは、LINEがつながらなくなった際の連絡用にだけ使います" (we only use your email to reach you if LINE access is interrupted).

Email-hedge capture target: ≥ 40% of friend-adds (per `JAPAN_LINE_FREEBIE_FUNNEL_PLAN_2026-04-29.md` §8 KPIs).

LINE Login OAuth is **not** required for users who decline the quiz; declining still grants friend-add and the m1 welcome message will fire.

---

## Webhook events — what arrives, what we do

LINE posts JSON to `POST /webhook/line/${hub_id}` for every event. Validate the `x-line-signature` header against `LINE_${HUB}_CHANNEL_SECRET` before trusting payload.

### `follow` — equivalent to GHL "contact created"

**Payload:** `events[].source.userId`, `events[].timestamp`.
**Our actions (atomic, in this order):**

1. Insert / upsert contact row in DB keyed by `(hub_id, line_user_id)`.
2. Resolve entry-point metadata (URL params at QR / ad / `liff.line.me?state=…`) → `brand_id`, `topic`, `utm_*`.
3. Tag contact: `funnel_burnout_reset_jp`, `topic_${topic}`, `hub_${hub_id}`, `brand_${brand_id}` (when known).
4. Send `m1_welcome` reply (immediate; uses brand-variant copy if `full_slot_authoring: true` in registry, else hub default).
5. Schedule `m2`, `m3`, `m4`, `m5`, `m6b_cross_sell` step messages per profile (`line_native_fast` default).
6. Push rich menu `rich_menu_${hub}_v1` to this user (`POST /v2/bot/user/{userId}/richmenu/{richMenuId}`).
7. Emit `lead_created` event to internal CRM bus.

### `unfollow` — equivalent to GHL "unsubscribed"

**Our actions:**

1. Tag contact `blocked`.
2. Cancel scheduled step messages.
3. Emit `lead_blocked` event. Do **not** retry add or send any message — the user owns the relationship, and LINE OA TOS prohibits re-adding without consent.

### `message` (inbound)

**Our actions:**

1. Run keyword auto-reply rules (e.g., 「クーポン」 → push current coupon flex message).
2. If no rule matches and operator-hours window is open → forward to operator inbox; otherwise auto-reply with operator-hours notice.

### `postback` — rich menu / button taps

**Our actions:**

1. Parse `postback.data` (e.g., `rich_menu:today_tip`, `book_intent:${book_slug}`).
2. Tag intent (e.g., `intent_book_interested`).
3. Push the corresponding flex / link-card / LIFF redirect.

---

## What "send a message" means on LINE

Three different APIs, three different pricing/behaviors. Pick deliberately.

| API | Endpoint | Cost | When to use |
|---|---|---|---|
| **Reply API** | `POST /v2/bot/message/reply` | Free (within tier) | Inside ~1 min of an inbound event (the `replyToken`). Use for `m1_welcome` reply to a `follow`. |
| **Push API** | `POST /v2/bot/message/push` | Counted against monthly quota | One-to-one push outside the reply window. Use for scheduled steps `m2`–`m7`. |
| **Multicast / Broadcast** | `POST /v2/bot/message/multicast` (≤500 ids) or `/broadcast` | Counted against quota; broadcast is cheaper per recipient | Audience-wide announcements (new-book launches, seasonal campaigns). Not used by the per-user step-message path. |

**Quota budgeting:** Each brand OA's monthly broadcast quota depends on its tier (Light / Standard). Per-user push messages also consume quota. Track quota burn in the same DB jobstore (mirrors APScheduler pattern from `funnel/burnout_reset/app.py`). When ≥80% quota is consumed, the scheduler must throttle low-priority broadcasts (cross-sell, re-engagement) before high-priority steps (`m1`–`m5`).

**Send-time scheduler:** Timer-fired states (m2 through m7) read `send_window_jst` from `funnel_definition.yaml` and queue dispatch within the window. Default: 20:00–21:30 JST Sun/Tue/Wed/Thu (per research §7.2). High-stakes states (m4, m5) target 20:30 Tue or Wed specifically. The scheduler must convert UTC timestamps to JST and respect the per-state window even if the timer would fire outside it (queue-and-dispatch-at-window pattern).

---

## Contact / event payload — equivalent of GHL Contacts API

**No external CRM in v1** — the funnel app owns the source of truth (SQLite for MVP, Postgres for prod, mirroring the GHL flow's persistence pattern). Schema:

| Table | Columns |
|---|---|
| `line_contacts` | `id`, `hub_id`, `line_user_id` (unique per hub), `display_name`, `language`, `created_at`, `blocked_at`, `brand_id`, `topic`, `utm_source`, `utm_medium`, `utm_campaign`, `quiz_persona` |
| `line_contact_tags` | `contact_id`, `tag` (composite unique on (contact_id, tag)) |
| `line_messages_sent` | `contact_id`, `message_slot`, `sent_at`, `replyToken_or_pushId`, `cost_quota_units` |
| `line_events` | `contact_id`, `event_type`, `payload_json`, `received_at` |
| `line_purchases` | `contact_id`, `book_slug`, `platform` (bookwalker / amazon_jp / line_pay), `purchase_at`, `revenue_jpy` |

The `line_purchases` table is populated either via affiliate-platform postback (BookWalker / Amazon JP affiliate webhooks) or via LINE Pay merchant webhook (when direct sale is enabled in Phase 2).

---

## Recommended tags (mirror GHL tag conventions)

- `funnel_burnout_reset_jp`
- `topic_${topic}` — e.g., `topic_burnout`
- `hub_${hub_id}` — e.g., `hub_iyashikei`
- `brand_${brand_id}` — e.g., `brand_stillness_press`
- `state_${state_id}` — e.g., `state_m4_soft_pitch_sent`
- `intent_${intent}` — e.g., `intent_book_interested`
- `buyer_${book_slug}` after purchase
- `blocked` — terminal
- `inactive_60d` — re-engagement target

---

## API reference (LINE Messaging API)

- **Base:** `https://api.line.me/v2/bot/`
- **Auth header:** `Authorization: Bearer <CHANNEL_ACCESS_TOKEN>`
- **Reply:** `POST /v2/bot/message/reply` body `{replyToken, messages:[…]}`
- **Push:** `POST /v2/bot/message/push` body `{to, messages:[…]}`
- **Multicast:** `POST /v2/bot/message/multicast` body `{to:[…≤500 ids], messages:[…]}`
- **Profile:** `GET /v2/bot/profile/{userId}` (display name, language, statusMessage)
- **Rich menu link:** `POST /v2/bot/user/{userId}/richmenu/{richMenuId}`
- **Rich menu unlink:** `DELETE /v2/bot/user/{userId}/richmenu`
- **Insight (per-message):** `GET /v2/bot/insight/message/event?requestId=…`
- **LINE Pay (Phase 2):** `https://api-pay.line.me/v3/payments/request` (operator must register as a LINE Pay merchant; out of scope for v1)

Reference: [LINE Messaging API docs](https://developers.line.biz/en/reference/messaging-api/).

---

## Who sends messages

Controlled by **send_mode** in `config.yaml` (or env `SEND_MODE`):

- **app:** This app sends `m1`–`m7` via Push API and APScheduler (persistent jobstore in same DB). Use for version-controlled, testable cadence. Default for v1.
- **manual:** App tags contacts and tracks state, but does NOT auto-send. Operator pushes messages manually from OA Manager. Useful for soft-launch before scheduled cadence is verified.

Do **not** go live with `send_mode: app` until:

1. `m1_welcome` is verified arriving within 1 min of friend-add.
2. `m2`–`m5` are verified arriving on schedule for at least 5 test friends.
3. Block-handling is verified (unfollow event cancels remaining steps).
4. Quota burn dashboard is wired and shows correct remaining-quota math.
5. Compliance review (per plan §"Compliance"): 特定商取引法 disclosure visible, privacy policy linked, no medical-claim language in any state.

---

## Coupons — LINE-native

LINE has a built-in coupon primitive (rich message with redemption tracking) — distinct from a generic discount code in message text.

- **Create** in OA Manager → Coupon. Get a coupon URL `https://line.me/R/oaMessage/${hub_oa_id}/?coupon=…`.
- **Reference** by `coupon_id` in `messages.ja_JP.yaml` `hard_pitch_day_14` slot.
- **Redemption tracking:** LINE reports redemption count in OA Manager; pull via Insight API into our DB.
- **One coupon per active campaign per hub** to keep redemption analytics clean. Rotate coupons monthly.

When the freebie funnel routes to off-platform purchase (BookWalker / Amazon JP affiliate), the LINE coupon does NOT apply — that's a platform-specific discount the seller controls. Reserve LINE-native coupons for `Phase 2` direct-sale-via-LINE-Pay.

---

## Compliance checklist (gate before going live)

- [ ] **特定商取引法 disclosure** linked from OA bio + `m4_soft_pitch` and `m5_hard_pitch` (seller name, address, contact).
- [ ] **個人情報保護法 privacy policy** linked from `m1_welcome` and from the LIFF quiz consent screen.
- [ ] **No medical claims** in any message slot (see `funnel_definition.yaml` `compliance.medical_claim_blocklist`).
- [ ] **特定電子メール法 inapplicable** — confirmed (LINE OA messages are not email under the act). Block / unfollow is the user's opt-out mechanism per LINE OA TOS.
- [ ] **Age gate** is required only if a freebie includes content not appropriate for under-18; default off.
- [ ] **LINE OA TOS prohibited categories** screened — wellness register (`整える` / `ととのう` / `やわらげる`) is permitted; medical / treatment register is not.

See plan §"Compliance" + research §5 for full citations.

---

## Differences vs GHL email funnel (operator must understand)

| Aspect | GHL email | LINE OA |
|---|---|---|
| Capture form | name + email + exercise | friend-add (only userId + display name) |
| Open rate | ~15–22% (JP email benchmarks) | ~60–80% same-day reads (LINE benchmarks) |
| CTR | ~2–5% | ~10–25% (link cards) |
| Opt-out | unsubscribe link required | block / unfollow (user-side, one-tap) |
| Cadence | ~14 days E1→E5 | 7–14 days m1→m5 (LINE-native fast); 14–21 days (slow profile) |
| Reach surface | inbox (passive) | message thread + rich menu (active surface) |
| Quota | unlimited (within deliverability) | per-OA monthly cap by tier |
| Personalization | merge fields | merge fields + LIFF quiz signal + postback intent |
| Compliance | CAN-SPAM / GDPR / 特定電子メール法 | LINE OA TOS + 特定商取引法 + 個人情報保護法 |

This funnel runs **in parallel** with the GHL email funnel — non-JP markets stay on GHL. Do not migrate non-JP traffic to LINE; LINE penetration outside JP/TW/TH is too low to justify the channel split.
