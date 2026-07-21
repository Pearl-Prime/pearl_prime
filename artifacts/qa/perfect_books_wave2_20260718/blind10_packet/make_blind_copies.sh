#!/usr/bin/env bash
# Makes de-identified local reading copies of the 10 blind-10 packet EPUBs.
# Writes to a scratch /tmp path only — nothing here is committed to git.
# Run from the repo root: bash artifacts/qa/perfect_books_wave2_20260718/blind10_packet/make_blind_copies.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
OUT_DIR="${1:-/tmp/blind10_reading_copies_20260718}"
mkdir -p "$OUT_DIR"

SRC_DIR="$REPO_ROOT/artifacts/epubs/way_stream_sanctuary"

declare -a MAP=(
  "Book_01:way_stream_sanctuary__corporate_managers__burnout__overwhelm.epub"
  "Book_02:way_stream_sanctuary__corporate_managers__anxiety__false_alarm.epub"
  "Book_03:way_stream_sanctuary__corporate_managers__boundaries__comparison.epub"
  "Book_04:way_stream_sanctuary__corporate_managers__boundaries__shame.epub"
  "Book_05:way_stream_sanctuary__entrepreneurs__anxiety__overwhelm.epub"
  "Book_06:way_stream_sanctuary__first_responders__burnout__grief.epub"
  "Book_07:way_stream_sanctuary__gen_x_sandwich__compassion_fatigue__watcher.epub"
  "Book_08:way_stream_sanctuary__healthcare_rns__compassion_fatigue__watcher.epub"
  "Book_09:way_stream_sanctuary__millennial_women_professionals__burnout__overwhelm.epub"
  "Book_10:way_stream_sanctuary__tech_finance_burnout__courage__false_alarm.epub"
)

for entry in "${MAP[@]}"; do
  blind_id="${entry%%:*}"
  real_file="${entry##*:}"
  cp "$SRC_DIR/$real_file" "$OUT_DIR/${blind_id}.epub"
  echo "wrote $OUT_DIR/${blind_id}.epub"
done

echo ""
echo "Done. Read from: $OUT_DIR"
echo "Do NOT open MANIFEST.tsv or KEY_SEALED.md until scoring is complete."
