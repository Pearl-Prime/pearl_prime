#!/usr/bin/env python3
"""ITE CI: Stealth vocabulary scan (T-04).
Authority: specs/IMPLICIT_THERAPEUTIC_ENGINE_DEV_SPEC.md §12.2, §15.1
Scans chapter_script.json dialogue + captions for forbidden therapeutic terms.
Exit 1 if any found."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def load_forbidden_terms() -> list[str]:
    """Load from ei_v2_config.yaml — single source of truth."""
    config_path = REPO_ROOT / "config" / "quality" / "ei_v2_config.yaml"
    if config_path.exists():
        try:
            import yaml
            data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
            vt = data.get("visual_therapeutic", {})
            dims = vt.get("dimensions", {})
            stealth = dims.get("vt_stealth", {})
            terms = stealth.get("forbidden_terms", [])
            if terms:
                return [t.lower() for t in terms]
        except Exception:
            pass
    # Fallback hardcoded list
    return [
        "therapy", "mindfulness", "grounding", "breathing exercise",
        "meditation", "wellness", "self-care", "healing journey",
        "inner peace", "mental health", "calm down", "relax your body",
        "take a breath",
    ]


def scan_text(text: str, forbidden: list[str]) -> list[dict]:
    violations = []
    text_lower = text.lower()
    for term in forbidden:
        pattern = re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)
        for match in pattern.finditer(text):
            violations.append({
                "term": term,
                "position": match.start(),
                "context": text[max(0, match.start() - 30):match.end() + 30],
            })
    return violations


def main() -> int:
    ap = argparse.ArgumentParser(description="ITE stealth vocabulary scan")
    ap.add_argument("--chapter-dir", required=True, help="Chapter output directory")
    args = ap.parse_args()
    chapter_dir = Path(args.chapter_dir)
    script_file = chapter_dir / "chapter_script.json"
    if not script_file.exists():
        print("No chapter_script.json found; skipping stealth scan")
        return 0

    data = json.loads(script_file.read_text(encoding="utf-8"))
    forbidden = load_forbidden_terms()
    all_violations = []

    # Scan dialogue
    for page in data.get("pages", []):
        for panel in page.get("panels", []):
            for dlg in panel.get("dialogue", []):
                text = dlg.get("text", "") if isinstance(dlg, dict) else str(dlg)
                violations = scan_text(text, forbidden)
                for v in violations:
                    v["source"] = f"dialogue:{panel.get('panel_id', 'unknown')}"
                all_violations.extend(violations)
            # Scan captions
            for cap in panel.get("captions", []):
                text = cap.get("text", "") if isinstance(cap, dict) else str(cap)
                violations = scan_text(text, forbidden)
                for v in violations:
                    v["source"] = f"caption:{panel.get('panel_id', 'unknown')}"
                all_violations.extend(violations)

    result = {
        "gate": "ite_stealth_scan",
        "violations": all_violations,
        "pass": len(all_violations) == 0,
    }
    print(json.dumps(result, indent=2))

    if all_violations:
        print(f"T-04 BLOCKER: {len(all_violations)} forbidden term(s) found", file=sys.stderr)
        for v in all_violations:
            print(f"  {v['source']}: '{v['term']}' — ...{v['context']}...", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
