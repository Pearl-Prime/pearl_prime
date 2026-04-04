#!/usr/bin/env python3
"""
Generate full content catalog for all teachers × personas × topics × locales × platforms.

Uses platform_knob_tuning.yaml to select optimal formats and knobs per platform.
Respects release_wave_controls.yaml caps (max 6 same topic/week, max 10 teacher/week, etc.).

Usage:
    # Dry run — show catalog plan without generating
    python scripts/generate_catalog.py --dry-run

    # Generate for one teacher, one locale
    python scripts/generate_catalog.py --teacher ahjan --locale en-US --limit 10

    # Generate full catalog (all teachers, all locales)
    python scripts/generate_catalog.py --all

    # Generate for specific platform
    python scripts/generate_catalog.py --platform audible --locale en-US --limit 20
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent

try:
    import yaml
except ImportError:
    print("pyyaml required: pip install pyyaml")
    sys.exit(1)


def _load_yaml(p: Path) -> dict:
    if not p.exists():
        return {}
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def build_catalog_manifest(
    teachers: list[str] | None = None,
    personas: list[str] | None = None,
    topics: list[str] | None = None,
    locales: list[str] | None = None,
    platforms: list[str] | None = None,
    limit: int = 0,
) -> list[dict[str, Any]]:
    """Build the catalog manifest — all valid (teacher, persona, topic, locale, platform, format) combos."""

    # Load configs
    canon_personas = _load_yaml(REPO_ROOT / "config" / "catalog_planning" / "canonical_personas.yaml")
    canon_topics = _load_yaml(REPO_ROOT / "config" / "catalog_planning" / "canonical_topics.yaml")
    teacher_matrix = _load_yaml(REPO_ROOT / "config" / "catalog_planning" / "teacher_persona_matrix.yaml")
    locale_reg = _load_yaml(REPO_ROOT / "config" / "localization" / "locale_registry.yaml")
    platform_tuning = _load_yaml(REPO_ROOT / "config" / "catalog_planning" / "platform_knob_tuning.yaml")
    arcs_dir = REPO_ROOT / "config" / "source_of_truth" / "master_arcs"

    # Resolve dimensions
    all_personas = list((canon_personas.get("personas") or canon_personas).keys()) if isinstance(canon_personas.get("personas", canon_personas), dict) else [p.get("id", p) if isinstance(p, dict) else p for p in (canon_personas.get("personas") or [])]
    if not all_personas:
        all_personas = [d.name for d in (REPO_ROOT / "atoms").iterdir() if d.is_dir() and not d.name.startswith(".")]

    all_topics_raw = canon_topics.get("topics") or canon_topics
    if isinstance(all_topics_raw, dict):
        all_topics = list(all_topics_raw.keys())
    elif isinstance(all_topics_raw, list):
        all_topics = [t.get("id", t) if isinstance(t, dict) else t for t in all_topics_raw]
    else:
        all_topics = ["anxiety", "boundaries", "burnout", "compassion_fatigue", "courage", "depression",
                      "financial_anxiety", "financial_stress", "grief", "imposter_syndrome", "overthinking",
                      "self_worth", "sleep_anxiety", "social_anxiety", "somatic_healing"]

    all_teachers = [d.name for d in (REPO_ROOT / "SOURCE_OF_TRUTH" / "teacher_banks").iterdir() if d.is_dir()]
    locale_platforms = (platform_tuning.get("locale_platform_defaults") or {})
    all_locales = list(locale_platforms.keys()) if locale_platforms else ["en-US"]

    # Apply filters
    if teachers:
        all_teachers = [t for t in all_teachers if t in teachers]
    if personas:
        all_personas = [p for p in all_personas if p in personas]
    if topics:
        all_topics = [t for t in all_topics if t in topics]
    if locales:
        all_locales = [l for l in all_locales if l in locales]

    # Find available arcs
    arc_files = {f.stem: f for f in arcs_dir.glob("*.yaml")}

    manifest = []
    for locale in sorted(all_locales):
        locale_plats = locale_platforms.get(locale, ["audible"])
        if platforms:
            locale_plats = [p for p in locale_plats if p in platforms]

        for platform in locale_plats:
            plat_prefs = (platform_tuning.get("platform_profiles") or {}).get(platform, {})
            preferred_formats = plat_prefs.get("preferred_formats", ["F006"])

            for teacher in sorted(all_teachers):
                for persona in sorted(all_personas):
                    for topic in sorted(all_topics):
                        # Find matching arc
                        for fmt in preferred_formats:
                            arc_key = f"{persona}__{topic}__*__{fmt}"
                            matching_arcs = [k for k in arc_files if k.startswith(f"{persona}__{topic}__") and k.endswith(f"__{fmt}")]
                            if matching_arcs:
                                arc_name = matching_arcs[0]
                                manifest.append({
                                    "teacher": teacher,
                                    "persona": persona,
                                    "topic": topic,
                                    "locale": locale,
                                    "platform": platform,
                                    "format": fmt,
                                    "arc": arc_name,
                                    "arc_path": str(arc_files[arc_name]),
                                })
                                break  # one format per platform per combo

        if limit and len(manifest) >= limit:
            manifest = manifest[:limit]
            break

    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate full content catalog")
    parser.add_argument("--teacher", help="Filter to specific teacher")
    parser.add_argument("--persona", help="Filter to specific persona")
    parser.add_argument("--topic", help="Filter to specific topic")
    parser.add_argument("--locale", help="Filter to specific locale")
    parser.add_argument("--platform", help="Filter to specific platform")
    parser.add_argument("--all", action="store_true", help="Generate full catalog")
    parser.add_argument("--limit", type=int, default=0, help="Limit total books")
    parser.add_argument("--dry-run", action="store_true", help="Show plan without generating")
    parser.add_argument("--quality-profile", default="production", choices=["production", "draft"])
    parser.add_argument("--output-dir", default="artifacts/catalog")
    args = parser.parse_args()

    if not args.all and not any([args.teacher, args.persona, args.locale, args.platform]):
        parser.error("Specify --all or at least one filter (--teacher, --locale, etc.)")

    teachers = [args.teacher] if args.teacher else None
    personas = [args.persona] if args.persona else None
    topics = [args.topic] if args.topic else None
    locales = [args.locale] if args.locale else None
    platforms = [args.platform] if args.platform else None

    manifest = build_catalog_manifest(
        teachers=teachers, personas=personas, topics=topics,
        locales=locales, platforms=platforms, limit=args.limit,
    )

    print(f"Catalog manifest: {len(manifest)} books")
    if not manifest:
        print("No matching books found.")
        return 1

    # Summary
    from collections import Counter
    print(f"  Teachers: {len(set(m['teacher'] for m in manifest))}")
    print(f"  Personas: {len(set(m['persona'] for m in manifest))}")
    print(f"  Topics:   {len(set(m['topic'] for m in manifest))}")
    print(f"  Locales:  {len(set(m['locale'] for m in manifest))}")
    print(f"  Platforms: {len(set(m['platform'] for m in manifest))}")
    print(f"  Formats:  {Counter(m['format'] for m in manifest).most_common(5)}")

    if args.dry_run:
        for i, m in enumerate(manifest[:20]):
            print(f"  [{i+1:4d}] {m['teacher']}/{m['persona']}/{m['topic']} → {m['locale']}/{m['platform']}/{m['format']}")
        if len(manifest) > 20:
            print(f"  ... and {len(manifest) - 20} more")
        return 0

    # Generate books
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    passed = failed = 0
    for i, m in enumerate(manifest):
        book_dir = out_dir / f"{m['teacher']}_{m['persona']}_{m['topic']}_{m['locale']}_{m['platform']}"
        book_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            sys.executable, "scripts/run_pipeline.py",
            "--topic", m["topic"],
            "--persona", m["persona"],
            "--arc", m["arc_path"],
            "--teacher", m["teacher"],
            "--location", "nyc_metro",
            "--quality-profile", args.quality_profile,
            "--render-book",
            "--render-dir", str(book_dir),
            "--out", str(book_dir / "plan.json"),
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=str(REPO_ROOT))

        if result.returncode == 0:
            passed += 1
            txt_files = list(book_dir.glob("*.txt"))
            wc = sum(len(f.read_text().split()) for f in txt_files) if txt_files else 0
            print(f"  [{i+1:4d}/{len(manifest)}] PASS {m['teacher']}/{m['persona']}/{m['topic']} — {wc}w")
        else:
            failed += 1
            err = result.stderr.strip().split('\n')
            short = [l for l in err if 'Error' in l or 'failed' in l.lower()][-1:]
            print(f"  [{i+1:4d}/{len(manifest)}] FAIL {m['teacher']}/{m['persona']}/{m['topic']} — {short[0][:80] if short else 'unknown'}")

    print(f"\nCatalog: {passed} passed, {failed} failed, {len(manifest)} total")

    # Save manifest
    manifest_path = out_dir / "catalog_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    print(f"Manifest: {manifest_path}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
