# Pearl Prime Book Script Catalogs — 2026-04-28

**Status:** initial drop, plan-only manga companion
**Authority:** [`docs/PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md`](PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md) §2 + §6
**Generator:** [`scripts/catalog/generate_pearl_prime_book_script_catalog.py`](../scripts/catalog/generate_pearl_prime_book_script_catalog.py)
**Outputs:** [`artifacts/catalog/pearl_prime_book_script_catalogs/`](../artifacts/catalog/pearl_prime_book_script_catalogs/)

---

## TL;DR

Four locale catalogs were generated for the Pearl Prime book script pipeline:
en_US, ja_JP, zh_TW, zh_CN. Total **8,940 rows** across all four locales,
of which **4,636 are `ready`** and **4,304 are `blocked_score`** (rows where
either `(teacher, topic)` or `(teacher, persona)` lacks an explicit score and
falls back to the default 0.5 — surfaced rather than fabricated, per dev brief).

These are **catalog/queue artifacts only.** No manuscripts, chapters,
sections, or variants were generated. No LLM was called. Pearl Prime
structural format is locked to **12 chapters × 10 sections × 5 variants
per section**; the bestseller overlay is applied at render time, not at
catalog time.

---

## Per-locale breakdown

| Locale | Tier      | Brands | Rows  | Ready | Blocked | Top blocker tag       |
|--------|-----------|-------:|------:|------:|--------:|-----------------------|
| en_US  | primary   |     12 | 1,600 | 1,044 |     556 | `blocked_score` (556) |
| ja_JP  | primary   |     12 | 1,600 | 1,044 |     556 | `blocked_score` (556) |
| zh_TW  | secondary |     19 | 2,964 | 1,288 |   1,676 | `blocked_score` (1,676) |
| zh_CN  | secondary |     18 | 2,776 | 1,260 |   1,516 | `blocked_score` (1,516) |
| **Total** |        |        | **8,940** | **4,636** | **4,304** |                |

`zh_TW` carries one extra brand (`bright_presence_tw`, the Adi Da Taiwan-only
teacher-mode brand) over `zh_CN`. Both Chinese locales include the 6 zh-specific
standard brands (`sleep_repair_*`, `stabilizer_*`, `panic_first_aid_*`,
`gen_z_grounding_*`, `grief_companion_*`, `inner_security_*`), which are
emitted with `teacher_mode=false` per owner decision Q2.

The higher block count in zh_TW / zh_CN is structural, not a bug: the 6
zh-specific brands all currently resolve to teacher `ahjan`, and ahjan has
explicit scores for ~10 topics × ~4 personas — outside that grid the
composite falls to default 0.5 and the row is correctly tagged
`blocked_score` / `needs_score` rather than fabricated.

### Top blockers (all locales)

1. `blocked_score` — `(teacher, topic, persona)` triple has no explicit
   score on at least one dimension. Resolution: extend
   `config/catalog_planning/teacher_topic_persona_scores.yaml` with explicit
   topic/persona scores for the missing combinations.

There are no `blocked_atoms`, `blocked_registry`, or `blocked_teacher`
rows in this drop. Atom-presence validation is a planned next iteration —
see "Coverage gaps" below.

---

## Pearl Prime structure recap

Per [`docs/PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md`](PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md) §2:

- **12 chapters** per book
- **10 sections** per chapter
- **5 variants** per section (1 selected deterministically by seed at render time)

Every catalog row stores the structural lock as literal values:

```
section_plan_id        = pearl_prime_12x10x5
variant_pool_size      = 5
bestseller_overlay_ref = docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md
selection_strategy     = deterministic_by_seed
pipeline_route         = scripts/run_pipeline.py --pipeline-mode spine
```

The bestseller overlay
([`docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md`](PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md))
is a **render-time injection layer**, not a catalog-time field. The catalog
records only the spec reference; injection rules execute when
`scripts/run_pipeline.py --pipeline-mode spine` runs against the row.

---

## Pipeline route — how to render a row

A catalog row is the input contract; rendering is a separate phase.

