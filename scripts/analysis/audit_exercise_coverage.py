#!/usr/bin/env python3
"""
audit_exercise_coverage.py — Audit EXERCISE atom coverage for a persona × topic combo.

Checks:
1. How many EXERCISE-type atoms exist for this persona × topic
2. Whether they cover all chapter positions in the expected arc
3. Whether library_34 fallback is being hit due to missing atoms

Usage:
    python3 scripts/analysis/audit_exercise_coverage.py \
        --persona gen_z_professionals \
        --topic anxiety \
        --output artifacts/regression/exercise_coverage_audit.md
"""
import argparse
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def parse_args():
    p = argparse.ArgumentParser(description="Audit EXERCISE atom coverage")
    p.add_argument("--persona", required=True)
    p.add_argument("--topic", required=True)
    p.add_argument("--output", default="artifacts/regression/exercise_coverage_audit.md")
    p.add_argument("--verbose", action="store_true")
    return p.parse_args()


def find_atom_dirs() -> list[Path]:
    """Return candidate directories containing atom YAML files."""
    candidates = [
        Path("config/source_of_truth"),
        Path("config/atoms"),
        Path("config/content_banks"),
        Path("config"),
        Path("phoenix_v4/atoms"),
        Path("phoenix_v4"),
        Path("data/atoms"),
    ]
    return [c for c in candidates if c.exists()]


def load_yaml_safe(path: Path) -> dict | list | None:
    if not HAS_YAML:
        return None
    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except Exception:
        return None


def is_exercise_atom(data, path: Path) -> bool:
    """Heuristic: is this YAML file an EXERCISE-type atom?"""
    path_str = str(path).lower()
    if "exercise" in path_str:
        return True
    if data is None:
        return False
    if isinstance(data, dict):
        atom_type = str(data.get("type", data.get("atom_type", ""))).lower()
        if "exercise" in atom_type:
            return True
        tags = data.get("tags", [])
        if isinstance(tags, list) and any("exercise" in str(t).lower() for t in tags):
            return True
    return False


def matches_persona_topic(data, path: Path, persona: str, topic: str) -> bool:
    """Check if an atom file is associated with persona and/or topic."""
    path_str = str(path).lower()
    persona_slug = persona.lower().replace("_", "[-_]?")
    topic_slug = topic.lower()
    path_match = re.search(persona_slug, path_str) or topic_slug in path_str
    if path_match:
        return True
    if data is None:
        return False
    data_str = str(data).lower()
    return (re.search(persona_slug, data_str) is not None or topic_slug in data_str)


def count_chapter_positions(data) -> set[int]:
    """Return set of chapter positions this atom is valid for."""
    positions = set()
    if not isinstance(data, dict):
        return positions
    for key in ("chapter_positions", "positions", "valid_positions", "chapter"):
        val = data.get(key)
        if val is not None:
            if isinstance(val, list):
                positions.update(int(v) for v in val if str(v).isdigit())
            elif str(val).isdigit():
                positions.add(int(val))
    return positions


def check_library_fallback_in_logs(persona: str, topic: str) -> list[str]:
    """Scan recent log files for library_34 fallback mentions."""
    hits = []
    log_dirs = [Path("artifacts"), Path("logs"), Path(".")]
    for d in log_dirs:
        if not d.exists():
            continue
        for log_file in sorted(d.glob("**/*.log"), key=os.path.getmtime, reverse=True)[:5]:
            try:
                content = log_file.read_text()
                for line in content.split("\n"):
                    if "library_34" in line and (persona in line or topic in line):
                        hits.append(f"{log_file}: {line.strip()}")
            except Exception:
                pass
    return hits


