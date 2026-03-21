#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
CONFIG_FILE="${ROOT_DIR}/.messaging_channels.local.yaml"
SOURCE_FILE="${ROOT_DIR}/docs/all_credentials.txt"

extract_first_email() {
  local pattern="$1"
  if [[ ! -f "$SOURCE_FILE" ]]; then
    return 0
  fi
  awk -v pat="$pattern" '
    BEGIN { IGNORECASE = 1 }
    $0 ~ pat { capture = 1; next }
    capture && match($0, /[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/) {
      print substr($0, RSTART, RLENGTH)
      exit
    }
  ' "$SOURCE_FILE"
}

extract_first_phoneish() {
  local pattern="$1"
  if [[ ! -f "$SOURCE_FILE" ]]; then
    return 0
  fi
  awk -v pat="$pattern" '
    BEGIN { IGNORECASE = 1 }
    $0 ~ pat { capture = 1; next }
    capture && match($0, /[0-9]{7,15}/) {
      print substr($0, RSTART, RLENGTH)
      exit
    }
  ' "$SOURCE_FILE"
}

yaml_value() {
  local key="$1"
  python3 - "$CONFIG_FILE" "$key" <<'PY'
import sys
from pathlib import Path
try:
    import yaml
except Exception:
    print("")
    raise SystemExit(0)

path = Path(sys.argv[1])
key = sys.argv[2].split(".")
if not path.exists():
    print("")
    raise SystemExit(0)
data = yaml.safe_load(path.read_text()) or {}
cur = data
for part in key:
    if not isinstance(cur, dict):
        print("")
        raise SystemExit(0)
    cur = cur.get(part)
    if cur is None:
        print("")
        raise SystemExit(0)
print(cur)
PY
}

check_keychain() {
  local service="$1"
  local account="$2"
  if security find-generic-password -s "$service" -a "$account" >/dev/null 2>&1; then
    printf "present"
  else
    printf "missing"
  fi
}

print_field() {
  local label="$1"
  local value="$2"
  if [[ -n "$value" && "$value" != "None" ]]; then
    printf "  - %s: present (%s)\n" "$label" "$value"
  else
    printf "  - %s: missing\n" "$label"
  fi
}

print_secret_field() {
  local label="$1"
  local service="$2"
  local account="$3"
  printf "  - %s: %s\n" "$label" "$(check_keychain "$service" "$account")"
}

GENERAL_EMAIL="$(extract_first_email "Whatsapp and WeChat and all other integrations")"
FB_HINT="$(extract_first_phoneish "^facebook$")"

printf "Phoenix Omega messaging requirements report\n\n"

printf "Hints from local credentials file:\n"
printf "  - account email hint: %s\n" "${GENERAL_EMAIL:-missing}"
printf "  - phone/profile hint: %s\n\n" "${FB_HINT:-missing}"

printf "LINE\n"
print_field "channel/user/group id" "$(yaml_value channels.line.user_id)"
print_field "group id" "$(yaml_value channels.line.group_id)"
print_field "channel id" "$(yaml_value channels.line.channel_id)"
print_secret_field "channel access token" "phoenix-omega-line" "access_token"
print_secret_field "channel secret" "phoenix-omega-line" "channel_secret"
printf "\n"

printf "WhatsApp\n"
print_field "recipient phone number" "$(yaml_value channels.whatsapp.phone_number)"
print_field "phone number id" "$(yaml_value channels.whatsapp.phone_number_id)"
print_field "business account id" "$(yaml_value channels.whatsapp.business_account_id)"
print_field "verify token" "$(yaml_value channels.whatsapp.verify_token)"
print_secret_field "access token" "phoenix-omega-whatsapp" "access_token"
print_secret_field "app secret" "phoenix-omega-whatsapp" "app_secret"
printf "\n"

printf "WeChat\n"
print_field "wechat id" "$(yaml_value channels.wechat.wechat_id)"
print_field "app id" "$(yaml_value channels.wechat.app_id)"
print_field "recipient openid" "$(yaml_value channels.wechat.recipient_openid)"
print_field "verify token" "$(yaml_value channels.wechat.verify_token)"
print_secret_field "app secret" "phoenix-omega-wechat" "app_secret"
printf "\n"

printf "Messenger\n"
print_field "profile hint" "$(yaml_value channels.messenger.profile)"
print_field "page id" "$(yaml_value channels.messenger.page_id)"
print_field "recipient PSID" "$(yaml_value channels.messenger.recipient_id)"
print_field "verify token" "$(yaml_value channels.messenger.verify_token)"
print_secret_field "page access token" "phoenix-omega-messenger" "page_access_token"
print_secret_field "app secret" "phoenix-omega-messenger" "app_secret"
printf "\n"

printf "iMessage\n"
print_field "handle" "$(yaml_value channels.imessage.handle)"
