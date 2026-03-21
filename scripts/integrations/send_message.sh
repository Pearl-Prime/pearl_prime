#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

python3 "${ROOT_DIR}/scripts/integrations/send_message.py" "$@"
