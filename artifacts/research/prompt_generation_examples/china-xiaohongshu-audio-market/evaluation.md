# Before / After Evaluation

Case: `china_xiaohongshu_audio_market`
Recommended route: `Qwen / QuinChat-style China Deep Research`
Recommended prompt key: `qwen_china`

## Quality Score

| Criterion | Legacy | New |
|---|---:|---:|
| exact_research_objective | no | yes |
| system_business_context | no | yes |
| failure_symptoms | no | yes |
| hypotheses_to_test | no | yes |
| specific_questions | no | yes |
| required_comparisons | yes | yes |
| decision_output | no | yes |
| evidence_standards | no | yes |
| source_quality_rules | no | yes |
| no_generic_advice | no | yes |
| contradictions_uncertainty | yes | yes |
| phoenix_implications | no | yes |
| provenance_sources | yes | yes |
| **Total** | **3/13** | **13/13** |

## Why The New Prompt Is Stronger

- It adds a structured research brief before execution, preserving the operator's messy context without asking the downstream engine to infer the real decision from noise.
- It routes explicitly using `config/research/deep_research_prompt_routing.yaml`, so China, Japan, and global cases are inspectable and editable.
- It asks for hypotheses, disconfirming evidence, source-quality rules, contradictions, open risks, and Phoenix Omega implementation implications.
- It emits provider-specific variants instead of one generic prompt.

## Files

- Legacy prompt: `before_legacy_prompt.md`
- brief: `china-xiaohongshu-audio-market_research_brief.yaml`
- routing: `china-xiaohongshu-audio-market_routing.yaml`
- prompt_master: `china-xiaohongshu-audio-market_master_prompt.md`
- prompt_gemini: `china-xiaohongshu-audio-market_gemini_prompt.md`
- prompt_qwen_china: `china-xiaohongshu-audio-market_qwen_china_prompt.md`
- prompt_rakuten_japan: `china-xiaohongshu-audio-market_rakuten_japan_prompt.md`
- index: `china-xiaohongshu-audio-market_INDEX.md`
