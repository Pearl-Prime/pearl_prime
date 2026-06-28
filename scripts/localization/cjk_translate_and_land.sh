#!/usr/bin/env bash
# cjk_translate_and_land.sh — atomic translate → validate → pull → PR for CJK atoms.
#
# Prevents silent stranding: a batch is not "done" until files land on origin/main.
# Translation MUST go through the Procrastinate llm queue (RAP queue-first), not
# direct Ollama. Ref OPD-20260627-001 / OPD-20260629-003.
#
# Usage:
#   bash scripts/localization/cjk_translate_and_land.sh check
#   bash scripts/localization/cjk_translate_and_land.sh pull-stranded [--locale ja_JP|zh_TW]
#   bash scripts/localization/cjk_translate_and_land.sh land-batch --locale ja_JP --paths-file /tmp/clean.txt
#   bash scripts/localization/cjk_translate_and_land.sh translate-batch --locale ja-JP --paths-file /tmp/batch.txt
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT"
export PYTHONPATH=.

SSH_HOST="${PS_QUEUE_SSH_HOST:-pearl_star}"
PS_REPO="${PS_PHOENIX_REPO:-~/phoenix_omega}"
BATCH_SIZE="${CJK_PR_BATCH_SIZE:-180}"
ARTIFACT_DIR="${REPO_ROOT}/artifacts/localization/cjk_land"
mkdir -p "$ARTIFACT_DIR"

log() { echo "[cjk-land $(date -u +%FT%TZ)] $*"; }

require_pscli() {
  if ! command -v pscli >/dev/null 2>&1; then
    log "WARN: pscli not on PATH — queue dispatch may fail (source /etc/pearl-star/queue.env on PS)"
  fi
}

cmd_check() {
  python3 scripts/localization/cjk_unpulled_check.py --strict || {
    log "Stranded inventory detected — run pull-stranded or translate-batch+land"
    return 1
  }
}

build_stranded_lists() {
  local locale="${1:-}"
  local ts
  ts="$(date -u +%Y%m%dT%H%M%SZ)"
  local out_dir="${ARTIFACT_DIR}/${ts}"
  mkdir -p "$out_dir"

  # Exclude held-back backlog paths on Pearl Star
  ssh "$SSH_HOST" "cat /tmp/backlog_ja.txt /tmp/backlog_zhtw.txt 2>/dev/null" \
    > "${out_dir}/exclude_backlog.txt" || true

  if [[ -n "$locale" ]]; then
    python3 scripts/localization/cjk_unpulled_check.py \
      --locale "$locale" \
      --exclude-file "${out_dir}/exclude_backlog.txt" \
      --write-stranded "${out_dir}/stranded_${locale}.txt" \
      --json > "${out_dir}/report_${locale}.json"
    echo "${out_dir}/stranded_${locale}.txt"
  else
    for loc in ja_JP zh_TW; do
      python3 scripts/localization/cjk_unpulled_check.py \
        --locale "$loc" \
        --exclude-file "${out_dir}/exclude_backlog.txt" \
        --write-stranded "${out_dir}/stranded_${loc}.txt" \
        --json > "${out_dir}/report_${loc}.json" || true
    done
    echo "$out_dir"
  fi
}

cmd_pull_stranded() {
  local locale="${2:-ja_JP}"
  require_pscli
  local stranded_file
  stranded_file="$(build_stranded_lists "$locale")"
  if [[ ! -s "$stranded_file" ]]; then
    log "No stranded ${locale} atoms to pull."
    return 0
  fi
  local n
  n="$(wc -l < "$stranded_file" | tr -d ' ')"
  log "Pulling up to ${BATCH_SIZE} of ${n} stranded ${locale} atoms..."
  python3 scripts/localization/cjk_pull_from_pearl_star.py \
    --locale "$locale" \
    --paths-file "$stranded_file" \
    --batch-size "$BATCH_SIZE" \
    --manifest-out "${ARTIFACT_DIR}/pulled_${locale}_$(date -u +%Y%m%dT%H%M%SZ).txt"
  cmd_check || true
}

cmd_land_batch() {
  local locale_key=""
  local paths_file=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --locale) locale_key="$2"; shift 2 ;;
      --paths-file) paths_file="$2"; shift 2 ;;
      *) log "unknown arg: $1"; return 2 ;;
    esac
  done
  [[ -n "$locale_key" && -n "$paths_file" ]] || { log "usage: land-batch --locale ja_JP --paths-file FILE"; return 2; }

  python3 scripts/localization/cjk_pull_from_pearl_star.py \
    --locale "$locale_key" \
    --paths-file "$paths_file" \
    --batch-size "$BATCH_SIZE"

  local branch="agent/cjk-land-${locale_key}-$(date -u +%Y%m%d)"
  git fetch origin
  git checkout -B "$branch" origin/main
  git add atoms/
  if git diff --cached --quiet; then
    log "Nothing to commit after pull."
    return 0
  fi
  local count
  count="$(git diff --cached --name-only | wc -l | tr -d ' ')"
  git commit -m "$(cat <<EOF
feat(atoms): land ${locale_key} batch from Pearl Star (atomic cjk_translate_and_land)

Validated + batched-tar pull; ${count} locale atoms. Ref OPD-20260627-001.
EOF
)"
  log "Committed on ${branch} (${count} files). Push + PR manually or via Pearl_GitHub."
  cmd_check || true
}

cmd_translate_batch() {
  local locale=""
  local paths_file=""
  local wait_flag="--wait"
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --locale) locale="$2"; shift 2 ;;
      --paths-file) paths_file="$2"; shift 2 ;;
      --no-wait) wait_flag=""; shift ;;
      *) log "unknown arg: $1"; return 2 ;;
    esac
  done
  [[ -n "$locale" && -n "$paths_file" ]] || {
    log "usage: translate-batch --locale ja-JP --paths-file FILE (paths file on Pearl Star)"
    return 2
  }
  require_pscli
  ssh "$SSH_HOST" "pscli gpu-acquire cjk --note 'cjk_translate_and_land'" || true

  # Copy paths file to Pearl Star if local
  local ps_paths="$paths_file"
  if [[ -f "$paths_file" ]]; then
    ps_paths="/tmp/cjk_batch_$(basename "$paths_file")"
    scp -q "$paths_file" "${SSH_HOST}:${ps_paths}"
  fi

  PYTHONPATH=. python3 scripts/localization/cjk_enqueue_translate.py \
    --locale "$locale" \
    --paths-file "$ps_paths" \
    --gpu-acquire \
    $wait_flag

  log "Post-translate: validate on PS, then land-batch with clean manifest"
  cmd_check || true
}

cmd_full_stranded() {
  local locale="${2:-ja_JP}"
  cmd_pull_stranded pull-stranded "$locale"
  local manifest
  manifest="$(ls -t "${ARTIFACT_DIR}"/pulled_${locale}_*.txt 2>/dev/null | head -1)"
  [[ -n "$manifest" ]] || { log "No manifest from pull"; return 1; }
  cmd_land_batch land-batch --locale "$locale" --paths-file "$manifest"
}

main() {
  local cmd="${1:-check}"
  shift || true
  case "$cmd" in
    check) cmd_check ;;
    pull-stranded) cmd_pull_stranded "$@" ;;
    land-batch) cmd_land_batch "$@" ;;
    translate-batch) cmd_translate_batch "$@" ;;
    full-stranded) cmd_full_stranded "$@" ;;
    *)
      echo "Usage: $0 {check|pull-stranded|land-batch|translate-batch|full-stranded} [args...]"
      exit 2
      ;;
  esac
}

main "$@"
