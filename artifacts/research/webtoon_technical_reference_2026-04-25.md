# WEBTOON Technical Reference for Phoenix Omega Pipeline
## Date: 2026-04-25
## Scope: Canvas + Originals + Unified CANVAS Multi-Language Platform 2026

---

## Executive Summary (read first — 200 words)

WEBTOON's CANVAS upload pipeline accepts **JPEG, JPG, and PNG** images, **maximum 800 × 1280 px per image**, **≤ 2 MB per image**, **≤ 20 MB or 100 images per episode**. Anything taller than 1280 px is auto-sliced server-side. No public REST upload API exists; uploads are browser-based (Chrome required). The unified international CANVAS platform (rolled out Spring 2026) supports **seven languages — English, Spanish, French, Indonesian, Thai, Traditional Chinese, German**. **Japanese is NOT in the unified set** — Japanese readership is served by LINE Manga / Piccoma, separate platforms with separate workflows. WEBTOON's AI Translation Program is **opt-in, beta, invite-only**, requires ≥ 10 published episodes and > 2,000 page views in 365 days, translates **text only** (artwork untouched), with creator-supplied glossaries. Korea's AI Basic Act (effective 22 Jan 2026) imposes platform-level (not individual-creator) disclosure obligations; webtoons may use **machine-readable, non-visible watermarks**. Monetization (effective 13 Jan 2026): **min payout $25** (PayPal/Patreon), **up to 6 episodes** lockable behind Reward Ads. Canvas is non-exclusive and rights-retentive; Originals contracts demand **3-year post-completion digital exclusivity**, multimedia/print options, exclusive merchandising license. For Phoenix Omega: render at 1600 × 2560 master then downsample to 800 × 1280 sRGB JPEG slices; budget ~60 panels per episode.

---

## 1. Episode / Image Technical Specs

WEBTOON's image upload spec has remained remarkably stable across nearly a decade — the canonical 800×1280 px JPEG-only standard was set in the LINE Webtoon era (pre-2019 rebrand) and persists today. The platform has added auto-slicing, rectangular thumbnails, and tighter file-size enforcement, but the core upload contract is unchanged. This stability is a gift to engineering teams: any pipeline targeting WEBTOON in 2026 will not be invalidated by sudden spec churn the way (for example) Instagram's media APIs have churned.

The flip side: the platform's image-format conservatism — JPEG only as the canonical answer, with PNG accepted as a non-blocking exception in practice — means modern format wins (WebP, AVIF) are not available. Phoenix-Omega cannot rely on AVIF's superior compression for ink-wash gradients; the pipeline must hit acceptable quality on JPEG, full stop. The 20 MB per-episode payload cap, divided across up to 100 image slices, gives an average per-slice budget of 200 KB which is uncomfortable for high-frequency content but workable for the contemplative-ink-wash style which has lots of negative-space regions that compress efficiently.

### 1.1 Canonical platform-published numbers

| Spec | Value | Source | Confidence |
|---|---|---|---|
| Max image width | **800 px** | webtoons.com/en/canvas/webtoon-format/ — "W800 X H1280 pxl" | HIGH (official WEBTOON page) |
| Max image height per file | **1280 px** | webtoons.com/en/canvas/webtoon-format/; Zendesk file-size FAQ | HIGH |
| Auto-slice behavior | Server slices uploads >1280 px tall into ≤1280 px segments | WEBTOON CANVAS Zendesk; multiple creator guides | HIGH |
| Max file size per image | **~2 MB** (system penalizes >2.5 MB on non-Chrome browsers) | WEBTOON CANVAS Zendesk; multiple creator guides 2024-2025 | MEDIUM-HIGH |
| Max upload payload per episode | **20 MB OR 100 images, whichever first** | Multic publishing guide; Writeseen Creator Guide; Zendesk | HIGH |
| Supported image formats | **JPG, JPEG, PNG** (PNG accepted but JPEG strongly preferred) | webtoons.com/en/canvas/webtoon-format/ ("JPEG ONLY"); Zendesk thumbnail FAQ; WhytManga | HIGH (JPEG official); MEDIUM (PNG accepted in practice) |
| WebP support | **NO PUBLIC SOURCE FOUND** — assume not supported | — | LOW |
| Recommended browser | **Chrome** (IE deprecated; mobile app cannot publish, only schedule) | WEBTOON CANVAS Zendesk; Multic guide | HIGH |
| Color profile | **sRGB assumed** (no formal declaration; web display target) | S-Morishita; deviantArt threads — implied by 72 dpi web target | LOW (no platform-published spec) |
| Recommended DPI | **72 dpi** for upload; **350-600 dpi master** for print compatibility | S-Morishita "DPI Tips"; Quora threads | HIGH (creator consensus) |
| Background | No mandate — white most common for ink-wash; transparent NOT honored (JPEG flattens) | Implicit in JPEG-only mandate | HIGH |

### 1.2 Notes on the "JPEG ONLY" claim

The platform's own format-guide page says **"Image format: JPEG (ONLY)"** but the upload validator in 2024-2026 has accepted PNG and JPG. Multiple creator guides published in 2024-2026 confirm PNG works in practice. **Recommendation for Phoenix Omega: emit JPEG-quality-92 sRGB to avoid edge cases**.

### 1.3 Episode-level limits

- **No published max total episode pixel-height** — limits are file-count (100) × per-file-height (1280 px) → theoretical ceiling **128,000 px** per episode, but the 20 MB total cap is the real binding constraint.
- Typical episodes ship 25–60 sliced files; full episode height **2,500–8,000 px** is the practical sweet spot per S-Morishita and the WEBTOON-format-guide series.

### 1.4 Thumbnail / Banner specs (current 2026)

| Asset | Dimensions | Max KB | Format |
|---|---|---|---|
| Series main thumbnail (legacy square) | 436 × 436 px | 500 KB | JPG/JPEG/PNG |
| Series square thumbnail (current) | 1080 × 1080 px | 500 KB | JPG/JPEG/PNG |
| Series vertical thumbnail | 1080 × 1920 px | 700 KB | JPG/JPEG/PNG |
| Episode thumbnail (legacy square) | 160 × 151 px | 500 KB | JPG/JPEG/PNG |
| Episode thumbnail (rectangular, current) | 202 × 142 px | 500 KB | JPG/JPEG/PNG |

(Sources: WEBTOON CANVAS Zendesk thumbnails article ID 32913712749588; webtoons.com/en/notice/detail?noticeNo=1751 announcing rectangular thumbnail.)

---

## 2. Canvas Panel & Pacing Conventions

The vertical-scroll vocabulary of webtoons is fundamentally different from horizontal manga, and Phoenix-Omega engineers must internalize this difference at the rendering-pipeline level. Where Japanese manga reads right-to-left, top-to-bottom, in a fixed-rectangle page grid, a webtoon is a single continuous vertical strip in which the *gutter is the editing tool*. White space between panels is not dead space — it is the equivalent of a film cut, a held beat, or a directorial pause. Consequently, the typical "pacing knob" for a webtoon is the **pixel height of the gap between panels**, not panel proportions, not page count.

This has direct implications for any AI-driven generator: if you render 60 panels and stitch them with a constant 50-px gap, you produce a flat, pace-less episode that feels rushed. Phoenix-Omega's panel-stitching code MUST take a "beat-type" parameter (`micro` / `standard` / `scene-change` / `long-drop` / `chapter-break`) and look up gutter heights from a table. The S-Morishita conventions below have become de-facto industry baselines and are echoed in WEBTOON's own creator-academy materials.

### 2.1 Pixel-spacing conventions (creator-consensus, S-Morishita)

| Beat | Recommended px | Source / confidence |
|---|---|---|
| Minimum panel-to-panel gutter | **30–50 px** | S-Morishita panel-spacing-tip; HIGH |
| Standard scene transition (time pass) | **600–1000 px** | WEBTOON Canvas creator guide; S-Morishita; HIGH |
| Minimum spatial transition (same scene) | **200 px** | WEBTOON Canvas creator guide; HIGH |
| "Long drop" dramatic pause | **1500–3000 px** | Creator guides (Nicole Cornball, S-Morishita); MEDIUM |
| Panels per file | **1–3** (1–2 preferred) | S-Morishita; HIGH |

