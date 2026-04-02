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
# From repo root
python scripts/research/run_research.py --prompt-id psychology --paste artifacts/research/raw/sample.txt
python scripts/research/run_research.py --prompt-id pain_points --paste -
python scripts/research/run_research.py --prompt-id event_impact --skip-yaml-pass
```

- **--prompt-id:** `psychology` | `pain_points` | `event_impact`
- **--paste:** Path to raw data file, or `-` to read from stdin.
- **--skip-yaml-pass:** Only run the reasoning pass (writes `.reasoning.md` only).
- **--model:** Override model id (else `QWEN_MODEL` / file, or Ollama `OLLAMA_MODEL` / `qwen3:14b`).
- **--out-dir:** Override output directory (default: `artifacts/research/<layer>/`).
- **--output-stem:** Fixed names `<STEM>_reasoning.md` and `<STEM>.yaml` (e.g. `2026-03-31`). Pass 1 frontmatter includes `mode: reasoning (enable_thinking=True)` on API path, or `reasoning (/think)` on Ollama.

Outputs:

- `artifacts/research/<layer>/<timestamp>_reasoning.md` — Pass 1 (thinking) response (default stem), or `<STEM>_reasoning.md` with `--output-stem`.
- `artifacts/research/<layer>/<timestamp>.yaml` — Pass 2 YAML with provenance header (or `<STEM>.yaml`).

**Batch (local):** `bash scripts/research/run_all_layers_20260331.sh` with optional `PASTE=...` and `STEM=2026-03-31`.

**semantic_trend** writes to `artifacts/research/semantic_trend/` (dim 6 linguistic remains `artifacts/research/linguistic/`).
