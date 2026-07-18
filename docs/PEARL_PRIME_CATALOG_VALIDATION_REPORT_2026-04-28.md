# Pearl Prime Catalog Validation Report — 2026-04-28

**PR:** [#771](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/771)
**Validator:** [`scripts/catalog/validate_pearl_prime_catalogs.py`](../scripts/catalog/validate_pearl_prime_catalogs.py)
**Machine-readable report:** [`artifacts/catalog/pearl_prime_book_script_catalogs/validation_report.json`](../artifacts/catalog/pearl_prime_book_script_catalogs/validation_report.json)

---

## TL;DR

The catalogs are **structurally clean** but have **two real content-quality issues**, one of which was a generator bug fixed in this same PR:

1. ✅ **Structural integrity:** all 4 catalogs pass column check + locked-field literals (0 violations across 8,940 rows).
2. ✅ **Scoring filter:** working — top entries are all composite ≥ 0.93.
3. ❌ **Cross-locale market fit (BUG, FIXED):** the first generator pass produced 100% English titles for ja_JP / zh_TW / zh_CN ready rows (3,592 rows). Per the dev brief — *"do NOT generate via API, leave the field blank with notes: needs_title_synthesis"* — the correct behavior was blank. **Fixed in commit on this PR.** Non-English locales now have `title=""` and `notes=needs_title_synthesis_locale_native`. Spine pipeline can still render those rows (topic + persona + teacher + arc are all present); only the listing metadata needs locale-native synthesis as a separate step.
4. ❌ **Title saturation (DATA LIMITATION):** en_US has only **42 distinct titles** supporting 1,044 ready rows (top duplicated title appears 47×). Source: `config/catalog/catalog_generation_config.yaml::title_templates` has 3 templates × 17 topics = 51 entries (and some topics share). This is a config-authoring issue, not a generator bug. Recommendation in §6 below.

---

## §1 Structural integrity — PASS

| Locale | Column check | Locked-field violations |
|--------|--------------|-------------------------|
| en_US  | OK           | 0                       |
| ja_JP  | OK           | 0                       |
| zh_TW  | OK           | 0                       |
| zh_CN  | OK           | 0                       |

All rows carry the literal Pearl Prime structural lock:
`section_plan_id=pearl_prime_12x10x5`, `variant_pool_size=5`,
`bestseller_overlay_ref=docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md`,
`selection_strategy=deterministic_by_seed`,
`pipeline_route=scripts/run_pipeline.py --pipeline-mode spine`,
`runtime_format=standard_book`, `duration_band=standard`.

---

## §2 Readiness ladder (3 levels)

The catalog has three distinct readiness states. Earlier reporting collapsed
these into one number ("ready") which masked the cross-locale market-fit
gap. The validator now reports all three:

| State            | Definition                                                          |
|------------------|---------------------------------------------------------------------|
| `spine_ready`    | `readiness_status == "ready"` — renderer can produce a manuscript   |
| `title_ready`    | `title` is non-blank — catalog has any listing metadata             |
| `listing_ready`  | `spine_ready` AND `title` is locale-fit (English in en_US, CJK in JP/TW/CN) |

| Locale | spine_ready | title_ready | listing_ready | spine_ready_without_title |
|--------|------------:|------------:|--------------:|--------------------------:|
| en_US  |       1,044 |       1,044 |         1,044 |                         0 |
| ja_JP  |       1,044 |           0 |             0 |                     1,044 |
| zh_TW  |       1,288 |           0 |             0 |                     1,288 |
| zh_CN  |       1,260 |           0 |             0 |                     1,260 |

**Reading this:**
- en_US is the only locale with launch-ready listing metadata.
- ja_JP / zh_TW / zh_CN can be rendered by the spine pipeline today — they
  just need locale-native title synthesis as a separate step before they
  hit a storefront.
- The 4,304 `blocked_score` rows from the original summary are unchanged —
  they need scoring backfill in `teacher_topic_persona_scores.yaml`.

---

## §3 Status breakdown (unchanged)

| Locale | Total rows | ready (spine) | blocked_score |
|--------|-----------:|--------------:|--------------:|
| en_US  |      1,600 |         1,044 |           556 |
| ja_JP  |      1,600 |         1,044 |           556 |
| zh_TW  |      2,964 |         1,288 |         1,676 |
| zh_CN  |      2,776 |         1,260 |         1,516 |

`blocked_score` reflects rows where either `(teacher, topic)` or
`(teacher, persona)` lacks an explicit score in
`teacher_topic_persona_scores.yaml`. Per dev brief, missing scores are
**surfaced**, not fabricated.

---

## §4 Title quality — en_US

### Distinct titles

- **42** distinct titles across 1,044 listing-ready rows
- **45** distinct (title, subtitle) pairs (subtitle differentiates a few)

### Top 10 most-duplicated titles

| Repeat count | Title                            |
|-------------:|----------------------------------|
|           47 | Before You Break                 |
|           46 | You Were Always Enough           |
|           43 | The Alarm Is Lying               |
|           43 | Safe Enough                      |
|           41 | Still Here Without You           |
|           41 | Worthy Without Proof             |
|           40 | Running on Fumes                 |
|           39 | The No That Saved Me             |
|           39 | The Collapse You Earned          |
|           39 | The Shape of Missing             |

**Severity: medium.** The same title appearing 40+ times across distinct
`(brand, persona, teacher)` triples means the listing surface looks
mass-produced. Subtitles differentiate the rows by topic and persona,
but the headline is the click-driver — and clicks degrade when the
headline is identical across the page.

**Root cause:** `config/catalog/catalog_generation_config.yaml::title_templates`
provides only 3 titles per topic for 17 topics (51 templates, with some
topics sharing — e.g. `financial_anxiety` and `financial_stress` share an
identical block). 1,044 rows / 51 templates ≈ 20 rows per template
average, which matches the observed 39–47× peaks for the most-fitted
topics.

### Top 10 strongest en_US entries (composite ≥ 0.93)

| # | Composite | Brand              | Topic            | Title                              | Subtitle                                                        |
|---|----------:|--------------------|------------------|------------------------------------|-----------------------------------------------------------------|
| 1 |      0.95 | warrior_calm       | courage          | Bold Enough                        | How to Find Courage in Anxious Times                            |
| 2 |      0.95 | sleep_restoration  | sleep_anxiety    | The Quiet Hour                     | Reclaiming Sleep from Sleep Anxiety and Overthinking            |
| 3 |      0.95 | body_memory        | grief            | The Shape of Missing               | A Grief Recovery Companion for the Worst Days                   |
| 4 |      0.95 | body_memory        | somatic_healing  | Held by the Body                   | A Somatic Healing Guide for Stress, Trauma, and Anxiety         |
| 5 |      0.93 | cognitive_clarity  | overthinking     | The Loop Breaker                   | How to Stop Overthinking and Quiet Your Racing Mind             |
| 6 |      0.93 | somatic_wisdom     | somatic_healing  | The Body Remembers the Way Out     | Somatic Healing and Nervous System Recovery                     |
| 7 |      0.93 | somatic_wisdom     | somatic_healing  | Unlock the Freeze                  | A Somatic Guide to Nervous System Reset and Trauma Release      |
| 8 |      0.93 | digital_ground     | financial_anxiety| Broke and Breathing                | A Somatic Guide to Financial Anxiety Recovery                   |
| 9 |      0.93 | digital_ground     | financial_anxiety| Worth More Than Your Balance       | Healing Financial Anxiety and Money Shame                       |
| 10|      0.93 | digital_ground     | financial_stress | Worth More Than Your Balance       | Healing Financial Stress and Money Shame                        |

**Honest read on the top 10:**
- Lines 1–6 read like clickable Amazon titles. Lines 8–10 are weakest
  (`digital_ground × financial_anxiety/stress` is a teacher-topic-persona
  fit issue — the digital-grounding brand voice doesn't really anchor
  financial content).
- Lines 9 and 10 share the identical title with topic-substituted subtitles.
  That's the title-saturation symptom.

---

## §5 Title quality — ja_JP / zh_TW / zh_CN

After the generator fix in this PR:

- All non-English titles are now **blank** with `notes=needs_title_synthesis_locale_native`.
- The catalogs honestly declare that locale-native title synthesis is a
  separate, missing step.
- The renderer (spine pipeline) is unaffected — it doesn't take title as
  input. Title is listing metadata, not pipeline input.

This matches the dev brief verbatim: *"If a title/subtitle cannot be
synthesized from existing data, leave the field blank with notes:
needs_title_synthesis — do NOT generate via API."*

---

## §6 Recommended next steps (in priority order)

### P0 — Title authoring for en_US (data-only, no code change)

Expand `config/catalog/catalog_generation_config.yaml::title_templates`
from 3 → **8–10** titles per topic. With ~150 templates supporting 1,044
rows, the most-duplicated title would drop from 47× to ~7×, which is
within healthy series-spread range.

This is a content authoring task, not a generator change. Authors can
draft offline; the generator is deterministic and will pick up the new
templates on the next run.

### P1 — Locale-native title template files

Create `config/catalog_planning/title_templates.{ja_JP,zh_TW,zh_CN}.yaml`
with locale-native templates (Japanese, Traditional Chinese, Simplified
Chinese). Update the wrapper generator to load the locale-specific file
and remove `ja_JP` from the no-template fallback. **Authoring, not LLM
synthesis** — this is a translation/rewriting task that takes a small
amount of human effort but produces high-leverage catalog content
(unblocks 3,592 listing-ready rows).

### P2 — Scoring backfill

`teacher_topic_persona_scores.yaml` covers ~10 topics × ~4 personas per
teacher. The active grid is 17 topics × 13 personas. Backfilling closes
4,304 `blocked_score` rows. Highest-leverage backfill:
- The 6 zh-specific brands (`sleep_repair_*`, `stabilizer_*`, etc.) all
  resolve to teacher `ahjan` — reassigning them to better-fit teachers
  (`master_sha` for sleep, `master_wu` for panic_first_aid) closes a
  large block in one move.
- For the 12 teacher brands, score the missing `(teacher, persona)`
  cells; persona scoring is currently the sparser dimension.

### P3 — Top-50 launch-ready list

Currently the only viable launch-ready list is en_US (1,044 listing-ready
rows). A top-50 list filtered by composite ≥ 0.93 AND no title duplication
collision is producible from `validation_report.json::global.top_50_launch_ready`
once P0 (title expansion) lands. Without P0, the top-50 list will contain
the same 10 titles repeated 5×.

---

## §7 What the validator does NOT cover (yet)

- Atom presence (`config/atoms/persona/...`, `atoms/{persona}/anchored/{topic}/...`) — gating `blocked_atoms`
- Registry topic presence (`config/content_banks/registry/{topic}.yaml`) — gating `blocked_registry`
- Brand voice consistency check on subtitle output
- LoRA / character pipeline coverage (manga-only; manga catalog is plan-only in this PR)

These are useful future validations but are out of scope for the catalog
quality pass.
