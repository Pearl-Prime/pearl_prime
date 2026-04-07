# EI v2 Registry Learning Spec

**Authority:** This spec governs how the pipeline learns from registry failures and prevents the catalog planner from requesting topics that lack content.

## Problem

The catalog planner generates 8,287 titles across 17 topics and 13 markets. But section registries (the sole content source) currently exist for 1 topic (grief). When the pipeline attempts to produce a book for a topic without a registry, it must:

1. **Hard fail** — no silent fallback, no degraded output
2. **Log the failure** to `artifacts/ei_v2/registry_failures.jsonl`
3. **Block the topic** in future planning cycles until a registry is created

## Failure Event Schema

```jsonl
{
  "event": "REGISTRY_MISSING",
  "topic_id": "anxiety",
  "persona_id": "gen_z_professionals",
  "teacher_id": "adi_da",
  "arc_path": "config/source_of_truth/master_arcs/...",
  "timestamp": "2026-04-08T12:00:00",
  "message": "No section registry for topic 'anxiety'...",
  "available_registries": ["grief"],
  "action": "BLOCK_TOPIC_UNTIL_REGISTRY_EXISTS"
}
```

## Learning Loop

### 1. Pipeline fails → logs event

`scripts/run_pipeline.py` writes to `artifacts/ei_v2/registry_failures.jsonl` on every missing-registry failure. This file is append-only — never truncated.

### 2. Catalog planner reads failure log before generation

`scripts/catalog/generate_full_catalog.py` should check `registry_failures.jsonl` and:
- Exclude topics with `BLOCK_TOPIC_UNTIL_REGISTRY_EXISTS` from WAVE_1 (golden set)
- Demote blocked topics to WAVE_2 with `market_viability: BLOCKED_NO_REGISTRY`
- Log which topics were blocked and why

### 3. Weekly production queue respects blocks

`scripts/catalog/weekly_production_queue.py` should skip any catalog entry where the topic has a registry failure logged and no registry file exists.

### 4. Registry creation unblocks topic

When `registry/registry_{topic}.yaml` is created, the topic is automatically unblocked because the pipeline checks for file existence at runtime.

## Available Registries Check

```python
from phoenix_v4.planning.registry_resolver import available_registries
# Returns: ["grief"] (currently)
# After building more: ["grief", "anxiety", "burnout", "self_worth", ...]
```

## Registry Template

See `registry/registry_grief.yaml` — 12 chapters × 7-10 sections × 2-5 variants.

Target per registry:
- 12 chapters with authored titles
- 10 sections per chapter (HOOK, SCENE, REFLECTION, TEACHER_DOCTRINE, EXERCISE, INTEGRATION)
- 5 variants per section (variant families F1-F5)
- Total: ~600 content blocks per topic registry

## Priority Order for New Registries

Based on catalog golden set volume and market demand:

1. **anxiety** — 819 catalog entries, highest search volume
2. **burnout** — 814 entries, universal across all markets
3. **self_worth** — 891 entries, highest total volume
4. **imposter_syndrome** — 814 entries
5. **boundaries** — 728 entries
6. **depression** — 446 entries
7. **grief** — ✅ DONE
8. **courage** — 709 entries
9. **overthinking** — 541 entries
10. **somatic_healing** — 532 entries

## Verification

```bash
# Check what registries exist
ls registry/registry_*.yaml

# Check failure log
cat artifacts/ei_v2/registry_failures.jsonl

# Test a topic with registry
python3 scripts/run_pipeline.py --topic grief --persona gen_z_professionals \
  --arc config/source_of_truth/master_arcs/gen_z_professionals__grief__grief__F006.yaml \
  --teacher adi_da --render-book --render-dir /tmp/test

# Test a topic WITHOUT registry (should hard fail)
python3 scripts/run_pipeline.py --topic anxiety --persona gen_z_professionals \
  --arc config/source_of_truth/master_arcs/gen_z_professionals__anxiety__grief__F006.yaml \
  --teacher adi_da --render-book --render-dir /tmp/test
# Expected: HARD FAIL + event logged to artifacts/ei_v2/registry_failures.jsonl
```
