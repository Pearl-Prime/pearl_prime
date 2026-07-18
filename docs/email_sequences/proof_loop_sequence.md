# Proof-Loop email sequence (conversion-optimized)

**Purpose:** Exercise -> Second exercise -> Story -> Book -> More books -> Book 2 -> Book 3/bundle -> Last chance -> Still here. Two micro-reliefs before offer, then a lightweight evergreen book path. Canonical copy source for E1-E9.

**HTML shell source:** Mirror [funnel/waystream_sanctuary/emails/email_1_tool_delivery.html](../../funnel/waystream_sanctuary/emails/email_1_tool_delivery.html) through [email_9_still_here.html](../../funnel/waystream_sanctuary/emails/email_9_still_here.html) into GHL for Waystream. The older generic pilot shells remain under `funnel/burnout_reset/emails/`.

**Scope note:** WF2 `bonus_pre_story` is not part of canonical E1-E5 copy. It is the optional pre-E3 branch used only when `funnel_variant = welcome_depth`. `guided_audio` belongs only in `bonus_pre_story`, never E1.

**Placeholders:** GHL receives evergreen contact fields at capture time. Each slot E1-E9 has `phoenix_eN_title`, `phoenix_eN_url`, `phoenix_eN_cta`, `phoenix_eN_tool_name`, `phoenix_eN_short_description`, `phoenix_eN_benefit`, and `phoenix_eN_microcopy`. Special fields include `phoenix_e3_story_body`, `phoenix_e4_book_title`, `phoenix_e5_book1_*` through `phoenix_e5_book3_*`, `phoenix_e6_book_title`, `phoenix_e7_bundle_title`, and `phoenix_e8_last_chance_note`.

**Timing:** E1 immediate, E2 +24h, optional WF2 `bonus_pre_story` +48h (`welcome_depth` only), E3 +72h, E4 +120h, E5 +288h, E6 +72h after E5, E7 after E6, E8 last-chance nudge, E9 still-here/free-tool reminder.

---

## Email 1 — Immediate

**Subject:** Your {{exercise_name}} tool is here, {{first_name}}

**Body:**

{{first_name}},

You asked for it. Here it is.

**{{exercise_name}}** — one practice, no sign-up walls.

[Open the tool →]({{tool_link}})

Use it when you need it. Or use it now, before you need it — that's when it sticks.

— Phoenix Protocol

---

## Email 2 — +24h (second practice)

**Subject:** One more reset — {{second_exercise_name}}, {{first_name}}

**Body:**

{{first_name}},

Today: a second practice. Different from the first. Same idea — your nervous system, a few minutes, real shift.

**{{second_exercise_name}}** — do it once. Notice what changes.

[Do {{second_exercise_name}} →]({{second_tool_link}})

No philosophy. Just the link. Next I'll send you a short story about someone who used both.

— Phoenix Protocol

---

## Email 3 — +72h (transformation story)

**Subject:** Why this actually works (a short story)

**Body:**

{{first_name}},

{{story_body}}

No pitch today. Just the story. In 48 hours I'll share one book that goes deeper — for when you're ready.

— Phoenix Protocol

---

## Email 4 — +48h after Email 3 (book offer)

**Subject:** Recommended for you: {{book_title}}, {{first_name}}

**Body:**

{{first_name}},

You've tried two practices. You've read how it landed for someone else.

If you're ready to go deeper: **{{book_title}}** is built for this pattern.

[See {{book_title}} →]({{book_link}})

No pressure. The free tools are still there. This is for when you want the full journey.

— Phoenix Protocol

---

## Email 5 — +168h after Email 4 (+288h from capture)

**Subject:** More books for this issue, {{first_name}}

**Body:**

{{first_name}},

You're on this list because you chose a tool that actually works. If you want to go further:

{{more_books}}

Use the links above when you're ready. And keep using the free practices — especially on the days you don't "need" them.

— Phoenix Protocol

---

## Email 6 — post-E5 Book 2 recommendation

**Subject:** {{phoenix_e6_title}}

**Body:**

{{first_name}},

The next recommendation is **{{phoenix_e6_book_title}}**.

{{phoenix_e6_short_description}}

[{{phoenix_e6_cta}}]({{phoenix_e6_url}})

{{phoenix_e6_microcopy}}

— Phoenix Protocol

---

## Email 7 — Book 3 / bundle path

**Subject:** {{phoenix_e7_title}}

**Body:**

{{first_name}},

If you prefer a grouped path, use **{{phoenix_e7_bundle_title}}**.

{{phoenix_e7_short_description}}

[{{phoenix_e7_cta}}]({{phoenix_e7_url}})

{{phoenix_e7_microcopy}}

— Phoenix Protocol

---

## Email 8 — last chance

**Subject:** {{phoenix_e8_title}}

**Body:**

{{first_name}},

This is the last direct nudge in this sequence.

{{phoenix_e8_last_chance_note}}

[{{phoenix_e8_cta}}]({{phoenix_e8_url}})

{{phoenix_e8_microcopy}}

— Phoenix Protocol

---

## Email 9 — still here / free tool link

**Subject:** {{phoenix_e9_title}}

**Body:**

{{first_name}},

No new ask today. Just the original free tool again.

**{{phoenix_e9_tool_name}}**

[{{phoenix_e9_cta}}]({{phoenix_e9_url}})

{{phoenix_e9_microcopy}}

— Phoenix Protocol
