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
import re
from pathlib import Path

import yaml

from . import palette as P
from .templates import Spec
from .layout_zones import layout_variant_for_book

ROOT = Path(__file__).resolve().parents[3]
CFG = ROOT / "config/publishing/waystream_cover_system.yaml"
CATALOG = ROOT / "artifacts/waystream/waystream_800book_catalog_plan.csv"
PLANS_DIR = ROOT / "config/source_of_truth/book_plans_en_us"
SERVED_COVERS = ROOT / "brand-wizard-app/public/assets/covers/way_stream_sanctuary"
POOLS = ROOT / "artifacts/waystream/author_pools"

TRACK_FALLBACK_POOL = {"activation": "lena_frost", "ground": "theo_castellan"}

TYPE_DOMINANT_ELIGIBLE = {"gradient_solo", "framed", "duotone_split", "stripe_minimal"}


def render_family(card_family: str, book_id: str) -> str:
    h = hashlib.sha256(f"type_dominant|{book_id}".encode()).digest()
    if card_family in TYPE_DOMINANT_ELIGIBLE and h[2] % 5 == 0:
        return "type_dominant"
    return card_family


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
    # short_hook: plan `cover_short_hook` wins; otherwise preserve an existing
    # CSV hook (legacy merge) so a re-sync never silently drops authored hooks.
    plan_hook = (plan.get("cover_short_hook") or "").strip()
    short_hook = plan_hook or (row.get("short_hook") or "").strip()
    row.update({
        "book_id": plan["book_id"],
        "title": (plan.get("title") or "").strip(),
        "subtitle": (plan.get("subtitle") or "").strip(),
        "short_hook": short_hook,
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


# ---------------------------------------------------------------------------
# PER-AUTHOR COVER FINGERPRINT (anti-spam diversity).
# Mirrors scripts/publish/abstract_cover_art.py:fingerprint() — a sha256 of the
# brand+author id, then per-author bytes drive treatment choices so two authors
# never collide and one author always looks the same. Here it drives two new
# axes (on top of the existing family/serif/sans/palette per author):
#   * framing  — one of {box, strike, double, line_above, line_below} around the
#                (now much bigger) subtitle.
#   * plate    — whether the translucent subtitle contrast plate is drawn.
# Plate is FORCED True whenever the subtitle sits over imagery / a dark gradient
# (image families + gradient_solo + duotone_split) so the bigger subtitle ALWAYS
# reads at thumbnail; on the light-paper families it is a deterministic coin-flip
# (palette contrast + the bigger/bolder subtitle already carry the read there).
# ---------------------------------------------------------------------------
FRAMING_TREATMENTS = ["box", "strike", "double", "line_above", "line_below"]

# subtitle-over-dark families: plate is non-negotiable here (legibility wins).
# These render the subtitle over FLUX imagery / a dark gradient half, so a light
# subtitle without a plate could wash out -> plate ALWAYS on.
_DARK_SUBTITLE_FAMILIES = {
    "full_bleed", "title_block",        # subtitle over FLUX imagery + scrim
    "gradient_solo", "duotone_split",   # subtitle over a dark gradient half
}
# The remaining families (inset_card, panel_bands, framed, stripe_minimal) draw
# the subtitle as DARK accent text on a LIGHT paper field — already high contrast,
# so the plate becomes a free uniqueness axis: deterministic coin-flip per author.


# A subtitle longer than this can't render at the operator's >=12px cap-height in
# 3 lines on a 250px thumbnail without overrunning, so it is shortened to a hook.
# Measured ~14 chars/line at the 12px floor; 3 lines ~= 42 chars. We keep this
# generous (only the truly overlong, dash-less marketing sentences trim) — the
# layouts below are sized to hold the full 3-line floor block, so nothing common
# gets an ellipsis.
COVER_SUBTITLE_MAX_CHARS = 42


def cover_subtitle(subtitle: str, short_hook: str | None = None,
                   max_chars: int = COVER_SUBTITLE_MAX_CHARS) -> str:
    """RE-ENABLED (operator 2026-07-01, second pass): spec_from_row calls this to
    compute the per-cell COVER HOOK that the templates use as the fallback when
    the FULL catalog subtitle won't fit at the bigger (2.2x) size. Where the full
    subtitle fits, the templates draw it; only the overrunning cells use this hook.

    The COVER hook = the authored `short_hook` if present, else a SHORT lead
    phrase derived from the catalog subtitle.

    An authored `short_hook` (catalog `short_hook` column / plan
    `cover_short_hook`) is governed by docs HOOK_CONTRACT: <=14 ASCII chars,
    <=2 words (3 only if all <=4 chars), no word >10 chars, Title Case, no
    trailing punctuation. When a non-empty hook is supplied it is preferred
    VERBATIM (whitespace-trimmed only) so the operator-authored, thumbnail-safe
    hook is what gets drawn — it is guaranteed to render at >=12px cap-height
    with no truncation on every cover family.

    With no authored hook, fall back to deriving a lead phrase from the catalog
    subtitle (which carries the full SEO/positioning string, e.g.
    "The Overwhelm Response — Sleep Anxiety for Tech Finance Burnout (When ...)").
    At a 250px Amazon thumbnail only a short hook renders big enough to read
    (>=12px cap-height), so the derivation uses, in order: the text before the
    first em/en dash; minus any trailing "(...)"; then, if still too long, the
    first clause (before a comma/colon); then a word-boundary trim + ellipsis.
    The FULL subtitle still lives in the catalog/metadata — this only changes the
    drawn hook so the bigger subtitle never overruns the symbol/byline."""
    if short_hook and short_hook.strip():
        return short_hook.strip()
    if not subtitle:
        return subtitle
    s = subtitle.strip()
    for sep in (" — ", " – ", " - "):
        if sep in s:
            s = s.split(sep, 1)[0].strip()
            break
    s = re.sub(r"\s*\([^)]*\)\s*$", "", s).strip()
    if len(s) <= max_chars:
        return s or subtitle.strip()
    # still long -> first clause before a comma / colon
    for sep in (": ", ", "):
        if sep in s and len(s.split(sep, 1)[0].strip()) <= max_chars:
            return s.split(sep, 1)[0].strip()
    # last resort: trim to <= max_chars at a word boundary + ellipsis
    words, out = s.split(), ""
    for w in words:
        if len((out + " " + w).strip()) > max_chars - 1:
            break
        out = (out + " " + w).strip()
    return (out + "…") if out else s[:max_chars - 1].rstrip() + "…"


def author_fingerprint(author_id: str, family: str = "",
                       brand_id: str = "way_stream_sanctuary") -> dict:
    """Deterministic per-author cover signature -> {framing, plate}.

    Same author -> same look forever; different authors -> guaranteed-different
    framing (and varied plate on the light-paper families). `family` lets us
    force the plate on the subtitle-over-dark families."""
    h = hashlib.sha256(f"{brand_id}|{author_id}".encode()).digest()
    framing = FRAMING_TREATMENTS[h[8] % len(FRAMING_TREATMENTS)]
    if family in _DARK_SUBTITLE_FAMILIES:
        plate = True                    # darkest fields: always plate
    else:
        plate = bool(h[9] & 1)          # light-paper families: deterministic coin-flip
    return {"framing": framing, "plate": plate}


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
    card_fam = card["family"]
    fam = render_family(card_fam, row["book_id"])
    layout_var = layout_variant_for_book(row["book_id"])
    fp = author_fingerprint(aid, card_fam, cfg["brand"]["brand_id"])
    spec = Spec(
        title=(row["title"] or "").strip(),
        subtitle=(row["subtitle"] or "").strip(),
        author_display=row["author"], imprint=cfg["brand"]["imprint"],
        series_name=row["cluster"].strip().upper(), book_num=inst, count=inst,
        topic=row["topic"], motif=motif,
        serif=card["serif"], sans=card["sans"], title_case=card.get("title_case", "sentence"),
        deep=P.hex_rgb(card["deep"]), field=P.hex_rgb(card["field"]), accent=P.hex_rgb(card["accent"]),
        seed=seed_of(row["book_id"]), family=fam, layout_variant=layout_var,
        framing=fp["framing"], plate=fp["plate"],
    )
    img_path, pool_src = (None, None)
    if card_fam in cfg["image_families"]:
        img_path, pool_src = pick_pool_image(aid, card["track"], row["book_id"], allow_fallback)
    return spec, img_path, pool_src, aid
