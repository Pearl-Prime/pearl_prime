"""Deterministic resolution: a catalog row -> a fully-specified cover.

author display name -> author_id (slug) -> author card (family/fonts/palette)
topic -> motif ; installment -> book number AND symbol count ; book_id -> seed
(stable symbol arrangement + stable pool-image pick).

Image-family authors with no pool of their own fall back to a track-matched
pilot pool (for the zero-GPU PROOF only); real per-author pools are generated
at scale time (pools.py).
"""
from __future__ import annotations
import csv
import hashlib
from pathlib import Path

import yaml

from . import palette as P
from .templates import Spec

ROOT = Path(__file__).resolve().parents[3]
CFG = ROOT / "config/publishing/waystream_cover_system.yaml"
CATALOG = ROOT / "artifacts/waystream/waystream_800book_catalog_plan.csv"
PLANS_DIR = ROOT / "config/source_of_truth/book_plans_en_us"
SERVED_COVERS = ROOT / "brand-wizard-app/public/assets/covers/way_stream_sanctuary"
POOLS = ROOT / "artifacts/waystream/author_pools"

TRACK_FALLBACK_POOL = {"activation": "lena_frost", "ground": "theo_castellan"}


def load_cfg(path: Path = CFG) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def load_catalog(path: Path = CATALOG) -> list[dict]:
    if not path.is_file():
        return []
    with open(path) as f:
        return list(csv.DictReader(f))


def _author_display(cfg: dict, byline_slug: str) -> str:
    card = cfg["authors"].get(byline_slug) or {}
    return card.get("display") or byline_slug.replace("_", " ").title()


def _cluster_from_plan(plan: dict) -> str:
    ss = plan.get("store_series") or {}
    name = (ss.get("name") or "").strip()
    return name.split(" — ")[0].strip() if name else ""


def row_from_plan(cfg: dict, plan: dict, stem: str, legacy: dict | None = None) -> dict:
    """Build a catalog row keyed by plan book_id (source of truth for titles)."""
    parts = stem.split("__")
    ap = plan.get("author_positioning") or {}
    byline = (ap.get("byline_author") or "").strip()
    row = dict(legacy or {})
    row.update({
        "book_id": plan["book_id"],
        "title": (plan.get("title") or "").strip(),
        "subtitle": (plan.get("subtitle") or "").strip(),
        "author": _author_display(cfg, byline),
        "installment": str(plan.get("installment_number") or row.get("installment") or ""),
        "topic": plan.get("topic") or (parts[3] if len(parts) > 3 else row.get("topic", "")),
        "engine": plan.get("engine") or (parts[4].removesuffix("__1hr") if len(parts) > 4 else row.get("engine", "")),
        "persona": plan.get("persona") or (parts[2] if len(parts) > 2 else row.get("persona", "")),
        "cluster": _cluster_from_plan(plan) or row.get("cluster", ""),
    })
    return row


def sync_catalog_from_plans(
    brand: str = "way_stream_sanctuary",
    out_path: Path = CATALOG,
    cfg: dict | None = None,
) -> list[dict]:
    """Regenerate cover catalog CSV from book plans (plan book_id = row book_id)."""
    cfg = cfg or load_cfg()
    legacy_by_title = {r["title"]: r for r in load_catalog()}
    rows: list[dict] = []
    for f in sorted(PLANS_DIR.glob(f"{brand}__*.yaml")):
        plan = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        if plan.get("_needs_authoring") is not False or not plan.get("title"):
            continue
        title = (plan.get("title") or "").strip()
        legacy = legacy_by_title.get(title)
        rows.append(row_from_plan(cfg, plan, f.stem, legacy))
    if not rows:
        raise SystemExit(f"no authored plans for brand {brand}")
    rows.sort(key=lambda r: (r.get("persona", ""), r.get("topic", ""), r.get("engine", ""), int(r.get("installment") or 0)))
    fieldnames = list(rows[0].keys())
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    return rows


def slug(name: str) -> str:
    return name.strip().lower().replace("'", "").replace(".", "").replace(" ", "_")


def seed_of(s: str) -> int:
    return int(hashlib.sha1(s.encode()).hexdigest()[:8], 16)


def pool_images(author_id: str) -> list[Path]:
    d = POOLS / author_id
    return sorted(d.glob("*.png")) if d.exists() else []


def pick_pool_image(author_id: str, track: str, book_id: str, allow_fallback=True):
    imgs = pool_images(author_id)
    src = author_id
    if not imgs and allow_fallback:
        src = TRACK_FALLBACK_POOL.get(track)
        imgs = pool_images(src) if src else []
    if not imgs:
        return None, None
    return imgs[seed_of(book_id) % len(imgs)], src


def spec_from_row(cfg: dict, row: dict, allow_fallback=True):
    aid = slug(row["author"])
    card = cfg["authors"].get(aid)
    if not card:
        raise KeyError(f"author not in config: {row['author']} -> {aid}")
    inst = int(row["installment"])
    motif = cfg["topic_symbols"].get(row["topic"], {}).get("motif", "ring")
    spec = Spec(
        title=row["title"], subtitle=row["subtitle"],
        author_display=row["author"], imprint=cfg["brand"]["imprint"],
        series_name=row["cluster"].strip().upper(), book_num=inst, count=inst,
        topic=row["topic"], motif=motif,
        serif=card["serif"], sans=card["sans"], title_case=card.get("title_case", "sentence"),
        deep=P.hex_rgb(card["deep"]), field=P.hex_rgb(card["field"]), accent=P.hex_rgb(card["accent"]),
        seed=seed_of(row["book_id"]), family=card["family"],
    )
    img_path, pool_src = (None, None)
    if card["family"] in cfg["image_families"]:
        img_path, pool_src = pick_pool_image(aid, card["track"], row["book_id"], allow_fallback)
    return spec, img_path, pool_src, aid
