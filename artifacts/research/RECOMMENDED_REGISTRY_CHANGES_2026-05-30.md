# Recommended Registry Changes — 2026-05-30

**Status:** PROPOSAL ONLY — operator review required. **No config edits applied in this PR.**

**Authority:** Synthesis of Pearl_Research + Pearl_Marketing audit (`DURATION_FORMAT_UNIVERSE_AUDIT_2026-05-30.md`).

---

## P0 — Close Wave 1 duration gaps

### 1. Add `podcast_micro_10min` to `config/podcast/podcast_format.yaml`

**Why:** Research-strong Spotify daily micro-dose band (10 min daily beats 70 min weekly [D:18][D:38]). Current gap: `podcast_short` (2–5 min) ↔ `podcast_episode` (15–25 min).

**Proposed entry:**

```yaml
podcast_micro_10min:
  id: podcast_micro_10min
  description: >
    Spotify daily micro-dose episode. 8-12 minutes. One teaching + one practice.
    Fills the gap between podcast_short (2-5 min) and podcast_episode (15-25 min).
  duration_range_s: [480, 720]        # 8-12 min (center on 10)
  platforms:
    - spotify
    - apple_podcasts
  therapeutic_mechanisms:
    - micro_dose_therapeutic
    - habit_formation_daily
  notes: >
    Implements CONTENT_DURATION_MARKETING_PLAN S2 micro-dose tier and
    duration_intelligence_briefing.html Spotify "daily 10-min micro-podcast" strategy.
```

**Operator gate:** OQ-DFU-04

---

### 2. Extend `therapeutic_short` duration cap in `config/video/format_specs.yaml`

**Why:** TikTok Creator Rewards band is 60–90s ([D:33]); current cap is 60s max.

**Proposed change:**

```yaml
# short format block:
duration_max_s: 90   # was 60; research: 60-90s TikTok wellness optimal
```

**Alternative:** Add sibling key `short_90` if backward-compat required for renders already validated at 60s cap.

**Operator gate:** OQ-DFU-05

---

## P1 — Book registry completeness

### 3. Extend atom-native modular formats in `config/format_selection/format_registry.yaml`

**Why:** Group A backfill (AUTO-PLAN-SSOT-01-AMENDMENT) added `chapter_count_default` only. Marketing and format_selector need duration/word bands.

**Proposed fields per format** (from `docs/ATOM_NATIVE_MODULAR_FORMATS.md`):

| format_id | duration_minutes | word_range | marketing_role annotation |
|-----------|------------------|------------|---------------------------|
| `five_min_practice` | 5 | [350, 650] | sample/preview |
| `pocket_guide` | — | [1800, 8400] | catalog_product (10–20 entries) |
| `ten_things_to_do` | — | [1200, 2600] | catalog_product |
| `symptom_to_action_atlas` | 1 | [1800, 13200] | catalog_product (20–60 cards) |
| `daily_text_audio_companion` | 1 | [1400, 3200] | catalog_product |
| `crisis_cards` | — | [540, 1200] | freebie_leadgen |
| `weekly_challenge_pack` | — | [1260, 3360] | catalog_product |
| `faq_audiobook` | 3 | [2560, 5600] | catalog_product |
| `myth_vs_mechanism` | 4 | [2560, 5600] | sample/preview |
| `protocol_library` | — | [1200, 2800] | catalog_product |

Add `marketing_role:` YAML comment or parallel `config/marketing/format_role_matrix.yaml` if registry should stay engineering-pure.

---

### 4. Deprecate micro runtimes for GTM (selector redirect)

**Why:** `micro_book_15` / `micro_book_20` use 12-ch spine → known EI FAIL (`COMPACT_BOOK_FORMAT_SPECS` §2). Compact equivalents are wired.

**Proposed changes:**

1. `phoenix_v4/planning/format_selector.py` — when persona/topic requests micro_book_15/20, redirect to compact_book_5ch_15min/20min (log deprecation warning).
2. `format_registry.yaml` — add comment block:

