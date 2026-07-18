#!/usr/bin/env python3
"""
Bestseller quality analyzer for the 1,000-book simulation.

Reads simulation_1000_results.jsonl produced by run_1000_book_simulation.py,
loads each successful book's rendered output + plan, runs the full editorial
quality stack (bestseller editor report, ONTGP craft gate, scene anti-genericity,
chapter flow), and produces a comprehensive quality report.

Outputs:
    artifacts/simulation/bestseller_quality_report.json   (machine-readable)
    artifacts/simulation/bestseller_quality_report.md     (human-readable)

Usage:
    python3 scripts/ci/analyze_bestseller_quality.py
    python3 scripts/ci/analyze_bestseller_quality.py --results path/to/results.jsonl
    python3 scripts/ci/analyze_bestseller_quality.py --limit 50
    python3 scripts/ci/analyze_bestseller_quality.py --max-parallel 8
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Ensure repo root is on PYTHONPATH
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

DEFAULT_RESULTS_PATH = ROOT / "artifacts" / "simulation" / "simulation_1000_results.jsonl"
DEFAULT_OUTPUT_DIR = ROOT / "artifacts" / "simulation"


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@dataclass
class BookQuality:
    """Quality assessment for one book."""
    index: int
    persona: str
    topic: str
    engine: str
    format_id: str
    location: str
    quality_profile: str
    render_dir: str
    word_count: int = 0

    # Editorial report fields
    editorial_status: str = "SKIP"
    flow_status: str = "SKIP"
    word_status: str = "SKIP"
    book_pass_status: str = "SKIP"
    thesis_drift_status: str = "SKIP"
    craft_gate_status: str = "SKIP"
    craft_fail_chapters: int = 0
    craft_warn_chapters: int = 0
    chapter_count: int = 0
    grand_total_words: int = 0

    # ONTGP move scores (averages across chapters)
    orient_score: float = 0.0
    name_score: float = 0.0
    turn_score: float = 0.0
    give_score: float = 0.0
    pull_score: float = 0.0

    # Scene anti-genericity
    scene_status: str = "SKIP"
    scene_collisions: int = 0
    scene_detail_failures: int = 0
    scene_static_chapters: int = 0

    # Errors during analysis
    analysis_error: str = ""

    # Overall verdict
    verdict: str = "SKIP"  # PASS / NEEDS_REVISION / FAIL


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_jsonl(path: Path) -> List[Dict[str, Any]]:
    """Load all JSON lines from a file."""
    records: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def _collect_chapter_texts(render_dir: Path) -> List[str]:
    """
    Collect chapter texts from a render directory.

    Looks for chapter_*.txt files or the concatenated rendered_book.txt,
    splitting on chapter headers.
    """
    chapters: List[str] = []

    # Strategy 1: individual chapter files
    ch_files = sorted(render_dir.glob("chapter_*.txt"))
    if ch_files:
        for cf in ch_files:
            try:
                chapters.append(cf.read_text(encoding="utf-8", errors="replace"))
            except Exception:
                pass
        if chapters:
            return chapters

    # Strategy 2: rendered_book.txt split on chapter headers
    book_txt = render_dir / "rendered_book.txt"
    if book_txt.exists():
        try:
            full_text = book_txt.read_text(encoding="utf-8", errors="replace")
            # Split on "Chapter N" or "CHAPTER N" headers
            parts = re.split(r"\n(?=(?:Chapter|CHAPTER)\s+\d+)", full_text)
            chapters = [p.strip() for p in parts if p.strip()]
            if chapters:
                return chapters
        except Exception:
            pass

    # Strategy 3: any .txt files in the directory
    txt_files = sorted(render_dir.glob("*.txt"))
    for tf in txt_files:
        if tf.name.startswith("bestseller_editor") or tf.name == "budget.txt":
            continue
        try:
            text = tf.read_text(encoding="utf-8", errors="replace")
            if len(text.split()) > 100:
                chapters.append(text)
        except Exception:
            pass

    return chapters


def _count_words(text: str) -> int:
    return len(text.split())


def _extract_ngrams(text: str, n: int = 3) -> List[str]:
    """Extract word n-grams from text."""
    words = re.findall(r"[a-z]+", text.lower())
    return [" ".join(words[i:i + n]) for i in range(len(words) - n + 1)]


# ---------------------------------------------------------------------------
# Single-book quality analysis
# ---------------------------------------------------------------------------

def analyze_single_book(record: Dict[str, Any]) -> BookQuality:
    """Run quality analysis on one successfully rendered book."""
    render_dir = Path(record.get("render_dir", ""))
    quality = BookQuality(
        index=record.get("index", -1),
        persona=record.get("persona", ""),
        topic=record.get("topic", ""),
        engine=record.get("engine", ""),
        format_id=record.get("format_id", ""),
        location=record.get("location", ""),
        quality_profile=record.get("quality_profile", ""),
        render_dir=str(render_dir),
        word_count=record.get("word_count", 0),
    )

    if not render_dir.is_dir():
        quality.analysis_error = f"render_dir not found: {render_dir}"
        quality.verdict = "FAIL"
        return quality

    # Load plan.json
    plan_path = render_dir / "plan.json"
    plan: Dict[str, Any] = {}
    if plan_path.exists():
        try:
            with open(plan_path, "r", encoding="utf-8") as f:
                plan = json.load(f) or {}
        except Exception as exc:
            quality.analysis_error = f"plan.json load error: {exc}"

    # Collect chapter texts
    chapters = _collect_chapter_texts(render_dir)
    if not chapters:
        quality.analysis_error = "No chapter texts found in render_dir"
        quality.verdict = "FAIL"
        return quality

    quality.chapter_count = len(chapters)
    quality.grand_total_words = sum(_count_words(ch) for ch in chapters)

    # ---------------------------------------------------------------
    # 1. Bestseller editor report
    # ---------------------------------------------------------------
    try:
        from phoenix_v4.qa.bestseller_editor import build_bestseller_editor_report

        editorial = build_bestseller_editor_report(plan, render_dir)
        quality.editorial_status = editorial.get("status", "SKIP")
        quality.flow_status = editorial.get("flow_status", "SKIP")
        quality.word_status = editorial.get("word_status", "SKIP")
        quality.book_pass_status = editorial.get("book_pass_status", "SKIP")
        quality.thesis_drift_status = editorial.get("thesis_drift_status", "SKIP")
        quality.craft_gate_status = editorial.get("craft_gate_status", "SKIP")
        quality.chapter_count = editorial.get("chapter_count", quality.chapter_count)
        quality.grand_total_words = editorial.get("grand_total_words", quality.grand_total_words)

        craft_gate = editorial.get("craft_gate", {})
        quality.craft_fail_chapters = craft_gate.get("fail_count", 0)
        quality.craft_warn_chapters = craft_gate.get("warn_count", 0)

        # Extract average ONTGP move scores across chapters
        move_totals: Dict[str, float] = defaultdict(float)
        move_counts: Dict[str, int] = defaultdict(int)
        for ch_data in craft_gate.get("chapters", []):
            scores = ch_data.get("move_scores", {})
            for move in ("orient", "name", "turn", "give", "pull"):
                if move in scores:
                    move_totals[move] += scores[move]
                    move_counts[move] += 1
        for move in ("orient", "name", "turn", "give", "pull"):
            if move_counts[move] > 0:
                setattr(quality, f"{move}_score",
                        round(move_totals[move] / move_counts[move], 3))
    except Exception as exc:
        quality.analysis_error += f" | editorial_error: {exc}"

    # ---------------------------------------------------------------
    # 2. ONTGP craft gate (standalone per-chapter if editorial missed it)
    # ---------------------------------------------------------------
    if quality.craft_gate_status == "SKIP":
        try:
            from phoenix_v4.quality.bestseller_craft_gate import evaluate_bestseller_craft

            statuses = []
            for ch_text in chapters:
                if _count_words(ch_text) < 200:
                    continue
                result = evaluate_bestseller_craft(ch_text)
                statuses.append(result.status)
            if statuses:
                if "FAIL" in statuses:
                    quality.craft_gate_status = "FAIL"
                elif "WARN" in statuses:
                    quality.craft_gate_status = "WARN"
                else:
                    quality.craft_gate_status = "PASS"
        except Exception as exc:
            quality.analysis_error += f" | craft_standalone_error: {exc}"

    # ---------------------------------------------------------------
    # 3. Scene anti-genericity gate
    # ---------------------------------------------------------------
    try:
        from phoenix_v4.qa.scene_anti_genericity_gate import check_scene_genericity

        scene_report = check_scene_genericity(chapters)
        quality.scene_status = scene_report.status
        quality.scene_collisions = sum(
            1 for e in scene_report.errors if "SCENE_COLLISION" in e
        )
        quality.scene_detail_failures = sum(
            1 for d in scene_report.chapter_diagnostics
            if any("THREE_DETAIL_RULE" in e for e in d.errors)
        )
        quality.scene_static_chapters = sum(
            1 for d in scene_report.chapter_diagnostics
            if any("STATIC_SCENE" in e for e in d.errors)
        )
    except Exception as exc:
        quality.analysis_error += f" | scene_gate_error: {exc}"

    # ---------------------------------------------------------------
    # 4. Chapter flow gate (per-chapter)
    # ---------------------------------------------------------------
    if quality.flow_status == "SKIP":
        try:
            from phoenix_v4.quality.chapter_flow_gate import evaluate_chapter_flow

            flow_statuses = []
            for ch_text in chapters:
                result = evaluate_chapter_flow(ch_text)
                flow_statuses.append(result.status)
            if flow_statuses:
                if "FAIL" in flow_statuses:
                    quality.flow_status = "FAIL"
                elif "WARN" in flow_statuses:
                    quality.flow_status = "WARN"
                else:
                    quality.flow_status = "PASS"
        except Exception as exc:
            quality.analysis_error += f" | flow_gate_error: {exc}"

    # ---------------------------------------------------------------
    # 5. Overall verdict
    # ---------------------------------------------------------------
    statuses = [
        quality.editorial_status,
        quality.flow_status,
        quality.craft_gate_status,
        quality.scene_status,
    ]
    if "FAIL" in statuses:
        quality.verdict = "FAIL"
    elif "WARN" in statuses:
        quality.verdict = "NEEDS_REVISION"
    else:
        quality.verdict = "PASS"

    return quality


# ---------------------------------------------------------------------------
# Aggregation and report generation
# ---------------------------------------------------------------------------

def _breakdown_by_field(
    results: List[BookQuality],
    field_name: str,
) -> Dict[str, Dict[str, int]]:
    """Group verdict counts by a given field (persona, topic, format_id, etc.)."""
    groups: Dict[str, Counter] = defaultdict(Counter)
    for r in results:
        key = getattr(r, field_name, "unknown")
        groups[key][r.verdict] += 1
    return {k: dict(v) for k, v in sorted(groups.items())}


def _top_n(
    results: List[BookQuality],
    n: int,
    best: bool = True,
) -> List[Dict[str, Any]]:
    """
    Return top N books by a composite quality score.
    Score: PASS=3, NEEDS_REVISION=1, FAIL=0, plus average ONTGP scores.
    """
    def score(r: BookQuality) -> float:
        base = {"PASS": 3, "NEEDS_REVISION": 1, "FAIL": 0}.get(r.verdict, 0)
        ontgp_avg = (r.orient_score + r.name_score + r.turn_score
                     + r.give_score + r.pull_score) / 5.0
        return base + ontgp_avg

    scored = sorted(results, key=score, reverse=best)
    entries = []
    for r in scored[:n]:
        entries.append({
            "index": r.index,
            "persona": r.persona,
            "topic": r.topic,
            "engine": r.engine,
            "format_id": r.format_id,
            "location": r.location,
            "verdict": r.verdict,
            "word_count": r.grand_total_words,
            "ontgp_scores": {
                "orient": r.orient_score,
                "name": r.name_score,
                "turn": r.turn_score,
                "give": r.give_score,
                "pull": r.pull_score,
            },
            "editorial_status": r.editorial_status,
            "scene_status": r.scene_status,
            "craft_gate_status": r.craft_gate_status,
            "flow_status": r.flow_status,
            "error": r.analysis_error or None,
        })
    return entries


def _failure_pattern_analysis(results: List[BookQuality]) -> Dict[str, int]:
    """Group and count common failure patterns across books."""
    patterns: Counter = Counter()
    for r in results:
        if r.verdict == "FAIL" or r.verdict == "NEEDS_REVISION":
            if r.editorial_status == "FAIL":
                patterns["editorial_report_FAIL"] += 1
            if r.flow_status == "FAIL":
                patterns["chapter_flow_FAIL"] += 1
            if r.craft_gate_status == "FAIL":
                patterns["craft_gate_ONTGP_FAIL"] += 1
            if r.scene_status == "FAIL":
                patterns["scene_anti_genericity_FAIL"] += 1
            if r.book_pass_status == "FAIL":
                patterns["book_pass_validation_FAIL"] += 1
            if r.thesis_drift_status == "WARN":
                patterns["thesis_drift_WARN"] += 1
            if r.word_status == "WARN":
                patterns["word_budget_WARN"] += 1
            if r.scene_collisions > 0:
                patterns["scene_collisions_detected"] += r.scene_collisions
            if r.scene_static_chapters > 0:
                patterns["static_scene_chapters"] += r.scene_static_chapters
            if r.scene_detail_failures > 0:
                patterns["three_detail_rule_failures"] += r.scene_detail_failures
            if r.craft_fail_chapters > 0:
                patterns["ONTGP_fail_chapters_total"] += r.craft_fail_chapters
    return dict(patterns.most_common())


def _repetition_analysis(results: List[BookQuality], top_n: int = 20) -> List[Dict[str, Any]]:
    """
    Find the most-repeated 3-gram phrases across all books.
    Samples from the rendered text to avoid memory issues.
    """
    phrase_counter: Counter = Counter()

    for r in results:
        render_dir = Path(r.render_dir)
        if not render_dir.is_dir():
            continue
        chapters = _collect_chapter_texts(render_dir)
        book_phrases: set = set()
        for ch in chapters:
            # Sample: first 2000 words per chapter to limit compute
            words = ch.split()[:2000]
            text = " ".join(words)
            for ngram in _extract_ngrams(text, n=3):
                book_phrases.add(ngram)
        for phrase in book_phrases:
            phrase_counter[phrase] += 1

    # Filter to phrases appearing in 5+ books
    repeated = [
        {"phrase": phrase, "book_count": count}
        for phrase, count in phrase_counter.most_common(top_n * 5)
        if count >= 5
    ]
    return repeated[:top_n]


def _scene_collision_rate(results: List[BookQuality]) -> Dict[str, Any]:
    """Calculate scene collision statistics across all books."""
    total_books = len(results)
    books_with_collisions = sum(1 for r in results if r.scene_collisions > 0)
    total_collisions = sum(r.scene_collisions for r in results)
    return {
        "books_with_collisions": books_with_collisions,
        "total_books_analyzed": total_books,
        "collision_rate": round(books_with_collisions / total_books, 4) if total_books else 0,
        "total_collision_pairs": total_collisions,
    }


def _bestseller_recommendations(results: List[BookQuality]) -> List[Dict[str, Any]]:
    """
    Identify persona x topic x format combinations that consistently produce
    bestseller-grade (PASS verdict) content.
    """
    combos: Dict[Tuple[str, str, str], List[str]] = defaultdict(list)
    for r in results:
        key = (r.persona, r.topic, r.format_id)
        combos[key].append(r.verdict)

    recommendations: List[Dict[str, Any]] = []
    for (persona, topic, fmt), verdicts in sorted(combos.items()):
        total = len(verdicts)
        passes = verdicts.count("PASS")
        if total >= 2:  # need at least 2 books for meaningful signal
            pass_rate = passes / total
            recommendations.append({
                "persona": persona,
                "topic": topic,
                "format_id": fmt,
                "total_books": total,
                "pass_count": passes,
                "pass_rate": round(pass_rate, 3),
                "grade": (
                    "A" if pass_rate >= 0.8 else
                    "B" if pass_rate >= 0.5 else
                    "C" if pass_rate >= 0.2 else
                    "F"
                ),
            })

    # Sort: A-grade first, then by pass_rate descending
    grade_order = {"A": 0, "B": 1, "C": 2, "F": 3}
    recommendations.sort(key=lambda x: (grade_order.get(x["grade"], 9), -x["pass_rate"]))
    return recommendations


def build_report(results: List[BookQuality]) -> Dict[str, Any]:
    """Build the full quality report from analyzed results."""
    total = len(results)
    verdict_counts = Counter(r.verdict for r in results)

    report: Dict[str, Any] = {
        "summary": {
            "total_books_analyzed": total,
            "verdicts": dict(verdict_counts),
            "pass_rate": round(verdict_counts.get("PASS", 0) / total, 4) if total else 0,
        },
        "per_persona_breakdown": _breakdown_by_field(results, "persona"),
        "per_topic_breakdown": _breakdown_by_field(results, "topic"),
        "per_format_breakdown": _breakdown_by_field(results, "format_id"),
        "per_location_breakdown": _breakdown_by_field(results, "location"),
        "per_quality_profile_breakdown": _breakdown_by_field(results, "quality_profile"),
        "top_10_best": _top_n(results, 10, best=True),
        "top_10_worst": _top_n(results, 10, best=False),
        "failure_patterns": _failure_pattern_analysis(results),
        "repetition_analysis": _repetition_analysis(results),
        "scene_collision_rate": _scene_collision_rate(results),
        "recommendations": _bestseller_recommendations(results),
    }
    return report


# ---------------------------------------------------------------------------
# Markdown summary writer
# ---------------------------------------------------------------------------

def write_markdown_summary(report: Dict[str, Any], output_path: Path) -> None:
    """Write a human-readable Markdown summary of the quality report."""
    lines: List[str] = []

    def _line(s: str = "") -> None:
        lines.append(s)

    summary = report["summary"]
    _line("# Bestseller Quality Report")
    _line()
    _line(f"**Total books analyzed:** {summary['total_books_analyzed']}")
    _line()
    _line("## Overall Quality Distribution")
    _line()
    _line("| Verdict | Count | Rate |")
    _line("|---------|------:|-----:|")
    total = summary["total_books_analyzed"] or 1
    for verdict in ("PASS", "NEEDS_REVISION", "FAIL", "SKIP"):
        count = summary["verdicts"].get(verdict, 0)
        rate = f"{count / total:.1%}"
        _line(f"| {verdict} | {count} | {rate} |")
    _line()

    # Per-persona breakdown
    _line("## Per-Persona Quality")
    _line()
    _line("| Persona | PASS | NEEDS_REVISION | FAIL |")
    _line("|---------|-----:|---------------:|-----:|")
    for persona, counts in report["per_persona_breakdown"].items():
        p = counts.get("PASS", 0)
        nr = counts.get("NEEDS_REVISION", 0)
        f = counts.get("FAIL", 0)
        _line(f"| {persona} | {p} | {nr} | {f} |")
    _line()

    # Per-topic breakdown
    _line("## Per-Topic Quality")
    _line()
    _line("| Topic | PASS | NEEDS_REVISION | FAIL |")
    _line("|-------|-----:|---------------:|-----:|")
    for topic, counts in report["per_topic_breakdown"].items():
        p = counts.get("PASS", 0)
        nr = counts.get("NEEDS_REVISION", 0)
        f = counts.get("FAIL", 0)
        _line(f"| {topic} | {p} | {nr} | {f} |")
    _line()

    # Per-format breakdown
    _line("## Per-Format Quality")
    _line()
    _line("| Format | PASS | NEEDS_REVISION | FAIL |")
    _line("|--------|-----:|---------------:|-----:|")
    for fmt, counts in report["per_format_breakdown"].items():
        p = counts.get("PASS", 0)
        nr = counts.get("NEEDS_REVISION", 0)
        f = counts.get("FAIL", 0)
        _line(f"| {fmt} | {p} | {nr} | {f} |")
    _line()

    # Top 10 best
    _line("## Top 10 Best Books")
    _line()
    for i, book in enumerate(report["top_10_best"], 1):
        ontgp = book.get("ontgp_scores", {})
        _line(f"### {i}. Book {book['index']:04d}")
        _line(f"- **Persona:** {book['persona']}")
        _line(f"- **Topic:** {book['topic']} / {book.get('engine', '')}")
        _line(f"- **Format:** {book['format_id']}")
        _line(f"- **Verdict:** {book['verdict']}")
        _line(f"- **Words:** {book['word_count']}")
        _line(f"- **ONTGP:** O={ontgp.get('orient', 0):.2f} "
              f"N={ontgp.get('name', 0):.2f} "
              f"T={ontgp.get('turn', 0):.2f} "
              f"G={ontgp.get('give', 0):.2f} "
              f"P={ontgp.get('pull', 0):.2f}")
        _line()

    # Top 10 worst
    _line("## Top 10 Worst Books")
    _line()
    for i, book in enumerate(report["top_10_worst"], 1):
        _line(f"### {i}. Book {book['index']:04d}")
        _line(f"- **Persona:** {book['persona']}")
        _line(f"- **Topic:** {book['topic']}")
        _line(f"- **Verdict:** {book['verdict']}")
        _line(f"- **Editorial:** {book.get('editorial_status', 'N/A')}")
        _line(f"- **Scene:** {book.get('scene_status', 'N/A')}")
        _line(f"- **Craft Gate:** {book.get('craft_gate_status', 'N/A')}")
        err = book.get("error")
        if err:
            _line(f"- **Error:** {err[:120]}")
        _line()

    # Failure patterns
    _line("## Most Common Failure Patterns")
    _line()
    _line("| Pattern | Count |")
    _line("|---------|------:|")
    for pattern, count in sorted(
        report["failure_patterns"].items(), key=lambda x: -x[1]
    ):
        _line(f"| {pattern} | {count} |")
    _line()

    # Repetition analysis
    _line("## Most Repeated Phrases (3-grams)")
    _line()
    _line("| Phrase | Books Using It |")
    _line("|--------|---------------:|")
    for item in report["repetition_analysis"][:15]:
        _line(f"| {item['phrase']} | {item['book_count']} |")
    _line()

    # Scene collision rate
    scr = report["scene_collision_rate"]
    _line("## Scene Collision Rate")
    _line()
    _line(f"- Books with intra-book collisions: "
          f"{scr['books_with_collisions']}/{scr['total_books_analyzed']} "
          f"({scr['collision_rate']:.1%})")
    _line(f"- Total collision pairs: {scr['total_collision_pairs']}")
    _line()

    # Recommendations
    _line("## Bestseller-Grade Combinations")
    _line()
    _line("Persona x Topic x Format combinations with the highest PASS rates:")
    _line()
    _line("| Grade | Persona | Topic | Format | Pass Rate | Books |")
    _line("|-------|---------|-------|--------|----------:|------:|")
    for rec in report["recommendations"][:30]:
        _line(f"| {rec['grade']} | {rec['persona']} | {rec['topic']} | "
              f"{rec['format_id']} | {rec['pass_rate']:.0%} | {rec['total_books']} |")
    _line()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze bestseller quality from simulation results.",
    )
    parser.add_argument(
        "--results", type=str, default=None,
        help=f"Path to simulation results JSONL (default: {DEFAULT_RESULTS_PATH}).",
    )
    parser.add_argument(
        "--output-dir", type=str, default=None,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR}).",
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Analyze only the first N successful books.",
    )
    parser.add_argument(
        "--max-parallel", type=int, default=4,
        help="Maximum parallel workers (default: 4).",
    )
    args = parser.parse_args()

    results_path = Path(args.results) if args.results else DEFAULT_RESULTS_PATH
    output_dir = Path(args.output_dir) if args.output_dir else DEFAULT_OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    if not results_path.exists():
        print(f"ERROR: Results file not found: {results_path}", file=sys.stderr)
        print("Run run_1000_book_simulation.py first.", file=sys.stderr)
        sys.exit(1)

    # Load simulation results
    all_records = _load_jsonl(results_path)
    print(f"Loaded {len(all_records)} records from {results_path}")

    # Filter to successful books only
    successful = [r for r in all_records if r.get("success", False)]
    print(f"Successful books to analyze: {len(successful)}")

    if args.limit:
        successful = successful[:args.limit]
        print(f"Limited to first {args.limit} books.")

    if not successful:
        print("No successful books to analyze.", file=sys.stderr)
        sys.exit(1)

    # Analyze books (parallel)
    print(f"Analyzing {len(successful)} books with {args.max_parallel} workers...")
    t0 = time.monotonic()
    qualities: List[BookQuality] = []
    completed = 0

    with ProcessPoolExecutor(max_workers=args.max_parallel) as executor:
        future_to_record = {
            executor.submit(analyze_single_book, record): record
            for record in successful
        }

        for future in as_completed(future_to_record):
            record = future_to_record[future]
            try:
                quality = future.result()
            except Exception as exc:
                quality = BookQuality(
                    index=record.get("index", -1),
                    persona=record.get("persona", ""),
                    topic=record.get("topic", ""),
                    engine=record.get("engine", ""),
                    format_id=record.get("format_id", ""),
                    location=record.get("location", ""),
                    quality_profile=record.get("quality_profile", ""),
                    render_dir=record.get("render_dir", ""),
                    analysis_error=f"WORKER_EXCEPTION: {exc}",
                    verdict="FAIL",
                )
            qualities.append(quality)
            completed += 1

            if completed % 50 == 0 or completed == len(successful):
                elapsed = time.monotonic() - t0
                print(f"  [{completed}/{len(successful)}] "
                      f"elapsed={elapsed:.0f}s "
                      f"verdicts so far: "
                      f"PASS={sum(1 for q in qualities if q.verdict == 'PASS')} "
                      f"NR={sum(1 for q in qualities if q.verdict == 'NEEDS_REVISION')} "
                      f"FAIL={sum(1 for q in qualities if q.verdict == 'FAIL')}")

    # Sort by index
    qualities.sort(key=lambda q: q.index)
    elapsed = time.monotonic() - t0
    print(f"\nAnalysis complete in {elapsed:.1f}s")

    # Build report
    print("Building quality report...")
    report = build_report(qualities)

    # Write JSON report
    json_path = output_dir / "bestseller_quality_report.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"JSON report: {json_path}")

    # Write Markdown summary
    md_path = output_dir / "bestseller_quality_report.md"
    write_markdown_summary(report, md_path)
    print(f"Markdown summary: {md_path}")

    # Print quick summary
    s = report["summary"]
    print(f"\n{'=' * 60}")
    print("QUALITY SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total analyzed:    {s['total_books_analyzed']}")
    for verdict in ("PASS", "NEEDS_REVISION", "FAIL", "SKIP"):
        count = s["verdicts"].get(verdict, 0)
        rate = count / (s["total_books_analyzed"] or 1)
        print(f"  {verdict:20s} {count:>5}  ({rate:.1%})")
    print(f"  Pass rate:          {s['pass_rate']:.1%}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
