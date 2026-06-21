"""book_plans_en_us/*.yaml -> cover render rows for a brand.

Resolves the pen-name author via the wired resolver
(phoenix_v4.planning.author_brand_resolver) — topic/persona come from the
book_id (brand__teacher__persona__topic__engine).
"""
from __future__ import annotations
from pathlib import Path
import yaml

try:
    from phoenix_v4.planning.author_brand_resolver import resolve_author_from_brand
except Exception:  # resolver optional; fall back to brand 'house' line
    def resolve_author_from_brand(**_kw):
        return None

ROOT = Path(__file__).resolve().parents[3]
BOOK_PLANS = ROOT / "config/source_of_truth/book_plans_en_us"
# Superset roster (curated + generated) when present, else the curated default.
GEN_ASSIGN = ROOT / "config/brand_author_assignments_generated.yaml"
ASSIGN_PATH = GEN_ASSIGN if GEN_ASSIGN.exists() else None


def parse_book_id(book_id: str):
    parts = book_id.split("__")
    if len(parts) >= 5:
        return parts[0], parts[2], parts[3], parts[4]   # brand, persona, topic, engine
    return parts[0], "", "", (parts[-1] if parts else "")


def rows_for_brand(brand_id: str, book_plans_dir: Path = BOOK_PLANS):
    rows = []
    for p in sorted(book_plans_dir.glob(f"{brand_id}__*.yaml")):
        d = yaml.safe_load(p.read_text()) or {}
        if d.get("_needs_authoring") is not False:
            continue  # authored-only: skip skeletons (true) + legacy orphans (field absent)
        bid = d.get("book_id", p.stem)
        _, persona, topic, engine = parse_book_id(bid)
        aid = resolve_author_from_brand(brand_id=brand_id, topic_id=topic, persona_id=persona,
                                        assignments_path=ASSIGN_PATH) or "house"
        rows.append({
            "book_id": bid,
            "title": d.get("title", ""),
            "subtitle": d.get("subtitle", ""),
            "author_id": aid,
            "topic": topic,
            "persona": persona,
            "engine": engine,
            "installment": int(d.get("installment_number", 1) or 1),
            "series_name": topic.replace("_", " ").upper(),
        })
    return rows
