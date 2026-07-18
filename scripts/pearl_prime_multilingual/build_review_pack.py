#!/usr/bin/env python3
"""
Pearl_Publisher — Qualitative Review Sample Pack Builder.

Pulls a stratified sample of rendered books across locales for the FIRST_10
listening evaluation (Emotional Pull / Clarity / Memorability / Practicality /
Identity Shift).

Stratification per locale:
  - Only books that have book.txt AND passed quality gates
  - Max 1 book per (brand × teacher × topic) combo
  - Prefer book_word_count within [9000, 12000] (production range)
  - Diverse persona coverage within locale

Inputs (scanned automatically):
  artifacts/pearl_prime_<locale_slug>/full_catalog_qa/assembly_summary.json
  artifacts/pearl_prime_<locale_slug>/full_catalog_qa_production/assembly_summary.json

Output:
  artifacts/pearl_prime_review_pack/
    README.md                  — index with links + stratification rationale
    {locale}/{book_id}.txt     — copied book.txt
    {locale}/{book_id}.meta.json — topic/persona/teacher/brand/wc/quality_summary

Usage:
  python3 scripts/pearl_prime_multilingual/build_review_pack.py
  python3 scripts/pearl_prime_multilingual/build_review_pack.py --per-locale 3
"""
from __future__ import annotations

import argparse
import json
import random
import shutil
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
OUT_ROOT = REPO_ROOT / "artifacts" / "pearl_prime_review_pack"


def find_runs() -> list[tuple[str, Path]]:
    """Return list of (label, assembly_summary_path)."""
    runs = []
    for artifact_dir in (REPO_ROOT / "artifacts").glob("pearl_prime_*"):
        if artifact_dir.name == "pearl_prime_review_pack":
            continue
        for qa_dir in artifact_dir.iterdir():
            if qa_dir.is_dir() and qa_dir.name.startswith("full_catalog_qa"):
                sum_path = qa_dir / "assembly_summary.json"
                if sum_path.exists():
                    # label: include the QA variant if it's not just 'full_catalog_qa'
                    suffix = qa_dir.name.replace("full_catalog_qa", "").lstrip("_") or "draft"
                    label = f"{artifact_dir.name.replace('pearl_prime_', '')}_{suffix}"
                    runs.append((label, sum_path))
    return sorted(runs)


