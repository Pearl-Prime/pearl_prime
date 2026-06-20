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
POOLS = ROOT / "artifacts/waystream/author_pools"

TRACK_FALLBACK_POOL = {"activation": "lena_frost", "ground": "theo_castellan"}


def load_cfg(path: Path = CFG) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def load_catalog(path: Path = CATALOG) -> list[dict]:
    with open(path) as f:
        return list(csv.DictReader(f))


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
