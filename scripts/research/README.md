# Generational research scripts

**Repo standard:** two-pass Qwen3 research on the **Qwen API key lane** (OpenAI-compatible HTTP — same as GitHub Actions). See [docs/AGENT_QWEN_API_KEY_LANE.md](../../docs/AGENT_QWEN_API_KEY_LANE.md). Spec and offline variant: [docs/research/continue_gen_research3.md](../../docs/research/continue_gen_research3.md).

## Prerequisites

- Python 3.9+ with **`openai`**, **`requests`**, **`pyyaml`**: `pip install openai requests pyyaml`.

### Qwen API (default) — OpenAI-compatible endpoint (repo standard)

Same pattern as `pearl_news/pipeline/slot_provider_qwen.py` and GitHub workflows:

| Variable | Fallback file |
|----------|----------------|
| `QWEN_BASE_URL` | `docs/qwen_api_base_url.txt` (e.g. `https://dashscope.aliyuncs.com/compatible-mode/v1`) |
| `QWEN_API_KEY` | `docs/qwen_api_key.txt` |
| `QWEN_MODEL` | `docs/qwen_model.txt` (default `qwen-plus` if key set) |

Pass 1 uses `extra_body={"enable_thinking": True}`; pass 2 uses `enable_thinking=False` and continues the chat with the pass-1 assistant message.

### Ollama / local (optional backward compat only)

**Do not treat this as the default lane for agents or CI.** Use only for local experiments.

If `QWEN_BASE_URL` contains **`11434`**, the runner uses Ollama **`/api/generate`** instead (append `/think` / `/no_think`). With **no** base URL and **no** API key, it may default to `http://localhost:11434` + `OLLAMA_MODEL` / `qwen3:14b`. That path is **not** the repo’s stated standard; prefer **Qwen API** secrets above.

## Usage

```bash
# Load all keys from Keychain first (see CLAUDE.md or docs/INTEGRATION_CREDENTIALS_REGISTRY.md)
for key in QWEN_API_KEY DASHSCOPE_API_KEY RUNCOMFY_API_KEY ELEVENLABS_API_KEY ANTHROPIC_API_KEY DEEPSEEK_API_KEY CLOUDFLARE_ACCOUNT_ID CLOUDFLARE_API_TOKEN CLOUDFLARE_AI_API_TOKEN WORDPRESS_SITE_URL WORDPRESS_USERNAME WORDPRESS_APP_PASSWORD YT_CLIENT_ID_SP YT_CLIENT_SECRET_SP YT_CLIENT_ID_CC YT_CLIENT_SECRET_CC TIKTOK_CLIENT_KEY_SP TIKTOK_CLIENT_SECRET_SP TIKTOK_CLIENT_KEY_CC TIKTOK_CLIENT_SECRET_CC QWEN_BASE_URL QWEN_MODEL RUNCOMFY_DEPLOYMENT_ID META_APP_ID META_APP_SECRET SLACK_BOT_TOKEN SLACK_SIGNING_SECRET TELEGRAM_BOT_TOKEN DISCORD_BOT_TOKEN GITHUB_PAT; do
  val=$(security find-generic-password -s "phoenix-omega" -a "$key" -w 2>/dev/null)
  [ -n "$val" ] && export $key="$val"
done

# From repo root. Direct runs are legacy feed extraction only.
python scripts/research/run_research.py --prompt-id psychology --paste artifacts/research/raw/sample.txt --allow-legacy-direct-run
python scripts/research/run_research.py --prompt-id pain_points --paste - --allow-legacy-direct-run
python scripts/research/run_research.py --prompt-id event_impact --skip-yaml-pass --allow-legacy-direct-run
```

