# `cluster_titles.py` — Pearl Prime catalog title cannibalization gate

Issue [#786](https://github.com/Ahjan108/phoenix_omega_v4.8/issues/786) (B2)
defined acceptance criteria for catalog title differentiation. PR #788 fixed
the underlying B2 problem on en_US. This script is the **acceptance gate**:
deterministic, no LLM, CI-runnable. Use it to:

- Verify a catalog passes B2 acceptance after generator changes.
- Catch regressions when title templates or generation logic change.
- Surface true cannibalization (low distinct-title density within a cluster)
  vs. healthy catalog depth (many distinct titles within a topic theme).

## What it checks

Four acceptance criteria from Issue #786, each gated independently:

| Check | Threshold | Source |
|---|---|---|
| Avg ready rows per distinct title | `≤ 3.0` | Issue #786 §3 |
| Exact `(title, subtitle)` pairs > 3 | `0` | Issue #786 §2 |
| Semantic clusters > 6 with low density | `0` (density floor 0.30) | Issue #786 §1 + §3 |
| Ready-but-blank en_US title rows | `0` | Issue #786 §7 |

Exits **0** if all four pass; **1** otherwise. Suitable for CI gating.

## Why a density floor

A naive read of "no semantic cluster > 6 rows" fails on a 1,478-row catalog —
every topic-themed group naturally exceeds 6. The density metric distinguishes
the two failure modes:

- **Real cannibalization (the original B2 problem):** 47 rows of the same
  title "Before You Break". Cluster size 47, distinct titles 1, density 0.02.
- **Catalog depth (the healthy state after B2):** 75 rows in the
  `mindfulness/presence` cluster, 30 distinct brand-voiced titles, density 0.40.

Density floor is **0.30**, the structural lower bound of a 4-template-per-cell
× ~3-persona-per-template architecture (1 distinct title per ~3.3 rows). Below
the floor = real cannibalization; at/above = brand voice carrying the differentiation.

The floor is editable inline (`SEMANTIC_CLUSTER_DENSITY_FLOOR`) — adjust
upward if a future generator design supports tighter density.

## Usage

### One-shot (CI / verification)

```bash
python3 scripts/catalog/cluster_titles.py \
  --input artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv \
  --report artifacts/catalog/pearl_prime_book_script_catalogs/cluster_report.md \
  --json artifacts/catalog/pearl_prime_book_script_catalogs/cluster_data.json \
  --locale en_US
echo "exit=$?"  # 0 = pass, 1 = fail
```

### Quick CLI summary

```bash
python3 scripts/catalog/cluster_titles.py \
  --input artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv \
  --locale en_US
# Prints JSON summary to stdout, exits 0/1 based on acceptance.
```

### Other locales (B1 follow-up)

When B1 (locale-native title templates for ja_JP / zh_TW / zh_CN) lands,
re-run for each:

```bash
for loc in ja_JP zh_TW zh_CN; do
  python3 scripts/catalog/cluster_titles.py \
    --input artifacts/catalog/pearl_prime_book_script_catalogs/${loc}_catalog.csv \
    --locale $loc
done
```

## Cluster keyword editing

The semantic-cluster taxonomy is in the `CLUSTER_KEYWORDS` dict at the top of
the script. Each cluster maps to a list of keywords (single-word matched on
word boundaries; multi-word matched as substrings). When new topics or title
patterns emerge, add a cluster entry — do NOT use LLM-derived clustering.

The matcher uses word boundaries on single-word keywords to prevent false
positives like `numb` matching `Numbers`.

## Output artifacts

Both reports are emitted on every run (when `--report` and `--json` are passed):

- `cluster_report.md` — human-readable markdown with cluster table + status
- `cluster_data.json` — machine-readable, includes per-cluster metrics, top
  exact-pair violations, blank-by-topic counts, worst (brand × topic) cells

Current state (post-PR #788 on main):

| Metric | Value |
|---|---:|
| ready_total | 1,478 |
| ready_with_title | 1,478 |
| ready_blank_title | 0 |
| distinct_titles | 1,149 |
| distinct_pairs | 1,478 |
| avg_rows_per_distinct_title | 1.29 |
| exact_pair_violations | 0 |
| semantic_violations | 0 |
| **acceptance_passed** | **true** |

## What this script does NOT do

- Modify catalog rows
- Modify title generation logic
- Call any LLM
- Mutate any config under `config/catalog_planning/` or `config/catalog/`

It is a read-only gate. The catalog is owned by
[`scripts/catalog/generate_pearl_prime_book_script_catalog.py`](generate_pearl_prime_book_script_catalog.py)
+ the templates / dedup phrase tables under `config/catalog_planning/`.

## Provenance

The analyzer was authored as part of an alternative B2 implementation that was
superseded by PR #788's flagship-cap approach (which produced 1,149 distinct
titles vs. the alternative's 604). PR #788's solution shipped; the analyzer
itself is approach-agnostic and was extracted in a follow-up so future B-series
work has a regression-protection gate.
