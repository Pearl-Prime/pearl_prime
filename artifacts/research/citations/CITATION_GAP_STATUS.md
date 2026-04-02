# Citation Gap Status Tracker

**Authority:** `docs/RESEARCH_CITATION_GAP_DEV_SPEC.md`
**Last updated:** 2026-04-01

## Legend

| Status | Meaning |
|--------|---------|
| MEMO_CORRECT | Research memo written addressing the CORRECT topic from the audit/spec |
| INLINE_DONE | Memo written AND target file updated with `_source:` or `## References` |
| OPEN | No memo or research completed |
| N/A | Not applicable (internal/operational) |

---

## Spec section A — 22 citation gaps

### Batch 1 — HIGH (RCG-001 to RCG-005)

| RCG-ID | Audit item | Claim summary | Memo path | Verdict | Memo status | Inline status | Notes |
|--------|------------|---------------|-----------|---------|-------------|---------------|-------|
| RCG-001 | 1 | Sleep complaints risen 40% in a decade | `RCG-001_sleep_complaints_trend.md` | PARTIALLY_CONFIRMED | MEMO_CORRECT | OPEN | Trend is real but 40% figure overstates published data (CDC/BRFSS show ~14-15% relative increase). Recommend softening. |
| RCG-002 | 2 | Amygdala/PFC regulation metaphor | `RCG-002_amygdala_pfc_regulation.md` | PARTIALLY_CONFIRMED | MEMO_CORRECT | OPEN | PFC-amygdala circuits well-established (Ochsner & Gross 2005). "Stops running the show" oversimplifies. Label as metaphor. |
| RCG-003 | 3 | Willpower is a limited resource (ego depletion) | `RCG-003_ego_depletion_contested.md` | UNCONFIRMED | MEMO_CORRECT | OPEN | Failed major replication (Hagger et al. 2016, 23-lab, d=0.04). Current consensus: contested. Do not present as fact. |
| RCG-004 | 4 | Persona revenue TAM ($555-730M aggregate) | `RCG-004_persona_revenue_TAM.md` | NEEDS_PRIMARY_SOURCE | MEMO_CORRECT | OPEN | Aggregate exceeds likely US self-help audiobook market. Methodology undisclosed. Label provisional. |
| RCG-005 | 5 | Bestseller structure bibliography | `RCG-005_bestseller_structure_bibliography.md` | CONFIRMED | MEMO_CORRECT | OPEN | All named works verified with full ISBNs. Need to add References section to source doc. |

### Batch 2 — MEDIUM (RCG-006 to RCG-018, RCG-021, RCG-022)

| RCG-ID | Audit item | Claim summary | Memo path | Verdict | Memo status | Inline status | Notes |
|--------|------------|---------------|-----------|---------|-------------|---------------|-------|
| RCG-006 | 6 | "yet" changes neural pathways | `RCG-006_growth_mindset_yet.md` | UNCONFIRMED | MEMO_CORRECT | OPEN | No study supports single-word neural pathway change. Growth mindset is real but modest (Sisk et al. 2018 d=0.08). |
| RCG-007 | 7 | Nervous system evolved to protect you | `RCG-007_nervous_system_protection.md` | PARTIALLY_CONFIRMED | MEMO_CORRECT | OPEN | General evolutionary framing sound (Cannon 1932). Polyvagal-specific framing contested (Grossman & Taylor 2007). |
| RCG-008 | 8 | Healthcare RNs 3.4M workforce | `RCG-008_healthcare_rn_workforce.md` | CONFIRMED | MEMO_CORRECT | OPEN | Matches BLS OEWS (~3.18M) and NCSBN survey (~3.4M employed in nursing). |
| RCG-009 | 9 | First Responders 2.5M workforce | `RCG-009_first_responders_workforce.md` | PARTIALLY_CONFIRMED | MEMO_CORRECT | OPEN | Plausible under broad definition. Narrow (police+fire+EMS) is ~1.3M. Specify definition. |
| RCG-010 | 10 | Dhaka floods / 40,000 students lede | `RCG-010_dhaka_floods_lede.md` | UNCONFIRMED | MEMO_CORRECT | OPEN | No matching news report found. Appears composite. Label as illustrative example. |
| RCG-011 | 11 | "Amara Odhiambo" Nairobi climate organizer | `RCG-011_nairobi_composite.md` | UNCONFIRMED | MEMO_CORRECT | OPEN | No public record of this person. Label as composite/fictional. |
| RCG-012 | 12 | Emotional token caps (reset:12, clarity:18, calm:24) | `RCG-012_emotional_token_caps.md` | NEEDS_PRIMARY_SOURCE | MEMO_CORRECT | OPEN | Internal calibration. No external A/B or benchmark found. Label as engineering default. |
| RCG-013 | 13 | 12 personas as market segments | `RCG-013_persona_segment_validation.md` | NEEDS_PRIMARY_SOURCE | MEMO_CORRECT | OPEN | Directionally consistent with Edison/APA/Pew data. Not validated by dedicated segmentation study. |
| RCG-014 | 14 | $2.22B, 13% growth, 51% adults listened | `RCG-014_apa_audiobook_stats.md` | PARTIALLY_CONFIRMED | MEMO_CORRECT | OPEN | Figures directionally correct per APA/Edison. Specific edition/page citation needed. |
| RCG-015 | 15 | Recommender scoring weights | `RCG-015_recommender_weights.md` | NEEDS_PRIMARY_SOURCE | MEMO_CORRECT | OPEN | Documentation gap. Add provenance labels (hand-tuned vs. A/B-derived). |
| RCG-016 | 16 | Teacher profile audience assumptions | `RCG-016_teacher_profile_audience.md` | NEEDS_PRIMARY_SOURCE | MEMO_CORRECT | OPEN | 480 rows with editorially constructed assumptions. Add provenance header. |
| RCG-017 | 17 | Brand archetype taxonomy | `RCG-017_brand_archetype_taxonomy.md` | PARTIALLY_CONFIRMED | MEMO_CORRECT | OPEN | Framework rooted in Jung/Pearson tradition. Specific application is internal. |
| RCG-018 | 18 | PIVOT/TAKEAWAY/THREAD/PERMISSION slots | `RCG-018_chapter_slot_craft.md` | PARTIALLY_CONFIRMED | MEMO_CORRECT | OPEN | Each slot maps to established craft/pedagogy principles. Four-slot formalization is internal synthesis. |
| RCG-021 | 21 | Locale/persona facts in atoms | (not yet created) | — | OPEN | OPEN | Requires per-locale citation bundles. Out of scope for this pass. |
| RCG-022 | 22 | Teacher bank pedagogical claims | (not yet created) | — | OPEN | OPEN | Requires per-slot pedagogy bibliography. Out of scope for this pass. |

