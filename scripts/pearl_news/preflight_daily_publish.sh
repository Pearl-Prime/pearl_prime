#!/usr/bin/env bash
# Preflight checks for Pearl News daily publish (GHA or local cron).
# Fails fast when secrets or Pearl Star Ollama are misconfigured.
set -euo pipefail

fail() { echo "PREFLIGHT FAIL: $*" >&2; exit 1; }

# ── Required env vars ────────────────────────────────────────────────────────
for var in WORDPRESS_SITE_URL WORDPRESS_USERNAME WORDPRESS_APP_PASSWORD; do
  if [ -z "${!var:-}" ]; then
    fail "$var is not set"
  fi
done

if [ -z "${GEMMA_BASE_URL:-}" ]; then
  fail "GEMMA_BASE_URL is empty — run: bash scripts/pearl_news/wire_github_secrets.sh"
fi
if [ -z "${QWEN_BASE_URL:-}" ]; then
  fail "QWEN_BASE_URL is empty — run: bash scripts/pearl_news/wire_github_secrets.sh"
fi

# Reject DashScope cloud from scheduled Tier-2 pipeline (401 / paid / policy).
for url in "$GEMMA_BASE_URL" "$QWEN_BASE_URL"; do
  case "$url" in
    *dashscope*|*aliyuncs.com*)
      fail "BASE_URL points at DashScope cloud ($url). Use Pearl Star Ollama (pearlstar.tail7fd910.ts.net:11434/v1)."
      ;;
  esac
done

GEMMA_MODEL="${GEMMA_MODEL:-gemma3:27b}"
QWEN_MODEL="${QWEN_MODEL:-qwen2.5:14b}"
API_KEY="${QWEN_API_KEY:-ollama}"

echo "=== Pearl News daily preflight ==="
echo "GEMMA_BASE_URL=$GEMMA_BASE_URL model=$GEMMA_MODEL"
echo "QWEN_BASE_URL=$QWEN_BASE_URL model=$QWEN_MODEL"

# ── Ollama model list (optional quick reachability) ───────────────────────────
OLLAMA_ROOT="${GEMMA_BASE_URL%/v1}"
if curl -fsS --max-time 15 "${OLLAMA_ROOT}/api/tags" > /tmp/ollama_tags.json 2>/dev/null; then
  python3 - <<'PY'
import json, sys
data = json.load(open("/tmp/ollama_tags.json"))
models = [m["name"] for m in data.get("models", [])]
print("Ollama models:", ", ".join(models) or "(none)")
for need in ("gemma", "qwen"):
    if not any(need in m.lower() for m in models):
        print(f"WARNING: no {need} model in Ollama tags", file=sys.stderr)
PY
else
  echo "WARNING: could not reach ${OLLAMA_ROOT}/api/tags (runner may lack Tailscale)" >&2
fi

# ── Warmup: Gemma (EN) ───────────────────────────────────────────────────────
echo "=== Gemma warmup ==="
curl -fsS --max-time 120 "${GEMMA_BASE_URL}/chat/completions" \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer ${API_KEY}" \
  -d "{\"model\":\"${GEMMA_MODEL}\",\"messages\":[{\"role\":\"user\",\"content\":\"ok\"}],\"max_tokens\":8,\"temperature\":0.0}" \
  > /tmp/gemma_warmup.json
python3 - <<'PY'
import json, sys
data = json.load(open("/tmp/gemma_warmup.json"))
if data.get("error"):
    sys.exit(f"Gemma warmup failed: {data['error']}")
print("gemma_warmup_ok=true")
PY

# ── Warmup: Qwen (CJK) ───────────────────────────────────────────────────────
echo "=== Qwen warmup ==="
curl -fsS --max-time 120 "${QWEN_BASE_URL}/chat/completions" \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer ${API_KEY}" \
  -d "{\"model\":\"${QWEN_MODEL}\",\"messages\":[{\"role\":\"user\",\"content\":\"ok\"}],\"max_tokens\":8,\"temperature\":0.0,\"enable_thinking\":false}" \
  > /tmp/qwen_warmup.json
python3 - <<'PY'
import json, sys
data = json.load(open("/tmp/qwen_warmup.json"))
if data.get("error"):
    sys.exit(f"Qwen warmup failed: {data['error']}")
print("qwen_warmup_ok=true")
PY

echo "=== Preflight passed ==="
