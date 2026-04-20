# LLM callers audit

- Violations: **40**
- Files scanned: **17902**

## `_wt_beatmap/pearl_news/pipeline/llm_expand_claude.py`:396 — `anthropic_api_direct`

- Reason: Anthropic API is paid. Route prose via phoenix_v4.llm.router.route_llm (Gemma/Qwen on Pearl Star) or operator Claude Code.
- Snippet: `Anthropic(api_key=`

## `_wt_beatmap/scripts/ci/llm_bestseller_error_report.py`:191 — `anthropic_api_direct`

- Reason: Anthropic API is paid. Route prose via phoenix_v4.llm.router.route_llm (Gemma/Qwen on Pearl Star) or operator Claude Code.
- Snippet: `anthropic.Anthropic(`

## `_wt_beatmap/scripts/ci/llm_cohesive_bestseller_tester.py`:490 — `anthropic_api_direct`

- Reason: Anthropic API is paid. Route prose via phoenix_v4.llm.router.route_llm (Gemma/Qwen on Pearl Star) or operator Claude Code.
- Snippet: `anthropic.Anthropic(`

## `_wt_beatmap/tools/teacher_mining/intake_normalize.py`:96 — `anthropic_api_direct`

- Reason: Anthropic API is paid. Route prose via phoenix_v4.llm.router.route_llm (Gemma/Qwen on Pearl Star) or operator Claude Code.
- Snippet: `anthropic.Anthropic(`

## `_wt_inj/pearl_news/pipeline/llm_expand_claude.py`:396 — `anthropic_api_direct`

- Reason: Anthropic API is paid. Route prose via phoenix_v4.llm.router.route_llm (Gemma/Qwen on Pearl Star) or operator Claude Code.
- Snippet: `Anthropic(api_key=`

## `_wt_inj/scripts/ci/llm_bestseller_error_report.py`:191 — `anthropic_api_direct`

- Reason: Anthropic API is paid. Route prose via phoenix_v4.llm.router.route_llm (Gemma/Qwen on Pearl Star) or operator Claude Code.
- Snippet: `anthropic.Anthropic(`

## `_wt_inj/scripts/ci/llm_cohesive_bestseller_tester.py`:490 — `anthropic_api_direct`

- Reason: Anthropic API is paid. Route prose via phoenix_v4.llm.router.route_llm (Gemma/Qwen on Pearl Star) or operator Claude Code.
- Snippet: `anthropic.Anthropic(`

## `_wt_inj/tools/teacher_mining/intake_normalize.py`:96 — `anthropic_api_direct`

- Reason: Anthropic API is paid. Route prose via phoenix_v4.llm.router.route_llm (Gemma/Qwen on Pearl Star) or operator Claude Code.
- Snippet: `anthropic.Anthropic(`

## `pearl_news/pipeline/slot_expansion_engine.py`:203 — `anthropic_api_direct`

- Reason: Anthropic API is paid. Route prose via phoenix_v4.llm.router.route_llm (Gemma/Qwen on Pearl Star) or operator Claude Code.
- Snippet: `Anthropic(api_key=`

## `phoenix_v4/rendering/pearl_writer_expand.py`:153 — `anthropic_api_direct`

- Reason: Anthropic API is paid. Route prose via phoenix_v4.llm.router.route_llm (Gemma/Qwen on Pearl Star) or operator Claude Code.
- Snippet: `Anthropic(api_key=`

## `scripts/ci/llm_bestseller_error_report.py`:191 — `anthropic_api_direct`

- Reason: Anthropic API is paid. Route prose via phoenix_v4.llm.router.route_llm (Gemma/Qwen on Pearl Star) or operator Claude Code.
- Snippet: `anthropic.Anthropic(`

## `scripts/ci/llm_cohesive_bestseller_tester.py`:490 — `anthropic_api_direct`

- Reason: Anthropic API is paid. Route prose via phoenix_v4.llm.router.route_llm (Gemma/Qwen on Pearl Star) or operator Claude Code.
- Snippet: `anthropic.Anthropic(`

## `tools/teacher_mining/intake_normalize.py`:96 — `anthropic_api_direct`

- Reason: Anthropic API is paid. Route prose via phoenix_v4.llm.router.route_llm (Gemma/Qwen on Pearl Star) or operator Claude Code.
- Snippet: `anthropic.Anthropic(`

## `_wt_beatmap/pearl_news/pipeline/llm_expand_claude.py`:399 — `anthropic_messages_create`

- Reason: Anthropic messages API is paid.
- Snippet: `.messages.create(`

## `_wt_beatmap/scripts/ci/llm_bestseller_error_report.py`:192 — `anthropic_messages_create`

- Reason: Anthropic messages API is paid.
- Snippet: `.messages.create(`

## `_wt_beatmap/scripts/ci/llm_cohesive_bestseller_tester.py`:491 — `anthropic_messages_create`

- Reason: Anthropic messages API is paid.
- Snippet: `.messages.create(`

## `_wt_beatmap/tools/teacher_mining/intake_normalize.py`:97 — `anthropic_messages_create`

- Reason: Anthropic messages API is paid.
- Snippet: `.messages.create(`

## `_wt_inj/pearl_news/pipeline/llm_expand_claude.py`:399 — `anthropic_messages_create`

- Reason: Anthropic messages API is paid.
- Snippet: `.messages.create(`

## `_wt_inj/scripts/ci/llm_bestseller_error_report.py`:192 — `anthropic_messages_create`

- Reason: Anthropic messages API is paid.
- Snippet: `.messages.create(`

## `_wt_inj/scripts/ci/llm_cohesive_bestseller_tester.py`:491 — `anthropic_messages_create`

