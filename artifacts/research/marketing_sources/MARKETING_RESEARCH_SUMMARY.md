# Marketing research summary — 2026-03-31

## Provenance

- **Date:** 2026-03-31  
- **Agent:** Pearl_Research (Cursor / Claude)  
- **Tools:** Web search, `web_fetch` on public help and industry pages; **Claude-in-Chrome MCP unavailable** in this runtime.  
- **Prompt source:** `docs/research/MARKETING_DEEP_RESEARCH_PROMPTS.md` §1, §2, §5, §6, §7.

## Which sub-deliverables are complete

| Sub # | Topic | Standalone artifact | Status |
|-------|--------|---------------------|--------|
| 1 | Per-brand GTM & audience funnel | `sub1_gtm_audience_funnel.md` | **Complete** (cited industry + platform policy; keyword volumes explicitly `null`) |
| 2 | Controlled emotional vocabulary | `sub2_emotional_vocabulary.md` | **Complete** (policy-based risk; **no** public per-word conversion tables) |
| 3 | Consumer language vs. clinical | `config/marketing/consumer_language_by_topic.yaml` | **Already FULL** (pre-existing) |
| 4 | Invisible scripts | `config/marketing/invisible_scripts_by_persona_topic.yaml` | **Already FULL** (pre-existing) |
| 5 | Duration bands & consumption | `sub5_duration_bands.md` | **Complete** (cited reach + multitask context; completion curves **not** URL-sourced) |
| 6 | Cover design by audience | `sub6_cover_design.md` | **Complete** (cited Play + ACX specs + NN/g; segment **A/B** not URL-sourced) |
| 7 | Pricing & discount psychology | `sub7_pricing_topology.md` | **Complete** (cited Google bundles + list price mechanics + anchoring papers) |

## Key new findings **not** already evidenced in `brand_archetype_registry.yaml`

1. **Spotify chart-based audiobook discovery** — genre charts and weekly updates are documented in trade press and Spotify newsroom links cited in `sub1` (registry channels are generic placeholders).  
2. **Google Play bundle discount monotonicity** — tiered series discounts must **increase** with books purchased; invalid examples are in Google Help (`sub7`).  
3. **List price vs. sale price on Google Play** — List Price is **recommended** and may **not** equal customer sale price (`sub7`).  
4. **International price rounding** — up to **±5%** adjustment on currency-converted list prices for “appealing” endings (`sub7`).  
5. **Spam/misleading metadata** — explicit policy text covers **titles and covers**, with automated + human review (`sub1`, `sub2`, `sub6`).  
6. **Cover technical baseline** — Play recommends **2400×2400** square JPEG/PNG; ACX PDF specifies Audible square cover rules (`sub6`).  
7. **Emotional token performance** — **No** authoritative public URL maps tokens like “rewire” or “calm” to conversion or spam scores; registry numeric caps remain **internal** (`sub2`).

**Confirms registry:** Multi-channel discovery (search + audio surfaces) is **directionally consistent** with APA/Edison listening growth and Spotify charts (`sub1`).  
**Does not contradict** duration or pricing numerics in YAML; **does not validate** them with external experiments (`sub5`, `sub7`).

## Recommendations for config updates

1. **Optional overlay file** for `gtm_identity` research notes (mapping table in `sub1`) instead of editing 24 registry rows until keyword data exists.  
2. **Pricing ops checklist** referencing Google bundle tier math and list-price disclaimers before campaigns (`sub7`).  
3. **Cover QA script** enforcing 2400×2400, square, title/author legibility at thumbnail sizes (`sub6`).  
4. **Title experiments log** if marketing changes emotional caps—tie to provenance block in `MARKETING_DEEP_RESEARCH_PROMPTS.md` (`sub2`).  
5. **Competitive pricing snapshot pipeline** to replace guessed micro/mid/deep USD tiers (`sub7`).  
6. **Re-run or augment** with Chrome deep-research cascade when MCP is available for gated tools and long-form reports.

## Audit cross-reference

`artifacts/research/RESEARCH_AUDIT_2026_03_30.md` Section B items **15–22** updated to reflect these artifacts.
