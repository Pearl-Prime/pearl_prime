#!/usr/bin/env python3
"""
trace_library_fallback.py — Trace which atom slots hit the library_34 fallback
for a given persona × topic combo.

Scans:
1. Recent pipeline log files for library_34 fallback mentions
2. The enrichment_select / spine planning code for fallback triggers
3. Arc YAML files to identify slots that have no primary coverage

Usage:
    python3 scripts/analysis/trace_library_fallback.py \
        --persona gen_z_professionals \
        --topic anxiety \
        --output artifacts/regression/library_34_fallback_trace.md
"""
import argparse
import os
import re
import sys
from pathlib import Path
from collections import defaultdict

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def parse_args():
    p = argparse.ArgumentParser(description="Trace library_34 fallback usage")
    p.add_argument("--persona", required=True)
    p.add_argument("--topic", required=True)
    p.add_argument("--output", default="artifacts/regression/library_34_fallback_trace.md")
    return p.parse_args()


def find_arc_yaml(persona: str, topic: str) -> Path | None:
    """Find the arc YAML file for this persona × topic."""
    search_dirs = [
        Path("config/source_of_truth"),
        Path("config/arcs"),
        Path("config"),
        Path("phoenix_v4"),
        Path("data"),
    ]
    persona_slug = persona.lower()
    topic_slug = topic.lower()
    for d in search_dirs:
        if not d.exists():
            continue
        for f in d.rglob("*.yaml"):
            name = f.name.lower()
            if persona_slug in name and topic_slug in name:
                return f
        for f in d.rglob("*.yml"):
            name = f.name.lower()
            if persona_slug in name and topic_slug in name:
                return f
    return None


def scan_logs_for_fallback(persona: str, topic: str) -> dict:
    """Scan log files for library_34 fallback mentions and extract context."""
    results = defaultdict(list)
    log_dirs = [Path("artifacts"), Path("logs"), Path(".")]
    pattern = re.compile(r"library_34|fallback|FALLBACK", re.IGNORECASE)
    persona_pattern = re.compile(re.escape(persona), re.IGNORECASE)
    topic_pattern = re.compile(re.escape(topic), re.IGNORECASE)

    for d in log_dirs:
        if not d.exists():
            continue
        for log_file in sorted(d.glob("**/*.log"), key=os.path.getmtime, reverse=True)[:10]:
            try:
                lines = log_file.read_text().split("\n")
                for i, line in enumerate(lines):
                    if pattern.search(line):
                        context_lines = lines[max(0, i-2):i+3]
                        has_persona_or_topic = any(
                            persona_pattern.search(l) or topic_pattern.search(l)
                            for l in context_lines
                        )
                        if has_persona_or_topic:
                            results[str(log_file)].append({
                                "line_num": i + 1,
                                "line": line.strip(),
                                "context": [l.strip() for l in context_lines],
                            })
            except Exception:
                pass
    return dict(results)


def scan_enrichment_select_for_fallback_logic() -> list[str]:
    """Find fallback logic in enrichment_select.py or similar."""
    candidates = [
        Path("phoenix_v4/planning/enrichment_select.py"),
        Path("phoenix_v4/enrichment_select.py"),
        Path("phoenix_v4/planning/slot_select.py"),
    ]
    findings = []
    fallback_pattern = re.compile(r"library_34|fallback|FALLBACK|default.*atom", re.IGNORECASE)
    for path in candidates:
        if not path.exists():
            continue
        try:
            lines = path.read_text().split("\n")
            for i, line in enumerate(lines):
                if fallback_pattern.search(line):
                    findings.append(f"{path}:{i+1}: {line.rstrip()}")
        except Exception:
            pass
    return findings


