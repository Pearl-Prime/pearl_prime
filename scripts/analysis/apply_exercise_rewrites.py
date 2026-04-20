#!/usr/bin/env python3
"""
apply_exercise_rewrites.py
Pearl_Writer exercise replacement script.

Replaces F1 variants of EXERCISE sections in template registries
with Pearl_Writer generated content.

Usage:
    python3 scripts/analysis/apply_exercise_rewrites.py --topic burnout --json-file /tmp/burnout_exercises.json
    python3 scripts/analysis/apply_exercise_rewrites.py --all --json-dir /tmp/exercise_outputs/
"""

import argparse
import json
import re
import sys
from pathlib import Path

REGISTRY_DIR = Path("registry")

# The 7 standard exercise variant IDs in all template registries
EXERCISE_VARIANT_IDS = [
    "ch04_sec06_exercise_f1",
    "ch07_sec03_exercise_f1",
    "ch07_sec04_exercise_f1",
    "ch07_sec05_exercise_f1",
    "ch08_sec03_exercise_f1",
    "ch08_sec04_exercise_f1",
    "ch08_sec05_exercise_f1",
]

# Prohibited terms — hard block (from topic_skins.yaml global_rules)
GLOBAL_PROHIBITED = [
    "journey", "transform", "heal", "healing journey", "self-care", "wellness",
    "mindfulness", "empower", "empowering", "overcome", "conquer", "battle",
    "fight", "warrior", "survivor", "thrive", "manifest", "authentic self",
    "best self", "inner child", "trigger warning", "safe space", "toxic",
    "self-love", "you've got this", "be gentle with yourself",
    "believe in yourself", "everything happens for a reason",
    "it gets better", "stay strong", "you're not alone", "reach out",
]

TOPIC_PROHIBITED = {
    "anxiety": ["anxiety attack", "panic attack", "anxiety disorder", "mental health",
                 "coping mechanism", "grounding technique"],
    "boundaries": ["healthy boundaries", "toxic people", "protect your energy",
                   "boundary setting", "self-protection"],
    "financial_stress": ["abundance mindset", "money blocks", "financial freedom",
                          "wealth consciousness", "prosperity", "manifest money"],
    "courage": ["brave", "fearless", "courageous", "bold", "leap of faith", "comfort zone"],
    "compassion_fatigue": ["burnout", "self-care", "caregiver fatigue", "emotional labor",
                            "set boundaries", "compassion satisfaction"],
    "depression": ["depression", "depressed", "mental illness", "chemical imbalance",
                   "antidepressant", "clinical", "diagnosis"],
    "self_worth": ["self-esteem", "self-worth", "worthy", "deserve", "enough",
                   "imposter syndrome", "inner critic"],
    "grief": ["closure", "move on", "get over it", "stages of grief", "grief process",
              "healing process", "they're in a better place", "everything happens for a reason",
              "at least"],
    "financial_anxiety": ["abundance mindset", "money blocks", "financial freedom",
                           "wealth consciousness", "prosperity", "manifest money"],
}


def check_prohibited(text: str, topic: str) -> list[str]:
    """Return list of prohibited terms found in text."""
    violations = []
    text_lower = text.lower()
    all_prohibited = GLOBAL_PROHIBITED + TOPIC_PROHIBITED.get(topic, [])
    for term in all_prohibited:
        if term.lower() in text_lower:
            violations.append(term)
    return violations


def format_yaml_content(text: str, indent: int = 12) -> str:
    """Format multi-line text for YAML block scalar or flow scalar."""
    text = text.strip()
    # If it fits on one line and has no special chars, use flow scalar
    if "\n" not in text and len(text) < 200 and '"' not in text:
        return text
    # Use block scalar with proper indentation
    indent_str = " " * indent
    lines = text.split("\n")
    result = "|\n"
    for line in lines:
        result += indent_str + line + "\n"
    return result.rstrip()


def replace_exercise_in_yaml(content: str, variant_id: str, new_text: str) -> tuple[str, bool]:
    """
    Replace the content field of a specific exercise variant in YAML.
    Returns (new_content, was_replaced).
    """
    # Pattern: find the variant_id line, then find the content: line after it
    # We look for the variant_id, then the next content: line before the next variant_id or fingerprint
    pattern = re.compile(
        r'(        - variant_id: ' + re.escape(variant_id) + r'\n'
        r'          variant_number: \d+\n'
        r'          variant_family: F1\n'
        r'          content: )(.+?)(\n          fingerprint:)',
        re.DOTALL
    )

    new_text_clean = new_text.strip().replace('"', "'")

    # Try to find and replace
    match = pattern.search(content)
    if not match:
        return content, False

    # Format the replacement content
    # Use a simple quoted scalar if no special characters
    if "\n" not in new_text_clean and len(new_text_clean) < 300:
        replacement_content = new_text_clean
    else:
        # Use block scalar
        lines = new_text_clean.split("\n")
        replacement_content = "|\n" + "".join(f"            {line}\n" for line in lines)
        replacement_content = replacement_content.rstrip()

    new_content = pattern.sub(
        r'\g<1>' + replacement_content + r'\g<3>',
        content,
        count=1
    )
    return new_content, new_content != content


