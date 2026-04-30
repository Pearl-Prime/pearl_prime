# Japan LINE Freebie Funnel Plan

**Generated:** 2026-04-29
**Authority:** Pearl_Marketing + Pearl_Research + Pearl_Int (multi-agent)
**Locale:** ja_JP only (TW / KR are separate planning streams)
**Scope:** Plan + funnel definition + native Japanese microcopy. **No** OA / Ads / Pay account creation, no asset generation, no LLM calls.
**Mirrors structurally:** [docs/FREEBIE_MARKETING_PLAN.md](FREEBIE_MARKETING_PLAN.md) + [funnel/burnout_reset/GHL_HANDBOFF.md](../funnel/burnout_reset/GHL_HANDBOFF.md).
**Companion docs:** [funnel/burnout_reset/LINE_HANDOFF.md](../funnel/burnout_reset/LINE_HANDOFF.md), [config/funnel/line_jp/funnel_definition.yaml](../config/funnel/line_jp/funnel_definition.yaml), [config/funnel/line_jp/oa_brand_registry.yaml](../config/funnel/line_jp/oa_brand_registry.yaml), [config/funnel/line_jp/messages.ja_JP.yaml](../config/funnel/line_jp/messages.ja_JP.yaml), [config/funnel/line_jp/rich_menu.ja_JP.yaml](../config/funnel/line_jp/rich_menu.ja_JP.yaml).
**Research grounding:** [artifacts/research/japan_line_freebie_funnel_market_research_2026-04-29.md](../artifacts/research/japan_line_freebie_funnel_market_research_2026-04-29.md), [artifacts/research/japan_line_competitive_funnel_audit_2026-04-29.md](../artifacts/research/japan_line_competitive_funnel_audit_2026-04-29.md).

---

## 0. Executive summary

The operator runs a US-style email-funnel via GoHighLevel (5-email Proof Loop, Exercise → Exercise → Story → Book → More books). For the Japan market, an email-led funnel is structurally wrong: LINE messaging penetration in Japan is near-universal in the wellness reader cohort and outperforms email by ~3–4× on read rates and ~3–5× on click-through. The GHL Proof Loop **psychology** transfers cleanly to LINE; the **plumbing** must be rebuilt on LINE-native primitives.

This plan ships a Japan-LINE freebie funnel that:

