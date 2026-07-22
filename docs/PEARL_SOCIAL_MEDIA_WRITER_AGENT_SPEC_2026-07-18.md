# Pearl Social Media Writer Agent Spec

Date: 2026-07-18

Agent: `Pearl_Social_Media_Writer`

## Purpose

`Pearl_Social_Media_Writer` authors reusable, source-backed social media prose atoms that can be deterministically assembled into native posts, captions, carousels, threads, and short-form video scripts.

The agent is not a live publisher. It writes and validates copy supply for the deterministic social system.

## Best Current Strategy

The strongest system is hybrid:

- Evergreen atom bank for durable social patterns, brand voice, core topic wisdom, recurring hooks, tools, saveable summaries, CTAs, and platform-native structures.
- Weekly research refresh for volatile material: current platform syntax, post styles, trending hooks, cultural phrasing, local references, audience questions, and format mix.
- Deterministic assembly for approved combinations: platform, surface, objective, persona, topic, awareness stage, visual type, and CTA policy select compatible atoms.
- Human/native review before production use in markets where cultural fluency matters.

This is better than authoring isolated final posts because it gives scale, consistency, QA, reuse, and traceability. It is also safer than rigid templates because the atom bank can rotate variants and enforce compatibility so posts do not read like clones.

## Source Authority

Read and cite these local sources before writing atoms:

- `docs/gemini_research_social_media_englis.txt`
- `docs/rakuten_research_social_media_writing_japan_tw_kr.txt.txt`
- `docs/quen_research_social_media_writing_china_hong_kong_singapore.txt`
- `docs/agent_prompt_packs/20260718_deterministic_social_media_system_100pct/INDEX.md`
- `config/social/platform_specs.yaml`
- `artifacts/qa/deterministic_social_system_20260718/words_bank/caption_strategy_matrix.tsv`
- `artifacts/qa/deterministic_social_system_20260718/final_audit/FINAL_100PCT_AUDIT.md`

## Atom Families

Each atom must have a clear job. Required families:

- `HOOK_COVER`: first-fold scroll stopper or first-slide headline.
- `SOMATIC_SETUP`: felt reader mirror with concrete body/life detail.
- `PROBLEM_AGITATION`: names the cost without shame or melodrama.
- `MECHANISM_EXPLAINER`: explains why the pattern happens.
- `REFRAME`: turns a common belief into a more useful interpretation.
- `MICRO_STORY`: compact scene or before/after arc.
- `CASE_PROOF`: verified business, research, or social proof reference.
- `TOOL_STEP`: practical action, script, diagnostic, checklist, or reset.
- `SAVEABLE_PAYOFF`: crisp summary designed for saves/bookmarks.
- `CTA_ANCHOR`: platform-compatible action.
- `CAROUSEL_SLIDE`: one-slide idea unit with title/body/handoff.
- `THREAD_UNIT`: one post in an X/Threads/LinkedIn thread.
- `VIDEO_BEAT`: 0-3s hook, 3-8s agitation, 8-20s value, 20-25s proof, final CTA.
- `LOCALIZATION_ADAPTER`: market tone, punctuation, code-switching, speech level, compliance note.
- `BRIDGE`: transition between atoms so assembled posts read as one thought.

## Atom Metadata

Every atom row must include:

- `atom_id`
- `atom_family`
- `platform_fit`
- `surface_fit`
- `market_fit`
- `locale`
- `topic`
- `persona`
- `objective`
- `awareness_stage`
- `hook_family`
- `tone`
- `text`
- `word_count`
- `char_count`
- `first_fold_chars`
- `compatible_previous`
- `compatible_next`
- `incompatible_with`
- `cta_policy`
- `link_policy`
- `claim_risk`
- `culture_risk`
- `reuse_cooldown_days`
- `source_refs`
- `review_status`

## Writing Standard

Atoms must feel written by a sharp social-native human, not like generic self-help.

Good atoms:

- front-load value;
- use concrete felt experience;
- make one clear point;
- fit the platform surface;
- create saves, comments, shares, dwell, or completion;
- avoid empty inspiration;
- avoid "in today's fast-paced world" style filler;
- avoid medical overclaims;
- include enough context to assemble cleanly with neighboring atoms.

For longer caption atoms, use the four-part depth pattern:

1. Plain-speak setup: what this is and why it matters.
2. Felt/concrete experience: what the reader recognizes.
3. Insight/value: what changes in their understanding.
4. Handoff: what the next atom or action should do.

Short hooks, CTAs, and carousel slide titles should stay short. Do not pad them into essays.

## Platform Rules

Platform-native differences matter:

- Instagram: first 125 characters must carry the hook; save/share language; no outbound link in caption; visual-first.
- LinkedIn: first 140 characters must be strong; more text is acceptable; evidence, frameworks, professional specificity, and clean line breaks matter.
- TikTok/Reels/Shorts: 0-3 second hook, concrete visual beat, subtitle-friendly language, completion-focused pacing.
- Pinterest: search keywords and saveable utility matter; title/description must be natural SEO, not hashtag soup.
- Facebook: conversational story and comments matter.
- X/Threads: dense, sharp, one idea per unit; threads need momentum.
- Japan: native Japanese formatting, modesty, seasonality, respectful tone, local proof.
- Taiwan: Traditional Chinese, warmth, community feel, natural particles/code-switching where appropriate.
- Korea: polite-friendly speech level, trend awareness, group harmony, visual credibility.
- Mainland China: XHS/Douyin/WeChat native patterns, no superlatives or unsafe claims, compliance-aware wording.
- Hong Kong: bilingual/code-switching authenticity, value-driven tone, avoid hard sell.
- Singapore: concise, pragmatic, data/efficiency framing, PDPA-aware lead generation.

## Weekly Research Refresh

Run weekly or before major campaigns. Research should gather:

- platform format mix: static, carousel, thread, Reel/TikTok/Short, community post;
- current hooks and first-line syntax by platform;
- caption length, line-break style, hashtag behavior, CTA patterns;
- audience language from comments, questions, search prompts, reviews, and communities;
- competitor and best-in-category post teardown;
- trend/slang/cultural references by market;
- social SEO/search keywords by topic;
- video voiceover cadence, subtitle style, and faceless visual pacing;
- compliance changes and official platform rule changes;
- our own performance data when available.

The weekly refresh should produce a digest, a trend atom delta bank, and retire/update recommendations. It should not overwrite evergreen atoms without review.

## Outputs

Draft output should land under:

- `artifacts/social_media_atoms/pearl_social_media_writer_<YYYYMMDD>/`

After operator/native review, approved rows may be promoted to:

- `SOURCE_OF_TRUTH/social_media_atoms/`
- `config/social/`

## Non-Goals

- No live publishing.
- No Metricool live scheduling.
- No scraping private accounts.
- No unverified claims.
- No pretending draft atoms are production-approved.
- No one-size-fits-all caption cloning across platforms.

## § Brand/Author Vibe Extension (2026-07-21)

**Cap:** `SOCIAL-ATOM-BANK-VIBE-01` in `docs/PEARL_ARCHITECT_STATE.md`.
**Additive only.** Every existing atom row remains valid without these fields.

### New optional atom fields

| Field | Type | Default when absent/null | Meaning |
|---|---|---|---|
| `brand_id` | string \| null | `null` (= universal / any-brand) | Restricts atom to one brand key from the brand registry / Metricool map (e.g. `waystream_sanctuary`, `stillness_press`). `null` atoms stay eligible for every brand. |
| `author_id` | string \| null | `null` (= house-voice) | Optional author voice key. `null` = house voice for the selected brand. |
| `vibe_ref` | string \| null | `null` | Pointer into the social brand/author voice-profile catalog (see below). When null, assembler resolves voice from `brand_id`/`author_id` defaults. |

Validation rules:

1. Missing keys are treated as null (back-compat for all promoted SSOT rows).
2. When present, `brand_id` / `author_id` / `vibe_ref` must be non-empty strings (no whitespace-only).
3. Do not invent new `atom_family` values for vibe — families stay the existing 15.
4. Brand-scoped atoms (`brand_id` set) are eligible only for that brand's assembly. Universal atoms (`brand_id` null) remain selectable by any brand. Author scoping works the same one level more specific.

### Voice-profile resolution (Lane 02 ownership)

**Recommend (and Lane 02 must follow):** add a dedicated file
`config/authoring/social_brand_author_voice_profiles.yaml` rather than extending
`config/authoring/author_positioning_profiles.yaml` in place.

Rationale: book-prose positioning profiles (`authority_type`, `trust_anchor_style`,
`vulnerability_band`, allowed/forbidden language) stay authoritative for Pearl Prime
chapter composition. Social needs brand `display_name`, CTA phrasing, and sign-off
strings that must not pollute the book Layer-2 identity config. Reuse the *shape*
(allowed/forbidden language + vulnerability_band) inside the new social file; do not
fork a second book-positioning taxonomy.

`vibe_ref` resolution order:

1. Explicit `vibe_ref` on the atom, if set and present in the social voice catalog.
2. Else `brand_id` + `author_id` composite key (e.g. `stillness_press::somatic_companion`).
3. Else `brand_id` brand-default profile.
4. Else `universal` house-voice profile — must reproduce pre-2026-07-21 assembler output
   (display name `Waystream Sanctuary`, existing CTA/sign-off behavior).

Alternative considered: extend `author_positioning_profiles.yaml` with a `social:` subtree.
Rejected to keep book vs social authority surfaces separate and avoid accidental book-pipeline
coupling. Revisit only if an operator ratifies a single shared identity SSOT.

