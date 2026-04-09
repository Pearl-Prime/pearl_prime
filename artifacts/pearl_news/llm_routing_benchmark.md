# Pearl News — LLM Routing Benchmark (comparative)

**Date:** 2026-04-09  
**Branch:** `agent/pearl-news-llm-routing`  
**Config:** `pearl_news/config/llm_expansion.yaml` (`routing` + `ei_scoring`)

## Environment (_runner at benchmark time_)

| Check | Result |
|-------|--------|
| `ANTHROPIC_API_KEY` | Not set → EN path invoked Claude, failed, **fallback to Qwen** per `routing.fallback.on_provider_error` |
| Pearl Star `http://192.168.1.112:11434/v1` | Reachable; **`qwen3:14b` 404** (model name not available on server) |
| Expansion | All retries exhausted; **draft = assembler output** |
| EI v2 | **Enabled**; scoring ran on HTML body |
| Validation | **3/8 gates failed** on placeholder content (`named_teacher`, `youth_anchor`, `no_banned_phrases`) |

## Planned matrix (re-run when keys + model are healthy)

| Run | Lang | Provider | N=3 | Record: time (s), est. tokens*, EI composite, per-dimension scores, manual rubric (structure/voice/cultural), gate pass rate |
|-----|------|----------|-----|----------------------------------------------------------------------------------------------------------------------------------|
| A | EN | Claude | ☐ | Expect: higher anchor density + contradiction clarity vs Qwen |
| B | EN | Qwen | ☐ | Temporarily force `language_map.en: qwen` or use pre-routing baseline |
| C | JA | Qwen | ☐ | Expect: stronger keigo / indirect framing vs EN-model |
| D | ZH-CN | Qwen | ☐ | Expect: gaokao/tangping/996 framing |

\*Token counts: add logging in `llm_expand` / Claude client if product needs exact I/O token reporting; Ollama may expose usage in response body when available.

## Single-sample measurements (UN item `f565a3628a8c1f7d`, limit=1)

| Metric | EN | JA | ZH-CN |
|--------|-----|-----|-------|
| Expansion provider (intended) | claude → fallback qwen | qwen | qwen |
| Expansion success | No | No | No |
| EI composite | ~0.80 | ~0.80 | *(same code path)* |
| Validation passed | No | No | No |

## Hypotheses to validate after full run

- EN + Claude > EN + Qwen on prose precision and anchors.  
- JA/ZH-CN + Qwen > Claude on cultural markers and register.  
- CJK + local Qwen latency < CJK + Claude (multi-slot API).

## Commands (repo root)

```bash
PYTHONPATH=. python3 -m pearl_news.pipeline.run_article_pipeline --language en --limit 3 --expand --validate
PYTHONPATH=. python3 -m pearl_news.pipeline.run_article_pipeline --language ja --limit 3 --expand --validate
PYTHONPATH=. python3 -m pearl_news.pipeline.run_article_pipeline --language zh-cn --limit 3 --expand --validate
```

Ensure: `eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"` and Ollama model pulled on Pearl Star.
