#!/usr/bin/env python3
"""Lane C — batch tuple-viability sweep over all 657 distinct catalog cells.

Read-only. Imports check_tuple_viability() directly (the exact function
phoenix_v4/gates/check_tuple_viability.py's CLI calls) — no subprocess, no
render, no write. This answers Lane A's explicit NEXT_ACTION: "run a real
batch tuple-viability sweep... to size the plan-to-spine-buildable gap
precisely, with particular attention to whether NO_BINDING clusters around
specific topics."

format_id is fixed to F006 (structural_format_id) since 32,391 of 32,401
en_US book plans (99.97%, per Lane A REPORT.md §2) use F006 — the near-total
catalog shape.
"""
import sys
import csv
import json
from pathlib import Path
from collections import Counter, defaultdict

REPO = Path("/private/tmp/claude-501/-Users-ahjan-phoenix-omega/eda0f494-ed89-4f19-95ff-cb16877fe8ea/scratchpad/wt-lane-c")
sys.path.insert(0, str(REPO))

from phoenix_v4.gates.check_tuple_viability import check_tuple_viability  # noqa: E402

# Load the cell table built by build_cell_table.py (persona, topic, engine, planned_book_count)
cells = []
with open(REPO.parent / "lane_c_work" / "full_cell_table.csv") as f:
    r = csv.DictReader(f)
    for row in r:
        cells.append(row)

results = []
error_code_counter = Counter()
status_counter = Counter()
books_by_status = Counter()
error_code_books = Counter()

for row in cells:
    persona, topic, engine = row["persona"], row["topic"], row["engine"]
    count = int(row["planned_book_count"])
    res = check_tuple_viability(persona, topic, engine, "F006", repo_root=REPO)
    status_counter[res.status] += 1
    books_by_status[res.status] += count
    # bucket first error code (e.g. NO_BINDING, NO_ARC, NO_STORY_POOL, POOL_TOO_SHALLOW, BAND_DEFICIT)
    codes = set()
    for e in res.errors:
        code = e.split(":")[0].strip()
        codes.add(code)
        error_code_counter[code] += 1
        error_code_books[code] += count
    results.append({
        **row,
        "tuple_viability_status": res.status,
        "tuple_viability_errors": ";".join(res.errors),
        "tuple_viability_error_codes": ";".join(sorted(codes)),
    })

out_csv = REPO.parent / "lane_c_work" / "full_cell_table_with_tuple_viability.csv"
with open(out_csv, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
    w.writeheader()
    w.writerows(results)

print(f"Cells checked: {len(cells)}")
print(f"Status (by cell count): {dict(status_counter)}")
print(f"Status (weighted by planned book count): {dict(books_by_status)}")
print(f"\nError codes (by cell count, a cell can have multiple codes): {dict(error_code_counter)}")
print(f"Error codes (weighted by planned book count): {dict(error_code_books)}")

total_books = sum(int(row["planned_book_count"]) for row in cells)
print(f"\nTotal planned books covered: {total_books}")
print(f"PASS: {books_by_status['PASS']} books ({100*books_by_status['PASS']/total_books:.1f}%)")
print(f"FAIL: {books_by_status['FAIL']} books ({100*books_by_status['FAIL']/total_books:.1f}%)")

summary = {
    "cells_checked": len(cells),
    "status_by_cell_count": dict(status_counter),
    "status_by_book_count": dict(books_by_status),
    "error_codes_by_cell_count": dict(error_code_counter),
    "error_codes_by_book_count": dict(error_code_books),
    "total_books": total_books,
    "pass_pct_books": round(100*books_by_status['PASS']/total_books, 2),
    "fail_pct_books": round(100*books_by_status['FAIL']/total_books, 2),
}
with open(REPO.parent / "lane_c_work" / "tuple_viability_summary.json", "w") as f:
    json.dump(summary, f, indent=2)
print("\nWrote tuple_viability_summary.json")

# Cross-tab: bind_status (BOUND/UNBOUND-thin/UNKNOWN) x tuple_viability status, weighted by books
cross = defaultdict(lambda: Counter())
for row in results:
    key = row["predicted_bind_status"]
    cross[key][row["tuple_viability_status"]] += int(row["planned_book_count"])
print("\n=== CROSS-TAB: predicted_bind_status x tuple_viability_status (book-weighted) ===")
for k, c in cross.items():
    print(k, dict(c))