def stratified_pick(books: list[dict], n: int, seed: int = 42) -> list[dict]:
    """Pick n books diversifying across brand × teacher × topic × persona."""
    rng = random.Random(seed)
    # Only eligible: has book.txt + passed gates + wc in target range
    eligible = [
        b for b in books
        if b.get("has_book_txt") and b.get("quality_gates_pass")
        and 7000 <= (b.get("book_word_count") or 0) <= 12500
    ]
    if not eligible:
        # Fallback: any rendered book
        eligible = [b for b in books if b.get("has_book_txt")]
    if len(eligible) <= n:
        return eligible

    # Group by (brand, teacher) and pick one per group, up to n
    buckets: dict[tuple[str | None, str | None], list[dict]] = defaultdict(list)
    for b in eligible:
        buckets[(b.get("brand"), b.get("teacher"))].append(b)

    # Randomize bucket order, pick one from each until we have n
    bucket_keys = list(buckets.keys())
    rng.shuffle(bucket_keys)

    picks: list[dict] = []
    seen_topics: set[str] = set()
    seen_personas: set[str] = set()

    # First pass: prefer books with new topic+persona combos
    for k in bucket_keys:
        if len(picks) >= n:
            break
        for b in sorted(buckets[k], key=lambda x: (x["topic"] in seen_topics, x["persona"] in seen_personas)):
            if b["topic"] not in seen_topics or b["persona"] not in seen_personas:
                picks.append(b)
                seen_topics.add(b["topic"])
                seen_personas.add(b["persona"])
                break

    # Second pass: fill remaining slots from any remaining bucket
    remaining_pool = [b for k in bucket_keys for b in buckets[k] if b not in picks]
    rng.shuffle(remaining_pool)
    for b in remaining_pool:
        if len(picks) >= n:
            break
        picks.append(b)

    return picks[:n]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-locale", type=int, default=2, help="Books per locale (default 2)")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out-root", default=str(OUT_ROOT))
    args = ap.parse_args()

    out_root = Path(args.out_root)
    if out_root.exists():
        shutil.rmtree(out_root)
    out_root.mkdir(parents=True)

    runs = find_runs()
    if not runs:
        raise SystemExit("No assembly_summary.json files found under artifacts/pearl_prime_*")

    readme_lines: list[str] = []
    readme_lines.append("# Pearl Prime Review Pack")
    readme_lines.append("")
    readme_lines.append(f"**Generated:** {datetime.now(timezone.utc).isoformat()}")
    readme_lines.append(f"**Books per run:** {args.per_locale}")
    readme_lines.append("")
    readme_lines.append("## Evaluation axes (per FIRST_10_BOOKS_EVALUATION_PROTOCOL.md)")
    readme_lines.append("")
    readme_lines.append("Score each book 1–5 on:")
    readme_lines.append("")
    readme_lines.append("| Axis | What it measures |")
    readme_lines.append("|---|---|")
    readme_lines.append("| Emotional Pull | Did I feel something? |")
    readme_lines.append("| Clarity | Was it easy to follow? |")
    readme_lines.append("| Memorability | Any standout lines? |")
    readme_lines.append("| Practicality | Would someone apply it? |")
    readme_lines.append("| Identity Shift | Does it reframe the listener's self-image? |")
    readme_lines.append("")
    readme_lines.append("---")
    readme_lines.append("")
    readme_lines.append("## Books")
    readme_lines.append("")

    total_picked = 0
    for label, sum_path in runs:
        summary = json.loads(sum_path.read_text())
        books = summary.get("books") or []
        picks = stratified_pick(books, n=args.per_locale, seed=args.seed)
        if not picks:
            readme_lines.append(f"### {label}")
            readme_lines.append(f"*No eligible books.*")
            readme_lines.append("")
            continue

        readme_lines.append(f"### {label}  (run: {sum_path.parent.relative_to(REPO_ROOT)})")
        readme_lines.append("")
        readme_lines.append("| # | Topic × Persona | Teacher | Brand | Words | Book |")
        readme_lines.append("|---|---|---|---|---|---|")

        run_dir = out_root / label
        run_dir.mkdir(parents=True, exist_ok=True)

        for i, b in enumerate(picks, start=1):
            render_dir = sum_path.parent / "renders" / b["render_name"]
            book_txt = render_dir / "book.txt"
            if not book_txt.exists():
                continue
            dst_txt = run_dir / f"{b['render_name']}.txt"
            shutil.copy2(book_txt, dst_txt)
            meta = {
                "locale": b.get("locale"),
                "topic": b["topic"],
                "persona": b["persona"],
                "teacher": b["teacher"],
                "brand": b["brand"],
                "book_word_count": b["book_word_count"],
                "quality_gates_pass": b["quality_gates_pass"],
                "source_render": str(render_dir.relative_to(REPO_ROOT)),
            }
            (run_dir / f"{b['render_name']}.meta.json").write_text(json.dumps(meta, indent=2))

            readme_lines.append(
                f"| {i} | {b['topic']} × {b['persona']} | {b['teacher']} | "
                f"{b['brand']} | {b['book_word_count']} | [book]({label}/{b['render_name']}.txt) |"
            )
            total_picked += 1
        readme_lines.append("")

    readme_lines.append("---")
    readme_lines.append("")
    readme_lines.append(f"**Total books in pack:** {total_picked}")
    readme_lines.append("")
    readme_lines.append("## How to evaluate")
    readme_lines.append("")
    readme_lines.append("1. Read (or use text-to-speech on) 20 minutes of each book — beginning, midpoint, final chapter.")
    readme_lines.append("2. Score each book on the 5 axes. Use 1–5 scale.")
    readme_lines.append("3. Aggregate: if ≥7/10 score below 3 on Emotional Pull → arc/story layer is weak (fix upstream, not governance).")
    readme_lines.append("4. See [docs/FIRST_10_BOOKS_EVALUATION_PROTOCOL.md](../../docs/FIRST_10_BOOKS_EVALUATION_PROTOCOL.md) for the full protocol.")
    readme_lines.append("")

    (out_root / "README.md").write_text("\n".join(readme_lines))

    print(f"Review pack built: {out_root}")
    print(f"  Runs scanned:    {len(runs)}")
    print(f"  Books included:  {total_picked}")
    print(f"  See {out_root / 'README.md'}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
