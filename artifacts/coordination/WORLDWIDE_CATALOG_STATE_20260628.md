# Worldwide Catalog Program — State Table (2026-06-28)

**Orientation (Prompt 0)** — read-only ground truth after `git fetch origin --prune`.

## Lane status

| Lane | Done | In-flight | Blocked on |
|------|------|-----------|------------|
| **en_US plans (40×800)** | ✅ 40/40 brands, 32,401 YAMLs on `origin/main` | — | — |
| **Authoring flip (Prompt 1)** | Tool: `scripts/catalog/flip_authoring_skeletons.py` | First batch (≤180) on branch | 21k flip = many ≤180 PRs |
| **Arc seeding (Prompt 2)** | — | **SKIPPED** per operator | 9,164 arc-blocked plans |
| **Assembly EPUBs (Prompt 3)** | Bugs identified | Fix PR on `agent/catalog-assemble-campaign` | `R2_BUCKET` secret empty; validate_epub list fix |
| **CJK atoms → origin (Prompt 4)** | Audit script exists | Not started this session | Pearl Star atoms stranded; 26.5% origin coverage |
| **Localization (Prompt 5)** | de_DE orphans deleted (#2235) | Fanout run **28293349152 QUEUED 19h+** | Runner capacity; many open de_DE PRs |
| **Manga slice (Prompt 6)** | Spec exists | Not started | TW/FR manga line missing in registry |
| **Pearl News** | Sidebar parity gate | Daily workflow disabled | LLM secrets (separate track) |

## Authoring frontier (`authoring_frontier_en_US.json`)

| Metric | Count |
|--------|------:|
| Skeletons | 30,448 |
| Flip-ready (arc+atoms) | 21,284 |
| Arc-blocked (Prompt 2) | 9,164 |
| Buildable now | 2,176 |
| After deterministic flip | ~23,460 |

## Resolved incidents (do not redo)

- **#2227, #2230** — CLOSED, superseded by **#2235** (720 de_DE orphans deleted, OPD-20260627-003)
- **Platform spam model** — RATIFIED OPD-20260627-001: translate editions, don't regenerate per market

## Assembly pilot failure (28295414593)

1. `R2_BUCKET` GitHub secret **empty** (script defaults to `phoenix-omega-artifacts`)
2. `batch_catalog_epubs.py` `_validate_epub`: `validate_epub.py --json` returns **list**, not dict → TypeError

## Operator actions

1. Set **`R2_BUCKET`** repo secret (e.g. `phoenix-omega-artifacts`)
2. Unstick **catalog-fanout-campaign** run 28293349152 (queued 19h+)
3. Add **Taiwan/France manga** lines to `market_catalog_registry.yaml` when ready
4. Re-enable **pearl-news-daily** after pearl-star dry-run (separate handoff)

## Recommended run order (remaining)

```
1 (flip batches) → 3 (assembly pilot limit=5) → 4 (CJK catch-up) → 5 (hu_HU + CJK6) → 6 (manga + P0 quality)
```

Skip Prompt 2 until operator requests arc seeding wave.
