# Series Titles, Subtitles & Platform SEO — Book + Audiobook Series Planning Research

**Research Date:** 2026-07-23
**Researcher:** Pearl_Research (Tier-1 Claude, operator-present)
**Scope:** How subtitles drive SEO across Amazon/KDP, Google Play Books, Apple Books, and audio
platforms (Audible/ACX, Spotify, Ximalaya) — and the best available guidance for planning a
**series** (not a single book) across those platforms, including duration/pacing.

**Relationship to existing research (read these first — this doc does NOT repeat them):**
- [`docs/PLATFORM_ALGORITHM_RESEARCH_2026.md`](../../docs/PLATFORM_ALGORITHM_RESEARCH_2026.md) — single-book platform algorithm signals, completion-rate targets, chapter/book duration norms, seasonal windows. This doc **extends** it with series-specific pacing only.
- [`bestseller_titles_seo_covers_research.md`](bestseller_titles_seo_covers_research.md) — single-book title/subtitle formulas by market, KDP backend-keyword mechanics, cover specs (incl. §3.4 "Series Cover System" for the visual side of series design). This doc **extends** it with the metadata/SEO mechanics of a *series as its own object*, which §3.4 does not cover.
- [`docs/PODCAST_PLATFORM_MARKETING_RESEARCH.md`](../../docs/PODCAST_PLATFORM_MARKETING_RESEARCH.md) — podcast-specific title/description SEO, artwork anchors.
- [`docs/specs/session_mining_batch_20260718/STORE_SERIES_NAMING_ENGINE_V1_SPEC.md`](../../docs/specs/session_mining_batch_20260718/STORE_SERIES_NAMING_ENGINE_V1_SPEC.md) — the REFRESHED SPEC this research directly feeds. That spec asks for store-safe series naming with deterministic provenance; this doc supplies the platform-mechanics grounding it needs before `config/naming/series_taxonomy.yaml` gets built.
- **Citation-gap honesty bar (carried forward):** [`artifacts/research/citations/RCG-019_subtitle_patterns.md`](citations/RCG-019_subtitle_patterns.md) and `RCG-021_subtitle_patterns.md` found **no controlled A/B study anywhere** validating specific subtitle-pattern conversion lifts, for single books or series. Nothing in this doc claims a numeric conversion lift unless a primary source is cited with a URL; where no primary source exists, the finding is labeled "platform mechanic" (verified from the platform's own documentation) vs. "craft convention" (industry practice, unverified by controlled study).

---

## 1. Why series need different title/subtitle thinking than single books

A single book optimizes one title + one subtitle for one set of keywords. A **series** has to solve
a harder problem simultaneously across every book in it:

1. **Brand consistency** — the series name has to be the stable, exact-match anchor every storefront
   groups on (see §2 below — every platform that supports series linking requires **byte-identical**
   series-name strings across all books; a single typo, extra space, or inconsistent capitalization
   silently breaks the grouping and the series page never populates).
2. **Per-book differentiation** — each book's title + subtitle still has to carry its own unique
   keyword payload, or the series reads as one book chopped into N near-duplicates (a real risk
   flagged by Google Play's duplicate-content policy — see §2.2 for the precise scope of that rule).
3. **Reader promise + order legibility** — readers need to know both "is this the same trustworthy
   voice/brand" (series name) and "where do I start / what's different about this one" (title +
   subtitle + book number).
4. **Keyword non-cannibalization** — if every book in an 8-book series targets the identical
   long-tail keyword in its subtitle, the books compete against each other in search rather than
   collectively owning more search real estate (see §4).

This is exactly the gap the `STORE_SERIES_NAMING_ENGINE_V1_SPEC.md` requirements list names:
"produce store-safe series titles and subtitles with deterministic provenance" while preserving
"topic, persona, promise, tone, and author-brand constraints" and "prevent collisions across
current and planned series."

---

## 2. How subtitles (and series metadata) drive SEO, per storefront

### 2.1 Amazon / KDP

**Platform mechanic (verified from KDP's own help docs):**
- Title and subtitle are **auto-joined with a colon** on the detail page; combined they must be
  **≤200 characters** [KDP Metadata Guidelines](https://kdp.amazon.com/en_US/help/topic/G201097560).
- KDP's series feature is a **separate metadata object**, not derived from title/subtitle text:
  a **Series name** field (enter *only* the series name — never the book title or the number in
  this field) and a numeric-only **Series number** field
  [Start a Book Series](https://kdp.amazon.com/en_US/help/topic/GMFKBUS43QQ5AJ5A),
  [Edit your Series](https://kdp.amazon.com/en_US/help/topic/GJ3E8KQDLQ3NH3T9).
- The series detail page **auto-generates once ≥2 titles in the series are live**, appearing within
  **72 hours**; it shows all books in reading-order sequence with combined review counts, and
  Author Central can add a series-level description on top.
- **Non-obvious grounding point:** series grouping is keyed **entirely on the exact-match Series
  name string + Series number**, not on title or subtitle text similarity. This means Amazon gives
  you two *independent* levers: the **Series name** carries brand/discoverability equity across all
  books (must never vary by a single character), while **title + subtitle** on each book stays free
  to carry that book's unique keyword payload without needing to echo the series name at all — you
  do not need "SeriesName Book 3: Subtitle" as the actual title string; the series page does that
  labeling for you.
- **Backend keyword indexing:** unaffected by series structure — each book still gets its own 7×50-char
  keyword fields (see `bestseller_titles_seo_covers_research.md` §2.2); a series does not share or pool
  keyword slots, so each volume should still target book-specific long-tail keywords in its own fields.

**Craft convention (industry practice, no controlled-study citation):** "Book N of M" labeling
inside the title itself is common practice among indie publishers to aid readers browsing search
results (rather than the series page) — but this is redundant with the platform's own Series-number
display and adds character budget pressure against the 200-char combined limit; **recommendation:
rely on the platform's native series-number display rather than hand-writing "Book 3 of 8" into the
subtitle text**, reserving that character budget for keyword-bearing language instead.

### 2.2 Google Play Books

**Platform mechanic (verified from Partner Center help docs):**
- Series linking uses a **Series tab** with a **Series name** (must match **exactly** across every
  book — capitalization, spacing, punctuation) and a **Series number** (whole number, no gaps or
  repeats) [Get started with series](https://support.google.com/books/partner/answer/11069638?hl=en).
- **Genre-conditional display — this is the single most useful, non-obvious finding for Phoenix's
  catalog:** on the auto-generated series page, **comics/manga/light novels display the book's
  SUBTITLE + series name + number**, while **all other genres (including self-help/nonfiction —
  Phoenix's actual catalog) display the book's TITLE + series name + number, not the subtitle**.
  → **Implication for Phoenix:** for self-help series, the *title* (not the subtitle) is the field
  that actually surfaces on Google Play's series page. Subtitle SEO value on Google Play is confined
  to the individual book's own detail page and search indexing (title+subtitle+description are the
  "#1 search factor" per the existing research), not to series-page browsing.
- **Duplicate-content policy scope (precision correction to the existing repo doc):** Google's
  duplicate policy targets **duplicate copies of the same book** (identical or near-identical
  full text/ISBN reuse), *not* thematically-similar books in a series with distinct ISBNs, covers,
  and text [Publisher Content Policies](https://support.google.com/books/partner/answer/1067634?hl=en).
  A well-differentiated series (unique manuscript per volume, unique ISBN, unique cover, unique
  title/subtitle) is not itself a duplicate-content risk — the existing doc's "strictest anti-duplicate"
  framing should not be read as "series books trigger anti-duplicate flags"; it means *identical*
  content resubmitted under a new listing gets rejected.
- Metadata changes can take up to 48 hours to propagate.

### 2.3 Apple Books

**Platform mechanic (verified from Draft2Digital's aggregator docs, since most indie/small-press
distribution to Apple Books runs through an aggregator rather than direct submission):**
- **Series name** and **Volume number** are core metadata fields D2D passes through to Apple.
- **Apple's series-completeness rule:** "all series must be complete to date, with all books
  currently available in that series" — meaning **do not list a volume slot for an unpublished,
  future book**; add each volume to the series metadata only once it is actually live. This is a
  meaningfully different constraint from Amazon/Google Play (which tolerate an in-progress series
  with gaps in the visible catalog, since the series page is generated from whatever's live).
  → **Implication for Phoenix's catalog-scale series (e.g., Waystream's 800-title catalog):** if any
  series-grouping is later applied to Waystream titles for Apple Books distribution, series metadata
  submission should be staged to match actual publish order — never pre-declare the full planned
  volume count.
- Apple's ranking favors **complete, accurate metadata** over keyword density; subtitle is "optional
  but recommended for SEO" per the existing research, consistent with Apple's stated
  editorial-curation-plus-personalization ranking model.

### 2.4 Audio: Audible / ACX

**Platform mechanic (verified from ACX help docs) — the most important, least-obvious finding in
this whole doc:** ACX has **no independent series-metadata object**. The Title and Subtitle entered
during ACX title setup **must exactly match the Kindle/print edition's title and subtitle as they
appear on Amazon**; "part of a series" is communicated only informally, in producer/narrator
performance notes, not as a structured field
([Set up a title description on ACX](https://help.acx.com/s/article/acx-audiobook-profile)).
→ **This means an Audible series page is not built through the audiobook at all — it inherits from
the KDP ebook/print series-page setup on the same ASIN family.** The practical mechanism for Phoenix
to get audiobook titles grouped as a series on Audible/Amazon is to get the **Series name + Series
number exactly right on the linked KDP ebook/print edition** (§2.1); the audiobook rides on that
same series page once its ASIN is linked to the print/ebook edition. Do not treat "set up series
metadata for the audiobook" as a separate task from "set up series metadata for the book" — on
Amazon's ecosystem, they are the same task, done once, at the print/ebook SKU.

### 2.5 Audio: Spotify (audiobooks)

**Platform mechanic (verified from Spotify's own metadata guidance):** Spotify's audiobook catalog
grew from 150K to 700K+ titles as of the 2026 investor-day update
([Spotify newsroom, 2026-05-21](https://newsroom.spotify.com/2026-05-21/investor-day-audiobook-features-updates/)).
Spotify's metadata guidance explicitly states **"descriptions should be unique for each audiobook,
including those included in a series"** — but no dedicated structured "Series name / Series number"
field surfaced in the metadata/asset guide accessible in this pass
([SFA Metadata & Asset Guide](https://support.spotifycdn.com/pdf/SFA%20Metadata_Asset%20Guide_2024.pdf)).
→ **Honest gap:** unlike Amazon/Google Play/Apple, Spotify does not appear (from the primary sources
reachable in this session) to expose a first-class series taxonomy object. Discovery for a series on
Spotify likely relies on the existing algorithmic signals already documented in
`PLATFORM_ALGORITHM_RESEARCH_2026.md` (content embeddings via Sentence-BERT off title+description,
HGNN cross-domain signals, author-level browsing) rather than an explicit series grouping. **Practical
consequence:** on Spotify, the *title and description text* (not a series field) are doing all the
series-signaling work — repeating the series name as a consistent prefix or bracketed tag inside the
title text itself (e.g., "Series Name — Book Title") is the closest available lever, at the cost of
character budget, since there is no separate structured field to carry that signal instead.
This is flagged as a genuine platform gap, not a Phoenix authoring gap — re-verify against Spotify
for Authors' current dashboard directly before committing to a workaround, since aggregator/dashboard
UI can add fields the PDF guide doesn't document.

### 2.6 Audio: Ximalaya

**Honest finding:** Ximalaya's official open-platform documentation
([open.ximalaya.com](https://open.ximalaya.com/)) reachable in this session is **API-reference-only**
(album search/filter parameters: album ID, title, tags, category, price type) and does not surface a
creator-facing style guide for title/subtitle naming conventions or series structure. No primary
Ximalaya source was found describing subtitle-specific SEO mechanics.
- What **is** confirmed structurally: Ximalaya's content unit is the **专辑 (album)** — the series-
  equivalent container — holding individual audio tracks/episodes; album metadata includes title,
  tags, and a text introduction, with content subject to Chinese publishing-compliance review
  (already flagged in the existing repo research and `CLAUDE.md`-adjacent governance docs).
- Chinese-market naming conventions (idiom-style 4-character compounds, category taxonomy 个人成长/
  心理学/情感) are already documented in `bestseller_titles_seo_covers_research.md` §1.4 and §2.6 —
  this doc does not re-derive them.
- **Recommendation:** treat Ximalaya album/series mechanics as **unverified-pending-primary-source**
  until a session with confirmed Chinese-language creator-portal access (or a Chinese-market
  publishing partner) can review the actual 专辑创建 (album creation) flow directly. Do not assume
  parity with Amazon/Google Play's exact-match series-name mechanics without that verification.

---

## 3. Series planning + durations, per platform

Builds on `PLATFORM_ALGORITHM_RESEARCH_2026.md`'s existing single-book duration table — this section
adds only the **series-level pacing delta**.

### 3.1 How many books per series (craft convention, cited)

- No platform enforces a minimum/maximum series length. Practitioner convention for **standalone-
  linked nonfiction series** (each book complete on its own, series cohesion via shared theme/author
  voice — the model that fits Phoenix's persona/topic catalog structure) is **3–10+ books**; a tight
  **trilogy** structure (setup → complication → resolution) is the other common convention, but that
  maps to fiction arcs more than to self-help topic-cluster catalogs
  ([Goodreads series-length discussion](https://www.goodreads.com/topic/show/1915767-ideal-number-of-books-for-a-series)).
- **For Phoenix's existing catalog shape** (persona × topic × engine-angle cells), the natural series
  unit is **one series per persona-topic cluster** (e.g., all "burnout recovery for healthcare
  workers" cells as one series), not a pre-planned fixed N — series length should track how many
  distinct topic/engine-angle combinations that persona-cluster legitimately supports, consistent
  with [[project_atom_deficit_is_shape_not_count]]'s finding that thin pools are a shape problem, not
  a count target to hit artificially.

### 3.2 Per-platform episode/session duration inherited + series-specific delta

| Platform | Single-book norm (existing doc) | Series-specific delta |
|---|---|---|
| Audible | 5–6h self-help sweet spot, 15–30min chapters | Series volumes should hold that same per-volume runtime — do NOT compress later volumes just because "the reader is already invested"; completion-rate signal is scored per-title, not per-series, so every volume needs its own strong opening (highest drop-off is always the first 10–20 min of *that specific title*). |
| Spotify | Session-length/completion weighted, 15h/month included in Premium | A series gives Spotify's cross-domain/session-based algorithm more signal (repeat listening from the same author/series cluster) — but per-volume descriptions must stay unique (§2.5); do not let series volumes cannibalize each other's session-completion stats by shipping near-identical runtimes/structure. |
| Ximalaya | micro_book_15/20 episode format | Album (专辑) structure natively supports many short episodes under one container — this is the platform where a "series" and a "single long book split into episodes" are structurally closest; unverified whether Ximalaya's algorithm rewards a large multi-episode album differently from several standalone albums (flagged as an open question, not asserted). |
| Naver/Kakao | 90-min compact (Naver); serialized episodes (Kakao) | **Kakao's Wait-Until-Free (WUF) model, confirmed 2026:** free episodes unlock on a **24/12/8/3-hour regenerating pass**, with the latest ~10 episodes + a designated free-intro batch held back from the free rotation ([NamuWiki Kakao Page/System](https://en.namu.wiki/w/%EC%B9%B4%EC%B9%B4%EC%98%A4%ED%8E%98%EC%9D%B4%EC%A7%80/%EC%8B%9C%EC%8A%A4%ED%85%9C)). This is a genuine **series-native monetization structure** — it only works if content is already segmented into many short episodes releasing on a cadence, which is a materially different production pattern than Phoenix's current single-EPUB-per-cell assembly. Treat as a distinct future lane (episodic/serialized release), not a retrofit of the existing spine pipeline. |
| Amazon/Google/Apple/Kobo | standard_book/extended | No platform-enforced series pacing; box-set/bundle products need their **own separate ISBN/ASIN** distinct from the individual-volume ISBNs — "a single paperback of Book 1 and a three-book box set are completely different products" to retailer inventory systems ([UPCs.com ISBN rule](https://upcs.com/blog/box-sets-bundles-the-one-vs-many-isbn-rule/)); budget for a block of ISBNs per series if box-sets are planned, not one ISBN per title only. |

---

## 4. Cross-book keyword ladder (series-specific SEO strategy)

Grounded in the mechanics above, not a new invented framework:

1. **Series name = the fixed brand asset.** Locked, byte-identical across every book and every
   platform's series-linking field (§2.1–2.3). Carries the *category* keyword equity once (e.g., a
   series name that itself contains the core topic keyword benefits every volume's series-page
   grouping without needing to repeat it per-volume).
2. **Per-volume title = the distinguishing keyword.** Each book's title should target a **distinct**
   long-tail angle within the shared theme (matching the existing keyword-tier tables in
   `bestseller_titles_seo_covers_research.md` §4 — e.g., one volume takes "workplace anxiety," the
   next takes "sleep anxiety," the next "social anxiety," all under one series name) — this is what
   prevents the "8 near-duplicate books" cannibalization risk flagged in §1.
3. **Per-volume subtitle = the platform-specific SEO payload**, remembering it does **not** display on
   Google Play's series page for nonfiction (§2.2) and is auto-concatenated with a colon on Amazon
   (§2.1) — write it to read naturally as `Title: Subtitle` on Amazon/Apple/Kobo, and independently
   strong as a title-only string for Google Play's series-page context.
4. **Backend keywords (KDP) are per-book, not series-pooled** — do not economize by assuming the
   series name "covers" keyword ground for every volume; each volume still needs its own full 7×50-char
   keyword set targeting that volume's specific angle.

---

## 5. Open questions for the operator (recommend defaults; do not decide)

- **Q-SERIES-01 (Ximalaya verification):** the Ximalaya findings in §2.6 are the weakest-sourced
  section of this doc (no creator-facing primary source reached). *Default:* treat as
  unverified-pending-primary-source; do not build Ximalaya-specific series tooling off this doc alone.
- **Q-SERIES-02 (episodic/serialized lane):** Kakao's WUF model (§3.2) implies a structurally
  different production pattern (many short episodes vs. one EPUB per cell). *Default:* out of scope
  for the current spine pipeline; flag as a separate future lane if/when Phoenix pursues the Korean
  serialized-fiction-adjacent market specifically.
- **Q-SERIES-03 (box-set ISBN budget):** if Waystream or any brand plans box-set bundles, a
  block-ISBN purchase is needed ahead of time (§3.2). *Default:* not yet needed until a specific
  series is selected for box-set treatment — defer until that decision is live.

---

## Sources

### Series metadata mechanics
- [Start a Book Series — KDP](https://kdp.amazon.com/en_US/help/topic/GMFKBUS43QQ5AJ5A) (accessed 2026-07-23)
- [Edit your Series — KDP](https://kdp.amazon.com/en_US/help/topic/GJ3E8KQDLQ3NH3T9) (accessed 2026-07-23)
- [Metadata Guidelines for Books — KDP](https://kdp.amazon.com/en_US/help/topic/G201097560) (accessed 2026-07-23)
- [Get started with series — Google Play Books Partner Center](https://support.google.com/books/partner/answer/11069638?hl=en) (accessed 2026-07-23)
- [Publisher Content Policies — Google Play Books](https://support.google.com/books/partner/answer/1067634?hl=en) (accessed 2026-07-23)
- [Draft2Digital Knowledge Base](https://draft2digital.com/knowledge-base/) (accessed 2026-07-23)
- [Apple Books Formatting and Content Guidelines](https://help.apple.com/itc/applebooksstoreformatting/en.lproj/static.html) (accessed 2026-07-23)
- [Set up a title description on ACX](https://help.acx.com/s/article/acx-audiobook-profile) (accessed 2026-07-23)
- [Spotify Newsroom — 2026 Investor Day audiobook update](https://newsroom.spotify.com/2026-05-21/investor-day-audiobook-features-updates/) (accessed 2026-07-23)
- [Spotify for Authors Metadata & Asset Guide (PDF)](https://support.spotifycdn.com/pdf/SFA%20Metadata_Asset%20Guide_2024.pdf) (accessed 2026-07-23)
- [Ximalaya Open Platform](https://open.ximalaya.com/) (accessed 2026-07-23 — API reference only, no creator style guide reached)

### Series planning / duration
- [Goodreads — Ideal number of books for a series](https://www.goodreads.com/topic/show/1915767-ideal-number-of-books-for-a-series) (accessed 2026-07-23)
- [UPCs.com — Box Sets & Bundles ISBN rule](https://upcs.com/blog/box-sets-bundles-the-one-vs-many-isbn-rule/) (accessed 2026-07-23)
- [NamuWiki — Kakao Page/System (WUF model)](https://en.namu.wiki/w/%EC%B9%B4%EC%B9%B4%EC%98%A4%ED%8E%98%EC%9D%B4%EC%A7%80/%EC%8B%9C%EC%8A%A4%ED%85%9C) (accessed 2026-07-23)

### Carried-forward authority (not re-cited in body; see linked docs)
- `docs/PLATFORM_ALGORITHM_RESEARCH_2026.md`
- `artifacts/research/bestseller_titles_seo_covers_research.md`
- `docs/PODCAST_PLATFORM_MARKETING_RESEARCH.md`
- `artifacts/research/citations/RCG-019_subtitle_patterns.md`, `RCG-021_subtitle_patterns.md`
