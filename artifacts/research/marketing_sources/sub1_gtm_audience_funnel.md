# Sub-deliverable 1 — Per-brand GTM & audience funnel

## Provenance (required)

```yaml
provenance:
  run_date: "2026-03-31"
  model: "Claude (Cursor agent) + web retrieval"
  temperature: "N/A (synthesis over fetched pages)"
  prompt_id: "1"
  query_submitted: |
    Do deep research on go-to-market and audience discovery for 24 self-help audiobook
    brand archetypes in the US market (2025–2026). [Full prompt: docs/research/MARKETING_DEEP_RESEARCH_PROMPTS.md §1]
  source_links:
    - "https://www.edisonresearch.com/how-many-americans-listen-to-audiobooks/"
    - "https://www.audiopub.org/research-faq"
    - "https://www.theverge.com/entertainment/886037/spotify-audiobook-charts"
    - "https://newsroom.spotify.com/2026-02-27/audiobook-charts-launch/"
    - "https://support.google.com/books/partner/answer/1067634?hl=en"
  tools_used:
    - "Web search"
    - "web_fetch (Edison, APA, Google Play policies, The Verge)"
    - "Claude-in-Chrome MCP: unavailable in this runtime"
  confidence: "medium"
  reviewer: "TBD"
  notes: >
    Industry stats are well-cited; per-archetype keyword volumes and conversion rates are NOT
    available from public URLs in this run—those rows are framed as hypotheses aligned to registry.
```

## Executive summary

US audiobook reach is large and growing: Edison Research and the Audio Publishers Association (APA) report **51% of Americans 18+ have ever listened to an audiobook** (~134 million people), with rising interest among non-listeners [1]. APA summarizes **$2.22B publisher receipts in 2024** and notes **digital audiobooks = 99% of revenue** [2]. **Fiction dominates revenue share (67% in APA FAQ)** [2], so nonfiction/self-help publishers should assume **share-of-voice competition** with fiction in charts and recommendations.

**Discovery (platform-level, cited):** Spotify launched **audiobook charts including genre-specific charts**, improving browse-based discovery versus undifferentiated lists [3][4]. Google Play Books prohibits **misleading titles/metadata** and spam patterns under publisher content policies—metadata is explicitly used in automated and human review [5].

**Already in `brand_archetype_registry.yaml`:** Each brand already has `gtm_identity` (persona, age_range, primary_moment, emotional_job, functional_job) and `discovery_contract` (primary_channels, keyword_clusters). This artifact **does not replace** those fields; it adds **cited market context**, **funnel framing**, and **gaps** for future keyword-volume work.

## Cross-validation

| Claim | Source A | Source B | Verdict |
|-------|----------|----------|---------|
| ~51% US adults ever listened | Edison article [1] | APA FAQ [2] | **Aligned** |
| Spotify chart-based discovery | The Verge [3] | Spotify newsroom URL cited by Verge [4] | **Aligned** (primary narrative from [3]) |

## Funnel template (apply per brand)

Cited platform behavior supports this generic funnel; numeric conversion rates **not** found in public sources for self-help specifically.

1. **Awareness:** Search (Play), charts/browse (Spotify), samples/clips (YouTube—listener time on YouTube for audio is widely discussed in industry press; **not** deep-cited here).
2. **Consideration:** Metadata clarity (title/subtitle/cover) must not violate misleading/spam rules on Play [5].
3. **Purchase:** Price band + subscription benefits (platform-specific; see sub7).

## Prompt brand type → `brand_id` mapping (24 → 24)

One-to-one mapping for ingestion planning. **Registry remains authoritative** for IDs.

| # | Prompt brand type | Mapped `brand_id` | Rationale (brief) |
|---|-------------------|-------------------|-------------------|
| 1 | nervous system regulation | stabilizer | Regulation / burnout framing |
| 2 | somatic reset | healing_ground | Recovery / somatic |
| 3 | sleep repair | night_reset | Sleep |
| 4 | panic first aid | executive_calm | Acute regulation / performance stress |
| 5 | emotional resilience | stoic_edge | Resilience / discipline |
| 6 | grief companion | trauma_path | Grief / heavy emotional |
| 7 | gentle recovery | gentle_growth | Soft growth |
| 8 | inner security | spiritual_ground | Safety / grounding |
| 9 | breathwork | spiritual_ground | Breath / grounding / contemplative body |
| 10 | focus training | focus_sprint | Focus sprints |
| 11 | ADHD systems | adhd_forge | ADHD systems |
| 12 | dopamine balance | optimizer | Dopamine / efficiency |
| 13 | habit building | morning_momentum | Habits / momentum |
| 14 | clarity/decision | minimal_mind | Clarity / minimal |
| 15 | high efficiency | high_performer | Peak performance |
| 16 | energy return | longevity_lab | Energy / vitality lab framing |
| 17 | movement flow | bio_flow | Movement / somatic flow |
| 18 | metabolic stability | hormone_reset | Metabolic / hormones |
| 19 | boundaries | relationship_clarity | Relationship / boundaries |
| 20 | attachment repair | resilient_parent | Attachment framed as parenting/family resilience brand |
| 21 | communication clarity | career_lift | Workplace / professional communication and influence |
| 22 | Gen Z anxiety | calm_student | Student / Gen Z |
| 23 | identity rebuild | confidence_core | Identity / confidence |
| 24 | shadow work | creative_unfold | Depth / creative identity |

