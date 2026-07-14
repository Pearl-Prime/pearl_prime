#!/usr/bin/env python3
"""
Bridge: unified brand registry  →  brand_admin_weekly_os.html backend (static JSON).

Same pattern as gen_setup_helper_brands.py (#1600) — a generated public JSON the page
fetches via ?brand=<id>, so the Phase 0–3 console resolves the canonical 39×14 brand_ids
the wizard assigns (e.g. devotion_path_en_us → "Open Vessel Press"), with NO live backend.
Replaces the page's stale embedded deep-25 brand map.

Emits brand-wizard-app/public/brand_admin_brands.json keyed by brand_id, shape {d,t,tm,tr,f,tp,lane,manga_pct}
to match the console's existing B[] consumer. Run after regenerating the unified registry.

When the registry omits primary_topics for a composite brand, backfills from locale
catalog CSVs (artifacts/catalog/pearl_prime_book_script_catalogs/*_catalog.csv) and,
as fallback, en_US book plans (config/source_of_truth/book_plans_en_us/).
"""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from brand_director_assignments import director_for, load_director_assignments

REPO = Path(__file__).resolve().parents[2]
UNIFIED = REPO / "config" / "brand_management" / "global_brand_registry_unified.yaml"
CATALOG_DIR = REPO / "artifacts" / "catalog" / "pearl_prime_book_script_catalogs"
BOOK_PLANS = REPO / "config" / "source_of_truth" / "book_plans_en_us"
OUT = REPO / "brand-wizard-app" / "public" / "brand_admin_brands.json"
TOPIC_LIMIT = 6


def humanize(s) -> str:
    return " ".join(w.capitalize() for w in str(s or "").split("_")) if s else ""


def _non_buildable() -> set:
    """Archetype bases the onboarding matcher must NOT land a signup on (0 shippable)."""
    cfg = REPO / "config" / "brand_management" / "brand_buildability.yaml"
    try:
        return set((yaml.safe_load(cfg.read_text(encoding="utf-8")) or {}).get("non_buildable") or {})
    except Exception:
        return set()


def _top_topics(counter: Counter, limit: int = TOPIC_LIMIT) -> list[str]:
    return [t for t, _ in counter.most_common(limit) if t]


def _catalog_topics_by_archetype() -> dict[str, list[str]]:
    """brand column in locale catalogs = archetype base → ranked topic slugs."""
    counts: dict[str, Counter] = defaultdict(Counter)
    if not CATALOG_DIR.is_dir():
        return {}
    for csv_path in sorted(CATALOG_DIR.glob("*_catalog.csv")):
        try:
            with csv_path.open(encoding="utf-8", newline="") as fh:
                for row in csv.DictReader(fh):
                    arch = (row.get("brand") or "").strip()
                    topic = (row.get("topic") or "").strip()
                    if arch and topic:
                        counts[arch][topic] += 1
        except Exception:
            continue
    return {arch: _top_topics(c) for arch, c in counts.items() if c}


def _book_plan_topics_by_archetype() -> dict[str, list[str]]:
    """en_US book plan stems: <archetype>__<teacher>__<persona>__<topic>__…"""
    counts: dict[str, Counter] = defaultdict(Counter)
    if not BOOK_PLANS.is_dir():
        return {}
    for plan in BOOK_PLANS.glob("*.yaml"):
        parts = plan.stem.split("__")
        if len(parts) < 4:
            continue
        arch, topic = parts[0], parts[3]
        if arch and topic:
            counts[arch][topic] += 1
    return {arch: _top_topics(c) for arch, c in counts.items() if c}


def _resolve_primary_topics(
    b: dict,
    catalog_topics: dict[str, list[str]],
    plan_topics: dict[str, list[str]],
) -> list[str]:
    tp = b.get("primary_topics") or []
    if tp:
        return list(tp)
    arch = b.get("brand_archetype_id") or ""
    if arch and catalog_topics.get(arch):
        return list(catalog_topics[arch])
    if arch and plan_topics.get(arch):
        return list(plan_topics[arch])
    return []


def main() -> None:
    reg = yaml.safe_load(UNIFIED.read_text(encoding="utf-8")) or {}
    brands = reg.get("brands") or {}
    nb = _non_buildable()
    catalog_topics = _catalog_topics_by_archetype()
    plan_topics = _book_plan_topics_by_archetype()
    directors = load_director_assignments()
    backfilled = 0
    out = {}
    for bid, b in brands.items():
        if not isinstance(b, dict):
            continue
        tid = b.get("teacher_id") or ""
        arch = b.get("brand_archetype_id") or ""
        director = director_for(
            brand_id=bid,
            base_brand=arch,
            assignments=directors,
            allow_base=False,
        )
        tp = _resolve_primary_topics(b, catalog_topics, plan_topics)
        if not (b.get("primary_topics") or []) and tp:
            backfilled += 1
        entry = {
            "d": b.get("publication_corp") or b.get("display_name") or bid,  # display / imprint (KDP publisher)
            "t": humanize(tid),                                              # teacher display
            "tid": tid,                                                      # raw teacher slug (match key)
            "is_teacher": bool(tid),                                         # teacher brand vs composite
            "arch": arch,                                                    # archetype base
            "buildable": bool(arch) and arch not in nb,                      # onboarding may land here?
            "tm": bool(b.get("teacher_mode")),
            "tr": b.get("tradition") or "",
            "f": b.get("brand_focus") or "",
            "tp": tp,
            "lane": b.get("lane_id"),
            "manga_pct": b.get("lane_manga_pct"),
            "lifecycle": b.get("lifecycle") or "active",
        }
        if director:
            entry.update(director)
        out[bid] = entry
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"wrote {len(out)} brands -> {OUT.relative_to(REPO)}")
    if backfilled:
        print(f"  backfilled primary_topics for {backfilled} brand(s) from catalog/book plans")
    ws = out.get("way_stream_sanctuary_ja_jp", {})
    print(f"  way_stream_sanctuary_ja_jp tp={ws.get('tp', 'MISSING')}")
    # sanity: the brand the wizard assigns must resolve
    for k in ("devotion_path_en_us", "stillness_press_en_us"):
        print(f"  {k}: {out.get(k, {}).get('d', 'MISSING')}")


if __name__ == "__main__":
    main()
