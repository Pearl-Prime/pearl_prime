# Validation Prompts

Validation prompts are extracted from the "Follow-up if shallow" blocks in
`docs/research/PEARL_NEWS_QWEN_DEEP_RESEARCH_ENGINE.md`.

Each validation prompt re-checks a layer output for depth, citation quality,
and YAML schema compliance before promoting the artifact.

## Naming convention

```
dim<N>_prompt_<N>_<M>_validation.txt
```

Example: `dim1_prompt_1_1_validation.txt` validates the output of
`tasks/dim1_prompt_1_1_task.txt` (Dimension 1, Prompt 1.1 Trauma map).

## Status

Per `RESEARCH_CITATION_GAP_DEV_SPEC.md` section 4.3, approximately 29 prompt
slots (PC-001 through PC-029) remain to be extracted from the spec into
standalone files. This directory is the target for validation-type prompts.

Extraction is tracked in `artifacts/research/citations/CITATION_GAP_STATUS.md`.
