# Sub-deliverable 2 — Controlled emotional vocabulary

## Provenance (required)

```yaml
provenance:
  run_date: "2026-03-31"
  model: "Claude (Cursor agent) + web retrieval"
  temperature: "N/A"
  prompt_id: "2"
  query_submitted: |
    Do deep research on emotional trigger words in self-help audiobook titles: which words drive
    conversion vs. trigger platform spam detection (Google Play, Audible, Spotify) in 2025–2026?
    [docs/research/MARKETING_DEEP_RESEARCH_PROMPTS.md §2]
  source_links:
    - "https://support.google.com/books/partner/answer/1067634?hl=en"
    - "https://support.google.com/googleplay/android-developer/answer/9898842?hl=en"
  tools_used: ["Web search", "web_fetch (Google Play Books policies, Play Console metadata policy)"]
  confidence: "low-to-medium for token-level quotas; high for policy-derived risk framing"
  reviewer: "TBD"
  notes: >
    No authoritative public URL was found that lists per-word conversion rates or Audible/Spotify
    title-level spam allowlists. Findings below separate (A) policy-backed platform risk from
    (B) internal registry quotas already in YAML.
```

## Executive summary

**What we can cite:** Google Play Books **Publisher Content Policies** prohibit metadata that is **misleading**, **spam**, or **confusingly similar** to other books, including misleading titles [1]. Google Play **(apps) metadata policy** states metadata must not be **misleading, improperly formatted, non-descriptive, irrelevant, excessive, or inappropriate** [2]—useful analogy for how Google reasons about store listings, though the book-specific policy [1] is the direct citation for Play **Books**.

**What we cannot cite (honest gap):** Public documentation reviewed in this run does **not** provide word-level labels such as “`calm` = high conversion” or “`rewire` = flagged.” **Any numeric conversion signal for individual tokens would be fabrication** without first-party A/B data.

**Already in `brand_archetype_registry.yaml`:** `global_constraints.emotional_token_global_caps` (`reset`, `clarity`, `calm`) and `emotional_token_global_caps_source.note` explicitly state **no external citation**—internal engineering defaults [3]. Per-brand `emotional_vocabulary.allowed_tokens` and `quota_exceptions` are also present [3].

**Contradiction check:** This research **does not contradict** the registry; it **does not validate** the numeric caps either—those still require internal experiments or licensed market research.

## Platform risk framework (policy-based, not word-scored)

| Risk band | Meaning | Action for Phoenix |
|-----------|---------|---------------------|
| **Structural** | Misleading / confusing metadata | Avoid look-alike titles, false format cues [1] |
| **Spam / quality** | Spam, poor UX, duplicate confusion | Avoid duplicate editions confusion; ensure descriptive titles [1] |
| **App-store parallel** | Irrelevant or excessive metadata | Avoid stuffing; keep subtitles readable [2] |

## Word list (prompt §2) — structured table

**Conversion performance signal:** set to **`unknown`** for all tokens (no URL).

**Platform risk:** **`policy_dependent`** = must not be used in misleading/spam patterns per [1]; not an assertion the word is banned.

| Word | Conversion signal | Platform risk | Topic affinity (heuristic) | Registry overlap |
|------|--------------------|--------------|----------------------------|------------------|
| reset | unknown | policy_dependent | burnout, nervous system | **In global caps** [3] |
| calm | unknown | policy_dependent | anxiety, sleep | **In global caps** [3] |
| clarity | unknown | policy_dependent | decision, focus | **In global caps** [3] |
| grounded | unknown | policy_dependent | somatic, anxiety | allowed_tokens e.g. stabilizer [3] |
| regulation | unknown | policy_dependent | nervous system | allowed_tokens stabilizer [3] |
| safety | unknown | policy_dependent | trauma-adjacent care | allowed_tokens stabilizer [3] |
| release | unknown | policy_dependent | somatic, grief | varies by brand |
| momentum | unknown | policy_dependent | habits, career | common in self-help titles |
| focus | unknown | policy_dependent | ADHD, productivity | optimizer cluster |
| discipline | unknown | policy_dependent | stoic / performance | stoic_edge |
| rest | unknown | policy_dependent | sleep, burnout | night_reset |
| repair | unknown | policy_dependent | recovery | healing_ground |
| anchor | unknown | policy_dependent | anxiety | metaphor-heavy |
| steady | unknown | policy_dependent | regulation | stabilizer |
| flow | unknown | policy_dependent | performance, ADHD | bio_flow |
| choice | unknown | policy_dependent | decision | minimal_mind |
| unstuck | unknown | policy_dependent | career, anxiety | career_lift |
| restore | unknown | policy_dependent | recovery | healing_ground |
| reclaim | unknown | policy_dependent | boundaries, confidence | confidence_core |
| rewire | unknown | policy_dependent | neuroscience framing | **higher metaphor load—test with legal/compliance** |
| regulate | unknown | policy_dependent | nervous system | stabilizer |
| settle | unknown | policy_dependent | anxiety, sleep | night_reset |
| soothe | unknown | policy_dependent | sleep, somatic | night_reset |
| trust | unknown | policy_dependent | attachment, anxiety | relationship_clarity |
| enough | unknown | policy_dependent | self-worth | confidence_core |
| worthy | unknown | policy_dependent | self-worth | confidence_core |
| seen | unknown | policy_dependent | relational healing | relationship_clarity |
| held | unknown | policy_dependent | grief, trauma tone | trauma_path |
| supported | unknown | policy_dependent | burnout | stabilizer |

**Saturation / opportunity:** **Not URL-sourced.** Qualitative note only: terms like **calm**, **reset**, **anxiety**, and **sleep** appear frequently in consumer self-help; differentiation may require **persona-specific subtitles** (see existing `consumer_language_by_topic.yaml`) rather than avoiding the token entirely.

## YAML fragment (machine-readable)

```yaml
emotional_vocabulary_research_sub2:
  policy_citations:
    google_play_books_spam_misleading: "https://support.google.com/books/partner/answer/1067634?hl=en"
    play_console_metadata_analogy: "https://support.google.com/googleplay/android-developer/answer/9898842?hl=en"
  per_word_defaults:
    conversion_performance_signal: unknown
    platform_risk_model: policy_dependent
  registry_fields_already_populated:
    - global_constraints.emotional_token_global_caps
    - per-brand emotional_vocabulary.allowed_tokens
  recommended_next_step:
    - "Run title-level A/B tests per platform; store results in marketing_sources with experiment_id"
    - "Add compliance review for trauma/grief wording (not spam, but brand safety)"
```

## Recommendations

1. **Treat registry numeric caps as internal hypotheses** until backed by experiment logs; do not claim APA/Edison validation for token caps.
2. **Prioritize compliance** with misleading-metadata rules [1] over optimizing rare synonyms.
3. **Do not** publish per-word “banned on Audible” lists without Audible primary policy URLs (not retrieved in this run).

## References

[1] Google Play Books Partner Center, “Publisher Content Policies for Google Play Books”, https://support.google.com/books/partner/answer/1067634?hl=en

[2] Google Play Console Help, “Metadata” (Android app listings; analog for metadata discipline), https://support.google.com/googleplay/android-developer/answer/9898842?hl=en

[3] `config/catalog_planning/brand_archetype_registry.yaml` — `global_constraints.emotional_token_global_caps`, per-brand `emotional_vocabulary` (local file; not a web URL)
