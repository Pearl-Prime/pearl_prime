#!/usr/bin/env python3
"""Atom coverage audit — reads canonical topics/personas, walks atoms/, produces coverage matrix.

Usage:
    python3 scripts/inventory/atom_coverage_audit.py
    python3 scripts/inventory/atom_coverage_audit.py --topic anxiety
    python3 scripts/inventory/atom_coverage_audit.py --persona entrepreneurs
    python3 scripts/inventory/atom_coverage_audit.py --output-dir /tmp/audit_out
"""
import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).parent.parent.parent
ATOMS_DIR = REPO_ROOT / "atoms"
CONFIG_DIR = REPO_ROOT / "config" / "catalog_planning"
CATALOG_CONFIG = REPO_ROOT / "config" / "catalog" / "catalog_generation_config.yaml"
OUTPUT_DIR = REPO_ROOT / "artifacts" / "inventory"


def load_yaml(path):
    try:
        import yaml
        with open(path) as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Warning: could not load {path}: {e}", file=sys.stderr)
        return None


def get_canonical_topics():
    """Load topics from canonical_topics.yaml, falling back to catalog_generation_config, then atom dir scan."""
    # Primary: canonical_topics.yaml
    for name in ["canonical_topics.yaml", "canonical_topics.yml"]:
        p = CONFIG_DIR / name
        if p.exists():
            data = load_yaml(p)
            if data:
                if isinstance(data, list):
                    return [str(t) for t in data]
                if isinstance(data, dict) and "topics" in data:
                    return [str(t) for t in data["topics"]]

    # Secondary: catalog_generation_config.yaml
    if CATALOG_CONFIG.exists():
        data = load_yaml(CATALOG_CONFIG)
        if data and "topics" in data:
            return [str(t) for t in data["topics"]]

    # Fallback: scan atoms subdirectories for topic dirs
    topics = set()
    if ATOMS_DIR.exists():
        for persona_dir in ATOMS_DIR.iterdir():
            if persona_dir.is_dir() and not persona_dir.name.startswith("."):
                for topic_dir in persona_dir.iterdir():
                    if topic_dir.is_dir() and not topic_dir.name.startswith("."):
                        topics.add(topic_dir.name)
    return sorted(topics)


def get_canonical_personas():
    """Load personas from canonical_personas.yaml, falling back to catalog_generation_config, then atom dir scan."""
    # Primary: canonical_personas.yaml
    for name in ["canonical_personas.yaml", "canonical_personas.yml"]:
        p = CONFIG_DIR / name
        if p.exists():
            data = load_yaml(p)
            if data:
                if isinstance(data, list):
                    return [str(pr) for pr in data]
                if isinstance(data, dict) and "personas" in data:
                    return [str(pr) for pr in data["personas"]]

    # Secondary: catalog_generation_config.yaml
    if CATALOG_CONFIG.exists():
        data = load_yaml(CATALOG_CONFIG)
        if data and "personas" in data:
            return [str(pr) for pr in data["personas"]]

    # Fallback: scan atoms top-level dirs
    if ATOMS_DIR.exists():
        return sorted(
            d.name for d in ATOMS_DIR.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        )
    return []


def check_atom_coverage(persona, topic):
    """Return 'complete', 'partial', or 'missing'.

    Structure: atoms/persona/topic/engine/CANONICAL.txt
    - 'complete': CANONICAL.txt exists at topic level OR in any engine subdir
    - 'partial': topic dir exists with engine subdirs but no CANONICAL.txt anywhere
    - 'missing': topic dir does not exist or is empty
    """
    atom_dir = ATOMS_DIR / persona / topic
    if not atom_dir.exists():
        return "missing"
    # Check CANONICAL.txt at topic level (older structure)
    canonical = atom_dir / "CANONICAL.txt"
    if canonical.exists():
        return "complete"
    # Check CANONICAL.txt in engine subdirs (current structure: atoms/persona/topic/engine/CANONICAL.txt)
    try:
        children = list(atom_dir.iterdir())
    except Exception:
        return "missing"
    engines = [c for c in children if c.is_dir() and not c.name.startswith(".")]
    for engine_dir in engines:
        if (engine_dir / "CANONICAL.txt").exists():
            return "complete"
    # Has engine dirs but no CANONICAL.txt anywhere
    files = [c for c in children if c.is_file() and not c.name.startswith(".")]
    if engines or files:
        return "partial"
    return "missing"


def build_persona_summary(persona, topics, matrix):
    """Return per-persona stats dict."""
    pdata = matrix.get(persona, {})
    complete = sum(1 for t in topics if pdata.get(t) == "complete")
    partial = sum(1 for t in topics if pdata.get(t) == "partial")
    missing = sum(1 for t in topics if pdata.get(t) == "missing")
    total = len(topics)
    pct = round(complete / total * 100, 1) if total > 0 else 0.0
    return {"complete": complete, "partial": partial, "missing": missing, "total": total, "pct": pct}


def build_topic_summary(topic, personas, matrix):
    """Return per-topic stats dict."""
    complete = sum(1 for p in personas if matrix.get(p, {}).get(topic) == "complete")
    partial = sum(1 for p in personas if matrix.get(p, {}).get(topic) == "partial")
    missing = sum(1 for p in personas if matrix.get(p, {}).get(topic) == "missing")
    total = len(personas)
    pct = round(complete / total * 100, 1) if total > 0 else 0.0
    return {"complete": complete, "partial": partial, "missing": missing, "total": total, "pct": pct}


