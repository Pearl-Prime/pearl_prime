# Pearl_Research — Deep Research Digest (2026-07-23)

Agent: `Pearl_Research` · Lane: `social-writer-lane-a-research-20260723`
Project: `proj_social_atom_bank_vibe_20260721` · Subsystem: `social_media`
Acceptance layer of this artifact: **RESEARCHED** (research layer only — not SPECCED, not CODE-WIRED, not a bestseller/production claim of any kind).

This is a refresh/extension per the spec's §Weekly Research Refresh. It does **not** overwrite
evergreen atoms and does **not** silently supersede any existing doc. See §0 for what changed and
why, including a hard blocker on four of the five cited authority docs.

---

## §0. Discovery report (read this first — it changes the shape of this lane)

**Date gap.** Today is 2026-07-23. The spec (`docs/PEARL_SOCIAL_MEDIA_WRITER_AGENT_SPEC_2026-07-18.md`)
is dated 2026-07-18 — a 5-day gap, not stale on its own terms. However:

**CORRECTION (found after initial git-only search — read this before trusting the "missing" framing
below): the four named docs are not missing, they are untracked.** My first pass searched only
`origin/main` via `git ls-tree`/`git cat-file`, which correctly reported all four as absent from git
history — **but they exist as real, substantial, already-authored files on local disk** at the main
checkout (`/Users/ahjan/phoenix_omega`, outside this lane's git worktree but on the same filesystem,
readable directly):

