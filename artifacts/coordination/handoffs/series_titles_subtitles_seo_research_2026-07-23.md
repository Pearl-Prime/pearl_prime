# Handoff — Series Titles/Subtitles Platform SEO Research (2026-07-23)

## What was found

Produced `artifacts/research/SERIES_TITLES_SUBTITLES_PLATFORM_SEO_RESEARCH_2026-07-23.md` — the
gap this fills: existing research (`PLATFORM_ALGORITHM_RESEARCH_2026.md`,
`bestseller_titles_seo_covers_research.md`, `PODCAST_PLATFORM_MARKETING_RESEARCH.md`) covers
single-book title/subtitle formulas and platform algorithm/duration data, but nothing covered
**series-level** naming mechanics or **audiobook-specific** subtitle SEO per platform.

Key findings (all cited with URL + accessed-date in the doc):

1. **Amazon KDP** has a dedicated Series object (exact-match Series name + numeric Series number,
   independent of title/subtitle text); series page auto-generates within 72h once ≥2 titles are live.
2. **Google Play's series page display is genre-conditional** — self-help/nonfiction (Phoenix's
   catalog) shows TITLE, not subtitle, on the series page. This is the single most actionable,
   non-obvious finding.
3. **Apple Books requires series-completeness** — don't pre-declare unpublished future volumes.
4. **Audible/ACX has no independent series field at all** — an audiobook's series-page membership is
   entirely inherited from the linked KDP ebook/print edition's series setup. This means "set up
   audiobook series metadata" is not a real separate task on Amazon's ecosystem.
5. **Spotify and Ximalaya** — weaker/unverified series taxonomy from the primary sources reachable
   this session; flagged honestly as gaps rather than guessed at.
6. **Kakao's Wait-Until-Free model** (24/12/8/3-hour regenerating free-episode passes) is a genuine
   series-native monetization structure, but implies episodic production, not a retrofit of the
   current single-EPUB-per-cell spine pipeline.
7. Corrected a precision point in the existing repo doc: Google Play's "duplicate content" policy
   targets identical/near-identical copies of the *same* book, not thematically-similar series volumes
   with distinct ISBNs/covers/text — a well-differentiated series is not itself a duplicate-content risk.

## What's still a citation gap

- Ximalaya's creator-facing title/subtitle/series style guide (§2.6 of the new doc) — no primary
  source reached; treat as unverified-pending-primary-source.
- Spotify's structured series metadata field (§2.5) — the reachable metadata PDF doesn't confirm one
  exists; re-verify against the live Spotify for Authors dashboard before building tooling around it.
- No controlled A/B study exists anywhere (carried forward from RCG-019/021) validating subtitle
  pattern conversion lifts — nothing in the new doc asserts a numeric lift without a primary source.

## What changed in the repo

- New: `artifacts/research/SERIES_TITLES_SUBTITLES_PLATFORM_SEO_RESEARCH_2026-07-23.md`
- New registry row: `series_titles_subtitles_seo_research` in `CANONICAL_ARTIFACTS_REGISTRY.tsv`
- Cross-link "See also" pointers added to `PLATFORM_ALGORITHM_RESEARCH_2026.md`,
  `bestseller_titles_seo_covers_research.md`, `PODCAST_PLATFORM_MARKETING_RESEARCH.md`
- "Research inputs available" note added to `STORE_SERIES_NAMING_ENGINE_V1_SPEC.md`

## Next action

Hand this doc + the STORE_SERIES_NAMING_ENGINE_V1_SPEC.md to a Pearl_Dev lane to build
`config/naming/series_taxonomy.yaml` (out of scope for this research-only lane — no code was
touched). That lane should specifically implement: (a) exact-match series-name locking across
KDP/Google Play/Apple metadata submission, (b) the cross-book keyword ladder (§4 of the new doc) in
the naming engine's candidate generation, (c) staged series-metadata submission matching actual
publish order for Apple Books.

acceptance-layer: RESEARCHED (feeds a SPECCED spec; no code touched)