For canonical CLI, see [`docs/PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md`](PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md) §8.
Rough shape (do **not** treat this as the contract — the canonical doc wins):

```bash
PYTHONPATH=. python3 scripts/run_pipeline.py \
  --topic <row.topic> \
  --persona <row.persona> \
  --pipeline-mode spine \
  --runtime-format <row.runtime_format> \
  --render-book --render-dir <derived from row.output_target_path> \
  --seed <derived from row hash>
```

This catalog drop does **not** invoke the renderer. Rendering is out of scope
and is a separate task.

---

## Coverage gaps preventing more `ready` rows

1. **Scoring coverage gap** — 4,304 rows are `blocked_score` because
   `teacher_topic_persona_scores.yaml` has explicit scores for ~10 topics
   and ~4 personas per teacher, while the active grid is 17 topics × 13
   personas. Backfilling the scoring matrix would lift the
   `ready` count proportionally.
2. **zh-specific brand teacher diversity** — all 6 zh-specific brands
   currently resolve to teacher `ahjan` per
   `brand_teacher_matrix_zh.yaml`. Reassigning them to teachers whose
   doctrinal fit better matches the brand vertical (e.g. `sleep_repair_*`
   → `master_sha`, `panic_first_aid_*` → `master_wu`) would simultaneously
   improve composite scores and reduce blocked-score rows on the Chinese
   locales.
3. **Atom-presence validation not yet wired** — readiness today reflects
   scoring only. A future pass should resolve `required_source_atoms`
   against `config/atoms/persona/...` and `atoms/{persona}/anchored/{topic}/`
   to gate `blocked_atoms`, and against `config/content_banks/registry/`
   to gate `blocked_registry`.

---

## Reproduction command

```bash
python3 scripts/catalog/generate_pearl_prime_book_script_catalog.py \
  --locales en_US,ja_JP,zh_TW,zh_CN \
  --output-dir artifacts/catalog/pearl_prime_book_script_catalogs/
```

The generator is deterministic given identical input file contents.
`catalog_summary.json` includes SHA-256 fingerprints of every config file
read.

---

## Schema reference

Full row schema (23 columns, fixed order) is documented in
[`artifacts/catalog/pearl_prime_book_script_catalogs/README.md`](../artifacts/catalog/pearl_prime_book_script_catalogs/README.md).

---

## Files written in this drop

| Path                                                                            | Lines | Purpose                                         |
|---------------------------------------------------------------------------------|------:|-------------------------------------------------|
| `config/manga/canonical_genre_list.yaml`                                        |   308 | Precondition A — taxonomy ⇆ pacing reconciliation |
| `scripts/catalog/generate_pearl_prime_book_script_catalog.py`                   | (see git) | Wrapper generator                          |
| `artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv`          | 1,601 | en_US catalog (header + 1,600 rows)             |
| `artifacts/catalog/pearl_prime_book_script_catalogs/ja_JP_catalog.csv`          | 1,601 | ja_JP catalog                                   |
| `artifacts/catalog/pearl_prime_book_script_catalogs/zh_TW_catalog.csv`          | 2,965 | zh_TW catalog (19 brands incl. `bright_presence_tw`) |
| `artifacts/catalog/pearl_prime_book_script_catalogs/zh_CN_catalog.csv`          | 2,777 | zh_CN catalog                                   |
| `artifacts/catalog/pearl_prime_book_script_catalogs/catalog_summary.json`       |    ~80 | Aggregated summary + source SHAs                |
| `artifacts/catalog/pearl_prime_book_script_catalogs/README.md`                  | (see git) | Schema reference                            |
| `docs/PEARL_PRIME_BOOK_SCRIPT_CATALOGS_2026-04-28.md`                           | this  | This summary doc                                |
| `docs/MANGA_CATALOG_PLAN_EN_US_JA_JP_ZH_TW_ZH_CN_2026-04-28.md`                 | (plan-only) | Manga catalog plan — no manga artifacts created |

Registry edit (small): `config/catalog/market_catalog_registry.yaml` —
added `bright_presence_tw` to `taiwan.brands` and bumped `taiwan.brand_count`
from 18 → 19.
