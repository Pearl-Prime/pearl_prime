#!/usr/bin/env bash
set -euo pipefail

# Wire remaining platform credentials into GitHub Secrets
# Usage: bash wire_remaining_secrets.sh [instagram|bilibili|all|--verify-only]

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'

info()  { echo -e "${BLUE}[INFO]${NC} $*"; }
ok()    { echo -e "${GREEN}[OK]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
err()   { echo -e "${RED}[ERR]${NC} $*"; }

set_secret() {
    local name="$1" value="$2"
    if [[ -z "$value" ]]; then
        warn "Skipped $name (empty input)"
        return
    fi
    printf '%s' "$value" | gh secret set "$name" --body - 2>/dev/null
    ok "Set $name"
}

prompt_secret() {
    local name="$1" prompt="$2"
    echo -e "${BLUE}$prompt${NC}"
    read -rsp "  Paste value for $name (hidden): " value
    echo
    set_secret "$name" "$value"
}

wire_instagram() {
    echo
    info "=== Instagram / Meta Credentials ==="
    info "Find these at: developers.facebook.com/apps/888372914250445/settings/basic/"
    echo

    prompt_secret "IG_APP_ID_SP" "Meta App ID (shared across brands):"
    read -rp "  Same App ID for CC? [Y/n]: " same_id
    if [[ "${same_id:-Y}" =~ ^[Yy] ]]; then
        set_secret "IG_APP_ID_CC" "$value"
    else
        prompt_secret "IG_APP_ID_CC" "Meta App ID for Cognitive Clarity:"
    fi

    echo
    prompt_secret "IG_APP_SECRET_SP" "Meta App Secret (shared across brands):"
    read -rp "  Same App Secret for CC? [Y/n]: " same_secret
    if [[ "${same_secret:-Y}" =~ ^[Yy] ]]; then
        set_secret "IG_APP_SECRET_CC" "$value"
    else
        prompt_secret "IG_APP_SECRET_CC" "Meta App Secret for Cognitive Clarity:"
    fi

    echo
    info "Access tokens are per-brand (different IG accounts)."
    info "Generate via: Meta Dev Portal > Use Cases > API setup > Generate token"
    prompt_secret "IG_ACCESS_TOKEN_SP" "Instagram Access Token for Stillness Press:"
    prompt_secret "IG_ACCESS_TOKEN_CC" "Instagram Access Token for Cognitive Clarity:"

    echo
    ok "Instagram secrets wired."
}

wire_bilibili() {
    echo
    info "=== Bilibili Credentials ==="
    info "Extract from browser: F12 > Application > Cookies > bilibili.com"
    info "Copy SESSDATA and bili_jct values. Cookies expire ~30 days."
    warn "Do NOT decode URL-encoded characters in SESSDATA — copy raw."
    echo

    prompt_secret "BILI_SESSDATA_SP" "SESSDATA cookie for Stillness Press Bilibili account:"
    prompt_secret "BILI_CSRF_SP" "bili_jct (CSRF) cookie for Stillness Press:"
    echo
    prompt_secret "BILI_SESSDATA_CC" "SESSDATA cookie for Cognitive Clarity Bilibili account:"
    prompt_secret "BILI_CSRF_CC" "bili_jct (CSRF) cookie for Cognitive Clarity:"

    echo
    ok "Bilibili secrets wired."
}

verify() {
    echo
    info "=== Verification ==="
    local expected=(
        IG_APP_ID_SP IG_APP_ID_CC IG_APP_SECRET_SP IG_APP_SECRET_CC
        IG_ACCESS_TOKEN_SP IG_ACCESS_TOKEN_CC
        BILI_SESSDATA_SP BILI_CSRF_SP BILI_SESSDATA_CC BILI_CSRF_CC
    )
    local existing
    existing=$(gh secret list 2>/dev/null | awk '{print $1}')

    for name in "${expected[@]}"; do
        if echo "$existing" | grep -q "^${name}$"; then
            ok "$name"
        else
            warn "$name — NOT SET"
        fi
    done

    echo
    info "All IG_ and BILI_ secrets currently in repo:"
    gh secret list 2>/dev/null | grep -iE "IG_|BILI_" || warn "None found"
}

case "${1:---verify-only}" in
    instagram) wire_instagram; verify ;;
    bilibili)  wire_bilibili; verify ;;
    all)       wire_instagram; wire_bilibili; verify ;;
    --verify-only) verify ;;
    *)
        echo "Usage: $0 [instagram|bilibili|all|--verify-only]"
        exit 1
        ;;
esac
