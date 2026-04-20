# LLM callers audit

- Violations: **6**
- Files scanned: **254**

## `pearl_news/pipeline/slot_expansion_engine.py`:203 — `anthropic_api_direct`

- Reason: Anthropic API is paid. Route via phoenix_v4.llm.router.route_llm (local) or operator Claude Code.
- Snippet: `Anthropic(api_key=`

## `pearl_news/pipeline/slot_expansion_engine.py`:207 — `anthropic_messages_create`

- Reason: Anthropic messages API is paid.
- Snippet: `.messages.create(`

## `pearl_news/pipeline/llm_expand.py`:309 — `openai_api_cloud`

- Reason: OpenAI client must target local Ollama only (see line_allow_substrings).
- Snippet: `from openai import OpenAI`

## `pearl_news/pipeline/slot_expansion_engine.py`:278 — `openai_api_cloud`

- Reason: OpenAI client must target local Ollama only (see line_allow_substrings).
- Snippet: `from openai import OpenAI`

## `pearl_news/pipeline/slot_provider_qwen.py`:151 — `openai_api_cloud`

- Reason: OpenAI client must target local Ollama only (see line_allow_substrings).
- Snippet: `from openai import OpenAI`

## `scripts/localization/llm_client.py`:217 — `openai_api_cloud`

- Reason: OpenAI client must target local Ollama only (see line_allow_substrings).
- Snippet: `openai.OpenAI(`

