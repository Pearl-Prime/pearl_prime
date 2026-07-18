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

# Default + trim URLs (gh secret set can inject trailing newline).
GEMMA_BASE_URL="$(printf '%s' "${GEMMA_BASE_URL:-http://127.0.0.1:11434/v1}" | tr -d '\r\n' | sed 's/[[:space:]]*$//')"
QWEN_BASE_URL="$(printf '%s' "${QWEN_BASE_URL:-http://127.0.0.1:11434/v1}" | tr -d '\r\n' | sed 's/[[:space:]]*$//')"

# Reject DashScope cloud from scheduled Tier-2 pipeline (401 / paid / policy).
for url in "$GEMMA_BASE_URL" "$QWEN_BASE_URL"; do
  case "$url" in
    *dashscope*|*aliyuncs.com*)
      fail "BASE_URL points at DashScope cloud ($url). Use Pearl Star Ollama."
      ;;
  esac
done

GEMMA_MODEL="${GEMMA_MODEL:-gemma3:27b}"
QWEN_MODEL="${QWEN_MODEL:-qwen2.5:14b}"
API_KEY="${QWEN_API_KEY:-ollama}"

echo "=== Pearl News daily preflight ==="
echo "GEMMA_BASE_URL=$GEMMA_BASE_URL model=$GEMMA_MODEL"
echo "QWEN_BASE_URL=$QWEN_BASE_URL model=$QWEN_MODEL"

# ── Ollama reachability + warmup (Python avoids curl/shell quoting issues) ────
PYTHONPATH=. python3 - <<PY
import json
import os
import sys
import urllib.error
import urllib.request

gemma_url = os.environ["GEMMA_BASE_URL"].rstrip("/")
qwen_url = os.environ["QWEN_BASE_URL"].rstrip("/")
gemma_model = os.environ.get("GEMMA_MODEL", "gemma3:27b")
qwen_model = os.environ.get("QWEN_MODEL", "qwen2.5:14b")
api_key = os.environ.get("QWEN_API_KEY", "ollama")


def _post(base: str, payload: dict) -> dict:
    req = urllib.request.Request(
        f"{base}/chat/completions",
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode())


def _tags(base: str) -> list[str]:
    root = base.removesuffix("/v1")
    with urllib.request.urlopen(f"{root}/api/tags", timeout=15) as resp:
        data = json.loads(resp.read().decode())
    return [m["name"] for m in data.get("models", [])]


for label, base in ("GEMMA", gemma_url), ("QWEN", qwen_url):
    try:
        models = _tags(base)
        print(f"{label} Ollama models: {', '.join(models) or '(none)'}")
    except Exception as exc:
        sys.exit(f"PREFLIGHT FAIL: cannot reach {label} Ollama at {base}: {exc}")

print("=== Gemma warmup ===")
try:
    out = _post(gemma_url, {
        "model": gemma_model,
        "messages": [{"role": "user", "content": "ok"}],
        "max_tokens": 8,
        "temperature": 0.0,
    })
    if out.get("error"):
        raise RuntimeError(out["error"])
    print("gemma_warmup_ok=true")
except Exception as exc:
    sys.exit(f"PREFLIGHT FAIL: Gemma warmup: {exc}")

print("=== Qwen warmup ===")
try:
    out = _post(qwen_url, {
        "model": qwen_model,
        "messages": [{"role": "user", "content": "ok"}],
        "max_tokens": 8,
        "temperature": 0.0,
        "enable_thinking": False,
    })
    if out.get("error"):
        raise RuntimeError(out["error"])
    print("qwen_warmup_ok=true")
except Exception as exc:
    sys.exit(f"PREFLIGHT FAIL: Qwen warmup: {exc}")

print("=== Preflight passed ===")
PY
