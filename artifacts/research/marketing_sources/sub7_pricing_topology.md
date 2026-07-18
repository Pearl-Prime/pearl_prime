# Sub-deliverable 7 — Pricing topology & discount psychology

## Provenance (required)

```yaml
provenance:
  run_date: "2026-03-31"
  model: "Claude (Cursor agent) + web retrieval"
  temperature: "N/A"
  prompt_id: "7"
  query_submitted: |
    Do deep research on pricing and discount strategy for self-help audiobooks on Google Play,
    Audible, and Spotify (2025–2026). [docs/research/MARKETING_DEEP_RESEARCH_PROMPTS.md §7]
  source_links:
    - "https://support.google.com/books/partner/answer/11098073?hl=en"
    - "https://support.google.com/books/partner/answer/3238849?hl=en"
    - "https://support.google.com/books/partner/answer/166501?hl=en"
    - "https://www.audiopub.org/research-faq"
    - "https://www.gsb.stanford.edu/faculty-research/working-papers/anchoring-effects-consumers-willingness-pay-willingness-accept"
    - "https://journals.sagepub.com/doi/10.1177/0022243718808554"
  tools_used: ["Web search", "web_fetch (Google Play bundle + book prices + publisher policies)"]
  confidence: "high for Google bundle mechanics; medium for anchoring papers; low for exact micro/mid/deep USD tiers"
  reviewer: "TBD"
  notes: >
    Internal doc MARKETING_DEEP_RESEARCH_PROMPTS.md mentions Google Play price parity vs other stores;
    public help pages fetched here did not state a cross-retailer "MFN" rule—treat parity as contractual
    or ops policy if it exists, not as a cited Google URL.
```

## Executive summary

**Google Play series bundles (cited):** Partners may create **up to 3 discount tiers** per bundle campaign; **discount percentage must increase** as more books in the series are purchased; worked example shows **invalid** tiering when a higher book count gets a lower discount than a lower count [1].

**Google Play list price mechanics (cited):** For non-agency publishers, **List Price is only a recommended price** and **may not be the final sale price** on Google Play [2]. Separately, **book list prices** must fall between **$0.05 and $200 USD** (currency converted) [3]. **Currency conversion** can adjust international list prices by up to **±5%** for “visually appealing” price endings [3].

**Industry context (cited):** APA reports **$2.22B** publisher receipts in **2024** and **digital audiobooks = 99% of revenue** [4]—useful for **category revenue context**, not for setting Phoenix list prices.

**Behavioral pricing (cited, general):** Stanford GSB summarizes research on **anchoring effects** on willingness-to-pay [5]. Journal of Marketing research (Davis & Bagchi, 2018) analyzes **how consumers integrate multiple percentage discounts**—presentation order affects perceived value [6].

**Already in `brand_archetype_registry.yaml`:** Typical pattern includes `pricing_posture.micro_sessions` as a USD range, `deep_dives` range, and `discount_ratio: 0.20` (e.g. stabilizer) [7]. Validator doc in repo requires **`discount_ratio ≥ 0.20`** per internal contract [8].

## Answers to prompt questions

### 1. Tiered price points (micro / mid / deep)

**No cited public benchmark** for self-help **micro 15–30 min** vs **mid 45–90** vs **deep 3–6 hr** USD tiers in this run. **Action:** treat existing registry ranges [7] as **internal defaults** until competitive scrape with provenance is added.

### 2. Google Play bundle 15% / 25% / 35% tiers

Google’s documentation uses **example** tiers (e.g., 15%, 30%, 35%) and rules about **monotonicity** of discount vs books purchased [1]. It does **not** mandate 15/25/35 exactly—those numbers in the Phoenix prompt are **illustrative examples**, not quoted caps from the help page.

### 3. What % of catalog should be discounted?

**Not URL-sourced** for audiobooks specifically. Registry uses **`discount_ratio: 0.20`** [7][8].

### 4. Price anchoring vs everyday low price

