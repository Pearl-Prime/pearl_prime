#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
OUT_FILE="${ROOT_DIR}/.messaging_channels.local.yaml"

if [[ ! -f "$OUT_FILE" ]]; then
  echo "Missing $OUT_FILE. Run scripts/integrations/setup_messaging_channels_local.sh first." >&2
  exit 1
fi

echo "Messaging config file found:"
echo "  $OUT_FILE"
echo
echo "Configured channel stubs:"
/usr/bin/grep -E '^  [a-z]+:|^    enabled:|^    keychain_service:' "$OUT_FILE"
