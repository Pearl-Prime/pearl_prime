#!/bin/bash
# Install Pearl News daily cron on local machine (Taiwan timezone).
#
# Use this when Pearl Star (192.168.1.112) is on a local network that
# GitHub Actions runners cannot reach. This cron runs locally and has
# direct access to Pearl Star for CJK article generation.
#
# Prerequisites:
#   - WordPress + Pearl Star LLM env vars exported in your shell profile
#     (or loaded via: eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)")
#   - pip install -r requirements.txt
#
# Usage:
#   bash scripts/pearl_news/install_daily_cron.sh           # install
#   bash scripts/pearl_news/install_daily_cron.sh --remove  # uninstall
#   bash scripts/pearl_news/install_daily_cron.sh --status  # show installed entries
#
# Cron schedule (Taiwan time = UTC+8):
#   Morning:  6:00 AM Taiwan  = 22:00 UTC (previous day)
#   Evening:  6:00 PM Taiwan  = 10:00 UTC

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
LOG_FILE="$REPO_ROOT/artifacts/pearl_news/cron.log"
PYTHON_BIN="${PYTHON:-python3}"
CRON_MARKER="pearl_news_daily"

MORNING_CRON="0 22 * * * cd $REPO_ROOT && PYTHONPATH=. $PYTHON_BIN scripts/pearl_news/run_daily_news_cycle.py --cycle morning >> $LOG_FILE 2>&1  # $CRON_MARKER"
EVENING_CRON="0 10 * * * cd $REPO_ROOT && PYTHONPATH=. $PYTHON_BIN scripts/pearl_news/run_daily_news_cycle.py --cycle evening >> $LOG_FILE 2>&1  # $CRON_MARKER"

show_status() {
    echo "Current Pearl News cron entries:"
    crontab -l 2>/dev/null | grep "$CRON_MARKER" || echo "  (none installed)"
}

remove_cron() {
    echo "Removing Pearl News cron entries..."
    crontab -l 2>/dev/null | grep -v "$CRON_MARKER" | crontab - || true
    echo "Done. Current crontab:"
    crontab -l 2>/dev/null || echo "  (empty)"
}

install_cron() {
    # Create log directory
    mkdir -p "$(dirname "$LOG_FILE")"

    # Verify Python + repo
    if [ ! -f "$REPO_ROOT/pearl_news/pipeline/run_article_pipeline.py" ]; then
        echo "ERROR: repo root doesn't look right: $REPO_ROOT" >&2
        exit 1
    fi

    echo "Installing Pearl News cron in: $REPO_ROOT"
    echo "Log file: $LOG_FILE"
    echo ""
    echo "Schedule (UTC, which is Taiwan UTC+8 - 8h):"
    echo "  Morning (6 AM Taiwan):  22:00 UTC"
    echo "  Evening (6 PM Taiwan):  10:00 UTC"
    echo ""

    # Remove old entries first, then add new ones
    (crontab -l 2>/dev/null | grep -v "$CRON_MARKER"; echo "$MORNING_CRON"; echo "$EVENING_CRON") | crontab -

    echo "Cron installed. Verify with: crontab -l"
    echo ""
    show_status
}

# Parse args
case "${1:-}" in
    --remove) remove_cron ;;
    --status) show_status ;;
    "")       install_cron ;;
    *)
        echo "Usage: $0 [--remove|--status]"
        exit 1
        ;;
esac
