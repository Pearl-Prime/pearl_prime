#!/bin/zsh
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
/bin/zsh "${ROOT_DIR}/scripts/integrations/send_message.sh" --channel slack "$@"
