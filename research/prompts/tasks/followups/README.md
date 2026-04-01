# Follow-up Prompts

Follow-up prompts handle the "Follow-up if shallow" and "Part 3-4 operational"
chains described in `docs/research/PEARL_NEWS_QWEN_DEEP_RESEARCH_ENGINE.md`.

These prompts are dispatched when a layer's initial pass produces output below
the depth or citation threshold.

## Naming convention

```
dim<N>_prompt_<N>_<M>_followup_shallow.txt
```

Example: `dim1_prompt_1_1_followup_shallow.txt` is the follow-up for
`tasks/dim1_prompt_1_1_task.txt` when Pass 1 output is judged shallow.

## Status

Per `RESEARCH_CITATION_GAP_DEV_SPEC.md` section 4.3, approximately 29 prompt
slots (PC-001 through PC-029) remain to be extracted from the spec. This
directory is the target for follow-up/retry-type prompts.

Extraction is tracked in `artifacts/research/citations/CITATION_GAP_STATUS.md`.