### Batch 3 — LOW (RCG-019, RCG-020)

| RCG-ID | Audit item | Claim summary | Memo path | Verdict | Memo status | Inline status | Notes |
|--------|------------|---------------|-----------|---------|-------------|---------------|-------|
| RCG-019 | 19 | Subtitle pattern effectiveness | `RCG-019_subtitle_patterns.md` | NEEDS_PRIMARY_SOURCE | MEMO_CORRECT | OPEN | No public A/B data on audiobook subtitles. Treat as internal heuristic. |
| RCG-020 | 20 | Payout tier sourcing | `RCG-020_payout_tiers.md` | PARTIALLY_CONFIRMED | MEMO_CORRECT | OPEN | Platform rates (KDP/ACX) are public. Internal tiers need `internal_contract` label. |

---

## Summary counts

| Category | Count | Details |
|----------|-------|---------|
| Total citation gaps in spec | 22 | RCG-001 through RCG-022 |
| Memos correctly addressing spec topic | 20 | RCG-001 through RCG-020 (rewritten 2026-04-01) |
| Memos still OPEN | 2 | RCG-021, RCG-022 (require per-locale/per-slot research) |
| CONFIRMED | 2 | RCG-005 (bibliography), RCG-008 (RN workforce) |
| PARTIALLY_CONFIRMED | 7 | RCG-001, RCG-002, RCG-007, RCG-009, RCG-014, RCG-017, RCG-018, RCG-020 |
| UNCONFIRMED | 3 | RCG-003 (ego depletion), RCG-006 (yet/neural), RCG-010 (Dhaka), RCG-011 (Amara) |
| NEEDS_PRIMARY_SOURCE | 5 | RCG-004, RCG-012, RCG-013, RCG-015, RCG-016, RCG-019 |
| Inline citations applied | 0 | No target files updated yet — separate workstream |
| HIGH gaps with correct memos | 5 of 5 | All five HIGH claims now researched for the correct topic |
| MEDIUM gaps with correct memos | 13 of 15 | RCG-021, RCG-022 still OPEN |
| LOW gaps with correct memos | 2 of 2 | Both addressed |

---

## Verdict distribution

| Verdict | RCG IDs | Action needed |
|---------|---------|---------------|
| CONFIRMED | RCG-005, RCG-008 | Add inline citations to source files |
| PARTIALLY_CONFIRMED | RCG-001, RCG-002, RCG-007, RCG-009, RCG-014, RCG-017, RCG-018, RCG-020 | Soften claims or add hedging + citations |
| UNCONFIRMED | RCG-003, RCG-006, RCG-010, RCG-011 | Rewrite, retract, or label as illustrative/contested |
| NEEDS_PRIMARY_SOURCE | RCG-004, RCG-012, RCG-013, RCG-015, RCG-016, RCG-019 | Label as provisional/internal; document when primary data available |

---

## Change log

| Date | Agent | Change |
|------|-------|--------|
| 2026-03-31 | Pearl_Research | Initial 22 memos created (batch-generated from generic publishing industry prompt) |
| 2026-04-01 | Pearl_Research | Status tracker created; identified 20 of 22 memos as wrong-topic |
| 2026-04-01 | Pearl_GitHub | Rewrote 20 memos (RCG-001 through RCG-020) to address correct audit claims. Removed old wrong-topic files. Updated status tracker. |
