#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
OUT_FILE="${ROOT_DIR}/.messaging_channels.local.yaml"
LOCAL_CREDENTIALS_FILE="${ROOT_DIR}/docs/all_credentials.txt"

extract_first_email() {
  local pattern="$1"
  if [[ ! -f "$LOCAL_CREDENTIALS_FILE" ]]; then
    return 0
  fi
  awk -v pat="$pattern" '
    BEGIN { IGNORECASE = 1 }
    $0 ~ pat { capture = 1; next }
    capture && match($0, /[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/) {
      print substr($0, RSTART, RLENGTH)
      exit
    }
  ' "$LOCAL_CREDENTIALS_FILE"
}

extract_first_phoneish() {
  local pattern="$1"
  if [[ ! -f "$LOCAL_CREDENTIALS_FILE" ]]; then
    return 0
  fi
  awk -v pat="$pattern" '
    BEGIN { IGNORECASE = 1 }
    $0 ~ pat { capture = 1; next }
    capture && match($0, /[0-9]{7,15}/) {
      print substr($0, RSTART, RLENGTH)
      exit
    }
  ' "$LOCAL_CREDENTIALS_FILE"
}

extract_first_after_label() {
  local label="$1"
  if [[ ! -f "$LOCAL_CREDENTIALS_FILE" ]]; then
    return 0
  fi
  awk -v pat="$label" '
    BEGIN { IGNORECASE = 1 }
    $0 ~ pat { capture = 1; next }
    capture && NF {
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", $0)
      print $0
      exit
    }
  ' "$LOCAL_CREDENTIALS_FILE"
}

prompt() {
  local label="$1"
  local default="${2:-}"
  if [[ -n "$default" ]]; then
    printf "%s [%s]: " "$label" "$default" >&2
  else
    printf "%s: " "$label" >&2
  fi
  local value
  IFS= read -r value
  if [[ -z "$value" ]]; then
    value="$default"
  fi
  printf '%s' "$value"
}

prompt_secret() {
  local label="$1"
  printf "%s: " "$label" >&2
  stty -echo
  local value
  IFS= read -r value
  stty echo
  printf "\n" >&2
  printf '%s' "$value"
}

store_secret() {
  local service="$1"
  local account="$2"
  local secret="$3"
  if [[ -n "$secret" ]]; then
    security add-generic-password -U -a "$account" -s "$service" -w "$secret" >/dev/null
  fi
}

yn() {
  local label="$1"
  local answer
  answer="$(prompt "$label (y/n)" "n")"
  [[ "${answer:l}" == "y" ]]
}

DEFAULT_GENERAL_EMAIL="$(extract_first_email "Whatsapp and WeChat and all other integrations")"
DEFAULT_FB_PROFILE="$(extract_first_phoneish "^facebook$")"
DEFAULT_IMESSAGE_HANDLE="${DEFAULT_GENERAL_EMAIL}"
DEFAULT_WECHAT_ID="${DEFAULT_GENERAL_EMAIL}"
DEFAULT_WHATSAPP_PHONE="${DEFAULT_FB_PROFILE}"
DEFAULT_MESSENGER_PROFILE="${DEFAULT_FB_PROFILE}"

if [[ -f "$LOCAL_CREDENTIALS_FILE" ]]; then
  printf "Using local credential hints from %s when available.\n" "$LOCAL_CREDENTIALS_FILE" >&2
  [[ -n "$DEFAULT_GENERAL_EMAIL" ]] && printf "  account hint: %s\n" "$DEFAULT_GENERAL_EMAIL" >&2
  [[ -n "$DEFAULT_FB_PROFILE" ]] && printf "  profile/phone hint: %s\n" "$DEFAULT_FB_PROFILE" >&2
fi

LINE_ENABLED=false
WA_ENABLED=false
WECHAT_ENABLED=false
MESSENGER_ENABLED=false
IMESSAGE_ENABLED=false

if yn "Configure LINE"; then
  LINE_ENABLED=true
  LINE_USER_ID="$(prompt "LINE user ID" "")"
  LINE_GROUP_ID="$(prompt "LINE group ID (optional)" "")"
  LINE_CHANNEL_ID="$(prompt "LINE channel ID" "")"
  LINE_SERVICE="phoenix-omega-line"
  LINE_ACCESS_TOKEN="$(prompt_secret "LINE channel access token")"
  LINE_CHANNEL_SECRET="$(prompt_secret "LINE channel secret")"
  store_secret "$LINE_SERVICE" "access_token" "$LINE_ACCESS_TOKEN"
  store_secret "$LINE_SERVICE" "channel_secret" "$LINE_CHANNEL_SECRET"
fi

if yn "Configure WhatsApp"; then
  WA_ENABLED=true
  WA_PHONE_NUMBER="$(prompt "WhatsApp recipient phone number" "${DEFAULT_WHATSAPP_PHONE:-}")"
  WA_PHONE_NUMBER_ID="$(prompt "WhatsApp phone number ID" "")"
  WA_BUSINESS_ACCOUNT_ID="$(prompt "WhatsApp business account ID" "")"
  WA_VERIFY_TOKEN="$(prompt "WhatsApp verify token" "")"
  WA_GRAPH_VERSION="$(prompt "WhatsApp Graph API version" "v23.0")"
  WA_SERVICE="phoenix-omega-whatsapp"
  WA_ACCESS_TOKEN="$(prompt_secret "WhatsApp access token")"
  WA_APP_SECRET="$(prompt_secret "WhatsApp app secret")"
  store_secret "$WA_SERVICE" "access_token" "$WA_ACCESS_TOKEN"
  store_secret "$WA_SERVICE" "app_secret" "$WA_APP_SECRET"
fi

if yn "Configure WeChat"; then
  WECHAT_ENABLED=true
  WECHAT_ID="$(prompt "WeChat ID" "${DEFAULT_WECHAT_ID:-}")"
  WECHAT_APP_ID="$(prompt "WeChat app ID" "")"
  WECHAT_OPEN_ID="$(prompt "WeChat recipient openid" "")"
  WECHAT_VERIFY_TOKEN="$(prompt "WeChat verify token" "")"
  WECHAT_SERVICE="phoenix-omega-wechat"
  WECHAT_APP_SECRET="$(prompt_secret "WeChat app secret")"
  store_secret "$WECHAT_SERVICE" "app_secret" "$WECHAT_APP_SECRET"
fi

if yn "Configure Messenger"; then
  MESSENGER_ENABLED=true
  MESSENGER_PAGE_ID="$(prompt "Messenger page ID" "")"
  MESSENGER_PROFILE="$(prompt "Messenger profile URL or label" "${DEFAULT_MESSENGER_PROFILE:-}")"
  MESSENGER_RECIPIENT_ID="$(prompt "Messenger recipient PSID" "")"
  MESSENGER_VERIFY_TOKEN="$(prompt "Messenger verify token" "")"
  MESSENGER_GRAPH_VERSION="$(prompt "Messenger Graph API version" "v23.0")"
  MESSENGER_SERVICE="phoenix-omega-messenger"
  MESSENGER_PAGE_ACCESS_TOKEN="$(prompt_secret "Messenger page access token")"
  MESSENGER_APP_SECRET="$(prompt_secret "Messenger app secret")"
  store_secret "$MESSENGER_SERVICE" "page_access_token" "$MESSENGER_PAGE_ACCESS_TOKEN"
  store_secret "$MESSENGER_SERVICE" "app_secret" "$MESSENGER_APP_SECRET"
fi

if yn "Configure iMessage"; then
  IMESSAGE_ENABLED=true
  IMESSAGE_HANDLE="$(prompt "iMessage send/receive handle" "${DEFAULT_IMESSAGE_HANDLE:-}")"
fi

cat > "$OUT_FILE" <<EOF
channels:
  line:
    enabled: ${LINE_ENABLED}
    user_id: "${LINE_USER_ID:-}"
    group_id: "${LINE_GROUP_ID:-}"
    channel_id: "${LINE_CHANNEL_ID:-}"
    keychain_service: "${LINE_SERVICE:-}"
  whatsapp:
    enabled: ${WA_ENABLED}
    phone_number: "${WA_PHONE_NUMBER:-}"
    phone_number_id: "${WA_PHONE_NUMBER_ID:-}"
    business_account_id: "${WA_BUSINESS_ACCOUNT_ID:-}"
    verify_token: "${WA_VERIFY_TOKEN:-}"
    graph_version: "${WA_GRAPH_VERSION:-}"
    keychain_service: "${WA_SERVICE:-}"
  wechat:
    enabled: ${WECHAT_ENABLED}
    wechat_id: "${WECHAT_ID:-}"
    app_id: "${WECHAT_APP_ID:-}"
    recipient_openid: "${WECHAT_OPEN_ID:-}"
    verify_token: "${WECHAT_VERIFY_TOKEN:-}"
    keychain_service: "${WECHAT_SERVICE:-}"
  messenger:
    enabled: ${MESSENGER_ENABLED}
    page_id: "${MESSENGER_PAGE_ID:-}"
    profile: "${MESSENGER_PROFILE:-}"
    recipient_id: "${MESSENGER_RECIPIENT_ID:-}"
    verify_token: "${MESSENGER_VERIFY_TOKEN:-}"
    graph_version: "${MESSENGER_GRAPH_VERSION:-}"
    keychain_service: "${MESSENGER_SERVICE:-}"
  imessage:
    enabled: ${IMESSAGE_ENABLED}
    handle: "${IMESSAGE_HANDLE:-}"
EOF

printf "Saved messaging channel config to %s\n" "$OUT_FILE"
printf "Secrets were stored in macOS Keychain under phoenix-omega-* services.\n"