- **--prompt-id:** `psychology` | `pain_points` | `event_impact` | `narrative` | `platform` | `linguistic` | `semantic_trend`
- **--paste:** Path to raw data file, or `-` to read from stdin.
- **--skip-yaml-pass:** Only run the reasoning pass (writes `.reasoning.md` only).
- **--model:** Override model id (else `QWEN_MODEL` / file, or Ollama `OLLAMA_MODEL` / `qwen3:14b`).
- **--out-dir:** Override output directory (default: `artifacts/research/<layer>/`).
- **--output-stem:** Fixed names `<STEM>_reasoning.md` and `<STEM>.yaml` (e.g. `2026-03-31`). Pass 1 frontmatter includes `mode: reasoning (enable_thinking=True)` on API path, or `reasoning (/think)` on Ollama.
- **--allow-legacy-direct-run:** Required for the old direct Qwen/Ollama feed-extraction lane. Do not use it for messy, implementation-adjacent, regional, or decision-oriented Pearl_Research.

Outputs:

- `artifacts/research/<layer>/<timestamp>_reasoning.md` — Pass 1 (thinking) response (default stem), or `<STEM>_reasoning.md` with `--output-stem`.
- `artifacts/research/<layer>/<timestamp>.yaml` — Pass 2 YAML with provenance header (or `<STEM>.yaml`).

**Batch (local):** `bash scripts/research/run_all_layers_20260331.sh` with optional `PASTE=...` and `STEM=2026-03-31`.

**semantic_trend** writes to `artifacts/research/semantic_trend/` (dim 6 linguistic remains `artifacts/research/linguistic/`).

## Pre-Research Prompt Generation

Pearl_Research now has a prompt-generation layer that runs before any model
research execution. Use it when the operator has a messy chat/session,
failing output, issue context, or repo files and needs a stronger downstream
deep-research prompt first.

Direct execution without `--prepare-deep-research-prompt` is blocked unless the
caller explicitly opts into `--allow-legacy-direct-run` or sets
`PEARL_RESEARCH_ALLOW_LEGACY_DIRECT_RUN=1`.

```bash
python scripts/research/run_research.py \
  --prompt-id platform \
  --paste path/to/full_session.txt \
  --prepare-deep-research-prompt \
  --brief-issue "What decision does Phoenix Omega need research to make?" \
  --brief-market Japan \
  --brief-locale ja-JP \
  --brief-platform LINE \
  --brief-platform "Rakuten Kobo" \
  --brief-source-preference "Japanese-language platform docs" \
  --brief-exclude "generic global funnel advice" \
  --output-stem japan-line-funnel
```

This exits before the Qwen/Ollama research passes. It writes a package under
`artifacts/research/prompt_packages/` by default:

- `<stem>_research_brief.yaml` — structured transcript-to-research brief.
- `<stem>_routing.yaml` — inspectable provider recommendation and routing signals.
- `<stem>_master_prompt.md` — provider-neutral master prompt.
- `<stem>_gemini_prompt.md` — Gemini Deep Research version.
- `<stem>_qwen_china_prompt.md` — Qwen / QuinChat China version.
- `<stem>_rakuten_japan_prompt.md` — Rakuten Chat AI / Japan-native version.
- `<stem>_INDEX.md` — package manifest and recommended prompt key.

Routing is data-driven in
`config/research/deep_research_prompt_routing.yaml`: China/`zh-CN` routes to
Qwen / QuinChat-style prompts, Japan/`ja-JP` routes to Rakuten/Japan-native
prompts, and global or ambiguous work defaults to Gemini. The builder always
emits all four prompt variants so the operator can override the recommendation
without regenerating the package.

Explicit `--brief-market`, `--brief-locale`, and `--brief-platform` values
override noisy regional mentions in the transcript.

Before actual research starts, confirm the package includes the brief YAML,
routing YAML, master prompt, Gemini prompt, Qwen/China prompt, Rakuten/Japan
prompt, and index.

To regenerate the before/after examples and scoring artifact:

```bash
python3 scripts/research/evaluate_prompt_generation.py
```

Example packages live in `artifacts/research/prompt_generation_examples/` and
cover one China case, one Japan case, and one global case.
