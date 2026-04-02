# Sub-deliverable 5 — Duration bands & consumption behavior

## Provenance (required)

```yaml
provenance:
  run_date: "2026-03-31"
  model: "Claude (Cursor agent) + web retrieval"
  temperature: "N/A"
  prompt_id: "5"
  query_submitted: |
    Do deep research on self-help audiobook listener preferences for duration in 2025–2026...
    [docs/research/MARKETING_DEEP_RESEARCH_PROMPTS.md §5]
  source_links:
    - "https://www.edisonresearch.com/how-many-americans-listen-to-audiobooks/"
    - "https://www.audiopub.org/research-faq"
    - "https://www.voices.com/company/press/reports/audiobook-habits"
  tools_used: ["Web search", "web_fetch (Edison, APA, Voices report page)"]
  confidence: "medium for reach/subscription context; low for completion-by-duration causality"
  reviewer: "TBD"
  notes: >
    Public industry stats support listening growth and context; fine-grained completion curves
    by 15/30/90 min buckets for self-help were not found as open URLs in this run.
```

## Executive summary

**Market scale (cited):** Edison + APA report **51% of US adults 18+ have ever listened to an audiobook** [1]. APA notes **digital = 99% of revenue** in 2024 [2]—distribution is overwhelmingly digital, which matters for **chapterization and micro-session SKUs**.

**Listening contexts (third-party industry survey — cite carefully):** Voices.com’s **Audiobook Habits** report (survey-based) states respondents often listen **while multitasking** and lists common activities (e.g., commute, chores) with percentages in their materials [3]. This supports **use-case segmentation** (commute vs wind-down) even when exact minute-level preferences differ by genre.

**Genre length guidance (non-academic guide — lower weight):** Secondary sources such as genre guides claim business/self-help often lands in **shorter finished-hour bands** than epic fiction; treat as **hypothesis** unless corroborated by publisher sales CSVs.

**Already in `brand_archetype_registry.yaml`:** Each brand has `duration_strategy` with `micro_sessions`, `deep_dives`, `mid_form` summing to 1.0, capped by `global_constraints.max_mid_form_ratio` (0.25) with **internal note: no external citation** [4].

**New findings:** Cited **growth + digital share + multitask listening** supports maintaining **micro + deep mix**; **does not prove** the exact 0.55/0.35/0.10 style splits in the registry.

## Answers to prompt questions (with evidence discipline)

1. **Preferred bands (15–30 / 45–90 / 3–6 hr):** **Not directly answered** by APA/Edison FAQs retrieved. **Inference only:** multitask listening [3] favors **shorter session-friendly chapter design**; deep listens remain plausible for **narrative nonfiction** and **integrated programs**.

2. **By use case:** Commute/chores multitasking appears in Voices survey framing [3]. **Sleep/wind-down** is a common marketing segment but **not individually cited** in the URLs fetched for this file—flag as **gap**.

3. **Completion rates by band:** **No URL** with completion curves for Phoenix-relevant taxonomy in this run.

4. **Perceived value (longer = better vs micro completion):** **No direct URL**; do not assert.

5. **Platform differences (Play / Audible / Spotify):** APA notes **72% say availability on preferred platform matters** and **63% value library access** [2]—platform **distribution** matters more than duration in that datum.

6. **“Middle underperforming” bifurcation:** **Not verified** with a cited study in this run.

## Cross-validation

| Theme | Edison/APA | Voices | Verdict |
|-------|------------|--------|---------|
| Audiobooks mainstream | Yes [1][2] | Survey audience self-selected [3] | **Compatible** (different methods) |

## Recommended allocation (explicitly hybrid)

**Policy:** The prompt asks for `%` allocation across 1,008 titles. Without completion curves, only **registry + uncertainty** is honest.

```yaml
duration_strategy_recommendation_sub5:
  basis: "registry_defaults_plus_cited_multitask_listening"
  cited_support:
    - "Multitask listening common per Voices Audiobook Habits [3]"
    - "Digital share dominant per APA FAQ [2]"
  allocation_percent:
    micro_sessions: "retain_registry_majority_until_experiment"
    deep_dives: "retain_registry_substantial_minority"
    mid_form: "keep_at_or_below max_mid_form_ratio 0.25 per registry validator [4]"
  confidence: "low_for_exact_percentages"
  registry_current_example_stabilizer:
    micro_sessions: 0.55
    deep_dives: 0.35
    mid_form: 0.10
  source_for_example: "config/catalog_planning/brand_archetype_registry.yaml stabilizer [4]"
```

## Recommendations

1. Instrument **completion %** by title duration bucket in Phoenix analytics, then revisit `duration_strategy`.
2. Use APA/Edison **genre revenue shares** [2] to stress-test nonfiction positioning (fiction-heavy revenue share implies discovery competition).

## References

[1] Edison Research, “How Many Americans Listen to Audiobooks?”, https://www.edisonresearch.com/how-many-americans-listen-to-audiobooks/

[2] Audio Publishers Association, “APA Research FAQ”, https://www.audiopub.org/research-faq

[3] Voices, “Audiobook Habits” (company report page), https://www.voices.com/company/press/reports/audiobook-habits

[4] `config/catalog_planning/brand_archetype_registry.yaml` — `global_constraints.max_mid_form_ratio`, per-brand `duration_strategy` (local file)