def analyse_arc_slots(arc_path: Path, persona: str, topic: str) -> dict:
    """Parse arc YAML and identify EXERCISE slots."""
    if not HAS_YAML or arc_path is None:
        return {"slots": [], "exercise_slots": [], "arc_path": None}

    try:
        data = yaml.safe_load(arc_path.read_text())
    except Exception as e:
        return {"slots": [], "exercise_slots": [], "arc_path": str(arc_path), "error": str(e)}

    slots = []
    exercise_slots = []

    def recurse(node, chapter=None):
        if isinstance(node, dict):
            slot_type = node.get("type", node.get("atom_type", ""))
            if slot_type:
                entry = {"type": slot_type, "chapter": chapter}
                slots.append(entry)
                if "EXERCISE" in str(slot_type).upper():
                    exercise_slots.append(entry)
            for k, v in node.items():
                if k in ("chapter", "chapter_num", "position"):
                    recurse(v, chapter=node.get(k, chapter))
                else:
                    recurse(v, chapter=chapter)
        elif isinstance(node, list):
            for item in node:
                recurse(item, chapter=chapter)

    recurse(data)
    return {
        "slots": slots,
        "exercise_slots": exercise_slots,
        "arc_path": str(arc_path),
        "total_slots": len(slots),
        "total_exercise_slots": len(exercise_slots),
    }


def main():
    args = parse_args()

    arc_path = find_arc_yaml(args.persona, args.topic)
    arc_info = analyse_arc_slots(arc_path, args.persona, args.topic) if arc_path else {
        "slots": [], "exercise_slots": [], "arc_path": None
    }

    fallback_hits = scan_logs_for_fallback(args.persona, args.topic)
    code_fallback_lines = scan_enrichment_select_for_fallback_logic()

    lines = [
        f"# library_34 Fallback Trace — {args.persona} × {args.topic}",
        "",
        "## Arc Analysis",
        f"- Arc file: `{arc_info.get('arc_path', 'NOT FOUND')}`",
        f"- Total slots in arc: {arc_info.get('total_slots', 'N/A')}",
        f"- EXERCISE slots: {arc_info.get('total_exercise_slots', 'N/A')}",
        "",
    ]

    if arc_info.get("exercise_slots"):
        lines += ["### EXERCISE Slot Positions", "| Chapter | Type |", "|---------|------|"]
        for slot in arc_info["exercise_slots"][:20]:
            lines.append(f"| {slot.get('chapter', '?')} | `{slot['type']}` |")
        lines.append("")

    lines += [
        "## library_34 Fallback in Log Files",
        f"Files with fallback hits: **{len(fallback_hits)}**",
        "",
    ]

    if fallback_hits:
        for log_file, hits in list(fallback_hits.items())[:5]:
            lines.append(f"### `{log_file}` ({len(hits)} hits)")
            for hit in hits[:5]:
                lines.append(f"**Line {hit['line_num']}:** `{hit['line']}`")
                lines += ["```"] + hit["context"] + ["```", ""]
    else:
        lines.append("_No library_34 fallback hits found in recent logs for this persona × topic._")
        lines.append("")
        lines.append("> Note: logs may not be present if the pipeline hasn't run recently.")
        lines.append("")

    lines += [
        "## Fallback Logic in Code",
        f"Found {len(code_fallback_lines)} relevant lines in enrichment_select / slot_select:",
        "```",
    ]
    lines += (code_fallback_lines[:20] if code_fallback_lines else ["(none found)"])
    lines += ["```", ""]

    lines += [
        "## Recommendations",
        "",
        "1. If EXERCISE slots > 0 but all hit library_34: missing atom content for",
        f"   `{args.persona}` × `{args.topic}`. Create targeted YAML atoms.",
        "2. If arc has no EXERCISE slots: the arc itself may need EXERCISE entries added.",
        "3. If fallback logic has no diversity rotation: add a rotation pass before",
        "   returning library_34 to prevent identical content across chapters.",
        "4. Cross-reference with `audit_exercise_coverage.py` output for full picture.",
    ]

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    report = "\n".join(lines)
    out.write_text(report)
    print(f"Report written to {out}", file=sys.stderr)
    print(report)

    sys.exit(1 if fallback_hits else 0)


if __name__ == "__main__":
    main()
