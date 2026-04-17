#!/usr/bin/env python3
"""
diagnose_repetition.py — Analyse a pipeline run log or content bank for
content repetition patterns that cause quality_gate REJECT.

Usage:
    python3 scripts/analysis/diagnose_repetition.py \
        --topic anxiety \
        --persona gen_z_professionals \
        --runtime-format deep_book_6h \
        --output artifacts/regression/deep_book_6h_repetition_diagnosis.md

    python3 scripts/analysis/diagnose_repetition.py \
        --input artifacts/regression/deep_book_6h_trace.log \
        --output artifacts/regression/deep_book_6h_repetition_diagnosis.md
"""
import argparse
import os
import re
import sys
import json
from collections import Counter, defaultdict
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser(description="Diagnose content repetition in pipeline runs")
    p.add_argument("--input", help="Path to existing trace log (optional)")
    p.add_argument("--topic", default="anxiety")
    p.add_argument("--persona", default="gen_z_professionals")
    p.add_argument("--runtime-format", default="deep_book_6h")
    p.add_argument("--output", default="artifacts/regression/repetition_diagnosis.md")
    return p.parse_args()


def find_generated_book(topic: str, persona: str, runtime_format: str) -> Path | None:
    """Locate the most recent generated book for this combo."""
    search_dirs = [
        Path("artifacts/books"),
        Path("artifacts/output"),
        Path("output"),
        Path("artifacts"),
    ]
    pattern = f"{topic}*{persona}*{runtime_format}"
    for d in search_dirs:
        if not d.exists():
            continue
        candidates = sorted(d.glob("**/*.md"), key=os.path.getmtime, reverse=True)
        for c in candidates:
            if topic in str(c) or persona in str(c):
                return c
    return None


def scan_log_for_patterns(log_path: str) -> dict:
    """Extract repetition signals from a run trace log."""
    findings = {
        "reject_reasons": [],
        "repetition_flags": [],
        "band_scores": [],
        "quality_gate_lines": [],
    }
    if not os.path.exists(log_path):
        return findings

    with open(log_path) as f:
        for line in f:
            line = line.rstrip()
            if re.search(r"Reject|REJECT", line):
                findings["reject_reasons"].append(line)
            if re.search(r"repetition|duplicate|repeated", line, re.IGNORECASE):
                findings["repetition_flags"].append(line)
            if re.search(r"band:", line):
                findings["band_scores"].append(line)
            if re.search(r"quality_gate|QualityGate", line):
                findings["quality_gate_lines"].append(line)
    return findings