def apply_exercises_to_registry(topic: str, exercises: dict) -> dict:
    """
    Apply exercise rewrites to a registry YAML file.
    Returns summary dict with results.
    """
    registry_path = REGISTRY_DIR / f"{topic}.yaml"
    if not registry_path.exists():
        return {"topic": topic, "status": "error", "message": f"Registry not found: {registry_path}"}

    content = registry_path.read_text(encoding="utf-8")
    results = {"topic": topic, "applied": [], "skipped": [], "guardrail_blocked": [], "not_found": []}

    for variant_id in EXERCISE_VARIANT_IDS:
        if variant_id not in exercises:
            results["skipped"].append(variant_id)
            continue

        new_text = exercises[variant_id].strip()

        # Guardrail check
        violations = check_prohibited(new_text, topic)
        if violations:
            results["guardrail_blocked"].append({
                "variant_id": variant_id,
                "violations": violations,
                "text_preview": new_text[:80]
            })
            print(f"  BLOCKED {variant_id}: prohibited terms {violations}", file=sys.stderr)
            continue

        # Word count check
        word_count = len(new_text.split())
        if word_count > 120:  # Allow slight overflow
            print(f"  WARNING {variant_id}: {word_count} words (limit 100)", file=sys.stderr)

        content, replaced = replace_exercise_in_yaml(content, variant_id, new_text)
        if replaced:
            results["applied"].append(variant_id)
            print(f"  OK {variant_id} ({word_count} words)")
        else:
            results["not_found"].append(variant_id)
            print(f"  MISS {variant_id}: pattern not found in YAML", file=sys.stderr)

    if results["applied"]:
        # Create snapshot before writing
        snapshot_path = registry_path.with_suffix(".yaml.pre_exercise_rewrite")
        if not snapshot_path.exists():
            snapshot_path.write_text(registry_path.read_text(encoding="utf-8"), encoding="utf-8")
            print(f"  Snapshot saved: {snapshot_path.name}")
        registry_path.write_text(content, encoding="utf-8")
        print(f"  Wrote {registry_path} ({len(results['applied'])} exercises updated)")

    return results


def main():
    parser = argparse.ArgumentParser(description="Apply Pearl_Writer exercise rewrites to registry YAML files")
    parser.add_argument("--topic", help="Single topic to process (e.g. burnout)")
    parser.add_argument("--json-file", help="Path to JSON file with exercise content for one topic")
    parser.add_argument("--all", action="store_true", help="Process all topics using --json-dir")
    parser.add_argument("--json-dir", help="Directory containing topic JSON files (named topic.json)")
    parser.add_argument("--dry-run", action="store_true", help="Check but don't write")
    args = parser.parse_args()

    all_results = []

    if args.topic and args.json_file:
        data = json.loads(Path(args.json_file).read_text())
        if not args.dry_run:
            result = apply_exercises_to_registry(args.topic, data)
        else:
            result = {"topic": args.topic, "dry_run": True}
        all_results.append(result)

    elif args.all and args.json_dir:
        json_dir = Path(args.json_dir)
        for json_path in sorted(json_dir.glob("*.json")):
            topic = json_path.stem
            if topic == "grief":
                print(f"SKIP {topic} (READ-ONLY gold standard)")
                continue
            data = json.loads(json_path.read_text())
            print(f"\n=== {topic} ===")
            if not args.dry_run:
                result = apply_exercises_to_registry(topic, data)
            else:
                result = {"topic": topic, "dry_run": True}
            all_results.append(result)

    else:
        parser.print_help()
        sys.exit(1)

    # Summary
    print("\n=== SUMMARY ===")
    total_applied = sum(len(r.get("applied", [])) for r in all_results)
    total_blocked = sum(len(r.get("guardrail_blocked", [])) for r in all_results)
    total_miss = sum(len(r.get("not_found", [])) for r in all_results)
    print(f"Applied: {total_applied}")
    print(f"Guardrail blocked: {total_blocked}")
    print(f"Pattern not found: {total_miss}")

    if total_blocked > 0:
        print("\nBLOCKED DETAILS:")
        for r in all_results:
            for b in r.get("guardrail_blocked", []):
                print(f"  {r['topic']}/{b['variant_id']}: {b['violations']}")

    return 0 if total_blocked == 0 and total_miss == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
