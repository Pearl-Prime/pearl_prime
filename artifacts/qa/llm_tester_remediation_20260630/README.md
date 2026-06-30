# LLM Tester Free-Only Remediation — 2026-06-30

Repoint two CI quality testers off the paid Anthropic path onto the FREE local
Ollama router (`phoenix_v4.llm.router.route_llm`), and remove their CI allowlist
exemptions so the enforcer (`scripts/ci/audit_llm_callers.py`) becomes a real
oracle for them.

## Files changed
- `scripts/ci/llm_cohesive_bestseller_tester.py` — `call_llm()` rewired to router
- `scripts/ci/llm_bestseller_error_report.py` — `call_llm()` rewired to router (+ dropped now-unused `import os`)
- `config/governance/banned_llm_patterns.yaml` — removed 4 exempt_paths lines (2 per rule × these 2 files)

## Routing
- `route_llm(language="auto", ...)` → router auto-detects: EN → Gemma (`gemma2:9b`), CJK → Qwen (`qwen2.5:7b`).
- Models inherited from the router defaults / env (`GEMMA_MODEL` / `QWEN_MODEL`); no new model introduced.
- On router import failure → `{"llm_skipped": True, "reason": "router_unavailable"}`.
- On Ollama unreachable / route error → `{"llm_skipped": True, "reason": "ollama_unreachable"}`. NEVER a paid fallback.

## Proof artifacts
- `audit_BEFORE.txt` — exemptions removed, OLD code present → **4 violations** (gate bites).
- `audit_AFTER.txt` — cleaned code + exemptions removed → **0 violations** (scoped).
- `audit_FULLREPO_after.txt` — full-repo audit → **0 violations**.
- `grep_clean.txt` — `anthropic|openai|ANTHROPIC_API_KEY|OPENAI_API_KEY|api_key|claude-sonnet` over both files → **zero hits**.
- `rap_compliance.txt` — `check_rap_compliance.py` → OK, no violations.
- `dryrun_error_report.txt`, `dryrun_cohesive_tester.txt` — `--llm` with Ollama unreachable → clean `ollama_unreachable` skip, no crash, no key lookup.
