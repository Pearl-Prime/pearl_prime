# LLM callers audit

- Violations: **13**
- Files scanned: **17899**

## `pearl_news/pipeline/slot_expansion_engine.py`:149 — `anthropic_api_key_read`

- Reason: Reading ANTHROPIC_API_KEY from env is banned. Tier 1 = Claude Code subscription; Tier 2 = Gemma/Qwen on Pearl Star.
- Snippet: `os.environ.get("ANTHROPIC_API_KEY"`

## `tools/teacher_mining/intake_normalize.py`:86 — `anthropic_api_key_read`

- Reason: Reading ANTHROPIC_API_KEY from env is banned. Tier 1 = Claude Code subscription; Tier 2 = Gemma/Qwen on Pearl Star.
- Snippet: `os.environ.get("ANTHROPIC_API_KEY"`

## `tools/teacher_mining/intake_normalize.py`:263 — `anthropic_api_key_read`

- Reason: Reading ANTHROPIC_API_KEY from env is banned. Tier 1 = Claude Code subscription; Tier 2 = Gemma/Qwen on Pearl Star.
- Snippet: `os.environ.get("ANTHROPIC_API_KEY"`

## `scripts/manga/forensic_quality_sprint.py`:15 — `claude_api_key_read`

- Reason: Reading CLAUDE_API_KEY from env is banned. Tier 1 = Claude Code subscription.
- Snippet: `os.environ.get("CLAUDE_API_KEY"`

## `pearl_news/pipeline/slot_expansion_engine.py`:203 — `anthropic_api_direct`

- Reason: Anthropic API is paid. Route via phoenix_v4.llm.router.route_llm (Tier 2) or operator Claude Code (Tier 1).
- Snippet: `Anthropic(api_key=`

## `tools/teacher_mining/intake_normalize.py`:96 — `anthropic_api_direct`

- Reason: Anthropic API is paid. Route via phoenix_v4.llm.router.route_llm (Tier 2) or operator Claude Code (Tier 1).
- Snippet: `anthropic.Anthropic(`

## `pearl_news/pipeline/slot_expansion_engine.py`:207 — `anthropic_messages_create`

- Reason: Anthropic messages API is paid.
- Snippet: `.messages.create(`

## `tools/teacher_mining/intake_normalize.py`:97 — `anthropic_messages_create`

- Reason: Anthropic messages API is paid.
- Snippet: `.messages.create(`

## `.github/workflows/research-pipeline-run.yml`:45 — `openai_api_cloud`

- Reason: OpenAI client must target local Ollama only (line_allow_substrings checked).
- Snippet: `from openai import OpenAI`

## `pearl_news/pipeline/llm_expand.py`:309 — `openai_api_cloud`

- Reason: OpenAI client must target local Ollama only (line_allow_substrings checked).
- Snippet: `from openai import OpenAI`

## `pearl_news/pipeline/slot_provider_qwen.py`:151 — `openai_api_cloud`

- Reason: OpenAI client must target local Ollama only (line_allow_substrings checked).
- Snippet: `from openai import OpenAI`

## `scripts/localization/llm_client.py`:217 — `openai_api_cloud`

- Reason: OpenAI client must target local Ollama only (line_allow_substrings checked).
- Snippet: `openai.OpenAI(`

## `scripts/research/run_research.py`:281 — `openai_api_cloud`

- Reason: OpenAI client must target local Ollama only (line_allow_substrings checked).
- Snippet: `from openai import OpenAI`

