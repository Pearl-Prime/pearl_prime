#!/usr/bin/env bash
# Wire Pearl News daily-publish secrets from macOS Keychain → GitHub repo secrets.
# Run on operator Mac with gh CLI authenticated.
#
# Usage:
#   bash scripts/pearl_news/wire_github_secrets.sh          # apply
#   bash scripts/pearl_news/wire_github_secrets.sh --dry-run
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DRY=false
[ "${1:-}" = "--dry-run" ] && DRY=true

eval "$(python3 "$REPO_ROOT/scripts/ci/load_integration_env_from_keychain.py")"

GEMMA_URL="${GEMMA_BASE_URL:-http://pearlstar.tail7fd910.ts.net:11434/v1}"
QWEN_URL="${QWEN_BASE_URL:-http://pearlstar.tail7fd910.ts.net:11434/v1}"
GEMMA_MODEL="${GEMMA_MODEL:-gemma3:27b}"
QWEN_MODEL="${QWEN_MODEL:-qwen2.5:14b}"

set_secret() {
  local name="$1" value="$2"
  if [ "$DRY" = true ]; then
    echo "[dry-run] gh secret set $name"
    return
  fi
  printf '%s' "$value" | gh secret set "$name" --body -
  echo "Set $name"
}

echo "Wiring Pearl News secrets to $(gh repo view --json nameWithOwner -q .nameWithOwner)"
echo "  GEMMA_BASE_URL=$GEMMA_URL"
echo "  GEMMA_MODEL=$GEMMA_MODEL"
echo "  QWEN_BASE_URL=$QWEN_URL"
echo "  QWEN_MODEL=$QWEN_MODEL"
echo "  QWEN_API_KEY=ollama (Ollama placeholder)"

set_secret GEMMA_BASE_URL "$GEMMA_URL"
set_secret GEMMA_MODEL "$GEMMA_MODEL"
set_secret QWEN_BASE_URL "$QWEN_URL"
set_secret QWEN_MODEL "$QWEN_MODEL"
set_secret QWEN_API_KEY "ollama"

# WordPress — only if present in Keychain
for var in WORDPRESS_SITE_URL WORDPRESS_USERNAME WORDPRESS_APP_PASSWORD; do
  val="${!var:-}"
  if [ -n "$val" ]; then
    set_secret "$var" "$val"
  else
    echo "SKIP $var (not in Keychain)"
  fi
done

echo ""
echo "Done. Verify with: gh secret list | grep -iE 'GEMMA|QWEN|WORDPRESS'"
echo "Re-enable workflow: gh api repos/:owner/:repo/actions/workflows/pearl-news-daily.yml -X PUT -f state=active"
