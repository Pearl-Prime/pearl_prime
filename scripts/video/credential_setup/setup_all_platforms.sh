#!/usr/bin/env bash
#
# Master orchestration — runs all platform credential setup scripts in sequence.
#
# Usage:
#   # Full setup from manifest:
#   bash scripts/video/credential_setup/setup_all_platforms.sh --manifest credentials_manifest.yaml
#
#   # Specific platforms only:
#   bash scripts/video/credential_setup/setup_all_platforms.sh --manifest credentials_manifest.yaml --platforms youtube,tiktok
#
#   # Dry run (wire step only):
#   bash scripts/video/credential_setup/setup_all_platforms.sh --manifest credentials_manifest.yaml --dry-run
#
# Prerequisites:
#   - Python 3.9+
#   - gh CLI authenticated (gh auth status)
#   - credentials_manifest.yaml filled out (copy from .example)
#   - PyYAML installed (pip install pyyaml) for manifest mode

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
CRED_FILE="${REPO_ROOT}/.credentials.env"
PYTHON="${PYTHON:-python3}"

MANIFEST=""
PLATFORMS="youtube,tiktok,instagram,bilibili,douyin"
DRY_RUN=""
SKIP_WIRE=""

usage() {
    echo "Usage: $0 --manifest <file> [--platforms youtube,tiktok,...] [--dry-run] [--skip-wire]"
    echo ""
    echo "Options:"
    echo "  --manifest    Path to credentials_manifest.yaml (required)"
    echo "  --platforms   Comma-separated platform list (default: all)"
    echo "  --dry-run     Show what would be wired without actually setting secrets"
    echo "  --skip-wire   Run OAuth flows but don't wire to GitHub"
    exit 1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --manifest) MANIFEST="$2"; shift 2 ;;
        --platforms) PLATFORMS="$2"; shift 2 ;;
        --dry-run) DRY_RUN="--dry-run"; shift ;;
        --skip-wire) SKIP_WIRE="1"; shift ;;
        *) usage ;;
    esac
done

[[ -z "$MANIFEST" ]] && usage

if [[ ! -f "$MANIFEST" ]]; then
    echo "ERROR: Manifest not found: $MANIFEST"
    echo "Copy the example: cp ${SCRIPT_DIR}/credentials_manifest.yaml.example credentials_manifest.yaml"
    exit 1
fi

# Check prerequisites
command -v "$PYTHON" >/dev/null 2>&1 || { echo "ERROR: python3 not found"; exit 1; }
command -v gh >/dev/null 2>&1 || { echo "ERROR: gh CLI not found — install from https://cli.github.com/"; exit 1; }

echo "=============================================="
echo "  Video Platform Credential Setup"
echo "=============================================="
echo "  Manifest:  $MANIFEST"
echo "  Platforms: $PLATFORMS"
echo "  Output:    $CRED_FILE"
echo "=============================================="

# Initialize credentials file
touch "$CRED_FILE"
echo "# Video platform credentials — generated $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$CRED_FILE"
echo "# DELETE THIS FILE after wiring to GitHub Secrets" >> "$CRED_FILE"

IFS=',' read -ra PLATFORM_LIST <<< "$PLATFORMS"

for platform in "${PLATFORM_LIST[@]}"; do
    platform=$(echo "$platform" | tr -d ' ')
    case "$platform" in
        youtube)
            echo ""
            echo "── YouTube ──────────────────────────────────────"
            "$PYTHON" "${SCRIPT_DIR}/youtube_oauth.py" \
                --manifest "$MANIFEST" --output "$CRED_FILE"
            ;;
        tiktok)
            echo ""
            echo "── TikTok ───────────────────────────────────────"
            "$PYTHON" "${SCRIPT_DIR}/tiktok_oauth.py" \
                --manifest "$MANIFEST" --output "$CRED_FILE"
            ;;
        instagram)
            echo ""
            echo "── Instagram Reels ──────────────────────────────"
            "$PYTHON" "${SCRIPT_DIR}/instagram_oauth.py" \
                --manifest "$MANIFEST" --output "$CRED_FILE"
            ;;
        bilibili)
            echo ""
            echo "── Bilibili ─────────────────────────────────────"
            "$PYTHON" "${SCRIPT_DIR}/bilibili_setup.py" \
                --manifest "$MANIFEST" --output "$CRED_FILE"
            ;;
        douyin)
            echo ""
            echo "── Douyin ───────────────────────────────────────"
            "$PYTHON" "${SCRIPT_DIR}/douyin_oauth.py" \
                --manifest "$MANIFEST" --output "$CRED_FILE"
            ;;
        *)
            echo "WARNING: Unknown platform '$platform' — skipping"
            ;;
    esac
done

# Count credentials collected
CRED_COUNT=$(grep -c "=" "$CRED_FILE" 2>/dev/null || echo 0)
echo ""
echo "=============================================="
echo "  Collected $CRED_COUNT credentials"
echo "=============================================="

# Wire to GitHub Secrets
if [[ -z "$SKIP_WIRE" ]]; then
    echo ""
    echo "Wiring credentials to GitHub Secrets..."
    "$PYTHON" "${SCRIPT_DIR}/wire_secrets.py" --env-file "$CRED_FILE" $DRY_RUN

    if [[ -z "$DRY_RUN" ]]; then
        echo ""
        echo "Verifying..."
        "$PYTHON" "${SCRIPT_DIR}/wire_secrets.py" --verify

        echo ""
        echo "IMPORTANT: Delete the credentials file now:"
        echo "  rm $CRED_FILE"
    fi
else
    echo ""
    echo "Skipped wiring (--skip-wire). Credentials are in: $CRED_FILE"
    echo "Wire manually: python ${SCRIPT_DIR}/wire_secrets.py --env-file $CRED_FILE"
fi

echo ""
echo "Done."