def analyse_text_for_repetition(text: str) -> dict:
    """Scan chapter text for repeated phrases and sentence openers."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    sentences = re.split(r"(?<=[.!?])\s+", text)

    # Sentence opener repetition (first 3 words)
    openers = Counter()
    for s in sentences:
        words = s.split()
        if len(words) >= 3:
            openers[" ".join(words[:3]).lower()] += 1

    # Repeated 5-gram phrases
    words = text.lower().split()
    ngrams_5 = Counter()
    for i in range(len(words) - 4):
        ng = " ".join(words[i:i+5])
        ngrams_5[ng] += 1

    top_openers = [(k, v) for k, v in openers.most_common(10) if v > 1]
    top_ngrams = [(k, v) for k, v in ngrams_5.most_common(10) if v > 2]

    return {
        "total_paragraphs": len(paragraphs),
        "total_sentences": len(sentences),
        "repeated_openers": top_openers,
        "repeated_5grams": top_ngrams,
        "repetition_score": len(top_openers) + len(top_ngrams),
    }


def scan_content_bank(topic: str, persona: str) -> list[str]:
    """Look for EXERCISE or content bank atoms for this persona × topic combo."""
    search_paths = [
        Path("config/source_of_truth"),
        Path("config/atoms"),
        Path("config"),
        Path("phoenix_v4"),
    ]
    findings = []
    target_pattern = re.compile(
        rf"({re.escape(topic)}|{re.escape(persona)})", re.IGNORECASE
    )
    for base in search_paths:
        if not base.exists():
            continue
        for f in base.rglob("*.yaml"):
            try:
                content = f.read_text()
                if target_pattern.search(content):
                    findings.append(str(f))
            except Exception:
                pass
        for f in base.rglob("*.yml"):
            try:
                content = f.read_text()
                if target_pattern.search(content):
                    findings.append(str(f))
            except Exception:
                pass
    return findings


def write_report(args, log_findings: dict, text_analysis: dict | None,
                 bank_files: list[str], book_path: str | None) -> str:
    lines = [
        f"# Repetition Diagnosis — {args.topic} × {args.persona} ({args.runtime_format})",
        "",
        "## Summary",
        "",
    ]

    has_issues = (
        log_findings["reject_reasons"]
        or log_findings["repetition_flags"]
        or (text_analysis and text_analysis["repetition_score"] > 5)
    )
    lines.append(f"**Issues found:** {'YES — see below' if has_issues else 'None detected'}")
    lines.append("")

    # Log-based findings
    if log_findings["reject_reasons"]:
        lines += ["## Quality Gate Reject Reasons", "```"]
        lines += log_findings["reject_reasons"][:20]
        lines += ["```", ""]

    if log_findings["repetition_flags"]:
        lines += ["## Repetition Flags from Log", "```"]
        lines += log_findings["repetition_flags"][:20]
        lines += ["```", ""]

    if log_findings["band_scores"]:
        lines += ["## Band Scores", "```"]
        lines += log_findings["band_scores"][:10]
        lines += ["```", ""]

    # Text analysis
    if text_analysis:
        lines += [
            f"## Text Analysis (from: {book_path})",
            f"- Paragraphs: {text_analysis['total_paragraphs']}",
            f"- Sentences: {text_analysis['total_sentences']}",
            f"- Repetition score: **{text_analysis['repetition_score']}**",
            "",
        ]
        if text_analysis["repeated_openers"]:
            lines += ["### Top Repeated Sentence Openers", "| Opener | Count |", "|--------|-------|"]
            for opener, count in text_analysis["repeated_openers"][:10]:
                lines.append(f"| `{opener}` | {count} |")
            lines.append("")
        if text_analysis["repeated_5grams"]:
            lines += ["### Top Repeated 5-grams", "| Phrase | Count |", "|--------|-------|"]
            for phrase, count in text_analysis["repeated_5grams"][:10]:
                lines.append(f"| `{phrase}` | {count} |")
            lines.append("")
    else:
        lines += ["## Text Analysis", "_No generated book found for text analysis._", ""]

    # Content bank scan
    lines += [f"## Content Bank Files Found ({len(bank_files)})", ""]
    if bank_files:
        for f in bank_files[:20]:
            lines.append(f"- `{f}`")
    else:
        lines.append("_No content bank files found for this persona × topic._")
    lines.append("")

    # Recommendations
    lines += [
        "## Recommendations",
        "",
        "1. **If repeated sentence openers > 5:** Add opener-diversity constraint to Pearl_Writer prompt.",
        "2. **If repeated 5-grams > 3:** Enable dedup filter in enrichment_select.py before render.",
        "3. **If quality_gate REJECT with band scores < 0.4:** Investigate `_FLOW_GLUE_VARIANTS` exhaustion (P0.6).",
        "4. **If no content bank files found:** EXERCISE atoms may be missing — see `audit_exercise_coverage.py`.",
        "5. **If log shows REFLECTION fallback:** Wire late-book REFLECTION bank fill (P0.6 remainder).",
        "",
        "> Run `python3 scripts/analysis/audit_exercise_coverage.py` for EXERCISE-specific coverage audit.",
    ]

    return "\n".join(lines)


def main():
    args = parse_args()

    # Scan log if provided or if default exists
    log_path = args.input or ""
    log_findings = scan_log_for_patterns(log_path) if log_path else {
        "reject_reasons": [], "repetition_flags": [], "band_scores": [], "quality_gate_lines": []
    }

    # Try to find and analyse generated book text
    text_analysis = None
    book_path = find_generated_book(args.topic, args.persona, args.runtime_format)
    if book_path:
        try:
            text = book_path.read_text()
            text_analysis = analyse_text_for_repetition(text)
            print(f"Analysed book: {book_path}", file=sys.stderr)
        except Exception as e:
            print(f"Could not read book at {book_path}: {e}", file=sys.stderr)

    # Scan content banks
    bank_files = scan_content_bank(args.topic, args.persona)

    # Write report
    report = write_report(args, log_findings, text_analysis, bank_files, str(book_path) if book_path else None)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report)
    print(f"Report written to {out}", file=sys.stderr)
    print(report)

    # Exit non-zero if issues found
    has_issues = (
        log_findings["reject_reasons"]
        or log_findings["repetition_flags"]
        or (text_analysis and text_analysis["repetition_score"] > 5)
    )
    sys.exit(1 if has_issues else 0)


if __name__ == "__main__":
    main()
