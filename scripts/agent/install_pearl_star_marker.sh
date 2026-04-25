#!/usr/bin/env bash
# Install the Pearl Star marker file so scripts/agent/assert_remote.py
# accepts the rig as a remote-mode environment.
#
# Run this ONCE on Pearl Star (the RTX 5070 Ti Tailnet host) — not on the
# operator's laptop or in Codespaces.
#
# Usage:
#   ssh pearlstar.tail7fd910.ts.net
#   cd /path/to/phoenix_omega
#   bash scripts/agent/install_pearl_star_marker.sh
#
# The marker is a single empty file at ~/.phoenix_omega_pearl_star.
# assert_remote.py treats its presence as proof the host is Pearl Star.

set -euo pipefail

MARKER="${HOME}/.phoenix_omega_pearl_star"
HOSTNAME_REPORTED="$(hostname -s 2>/dev/null || hostname)"

echo "═══ Phoenix Omega — Pearl Star marker installer ═══"
echo "Host: ${HOSTNAME_REPORTED}"
echo "Marker target: ${MARKER}"

# ── Sanity check: confirm we're actually on Pearl Star ────────────────────
# Pearl Star is the only host that runs FLUX-schnell-fp8 on RTX 5070 Ti.
# Heuristic checks (any one is sufficient):
#   1. nvidia-smi reports an RTX 5070 Ti
#   2. hostname starts with 'pearlstar' or 'pearl-star'
#   3. user explicitly passes --force

FORCE=0
for arg in "$@"; do
  case "$arg" in
    --force) FORCE=1 ;;
  esac
done

is_pearl_star=0
if command -v nvidia-smi >/dev/null 2>&1; then
  if nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | grep -qi "5070 Ti\|5080\|5090"; then
    is_pearl_star=1
    echo "✓ nvidia-smi reports an Ada/Blackwell GPU consistent with Pearl Star"
  fi
fi
case "${HOSTNAME_REPORTED}" in
  pearlstar*|pearl-star*|pearl_star*)
    is_pearl_star=1
    echo "✓ hostname matches pearl-star pattern"
    ;;
esac

if [ "${is_pearl_star}" -eq 0 ] && [ "${FORCE}" -eq 0 ]; then
  echo ""
  echo "⚠️  This host does not look like Pearl Star (no RTX 5070+ GPU detected,"
  echo "    hostname does not start with 'pearlstar')."
  echo ""
  echo "If this IS Pearl Star, re-run with --force:"
  echo "  bash $0 --force"
  echo ""
  echo "Refusing to install marker on a host that may not be Pearl Star."
  exit 1
fi

# ── Create marker (idempotent) ────────────────────────────────────────────
if [ -f "${MARKER}" ]; then
  echo "✓ marker already present: ${MARKER}"
else
  echo "creating marker…"
  cat > "${MARKER}" <<EOF
# Phoenix Omega — Pearl Star marker
# Created: $(date -u +%Y-%m-%dT%H:%M:%SZ)
# Host:    ${HOSTNAME_REPORTED}
# Purpose: signals to scripts/agent/assert_remote.py that this is Pearl Star
EOF
  chmod 600 "${MARKER}"
  echo "✓ created"
fi

# ── Confirm assert_remote accepts the host ────────────────────────────────
if [ -f "scripts/agent/assert_remote.py" ]; then
  echo ""
  echo "── verifying assert_remote ──"
  if python3 scripts/agent/assert_remote.py 2>&1 | tail -1 | grep -q "pearl-star"; then
    echo "✓ assert_remote: pearl-star detected"
  else
    echo "⚠️  assert_remote did not return pearl-star — check that the script"
    echo "    is on the latest main and that the marker path resolves."
  fi
else
  echo "⚠️  scripts/agent/assert_remote.py not found in repo — re-clone or pull."
fi

echo ""
echo "═══ Pearl Star is registered ═══"
echo ""
echo "From now on, render scripts on this host can call the R2 push helper"
echo "(scripts/artifacts/r2_push_helper.py) to upload outputs after a render."
echo ""
echo "Required environment variables (load via integration_env_registry):"
echo "  CLOUDFLARE_ACCOUNT_ID"
echo "  R2_ACCESS_KEY_ID"
echo "  R2_SECRET_ACCESS_KEY"
echo ""
echo "Load them with:"
echo "  eval \"\$(python3 scripts/ci/load_integration_env_from_keychain.py)\""
