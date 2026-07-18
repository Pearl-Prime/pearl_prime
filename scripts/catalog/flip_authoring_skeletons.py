#!/usr/bin/env python3
"""Flip en_US skeleton plans (arc+atoms present) to buildable.

Sets _needs_authoring: false and fills title/subtitle via phoenix_v4.naming when empty.
Deterministic — no paid LLM. Idempotent.

  PYTHONPATH=. python3 scripts/catalog/flip_authoring_skeletons.py --dry-run
  PYTHONPATH=. python3 scripts/catalog/flip_authoring_skeletons.py --brand warrior_calm --limit 5
  PYTHONPATH=. python3 scripts/catalog/flip_authoring_skeletons.py --json-out artifacts/coordination/flip_report.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

import yaml

from phoenix_v4.naming import cli as naming

ROOT = Path(__file__).resolve().parents[2]
PLANS = ROOT / "config/source_of_truth/book_plans_en_us"
ARCS = ROOT / "config/source_of_truth/master_arcs"
ATOMS = ROOT / "atoms"

INTENTS = ["scenario_specific", "solution_seeking", "identity_based", "crisis", "informational"]
_ANXIETY_FAMILY = {"anxiety", "sleep_anxiety", "social_anxiety", "financial_anxiety", "overthinking"}
_TOPIC_BISAC = {t: ["SEL036000", "SEL024000", "SEL031000"] for t in _ANXIETY_FAMILY}


def _h(s: str) -> int:
    return int(hashlib.sha1(s.encode()).hexdigest()[:8], 16)


def _parse_stem(stem: str) -> tuple[str, str, str, str, str] | None:
    is_1hr = stem.endswith("__1hr")
    s = stem[:-5] if is_1hr else stem
    parts = s.split("__")
    if len(parts) < 5:
        return None
    brand, teacher, persona, topic, engine = parts[0], parts[1], parts[2], parts[3], parts[4]
    return brand, teacher, persona, topic, engine


def _cell_has_arc(persona: str, topic: str, engine: str, arc_set: set[tuple[str, str, str]]) -> bool:
    return (persona, topic, engine) in arc_set


def _cell_has_atoms(persona: str, topic: str, engine: str) -> bool:
    p = ATOMS / persona / topic / engine / "CANONICAL.txt"
    return p.is_file() and p.stat().st_size > 100


def _topic_bisac(topic: str) -> list[str]:
    return list(_TOPIC_BISAC.get(topic, []))


def _needs_flip(plan: dict) -> bool:
    return plan.get("_needs_authoring") is True


def _flip_plan(plan: dict, *, dry_run: bool) -> str | None:
    """Return skip reason or None if flipped/would flip."""
    bid = plan.get("book_id") or ""
    parsed = _parse_stem(bid)
    if not parsed:
        return "bad_parse"
    brand, _teacher, persona, topic, engine = parsed
    if not _cell_has_atoms(persona, topic, engine):
        return "no_atoms"
    arc_set = _flip_plan._arc_set  # type: ignore[attr-defined]
    if not _cell_has_arc(persona, topic, engine, arc_set):
        return "no_arc"

    title = (plan.get("title") or "").strip()
    subtitle = (plan.get("subtitle") or "").strip()
    installment = int(plan.get("installment_number") or 1)
    series_base = "__".join(bid.split("__")[:4])
    nm: dict = {}

    if not title or not subtitle:
        try:
            nm = naming.run(topic, persona, series_base, intent, brand, "", str(_h(bid)), installment)
            if not title:
                title = (nm.get("title") or "").strip()
            if not subtitle:
                subtitle = (nm.get("subtitle") or "").strip()
        except Exception as exc:
            return f"naming_error:{exc}"

    if not title:
        return "empty_title"

    plan["title"] = title
    plan["subtitle"] = subtitle or plan.get("subtitle") or f"A guide for {persona.replace('_', ' ').title()}"
    if not plan.get("bisac_codes"):
        plan["bisac_codes"] = _topic_bisac(topic)
    kw = plan.get("keywords") or {}
    if isinstance(kw, dict) and not kw.get("primary"):
        pk = (nm.get("keywords") or {}).get("primary") if nm else topic.replace("_", " ")
        kw["primary"] = [pk] if isinstance(pk, str) else (pk or [topic.replace("_", " ")])
        plan["keywords"] = kw
    plan["_needs_authoring"] = False
    plan["confidence"] = plan.get("confidence") or {"pricing": "low", "title": "medium", "comps": "low"}

    if not dry_run:
        path = PLANS / f"{bid}.yaml"
        path.write_text(yaml.safe_dump(plan, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--brand", action="append", dest="brands", help="Limit to brand(s)")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args()

    arc_set: set[tuple[str, str, str]] = set()
    for p in ARCS.glob("*.yaml"):
        parts = p.stem.split("__")
        if len(parts) == 4:
            arc_set.add((parts[0], parts[1], parts[2]))
    _flip_plan._arc_set = arc_set  # type: ignore[attr-defined]

    brand_filter = set(args.brands) if args.brands else None
    stats = Counter()
    flipped = 0

    for f in sorted(PLANS.glob("*.yaml")):
        if args.limit and flipped >= args.limit:
            break
        plan = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        if not _needs_flip(plan):
            continue
        bid = plan.get("book_id") or f.stem
        brand = bid.split("__")[0]
        if brand_filter and brand not in brand_filter:
            continue
        reason = _flip_plan(plan, dry_run=args.dry_run)
        if reason:
            stats[reason] += 1
        else:
            stats["flipped"] += 1
            flipped += 1

    report = {
        "dry_run": args.dry_run,
        "flipped": stats["flipped"],
        "skipped": {k: v for k, v in stats.items() if k != "flipped"},
    }
    print(f"flipped: {stats['flipped']} dry_run={args.dry_run}")
    for k, v in sorted(stats.items()):
        if k != "flipped":
            print(f"  skip {k}: {v}")

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