**New vs registry:** Mapping and funnel stages are **new** in this file. Personas/channels/keywords **already exist** per brand in YAML—diff any brand with `discovery_contract` before overwriting.

## Structured GTM brief (YAML excerpt — 3 sample brands)

Full registry has 24 brands; below shows pattern. **Keyword volumes:** not sourced—mark `null`.

```yaml
gtm_research_sub1_samples:
  stabilizer:
    primary_buyer_persona: "burned_out_professional"
    jobs_to_be_done:
      emotional_job: "calm nervous system"
      functional_job: "somatic regulation"
    discovery_channels_ranked:
      - channel: "google_play_search"
        evidence: "Registry default; Play is major Android book/audio surface"
      - channel: "spotify_charts_browse"
        evidence: "Spotify genre/chart discovery launch [3][4]"
    keyword_clusters:
      primary: ["nervous system regulation", "burnout recovery"]
      secondary: ["vagus nerve", "somatic calm"]
      search_volume_estimates_usd: null
    funnel:
      awareness: ["search", "social_audio_clips"]
      consideration: ["clear_metadata", "sample_quality"]
      purchase: ["price_fit", "subscription_inclusion"]
    citations: [1, 2, 3, 5]
  night_reset:
    primary_buyer_persona: "insomnia_wind_down"
    jobs_to_be_done:
      emotional_job: "feel safe to sleep"
      functional_job: "sleep onset support"
    discovery_channels_ranked:
      - channel: "google_play_search"
        evidence: "High-intent queries ('can't sleep') typical for sleep content—hypothesis; not URL-sourced"
      - channel: "spotify_audiobooks"
        evidence: "Chart/browse surfaces exist [3][4]"
    keyword_clusters:
      primary: ["sleep anxiety audiobook", "wind down meditation sleep"]
      secondary: ["sleep routine", "calm at night"]
      search_volume_estimates_usd: null
    funnel:
      awareness: ["nighttime_search", "wellness_playlists"]
      consideration: ["subtitle_signals_use_case", "duration_fit"]
      purchase: ["single_title_vs_subscription"]
    citations: [1, 2, 3]
  adhd_forge:
    primary_buyer_persona: "neurodivergent_focus_seeker"
    jobs_to_be_done:
      emotional_job: "feel in control"
      functional_job: "build ADHD-friendly systems"
    discovery_channels_ranked:
      - channel: "youtube_audio_clips"
        evidence: "Registry includes youtube_audio_clips for several brands; YouTube listening cited in APA piracy context (competition from free audio) [2]"
      - channel: "google_play_search"
        evidence: "Intent queries for ADHD systems"
    keyword_clusters:
      primary: ["ADHD audiobook", "focus systems ADHD"]
      secondary: ["body doubling audio", "ADHD habits"]
      search_volume_estimates_usd: null
    citations: [2, 5]
```

## Recommendations (config)

1. **Keep** existing `gtm_identity` / `discovery_contract` until keyword volume tooling (e.g. Search Console, paid keyword APIs) is attached—**do not** invent volumes.
2. Add optional `_research_note` fields in a **separate** overlay file if you want to avoid touching locked registry (per internal validator rules in MARKETING_DEEP_RESEARCH_PROMPTS.md).
3. Resolve **mapping collisions** (movement flow vs bio_flow; three relationship_clarity prompt types) in a future dedicated taxonomy review.

## References

[1] Edison Research, “How Many Americans Listen to Audiobooks?” (survey with APA), https://www.edisonresearch.com/how-many-americans-listen-to-audiobooks/

[2] Audio Publishers Association, “APA Research FAQ”, https://www.audiopub.org/research-faq

[3] The Verge, “Spotify launches audiobook charts…”, https://www.theverge.com/entertainment/886037/spotify-audiobook-charts

[4] Spotify Newsroom (linked from The Verge), Audiobook charts launch, https://newsroom.spotify.com/2026-02-27/audiobook-charts-launch/

[5] Google Play Books Partner Center, “Publisher Content Policies for Google Play Books” (spam/misleading metadata), https://support.google.com/books/partner/answer/1067634?hl=en
