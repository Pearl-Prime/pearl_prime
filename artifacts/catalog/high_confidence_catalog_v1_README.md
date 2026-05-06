# High-Confidence Catalog v1

**File:** `artifacts/catalog/high_confidence_catalog_v1.tsv`
**Date:** 2026-05-06
**Closes:** `ws_catalog_800_high_confidence_artifact_20260506`
**Cap entry:** `CATALOG-800-PER-BRAND-01` (decision: ~800 system-wide
high-confidence configs, NOT per-brand)

## What this is

800 ranked book configurations across the dimension space:
brand × topic × persona × format × locale. Scored by an explicit
heuristic (see "Scoring" below) so the ranking is reproducible and
defensible. This is the production-priority order for catalog
generation — the top 800 picks Pearl_Prime should target before
moving into the long tail.

## Schema

| Column | Description |
|---|---|
| `rank` | 1-800 by descending confidence |
| `config_id` | `brand.topic.persona.format.locale` |
| `brand` | from `config/brand_registry.yaml` (26 total) |
| `topic` | from `registry/<topic>.yaml` (15 total) |
| `persona` | from `atoms/<persona>/` tree (14 total) |
| `format` | from `config/format_selection/format_registry.yaml` (8 priority formats; full set = 20) |
| `locale` | en-US (primary) + en-GB (secondary; CJK locales are governed separately by Pearl_Localization) |
| `confidence_score` | 1.0 base + tier bonuses; max ~8.0 |
| `tier` | T1-flagship (≥7), T2-priority (≥5.5), T3-standard (≥4), T4-tail |
| `rationale` | semicolon-separated tags (which heuristics fired) |

## Scoring (v1 heuristic)

Base 1.0 + persona-tier (2 / 1 / 0) + topic-tier (2 / 1 / 0) +
brand-topic-affinity (1.5) + canonical-format (1.0 for
standard_book; 0.7 for deep/extended) + locale-primary (0.5 for
en-US).

**Tier 1 personas** (highest market signal — named in BG-PR-09
verification): `gen_z_professionals`, `millennial_women_professionals`,
`midlife_women`, `tech_finance_burnout`.

**Tier 1 topics**: `anxiety`, `burnout`, `grief`, `self_worth`,
`sleep_anxiety`.

**Brand-topic affinities** captured from `config/brand_registry.yaml`
positioning + `docs/GENRE_PORTFOLIO_PLAN.md` (the
`stillness_press → anxiety/sleep` affinity is the load-bearing one).

## Refinement path (Pearl_Research + Pearl_Marketing follow-up)

The heuristic is a baseline that operator/Pearl_Research can refine
with real marketing signal:
- Replace tier-bonuses with conversion-rate data when available
- Add brand-topic affinity rows from sales data
- Fold seasonal modifiers (e.g., year-end stress topics)
- Extend locale set to CJK once the Qwen 2.5 translation ws lands

The TSV format is stable; refinement = re-running the scorer with
better inputs.

## Out of scope (intentional)

- CJK locales (governed separately by Pearl_Localization)
- Manga catalog (governed by `proj_manga_catalog_reconciliation_20260426`)
- Brand × persona × topic combinations beyond the priority 8 formats
  (the long tail is on the catalog generator's TODO list, not this
  artifact)
