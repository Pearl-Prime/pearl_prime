# Frame v2 specimen — somatic-first therapeutic (burnout)

**Shape:** `tech_finance_burnout` × `burnout` × engine `overwhelm`, arc `tech_finance_burnout__burnout__overwhelm__F006.yaml`.

**Regenerate (spine mode — includes `frame_*` in `quality_summary.json`; registry fast-path does not):**

```bash
cd /path/to/phoenix_omega
PYTHONPATH=. python3 scripts/run_pipeline.py --pipeline-mode spine \
  --topic burnout --persona tech_finance_burnout \
  --arc config/source_of_truth/master_arcs/tech_finance_burnout__burnout__overwhelm__F006.yaml \
  --render-book --render-dir artifacts/pilots/frame_v2_specimen_somatic_burnout \
  --quality-profile draft --no-update-freebie-index --no-job-check \
  --out artifacts/pilots/frame_v2_specimen_somatic_burnout/plan.json
```

**Skim (agent):** `frame_governance_chapters`, `frame_softened_sentences`, `frame_stripped_sentences`, `frame_hard_fail_reasons` are present and empty for this run — prose did not trigger v2 strip/soften/hard_fail. Owner should still spot-check Chapter 1 body for any absolutes the lexicon should catch.
