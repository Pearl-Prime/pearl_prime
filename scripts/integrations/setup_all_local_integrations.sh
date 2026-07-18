#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

printf "\nPhoenix Omega local integrations setup\n"
printf "This will walk through WordPress and messaging channels in one pass.\n\n"

run_if_yes() {
  local label="$1"
  local script_path="$2"
  local default_answer="${3:-y}"
  local answer
  printf "%s (y/n) [%s]: " "$label" "$default_answer" >&2
  IFS= read -r answer
  answer="${answer:-$default_answer}"
  if [[ "${answer:l}" == "y" ]]; then
    /bin/zsh "$script_path"
    printf "\n"
  else
    printf "Skipped %s\n\n" "$label"
  fi
}

if [[ -f "${ROOT_DIR}/docs/all_credentials.txt" ]]; then
  run_if_yes "Import local credentials source from docs/all_credentials.txt" "${ROOT_DIR}/scripts/integrations/intake_all_credentials_local.sh"
fi

if [[ -f "${ROOT_DIR}/.env.wordpress.local" ]]; then
  run_if_yes "Set up WordPress interactively" "${ROOT_DIR}/scripts/integrations/setup_wordpress_local.sh" "n"
else
  run_if_yes "Set up WordPress" "${ROOT_DIR}/scripts/integrations/setup_wordpress_local.sh"
fi

run_if_yes "Set up messaging channels" "${ROOT_DIR}/scripts/integrations/setup_messaging_channels_local.sh"

printf "Done.\n"
printf "Docs:\n"
printf "  %s\n" "${ROOT_DIR}/docs/WORDPRESS_LOCAL_SETUP.md"
printf "  %s\n" "${ROOT_DIR}/docs/MESSAGING_CHANNELS_LOCAL_SETUP.md"
printf "  %s\n" "${ROOT_DIR}/docs/LOCAL_CREDENTIALS_INTAKE_RUNBOOK.md"
