#!/usr/bin/env bash
# Codespaces post-create — provisions the Phoenix Omega cloud-native agent env.
# Idempotent: safe to re-run.

set -euo pipefail

echo "═══ Phoenix Omega — Codespaces post-create ═══"
echo "Branch: $(git branch --show-current 2>/dev/null || echo 'detached')"
echo "Repo:   $(git rev-parse --show-toplevel 2>/dev/null || echo '?')"
echo "Marker: PHOENIX_OMEGA_REMOTE=${PHOENIX_OMEGA_REMOTE:-unset}"

# ── 1. Python deps ──────────────────────────────────────────────────────────
echo "── installing python deps ──"
python -m pip install --upgrade pip >/dev/null

# Core deps from the repo's pinned set, falling back to inline list if missing
if [ -f requirements.txt ]; then
  pip install -r requirements.txt
elif [ -f pyproject.toml ]; then
  pip install -e ".[dev]" 2>/dev/null || pip install -e . 2>/dev/null || true
fi

# Always-needed tooling for agents + push-guard + validators
pip install --quiet \
  pyyaml \
  jsonschema \
  pytest \
  pytest-timeout \
  ruff \
  feedparser \
  requests

# ── 2. Wrangler (Cloudflare CLI) for R2 / Workers ops ──────────────────────
echo "── installing wrangler ──"
npm install -g wrangler@latest >/dev/null 2>&1 || echo "(wrangler install skipped)"

# ── 3. Claude Code CLI (npm package) ───────────────────────────────────────
# The Claude Code VS Code extension is installed via devcontainer.json.
# CLI is optional but useful for terminal-driven sessions.
echo "── installing claude code cli ──"
npm install -g @anthropic-ai/claude-code 2>/dev/null || echo "(claude-code cli skipped — extension still works)"

# ── 4. Git / push-guard sanity ─────────────────────────────────────────────
echo "── git config ──"
git config --global --add safe.directory "$(pwd)"
git config --global pull.rebase false
git config --global init.defaultBranch main

# ── 5. Confirm remote-mode ─────────────────────────────────────────────────
echo "── asserting remote-mode ──"
python scripts/agent/assert_remote.py || {
  echo "⚠️  WARNING: assert_remote check failed — verify PHOENIX_OMEGA_REMOTE env"
}

# ── 6. Display next-steps ──────────────────────────────────────────────────
cat <<'EOF'

═══════════════════════════════════════════════════════════════════════════
✓ Phoenix Omega Codespace ready.

You are now running with:
  • PHOENIX_OMEGA_REMOTE=codespaces (assert_remote.py will pass)
  • All ephemeral state stays in this VM — your laptop never fills up
  • Claude Code via VS Code extension (subscription, operator-present)
  • gh CLI authenticated via Codespaces GITHUB_TOKEN
  • wrangler available for Cloudflare R2 ops (Layer 2)

To start a Pearl_GitHub branch:
  git fetch origin
  git checkout -b agent/<task> origin/main

To run the integration health check:
  python scripts/agent/assert_remote.py
  bash scripts/git/health_check.sh

Layer 1 of the cloud-native migration is active. Layer 2 (R2 artifact
sync) and Layer 3 (Pearl_INT remote-mode guards on Pearl Star) ship next.
═══════════════════════════════════════════════════════════════════════════
EOF
