# Sub-deliverable 6 — Cover design language by audience

## Provenance (required)

```yaml
provenance:
  run_date: "2026-03-31"
  model: "Claude (Cursor agent) + web retrieval"
  temperature: "N/A"
  prompt_id: "6"
  query_submitted: |
    Do deep research on audiobook cover art that converts for self-help/wellness audiences...
    [docs/research/MARKETING_DEEP_RESEARCH_PROMPTS.md §6]
  source_links:
    - "https://support.google.com/books/partner/answer/14187606?hl=en"
    - "https://support.google.com/books/partner/answer/1067634?hl=en"
    - "https://www.nngroup.com/articles/mobile-list-thumbnail/"
    - "https://www.nngroup.com/articles/text-over-images/"
    - "https://images-na.ssl-images-amazon.com/images/G/01/Audible/en_US/acx/pdf/OfficialAudibleCover-ArtRequirements.pdf"
  tools_used: ["Web search", "web_fetch (Google Play cover help, NN/g articles)"]
  confidence: "high for platform specs; low for segment-specific conversion rates by palette"
  reviewer: "TBD"
  notes: >
    ACX PDF is industry-standard reference for Audible; agent did not re-fetch PDF bytes.
    Segment-level “what converts” beyond usability heuristics is largely not URL-proven here.
```

## Executive summary

**Platform requirements (cited):** Google Play Books specifies **1:1 aspect ratio**, recommends **2400×2400 px**, **JPEG or PNG**, under **2 GB** for cover uploads in Partner Center guidance [1]. **Misleading covers** are prohibited alongside misleading titles under Play Books content policies [2].

**Thumbnail usability (cited, general UX):** Nielsen Norman Group notes thumbnails on mobile are only useful when they **carry distinguishable information**; overly generic thumbnails add noise [3]. For **text over images**, NN/g summarizes **contrast** expectations (WCAG-related thresholds in their article) [4]—relevant because **title/author must remain legible at small sizes**.

**Audible / ACX (cited PDF URL):** Amazon publishes **Official Audible Cover Art Requirements** as a PDF including **minimum 2400×2400**, square, title and author on art, RGB, etc. [5].

**Already in `brand_archetype_registry.yaml`:** Each brand includes `cover_art_identity.style_pool` and `color_palette` (e.g. stabilizer: `minimalist_gradient`, `muted_blue`/`warm_sand`) [6]. This file **does not duplicate** every brand row; it adds **platform + UX constraints** and **honest gaps** for “conversion by segment.”

## Answers to prompt questions

### 1–2. Visual styles & palettes by segment (burnout, ADHD, sleep, career, grief, relationships)

**Not URL-sourced as A/B conversion rates per segment** in this run. **Heuristic recommendations** (compatible with registry, not proven):

| Segment | Style direction (hypothesis) | Palette hypothesis | Why cautious |
|---------|----------------------------|--------------------|--------------|
| Burnout / regulation | Calm minimal, generous whitespace | Muted cool + warm neutrals | Aligns stabilizer registry [6]; no public A/B |
| Focus / ADHD | High-contrast typographic anchor | Bold accent + dark ground | Legibility bias from NN/g [3][4] |
| Sleep / anxiety wind-down | Dark minimal, low visual noise | Deep blue / slate | Fits night_reset palette patterns [6] |
| Career | Structured grid / crisp sans | Navy + gold sparingly | Common category language—**not** uniquely cited |
| Grief | Soft gradient, avoid stock “happy” | Desaturated earth | Emotional tonality—**brand safety** review needed [2] |
| Relationships | Warm humanist tone (not clip-art people) | Rose/clay neutrals | Subjective |

### 3. Clicked vs ignored (Play / Audible / Spotify)

**No first-party A/B URL** from those storefronts in this run. **Proxy:** misleading or confusing cover/metadata reduces trust per policy [2]; **legibility** constraints from NN/g [3][4].

### 4. Thumbnail requirements (cited)

- **Square 2400×2400 recommended** on Google Play [1].
- **ACX/Audible square high-res** requirements [5].

### 5. Trends (oversaturated vs emerging)

**Not cited** with durable URLs here—avoid claims.

## Banned styles (segment hints — policy/usability grounded)

Per [2], avoid **covers that confuse format or mimic other titles**. Per [3], avoid **generic abstract blobs** that do not differentiate at thumbnail size.

```yaml
cover_art_research_sub6:
  platform_specs:
    google_play:
      aspect_ratio: "1:1"
      recommended_pixels: [2400, 2400]
      formats: ["jpeg", "png"]
      url: "https://support.google.com/books/partner/answer/14187606?hl=en"
    audible_acx_pdf:
      url: "https://images-na.ssl-images-amazon.com/images/G/01/Audible/en_US/acx/pdf/OfficialAudibleCover-ArtRequirements.pdf"
  usability_guides:
    nn_group_mobile_thumbnails: "https://www.nngroup.com/articles/mobile-list-thumbnail/"
    nn_group_text_over_images: "https://www.nngroup.com/articles/text-over-images/"
  registry_alignment:
    note: "Existing style_pool and color_palette per brand in brand_archetype_registry.yaml [6]"
```

## Recommendations

1. **Automate QA:** script to verify **2400×2400**, **RGB**, **title/author present** before ingest [1][5].
2. **Mobile preview:** generate **96×96 and 256×256** mocks to apply NN/g thumbnail tests [3].
3. **Run category A/B** on a small Phoenix subset; log winners in `marketing_sources/` with experiment provenance.

## References

[1] Google Play Books Partner Center, “Upload or update a cover image”, https://support.google.com/books/partner/answer/14187606?hl=en

[2] Google Play Books Partner Center, “Publisher Content Policies for Google Play Books”, https://support.google.com/books/partner/answer/1067634?hl=en

[3] Nielsen Norman Group, “List Thumbnails on Mobile: When to Use Them and Where to Place Them”, https://www.nngroup.com/articles/mobile-list-thumbnail/

[4] Nielsen Norman Group, “Ensure High Contrast for Text Over Images”, https://www.nngroup.com/articles/text-over-images/

[5] Amazon Audible, “Official Audible Cover Art Requirements” (PDF), https://images-na.ssl-images-amazon.com/images/G/01/Audible/en_US/acx/pdf/OfficialAudibleCover-ArtRequirements.pdf

[6] `config/catalog_planning/brand_archetype_registry.yaml` — `cover_art_identity` blocks (local file)
