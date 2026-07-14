# Before / After Evaluation

Case: `global_social_media_pipeline`
Recommended route: `Gemini Deep Research`
Recommended prompt key: `gemini`

## Quality Score

| Criterion | Legacy | New |
|---|---:|---:|
| exact_research_objective | no | yes |
| system_business_context | no | yes |
| failure_symptoms | yes | yes |
| hypotheses_to_test | no | yes |
| specific_questions | no | yes |
| required_comparisons | yes | yes |
| decision_output | yes | yes |
| evidence_standards | no | yes |
| source_quality_rules | yes | yes |
| no_generic_advice | no | yes |
| contradictions_uncertainty | no | yes |
| phoenix_implications | yes | yes |
| provenance_sources | yes | yes |
| **Total** | **6/13** | **13/13** |

## Why The New Prompt Is Stronger

- It adds a structured research brief before execution, preserving the operator's messy context without asking the downstream engine to infer the real decision from noise.
- It routes explicitly using `config/research/deep_research_prompt_routing.yaml`, so China, Japan, and global cases are inspectable and editable.
- It asks for hypotheses, disconfirming evidence, source-quality rules, contradictions, open risks, and Phoenix Omega implementation implications.
- It emits provider-specific variants instead of one generic prompt.

## Files

- Legacy prompt: `before_legacy_prompt.md`
- brief: `global-social-media-pipeline_research_brief.yaml`
- routing: `global-social-media-pipeline_routing.yaml`
- prompt_master: `global-social-media-pipeline_master_prompt.md`
- prompt_gemini: `global-social-media-pipeline_gemini_prompt.md`
- prompt_qwen_china: `global-social-media-pipeline_qwen_china_prompt.md`
- prompt_rakuten_japan: `global-social-media-pipeline_rakuten_japan_prompt.md`
- index: `global-social-media-pipeline_INDEX.md`