- Reason: Anthropic messages API is paid.
- Snippet: `.messages.create(`

## `_wt_inj/tools/teacher_mining/intake_normalize.py`:97 — `anthropic_messages_create`

- Reason: Anthropic messages API is paid.
- Snippet: `.messages.create(`

## `pearl_news/pipeline/slot_expansion_engine.py`:207 — `anthropic_messages_create`

- Reason: Anthropic messages API is paid.
- Snippet: `.messages.create(`

## `phoenix_v4/rendering/pearl_writer_expand.py`:156 — `anthropic_messages_create`

- Reason: Anthropic messages API is paid.
- Snippet: `.messages.create(`

## `tools/teacher_mining/intake_normalize.py`:97 — `anthropic_messages_create`

- Reason: Anthropic messages API is paid.
- Snippet: `.messages.create(`

## `.github/workflows/research-pipeline-run.yml`:45 — `openai_api_cloud`

- Reason: OpenAI client pointed at api.openai.com is paid. Local Ollama OpenAI-compatible endpoints are allowed (see line_allow_substrings).
- Snippet: `from openai import OpenAI`

## `_wt_beatmap/.github/workflows/research-pipeline-run.yml`:45 — `openai_api_cloud`

- Reason: OpenAI client pointed at api.openai.com is paid. Local Ollama OpenAI-compatible endpoints are allowed (see line_allow_substrings).
- Snippet: `from openai import OpenAI`

## `_wt_beatmap/pearl_news/pipeline/llm_expand.py`:286 — `openai_api_cloud`

- Reason: OpenAI client pointed at api.openai.com is paid. Local Ollama OpenAI-compatible endpoints are allowed (see line_allow_substrings).
- Snippet: `from openai import OpenAI`

## `_wt_beatmap/pearl_news/pipeline/slot_provider_qwen.py`:147 — `openai_api_cloud`

- Reason: OpenAI client pointed at api.openai.com is paid. Local Ollama OpenAI-compatible endpoints are allowed (see line_allow_substrings).
- Snippet: `from openai import OpenAI`

## `_wt_beatmap/scripts/localization/llm_client.py`:217 — `openai_api_cloud`

- Reason: OpenAI client pointed at api.openai.com is paid. Local Ollama OpenAI-compatible endpoints are allowed (see line_allow_substrings).
- Snippet: `openai.OpenAI(`

## `_wt_beatmap/scripts/research/run_research.py`:281 — `openai_api_cloud`

- Reason: OpenAI client pointed at api.openai.com is paid. Local Ollama OpenAI-compatible endpoints are allowed (see line_allow_substrings).
- Snippet: `from openai import OpenAI`

## `_wt_inj/.github/workflows/research-pipeline-run.yml`:45 — `openai_api_cloud`

- Reason: OpenAI client pointed at api.openai.com is paid. Local Ollama OpenAI-compatible endpoints are allowed (see line_allow_substrings).
- Snippet: `from openai import OpenAI`

## `_wt_inj/pearl_news/pipeline/llm_expand.py`:286 — `openai_api_cloud`

- Reason: OpenAI client pointed at api.openai.com is paid. Local Ollama OpenAI-compatible endpoints are allowed (see line_allow_substrings).
- Snippet: `from openai import OpenAI`

## `_wt_inj/pearl_news/pipeline/slot_provider_qwen.py`:147 — `openai_api_cloud`

- Reason: OpenAI client pointed at api.openai.com is paid. Local Ollama OpenAI-compatible endpoints are allowed (see line_allow_substrings).
- Snippet: `from openai import OpenAI`

## `_wt_inj/scripts/localization/llm_client.py`:217 — `openai_api_cloud`

- Reason: OpenAI client pointed at api.openai.com is paid. Local Ollama OpenAI-compatible endpoints are allowed (see line_allow_substrings).
- Snippet: `openai.OpenAI(`

## `_wt_inj/scripts/research/run_research.py`:281 — `openai_api_cloud`

- Reason: OpenAI client pointed at api.openai.com is paid. Local Ollama OpenAI-compatible endpoints are allowed (see line_allow_substrings).
- Snippet: `from openai import OpenAI`

## `pearl_news/pipeline/llm_expand.py`:309 — `openai_api_cloud`

- Reason: OpenAI client pointed at api.openai.com is paid. Local Ollama OpenAI-compatible endpoints are allowed (see line_allow_substrings).
- Snippet: `from openai import OpenAI`

## `pearl_news/pipeline/slot_expansion_engine.py`:278 — `openai_api_cloud`

- Reason: OpenAI client pointed at api.openai.com is paid. Local Ollama OpenAI-compatible endpoints are allowed (see line_allow_substrings).
- Snippet: `from openai import OpenAI`

## `pearl_news/pipeline/slot_provider_qwen.py`:151 — `openai_api_cloud`

- Reason: OpenAI client pointed at api.openai.com is paid. Local Ollama OpenAI-compatible endpoints are allowed (see line_allow_substrings).
- Snippet: `from openai import OpenAI`

## `scripts/localization/llm_client.py`:217 — `openai_api_cloud`

- Reason: OpenAI client pointed at api.openai.com is paid. Local Ollama OpenAI-compatible endpoints are allowed (see line_allow_substrings).
- Snippet: `openai.OpenAI(`

## `scripts/research/run_research.py`:281 — `openai_api_cloud`

- Reason: OpenAI client pointed at api.openai.com is paid. Local Ollama OpenAI-compatible endpoints are allowed (see line_allow_substrings).
- Snippet: `from openai import OpenAI`