```yaml
# DEPRECATED GTM — use compact_book_* equivalents. Retained for backward compat.
micro_book_15:
  deprecated: true
  redirect_to: compact_book_5ch_15min
```

**Do NOT delete IDs** — existing book plans may reference them.

**Operator gate:** OQ-DFU-02

---

### 5. Mark `standard_book` chapter count provenance

**Why:** Operator confusion on 10 vs 12. Registry already has comment; add explicit `spine_source_chapters: 12` field:

```yaml
standard_book:
  chapter_count_default: 10
  spine_source_chapters: 12   # topic registry authoring shape; subset via auto-plan
  # Ratified: AUTO-PLAN-SSOT-01-AMENDMENT Group B + TEMPLATE-UNIVERSAL-01
```

**Operator gate:** OQ-DFU-01

---

## P2 — Sibling registry alignment

### 6. Add research-tier cross-reference doc (no registry edit)

Create `docs/DURATION_FORMAT_CROSSWALK.md` mapping:

- Marketing tier names → registry format_ids
- Research-only tiers → proposed future IDs
- Channel ownership (book vs podcast vs video)

**Rationale:** Prevents future Wave N rediscovery of same gaps.

---

### 7. Stale doc fix — `docs/COMPACT_BOOK_FORMAT_SPECS_2026-05-04.md` §1

Update status from `not yet wired` → `wired (PR-D-SPINE-01 + format_registry.yaml lines 176–205)`.

Separate docs-only PR; not bundled with registry proposals.

---

### 8. Vestigial cleanup — `book_structure_plan.py` RUNTIME_TEMPLATES

Remove or document vestigial `chapter_count` in `RUNTIME_TEMPLATES` (third value source flagged in AUTO-PLAN-SSOT-01-AMENDMENT). Low priority Pearl_Dev follow-up.

---

## P3 — Research gaps (no registry action until research complete)

| Gap | Action |
|-----|--------|
| Catalog `duration_strategy` % bands | Pearl_Research follow-on: primary-source completion curves before operationalizing `05_duration_bands_patch.yaml` |
| Ebook tiers (KDP page counts) | No book registry ID needed until ebook pipeline exists; track in crosswalk doc |
| Manga panel tiers | Owned by `config/manga/format_routing.yaml`; align marketing S3 tiers in separate manga ws |
| `podcast_deep_dive_45-60min` | Add to podcast_format.yaml when authority-funnel content authored |
| Korea Millie 30-min / Ximalaya episodic | Locale-specific; wire under `AUDIOBOOK_LOCALE_CATALOG_MARKETING_PLAN` execution ws |

---

## Formats recommended for DROP (GTM only — retain engineering IDs)

| format_id | Drop from | Keep in registry | Reason |
|-----------|-----------|------------------|--------|
| `micro_book_15` | GTM/catalog matrices | Yes (deprecated) | Superseded by compact_book_5ch_15min |
| `micro_book_20` | GTM/catalog matrices | Yes (deprecated) | Superseded by compact_book_5ch_20min |
| `manga_presentation` | Consumer funnel | Yes | Investor deck only |

---

## Formats recommended for MERGE (conceptual SSOT, not ID merge)

| Overlap set | Recommendation |
|-------------|----------------|
| `five_min_practice` + `podcast_short` + `exercise_video` (5-min band) | Single content SSOT (`five_min_practice` atom format) with channel render wrappers — do NOT merge registry IDs |
| `audiobook_clip` + `therapeutic_short` (30–60s) | Cross-reference in marketing matrix; distinct render pipelines |

---

## Implementation order (post-operator ratification)

1. OQ-DFU-01 through OQ-DFU-05 operator answers
2. P0 podcast + video cap (Pearl_Dev, small PRs)
3. P1 atom-native field backfill + micro deprecation redirect (Pearl_Dev)
4. P2 doc crosswalk + compact spec status update (Pearl_Architect / Pearl_GitHub)
5. P3 research follow-on (Pearl_Research)

---

## Files this proposal does NOT modify

- `config/format_selection/format_registry.yaml` (this audit PR)
- `config/podcast/podcast_format.yaml`
- `config/video/format_specs.yaml`
- `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`