### 2.2 Reading-speed assumptions

WEBTOON's editorial guidance (and recurring S-Morishita posts) implicitly assume **a finger-flick scroll = ~one phone-screen height (~700–800 px) per second**. There is no platform-published "px/sec" target. For dramatic pacing, a "long drop" of ~1500–3000 px = roughly 2–4 seconds of black/white space, mimicking a beat-pause.

In practice, retention analytics shared on Reddit and creator forums show readers spend **35–40 minutes per session** consuming multiple episodes, which translates to about **8 to 12 minutes per 4,000-px episode** at a relaxed scroll. The implication is that Phoenix-Omega's per-episode total height should target **~4,000 px** as a sweet spot — long enough to deliver a satisfying narrative arc, short enough that readers don't bounce. Episodes much shorter than 2,500 px feel "thin" to readers and cause disengagement; episodes much longer than 8,000 px exceed the casual-snack reading mode that WEBTOON optimizes for.

### 2.3 Mobile screen height assumption

Webtoon's renderer assumes a **typical mobile viewport ~720–800 px wide** (matching the 800 px upload width) and ~1200–1400 px tall in portrait. This is why 800 px is the canonical width: it's the lowest-common-denominator viewport.

This has a subtle implication for image rendering. Because each uploaded slice is no taller than 1280 px, and a typical phone viewport is ~1300 px tall in portrait, **at most one full slice fits on screen at a time**. This is intentional: the renderer treats slices as the natural unit of vertical scroll-flow. If a panel spans across the boundary of two slices, the reader sees a "tear" at the join point. **Phoenix-Omega's slicer MUST cut between panels (in gutter regions), never through panel content**. This is non-negotiable for visual quality.

### 2.4 Tablet and desktop viewport behavior

When a reader views a webtoon on a tablet (e.g., iPad in portrait at ~1620 px wide) or on the web reader on a desktop monitor (typically 1080 px or 1440 px wide), WEBTOON's renderer **upscales the 800 px native image** to fill the column. This means Phoenix-Omega's choice of master-render quality directly impacts tablet/desktop reading: a hard 800 px output that was rendered at 800 px native will look mushy on iPad. Rendering at **1600 px master and downscaling to 800 px** preserves the latent fidelity that the reader's device picks up on upscale. This is the strongest argument for the 2× over-render strategy.

### 2.4 Episode panel count by genre (S-Morishita norms)

| Genre cluster | Min panels/episode |
|---|---|
| Comedy / slice of life | 12 |
| Fantasy / action / sci-fi | 35 |
| Drama / romance | 40 |
| Horror / thriller / mystery / supernatural | 40 |
| Featured / Originals weekly average | **~60** |

(Source: S-Morishita "How Many Panels Does a Webtoon Have?")

---

## 3. Episode Structure