**Academic support** for anchoring influencing price judgments [5][6]. **Does not specify** Audible/Google consumer outcomes for audiobooks—use for **hypothesis design** only.

### 5. Competitor benchmarks

APA industry stats [4] are **category revenue**, not **price ladders**. **Gap.**

### 6. Price sensitivity by audience

**Not cited** in this run beyond general self-help positioning notes.

## Cross-validation

| Topic | Finding A | Finding B | Verdict |
|-------|-----------|-----------|---------|
| Discount stacking clarity | Google bundle tier monotonicity [1] | Multi-discount presentation affects perception [6] | **Compatible** (different layers: policy vs psychology) |

## Structured output (YAML)

```yaml
pricing_research_sub7:
  google_play:
    series_bundle_rules:
      max_tiers: 3
      monotonic_discount_vs_book_count: required
      url: "https://support.google.com/books/partner/answer/11098073?hl=en"
    list_price_bounds_usd:
      min: 0.05
      max: 200.0
      url: "https://support.google.com/books/partner/answer/3238849?hl=en"
    list_price_not_final_sale_price:
      url: "https://support.google.com/books/partner/answer/166501?hl=en"
    currency_conversion_price_rounding:
      max_change_vs_converted_list: "5%"
      url: "https://support.google.com/books/partner/answer/3238849?hl=en"
  behavioral_economics:
    anchoring_willingness_to_pay:
      url: "https://www.gsb.stanford.edu/faculty-research/working-papers/anchoring-effects-consumers-willingness-pay-willingness-accept"
    multiple_percentage_discounts:
      url: "https://journals.sagepub.com/doi/10.1177/0022243718808554"
  industry_context:
    apa_revenue_2024:
      url: "https://www.audiopub.org/research-faq"
  registry_snapshot_example_stabilizer:
    micro_sessions: [3.99, 5.99]
    deep_dives: [17.99, 24.99]
    discount_ratio: 0.20
    source_file: "config/catalog_planning/brand_archetype_registry.yaml"
```

## New vs registry

- **New:** Google Play **bundle tier mechanics** and **list price ≠ sale price** citations [1][2][3].
- **Already in registry:** Numeric **bands** and **discount_ratio** [7]—research **neither confirms nor refutes** optimality.

## Recommendations

1. Build a **competitive price panel** (Play, Audible, Spotify) with scrape date + URL per observation—store under `marketing_sources/pricing_snapshots/`.
2. When running series promotions, **pre-check tier math** against Google’s monotonicity examples [1].
3. If Phoenix has a **private MFN/parity clause** with Google, **link the contract excerpt** in provenance; it was **not** found on public help pages in this run.

## References

[1] Google Play Books Partner Center, “Create bundle discounts for books in a series”, https://support.google.com/books/partner/answer/11098073?hl=en

[2] Google Play Books Partner Center, “Publisher Program Policies for Google Play Books” (List Price explained), https://support.google.com/books/partner/answer/166501?hl=en

[3] Google Play Books Partner Center, “Book prices”, https://support.google.com/books/partner/answer/3238849?hl=en

[4] Audio Publishers Association, “APA Research FAQ”, https://www.audiopub.org/research-faq

[5] Stanford Graduate School of Business, “Anchoring Effects on Consumers' Willingness-to-Pay and Willingness-to-Accept” (working paper page), https://www.gsb.stanford.edu/faculty-research/working-papers/anchoring-effects-consumers-willingness-pay-willingness-accept

[6] Derick F. Davis and Rajesh Bagchi (2018), Journal of Marketing, “How Evaluations of Multiple Percentage Price Changes Are Influenced by Presentation Mode and Percentage Ordering”, https://journals.sagepub.com/doi/10.1177/0022243718808554

[7] `config/catalog_planning/brand_archetype_registry.yaml` — `pricing_posture` (local file)

[8] `docs/research/MARKETING_DEEP_RESEARCH_PROMPTS.md` — decision-to-config contract table (`discount_ratio ≥ 0.20`)