def main():
    parser = argparse.ArgumentParser(description="Atom coverage audit — topic × persona coverage matrix")
    parser.add_argument("--topic", help="Filter to specific topic (substring match)")
    parser.add_argument("--persona", help="Filter to specific persona (substring match)")
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR), help="Output directory for JSON and markdown")
    args = parser.parse_args()

    topics = get_canonical_topics()
    personas = get_canonical_personas()

    if args.topic:
        topics = [t for t in topics if args.topic.lower() in t.lower()]
    if args.persona:
        personas = [p for p in personas if args.persona.lower() in p.lower()]

    print(f"Auditing {len(personas)} personas × {len(topics)} topics = {len(personas) * len(topics)} combos")
    print(f"Topics: {topics}")
    print(f"Personas: {personas}")

    matrix = {}
    stats = {"complete": 0, "partial": 0, "missing": 0}

    for persona in personas:
        matrix[persona] = {}
        for topic in topics:
            status = check_atom_coverage(persona, topic)
            matrix[persona][topic] = status
            stats[status] += 1

    total = stats["complete"] + stats["partial"] + stats["missing"]
    pct = round(stats["complete"] / total * 100, 1) if total > 0 else 0.0

    # Per-persona and per-topic summaries
    persona_summaries = {p: build_persona_summary(p, topics, matrix) for p in personas}
    topic_summaries = {t: build_topic_summary(t, personas, matrix) for t in topics}

    output = {
        "generated": datetime.utcnow().isoformat() + "Z",
        "personas": personas,
        "topics": topics,
        "matrix": matrix,
        "stats": stats,
        "coverage_pct": pct,
        "persona_summaries": persona_summaries,
        "topic_summaries": topic_summaries,
    }

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / "atom_coverage_matrix.json"
    with open(json_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"JSON written: {json_path}")

    # ── Markdown report ──────────────────────────────────────────────────────
    STATUS_EMOJI = {"complete": "OK", "partial": "~", "missing": "X"}

    # Determine buildable threshold (>=90% complete)
    def buildable_label(pct_val):
        if pct_val >= 90:
            return "Yes"
        if pct_val >= 60:
            return "Partial"
        return "No"

    md_lines = [
        "# Atom Coverage Report",
        "",
        f"Generated: {output['generated']}",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Personas | {len(personas)} |",
        f"| Topics | {len(topics)} |",
        f"| Total combos | {total} |",
        f"| Complete | {stats['complete']} ({pct}%) |",
        f"| Partial | {stats['partial']} |",
        f"| Missing | {stats['missing']} |",
        "",
        "## By Persona",
        "",
        "| Persona | Topics | Complete | Partial | Missing | Coverage% | Buildable? |",
        "|---------|--------|----------|---------|---------|-----------|-----------|",
    ]
    for p in personas:
        s = persona_summaries[p]
        md_lines.append(
            f"| {p} | {s['total']} | {s['complete']} | {s['partial']} | {s['missing']} | {s['pct']}% | {buildable_label(s['pct'])} |"
        )

    md_lines += [
        "",
        "## By Topic",
        "",
        "| Topic | Personas | Complete | Partial | Missing | Coverage% | Buildable? |",
        "|-------|----------|----------|---------|---------|-----------|-----------|",
    ]
    for t in topics:
        s = topic_summaries[t]
        md_lines.append(
            f"| {t} | {s['total']} | {s['complete']} | {s['partial']} | {s['missing']} | {s['pct']}% | {buildable_label(s['pct'])} |"
        )

    # Coverage matrix (cap topics at 20 for readability)
    display_topics = topics[:20]
    md_lines += [
        "",
        f"## Coverage Matrix (OK=complete, ~=partial, X=missing; first {len(display_topics)} topics shown)",
        "",
        "| Persona \\\\ Topic | " + " | ".join(display_topics) + " |",
        "|---|" + "---|" * len(display_topics),
    ]
    for p in personas:
        row_vals = [STATUS_EMOJI.get(matrix[p].get(t, "missing"), "X") for t in display_topics]
        md_lines.append(f"| {p} | " + " | ".join(row_vals) + " |")

    # Missing combos
    missing_combos = [(p, t) for p in personas for t in topics if matrix[p].get(t) == "missing"]
    md_lines += [
        "",
        f"## Missing Combos ({len(missing_combos)} total — top 50 shown)",
        "",
    ]
    for p, t in missing_combos[:50]:
        md_lines.append(f"- `{p}` x `{t}`")

    # Partial combos
    partial_combos = [(p, t) for p in personas for t in topics if matrix[p].get(t) == "partial"]
    md_lines += [
        "",
        f"## Partial Combos ({len(partial_combos)} total — top 20 shown)",
        "",
    ]
    for p, t in partial_combos[:20]:
        md_lines.append(f"- `{p}` x `{t}` (has content dir but no CANONICAL.txt)")

    md_path = out_dir / "atom_coverage_report.md"
    with open(md_path, "w") as f:
        f.write("\n".join(md_lines) + "\n")
    print(f"Report written: {md_path}")

    print(f"\nCoverage: {pct}% complete ({stats['complete']}/{total} combos)")
    if stats["missing"] > 0:
        print(f"Missing: {stats['missing']} combos need atoms")
    if stats["partial"] > 0:
        print(f"Partial: {stats['partial']} combos have content dirs but no CANONICAL.txt")

    return 0


if __name__ == "__main__":
    sys.exit(main())