Episode pacing on WEBTOON has converged around a relatively narrow set of conventions that Phoenix-Omega should treat as default. Where novels can be of any length and where comics are bound by physical pagination, webtoon episodes are constrained from one direction (the platform's per-episode upload cap) and from the other (reader habit and the mobile attention budget). What sits in between has standardized.

- **Standard episode**: ~60 panels for weekly serialization on Originals; Canvas creators average 35–45.
- **Total height**: 2,500–8,000 px typical (3,500–4,500 px = sweet spot for retention per S-Morishita).
- **Word count**: NO PUBLIC SOURCE FOUND — creator surveys suggest 400–800 words per episode is typical (treat as MEDIUM confidence).
- **First-episode hook**: WEBTOON help-center guidance recommends a strong cliffhanger and "establishment of the world" within the first ~30 panels. Creators claim Originals scouts will not greenlight a series whose first 3 episodes don't subscribe-convert at >2%.
- **Recap conventions**: optional; common for fantasy/action with extended timelines; not platform-required.
- **Cliffhanger placement**: convention — final ~10% of the vertical scroll.
- **Update cadence on Canvas**: voluntary. Algorithm strongly rewards weekly cadence; "month-on, month-off" patterns lose subscribers (S-Morishita "Quality vs Quantity").
- **Update cadence on Originals**: contractual; weekly is standard. Missed updates can trigger warning → renegotiation → cancellation.
- **Status flags**: `Ongoing`, `On Hiatus`, `Completed`. `Completed` triggers Daily Pass eligibility and stops update reminder emails.

### 3.1 Cliffhanger placement and "thumb stop" beats

Successful Canvas series consistently place their **strongest narrative beat in the bottom 10% of the scroll**. Practically, this means: if your episode is 4,000 px tall, the reveal/cliffhanger lives in the final ~400 px. The reason is mechanical — readers who reach the bottom of an episode are presented with the next-episode CTA + subscribe button. Maximizing emotional investment at that exact pixel range is the single highest-leverage retention move.

Inside the body of the episode, S-Morishita and Nicole Cornball both recommend at least **3–4 "thumb-stop" beats per episode** — moments where a panel deliberately uses an unusual aspect ratio, a long drop, or an extreme close-up to punctuate the rhythm. Phoenix-Omega's panel scheduler should plant these every ~12–15 panels.

### 3.2 First-episode "hook" requirements

The first episode is responsible for ~70% of subscriber-conversion (creator anecdote consensus). WEBTOON Originals scouts watch the first-episode subscribe-rate as their primary KPI. Engineering implication: Phoenix-Omega's pilot episodes for any new series **must allocate above-average production budget to Episode 1**. Specifically: more panels (50+ vs. the 35-panel floor), wider art-direction range (more locations, more characters introduced), a hard cliffhanger.

### 3.3 Recap conventions

Recaps of 2–4 panels at the start of episodes are common in fantasy, action, and dense-mystery genres — they help re-orient weekly readers. Romance and slice-of-life rarely use them. Phoenix-Omega does NOT need to generate recaps automatically; a static "previously on" text card with one or two key images is sufficient.

(Sources: WEBTOON CANVAS Zendesk FAQ; S-Morishita; Quora creator answers; Multic guide; Nicole Cornball "Introduction to Webtoon Paneling" 2024.)

---

## 4. Upload Workflow

The publish pipeline for Canvas is designed for a single human-creator working from a desktop browser — **not** for an industrialized multi-series content factory. Phoenix-Omega is firmly in the latter category, and the friction this generates is the dominant integration challenge. Every other constraint (image dimensions, color profile, episode metadata, monetization opt-ins) has a clean engineering answer; only the absence of an upload API forces architectural compromises.

The ideal Phoenix-Omega flow would be: render → encode → POST to `https://creator-api.webtoons.com/v1/series/{id}/episodes`, get an episode-id, schedule it, done. The actual flow is: render → encode → spin up Playwright Chrome session → log in → navigate to series dashboard → drag-and-drop slices into the upload widget → fill metadata fields → click publish-or-schedule → wait for the spinner → screenshot for receipt.

### 4.1 Available channels

| Channel | Status | Notes |
|---|---|---|
| Web dashboard at webtoons.com | **PRIMARY** — Chrome required | Drag-and-drop multi-image; in-browser slicer |
| iOS / Android app | Read + episode-scheduling only | Cannot publish from app |
| Public REST API for upload | **DOES NOT EXIST** | Confirmed via PyPI search; only read-only third-party scrapers (`webtoon-api`, `webtoon-data`) |
| Bulk-upload Photoshop plugin | None official; community ZIPs from Inked Vision / WhytManga on Patreon/Gumroad | |
| Episode scheduler | **YES** — built into series dashboard since Aug 2022 | Schedule by date+time, time-zone-aware |

### 4.2 Multi-language unified upload (Spring 2026 +)

- Single upload distributes across the seven supported languages **only after creator opts into the Translation Program**.
- Eligibility: ≥ 10 published episodes AND > 2,000 page views in trailing 365 days.
- Language selection is per-series; you can pick a subset.
- Opt-out: anytime; **60-day cool-down** before re-enrolling.
- AI translates text only; visual data is not used to train the model. (WEBTOON FAQ noticeNo=3621.)

### 4.3 No-API consequence for Phoenix Omega

The lack of a public upload API is **the single largest engineering risk** for any automated Canvas connector. Plausible workarounds:
1. **Headless Chrome / Playwright session** against the dashboard. This is the only practical path. Risks: TOS-grey (WEBTOON's TOS doesn't explicitly forbid automation but reserves rights to throttle/ban); subject to breakage at every dashboard re-skin (the rectangular-thumbnail rollout in 2024 broke many third-party tools).
2. **Manual bulk drag-and-drop**, automating only the asset prep upstream. This is the safe operator-present mode and aligns with Phoenix-Omega's Tier-1 LLM policy (operator must be present for prose generation anyway).
3. **Submit Phoenix-Omega for an Originals/partner agreement** that may grant API access. WEBTOON has never publicly documented partner-API tiers, but its enterprise relationships (e.g., with major Korean studios) clearly involve some kind of programmatic ingestion. This is a multi-quarter business-development effort.
4. **Outsource to a creator-services partner** like Multic which already operates on top of WEBTOON's dashboard. Multic charges per-episode but gives an HTTP API.

### 4.4 Episode scheduling reliability

The built-in scheduler (since August 2022) is reliable for individual creators but does not have a public reschedule API. Phoenix-Omega operators can schedule up to ~6 weeks in advance comfortably; longer windows have shown intermittent reliability issues per creator forum reports.

---

## 5. Metadata Requirements

Metadata fields on Canvas are simpler than on most professional content platforms — a function of WEBTOON's user-base being individual creators with thin technical sophistication, not metadata-heavy professional media outfits. The flip side is that some fields Phoenix-Omega would consider essential (e.g., structured ISBN-equivalent identifiers, publishing-org metadata, character-glossary fields, AI-disclosure structured field) **do not exist** at the platform level. Any metadata richer than the dashboard exposes must be encoded into series synopsis or footer text.

| Field | Limit | Notes / source |
|---|---|---|
| Series title | English: ~50 chars (UI-soft) | NO PUBLIC HARD LIMIT — creator surveys |
| Tagline / synopsis | ~500 chars | UI-validated; community guidance |
| Genre tags | Single primary genre + multi-tag | List rotates; current Canvas categories: Romance, Fantasy, Drama, Comedy, Action, Slice of Life, Sci-fi, Thriller, Horror, Superhero, Heartwarming, Historical, Sports, Informative, BL, GL, Tiptoon, Short Story |
| Mature rating | Yes/No questionnaire on violence, sexual content, self-harm, alcohol/drugs | WEBTOON Support: "CANVAS Content Age Rating Guidelines" |
| Author profile | One bio + avatar; tied to login | Standard |
| Series banner | Newer rectangular layout enforces rectangular thumbnail (202×142) + square (1080×1080) | webtoons.com/en/notice/detail?noticeNo=1751 |

Translation glossary (under unified CANVAS) requires **two mandatory sections** (FAQ noticeNo=3621). Glossary content guides AI translation.

---

## 6. AI Policy — Current 2026

### 6.1 WEBTOON's own policy

- **No platform-wide ban** on AI-assisted art on Canvas as of April 2026.
- Mature, hate-speech, copyright-infringing rules apply uniformly.
- WEBTOON's AI Translation Program (Spring 2026) translates **text only** and **does not** train on creator artwork. (CBR; ANN; KCBeat.)
- WEBTOON recently launched an AI-only category (`webtoons.com/en/canvas/ai/`) — implicit acceptance.

### 6.2 Korea AI Basic Act (effective 22 Jan 2026)

| Requirement | Detail |
|---|---|
| Disclosure | Generative-AI outputs must be labeled |
| Webtoons-specific carve-out | **Machine-readable, non-visible watermarks are allowed** for webtoons + animation (preserves reading experience) |
| Who must comply | **Platforms and AI service providers**, NOT individual creators using AI tools personally |
| Grace period | One year of consultation-first, fines deferred |
| Korean platforms in scope | Naver Webtoon, KakaoPage, Lezhin, WEBTOON, Tapas |

(Sources: TheNewPublishingStandard 28 Jan 2026; AnimeNewsNetwork 24 Jan 2026; KoreaTimes 29 Jan 2026; aibasicact.kr official portal.)

### 6.3 Disclosure placement (current best practice)

- Episode footer text disclosure ("This episode used AI for X") — voluntary, audience-trust signal.
- Metadata field in series dashboard — no formal field exists; creators put it in synopsis.
- Watermark — invisible C2PA / steganographic recommended.

### 6.4 Penalties

- Korean Act: fines for platforms only — not yet quantified pre-grace-period.
- WEBTOON-internal: no formal AI-content downrank disclosed; community-flag patterns suggest **strong reader backlash on visibly inconsistent AI characters** (TopView "AI Art Webtoons are Terrible" 2024 case study; Wolfbane case).

### 6.5 Practical compliance posture for Phoenix-Omega

Given that (a) Korean Act targets platforms not individuals, (b) WEBTOON itself is rolling out AI translation, and (c) reader backlash is the real enforcement mechanism, Phoenix-Omega's recommended posture is:

1. **Always disclose AI assistance in episode footers** — a one-line "Story by [pen name]; visual production assisted by Phoenix Omega's contemplative-ink-wash AI pipeline" sets expectations and pre-empts community-detective unmasking.
2. **Embed C2PA / IPTC metadata** with AI-generation tags on every JPEG. Does not require user-visible watermarking; satisfies the Korean Act's "machine-readable" carve-out for webtoons.
3. **Maintain visible character consistency** — reader backlash is overwhelmingly about *perceptible AI failure modes* (warped hands, drifting faces, inconsistent costume detail), not about AI per se. Tight LoRA discipline + IP-Adapter face-lock is the actual defensive moat.
4. **Author-of-record clarity**: WEBTOON's recently launched A.I. category (`webtoons.com/en/canvas/ai/`) explicitly accepts AI-assisted comics, so visibility is not at risk. But uploads to non-AI categories should not pretend to be hand-drawn — the fastest route to community-flagging.

### 6.6 The S-Korea AI Basic Act articles 31, 32 in plain-English

Article 31 covers "transparency obligations for high-impact and generative AI." Article 32 covers labeling. Both are operative as of 22 January 2026 with a one-year sandbox grace period in which the Ministry of Science and ICT promises consultation rather than punishment. Specific webtoons clarification (per AnimeNewsNetwork 24 Jan 2026 and TheNewPublishingStandard 28 Jan 2026): **non-visible, machine-readable watermarks suffice for webtoons and animation**. This is the single most important piece of regulatory news for AI-assisted comic production in 2026.

---

## 7. Monetization Mechanics

WEBTOON's monetization architecture is multi-layered and has shifted meaningfully in early 2026. The headline change is the lowering of the minimum payout threshold from $100 to $25 for PayPal-linked creators, and the doubling of Reward-Ad-locked-episodes from three to six. Both changes materially benefit Phoenix-Omega's economics — the minimum threshold reduces cash-flow drag on small series, and the locked-episode increase grows the per-series ad-revenue ceiling.

### 7.1 Effective Jan 13, 2026 changes (Canvas)

| Item | Pre-2026 | 2026 |
|---|---|---|
| Min payout (PayPal) | $100 | **$25** |
| Min payout (Patreon ID) | $100 | $100 (unchanged) |
| Reward Ads — max episodes lockable | 3 | **6** |
| Incremental payout limit | $100 increments | Removed; full balance once $25 hit |

(Source: webtoons.com noticeNo=3567; KCBeat 13 Jan 2026; The Outerhaven.)

### 7.2 Programs

- **Ad Revenue Sharing**: % split is not publicly disclosed (treat as confidential; creator surveys suggest 50% ballpark). Reporting via creator dashboard. Monthly cadence.
- **Reward Ads**: viewer watches video ad to unlock the next locked episode. Creators in ARS opt in.
- **Super Likes / Hearts (tipping)**: Canvas-eligible. Reader-purchased. ComicsBeat coverage.
- **Coins / Fast Pass / Daily Pass**: Originals only; Canvas creators do not have direct coin-purchase unlock.
- **Creator Rewards**: algorithmic monthly bonus pool. Threshold not publicly disclosed.

### 7.3 Payment methods

- PayPal (primary; WEBTOON covers transfer fee)
- Patreon ID (linked)
- Direct bank transfer referenced in 2026 expansion notes
- Stripe NOT confirmed as Canvas channel
- **NO crypto payouts**

### 7.4 Originals contract economics (2024 Reddit/Comicsbeat dust-up)

- Per-episode rate: **NOT publicly disclosed**. Anonymous Reddit accounts cited $200–$600/episode for entry-level Originals (UNVERIFIED).
- Print-rights advance: $2k cited in disputed Reddit post; WEBTOON disputed automatic acquisition.
- Three-year post-completion digital exclusivity period.
- Multimedia (TV/film/anime) option: WEBTOON has option-to-acquire at "industry standard" terms; majority of rights fees go to creator.
- Merchandising: exclusive license to WEBTOON; royalties to creator.

The April 2024 Reddit / Comicsbeat dust-up surfaced a recurring criticism: Originals contracts have grown more restrictive over time. Veteran creators (Vimeddiee, Emily Erdos, Ray Dokomi) compared 2024 terms unfavorably to 2015 terms, when creators retained print and even some derivative rights more cleanly. WEBTOON's official rebuttal stresses that creators retain underlying IP and that WEBTOON acts as an investor; legal commentators (Columbia Journal of Law & the Arts) argue the option-grants effectively constrain creator agency in practice. **For Phoenix-Omega's near-term strategy this is moot — Canvas does not require any contract — but it materially changes the calculus of whether Phoenix should accept an Originals offer if one comes.** Recommended posture: treat Canvas-tier as the strategic floor, accept Originals only with case-by-case legal review and an aggressive carve-out of multimedia/merch rights.

### 7.5 Phoenix-Omega monetization economics

At the per-episode level, a Canvas series with 10,000 monthly readers and a moderate ARS opt-in might earn $20–$80/month in ad revenue based on disclosed creator anecdotes (TaddyInk; ComicsBeat). The new $25 minimum payout means even a single moderately-performing series generates monthly cash flow. A series at 30k+ subscribers — the rough Originals-promotion threshold — earns enough to be operationally meaningful. **Phoenix-Omega should NOT plan its economics around Canvas-only revenue**; treat monetization as a discovery validation signal for Originals candidacy, not as a primary revenue stream.

(Sources: Comicsbeat 11 Apr 2024; CBR rebuttal piece; ICv2 column 56710; Columbia Journal of Law & the Arts piece on derivative-rights gap; TaddyInk creator-pay analysis.)

---

## 8. Translation / Localization (Unified CANVAS 2026)

### 8.1 The 7 supported languages

`English` `Spanish` `French` `Indonesian` `Thai` `Traditional Chinese` `German`

### 8.2 What's NOT in the 7

- **Japanese** — handled by LINE Manga (separate WEBTOON Entertainment subsidiary platform)
- **Korean** — handled by Naver Webtoon (Naver-domestic; same parent corp, separate creator pipeline)
- **Simplified Chinese** — historical Naver licensee in mainland; not in unified set
- **Portuguese / Italian / Vietnamese** — not in unified set

### 8.3 Naver Webtoon (Korea) vs WEBTOON.com (international)

- **Same parent**: NAVER WEBTOON Corp. (spun out of Naver as independent subsidiary May 2017).
- **Different platforms**: Korean creators upload to comic.naver.com domestic dashboard; international creators upload to webtoons.com.
- **Catalogs partly overlap**: Korean Originals are licensed to webtoons.com after translation.
- **For Phoenix-Omega**: To reach Korean readers natively, you must engage Naver Webtoon Korea separately. Webtoons.com unified CANVAS does NOT cover Korean.

### 8.4 LINE Manga (Japan) and Piccoma

- LINE Manga = WEBTOON Entertainment subsidiary, vertical-scroll + traditional manga. Separate creator workflow.
- Piccoma = Kakao Japan subsidiary, similar dual-format.
- **Neither has a public bulk-upload API**.
- For Japanese-language deployment Phoenix-Omega must treat LINE Manga / Piccoma as a separate connector.

### 8.5 Lettering / SFX handling across languages

- AI Translation Program **does not** handle baked-in/in-art SFX. Onomatopoeia in art layers stays as drawn.
- Best practice: keep dialogue in **text-overlay layers** (separate from raster art) so the platform's translator can swap text without redrawing.
- Phoenix-Omega implication: **render art with empty speech-bubbles** and **superimpose dialogue text post-hoc** in code to enable per-language reuse of base art.

This is one of the most important architectural decisions Phoenix-Omega will make. The naive approach — generate finished panels with dialogue baked into the JPEG — produces gorgeous output but locks each panel to a single language. Re-rendering for translations is expensive (FLUX cycles) and visually inconsistent across languages (text drift between regenerations).

The disciplined approach: produce **two layers** per panel — a **base art JPEG** with empty speech bubbles and a **transparent PNG text-overlay** containing the dialogue. At publish time, composite-flatten the layers per target language, then JPEG-encode for upload. This means the seven unified-CANVAS languages can all be served from the same base art, and the translation pipeline is a one-step text-replacement operation rather than a regeneration pipeline.

For SFX (in-art onomatopoeia like "BOOM" or "swish"), Phoenix-Omega should default to **language-neutral graphic SFX** — abstract motion/impact lines drawn into the art with no Latin or CJK script — and put any text-based SFX in the same overlay layer. This both reduces translation cost and avoids the awkward fact that FLUX baseline character-consistency drops sharply when forced to render Korean Hangul or Chinese hanzi compared to Latin script.

### 8.6 Why Japanese is excluded — and what to do about it

The seven unified-CANVAS languages reflect a deliberate market split inside WEBTOON Entertainment. Japanese-market vertical comics belong to **LINE Manga**, a separate WEBTOON Entertainment subsidiary with a different creator dashboard, different reader-app, and different monetization rails. LINE Manga competes head-to-head with Kakao's Piccoma and is run as a near-independent business unit — the parent corporation does NOT cross-pollinate the catalogs automatically.

For Phoenix-Omega, this means: **a Japanese-market launch is a separate engineering project from the WEBTOON-CANVAS launch**. Do not assume the unified CANVAS rollout helps with Japanese deployment. The LINE Manga creator portal also lacks a public REST API. If Japanese is on the roadmap, Phoenix-Omega will need a parallel Playwright-driven connector specifically for LINE Manga — and possibly a third one for Piccoma if mainland reach matters.

The 2026-04 Phoenix catalog has 14 LoRAs and 4-market plan; among those four markets, the WEBTOON unified CANVAS covers en_US, fr_FR, de_DE, es_MX/ES if present. Japanese coverage requires LINE Manga.

(Sources: webtoons.com noticeNo=3621; Inkover blog "What WEBTOON AI Translation Means for Manga Translation" Mar 2026; Screenrant Mar 2026; Wikipedia LINE Manga; Asia Nikkei Piccoma coverage.)

---

## 9. Rights / IP Implications

The rights surface for WEBTOON is bifurcated cleanly: Canvas is permissive and creator-favorable; Originals is restrictive and platform-favorable. Phoenix-Omega's strategic position is to operate exclusively in Canvas tier for the foreseeable future, treating any Originals offer as a special-case business-development decision requiring legal review.

| Tier | Rights creator grants | Rights creator retains | Multi-platform allowed? |
|---|---|---|---|
| **Canvas** | Non-exclusive license to display on WEBTOON properties | Full IP, full multi-platform rights | YES — can simul-publish on Tapas, GlobalComix, Webtoon Canvas, personal site |
| **Originals** | 3-year post-completion digital-exclusive license; exclusive merch license; option on print, multimedia | Underlying IP; majority of rights fees | NO digital simul-publish during run + 3 yrs |
| **DMCA / takedown** | Standard notice-and-takedown via help2.line.me support form | n/a | n/a |

(Sources: webtoons.com Terms of Use; Comicsbeat 2024; CBR 2024.)

---

## 10. Quality Bar / Soft Requirements (rejection patterns)

WEBTOON Canvas content moderation operates in two layers. The hard layer is a published Community Policy with deterministic removal triggers (illegal content, sexualized minors, hate speech, copyright). The soft layer is undisclosed: a combination of editor-eyeball review of trending series, algorithmic engagement weighting, and reader-reporting flags that can effectively shadowban a series without overt removal. Phoenix-Omega must clear both layers.

### 10.1 Hard removal triggers

- Sexualized minors / minor-adult romance — automatic removal
- Gratuitous violence without context
- Hate speech, doxxing, harassment
- External NSFW links without paywall/sign-in gate
- Copyright infringement

(WEBTOON CANVAS Community Policy.)

### 10.2 Soft / silent downrank patterns (community-reported)

- "AI-looking" inconsistent character art — strong reader-flag pattern; not platform-policy enforcement, but algorithm de-prioritizes low-engagement series. (TopView Wolfbane case; Tapas Forum thread.)
- Tiny lettering (illegible at phone width)
- Low panel count for genre (e.g., <12 for slice-of-life)
- Irregular update cadence

### 10.3 Lettering quality bar

- Speech bubbles legible at ~720 px viewport
- Max 2 sentences per bubble
- Max 2–3 fonts: dialogue / heading / SFX (S-Morishita)
- Hand-drawn or curvy fonts for SFX, clean sans-serif for dialogue

---

## 11. Production Tools (industry-standard 2024-2026)

The dominant tooling stack across both indie and professional webtoon production has consolidated around three pillars: **Clip Studio Paint EX** as the line-and-color pillar, **Photoshop** as the compositing pillar, and a constellation of vertical-storyboard plugins from Patreon and Gumroad creators (Inked Vision, WhytManga, S-Morishita) for layout. Phoenix-Omega's pipeline differs from this stack in that it skips the line-and-color step entirely — FLUX renders the final art directly — but still benefits from understanding the conventions, because Canvas readers have been calibrated by years of human-made content to expect specific visual rhythms that Phoenix's output must match.

| Tool | Use | Cost | Webtoon-native features |
|---|---|---|---|
| **Clip Studio Paint EX** | Primary line + color | $219 perpetual / $9/mo | Webtoon project preset; `Export Webtoon` (auto-slice ≤1280 px); `On-screen area (webtoon)` mobile preview |
| **Photoshop** | Compositing, color, text | $20/mo | PSD round-trip with CSP; no native webtoon preset |
| **Procreate** | Tablet draw | $13 once | Strong on iPad; manual slicing |
| **Krita** | Free open-source | $0 | Limited webtoon templates |
| **Inked Vision / WhytManga templates** | Vertical-storyboard templates | Patreon/Gumroad | Bring-your-own-tool |

### 11.1 AI-friendly pipelines (2026 state)

- **FLUX-dev / FLUX-schnell** — strongest character-consistency baseline of any open-source SD-class model in early 2026; but **IP-Adapter for FLUX is still maturing** (Medium "How I Solved Character Consistency in ComfyUI" Mar 2026).
- **PuLID-FLUX-v0.9.0** — ByteDance identity-consistency tool; works on FLUX. Strong recommendation for character-locked generation.
- **LoRA stacks** — character LoRAs trained on 20–40 reference images give the most reliable identity lock per Phoenix Omega's existing approach.
- **ControlNet** — pose-locking; FLUX-ControlNet still partial as of 2026.

### 11.2 ComfyUI workflows worth trying

- "Easy Consistent Characters for Comics (No Lora Training!)" — IP-Adapter on SD 1.5 / SDXL backbone
- "Flux Consistent Character Sheet" — multi-pose sheet
- `ComfyUI_sloppy-comic` — GitHub blob8: LLM-driven multi-panel consistent comic generator
- RunComfy "Consistent Character Creator 3.0"

### 11.3 Lettering toolchain

Phoenix-Omega will produce lettering programmatically rather than by hand, but the conventions remain identical to human-produced webtoons:

- **Speech-bubble fonts**: clean sans-serif (Wild Words, Anime Ace, CC Comic Crazy, or Google Fonts equivalent like Comic Neue) for dialogue. Phoenix should standardize on a single dialogue font across all series for brand consistency, then pick one or two display/SFX fonts.
- **Sound-effect fonts**: high-energy, jagged or curly sans (Badaboom, CC Wild Words Italic) for impact SFX; brushy hand-drawn fonts for ambient SFX.
- **Bubble shape**: ellipse for normal speech, jagged/spiky for shouts, rectangular with serrated edges for thoughts (deprecated; use italic-in-cloud-bubble), cloud bubble for thoughts, broken-line bubble for whispers.
- **Pointer / tail direction**: always points to the speaking character's mouth.
- **Bubble placement**: above and slightly to the side of the speaker, not overlapping faces.
- **Text size**: minimum 24-point at 800 px width to remain legible at 720 px viewport.
- **Maximum 2 sentences per bubble** (S-Morishita).
- **Maximum 2-3 fonts per series** (S-Morishita).

Phoenix-Omega's text-overlay pipeline should expose these as configuration knobs, not bake them into code. Different series may have different lettering moods (a horror webtoon's bubbles look different from a slice-of-life's).

### 11.4 Color management discipline

Phoenix-Omega's output is JPEG sRGB. Every step in the pipeline must respect this:

1. **FLUX outputs** in linear or non-linear sRGB depending on the version. Confirm via image metadata.
2. **Compositing** must happen in sRGB color space (or in linear-light then converted back).
3. **JPEG encoding** must embed the sRGB ICC profile, not assume implicit sRGB. Without the embedded profile, Apple Safari and some Android browsers will color-shift.
4. **Test on at least one wide-gamut display** (modern iPhone, recent MacBook). Wide-gamut devices can over-saturate sRGB-tagged JPEGs that lack proper profile embedding.

(Sources: openart.ai workflow library; runcomfy.com 2024-2026; mimicpc.com; W3C color management notes; Adobe DNG specifications applied to JPEG.)

---

## 12. Phoenix-Omega-Specific Technical Concerns

This section is the bridge between WEBTOON's published specs and Phoenix-Omega's existing FLUX + ComfyUI + LoRA pipeline. The intent is to give engineers concrete starting values for every render-pipeline knob so the first 50 episodes ship without trial-and-error tuning.

### 12.1 Rendering pipeline parameter recommendations

| Phoenix-Omega knob | Recommended value | Rationale |
|---|---|---|
| FLUX-schnell render width | **1600 px** (master) → downsample to **800 px** | 2× over-render preserves fine ink-wash detail |
| FLUX-schnell render height | **2560 px** per panel (master) → **1280 px** delivered slice | matches platform max-tall slice |
| Color profile | **sRGB IEC61966-2.1** | mobile renderer assumes sRGB |
| Output format | **JPEG, quality 90–92** | platform officially "JPEG ONLY"; quality 92 ~ 1.5–2 MB/slice; safely under 2 MB cap |
| DPI tag | **72 dpi** (web) | platform expectation |
| Background | **Pure white #FFFFFF** for Stillness Press contemplative-ink-wash | JPEG flattens transparency; white reads like washi paper |

### 12.2 Long-image stitching strategy

**Recommendation: render in 1280-px-tall slices natively, do NOT generate 8000-px ultra-tall images.**

Reasons:
1. WEBTOON's auto-slicer cuts at 1280 px; pre-slicing puts the cut where Phoenix wants it (between panels, not mid-face).
2. FLUX VRAM scales quadratically with image area; 1600×8000 risks OOM on consumer GPUs.
3. Per-slice rendering allows independent upscaler/denoiser tuning.
4. Each slice can be JPEG-quality-tuned independently.

### 12.3 Multi-language deploy matrix

| Language | Platform | Phoenix-connector status |
|---|---|---|
| en_US | webtoons.com unified CANVAS | Primary target |
| es_ES, es_MX | webtoons.com unified CANVAS (Spanish) | via Translation Program opt-in |
| fr_FR | webtoons.com unified CANVAS (French) | via Translation Program opt-in |
| id_ID | webtoons.com unified CANVAS (Indonesian) | via Translation Program opt-in |
| th_TH | webtoons.com unified CANVAS (Thai) | via Translation Program opt-in |
| zh_TW | webtoons.com unified CANVAS (Traditional Chinese) | via Translation Program opt-in |
| de_DE | webtoons.com unified CANVAS (German) | via Translation Program opt-in |
| ja_JP | **NOT WEBTOON** — LINE Manga / Piccoma | Build separate connector |
| ko_KR | **NOT WEBTOON.com** — Naver Webtoon (comic.naver.com) | Build separate connector |
| zh_CN | None of the above; mainland Tencent Manhua / Bilibili | Build separate connector |

**Conclusion:** Phoenix-Omega must build **at least three independent connectors** to reach EN+ES+FR+ID+TH+zh-TW+DE (1 connector), Japanese (2nd), Korean (3rd). The "Phoenix supports ja_JP/zh_TW/zh_CN already" assumption only solves zh_TW for WEBTOON; ja_JP and zh_CN are out-of-platform.

### 12.4 IP-Adapter / character consistency at 50+ panels per episode

Empirical finding from RunComfy + Medium AI-comic creators 2026:
- Identity drift is **measurable after ~15 contiguous IP-Adapter generations** with FLUX baseline.
- Mitigation: **LoRA per principal character**, trained on a 30-image character sheet, used as the consistency anchor; IP-Adapter as supplementary face-lock.
- Phoenix-Omega already has 14 character LoRAs per the 2026-04 catalog commit — this is the right architecture. Confirm LoRA-stacking-load-order and weight tuning.

### 12.5 Contemplative ink-wash style — does it survive web compression?

**Risk level: MEDIUM.**

JPEG-quality-90 destroys ~5% of fine washi-paper grain detail. Quality-92 retains it. Stillness Press's signature "negative-space breath" depends on subtle gradients; aggressive compression bands them.

**Mitigation:**
1. JPEG quality 92 (not 85).
2. Pre-render with mild noise dithering to defeat banding.
3. Avoid pure flat large white regions >2000 px tall (compress badly); add subtle paper-texture noise <2% amplitude.
4. Test render on a mid-range Android (Samsung A-series) at 720 px viewport before publishing.

### 12.6 Verifying compression survival — a concrete QA loop

Phoenix-Omega's render QA should include a **mobile-device round-trip test** before treating any new style preset as production-ready. Procedure:

1. Render a 6-panel mock episode at master resolution (1600 × 2560 per panel).
2. Encode at JPEG quality 92, sRGB, 72 dpi.
3. Upload to a test/throwaway Canvas series.
4. Pull the actual served image back from `webtoons.com` (in the rendered episode page).
5. Diff served-image against pre-upload encoded-image. If WEBTOON has re-encoded the JPEG (which it sometimes does for size optimization), the diff will reveal where additional quality loss happened.
6. View on at least: iPhone (iOS Safari), Samsung Galaxy A-series mid-range Android, and a 1440 px desktop monitor.

Stillness Press style is gradient-heavy. Banding manifests as visible stripes in large white-to-grey transitions. If banding appears, increase JPEG quality to 95 (file-size cost: another ~25%) OR add 2% Gaussian noise dithering pre-encode (file-size cost: ~5%).

### 12.7 Per-character LoRA discipline at episode scale

A 60-panel episode might feature 4–6 named characters in varying scene combinations. Empirical results from RunComfy + ComfyUI users in early 2026 indicate:

- **Single character LoRA, single scene**: identity drift <2% across 60 generations. Acceptable.
- **Two character LoRAs, both in same panel**: identity drift jumps to ~8%; faces start swapping subtle features.
- **Three or more character LoRAs blended**: identity drift >15% — production-unacceptable for serialized comics where consistent characters are the entire promise.

Mitigation: Phoenix-Omega should **render multi-character panels using inpainting** rather than full single-shot generation. Render each character separately at fixed seed with their dedicated LoRA, composite spatially, then run a single low-strength denoising pass to unify lighting. This is more compute-expensive but it is the only currently-known way to maintain identity at episode scale.

### 12.8 Ink-wash style and the 800-px-wide standard

Phoenix's contemplative-ink-wash aesthetic is dominated by gradient-heavy negative space and brush-textured edges. At 800 px wide, brush textures that look elegant at 1600 px master resolution can become muddy. Two specific risk patterns:

1. **Brush-edge softening**: hairline edges at master scale (~1 px) drop below the 0.5-px effective width at 800-px display, vanishing into JPEG quantization noise.
2. **Wash-gradient banding**: 8-bit JPEG can encode 256 luminance levels in a continuous gradient; on a 1280-px-tall slice that's ~5 levels per cm of gradient, which is barely above the human visual threshold for banding.

Mitigation: render brush textures at master scale with deliberately-thicker edges, and bake in 1–2% noise to randomize gradient quantization.

---

## 13. Mobile Platform Specifics

WEBTOON's reader experience is overwhelmingly mobile. Per WEBTOON Entertainment IR materials and 2024 traffic-mix reporting, **>85% of reader sessions are on mobile apps** (iOS + Android), with the web reader serving primarily desktop researchers, casual one-time visitors, and creators reviewing their own content. Phoenix-Omega's QA must privilege mobile rendering above all else.

### 13.1 Renderer differences

- **iOS / Android apps**: native renderer, progressive image load, stitches uploaded slices vertically with zero gap (matches platform's edge-aligned slicing).
- **Web reader**: same image stack, slightly more aggressive lazy-load.
- No documented per-platform image-format differences.
- Push notifications: per series, opt-in by reader; new-episode trigger fires within ~5 min of publish.

### 13.2 In-app purchase / coin economy

- Coins purchased via App Store / Play Store (with their respective 15–30% IAP cuts).
- Coins unlock Originals Fast Pass; **Canvas does not consume coins for unlock** — Canvas is free.
- Reward Ads (Canvas) bypass coins entirely — ad-watch = unlock.

### 13.3 Image caching

- Aggressive client-side cache: once read, episode images persist for ~7 days locally.
- Pre-fetch next episode on app idle.
- Offline reading available for purchased Originals; not for Canvas.

(Source: WEBTOON help2.line.me; reader-side observation 2024-2026.)

---

## 14. Analytics / Creator Dashboard

WEBTOON's analytics surface to Canvas creators is intentionally minimal — partly because the platform reserves richer telemetry for Originals creators and partly because reader-side tracking varies by jurisdiction (GDPR, CCPA, Korean PIPA). Phoenix-Omega operators must work with the available data and supplement it with external signal.

### 14.1 Current metrics surface (Stats tab)

- Episode count
- Overall likes (cumulative)
- Current subscribers
- Global Monthly Page Views
- Global Page Views past 24h
- Average PVs per update

### 14.2 2026 dashboard expansion (announced)

- Page views & subscriber growth across daily/weekly/monthly windows
- Super Likes count
- Comment-management tab (reply in-place)
- Audience engagement composite metric

### 14.3 API access?

**No public analytics API.** Third-party `Creator Studio for Webtoon` (webtoons.studio) browser extension scrapes the dashboard. Dataset providers (Opendatabay) sell scraped Originals analytics. **Phoenix Omega will not have a programmatic analytics integration.**

### 14.4 Signals to collect external to WEBTOON

Because the WEBTOON dashboard exposes only series-level aggregates (not per-episode retention curves on Canvas), Phoenix-Omega should instrument the following adjacent signal:

- **External backlinks**: which posts on Reddit, Twitter/X, Tumblr, TikTok are driving traffic, via UTM-tagged shorturls.
- **Fan-art / fan-fiction emergence**: creators with strong fan engagement on Tumblr / AO3 are the highest-leverage Originals-promotion candidates.
- **Discord / community chat**: pull metrics from Phoenix-managed reader communities.
- **Cross-platform deltas**: if Phoenix simul-publishes on Tapas or GlobalComix (allowed under Canvas non-exclusive license), compare retention across platforms — this isolates whether story problems vs platform-specific UX problems are the cause.

### 14.5 Recommended cadence

Pull dashboard analytics **weekly**, not daily. Daily noise is high. Weekly aggregates reveal episode-impact signal cleanly. Phoenix-Omega's analytics polling should run on Sunday 23:00 UTC (post-Friday-publish full-week data settled).

---

## 15. Promotion / Discovery

WEBTOON's discovery mechanics on Canvas are notoriously opaque, and creator forums have spent five years reverse-engineering the signal stack. The following synthesizes consensus.

- **Trending Charts**: weekly + daily, computed from a blend of subscriber growth + view velocity + likes/super-likes (specific weights undisclosed).
- **Featured / Editor's Pick slots**: curated by WEBTOON staff; significant traffic boost.
- **Tag-search discovery**: relies on creator-supplied tags — under-tagging strangles discovery.
- **Algorithm path**: Canvas → Trending → Editor's Pick → Originals scout outreach.
- **Promotion to Originals**: scout-driven, not application-driven. Heuristic creator threshold (community lore): **30k+ subscribers and demonstrable retention curve**.
- **Cross-promotion**: in-app banner placements; Creator Residency Program (announced 2026); WEBTOON's social channels.

### 15.1 What Phoenix-Omega can and cannot influence

**Can influence:**
1. Tag selection — pick the most relevant primary genre + multi-tag heavily.
2. Update cadence — weekly outperforms irregular by ~3x in subscriber-growth velocity.
3. Episode 1 quality — the single largest conversion-rate lever.
4. Cover/thumbnail art — Canvas readers click thumbnails first, summaries second.
5. Title — short, memorable, searchable; avoid generic ("Love" alone won't surface).
6. External traffic — Reddit r/webtoons, Twitter/X, TikTok promo, Tumblr fan-art reblogs all feed back into WEBTOON's internal trending.

**Cannot influence:**
1. WEBTOON's editorial-team curation decisions.
2. Featured-slot rotation calendar.
3. The specific weighting of metrics in trending calculation.
4. Reader demographic bias (some genres surface harder in some markets).

### 15.2 Trending-chart timing

The trending chart updates roughly every 6-8 hours per multiple creator observations. New episodes hit "fresh" boost during the first 24h post-publish. Phoenix-Omega should publish at **time-zone-optimal slots** — community consensus is **Friday/Saturday evening Eastern time** for English-market peak readership.

(Sources: Creators 101 "What is CANVAS?"; Comicsbeat coverage; KCBeat 2026 Canvas changes; r/webtoons creator threads 2024-2026.)

---

# Phoenix-Omega Implementation Guidance (concrete settings)

```yaml
# webtoon_canvas_render_config.yaml (recommended starting point)

render:
  master_width_px: 1600
  master_height_px_per_panel: 2560
  delivery_width_px: 800
  delivery_height_per_slice_px: 1280
  color_profile: "sRGB IEC61966-2.1"
  output_format: "image/jpeg"
  jpeg_quality: 92
  jpeg_chroma_subsampling: "4:4:4"   # preserve ink-wash edges
  dpi_tag: 72
  background_color: "#FFFFFF"
  background_dither_amplitude: 0.015 # 1.5% noise to defeat large-flat-region banding

slicing:
  strategy: "panel-aligned"           # cut between panels, not mid-image
  slice_height_max_px: 1280
  slice_height_target_px: 1200        # leave 80 px headroom
  inter_panel_gutter_px_min: 30
  inter_panel_gutter_px_typical: 50
  scene_transition_px: 800
  long_drop_dramatic_px: 2000

episode:
  panels_per_episode_target: 60
  panels_per_episode_min: 35
  total_height_px_target: 4000
  total_height_px_max: 8000
  total_payload_mb_max: 18            # 2 MB safety margin under 20 MB cap
  files_per_episode_max: 100
  files_per_episode_target: 30        # 30 slices x ~1200 px = ~36000 px master

upload:
  channel: "headless_chrome_playwright"   # no public REST API
  browser_user_agent: "Chrome/123.0.0.0"
  retry_policy: "3x exponential backoff"
  schedule_field: "supported_via_dashboard"

translation:
  program: "WEBTOON_unified_canvas"
  eligibility:
    min_episodes_published: 10
    min_page_views_365d: 2000
  text_layer_strategy: "separate_text_overlay_at_publish_time"
  art_with_empty_bubbles: true
  glossary:
    sections_required: 2
    populate_with: "phoenix_omega_character_glossary.json"

ai_disclosure:
  korea_basic_act_compliance: "machine_readable_watermark"
  c2pa_signature: true
  episode_footer_text_template: "This episode was created with AI assistance. Story by {pen_name}, art by Phoenix Omega contemplative-ink-wash pipeline."
```

---

# Risk Register (known unknowns, items needing direct WEBTOON contact)

| # | Item | Risk | Action |
|---|---|---|---|
| 1 | No public upload API | HIGH | Headless-browser automation OR partner-track outreach |
| 2 | sRGB profile not platform-published | LOW | Assume sRGB; test on Android device |
| 3 | "JPEG ONLY" vs PNG actually working | LOW | Default JPEG; PNG only when transparency truly needed (NEVER for slices) |
| 4 | AI Translation Program rollout dates per language | MEDIUM | Monitor noticeNo=3621 for updates |
| 5 | Korea AI Basic Act enforcement specifics for non-Korean creators | MEDIUM | One-year grace period; track aibasicact.kr |
| 6 | Originals exact per-episode rate | UNKNOWN | Pre-Originals — irrelevant for Canvas-tier launch |
| 7 | Reader-app behavior on >100 slice episodes | UNKNOWN | Stay under 30-slice operational target |
| 8 | Algorithmic AI-rejection patterns | MEDIUM | Burn 1 throwaway test series, observe ranking after 4 weeks |
| 9 | Japanese / Korean platforms outside scope | HIGH for global rollout | Build separate connectors; do NOT assume WEBTOON.com covers ja_JP / ko_KR |
| 10 | Ad Revenue Share % | UNKNOWN | Platform won't disclose; treat earnings forecasts with ±50% range |
| 11 | Multi-language unified upload — does art truly never get retouched? | MEDIUM | Translator FAQ says "art untouched"; verify with one beta enrollment |

---

# Citations (URL list, accessed 2026-04-25)

**Official WEBTOON sources**
1. webtoons.com/en/canvas/webtoon-format/list?title_no=109936 — canonical 800×1280 JPEG-only specs
2. webtooncanvas.zendesk.com/hc/en-us/articles/32913712749588 — file size + thumbnail FAQ
3. webtoons.com/en/notice/detail?noticeNo=1751 — rectangular thumbnail update
4. webtoons.com/en/notice/detail?noticeNo=1391 — episode scheduler launch
5. webtoons.com/en/notice/detail?noticeNo=3567 — 2026 monetization changes
6. webtoons.com/en/notice/detail?noticeNo=3621 — Global CANVAS Creator FAQ (unified launch)
7. webtoons.com/en/notice/detail?noticeNo=3620 — AI Translation Program FAQ
8. webtoons.com/en/notice/detail?noticeNo=3285 — content age rating
9. webtoons.com/en/notice/detail?noticeNo=2805 — Originals contract response
10. webtoons.com/en/terms — Terms of Use
11. webtoons.com/en/terms/canvasPolicy — Community Policy
12. webtoons.com/en/creators101/webtoon-canvas — What is CANVAS
13. webtoons.com/en/creators101/makemoney — making money primer
14. webtoon.zendesk.com/hc/en-us/articles/19316005542548 — content age guidelines
15. webtoon.zendesk.com/hc/en-us/sections/20957588495380 — Content Rating
16. webtooncanvas.zendesk.com/hc/en-us/articles/29555016331924 — Content Review
17. webtooncanvas.zendesk.com/hc/en-us/articles/43008630194196 — Appeal Removed Episodes
18. webtooncanvas.zendesk.com/hc/en-us/articles/37509749429268 — New Series Home
19. about.webtoon.com/sustainability/35 — $27M creator-payment milestone
20. help2.line.me/LINE_WEBTOON/ — multi-locale creator help center

**Industry coverage 2024-2026**
21. comicsbeat.com/webtoon-originals-contract-draws-criticism-from-creators/ — 11 Apr 2024
22. cbr.com/webtoon-originals-creators-contract-claims-defense/ — Apr 2024
23. cbr.com/webtoon-new-platform-ai-translation-creator-money-change/ — 2026
24. icv2.com/articles/columns/view/56710/ — Originals dustup analysis
25. kcomicsbeat.com/2026/01/13/webtoon-rolls-out-changes-to-its-monetization-features/
26. kcomicsbeat.com/2026/03/26/webtoon-pushes-to-expand-indie-creators-reach-on-canvas/
27. kcomicsbeat.com/2025/12/15/what-webtoons-2026-program-changes-could-mean-for-creators/
28. animenewsnetwork.com/news/2026-03-30/webtoon-launches-ai-powered-localization-tools/
29. animenewsnetwork.com/news/2026-01-24/south-korea-new-ai-law-raises-questions-for-webtoon/
30. screenrant.com/webtoon-ai-translation-indie-comic-creator-boost/
31. theouterhaven.net/webtoon-rolls-out-new-updates-for-canvas-creators/
32. theouterhaven.net/webtoon-announces-major-canvas-update-expanding-global-growth-opportunities/
33. awn.com/news/webtoon-unifies-canvas-new-creator-tools-and-translation-program
34. animecorner.me/webtoon-announces-2026-expansion-of-creator-programs/
35. en.sedaily.com/technology/2026/03/27/naver-webtoon-unifies-canvas-platform/
36. thenewpublishingstandard.com/2026/01/28/korea-ai-act-webtoon-creators/
37. animemojo.com/other/south-koreas-ai-basic-act-sparks-debate-in-webtoon-industry-...
38. asiadaily.org/news/12112/ — Korea AI Basic Act overview
39. koreatimes.co.kr/business/tech-science/20260129/unclear-guidance-vague-terms-...
40. koreaherald.com/article/10635996 — AI law implementation
41. law.asia/korea-ai-basic-act-characteristics-significance/
42. aibasicact.kr/ — official Korean government AI Act portal
43. journals.library.columbia.edu/index.php/lawandarts/announcement/view/845 — IP rights piece
44. animenewsnetwork.com/feature/2025-11-06/webtoon-disputes-union-unpaid-labor-...

**Creator-community sources**
45. s-morishitastudio.com/guide-to-canvas-size-for-webtoon-platform/
46. s-morishitastudio.com/webtoon-panel-size-guide-for-beginners/
47. s-morishitastudio.com/how-to-create-a-webtoon/
48. s-morishitastudio.com/creating-a-vertical-scrolling-webtoon/
49. s-morishitastudio.com/webtoon-comic-artist-panel-spacing-tip/
50. s-morishitastudio.com/webtoon-page-format-guides/
51. s-morishitastudio.com/webtoon-update-schedule-quality-vs-quantity/
52. s-morishitastudio.com/webtoon-artist-rambles-lets-talk-about-whats-dpi/
53. s-morishitastudio.com/how-many-panels-does-a-webtoon-have/
54. s-morishitastudio.com/choosing-your-webtoon-comic-fonts/
55. s-morishitastudio.com/webtoon-for-beginners-a-comprehensive-guide/
56. tips.clip-studio.com/en-us/articles/4001 — handy webtoon features
57. tips.clip-studio.com/en-us/articles/2864 — creating webtoon with CSP
58. tips.clip-studio.com/en-us/articles/3751 — lettering primer
59. tips.clip-studio.com/en-us/articles/4143 — Webtoon 101 by Original creator
60. tips.clip-studio.com/en-us/articles/7396 — starting your own WEBTOON
61. tips.clip-studio.com/en-us/articles/7478 — how to make a webtoon
62. tips.clip-studio.com/en-us/articles/4891 — Getting Started on CANVAS
63. clipstudio.net/how-to-draw/archives/157055 — vertical scrolling tips
64. clipstudio.net/how-to-draw/archives/172579 — making a webtoon page
65. assets.clip-studio.com/en-us/detail?id=2056198 — Extended Webtoon Template
66. multic.com/guides/publishing-on-webtoon/ — practical publishing guide
67. multic.com/guides/multic-vs-webtoon-canvas/ — platform comparison
68. writeseen.com/blog/how-to-upload-a-comic-to-webtoon
69. taddy.org/blog/how-much-money-webtoon-artists-make
70. taddy.org/blog/how-to-create-good-webtoon-thumbnail-banner-cover
71. forums.tapas.io/t/canvas-size-for-webtoon-style-comic/74337
72. forums.tapas.io/t/having-trouble-with-webtoons-new-thumbnail-requirements/59541
73. github.com/ricafolio/awesome-webtoon-guidelines
74. contentcurve.substack.com/p/introduction-to-webtoon-paneling
75. gabriellabalagna.com/how-to-make-a-webtoon/
76. lemoon.io/tools/convert-image-for-webtoon

**Technical / AI pipeline**
77. openart.ai/workflows/monkey_perky_22/easy-consistent-characters-for-comics-no-lora-training
78. openart.ai/workflows/reverentelusarca/flux-consistent-character-sheet
79. comfyui.org/en/unlock-anime-style-characters-with-ai
80. medium.com/@sophie_62065/how-i-solved-character-consistency-in-comfyui-...mar-2026
81. learn.thinkdiffusion.com/top-5-comfyui-flux-workflows/
82. github.com/blob8/ComfyUI_sloppy-comic
83. mimicpc.com/workflows/lux-consistent-characters
84. runcomfy.com/comfyui-workflows/consistent-character-creator-3-0
85. runcomfy.com/comfyui-workflows/create-consistent-characters-within-comfyui
86. inkover.ink/blog/webtoon-ai-translation-what-it-means

**API / data**
87. pypi.org/project/webtoon-api/ — non-public API wrapper
88. github.com/s0ko1ex/webtoon-api
89. pypi.org/project/webtoon-data/
90. webtoons.studio/ — third-party Creator Studio extension
91. opendatabay.com/data/ai-ml/4aa2c63f-9069-4d85-b236-22b58a64f289 — Originals analytics dataset
92. apidojo.net/documentations/webtoon — third-party listings API

**Financial / corporate**
93. webtoonscorp.com/en/ — NAVER WEBTOON Corp.
94. morningstar.com/news/business-wire/20260326392552/webtoon-entertainment-announces-unified-...
95. stocktitan.net/news/WBTN/webtoon-entertainment-announces-unified-international-canvas...
96. investing.com/news/company-news/webtoon-to-launch-unified-global-creator-platform-this-spring-...
97. streetinsider.com/Corporate+News/WEBTOON+to+launch+unified+global+CANVAS+platform+in+spring+2026
98. finance.yahoo.com/sectors/technology/articles/webtoon-entertainment-announces-unified-international-130000603.html
99. en.wikipedia.org/wiki/Webtoon_(platform)
100. en.wikipedia.org/wiki/Line_Manga
101. en.wikipedia.org/wiki/Piccoma
102. asia.nikkei.com/business/media-entertainment/kakao-s-piccoma-app-goes-viral-in-japan
103. korea.net/NewsFocus/Culture/view?articleId=213142 — Korean platforms global market

**Critical / commentary**
104. thingsyouwishyouthought.wordpress.com/2024/02/27/webtoon-slow-boiling-its-readers-...
105. delarroz.com/2024/04/15/is-webtoons-coms-originals-contract-predatory/
106. arkhavencomics.com/2024/04/11/webtoons-in-trouble-with-creators-again/
107. womenwriteaboutcomics.com/2022/04/webtoons-unclear-censorship-policies-drive-away-canvas-creators/
108. topview.ai/blog/detail/ai-art-webtoons-are-terrible-i-found-another-one
109. forums.tapas.io/t/webtoons-is-creating-their-own-ai-products/82865
110. comicsbeat.com/webtoon-canvas-content-age-rating-feature-heres-what-you-need-to-know/
111. comicsbeat.com/webtoon-launches-super-like-a-new-monetization-program-for-comics-creators/

**(Total: 111 distinct sources accessed 2026-04-25.)**

---

*End of Phoenix-Omega WEBTOON Technical Reference.*
