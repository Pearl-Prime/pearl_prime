# Lane C — Before/After Comparison (2026-07-23)

Agent: `pearl-social-media-writer` (Lane C, atom repair) · Project:
`proj_social_atom_bank_vibe_20260721` · Subsystem: `social_media`

Acceptance layer of the changes below: **EXECUTED-REAL for the touched cells**
(byte-verified in `SOURCE_OF_TRUTH/social_media_atoms/*.jsonl`, self-QA gate
passing, manually hand-traced through the composition logic) — **not**
catalog-wide, and **not** `PROVEN-AT-BAR` (no blind-judged sample was run).
Six-layer taxonomy per `docs/specs/SOCIAL_MEDIA_100PCT_PRODUCTION_PLAN_2026-07-22.md`.

Touched cells: topics `anxiety`, `burnout` x personas `corporate_managers`,
`gen_z_professionals` (the proven pilot slice, per this lane's brief). The
LOCALIZATION_ADAPTER repairs below additionally cover `ja-JP`, `ko-KR`,
`zh-CN`, `zh-HK`, `zh-TW`, `en-SG`, and the new `zh-SG` market.

---

## 1. The broken mail-merge template (root defect named in the brief)

**Before** — live pilot evidence, `artifacts/qa/social_atom_composition_pilot_20260721/posts.jsonl`,
`copy_1bc8cdb2f97c` (persona=corporate_managers, topic=burnout, atom
`EVG-ENUS-BURN-CORP-HC-01`), assembled caption opening line:

> "corporate managers: more discipline will fix exhaustion is not the whole story."

This is a literal template fill (`"{persona}: {clause} is not the whole
story."`) — the persona slug leaks into the sentence as raw metadata, and the
clause-plus-tail construction is grammatically valid but semantically empty.
Root cause traced to `hook_family: contrarian_reframe`, documented as "Example
C" in `artifacts/research/storyblocks_semantic_sourcing_20260720/RECOMMENDED_TAXONOMY.md:410`
and stamped across 20 topics x 3 personas during the 2026-07-21 scaleup wave
(see GENERATOR_ROOT_CAUSE in the closeout below — no committed generator
script was found to fix at the source).

**After** — same atom_id, rewritten in place, re-assembled live through
`phoenix_v4/social/deterministic_social.py` (`generate_copy_package`) after the
repair, actual caption opening line for the same cell:

> "More discipline was never the missing piece. What's missing is a nervous
> system that's actually allowed to stand down."

No persona label in the sentence. A real, specific claim instead of a
mail-merge fill. Six rows total repaired this way (anxiety+burnout x
corporate_managers/gen_z_professionals/healthcare_rns) — 54 of the 60 broken
rows across the full bank remain (18 topics not yet touched); see NEXT_ACTION.

---

## 2. Cross-persona verbatim duplication (the "reads as generic" mechanism)

**Before** — `EVG-ENUS-ANXI-GEN_-HC-02` (gen_z_professionals, anxiety) was
byte-identical to `EVG-ENUS-ANXI-CORP-HC-02` (corporate_managers, anxiety):

> "If tight chest is familiar, this anxiety pattern needs a better reset."

Same for `-HC-03`, and for `REFRAME-01` / `MECHANISM_EXPLAINER-01` in both
`anxiety` and `burnout` — the entire "insight" carried by these rows was
identical regardless of persona; only the `persona` metadata field
differed. A live duplicate-rate audit run at the start of this lane found this
pattern is not confined to HOOK_COVER: within just the anxiety+burnout x
corp+genz+healthcare_rns cell (162 rows across all 9 populated families),
`BRIDGE`, `REFRAME`, `MECHANISM_EXPLAINER`, `TOOL_STEP`, and `SAVEABLE_PAYOFF`
each had every row triplicated verbatim across the three personas (3 unique
texts out of 9 rows per topic).

**After** (gen_z_professionals rewritten distinct from corporate_managers,
same idea, different sentence):

> HOOK_COVER: "Tight chest before a notification even loads? That's not
> overreacting — that's a nervous system stuck scanning for the next hit."
>
> REFRAME: "Try this instead: your body doesn't need a better argument, it
> needs a landmark. Name three things you can actually touch right now —
> that tells your nervous system the room isn't a threat faster than any
> reasoning does."

14 rows repaired this way across HOOK_COVER/REFRAME/MECHANISM_EXPLAINER for
the touched cells. **Reported honestly**: `REFRAME-02`/`-03` and
`MECHANISM_EXPLAINER-02`/`-03` remain duplicated between corporate_managers
and gen_z_professionals in these same cells — this lane rewrote at least one
occurrence per repaired cell (the mission's stated bar) but did not
de-duplicate every row; see DUPLICATE_HOOK_RATE_BEFORE_AFTER below for exact
counts and NEXT_ACTION for what remains.

---

## 3. Six families that could not be assembled at all

**Before**: `MICRO_STORY`, `CASE_PROOF`, `CAROUSEL_SLIDE`, `THREAD_UNIT`,
`VIDEO_BEAT` had zero rows anywhere in the bank (confirmed live, matches Lane
A's finding). A carousel, thread, or short-video post could not be assembled
for any topic/persona because no source rows existed. `LOCALIZATION_ADAPTER`
existed (60 rows) but had zero rows for the `zh-SG` market — only `en-SG`
(English-language Singapore) existed, and `en-SG`'s own `VOICE_POSTURE` row
stated only the productivity/efficiency register ("concise, pragmatic,
efficient, data/utility-first"), which today's native-speaker review flagged
as specifically wrong for mental-health content.

**After** — one full example of each new structural family, burnout x
corporate_managers cell, chained through `compatible_previous`/`compatible_next`:

> **MICRO_STORY → CASE_PROOF → TOOL_STEP → CTA_ANCHOR** (hand-traced live,
> see below): a concrete before/after scene ("the night she noticed her hands
> were shaking before she'd even opened Slack..."), followed by a
> shared-struggle proof line ("This isn't a rare pattern... This isn't a
> diagnosis and it isn't a guarantee. It's a pattern worth naming out loud."),
> a tool step, and a CTA — reads as one authored voice, no repeated
> "Try this:"-style label doubling, no persona-name leakage.

> **CAROUSEL_SLIDE** (6-slide open-loop arc, burnout x corporate_managers):
> cover poses the question ("Why do you still feel exhausted after a full
> weekend of rest?"), builds for 3 slides, resolves at slide 5, closes with a
> save-and-try CTA at slide 6 — matching the verified open-loop pattern from
> Lane A's digest §4.

> **THREAD_UNIT** (Hook → Context → Position → Invitation, anxiety x
> gen_z_professionals): opens with unresolved tension ("Overthinking isn't a
> thinking problem. It's a body problem wearing a thinking costume."),
> carries one clear position, closes with a specific-experience invitation
> rather than a generic "comment below."

> **VIDEO_BEAT** (0-3s hook / 3-8s agitation / 8-20s value / 20-25s proof /
> final CTA, burnout x corporate_managers): matches the spec's existing beat
> map, achievable with the pipeline's composited text+B-roll format (no live
> camera needed — confirmed by Lane A's research, closing the named operator
> question).

> **LOCALIZATION_ADAPTER, zh-SG** (new market, authored by the `translate-zh-sg`
> subagent): `VOICE_POSTURE` explicitly names the two-register split
> ("emotional-support content is warm... productivity/corporate-wellness
> content stays concise and pragmatic") rather than repeating `en-SG`'s
> efficiency-only framing.

38 new English rows + 13 new LOCALIZATION_ADAPTER rows (10 zh-SG + 3 native-
reviewer-recommended additions to ja-JP/zh-CN/zh-HK) were authored and
promoted this session. All are `review_status: draft_operator_review_required`
— none are self-marked as human/native-reviewed-final.

---

## 4. LOCALIZATION_ADAPTER — native-review-driven repairs (not just additions)

**Before** (`ko-KR`, `VOICE_POSTURE`): "South Korea voice contract:
polite-friendly haeyo-che, trend-aware but not slang-dependent." — silent on
the collectivism/individualism register question.

**After** (rewritten per `translate-ko` subagent review, 2026-07-23):
"South Korea voice contract: polite-friendly haeyo-che, individual-centered
self-care framing rather than collectivist 'group harmony,' trend-aware but
not slang-dependent."

**Before** (`zh-HK`, `CULTURE_RISK`): "Risk guard: avoid forced Cantonese,
political sensitivity, hard-sell resource framing." — no concrete mainland-
coded-term list, no XHS-specific warning.

**After** (rewritten per `translate-zh-hk` subagent review): names the
specific mainland-coded terms that undercut HK credibility in mental-health
content (治愈, 正能量, 视频 vs 影片, 网红 vs KOL) and the XHS-mainland-
inflection risk explicitly.

20 existing rows repaired across 6 markets this way (`ja-JP` x3, `ko-KR` x3,
`zh-CN` x3, `zh-HK` x6, `zh-TW` x4, `en-SG` x1), plus 3 new rows the native
reviewers recommended adding rather than folding into an existing row (for
atomicity). Full detail and per-market native-reviewer verdicts are in this
lane's CLOSEOUT_RECEIPT.

---

## What this comparison does NOT claim

- Not a claim that the bank is "fixed" — 54 broken-template rows and the bulk
  of the cross-family duplication (18 other topics, the `healthcare_rns`/
  `entrepreneurs`/`gen_x_sandwich`/`working_parents` personas, and
  `REFRAME`/`MECHANISM_EXPLAINER` variants 02/03 in the touched cells) remain
  untouched.
- Not a claim of native/operator sign-off — every row here is
  `draft_operator_review_required`even where a native-speaker subagent
  reviewed it; a subagent review is not an operator's or a paid professional
  linguist's final sign-off.
- Not a claim that the new families are wired into the assembler —
  `phoenix_v4/social/deterministic_social.py` does not yet select
  `MICRO_STORY`/`CASE_PROOF`/`CAROUSEL_SLIDE`/`THREAD_UNIT`/`VIDEO_BEAT` rows
  (confirmed by inspection); that wiring is Lane D's scope, not this lane's.
