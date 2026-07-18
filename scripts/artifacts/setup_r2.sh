#!/usr/bin/env bash
# Phoenix Omega R2 bucket setup — idempotent.
# Run from a Codespace (or anywhere with CLOUDFLARE_ACCOUNT_ID + CLOUDFLARE_API_TOKEN
# set) AFTER you've added Cloudflare creds to Codespaces secrets.
#
# This creates the phoenix-omega-artifacts bucket if missing, configures
# CORS for direct uploads from Codespaces, and applies lifecycle rules
# for QA-run rotation. Safe to re-run.

set -euo pipefail

BUCKET="${R2_BUCKET_OVERRIDE:-phoenix-omega-artifacts}"

echo "═══ Phoenix Omega — R2 setup ═══"
echo "Bucket: ${BUCKET}"

# ── Preflight ───────────────────────────────────────────────────────────────
: "${CLOUDFLARE_ACCOUNT_ID:?Set CLOUDFLARE_ACCOUNT_ID (Codespaces secret)}"
: "${CLOUDFLARE_API_TOKEN:?Set CLOUDFLARE_API_TOKEN (Codespaces secret)}"

if ! command -v wrangler >/dev/null 2>&1; then
  echo "❌ wrangler not installed. devcontainer post-create.sh installs it."
  echo "   In Codespaces this should be present; if missing run: npm i -g wrangler"
  exit 2
fi

# ── 1. Auth wrangler with the API token ────────────────────────────────────
# Wrangler reads CLOUDFLARE_API_TOKEN from env automatically.
echo ""
echo "── checking wrangler auth ──"
wrangler whoami 2>&1 | head -5 || {
  echo "wrangler whoami failed; check CLOUDFLARE_API_TOKEN scopes"
  echo "Required scopes: Workers R2 Storage: Edit"
  exit 2
}

# ── 2. Create bucket (idempotent) ──────────────────────────────────────────
echo ""
echo "── ensuring bucket exists ──"
if wrangler r2 bucket list 2>/dev/null | grep -q "^${BUCKET}$"; then
  echo "✓ bucket ${BUCKET} already exists"
else
  echo "creating bucket ${BUCKET}…"
  wrangler r2 bucket create "${BUCKET}"
  echo "✓ created"
fi

# ── 3. CORS for Codespaces direct upload ───────────────────────────────────
echo ""
echo "── applying CORS ──"
CORS_FILE="$(mktemp)"
cat > "${CORS_FILE}" <<'JSON'
[
  {
    "AllowedOrigins": [
      "https://*.github.dev",
      "https://*.app.github.dev",
      "https://github.com"
    ],
    "AllowedMethods": ["GET", "PUT", "POST", "HEAD"],
    "AllowedHeaders": ["*"],
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 3600
  }
]
JSON

if wrangler r2 bucket cors put "${BUCKET}" --file "${CORS_FILE}" 2>&1 | tail -5; then
  echo "✓ CORS applied"
else
  echo "⚠️  CORS configuration failed (non-fatal — bucket still works for boto3)"
fi
rm -f "${CORS_FILE}"

# ── 4. Lifecycle rules (QA rotation + tmp expiry) ──────────────────────────
echo ""
echo "── applying lifecycle rules ──"
LIFECYCLE_FILE="$(mktemp)"
cat > "${LIFECYCLE_FILE}" <<'JSON'
{
  "rules": [
    {
      "id": "rotate-qa-runs-30d",
      "enabled": true,
      "conditions": {"prefix": "qa_runs/"},
      "deleteObjectsTransition": {
        "condition": {"type": "Age", "maxAge": 2592000}
      }
    },
    {
      "id": "expire-tmp-1d",
      "enabled": true,
      "conditions": {"prefix": "tmp/"},
      "deleteObjectsTransition": {
        "condition": {"type": "Age", "maxAge": 86400}
      }
    }
  ]
}
JSON

if wrangler r2 bucket lifecycle set "${BUCKET}" --file "${LIFECYCLE_FILE}" 2>&1 | tail -5; then
  echo "✓ lifecycle rules applied"
else
  echo "⚠️  lifecycle configuration failed (non-fatal — apply via dash if needed)"
fi
rm -f "${LIFECYCLE_FILE}"

# ── 5. Print next steps ────────────────────────────────────────────────────
cat <<EOF

═══════════════════════════════════════════════════════════════════════════
✓ R2 bucket ${BUCKET} is ready.

Next steps:

1. Generate R2 access keys (separate from the API token used above):
     https://dash.cloudflare.com → R2 → Manage R2 API Tokens → Create API Token
     Permission: Object Read & Write
     Bucket scope: ${BUCKET}

2. Add as Codespaces secrets at https://github.com/settings/codespaces:
     R2_ACCESS_KEY_ID
     R2_SECRET_ACCESS_KEY

3. Smoke test from a Codespace:
     python3 scripts/artifacts/r2_sync.py ls --namespace tmp --head 5

4. Try a push:
     mkdir -p /tmp/r2-smoke && echo "hello" > /tmp/r2-smoke/test.txt
     python3 scripts/artifacts/r2_sync.py push \\
       --namespace tmp \\
       --src /tmp/r2-smoke/ \\
       --run-id smoke-\$(date +%s)

═══════════════════════════════════════════════════════════════════════════
EOF