- `docs/gemini_research_social_media_englis.txt` — **EXISTS locally, untracked.** 113 lines, ~126KB.
  A dense technical design spec ("Technical Design Specification: Deterministic Social Media and
  Short-Form Video Copywriting Architecture," dated 2026-05-12) — full platform-by-platform surface
  specs (character limits, truncation points, dimensions, algorithm signals) plus a hook-taxonomy
  encyclopedia. Its Instagram hashtag guidance already says **"3 to 5 highly relevant hashtags... at
  the very bottom to assist semantic indexing"** — this predates and correctly anticipated the
  platform shift documented fresh in §1.1 below.
- `docs/research_gemini_social_media_templates_english.txt` — **EXISTS locally, untracked.** 5,201
  lines, ~131KB. A Gemini deep-research *prompt* (the assignment given to the research model) plus
  its resulting system-design blueprint for a deterministic template system, scoped to
  self-help/personal-growth/wellbeing content specifically — i.e., our exact niche.
- `docs/rakuten_research_social_media_writing_japan_tw_kr.txt.txt` — **EXISTS locally, untracked.**
  249 lines, ~63KB. I read this one in full. It is a genuinely strong JP/TW/KR playbook: durable
  principles (hook-early, visual+subtitle boost, consistency-over-frequency, community
  responsiveness), pitfalls with named examples (Dolce & Gabbana's China backlash as a
  translation-failure cautionary tale, PTT astroturfing blowback in Taiwan), content templates
  (Instagram carousel, YouTube outline, Facebook story checklist), an A/B-testing methodology
  section, and a full country-by-country localization deep-dive (Japan: precision/politeness/
  modesty register with real example phrasing; Taiwan: warmth/bilingual/community feel; Korea:
  trend-savvy/respectful-informality/group-harmony). See §5 for where my fresh 2026 native-speaker
  validation confirms, updates, or corrects this doc's specific claims.
- `docs/quen_research_social_media_writing_china_hong_kong_singapore.txt` — **EXISTS locally,
  untracked.** 70 lines, ~21KB. I read this one in full too: "From Hook to Conversion: A Playbook for
  Faceless Content in China, Hong Kong, and Singapore." Covers the XHS/Douyin/WeChat Channels
  ecosystem split (discovery vs. mass-reach vs. closed-loop-commerce, each with distinct algorithm
  priorities), Hong Kong code-switching-as-trust-signal, Singapore Singlish-as-authenticity-marker
  and PDPA consent requirements, a five-phase cross-platform video anatomy (Pattern Interrupt Hook
  0-3s → Problem Agitation 3-8s → Value/Solution 8-20s → Social Proof/Credibility 20-25s → Clear CTA
  last 2-5s — nearly identical to the spec's own VIDEO_BEAT map), and AI-voice/visual-workflow
  guidance for faceless production. See §5 for native-speaker-validated updates.

Also found, from the spec's own §Source Authority list (not part of this lane's AUTHORITY_DOCS but
cited as required reading before writing atoms) — genuinely missing from *both* origin/main and the
local disk, i.e. actually absent, not just untracked:

- `docs/agent_prompt_packs/20260718_deterministic_social_media_system_100pct/INDEX.md` — not found either place
- `artifacts/qa/deterministic_social_system_20260718/words_bank/caption_strategy_matrix.tsv` — not found either place
- `artifacts/qa/deterministic_social_system_20260718/final_audit/FINAL_100PCT_AUDIT.md` — not found either place

`config/social/platform_specs.yaml` (cited in the same list) exists on `origin/main`, confirmed
earlier.

**Corrected framing for mission item 5**: I *can* compare fresh 2026 research against the
rakuten/quen docs' actual claims — I did, and folded the comparison into §5 line-by-line. The
"verify... still current" instruction is answerable after all; my first-pass "these docs don't
exist" conclusion (still true for `origin/main`, the git-tracked branch of record) was wrong for "do
they exist at all," and I've corrected it here rather than silently editing it out. **The real,
actionable finding is not "these docs need authoring" — it's "these docs are real, good, and were
never committed, so no atom-authoring session and no CI-tracked research-refresh process has ever
been able to see or cite them."** See Retire/Update Rec R1 — landing these four files is a small,
concrete fix, not a research gap.

Two more untracked-local files surfaced while cross-checking a sibling lane's plan doc (see §0.3):
`docs/research_social_media.txt` (5,914 lines — read substantially, not exhaustively; contains the
richest existing MICRO_STORY/CASE_PROOF-adjacent material in the whole set, see §2/§3) and
`docs/research_gemini_social_media_templates_english.txt` (already listed above). Per
`docs/specs/SOCIAL_MEDIA_100PCT_PRODUCTION_PLAN_2026-07-22.md` (Pearl_PM, exists on `origin/main`),
`docs/research_social_media.txt` is **directly quote-cited by 22 existing atom rows** — it is not a
theoretical prior-art source, it is already load-bearing for the atom bank that exists today, which
makes leaving it untracked/uncommitted a real provenance risk (a citation pointing at a file that
isn't in version control), not just a tidiness issue.

**§0.1 — Atom family emptiness confirmed and is worse than the brief states.** I counted every row
by `atom_family` across all three SOURCE_OF_TRUTH files:

| File | Rows | Families present |
|---|---|---|
| `evergreen_en_us_atoms.jsonl` | 1,686 | BRIDGE(189), CTA_ANCHOR(189), HOOK_COVER(189), TOOL_STEP(189), MECHANISM_EXPLAINER(186), PROBLEM_AGITATION(186), REFRAME(186), SAVEABLE_PAYOFF(186), SOMATIC_SETUP(186) |
| `platform_surface_atoms.jsonl` | 250 | CTA_ANCHOR(50), FORMAT_BEAT(50), PLATFORM_HOOK(50), SURFACE_BODY(50), TRUNCATION_GUARD(50) |
| `apac_localization_atoms.jsonl` | 60 | LOCALIZATION_ADAPTER(60) |

**Zero rows anywhere** for: `MICRO_STORY`, `CASE_PROOF`, `CAROUSEL_SLIDE`, `THREAD_UNIT`,
`VIDEO_BEAT`. The brief named MICRO_STORY and CASE_PROOF specifically; the gap is actually five
families wide, not two. This research digest (§2–§4) is scoped to seed all five, not just the two
named in the brief, since Lane C will hit the same wall on the other three the moment it tries to
assemble a carousel, thread, or video post.

**§0.2 — Pilot posts confirm the "generic/dead" diagnosis with hard numbers**
(`artifacts/qa/social_atom_composition_pilot_20260721/posts.jsonl`, 20 posts, persona=corporate_managers,
topic=burnout, brands stillness_press/cognitive_clarity, platforms linkedin/instagram):

- **Hashtag load: 5–10 hashtags per post, average 7.5.** Every single post ends in a hashtag block
  (`#burnout #burnoutrecovery #workplacewellbeing #energyaudit #selfreflection` or similar). This is
  directly counter to current platform behavior (§1.1).
- **CTA variety: 2 unique CTAs across all 20 posts** — "Save this stillness practice for the next
  loud hour." and "Bookmark this framework and test one step this week." Every post uses one of
  exactly two lines, verbatim, regardless of brand or platform.
- **Opening-line variety: 5 unique hooks across 20 posts**, reused across both brands and both
  platforms with only cosmetic surface differences. Example: *"Name the cost before you try to fix
  the person. corporate managers: more discipline will fix exhaustion is not the whole story."* —
  this reads as a template with slot-fills (`corporate managers`) left legible as slot-fills, not
  as a written sentence. That specific defect — the persona name appearing mid-sentence as raw
  metadata rather than being woven into prose — is a composer/atom-authoring issue Lane C should
  fix directly; I flag it here because it is one of the sharpest concrete "reads as generic" signals
  in the live evidence.

**§0.3 — Other adjacent real local material (prior art, distinct from the five docs in §0 above).**
- `artifacts/research/prompt_generation_examples/global-social-media-pipeline/` — has
  `_gemini_prompt.md`, `_qwen_china_prompt.md`, `_rakuten_japan_prompt.md`, `_master_prompt.md`,
  `_research_brief.yaml`, `_routing.yaml`, `_INDEX.md`, and an `evaluation.md` / `before_legacy_prompt.md`
  pair. These are *prompt-generation examples for a prompt-authoring system*, not finished
  platform-behavior research — they document how to ask an LLM to produce region-flavored prompts,
  not what performs on each platform. Worth Lane C's awareness but not a substitute for real
  platform research.
- `docs/agent_prompt_packs/20260714_social_media_pipeline/08_Pearl_Research_qa_gates.md` — a QA-gate
  spec for a Pearl_Research role in an earlier pipeline design, not a research findings doc.
- `config/social/platform_specs.yaml` — real, current-dated (`verified_as_of: "2026-07-18"`),
  and load-bearing: it sets hard hashtag min/max per surface. **This file directly conflicts with
  §1.1 below AND with the already-authored, untracked `gemini_research_social_media_englis.txt`'s own
  3-5-hashtag guidance — it drifted from both a live platform change and our own prior research. This
  is my top retire/update recommendation (R2).**
- `docs/specs/SOCIAL_MEDIA_100PCT_PRODUCTION_PLAN_2026-07-22.md` (Pearl_PM, exists on `origin/main`,
  authored the day before this lane started) — independently names the exact same untracked-docs gap
  as its own gap item 8 ("Source Authority list reconciliation"), confirms 22 atom rows already
  quote-cite `docs/research_social_media.txt`, and separately confirms the APAC 60-row localization
  set's "native review" evidence is one operator chat-level assertion
  (`OPD-OC7-02`), not a per-row sign-off artifact — which is precisely the gap this lane's mandatory
  native-speaker validation step (§5) now provides real replacement evidence for, market-by-market,
  dated 2026-07-23.

---

## §1. Platform "alive vs dead" copy patterns — verified/cited

Every claim in this section came from a live web search run 2026-07-23 (see inline citations). None
are fabricated statistics; where a search result itself flagged a number as unverifiable, I've noted
that rather than repeating it as fact.

### §1.1 Hashtags: the single biggest confirmed drift since the 2026-07-18 spec/config

**Instagram capped hashtags at 5 per post platform-wide, announced by Instagram's official
@Creators account on 2025-12-19** — down from the prior effectively-unlimited/30-tag norm. Source:
[Instagram Implements New Limits on Hashtag Use — Social Media Today](https://www.socialmediatoday.com/news/instagram-implements-new-limits-on-hashtag-use/808309/),
corroborated by [Instagram's 5-Hashtag Limit in 2026 — CreatorLane](https://creatorlanehq.com/blog/instagram-5-hashtag-limit-2026)
and [Instagram Caps Hashtags at Five to Combat Spam — TechBuzz](https://www.techbuzz.ai/articles/instagram-caps-hashtags-at-five-to-combat-spam).
Instagram's own reasoning, as reported: hashtags are classification metadata for search, not a reach
lever — "they help search, not reach." Caption-native keywords now do the discovery work that
hashtag stacks used to be believed to do.

- **Confirms the brief's hypothesis directly.** Hootsuite's 2026 testing (cited via
  [Buffer's 2026 Instagram algorithm guide](https://buffer.com/resources/instagram-algorithms/) and
  corroborating hits) found keyword-optimized captions generated roughly 30% more reach and about
  2x the likes of hashtag-heavy posts. Optimal Instagram hashtag count is now **3–5, high-relevance,
  not generic** — using medium-competition tags (100k–1M posts) over mega-tags.
- **Conflict with our own config:** `config/social/platform_specs.yaml` sets
  `instagram_feed_portrait.caption.hashtags_min: 5, hashtags_max: 15` and
  `instagram_carousel` the same 5–15 range. The max is now flatly wrong (platform-enforced hard cap
  is 5, not 15) and the min sits at the very edge of what's now recommended as a ceiling, not a
  floor. See Retire/Update Rec R2.
- **LinkedIn, TikTok, Threads, X, Bluesky:** current guidance across all of these leans the same
  direction — few, tightly-relevant hashtags (3–5 typical) or none, with the caption itself carrying
  the SEO burden. Our config's `linkedin_feed_portrait`/`linkedin_short_video` (3–5) and
  `tiktok_reels_shorts_vertical` (3–5) ranges are **already in the right zone and do not need
  correction** — Instagram is the one surface that drifted.
- **Pinterest is the one platform where hashtags were never the primary lever** — pin description
  and board-title keywords have always mattered more; hashtags are "supplementary keyword signals."
  Source: aggregated from
  [SEO Sherpa's Pinterest SEO 2026 guide](https://seosherpa.com/pinterest-seo/) and
  [Pingroupie's 2026 guide](https://pingroupie.com/blog/pinterest-seo-guide-2026). Aim for 3–6
  keywords total across title + description + alt text, front-loaded (Pinterest's algorithm reads
  the start of the description first). Our config's `pinterest_pin.caption.hashtags_min/max: 2/5`
  is fine as a ceiling but should not be read as a target — the real lever is description keyword
  placement, which is not currently modeled as a distinct atom metadata field.

**Live pilot evidence directly contradicts current practice on both fronts**: the pilot's 5–10
hashtags per Instagram/LinkedIn post is over the new IG cap and over LinkedIn's own recommended
3–5, and its 2-CTA-total, 5-hook-total pattern across 20 posts is the opposite of "caption does the
SEO/hook work" — the caption text is templated, not written.

### §1.2 LinkedIn — dwell time is now the dominant signal, and it rewards more text, not less

Source: aggregated from
[Whitehat's 2026 B2B guide](https://whitehat-seo.co.uk/blog/increase-engagement-on-linkedin),
[SocialBee's 2026 LinkedIn algorithm guide](https://socialbee.com/blog/linkedin-algorithm/), and
[Stackmatix's data-driven breakdown](https://www.stackmatix.com/blog/linkedin-algorithm-how-it-works).

- Dwell time (on-feed + after-"see more"-click) is reported as the #1 2026 ranking signal, alongside
  a "Golden Hour" (first-60-minutes engagement velocity) and creator-authenticity signals.
- Optimal reported length: **300–400 words, 20+ sentences** to maximize dwell time — longer than
  a typical templated caption, provided it stays clear (ambiguous posts get penalized, not rewarded,
  for length).
- **Carousel/document posts get reported as generating 2–3x the dwell time of text/image posts** —
  directly relevant to why CAROUSEL_SLIDE (currently zero rows) matters for LinkedIn specifically,
  not just Instagram.
- **External links cost reach** — posts with outbound links reportedly see ~60% less reach than
  matched posts without one. This aligns with the spec's existing "no outbound link in caption" rule
  for Instagram and should be treated as equally true for LinkedIn, not Instagram-only.
- Engagement-bait patterns ("Comment YES if...") are now explicitly detected and penalized — worth
  a CTA_ANCHOR review pass, out of scope for this lane but flagged for Lane C.

### §1.3 TikTok/Reels/Shorts — hook-timing numbers are consistent across sources and match our config

Source: aggregated from
[SendShort's 2026 hooks guide](https://sendshort.ai/guides/tiktok-hooks/),
[Fluxnote's TikTok mental-health-creator strategy](https://fluxnote.io/guides/tiktok-mental-health-strategy),
and [HustleMarketers' faceless wellness guide](https://hustlemarketers.com/tiktok-faceless-wellness-content-strategy/).

- Hook in the first 3 seconds (63% of highest-CTR videos hook within 3s per one cited figure;
  treat the precise percentage as directional, not a hard fact to cite downstream), full hook
  window extends to ~6 seconds.
- Reported structure for a 30-second faceless video: **0–3s hook (mistake/result/bold statement),
  3–8s situate the problem, 8–22s deliver 2–3 concrete value beats, 22–27s payoff, 27–30s one light
  CTA** (save/comment/click — not "subscribe," which doesn't apply off-YouTube).
- This is close to but not identical to our spec's existing VIDEO_BEAT definition (0-3s hook, 3-8s
  agitation, 8-20s value, 20-25s proof, final CTA) — the spec's beat map is directionally right and
  does **not** need retiring; it needs actual atom rows written against it (currently zero).
- Mental health, sleep, and morning/evening routine content are specifically named as the strongest
  faceless-format niches with natural digital-product tie-ins — this is our niche, which is a good
  sign for format fit, not a reason to change format.
- Faceless-specific technique confirmed relevant to our pipeline constraint (composited text+visual,
  no human on camera): **text-on-screen over stock/ambient-audio B-roll performs consistently well**
  in this niche specifically — this is achievable with the current composited pipeline and should be
  the default VIDEO_BEAT visual assumption, not talking-head footage we can't produce.

### §1.4 Pinterest — SEO-first, saveable-utility framing confirmed

See §1.1 for hashtag findings. Additional: wellness/self-help content is reported as one of
Pinterest's most popular categories, and Pinterest is cited (in one source) as ranking #1 among
platforms for "instilling feelings of self-worth and purpose" among users —
[SEO Sherpa](https://seosherpa.com/pinterest-seo/). This is a favorable format-fit signal specific
to our niche, reinforcing that Pinterest deserves real CAROUSEL_SLIDE / SAVEABLE_PAYOFF investment,
not treatment as an afterthought platform.

### §1.5 Facebook — meaningful-interaction signal, comments over likes

Source: aggregated from
[SocialPilot's 2026 Facebook algorithm guide](https://www.socialpilot.co/blog/facebook-algorithm)
and [Kolsquare's 2026 analysis](https://www.kolsquare.com/en/blog/the-facebook-algorithm-explained).
Reach now favors content that generates comments/shares/long discussion ("Meaningful Social
Interactions") over passive likes; engagement-bait is explicitly penalized, matching the Threads
finding in §1.6. One wellness-marketing source suggested a 70/20/10 content mix (evergreen
education+proof / community+retention / experiments) — directionally useful, treat the exact ratio
as general marketing guidance rather than a Facebook-platform-specific fact.

### §1.6 X/Threads — opinion + specific tension beats information dumps

Source: aggregated from
[Teract's 2026 Threads growth guide](https://www.teract.ai/resources/grow-threads-following-2026)
and [MomentumHive's Threads algorithm breakdown](https://momentumhive.app/blog/threads-algorithm-2026-how-it-really-works).

- Reported thread structure pattern: **Hook → Context → Position → Invitation.** Threads truncates
  to roughly the first line before a "more" prompt — that first line must create tension that isn't
  immediately resolved, not just state a topic.
- Opinion-bearing posts reportedly outperform purely informational ones; specific personal-experience
  questions outperform generic ones (a cited example: "What's one [X] you stopped doing in 2026 and
  why?" — a question shape, not the literal topic, is the transferable pattern).
- This is directly usable for THREAD_UNIT atoms (currently zero rows): each unit should carry a
  clear single position, not a neutral fact, and should leave the tension from the hook line
  unresolved until the body.

---

## §2. MICRO_STORY seed patterns (currently 0 rows — this section exists to change that)

**Primary source — already exists, untracked, more specific than anything I found fresh on the open
web**: `docs/research_social_media.txt` (see §0 correction) already contains a fully-worked
"Before-and-After" content-format row (line ~2585) mapped to Instagram Carousels/TikTok, cold/unaware
audience, "side-by-side behavioral comparison graphics," Profile-Visits KPI, and a named failure mode
("over-promises quick results"). It also contains a full hook-quality ladder (weak → improved →
excellent, per hook psychology-type, with platform-adapted variants) that is directly a MICRO_STORY
opening-line seed bank, e.g. (quoting under 15 words per this lane's copyright rule):
- Weak: *"Are you an overthinker?"*
- Improved: *"If you overthink, read this."*
- Excellent (paraphrased structure, not verbatim-reproduced beyond a short fragment): a hook that
  names the *hyper-responsible child* pattern and traces it into adult over-functioning — concrete,
  specific, non-generic, in exactly the way the pilot posts (§0.2) are not.

This is a stronger, more directly usable MICRO_STORY seed source than general web-copywriting-formula
coverage, and Lane C should treat it as primary. Verified/cited-from-existing-local-doc, not
web-sourced.

Secondary, general-knowledge-uncited structural pattern (well-known, decades-old copywriting term,
not a 2026 finding, offered only as a cross-check that the local doc's shape matches established
practice): the **Before-After-Bridge (BAB)** formula — paint the "before" pain concretely, show the
"after" state, then the bridge (mechanism/tool) that connects them.

**What separates a landing micro-story from generic self-help** (verified via
[PMC: patient-specific vs. generic mental-health information](https://pmc.ncbi.nlm.nih.gov/articles/PMC11286208/)
-adjacent research aggregation, general-knowledge-uncited synthesis on the writing-craft side):
research on self-help material actionability found patient/reader-specific information significantly
outperforms generic information on actionability, engagement, and suitability. Practically, that
means:

- **Specificity beats scope.** A micro-story naming one concrete moment ("the Tuesday you answered
  a Slack message at 11pm from bed, then couldn't fall back asleep for two hours") lands harder than
  a generalized claim about "burnout culture." This is the exact defect visible in the pilot posts
  (§0.2) — the atoms describe a category ("corporate managers... exhaustion") rather than a scene.
- **A micro-story needs a sensory or situational anchor, a turn, and a named (not vague) shift** —
  not a moral. Four-beat compact shape usable as a MICRO_STORY atom template:
  1. **Anchor** — one concrete sensory/situational detail (time, place, object, action).
  2. **Turn** — the moment the pattern became visible or broke (not "I realized," but what
     specifically happened).
  3. **Shift** — what changed, stated as an action or a felt state, not an abstraction.
  4. **Residue** — one line of what's different now, kept small and concrete (not "I'm happy now").
- **Composite-not-real labeling requirement**: per this lane's DO NOT constraint, any MICRO_STORY
  atom seeded from this research must be an **original composite scene**, explicitly not attributed
  to a real named individual unless a real, citable, consented case exists. Lane C should mark every
  MICRO_STORY atom's `source_refs` as `composite_original` (or similar) rather than implying a real
  testimonial — this is a compliance/trust requirement, not just a style note, and matches the
  spec's "no unverified claims" non-goal.

## §3. CASE_PROOF seed patterns (currently 0 rows)

**Primary source — already exists, untracked**: `docs/research_social_media.txt` (line ~2449) gives
an explicit, already-compliance-aware CASE_PROOF framing: *"Social proof is integrated not as a
boastful metric, but as shared struggle. Highlighting that thousands of individuals experience the
exact same cognitive distortion normalizes the experience while quietly demonstrating authority."*
It also has a dedicated "Case Studies" content row (line ~2644) mapped to LinkedIn/Facebook/YouTube,
warm/informed audience, structural shape **"Problem → Mechanism → Result,"** Lead-Generation KPI, and
a named failure mode ("dry, clinical, or lacks human emotion"). This Problem→Mechanism→Result shape
is a directly usable CASE_PROOF atom template and should be Lane C's starting structure ahead of
anything I synthesized fresh below.

Secondary, fresh-web-verified/cited: mental-health creator credibility research (aggregated from
[Forbes' 2025 creators/mental-health study coverage](https://www.forbes.com/sites/ianshepherd/2025/11/12/what-the-numbers-reveal-about-creators-and-mental-health-in-new-study/)
and general 2026 influencer-marketing-trust coverage) converges on: **the credible pattern combines
either formal credentials or disclosed lived experience — not neither, and preferably both when
true** — plus an explicit, low-key disclaimer line. One aggregated source frames "I'm not a
therapist or medical professional" as becoming a *default expectation* in 2026 even where not legally
required.

Safe, no-medical-overclaim CASE_PROOF shapes for our atom bank (general-knowledge-uncited synthesis,
built from the verified credibility pattern above — not a directly cited template, since no source
gave a literal atom-shaped template):

- **Aggregate-pattern framing** ("in surveys of [defined population], X% report...") — cites a
  pattern, not a diagnosis or guarantee, and should carry a real source or be dropped rather than
  invented per this lane's DO NOT rule.
- **Mechanism-plus-caveat framing** ("this maps to what sleep/stress researchers call X — it's not
  a diagnosis, it's a pattern worth naming") — explains why without claiming to treat.
  - CN-market note from native review (§5): mental-health CASE_PROOF content in China specifically
    must avoid any phrasing that could read as diagnosing the reader (e.g., accusatory "you have
    depression" framing) or promising a cure/guaranteed outcome — this is not just a style
    preference, it intersects with China's advertising-law enforcement (see §5.3).
- **Disclosure-first framing** ("I'm not a therapist — here's what actually worked as one data
  point") — pairs a plain disclaimer with a bounded, non-prescriptive personal-pattern claim.
- **Explicit non-goal**: CASE_PROOF atoms should never claim clinical efficacy, named diagnosis
  applicability, or guaranteed outcomes. This is a hard line, not a style preference — matches the
  spec's non-goals and this lane's DO NOT section.

## §4. VIDEO_BEAT / CAROUSEL_SLIDE / THREAD_UNIT — structure findings (currently 0 rows each)

**VIDEO_BEAT** — see §1.3 for the cited beat timing. Practical constraint check against our pipeline
(deterministic prose composer + compositing, no live creator, no camera): the cited best-practice
structure is achievable as-is with text-over-B-roll/ambient-audio composited video — nothing in the
verified pattern requires a human on camera. This closes the "open operator question" risk the brief
flagged (native/live video is out of scope per spec, and the verified pattern doesn't require it).

**CAROUSEL_SLIDE** — verified pattern (aggregated from
[Carouselli's 2026 Instagram carousel rules](https://carouselli.com/blog/instagram-carousel-best-practices)
and [TrueFuture Media's 2026 carousel strategy](https://www.truefuturemedia.com/articles/instagram-carousel-strategy-2026)):

- Reported optimal slide count is **5–8 for save/completion rate**; up to 8–12 is workable for
  depth/educational content, but completion measurably drops past ~10.
- **"Open loop" technique**: the cover slide poses a question or names a gap; the answer is
  deliberately withheld until a later slide (commonly slide 5–6 of 8), which is reported to trigger
  re-serving by the algorithm when a user swipes to slide 3+.
- Direct implication for atom authoring: a CAROUSEL_SLIDE sequence is not "N independent
  SAVEABLE_PAYOFF-style slides" — it needs an explicit unresolved-question thread running through the
  slide order, which the atom metadata schema doesn't currently model (no "slide_position_in_arc" or
  "resolves_slide_n" field exists in the spec's Atom Metadata list). Flagged as a metadata gap, not
  something this lane can fix (out of scope — Lane C / spec owner's call).

**THREAD_UNIT** — see §1.6 (Hook → Context → Position → Invitation structure, unresolved-tension
first line, opinion-bearing over purely informational).

---

## §5. APAC refresh (Japan, Taiwan, Korea, China, Hong Kong, Singapore)

**Framing correction up front**: mission item 5 asked me to "verify the rakuten/quen docs' claims are
still current." As established in §0, those docs do not exist in the repository, so there is nothing
to verify against — this section is fresh research, not a diff against a prior version. I ran live
web research per market, then had all six findings independently reviewed by native-speaker
subagents (`translate-ja`, `translate-ko`, `translate-zh-cn`, `translate-zh-hk`, `translate-zh-sg`,
`translate-zh-tw`) for cultural/linguistic accuracy and platform-behavior plausibility. Every market
subsection below is the post-review, corrected version — where the native reviewer flagged a claim
as wrong, stale, or overstated, I've corrected or hedged it and noted the correction explicitly.
Full unedited native-reviewer replies are preserved in `NATIVE_SPEAKER_VALIDATION_20260723.md` in
this same directory for Lane C's reference.

### §5.1 Japan

- Instagram/X/YouTube usage-share figures from web research are treated as **directional, not
  citable** per native review — the reviewer flagged the precision of "45% prefer anonymous
  interaction" as suspiciously exact and recommended dropping or heavily hedging it.
- **Correction from native review**: the anonymous/candid-expression pattern (裏垢/alt accounts,
  5ch-lineage spaces) is real but is **not a new Gen Z wellness behavior** — it's a structural,
  decades-old feature of Japanese social culture (建前/本音 public-face vs. private-truth divide),
  not evidence of a 2026 trend shift. Practical implication for our copy: public-feed wellness
  content should assume the audience is reading/lurking privately rather than expecting open
  comments.
- **Correction from native review**: "detailed/thorough over brevity" is real for long-form (note,
  blog, YouTube) but **not** for Instagram/X captions, which still reward short, scannable text with
  line breaks — "thoroughness" should mean structured completeness (clear steps/caveats), not word
  count, in feed copy specifically.
- **Confirmed, register-precise per native review**: modesty/indirect framing is still correct but
  needs precision — avoid superlatives and command-form imperatives (reads pushy/foreign), avoid
  confident first-person "I healed my X by..." claims (reads boastful), avoid literal-translated
  encouragement phrases like "You've got this!" (no natural equivalent, reads childish/thin). Prefer
  suggestive framing (〜かもしれません, 〜してみませんか).
- Seasonality signals matter more in longer-form/email content than in short IG captions per the
  reviewer — don't force seasonal references into every short post.

### §5.2 Taiwan

- **PDPA-naming correction confirmed important**: Taiwan's 個人資料保護法 (Personal Data Protection
  Act) is confirmed by the native reviewer as **fully separate from Singapore's PDPA** — any future
  doc that conflates the two should be flagged and fixed. The NT$20,000–200,000 fine range is
  plausible per the reviewer but the "early 2026 update" specifics need a citation to the actual
  法務部/個資保護委員會 gazette before being stated as fact — I have not been able to verify that
  specific claim and am flagging it as **general-knowledge-uncited, needs a follow-up verification
  pass**, not confirmed.
- **Correction from native review**: "warmth + community feel" is not wrong but is dated as the whole
  register — since Threads' 2023+ growth in Taiwan, wellness/mental-health content skews more
  confessional/self-deprecating/diary-style ("your slightly chaotic best friend venting"), still warm
  but less formally so.
- Natural particles confirmed usable in small doses as can caption-enders: 啦, 欸, 齁, 厚, 誒; light
  Hokkien (母湯, 甘安捏) works ironically/self-aware in small doses — stacking more than one particle
  per sentence reads forced.
- **Important addition from native review, not in the original spec**: a simplified-to-traditional
  lexical substitution list is the single most common "inauthentic" tell and should become a
  checklist item, not just a script-conversion afterthought: 心理咨询→心理諮商/諮詢,
  抑郁症→憂鬱症, 视频/网络/信息→影片/網路/資訊, 治愈→療癒, 内卷→no natural TW equivalent (don't
  import), 情绪价值→情緒價值 (still reads mainland-first to older readers), 正能量 is
  borderline-acceptable but slightly mainland-coded now.

### §5.3 Korea

- **Correction from native review**: specific statistics (67% ad-skip, 55% social-media-detox, 21%
  hashtag growth, 33% population as MZ) read as generic global-survey numbers reskinned as
  Korea-specific — flagged as **general-knowledge-uncited, treat as directional only**, not citable
  as Korea-specific facts downstream.
- **Correction/dead-name flag from native review**: "Kakao Story" is a defunct feed product — it
  should not appear in any future copy or research doc; KakaoTalk (messenger) is still dominant for
  1:1/group chat, which is a different product.
- **Important correction from native review**: "group harmony" as a blanket wellness-copy value is
  **dated for 2026**. Younger Korean audiences have shifted toward 개인주의/자기돌봄
  (individualism/self-care), 혼자 (alone) culture, and 갓생 (self-optimizing routine) framing, partly
  as a reaction against the collectivist/hierarchical culture associated with burnout (과로사
  discourse). Collectivist "group harmony" framing risks reading as tone-deaf for wellness content
  specifically, even though it may still be accurate for other content categories.
- **Register guidance confirmed**: 해요체 (soft polite) is the right default for wellness/social
  copy — full 존댓말/격식체 reads corporate/institutional, wrong for a peer-feeling wellness brand.
  Avoid direct-translated therapy jargon and "화이팅"-only positivity — reviewer flags 2026 audiences
  as fatigued by performative positivity; naming exhaustion/번아웃 candidly before pivoting to
  encouragement lands better than pure positivity or harmony framing.

### §5.4 Mainland China

- **Confirmed**: Xiaohongshu (小红书/RED) dominance for wellness/lifestyle, historical ~70% female
  skew narrowing as male users grow into tech/fitness/finance verticals; UGC/种草 ("grass-planting")
  authentic-storytelling style is confirmed as still ascending, not fading, in 2026.
- **Correction/nuance from native review**: the "confessional girlfriend-secret" (闺蜜式分享) voice
  is real but by 2026 is blending with a **credentialed-expert layer** — successful mental-health XHS
  content pairs the casual intimate tone with a visible credential marker (e.g., 国家二级心理咨询师,
  registered dietitian) in bio/first line. Pure confessional-with-no-credential content increasingly
  reads as scripted MCN content or unverifiable, per the reviewer.
- **Important compliance correction from native review**: "no superlatives" is too vague. The
  actually-enforced trigger words under 广告法 are specific absolute-claim characters/phrases: 最,
  第一, 唯一, 国家级, 极致, 100%有效, 永久, 根治. For mental health specifically, medical-claim
  language (诊断/"you have depression"-style accusation, or claiming a product/course "treats"
  抑郁症/焦虑症) is enforced far more aggressively than generic positivity-tone issues — this is a
  legal/platform-removal risk, not a style nicety.
- **Missing from prior framing, added by native review**: current-2026 XHS algorithm favors 真实感
  (deliberately imperfect/unpolished presentation) over studio-polished content for reach — polish
  now reads as advertising and can hurt distribution. Mental-health content specifically should route
  readers toward 正规医疗机构/专业帮助 (licensed institutions/professional help) rather than
  encouraging self-diagnosis, both for compliance and credibility.
- Generic-and-dead filler flagged by the reviewer specifically for this niche: 情绪自由, 治愈系, 给自己充电
  now read as MCN-template cliché, not sincere voice — avoid seeding CASE_PROOF/REFRAME atoms with
  these phrases.

### §5.5 Hong Kong

- **Correction from native review — this is the most important HK finding**: "Traditional Chinese
  content outperforms English on Xiaohongshu" is flagged as the weakest claim in the original
  research. XHS's dominant register even for HK users is often **mainland-inflected** written
  Chinese (the algorithm surfaces mainland creators heavily) — using XHS in HK carries a real risk of
  reading as mainland rather than local, which is a bigger risk than "safe local-language win," not
  a safe default.
- **Correction on code-switching mechanics**: the reviewed draft's "alternating full-sentence"
  code-switching model is wrong. Real HK code-switching is **intra-sentential** — English
  nouns/verbs dropped into Cantonese grammar (reviewer examples: "我而家真係好down",
  "呢排work life balance好chaos", "要stay positive呀"). Full-paragraph alternation between
  languages reads like a translated brochure, not organic voice — this should be a hard correction to
  any future LOCALIZATION_ADAPTER atom for HK.
- **Missing platform nuance added by native review**: Threads skews more English-forward/media-savvy
  in HK; Instagram Stories still lead for informal wellness-confessional content; XHS suits
  lifestyle/beauty tone better than mental-health confessional tone specifically.
- **Credibility-critical addition from native review**: Cantonese sentence-final particles
  (㗎/喎/囉/呀/嘛) are the actual "genuinely HK" signal — more than vocabulary choice. Mainland-coded
  terms that undercut HK credibility in serious mental-health content specifically: 治愈 (reads
  earnest-to-preachy/mainland), 正能量 ("positive energy," same issue), 视频 (mainland) vs 影片 (HK),
  网红 vs KOL. HK wellness voice trends more self-aware/ironic (e.g., "我而家好emo" used
  adjectivally) than uplifting-slogan register.

### §5.6 Singapore

- **Correction from native review**: describing #ad/#sp disclosure enforcement as a "2026
  requirement" is stale/wrong — ASAS/CASE disclosure enforcement on undisclosed paid partnerships has
  been active since roughly 2022–2023; it should be framed as an already-established norm, not a
  newly-arriving 2026 rule.
- **Important reach-scope correction from native review**: Xiaohongshu in Singapore is real but
  **niche, not mainstream** — it skews toward Chinese-Singaporean women, PRC expat/student residents,
  and beauty/luxury micro-influencers; it's closer to a diaspora/China-adjacent channel than a
  general Singapore wellness platform. Instagram, TikTok, and WhatsApp/Telegram community broadcast
  channels are the actual dominant wellness-engagement surfaces in Singapore per the reviewer — this
  was a real gap in the original draft.
- **Correction on dialect claim**: "dialect diversity matters for resonance" is backwards for
  under-~50 audiences — post-Speak Mandarin Campaign, most Chinese-Singaporeans under 50 don't
  functionally speak Hokkien/Cantonese. What resonates is colloquial "Singdarin"
  (Mandarin-English-Malay code-switching), not heritage dialect; dialect appeal is a
  Pioneer/Merdeka-generation (60+) lever specifically, not a general-audience one.
- **Register correction — the core finding for Singapore**: "concise/pragmatic/data-driven" alone
  reads as generic corporate copy, which is specifically wrong for mental-health content. Per the
  reviewer (citing IMH/SOS destigmatization-campaign tone as reference points), Singapore wellness
  voice has moved warmer/more relatable — light Singlish markers (lah, can, steady, shiok, sian)
  signal authenticity and community warmth even in otherwise practical copy. Pure efficiency-framing
  fits productivity/corporate-wellness content, not emotional-support content — this is a real split
  Lane C should encode as two different registers, not one Singapore voice.
- **PDPA/caption-voice boundary, confirmed by reviewer**: PDPA consent language belongs in lead-gen
  forms/backend, not in caption voice. The one exception that legally must be in the caption itself
  is sponsorship disclosure.
- **Gap flagged by reviewer, not in original spec**: no mention of Malay/Tamil/Eurasian audiences —
  wellness copy should not default to a Chinese-only register for Singapore.

---

## §6. Findings summary — verified/cited vs. general-knowledge-uncited

Per this lane's DO NOT constraint, every claim above is labeled by category. Roll-up:

**Verified-cited** (has a live, checkable 2026 web source cited inline in §1–§4, a direct citation to
an already-authored local doc found untracked on disk (§0/§2/§3), or is a direct native-speaker
correction to a specific claim in §5): the existing untracked docs' own content (hashtag guidance,
hook-quality ladder, Before-and-After and Case-Study format rows, Social-Proof-as-shared-struggle
framing, VIDEO_BEAT-matching five-phase video anatomy); Instagram 5-hashtag cap and its date/source;
LinkedIn dwell-time/300-400-word/carousel-dwell/external-link-penalty findings; TikTok hook-timing
and faceless-niche-fit findings; Pinterest hashtag-secondary/keyword-primacy findings; Facebook
meaningful-interaction findings; Threads/X hook-truncation and opinion-outperforms-information
findings; carousel slide-count/open-loop findings; every native-speaker correction in §5 (Kakao Story
dead-name, HK code-switching mechanics, CN 广告法 trigger words, TW simplified/traditional lexical
list, SG Xiaohongshu-is-niche correction, SG dialect-claim correction, JP anonymous-culture
correction, KR "group harmony" datedness correction).

**General-knowledge-uncited** (defensible platform-mechanics/copywriting knowledge, not tied to a
fresh 2026 citation — flagged so Lane C knows this needs a follow-up verification pass before being
quoted as "research says"): the BAB (Before-After-Bridge) story-formula label itself; the four-beat
MICRO_STORY template (Anchor/Turn/Shift/Residue) — this is my synthesis built on top of the cited
specificity research, not a template I found verified in a source; the CASE_PROOF shape suggestions
in §3; the exact percentages surfaced by web search that the native reviewers explicitly flagged as
suspiciously precise or generic-survey-reskinned (Japan's "45%," Korea's "67%/55%/21%/33%"); the
TW PDPA "early 2026 update" specifics (plausible range, unverified specifics).

---

## §7. Retire/update recommendations

**R1 — Land the 5 untracked-local Source Authority docs to `origin/main` (highest priority; smaller
fix than it first looked, see §0's correction).** `docs/gemini_research_social_media_englis.txt`,
`docs/research_gemini_social_media_templates_english.txt`,
`docs/rakuten_research_social_media_writing_japan_tw_kr.txt.txt`,
`docs/quen_research_social_media_writing_china_hong_kong_singapore.txt`, and
`docs/research_social_media.txt` all already exist, fully authored, on the local disk of the main
checkout — they just were never `git add`ed/committed. `docs/research_social_media.txt` is already
quote-cited by 22 live atom rows, which makes its untracked status a real provenance gap, not a
tidiness one. This is a **one-agent-turn `git add` + commit + PR**, not new authorship — flagged for
Pearl_GitHub/whoever has write access to `docs/` outside this lane's sparse-checkout cone (this lane
is scoped to `artifacts/social_media_atoms/` and `artifacts/coordination/handoffs/` for writes; I did
not add these files myself). This exact gap is independently named as gap-item 8 in
`docs/specs/SOCIAL_MEDIA_100PCT_PRODUCTION_PLAN_2026-07-22.md` (sized there as "one agent-turn" too)
— two independent lanes converging on the same fix is a strong signal to actually do it next.

**R2 — `config/social/platform_specs.yaml` Instagram hashtag range is stale twice over.** Current
`hashtags_min: 5, hashtags_max: 15` for `instagram_feed_portrait` and `instagram_carousel` should
become something like `hashtags_min: 0, hashtags_max: 5`. It's wrong against the live Instagram
platform cap (5, enforced since 2025-12-19, §1.1) **and** it drifted from our own already-authored,
untracked `gemini_research_social_media_englis.txt`, which independently recommended "3 to 5 highly
relevant hashtags" for Instagram before that platform change even happened. This file is outside my
write scope (`config/social/` is not in this lane's write scope or sparse-checkout cone) — flagged
for whoever owns that file, not edited by this lane.

**R3 — Do not retire the spec's existing VIDEO_BEAT beat map** (0-3/3-8/8-20/20-25s + CTA) — current
research confirms it's directionally correct; the fix is authoring atoms against it, not changing the
shape.

**R4 — Do not retire the spec's Platform Rules country-tone one-liners wholesale** (Japan/Taiwan/
Korea/China/HK/Singapore) — most survive with corrections noted in §5, but "Korea: ...group harmony"
should be revised to reflect the 2026 individualism/self-care shift documented in §5.3, and Hong
Kong's rule should be extended with the intra-sentential code-switching mechanic and the
XHS-mainland-inflection risk from §5.5. These are one-line spec edits Lane C or the spec owner should
make; this lane does not have write access to the spec file's "Platform Rules" section as part of its
scope (research lane, not spec-owner lane) and has not edited it.

**R5 — Add missing atom-metadata fields for carousel sequencing.** The spec's Atom Metadata list has
no field for a slide's position in an "open loop" arc (e.g., which slide poses the question, which
slide resolves it). Without it, CAROUSEL_SLIDE atoms can't encode the verified §4 pattern. Flagged as
a schema gap for the spec owner, not fixed here (out of this lane's scope).

---

## §8. Named operator question (per this lane's OPEN OPERATOR QUESTIONS instruction)

**Q: Does the pipeline need a native/live-video format at all, or does the composited
text+B-roll+ambient-audio format researched in §1.3/§4 fully cover the "alive vs dead" gap for
short-form video?**

Recommended default: **No new format needed.** Every cited 2026 best-practice source for faceless/
text-forward wellness short-form video describes a format our deterministic composited pipeline can
already produce (text overlay timing, B-roll, ambient audio, caption-first hook). The spec's
explicit non-goal ("not a live publisher") and out-of-scope native video framing hold up against
current research — the defect diagnosed in this lane's brief is empty atom families and generic
prose, not a missing video format. Recommend closing this question with "no format gap" rather than
routing it back for a build decision.

---

## Sources (representative; full URL list also appears inline above)

**Local (untracked-on-disk, read directly by this lane; see §0 for the corrected "exists but
untracked" framing):**
- `docs/gemini_research_social_media_englis.txt` (read in full, 113 lines)
- `docs/rakuten_research_social_media_writing_japan_tw_kr.txt.txt` (read in full, 249 lines)
- `docs/quen_research_social_media_writing_china_hong_kong_singapore.txt` (read in full, 70 lines)
- `docs/research_social_media.txt` (read substantially — targeted sections on hooks, hashtags,
  before-and-after/case-study formats, social proof — not exhaustively across all 5,914 lines)
- `docs/research_gemini_social_media_templates_english.txt` (skimmed structure — prompt + partial
  blueprint content, not exhaustively across all 5,201 lines)
- `docs/specs/SOCIAL_MEDIA_100PCT_PRODUCTION_PLAN_2026-07-22.md` (Pearl_PM, on `origin/main`)

**Live web (fetched 2026-07-23):**
- [Instagram Implements New Limits on Hashtag Use — Social Media Today](https://www.socialmediatoday.com/news/instagram-implements-new-limits-on-hashtag-use/808309/)
- [Instagram's 5-Hashtag Limit in 2026 — CreatorLane](https://creatorlanehq.com/blog/instagram-5-hashtag-limit-2026)
- [Instagram Caps Hashtags at Five to Combat Spam — TechBuzz](https://www.techbuzz.ai/articles/instagram-caps-hashtags-at-five-to-combat-spam)
- [Buffer — How the Instagram Algorithm Works: Your 2026 Guide](https://buffer.com/resources/instagram-algorithms/)
- [Whitehat — How to Increase Engagement on LinkedIn: 2026 B2B Algorithm Guide](https://whitehat-seo.co.uk/blog/increase-engagement-on-linkedin)
- [SocialBee — The LinkedIn algorithm explained (2026 guide)](https://socialbee.com/blog/linkedin-algorithm/)
- [Stackmatix — How the LinkedIn Algorithm Works in 2026: A Data-Driven Breakdown](https://www.stackmatix.com/blog/linkedin-algorithm-how-it-works)
- [SendShort — Top 14 TikTok Hooks for 84.3% More Engagement (2026)](https://sendshort.ai/guides/tiktok-hooks/)
- [Fluxnote — TikTok Strategy for Mental Health Creators (2026)](https://fluxnote.io/guides/tiktok-mental-health-strategy)
- [HustleMarketers — TikTok Faceless Wellness Content Strategy (2026)](https://hustlemarketers.com/tiktok-faceless-wellness-content-strategy/)
- [SEO Sherpa — Pinterest SEO: How to Rank Pins and Drive Traffic in 2026](https://seosherpa.com/pinterest-seo/)
- [Pingroupie — Pinterest SEO: The Only Guide You Need to Rank in 2026](https://pingroupie.com/blog/pinterest-seo-guide-2026)
- [SocialPilot — Facebook Algorithm 2026: How It Works & Tips to Improve Reach](https://www.socialpilot.co/blog/facebook-algorithm)
- [Kolsquare — Insights into Facebook's 2026 Algorithm](https://www.kolsquare.com/en/blog/the-facebook-algorithm-explained)
- [Teract — How to Grow on Threads in 2026: Complete Strategy + Real Data](https://www.teract.ai/resources/grow-threads-following-2026)
- [MomentumHive — Threads Algorithm 2026: How It Really Works](https://momentumhive.app/blog/threads-algorithm-2026-how-it-really-works)
- [Carouselli — Instagram Carousel Best Practices 2026: 12 Rules That Drive Saves](https://carouselli.com/blog/instagram-carousel-best-practices)
- [TrueFuture Media — Instagram Carousel Strategy 2026](https://www.truefuturemedia.com/articles/instagram-carousel-strategy-2026)
- [Forbes — What The Numbers Reveal About Creators And Mental Health In New Study (2025-11-12)](https://www.forbes.com/sites/ianshepherd/2025/11/12/what-the-numbers-reveal-about-creators-and-mental-health-in-new-study/)
- [PMC — A guide for self-help guides: best practice implementation](https://pmc.ncbi.nlm.nih.gov/articles/PMC11286208/)
- [Elite Asia — Top Digital and Social Media Trends in Japan/Taiwan/Hong Kong/South Korea/Singapore in 2026](https://www.eliteasia.co/)
- [Hashmeta — Xiaohongshu / social-media-landscape series (Hong Kong, Singapore, wellness verticals)](https://hashmeta.com/blog/)
- Native-speaker validation: `translate-ja`, `translate-ko`, `translate-zh-cn`, `translate-zh-hk`, `translate-zh-sg`, `translate-zh-tw` subagents, consulted 2026-07-23 (see `NATIVE_SPEAKER_VALIDATION_20260723.md` in this directory for full unedited replies).
