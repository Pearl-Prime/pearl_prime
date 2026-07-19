#!/bin/bash
# Batched CosyVoice retry with health checks between batches.
set -euo pipefail
REMOTE=/home/ahjan108/smv_voice_bank_20260719b
source "$REMOTE/creds/r2.env"
LOG="$REMOTE/out/retry.log"
BATCH=40
ATOMS="$REMOTE/atoms/retry_fails.jsonl"
TOTAL=$(wc -l < "$ATOMS")
echo "RETRY_START total=$TOTAL batch=$BATCH $(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a "$LOG"

ensure_cosy() {
  local i code
  if curl -sS -m 3 http://127.0.0.1:9880/api/v1/health >/dev/null 2>&1; then
    return 0
  fi
  echo "COSY_DOWN restarting $(date -u +%H:%M:%SZ)" | tee -a "$LOG"
  sudo systemctl start cosyvoice || true
  for i in $(seq 1 24); do
    code=$(curl -sS -m 3 -o /dev/null -w "%{http_code}" http://127.0.0.1:9880/api/v1/health 2>/dev/null || echo 000)
    if [ "$code" = "200" ]; then
      echo "COSY_UP try=$i $(date -u +%H:%M:%SZ)" | tee -a "$LOG"
      return 0
    fi
    sleep 5
  done
  echo "COSY_FAIL_TO_START" | tee -a "$LOG"
  return 1
}

offset=0
while [ "$offset" -lt "$TOTAL" ]; do
  ensure_cosy || exit 2
  echo "BATCH offset=$offset limit=$BATCH $(date -u +%H:%M:%SZ)" | tee -a "$LOG"
  set +e
  python3 -u "$REMOTE/scripts/generate_voice_bank_onbox.py" \
    --atoms "$ATOMS" \
    --matrix "$REMOTE/config/social_media_voice_matrix.yaml" \
    --text-prep "$REMOTE/config/social_media_tts_text_prep.yaml" \
    --out "$REMOTE/out" \
    --manifest "$REMOTE/out/MANIFEST.tsv" \
    --r2-prefix social_media/voice_bank/20260719b/ \
    --offset "$offset" \
    --limit "$BATCH" \
    >>"$LOG" 2>&1
  rc=$?
  set -e
  if tail -n 100 "$LOG" | grep -q "Connection refused"; then
    echo "DETECTED_CONN_REFUSED after offset=$offset — restart cosy and redo batch" | tee -a "$LOG"
    sudo systemctl restart cosyvoice || sudo systemctl start cosyvoice
    sleep 15
    ensure_cosy || exit 2
    continue
  fi
  if [ "$rc" -ne 0 ]; then
    echo "BATCH_RC=$rc offset=$offset — health check then advance" | tee -a "$LOG"
    ensure_cosy || true
  fi
  offset=$((offset + BATCH))
  python3 - <<'PY'
from pathlib import Path
lines = Path("/home/ahjan108/smv_voice_bank_20260719b/out/MANIFEST.tsv").read_text().splitlines()
cols = lines[0].split("\t")
ok = fail = 0
for line in lines[1:]:
    row = dict(zip(cols, line.split("\t")))
    st = row.get("status", "")
    if st == "ok":
        ok += 1
    elif st.startswith("fail"):
        fail += 1
print(f"PROGRESS ok={ok} fail={fail} target=1620")
PY
done
echo "RETRY_DONE $(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a "$LOG"