def main():
    args = parse_args()

    atom_dirs = find_atom_dirs()
    print(f"Scanning {len(atom_dirs)} atom directory candidates...", file=sys.stderr)

    exercise_atoms = []       # (path, data)
    persona_topic_atoms = []  # exercise atoms matching persona × topic
    all_yaml_count = 0

    for d in atom_dirs:
        for f in d.rglob("*.yaml"):
            all_yaml_count += 1
            data = load_yaml_safe(f) if HAS_YAML else None
            if is_exercise_atom(data, f):
                exercise_atoms.append((f, data))
                if matches_persona_topic(data, f, args.persona, args.topic):
                    persona_topic_atoms.append((f, data))
        for f in d.rglob("*.yml"):
            all_yaml_count += 1
            data = load_yaml_safe(f) if HAS_YAML else None
            if is_exercise_atom(data, f):
                exercise_atoms.append((f, data))
                if matches_persona_topic(data, f, args.persona, args.topic):
                    persona_topic_atoms.append((f, data))

    # Collect chapter position coverage
    positions_covered = set()
    for _, data in persona_topic_atoms:
        positions_covered |= count_chapter_positions(data)

    # Check for library_34 fallback in recent logs
    fallback_hits = check_library_fallback_in_logs(args.persona, args.topic)

    # Gap analysis — expected positions 1–12 for a standard book
    expected_positions = set(range(1, 13))
    missing_positions = expected_positions - positions_covered if positions_covered else set()

    # Write report
    lines = [
        f"# EXERCISE Coverage Audit — {args.persona} × {args.topic}",
        "",
        "## Summary",
        f"- Total YAML files scanned: **{all_yaml_count}**",
        f"- Total EXERCISE atoms found: **{len(exercise_atoms)}**",
        f"- EXERCISE atoms for {args.persona} × {args.topic}: **{len(persona_topic_atoms)}**",
        f"- Chapter positions covered: **{sorted(positions_covered) if positions_covered else 'unknown'}**",
        f"- Missing positions (1–12): **{sorted(missing_positions) if missing_positions else 'none detected'}**",
        f"- library_34 fallback hits in recent logs: **{len(fallback_hits)}**",
        "",
        f"## Verdict",
        "",
    ]

    if len(persona_topic_atoms) == 0:
        lines.append("🔴 **CRITICAL**: No EXERCISE atoms found for this persona × topic combo.")
        lines.append("All EXERCISE slots will hit the library_34 fallback. Needs new atom content.")
    elif len(persona_topic_atoms) < 3:
        lines.append(f"🟡 **LOW COVERAGE**: Only {len(persona_topic_atoms)} atoms found. Likely causing fallback.")
    elif missing_positions:
        lines.append(f"🟡 **GAP**: Chapters {sorted(missing_positions)} have no dedicated EXERCISE atoms.")
    else:
        lines.append("🟢 **OK**: Coverage looks adequate for standard book length.")

    lines += ["", "## EXERCISE Atoms Found", ""]
    if persona_topic_atoms:
        for path, _ in persona_topic_atoms[:30]:
            lines.append(f"- `{path}`")
    else:
        lines.append("_None found._")

    if fallback_hits:
        lines += ["", "## library_34 Fallback Hits in Recent Logs", "```"]
        lines += fallback_hits[:20]
        lines += ["```"]

    lines += [
        "",
        "## Recommendations",
        "",
        "1. If **0 atoms found**: create EXERCISE atom YAML files under",
        f"   `config/source_of_truth/atoms/exercise/{args.topic}/` targeting `{args.persona}`.",
        "2. If **positions missing**: add atoms specifying `chapter_positions: [N, M, ...]` for gaps.",
        "3. If **library_34 hits confirmed**: temporary workaround — add a library_34 diversification",
        "   pass in enrichment_select.py to rotate variants before final fallback.",
        "4. Run `trace_library_fallback.py` for detailed fallback trace.",
    ]

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    report = "\n".join(lines)
    out.write_text(report)
    print(f"Report written to {out}", file=sys.stderr)
    print(report)

    # Exit non-zero if coverage gap
    sys.exit(1 if len(persona_topic_atoms) < 3 or missing_positions else 0)


if __name__ == "__main__":
    main()