1. **Mirrors the GHL Proof Loop psychology 1:1** — same lifecycle (Awareness → Landing → Capture → Nurture → Upsell → Re-engage), same proof-loop mechanic (two micro-reliefs before any offer, min 48h gap from story to offer).
2. **Replaces email-funnel primitives with LINE-native ones** — friend-add as capture, step messages as drip, rich menu as persistent surface, LIFF as interactive freebie carrier, link cards / coupons / LINE Pay as monetization rails.
3. **Compresses cadence** — LINE consumption is faster than email (same-day reads dominant); fast cadence runs Day 0 / 1 / 3 / 7 / 14 / 21 / 60 (vs GHL's ~14-day E1→E5). A `email_equivalent_slow` cadence is also defined for direct A/B comparison.
4. **Runs 12 separate per-brand LINE Official Accounts** at Standard tier (~¥180k/mo combined floor) — Pearl_Research-recommended after weighing brand integrity, narrower friend-add CPA, friend-list throttling hedge, and rich-menu real estate against cost. A hybrid 3-hub fallback model (~¥45k/mo) is documented in [config/funnel/line_jp/oa_brand_registry.yaml](../config/funnel/line_jp/oa_brand_registry.yaml) for degraded-launch use only.
5. **Routes purchase via affiliate by default** — BookWalker (manga-led brands), Amazon JP Kindle (prose-led brands) — with LINE Pay direct-sale gated to Phase 2 (highest-volume hub only, after operational learning).
6. **Soft-launches with 静心社 (stillness_press)** — lowest-risk content register, most proven catalog, simplest hub assignment.

The deliverable is **plan + config**, not infrastructure. Operator action is required to provision LINE OA channels, Ads access, Pay merchant, and the engineering bus that converts LINE webhooks → CRM events.

---

## 1. Funnel ladder (mirrors GHL stages)

```
Awareness   →   Landing   →   Capture   →   Nurture (m1–m4)   →   Hard pitch (m5)   →   Post-purchase / Cross-sell (m6, m6b)   →   Re-engage (m7)
   ↑                                                                                                                                  ↓
   └──────────────────────────────  Re-acquire if blocked (cannot re-add without consent — per LINE OA TOS)  ──────────────────────────┘
```

| Stage | GHL primitive | LINE primitive | What it does |
|---|---|---|---|
| Awareness | Book CTA, social, paid → hub URL | LINE Ads (Talk Head View / Smart Channel / LAP click-to-message), VOOM organic, in-book QR, X/TikTok JP cross-promo | Reader sees the brand and clicks toward an OA add-friend or a LIFF landing |
| Landing | 6-section page with form (name, email, exercise) | OA profile page **or** LIFF landing page (with optional pre-add quiz) | Reader gets a one-screen explanation of the freebie and the brand voice before adding |
| Capture | Form submit → contact pushed to GHL Contacts API | `follow` webhook → contact upserted in funnel DB; tags applied | Lead created |
| Nurture | E1–E3 (Exercise / Exercise / Story) | m1–m3 step messages | Two micro-reliefs + a story — Proof Loop intact |
| Hard pitch | E4 book offer | m4 soft pitch (Day 7) → m5 hard pitch + LINE coupon (Day 14) | Two-step pitch instead of one — LINE's faster cadence makes this not feel rushed |
| Post-purchase / cross-sell | E5 more books | m6 thanks → m6b cross-sell carousel | Recommend 2–3 related books from same brand or hub |
| Re-engage | GHL workflow — 30-day re-engagement | m7 at Day 60 with new micro-exercise + seasonal hook | Recover inactive friends before they block |

### Deviations from GHL — documented

The brief mandates structural alignment to GHL with deviations called out. Here they are, with rationale.

**D1. No "form submit" — friend-add is the capture event.**
GHL captures `(name, email, exercise_choice)` via a web form. LINE friend-add only delivers `userId` + display name. We collect richer signals via two LINE-native paths instead:
- **Pre-add LIFF quiz** (optional) — a 3-question quiz on a LIFF page **before** add-friend, which can be shared as a `liff.line.me/...` URL via ad / VOOM / website. The quiz output shapes the brand assignment (which hub OA to suggest) and tags the contact at first message.
- **Post-add postback signals** — first rich-menu tap, first message keyword, first link-card click — feed `topic` / `brand` / `intent` tags within the first 24h.

**D2. Cadence compression — front-end telescopes.**
Email Proof Loop runs ~14 days; LINE consumption is faster. LINE's same-day read rate (~60–80%, [research §2]) means the psychological space between messages can be tighter without feeling rushed. Pearl_Research §7.1 specifically recommends collapsing M1+M2 to **immediate + 12h** (not +24h) because LINE open-rate half-life is hours, not days. Default `line_native_fast` profile: 0h / +12h / Day 3 / Day 7 / Day 14 / Day 21 / Day 60. The 48h-min-gap-from-story-to-offer rule is preserved (m3 story → m4 soft pitch = 96h gap). A `email_equivalent_slow` profile is defined for A/B testing (Day 0 / 1 / 4 / 11 / 21 / 28 / 60).

**D3. Rich menu replaces persistent CTA.**
Email has no persistent surface; once read, an email is gone. LINE's rich menu is a 6-cell always-visible bottom dock. This is a strict gain — the brand keeps a "shelf" the reader can return to. Cells are stage-aware (a buyer's rich menu surfaces 購入履歴 instead of おすすめ本; an inactive-friend's surfaces 復帰特典).

**D4. LIFF mini-app raises the ceiling on "second exercise."**
GHL email E2 ships a static link to a web-based exercise. LIFF lets m2's exercise be **interactive inside the chat** (timer, breathwork visualizer, body-scan walkthrough). This is the largest qualitative upgrade vs the GHL flow — a LINE-native capability that has no email equivalent.

**D5. Block / unfollow replaces unsubscribe.**
GHL email requires an unsubscribe link in every message (CAN-SPAM, GDPR, 特定電子メール法). LINE has no equivalent in-message requirement — the reader blocks or unfollows the OA in one tap from the chat surface. Compliance treats LINE OA messaging under the LINE OA TOS and 個人情報保護法 (not 特定電子メール法; see research §5). One downstream consequence: re-acquisition of a blocked user requires fresh consent — we cannot back-fill them via another channel.

**D6. Quota is finite per OA.**
GHL email is unlimited within deliverability constraints. LINE OA imposes a hard monthly broadcast quota by tier (Free / Light / Standard). This is a major operational constraint and forces explicit quota budgeting in the engineering layer ([funnel/burnout_reset/LINE_HANDOFF.md](../funnel/burnout_reset/LINE_HANDOFF.md) §"What 'send a message' means on LINE"). Standard tier is the per-OA floor at launch (research §1).

**D7. Hedge — capture email via LIFF + LINE Login `email` scope.**
LINE-Yahoo merger (2024), 2026-04 ad-platform integration, and 2026-10 pricing reform create concentration risk if the operator becomes 100% LINE-dependent. Pearl_Research §7.10 recommends running the email Proof Loop in parallel for ≥12 months and capturing email at the LIFF quiz step via LINE Login `email` scope so every LINE friend is also a recoverable email contact. Framing: **LINE-primary, email-archive** — not LINE-only.

---

## 2. State machine

The full state machine is defined in [config/funnel/line_jp/funnel_definition.yaml](../config/funnel/line_jp/funnel_definition.yaml). Summary:

| State | Fires on | Cadence (fast — research-recommended) | Cadence (slow — GHL-equivalent) | Proof Loop role |
|---|---|---|---|---|
| `m1_welcome` | `follow` event | +0h | +0h | Exercise 1 |
| `m2_second_exercise` | timer | **+12h** (research §7.1) | +24h | Exercise 2 (different mechanism) |
| `m3_story` | timer | +72h (Day 3) | +96h (Day 4) | Story |
| `m4_soft_pitch` | timer | +168h (Day 7) | +264h (Day 11) | Soft pitch (book intro, no coupon) |
| `m5_hard_pitch` | timer | +336h (Day 14) | +504h (Day 21) | Hard pitch + LINE coupon |
| `m6_post_purchase_thanks` | `purchase_confirmed` | event-driven | event-driven | Buyer thanks |
| `m6b_cross_sell` | timer | +504h (Day 21) | +672h (Day 28) | More books |
| `m7_re_engage` | timer (no purchase) | +1440h (Day 60) | +1440h (Day 60) | Re-engagement |
| `blocked` | `unfollow` event | terminal | terminal | — |
| `purchased` | `purchase_confirmed` | terminal | terminal | — |

All Proof-Loop ordering rules are honored:
- Two micro-reliefs (m1, m2) before any offer.
- Story (m3) before any pitch.
- Min 48h gap from story to offer (fast: 96h; slow: 168h).

**Send-time windows (JST):** Per research §7.2, schedule timer-fired states for **20:00–21:30 JST on Sun / Tue / Wed / Thu**. Avoid Friday evenings (oversaturated commercial messaging) and Saturday mornings (low engagement on lifestyle content). High-stakes states (m4 soft pitch, m5 hard pitch) should target **20:30 Tue or Wed** specifically. The scheduler's job dispatcher reads `send_window_jst` from each state in [config/funnel/line_jp/funnel_definition.yaml](../config/funnel/line_jp/funnel_definition.yaml).

---

## 3. Freebie format — top 3 ranked

After review of the operator's existing freebie types ([specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md](../specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md) §4) and LINE-native delivery surfaces ([research §1, §3]), three freebie formats are recommended for the Japan funnel. Ranked by **predicted CVR × engineering cost**.

### Format A (default v1) — **7-Day LINE Drip Mini-Course**

A 7-day daily-arrival mini-course delivered entirely as LINE messages. Each day is a 2–3 minute read, with one audio clip on Day 4 (anchored to the operator's existing `mini_audio` and `guided_audio` registry types). No off-platform navigation required.

**Why predicted highest CVR:**
- LINE's primary use pattern is daily messaging; this format **matches reader habit perfectly**.
- The format **is** the funnel — m1 through m4 simultaneously deliver the freebie and the Proof Loop.
- Zero tooling cost: pure LINE step messages + one audio asset (already produced for some brands per `audio_scripts.yaml`).
- Same content shape works across all 3 hubs with different voice tints (`messages.ja_JP.yaml` already supports per-hub variants).

**Engineering cost:** Lowest. Reuses LINE step messaging + existing audio assets.

**Best for:** All 12 brands. Ship as v1 default.

### Format B (Phase 1.5) — **LIFF Quiz → Personalized PDF**

A 3-question LIFF quiz captured **before** friend-add or in `m1_welcome`. The quiz output maps the user to a (topic × persona × hub) cell, generates a tailored PDF freebie referencing the operator's existing `companion_workbook_pdf` template, and tags the contact for downstream personalization.

**Why predicted strong CVR:**
- The quiz **captures persona signal** that no other freebie format does — drives smarter Day-7 book recommendation and Day-14 coupon allocation.
- Personalization signal compounds: by Day 60 the funnel has 3+ tags per contact, enabling sharper re-engagement copy.
- LIFF apps inherit LINE auth, so no friction.

**Engineering cost:** Medium. Requires LIFF page + a `quiz_to_pdf` generator service that calls the existing freebie pipeline (`scripts/create_freebie_assets.py` already produces tailored PDFs from `(topic, persona)` keys; the LIFF quiz output maps directly to those keys).

**Best for:** Hub 2 (cognitive) — knowledge-worker reader expects more interactivity. Phase 1.5 rollout (after Format A is proven, ~Week 6–8).

### Format C (Phase 2 for manga brands) — **Sample Manga Chapter as Rich Message**

For manga-led brands (`stillness_press`, `cognitive_clarity`, `body_memory`, `digital_ground`, per [docs/CJK_CATALOG_PLAN.md](CJK_CATALOG_PLAN.md) §4–5), the freebie is a sample chapter delivered as a LINE rich message (image carousel) with a continuation link card to BookWalker / LINE Manga.

**Why predicted high CVR for manga-led brands:**
- The freebie **is** the product, in a smaller dose. No translation between freebie and book.
- Routes via affiliate (BookWalker = ~5–10% commission, [research §4]); zero merchant overhead.
- LINE Manga adjacency: readers in the LINE app are one tap from the LINE Manga app.

**Engineering cost:** Low (manga assets already exist for several brands per `docs/MANGA_GTM_PLAN.md` Q2 2026 milestone). Main work is the LINE rich-message authoring + affiliate-link templating.

**Best for:** Manga-led brands only. Phase 2 rollout when first manga catalog ships (Q2 2026 per MANGA_GTM_PLAN).

### Why **NOT** other formats (rejected with rationale)

- **Direct PDF download via LINE Notify** — LINE Notify is being deprecated through 2025; do not build new flows on it.
- **Video-as-freebie** — JP wellness reader prefers text + audio over video on smartphone for daily-cadence content; video has higher CPA and lower completion. Reserve for awareness/ads, not freebie.
- **Webinar / live event opt-in** — high friction, doesn't match the Proof Loop psychology; reserve for Phase 3.

---

## 4. Message cadence — full schedule

Two profiles, both honoring the Proof Loop psychology.

### `line_native_fast` (default — recommended for Format A and B)

| Day / hour | Slot | Content | Send window (JST) |
|---|---|---|---|
| 0h | `m1_welcome` (immediate) | Greeting + first micro-exercise (somatic, ~2 min). Brand-voice anchor. Sticker. | event-driven |
| +12h | `m2_second_exercise` | Second micro-exercise on a different mechanism. Optional 60-sec audio. | 20:00–21:30 |
| +72h (Day 3) | `m3_story` | Transformation story from a representative reader. No offer. | 20:00–21:30 Tue/Wed/Thu |
| +168h (Day 7) | `m4_soft_pitch` | Gentle book introduction. Link card (no coupon, no urgency). | **20:30 Tue or Wed** |
| +336h (Day 14) | `m5_hard_pitch` | Explicit purchase invitation + LINE-native coupon. | **20:30 Tue or Wed** |
| +504h (Day 21) | `m6b_cross_sell` | (If purchased) Carousel of 2–3 related books from same brand. | 20:00–21:30 |
| +1440h (Day 60) | `m7_re_engage` | (If no purchase + no block) Soft re-engagement: new micro-exercise + seasonal hook. | 20:00–21:30 Sun |
| event | `m6_post_purchase_thanks` | (On purchase confirmation) Thank-you + review request. Tag as buyer. | event-driven |

### `email_equivalent_slow` (for direct comparison vs GHL email)

| Day | Slot | Notes |
|---|---|---|
| 0 | `m1_welcome` | Same as fast |
| 1 | `m2_second_exercise` | Same as fast |
| 4 | `m3_story` | +24h vs fast — matches GHL E3 timing |
| 11 | `m4_soft_pitch` | +96h after story — matches GHL E4 |
| 21 | `m5_hard_pitch` | Stretched to weekly cadence |
| 28 | `m6b_cross_sell` | Matches GHL E5 +168h |
| 60 | `m7_re_engage` | Same |

The operator can run both profiles in parallel (different brands, or A/B split within one brand) to measure whether LINE-fast actually outperforms email-pace on first-purchase CVR. Hypothesis: fast wins by 1.5–2.5× on first-purchase CVR within 30 days, but slow wins on `m7` re-engagement rate (less message-fatigue). Confirm in Week 6–8 readout.

---

## 5. Soft pitch → paid book mechanic

Three monetization options are modeled. **Recommendations differ by brand archetype.**

### Option (a) — Affiliate to BookWalker / Amazon JP

**Mechanic:** LINE link card → external store. Operator earns affiliate commission (BookWalker ~5–10% [research §4]; Amazon JP ~3–8% [research §4]).

**Pros:**
- Zero merchant overhead.
- Inherits the platform's purchase trust (Amazon JP especially).
- Settles in JPY automatically.
- Lowest engineering cost.

**Cons:**
- Lowest revenue per sale (commission only).
- Reader leaves the LINE chat — measurement requires affiliate postback.
- No upsell control (the platform owns the next-step UX).

**Recommended for:** Default for v1, all brands. Specifically:
- **Manga-led brands** (`stillness_press`, `cognitive_clarity`, `body_memory`, `digital_ground`) → BookWalker primary, Amazon JP secondary. BookWalker has stronger manga-affinity audience.
- **Prose-led brands** (`somatic_wisdom`, `qi_foundation`, `sleep_restoration`, `relational_calm`, `heart_balance`, `warrior_calm`, `solar_return`, `devotion_path`) → Amazon JP Kindle primary, Rakuten Kobo secondary.

### Option (b) — Direct LINE Pay sale + EPUB delivery via LIFF

**Mechanic:** LINE Pay merchant (operator-side setup) accepts payment inside LINE; on confirmation, a LIFF page delivers the EPUB.

**Pros:**
- Highest margin (no platform commission, only LINE Pay's transaction fee — ~3.45% per [research §1]).
- Reader stays in the LINE chat — measurement and upsell are operator-controlled.
- Direct buyer relationship.

**Cons:**
- LINE Pay merchant onboarding is non-trivial (operator KYC, business verification, settlement bank).
- EPUB delivery via LIFF is operator-built — not a turn-key surface.
- Compliance: 特定商取引法 disclosures are operator's responsibility.

**Recommended for:** **Phase 2 only**, gated to the highest-volume hub (likely iyashikei). Pilot with 1–2 books to validate operational mechanics before broadening.

### Option (c) — Konbini ISBN + physical book hybrid

**Mechanic:** LINE link card → operator's own landing page → ISBN / 7-Eleven konbini payment → physical book mailed.

**Pros:**
- Captures the older self-help reader cohort that prefers print.
- Konbini payment has near-100% trust in JP.

**Cons:**
- Complex fulfillment (physical inventory, shipping).
- Slow cycle (Day 0 friend-add → Day ~21 book in hand) → high abandonment.
- Long tail; small ARPAF impact.

**Recommended for:** Niche pilot only — best fit for `qi_foundation` and `warrior_calm` (older-skewing readers per CJK_CATALOG_PLAN.md tier mapping). Defer to Phase 3.

### Per-hub primary recommendation

| Hub | Primary route | Fallback | Rationale |
|---|---|---|---|
| iyashikei | Amazon JP Kindle (prose) + BookWalker (manga) | Apple Books JP | Largest reader cohort; multi-platform reduces single-platform risk |
| cognitive | Amazon JP Kindle | BookWalker | Knowledge-worker reader skews Amazon |
| transformation | Amazon JP Kindle | Rakuten Kobo | Devotion register has strong Rakuten overlap |

Phase 2 LINE Pay direct-sale: pilot with iyashikei hub (highest projected volume) only. All other brands stay on affiliate routing through Phase 2.

---

## 6. Multi-brand orchestration — 12 separate per-brand OAs (research-recommended)

12 ja_JP brands. Three orchestration models were considered. Pearl_Research §7.5 recommends **12 separate Standard-tier OAs**, one per brand. The recommendation flipped from an earlier hybrid 3-hub working hypothesis after research weighed brand integrity, friend-add CPA, throttling hedge, and rich-menu real estate against cost.

### Models compared

| Model | Setup | Pros | Cons |
|---|---|---|---|
| **Per-brand 12 OAs** (recommended) | One OA per brand at Standard tier | Brand voice integrity (each OA = one promise); narrower brand-promise → lower friend-add CPA; 12 separate friend lists hedge against throttle / policy review on any single OA; full rich-menu real estate per brand | ¥180k/mo combined floor; 12× admin overhead; 12× sticker sets at launch (¥76,800 one-time) |
| **Hybrid 3 hubs** (fallback) | iyashikei / cognitive / transformation hub OAs | ~75% cost saving vs primary; hub-level admin only | Brand voice diluted (reader sees one persona, not the brand); rich-menu shared across 4–5 brands; cross-brand intent-segmentation harder |
| **Single OA** | All 12 brands in 1 OA + a 14-cell rich-menu (research-discussed plan B for hybrid) | Cheapest; pooled friend list; rich-menu has 20-area cap, so 12-brand cells fit | Brand voice fully collapses; reader taps a brand cell expecting brand voice and gets a hub voice — fatal for the operator's brand-portfolio system. **Rejected.** |

### Why per-brand 12 OAs wins (research §7.5)

1. **Brand promise narrowness lowers CPA.** When 鉄門社 (warrior_calm — courage / discipline) targets a separate ad audience from 羽と秤社 (heart_balance — balance / lightness), each ad delivers a more specific promise to a more specific reader. A hub mixing both promises ("we offer a bit of both") underperforms on intent-match.
2. **Rich-menu space.** A per-brand OA has 6–8 cells of brand-specific tooling (今日のヒント, 無料ガイド, おすすめ本, 著者について, etc.). A hub OA must compress brand-specific tooling into shared cells or burn cells on brand-switching.
3. **Friend-list throttle hedge.** If LINE flags one OA for review (false-positive medical-claim filter, ad-platform pause, sticker compliance), 11 other OAs continue running. Hub model concentrates risk.
4. **Reader brand-trust.** Japanese wellness readers expect a publisher brand to speak with one voice. A hub OA that switches voice between messages ("today this is 静心社 speaking; tomorrow this is 体記堂 speaking") feels structurally wrong.

### What's preserved when running 12 OAs

- **Shared content pipeline** — same `messages.ja_JP.yaml` slot vocabulary; per-brand variants are authored once and apply across the brand's full step-message sequence.
- **Shared CRM event bus** — all 12 OAs feed `lead_created` / `purchase_confirmed` / `unsubscribed` to the same internal event bus tagged with `brand_id`.
- **Shared compliance gates** — one medical-claim blocklist applies to all 12 OAs; one 特定商取引法 disclosure published per legal entity covers all (operator runs all 12 brands under one legal entity).

### Cost math (research §1 sourcing)

| Model | Monthly recurring | Sticker sets (one-time) | Status |
|---|---|---|---|
| **12 OAs × Standard** | **¥180,000** | **¥76,800** (12 × ¥6,400) | **Recommended primary** (research §7.5) |
| 12 OAs × Light | ¥60,000 | ¥76,800 | Inadequate — Light's broadcast cap (~15k/mo) hits at ~5k friends |
| 3 hub OAs × Standard | ¥45,000 | ¥19,200 | Documented fallback (75% cost saving; brand-voice loss) |
| 3 hub OAs × Light | ¥15,000 | ¥19,200 | Inadequate at scale |
| 1 OA × Standard | ¥15,000 | ¥6,400 | Rejected — brand voice collapses |

The fallback model is operationally functional and is documented in [config/funnel/line_jp/oa_brand_registry.yaml](../config/funnel/line_jp/oa_brand_registry.yaml) (`fallback_orchestration_model: hybrid_3_hubs`). Use only if launch funding cannot support 12 Standard accounts; migrate to primary when funding allows.

### Brand → OA mapping

All 12 brands run as their own OA. The `fallback_hub` field in `oa_brand_registry.yaml::brands[]` shows which hub each brand falls into if the operator runs in fallback mode:

| Brand | Fallback hub | Tier priority |
|---|---|---|
| 静心社 (stillness_press) | iyashikei | Tier 1 flagship |
| 体知社 (somatic_wisdom) | iyashikei | Tier 1 flagship |
| 体記堂 (body_memory) | iyashikei | Tier 1 flagship |
| 夜の設計社 (sleep_restoration) | iyashikei | Tier 1 flagship |
| 素形堂 (relational_calm) | iyashikei | Tier 2 core |
| 直見堂 (cognitive_clarity) | cognitive | Tier 1 flagship |
| 今此処社 (digital_ground) | cognitive | Tier 1 flagship |
| 羽と秤社 (heart_balance) | cognitive | Tier 2 core |
| 氣根社 (qi_foundation) | cognitive | Tier 2 core |
| 鉄門社 (warrior_calm) | transformation | Tier 3 niche |
| 燼と灰社 (solar_return) | transformation | Tier 3 niche |
| 開器社 (devotion_path) | transformation | Tier 3 niche |

### Phased provisioning (from §10 test plan)

- **Week 1 launch:** 1 OA — 静心社 (Tier 1 flagship, lowest content risk, most proven catalog).
- **Week 7 expansion:** +1 OA — 体記堂 (second iyashikei brand for variant copy validation).
- **Month 3:** all 4 Tier 1 flagships live (静心社, 体知社, 体記堂, 直見堂, 今此処社).
- **Month 6:** all 12 OAs live.

This phased approach defers full ¥180k/mo cost until Tier 1 brands are proven; first 3 months only carry ~¥30–60k/mo recurring.

### Cross-brand handoff

A reader on 静心社 may show 直見堂 interest (e.g., bought a sleep_restoration book and now keyword-searches for "overthinking"). Cross-brand handoff is **soft consent**:

- `m6b_cross_sell` can include a single rich message suggesting another brand's add-friend QR.
- The reader chooses to add the second OA or not.
- We do **not** force-add or auto-share `userId` between OAs (LINE OA TOS prohibits cross-channel `userId` sharing without consent for marketing purposes).

---

## 7. Acquisition channels

### Sequencing rule (research §7.4) — owned channels first, paid second

Per Pearl_Research §7.4, **paid friend-add buys (LAP) should not turn on until each brand OA has a 3,000–5,000-friend organic baseline**. Reasons: paid CPA is volatile early; organic friends self-select for higher intent; the funnel's per-brand CVR benchmarks need an unfiltered baseline before paid traffic is layered on.

Friend-add CPA target: **¥300 CPF** (cost per friend) once paid is enabled — but only against an ad creative tuned to the brand's specific promise (no generic "wellness" creative).

### Owned (Phase 1 — primary acquisition)

| Channel | Surface | Notes |
|---|---|---|
| **In-book QR** | Existing back-matter CTA insertion ([specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md](../specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md) §10.5) | Replace `/free/{slug}` URL with `liff.line.me/...` for ja_JP editions |
| **GHL email list → LINE friend-add invite** | Where the operator has consent + JP locale, one-time email with the OA add-friend QR | Compliance: re-consent at email level; do NOT auto-import to LINE. Tag GHL contact `consent_line_invitation_sent`. |
| **Brand website pop-ups** | If operator runs brand-specific landing pages, surface QR / `liff.line.me/...` add-friend link | High-intent surface; opt-in only, no auto-popup |
| **LINE VOOM (organic)** | Timeline-style surface inside LINE | Per research §7.9: post 3–5/week per brand — manga panels, breath-work loops, book teaser cards. VOOM-search integration (Yahoo, Google) gives organic SEO surface. Cheapest content surface. |
| **Cross-platform organic** | Brand X / Threads / Instagram cross-promo | Existing brand audiences; route to OA add-friend QR |

### Paid (Phase 1.5 — only after 3,000-friend organic baseline per brand)

| Channel | Surface | When to use |
|---|---|---|
| **LAP click-to-message** | Ad click opens OA chat with pre-filled message | Highest-intent paid variant; primary friend-add CPA driver |
| **LINE Smart Channel** | Chat list inline — high visibility | Always-on at modest budget after baseline established |
| **LINE Talk Head View** | Top banner of chat tab — premium awareness | Reserve for major book launches; high CPM |
| **LINE Ads Platform (LAP)** | Cross-network targeted | Topic-targeted always-on at brand-fit creative |
| **App-promotion ads** | Drive LINE Manga app installs (manga-led brands) | Phase 2; only when manga catalog ships |

### Phase 2 — manga app cross-promo

Manga-led brands (per [docs/CJK_CATALOG_PLAN.md](CJK_CATALOG_PLAN.md) §4–5) have a `manga_partnership` business track in `config/catalog/market_catalog_registry.yaml`. This unlocks LINE Manga app cross-promo, doujin partnerships, and BOOTH/PM placement. Acquisition through these channels is paid + relationship-driven, not impressions-driven; out of scope for the v1 funnel plan.

### Referral

| Channel | Mechanic | Notes |
|---|---|---|
| **Existing-buyer referral** | `m6_post_purchase_thanks` includes a "share with a friend" QR | Soft mechanic; no incentive in v1 to avoid spam-flag risk |
| **Cross-brand handoff** | `m6b_cross_sell` recommends a sister brand's OA | See §6 cross-brand handoff |

---

## 8. KPIs + targets

KPI numbers are grounded in [research §2 benchmarks](../artifacts/research/japan_line_freebie_funnel_market_research_2026-04-29.md). Targets below are conservative starting points; revise after first 8 weeks of data.

### Acquisition

| Metric | Tier 1 brands target | Tier 2/3 brands target | Source |
|---|---|---|---|
| Friend-add CPA (LAP click-to-message) | **¥300 (research §2 anchor)** | ¥400–700 | research §2 (¥300 wellness analog; CPF for "self-help / digital book reader" segment marked `[unverified]` in research) |
| Friend-add CPA (Talk Head View) | ¥600–1,200 | ¥1,000–2,000 | research §2 |
| Friend-add CPA (organic / VOOM / in-book QR / email-list cross-promo) | ¥0 effective; **3,000–5,000-friend organic baseline required before paid is enabled** | same | research §7.4 |
| Friends per brand at end of Month 3 | ≥ 3,000 (Tier 1 brands only — phased provisioning) | n/a | research §7.4 |

### Funnel

| Metric | Target | Source / rationale |
|---|---|---|
| `m1_welcome` read rate within 1h | ≥ 70% | LINE same-day read benchmarks ~60–80% [research §2] |
| `m2_second_exercise` read rate | ≥ 60% | Decay across drip — typical ~10pt drop per message |
| `m3_story` read rate | ≥ 50% | — |
| `m4_soft_pitch` link-card CTR | ≥ 8% | LINE link-card CTR benchmarks ~10–25% [research §2]; conservative |
| `m5_hard_pitch` coupon redemption | ≥ 4% | — |
| Drip → first purchase CVR (60-day) | ≥ 3% (Tier 1); ≥ 1.5% (Tier 2/3) | — |
| Block / unfollow rate by Day 14 | ≤ 8% | Healthy LINE OA range [research §2] |

### Revenue

| Metric | Target | Notes |
|---|---|---|
| ARPAF (avg revenue per added friend, 60-day) | ≥ ¥250 (Tier 1); ≥ ¥120 (Tier 2/3) | At ~3% × ¥1,200 avg book + cross-sell |
| LTV at Day 365 | ≥ ¥800 (Tier 1) | Includes cross-sell + repeat purchase |
| Payback on friend-add CPA | ≤ 90 days | First purchase covers acquisition |

### Operations

| Metric | Target |
|---|---|
| Quota burn (% of monthly per OA) | ≤ 70% by Day 21 of month |
| Step-message delivery success rate | ≥ 98% |
| Compliance-flagged-message rate (medical-claim filter hits) | 0 (zero tolerance — block deploy) |
| Email-hedge capture rate (LIFF + LINE Login `email` scope) | ≥ 40% of friend-adds | research §7.10 |

---

## 9. Migration / parallel-run with GHL email

The Japan-LINE funnel runs **in parallel** with the GHL email funnel for non-JP markets. Migration is **not** the goal; **coexistence** is.

### Where they share data

- **Shared CRM event bus** — `lead_created`, `purchase_confirmed`, `unsubscribed` events flow into a single internal CRM regardless of channel. Source = LINE webhook OR GHL contact-created webhook. Tag includes `channel: line` or `channel: email`.
- **Shared catalog / freebie pipeline** — `scripts/create_freebie_assets.py` produces freebie PDFs / audio that feed both funnels via `(topic, persona)` keying.
- **Shared analytics dashboard** — friend-add CPA (LINE) and email-list-add CPA (GHL) sit on the same chart for comparison.

### Where they're independent

- **Sender reputation** — LINE OAs and GHL email domains have separate sender reputations; no cross-channel deliverability impact.
- **Content cadence** — different cadences are intended; LINE-fast vs email-Proof-Loop.
- **Compliance regimes** — LINE OA TOS + 特定商取引法 + 個人情報保護法 (LINE) vs CAN-SPAM / GDPR / 特定電子メール法 (email).
- **Coupon mechanics** — LINE-native coupons (LINE Pay-redeemable) do not transfer to email recipients; operator must run separate promotions per channel.

### What about JP readers already on the GHL email list?

If the operator has explicit prior consent for marketing communication AND the user's locale is JP, run a **one-time consent migration**:

1. Send an email to the JP segment of the GHL list explaining the new LINE OA option.
2. Include the OA add-friend QR + link.
3. **Do not auto-import** to LINE. Reader chooses.
4. Tag the GHL contact `consent_line_invitation_sent` to avoid re-spamming.

---

## 10. Test plan — first 8 weeks

Soft-launch with **静心社 (stillness_press)** as a single-OA pilot — Tier 1 flagship, lowest content risk, most proven catalog. **Organic acquisition only for the first 3 weeks** (per research §7.4). Paid friend-add (LAP) does not turn on until Week 4 at earliest, and only against a 3,000-friend organic baseline if reachable in the test window — otherwise paid is deferred.

### Week 1 — provisioning

- [ ] Operator creates LINE Developers provider + 静心社 OA channel (Standard tier).
- [ ] Operator orders ¥6,400 sticker set for 静心社 (4–6 stickers, contemplative-Buddhist tone).
- [ ] Engineering: deploy webhook receiver `/webhook/line/stillness_press`.
- [ ] Engineering: wire APScheduler to push `m2`–`m5` per fast cadence + send-time windows (20:00–21:30 JST Sun/Tue/Wed/Thu).
- [ ] Engineering: implement LIFF quiz endpoint (3-question persona quiz capturing email via LINE Login `email` scope — research §7.10 hedge).
- [ ] Compliance review: 特定商取引法 disclosure page published; privacy policy linked from m1 + LIFF consent.

### Week 2 — internal soft-launch

- [ ] 5 internal test friends added via `liff.line.me` add link.
- [ ] Verify all 7 step messages arrive on schedule (m1 immediate; m2 at +12h; m3 Day 3; m4 Day 7; m5 Day 14; m6b Day 21; m7 Day 60).
- [ ] Verify block / unfollow handling cancels remaining steps.
- [ ] Verify rich menu loads correctly with brand-specific cells.
- [ ] Verify LIFF book preview routes to BookWalker / Amazon JP.
- [ ] Verify LIFF quiz captures email (LINE Login `email` scope) and stores in same DB.

### Week 3 — friends-and-family + organic launch

- [ ] In-book QR codes activate for the live 静心社 catalog (back-matter CTA per `specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md` §10.5; URL replaced with `liff.line.me/...`).
- [ ] One-time GHL email blast to JP-locale opt-in segment with the 静心社 OA add-friend QR.
- [ ] LINE VOOM posting begins (3–5/week).
- [ ] First m1 read rate reading (target ≥ 70% within 1h).
- [ ] First email-hedge capture rate reading (target ≥ 40%).

### Week 4 — paid pilot (only if Week 3 organic friend count ≥ 1,000)

- [ ] LAP click-to-message ad with ¥30,000 test budget, **brand-fit creative** (no generic wellness creative).
- [ ] Two ad variants A/B (e.g., morning calm vs evening calm).
- [ ] CPA target ¥300 per friend; pause if CPA > ¥500 after first 100 adds.
- [ ] First m4 link-card CTR reading.
- [ ] If Week 3 organic < 1,000: defer paid to Week 6, double down on owned channels.

### Week 5 — first hard-pitch fire

- [ ] First cohort hits Day 14 → m5 fires with first LINE-native coupon (20:30 Tue or Wed).
- [ ] First purchase confirmations expected via affiliate postback (Amazon JP + BookWalker).

### Week 6 — first full KPI readout

- [ ] All v1 KPIs measured against targets.
- [ ] Decision: tighten or stretch cadence based on read-rate decay curve.
- [ ] Decision: A/B `line_native_fast` (+12h M2) vs `email_equivalent_slow` (+24h M2) — pick winner.
- [ ] Decision: keep Format A only, or layer Format B (LIFF quiz → tailored PDF).
- [ ] Quota burn check: is 静心社 Standard tier headroom sufficient?

### Week 7 — second-brand pilot (体記堂 body_memory)

- [ ] Operator creates second OA channel: 体記堂 (Standard tier).
- [ ] Sticker set order (¥6,400).
- [ ] 体記堂 brand-variant copy already in `messages.ja_JP.yaml` (full slot authoring).
- [ ] Brand-tagged friend-add via 体記堂 in-book QR.
- [ ] Verify per-brand variant copy fires correctly.
- [ ] Two-OA cross-brand-handoff test in m6b_cross_sell.

### Week 8 — readout + scale-out gate

- [ ] Did `line_native_fast` (+12h M2) outperform `email_equivalent_slow` (+24h M2) on first-purchase CVR within 30d? Hypothesis: yes by 1.5–2.5×.
- [ ] Did Format A meet ≥ 3% drip→purchase CVR for Tier 1?
- [ ] Did email-hedge capture meet ≥ 40% target?
- [ ] **Greenlight Tier 1 expansion** (体知社, 直見堂, 今此処社) → Month 3 milestone.
- [ ] If 静心社 is at ≥ 3,000 friends: paid acquisition unlocked for that brand at full ¥300 CPF spend.

---

## 11. Compliance

See [funnel/burnout_reset/LINE_HANDOFF.md](../funnel/burnout_reset/LINE_HANDOFF.md) §"Compliance checklist" for the operational gate. Plan-level treatment:

| Regulation | Applies to LINE? | Operational implication |
|---|---|---|
| 特定商取引法 (Specified Commercial Transactions Act) | Yes — for any commerce flow | Disclosure on landing + soft-pitch + hard-pitch slots; seller name, address, contact |
| 個人情報保護法 (Personal Information Protection Act) | Yes — even friend-add | Privacy policy link in m1_welcome + LIFF quiz consent screen |
| 特定電子メール法 (Anti-spam Act) | **No** — applies to email only [research §5] | Block / unfollow is the user-side opt-out under LINE OA TOS |
| LINE OA Terms of Service | Yes — primary cadence rule | No more than ~daily push; no medical claims; no prohibited categories |
| 薬機法 (Pharmaceutical/medical device law) | Yes — limits wellness-claim language | Use 整える / ととのう / やわらげる; never 治る / 効きます / 必ず |

The medical-claim blocklist is encoded in `funnel_definition.yaml::compliance.medical_claim_blocklist`. Pre-publish gate (run as part of `scripts/ci/check_book_output_no_placeholders.py` analog) blocks any message slot containing blocklist patterns.

### APPI sensitive-data care (research §5)

Any LIFF quiz question of the form "do you have anxiety / insomnia / depression" risks being classified as **sensitive personal data** under 個人情報保護法 (APPI) Article 2.3, which carries stricter consent requirements. Mitigation per research §5:

- Frame quiz questions as **self-classification surveys**, not health-data collection. Example: "今、いちばん近い気分はどれ?" (which mood is closest to you right now?) — not "Do you suffer from anxiety?"
- Do **not** store quiz answers as a medical record; tag them as voice/topic preferences only.
- Surface a privacy policy link **before** the quiz starts, not just after.
- Reference 厚生労働省 こころの耳 ([https://kokoro.mhlw.go.jp/](https://kokoro.mhlw.go.jp/)) as a safe-harbor referral pattern for any reader self-disclosing serious distress — research §5 cites this as the operator's defensible referral target.

### Frame books as 悩みを軽くするヒント, not therapeutic claims

Per research §7.8, all book descriptions in m4/m5/m6b should use frames such as:

- 「悩みを軽くするヒント」 (hints for lightening worries)
- 「夜の落ち着きを取り戻すための物語」 (a story for restoring evening calm)
- 「ととのうための短いワーク」 (a short practice for tuning yourself)

Avoid: 「不安症が治る」 / 「鬱が改善する」 / 「不眠を完全に治す」 — these trigger 薬機法 / APPI scrutiny.

---

## 12. What's next (post-PR engineering / operator actions)

Engineering (separate PRs):

1. **LINE webhook receiver** — `funnel/burnout_reset/line_app.py` mirroring `app.py` for GHL but on LINE primitives.
2. **LIFF quiz-to-PDF generator** — small service that maps quiz output `(topic, persona)` → existing `scripts/create_freebie_assets.py` invocation.
3. **Quota burn dashboard** — pulls Insight API into the same DB dashboard as email metrics.
4. **Rich-menu image authoring + upload** — design + 1024×682 image per hub; `POST /v2/bot/richmenu`.

Operator (operational):

1. **LINE Developers provider** + 3 hub channels.
2. **Sticker sets** (3 × ¥6,400) — brand-tone, 4–6 stickers each.
3. **LAP advertiser account** + KYC.
4. **特定商取引法 disclosure page** published on operator domain.
5. **LINE Pay merchant** (Phase 2 only — gated to iyashikei hub after Week 8 readout).

Translation / planning (separate planning streams):

1. **zh_TW LINE Taiwan extension** — Taiwan has high LINE penetration; the funnel structure transfers but the language and store routing differ. Separate research task.
2. **Asset team** — create 12 brand sticker sets across all 3 hubs as Phase 2 expansion (currently scoped at 3 hub-level sets only).
3. **Per-brand voice expansion** — `tier_3_niche` brands currently fall back to hub-level copy; full slot authoring is a Phase 2 task once the hub-level model is proven.

---

## 13. Open questions / decisions held for operator

Decisions resolved by Pearl_Research and incorporated above:
- ✅ **Multi-brand orchestration model** — flipped from hybrid 3-hub (preliminary) to **per-brand 12 OAs at Standard tier** (research §7.5). Hybrid retained as documented fallback.
- ✅ **Cadence** — M2 telescopes from +24h to **+12h** (research §7.1). Slow profile preserved for A/B comparison.
- ✅ **Send-time windows** — 20:00–21:30 JST Sun/Tue/Wed/Thu (research §7.2).
- ✅ **Email hedge** — capture email at LIFF quiz step via LINE Login `email` scope (research §7.10).
- ✅ **CPF target** — ¥300 (research §2 anchor).
- ✅ **Acquisition sequencing** — owned-channels-first; paid LAP only after 3,000-friend organic baseline per brand (research §7.4).

Remaining for operator:

1. **Brand-name discrepancies** — three brand-name comments in `config/catalog/market_catalog_registry.yaml` (Japan section) conflict with canonical `config/catalog_planning/locale_brand_names.yaml`:
   - `body_memory` — registry comment says `持地社 (Mochi Chi Sha)`; canonical = **体記堂 (Taiki-dō)** (locale file line 159).
   - `solar_return` — registry comment says `炎転社 (Honten-sha)`; canonical = **燼と灰社 (Jin to Hai Sha)** (locale file line 173).
   - `devotion_path` — registry comment says `開心堂 (Kaishin-dō)`; canonical = **開器社 (Kaiki-sha)** (locale file line 187).
   This plan uses the canonical locale-file names. Registry-comment cleanup is out of scope for this PR.

2. **48_SOCIAL_GHL spec mojibake** — JP CTA strings in [docs/48_SOCIAL_GHL_BRAND_ADMIN_SPEC.md](48_SOCIAL_GHL_BRAND_ADMIN_SPEC.md) lines 181, 189, 226 contain mojibake. Out of scope for this PR; flagged for separate cleanup.

3. **Per-brand sticker set design** — 12 sticker sets at ¥6,400 each = ¥76,800 launch one-time. Operator decides whether to commission all 12 at launch or stagger with brand provisioning (Tier 1 flagships first).

4. **Research's `[unverified]` items** (research §1, §2, §4) include:
   - Exact 2026 LINE Pay online-merchant transaction rate (last public rate is 2018).
   - 2026 Amazon Associates JP ebook commission table.
   - Friend-add → first-purchase CVR for digital book publishers.
   - Smartphone vs e-ink vs print share for self-help reading.
   These are sourced from analog data; operator should validate with the publishers directly before locking final KPI numbers.

5. **Phased provisioning vs all-at-once launch** — plan recommends Tier 1 flagships in Month 3, full 12 OAs by Month 6 (§6). Operator can compress timeline if budget is sufficient and Week 8 readout is positive.

---

## Appendix A — Companion file index

| File | Purpose |
|---|---|
| [docs/JAPAN_LINE_FREEBIE_FUNNEL_PLAN_2026-04-29.md](JAPAN_LINE_FREEBIE_FUNNEL_PLAN_2026-04-29.md) | This doc — strategic plan |
| [funnel/burnout_reset/LINE_HANDOFF.md](../funnel/burnout_reset/LINE_HANDOFF.md) | Engineering + operator handoff (mirrors GHL_HANDBOFF.md) |
| [config/funnel/line_jp/funnel_definition.yaml](../config/funnel/line_jp/funnel_definition.yaml) | State machine YAML |
| [config/funnel/line_jp/oa_brand_registry.yaml](../config/funnel/line_jp/oa_brand_registry.yaml) | 12 brands × 3 hubs orchestration map |
| [config/funnel/line_jp/messages.ja_JP.yaml](../config/funnel/line_jp/messages.ja_JP.yaml) | Native Japanese message copy (per slot, per hub, per brand) |
| [config/funnel/line_jp/rich_menu.ja_JP.yaml](../config/funnel/line_jp/rich_menu.ja_JP.yaml) | Rich menu cells, per-hub layouts |
| [artifacts/research/japan_line_freebie_funnel_market_research_2026-04-29.md](../artifacts/research/japan_line_freebie_funnel_market_research_2026-04-29.md) | Pearl_Research market intelligence + citations |
| [artifacts/research/japan_line_competitive_funnel_audit_2026-04-29.md](../artifacts/research/japan_line_competitive_funnel_audit_2026-04-29.md) | Competitor LINE OA flow walkthroughs |

## Appendix B — Quick decision summary

| Question from brief | Answer |
|---|---|
| What freebie format converts on LINE in Japan? | **Format A (7-Day LINE Drip Mini-Course)** as v1 default for all brands. Format B (LIFF Quiz → PDF) Phase 1.5 for cognitive hub. Format C (sample manga chapter) Phase 2 for manga-led brands. |
| What's the optimal opt-in mechanic? | **Friend-add directly** (no LINE Login OAuth in v1). Optional **pre-add LIFF quiz** for richer signal capture. |
| How does it lead to paid book purchase? | **Affiliate routing** (BookWalker manga-led / Amazon JP prose-led) is v1 default. **LINE Pay direct sale** is Phase 2, gated to iyashikei hub only after Week 8 readout. |
