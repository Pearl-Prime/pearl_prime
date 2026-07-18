#!/usr/bin/env bash
# Independent F1 proof: true-pre-fix (origin/main) vs fixed (working tree),
# 3 full-12 tiers, gen_z_professionals x anxiety x ahjan, seed leverB_baseline.
# Deterministic, no paid API. Runs sequentially to stay friendly to concurrent
# renders sharing the box.
set -uo pipefail
cd /Users/ahjan/phoenix_omega
OUT=artifacts/qa/f1_depth_dedup_verify_20260615
echo "START $(date)"
for fmt in standard_book extended_book_2h deep_book_6h; do
  for arm in prefix fixed; do
    echo ">>> RENDER arm=$arm fmt=$fmt $(date +%H:%M:%S)"
    if PYTHONPATH=. python3 "$OUT/render_one.py" --arm "$arm" --format "$fmt" --out "$OUT"; then
      echo "<<< DONE arm=$arm fmt=$fmt"
    else
      echo "!!! FAIL arm=$arm fmt=$fmt rc=$?"
    fi
  done
done
echo "=== AGGREGATE ==="
PYTHONPATH=. python3 "$OUT/aggregate.py" || echo "aggregate failed"
echo "END $(date)"
