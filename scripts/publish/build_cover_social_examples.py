#!/usr/bin/env python3
"""Deterministic cover/social EXAMPLE builder — image-aware type placement proof.

WHAT THIS IS
------------
A NON-PRODUCTION proof layer. It renders one cover and one or more platform
social examples per topic from `config/publishing/waystream_cover_social_recipes.yaml`,
placing type according to what is actually in the photograph underneath
(`waystream_covers/image_placement.py`).

WHAT THIS IS NOT
----------------
- Not a production cover build. The production path is
  `scripts/publish/waystream_covers/render.py` + `assign.py`; this script does
  not import, modify, or replace it.
- Not a license approval. Every example is stamped NOT_PRODUCTION_APPROVED and
  every manifest row carries the source's real `license_status`.
- Not an image generator of record. Type is composited over an EXISTING curated
  photo or over the repo's existing abstract cover renderer. The image layer
  never contains baked text (two-stage doctrine).

SOURCE RESOLUTION (deterministic, honest)
-----------------------------------------
1. Curated row from artifacts/curation/waystream_image_winners_20260715/, ranked
   license_status=verified first, then cover_score desc, then asset_id. Marked
   `curated_pending_license`.
2. Otherwise a deterministic abstract background from the existing
   `abstract_cover_art.build_background()`. Marked `abstract_generated_placeholder`.
   License-clean and face/logo-free by construction.
3. `--uncurated-bank` opts into the raw local bank instead. OFF by default: the
   sorted-order pick is blind to image content and has already selected a
   recognizable face beside alcohol bottles (`burnout`) and an identifiable
   firefighter in a live emergency scene (`healing`) — both excluded by the plan
   doc's own face/sensitive-topic gates. See the handoff for the full finding.

Only 6 of 12 topics have curated imagery today (anxiety, boundaries, grief,
loneliness, overthinking, hope). The other 6 render abstract. That gap is the
honest state, not a defect of this script.

USAGE
    # smoke (2 topics), pilot (4, incl. busy + sky), scale (all 12)
    python3 scripts/publish/build_cover_social_examples.py --ramp smoke
    python3 scripts/publish/build_cover_social_examples.py --ramp pilot
    python3 scripts/publish/build_cover_social_examples.py --ramp scale
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts.publish import abstract_cover_art as ACA  # noqa: E402
from scripts.publish.waystream_covers import image_placement as IP  # noqa: E402
from scripts.publish.waystream_covers import symbols as S  # noqa: E402
from scripts.publish.waystream_covers.fonts import get_font  # noqa: E402

REGISTRY = REPO_ROOT / "config/publishing/waystream_cover_social_recipes.yaml"
CURATION = REPO_ROOT / "artifacts/curation/waystream_image_winners_20260715"
BANK = "artifacts/stock_image_bank/way_stream_sanctuary/mental_health_editorial_100x/downloads"

NOT_APPROVED = "NOT_PRODUCTION_APPROVED"

# Smoke: one quiet + one busy topic. Pilot adds an explicit busy/negative-space pair.
SMOKE_TOPICS = ("overthinking", "hope")
PILOT_TOPICS = ("overthinking", "hope", "anxiety", "loneliness")

COVER_SIZE = (1600, 2560)

PLATFORM_FORMATS = {
    "instagram_feed_4x5": {"size": (1080, 1350), "style": "feed", "label": "IG / FB feed"},
    "story_reel_short_9x16": {"size": (1080, 1920), "style": "steps", "label": "Stories / Reels / Shorts"},
    "pinterest_pin_2x3": {"size": (1000, 1500), "style": "pin", "label": "Pinterest pin"},
    "linkedin_landscape_1_91x1": {"size": (1200, 627), "style": "linkedin", "label": "LinkedIn landscape"},
    "square_1x1": {"size": (1080, 1080), "style": "square", "label": "Square"},
}
DEFAULT_SOCIAL = "instagram_feed_4x5"

SERIF = "playfair"
SANS = "inter"


# --------------------------------------------------------------------------- #
# source resolution
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Source:
    topic: str
    path: Path | None          # None => abstract generated background
    asset_id: str
    provider: str
    source_url: str | None
    license_status: str
    image_status: str
    attribution_text: str | None
    metaphor: str | None
    abstract: bool = False


def _load_curated() -> dict[str, list[dict]]:
    draft = CURATION / "curated_winners_draft.json"
    ledger = CURATION / "license_verification_ledger.json"
    if not draft.exists():
        return {}
    rows = json.loads(draft.read_text())["candidates"]
    status: dict[str, str] = {}
    if ledger.exists():
        for r in json.loads(ledger.read_text())["rows"]:
            status[r["asset_id"]] = r.get("license_status", "unknown")
    by_topic: dict[str, list[dict]] = {}
    for r in rows:
        r = dict(r)
        r["_license_status"] = status.get(r["asset_id"], r.get("license_status", "unknown"))
        by_topic.setdefault(r["topic"], []).append(r)
    for topic, lst in by_topic.items():
        # verified first, then strongest cover score, then id — fully deterministic
        lst.sort(key=lambda r: (r["_license_status"] != "verified", -(r.get("cover_score") or 0), r["asset_id"]))
    return by_topic


def _bank_pick(topic: str, source_root: Path) -> Path | None:
    """Deterministic raw-bank fallback: first file in sorted order for the topic."""
    root = source_root / BANK
    if not root.exists():
        return None
    hits: list[Path] = []
    for provider_dir in sorted(root.iterdir()):
        tdir = provider_dir / topic
        if tdir.is_dir():
            hits.extend(sorted(p for p in tdir.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"}))
    return hits[0] if hits else None


def resolve_source(
    topic: str, curated: dict[str, list[dict]], source_root: Path, *, allow_bank: bool = False,
) -> Source | None:
    """curated -> (opt-in) raw bank -> abstract generated background.

    The raw-bank fallback is OPT-IN and defaults OFF on purpose. "First file in
    sorted order" has no idea what is in the photograph: on the 2026-07-15 scale
    run it selected a recognizable face beside alcohol bottles for `burnout` and
    an identifiable firefighter in a live emergency scene for `healing` — both
    excluded by this registry's own `avoid` lists and by the plan doc's face /
    sensitive-topic gates. An unreviewed photo is not a safe default; a
    deterministic abstract background is.
    """
    for row in curated.get(topic, []):
        p = source_root / row["local_path"]
        if p.exists():
            return Source(
                topic=topic, path=p, asset_id=row["asset_id"], provider=row.get("provider", "unknown"),
                source_url=row.get("source_url"), license_status=row["_license_status"],
                image_status="curated_pending_license", attribution_text=row.get("attribution_text"),
                metaphor=row.get("metaphor"),
            )

    if allow_bank:
        p = _bank_pick(topic, source_root)
        if p is not None:
            return Source(
                topic=topic, path=p, asset_id=f"uncurated_{topic}_{p.stem}",
                provider=p.parent.parent.name, source_url=None,
                license_status="pending_source_page_verification",
                image_status="uncurated_bank_placeholder_UNREVIEWED_FACE_LOGO_RISK",
                attribution_text=None, metaphor=None,
            )

    return Source(
        topic=topic, path=None, asset_id=f"abstract_{topic}", provider="phoenix_abstract_cover_art",
        source_url=None, license_status="not_applicable_generated_in_repo",
        image_status="abstract_generated_placeholder", attribution_text=None,
        metaphor=None, abstract=True,
    )


_ABSTRACT_CACHE: dict[str, Image.Image] = {}


def _rgb_hex(rgb) -> str:
    return "#%02x%02x%02x" % tuple(rgb)


def load_base(src: Source, rec: dict, size: tuple[int, int]) -> Image.Image:
    """The image layer, cropped to `size`. Never contains text (two-stage doctrine)."""
    if not src.abstract:
        return cover_crop(Image.open(src.path), size)
    if src.topic not in _ABSTRACT_CACHE:
        # Reuse the existing abstract cover renderer rather than inventing a
        # second gradient engine.
        bg, _meta = ACA.build_background(
            src.topic,
            primary_hex=_rgb_hex(rec["accent"]),
            secondary_hex=_rgb_hex(rec["scrim"]),
            accent_hex=_rgb_hex(rec["accent"]),
            author_id="waystream_recipe_proof",
            brand_id="way_stream_sanctuary",
        )
        _ABSTRACT_CACHE[src.topic] = bg.convert("RGB")
    return cover_crop(_ABSTRACT_CACHE[src.topic], size)


# --------------------------------------------------------------------------- #
# drawing helpers
# --------------------------------------------------------------------------- #
def cover_crop(src: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Deterministic center crop to target ratio (no metaphor-destroying zoom)."""
    src = src.convert("RGB")
    sw, sh = src.size
    tw, th = size
    scale = max(tw / sw, th / sh)
    nw, nh = math.ceil(sw * scale), math.ceil(sh * scale)
    r = src.resize((nw, nh), Image.Resampling.LANCZOS)
    x, y = (nw - tw) // 2, (nh - th) // 2
    return r.crop((x, y, x + tw, y + th))


def grade(img: Image.Image) -> Image.Image:
    """Uniform muted grade. Deliberately does NOT darken a chosen band — the
    placement engine must see the real photograph, not a grade we imposed."""
    out = ImageEnhance.Color(img).enhance(0.82)
    return ImageEnhance.Contrast(out).enhance(1.06)


def wrap(draw, text, font, maxw) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_text(draw, text, family, weight, maxw, max_lines, start_px, min_px):
    for px in range(start_px, min_px - 1, -2):
        f = get_font(family, weight, px)
        lines = wrap(draw, text, f, maxw)
        if len(lines) <= max_lines and all(draw.textlength(l, font=f) <= maxw for l in lines):
            return f, lines, px
    f = get_font(family, weight, min_px)
    return f, wrap(draw, text, f, maxw)[:max_lines], min_px


def line_h(font) -> int:
    a, d = font.getmetrics()
    return a + d


def block_h_for(lines, font, spacing=1.08) -> int:
    return int(len(lines) * line_h(font) * spacing)


def draw_lines(draw, xy, lines, font, fill, spacing=1.08) -> int:
    x, y = xy
    lh = int(line_h(font) * spacing)
    for l in lines:
        draw.text((x, y), l, font=font, fill=fill)
        y += lh
    return y


def draw_backing(canvas: Image.Image, box, treatment: str, scrim_rgb, radius: int = 18) -> None:
    """Protect type from a busy/mid-busy photo. Never called on a quiet band."""
    if treatment == IP.TREATMENT_PLAIN:
        return
    x0, y0, x1, y1 = box
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    if treatment == IP.TREATMENT_BOX:
        # Opaque inset card: reads as an intentional object on a busy photo.
        d.rounded_rectangle((x0, y0, x1, y1), radius=radius, fill=(*scrim_rgb, 232))
    else:
        # Scrim: FULL-BLEED vertical gradient band. An inset gradient reads as a
        # smudge floating on the photo; edge-to-edge reads as deliberate grading.
        h = max(1, int(y1 - y0))
        for i in range(h):
            t = i / h
            a = int(196 * (1 - abs(2 * t - 1) ** 1.7))
            d.rectangle((0, y0 + i, canvas.width, y0 + i + 1), fill=(*scrim_rgb, a))
        layer = layer.filter(ImageFilter.GaussianBlur(9))
    canvas.alpha_composite(layer)


def stamp_not_approved(canvas: Image.Image, w: int, h: int) -> None:
    """Every example carries its own status. A screenshot must not be able to
    escape the label."""
    d = ImageDraw.Draw(canvas)
    px = max(14, int(w * 0.019))
    f = get_font(SANS, "bold", px)
    pad = max(8, int(w * 0.010))
    tw = d.textlength(NOT_APPROVED, font=f)
    th = line_h(f)
    x1, y1 = w - pad, h - pad
    x0, y0 = x1 - tw - pad * 1.6, y1 - th - pad * 0.9
    d.rounded_rectangle((x0, y0, x1, y1), radius=5, fill=(150, 30, 30, 236))
    d.text((x0 + pad * 0.8, y0 + pad * 0.35), NOT_APPROVED, font=f, fill=(255, 240, 240))


# --------------------------------------------------------------------------- #
# renderers
# --------------------------------------------------------------------------- #
def render_cover(rec: dict, src: Source, out: Path, defaults: dict) -> dict:
    w, h = COVER_SIZE
    canvas = grade(load_base(src, rec, COVER_SIZE)).convert("RGBA")
    draw = ImageDraw.Draw(canvas)
    margin = int(w * 0.089)
    maxw = w - margin * 2
    cream = tuple(defaults["cream"])
    accent = tuple(rec["accent"])
    scrim = tuple(rec["scrim"])

    tf, tlines, tpx = fit_text(draw, rec["title"].upper(), SERIF, "bold", maxw, 3, 150, 92)
    sf, slines, spx = fit_text(draw, rec["subtitle"], SANS, "regular", maxw, 3, 58, IP.min_font_px_for_thumbnail(w))
    t_h, s_h = block_h_for(tlines, tf), block_h_for(slines, sf)
    imprint_f = get_font(SANS, "bold", 30)
    # imprint + title + subtitle + rule + symbol travel together as ONE block, so
    # the symbol inherits the same protection (and the same quiet band) as the
    # type. A motif dropped loose on the photo reads as a defect, not support.
    rule_h, sym_h = 24, 58
    unit_h = int(45 + t_h + 34 + s_h + rule_h + sym_h)

    # --- the image decides where the type goes ---
    place = IP.choose_placement(
        canvas.convert("RGB"), block_h=unit_h / h, cream=cream,
        step=0.03, margin=0.045, prefer=None,
    )
    y = int(place.band.y0 * h)
    ink = place.ink
    sub_ink = ink if place.treatment == IP.TREATMENT_PLAIN else (238, 234, 221)

    pad = int(w * 0.030)
    draw_backing(canvas, (margin - pad, y - pad, w - margin + pad, y + unit_h + pad),
                 place.treatment, scrim)

    draw.text((margin, y), defaults["imprint"], font=imprint_f, fill=accent)
    y += 45
    y = draw_lines(draw, (margin, y), tlines, tf, ink)
    y += 34
    y = draw_lines(draw, (margin, y), slines, sf, sub_ink)
    draw.rounded_rectangle((margin, y + 14, margin + 300, y + 24), radius=5, fill=accent)
    y += rule_h

    # Symbol support: reuse the production motif vocabulary (symbols.py MOTIF_FN),
    # anchored under the rule inside the protected block. Deterministic seed —
    # same topic always yields the same cluster.
    S.draw_symbol_set(
        canvas, rec["symbol"],
        (margin, y + 6, margin + 210, y + sym_h - 6),
        3, accent, seed=sum(src.topic.encode()), orientation="row",
    )

    byline_y = h - int(h * 0.055)
    draw.text((margin, byline_y), defaults["byline"], font=get_font(SANS, "bold", 42), fill=cream)
    stamp_not_approved(canvas, w, h)

    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(out, quality=92, optimize=True)
    return {
        "path": str(out.relative_to(REPO_ROOT)), "kind": "cover", "size": list(COVER_SIZE),
        "placement": place.as_dict(), "title_px": tpx, "subtitle_px": spx,
        "subtitle_thumbnail_ok": IP.thumbnail_ok(spx, w),
        "subtitle_thumb_cap_px": round(IP.thumb_cap_px(spx, w), 2),
    }


def render_social(rec: dict, src: Source, fmt_name: str, out: Path, defaults: dict) -> dict:
    spec = PLATFORM_FORMATS[fmt_name]
    w, h = spec["size"]
    style = spec["style"]
    canvas = grade(load_base(src, rec, (w, h))).convert("RGBA")
    draw = ImageDraw.Draw(canvas)
    margin = max(48, int(w * 0.072))
    maxw = w - margin * 2
    cream = tuple(defaults["cream"])
    accent = tuple(rec["accent"])
    scrim = tuple(rec["scrim"])

    headline = {"pin": rec["pin_title"], "linkedin": rec["linkedin_angle"]}.get(style, rec["social_hook"])
    body_maxw = int(w * 0.56) if style == "linkedin" else maxw
    hf, hlines, hpx = fit_text(draw, headline, SERIF, "bold", body_maxw, 5,
                               max(34, int(w * 0.082)), max(24, int(w * 0.044)))
    h_h = block_h_for(hlines, hf)

    extras: list[str] = []
    if style in ("steps", "pin"):
        extras = list(rec["micro_steps"])
    elif style in ("feed", "linkedin"):
        extras = [rec["social_body"]]
    bf = get_font(SANS, "regular", max(22, int(w * 0.034)))
    elines: list[str] = []
    for e in extras:
        elines.extend(wrap(draw, ("+ " + e) if style in ("steps", "pin") else e, bf, body_maxw))
    e_h = block_h_for(elines, bf) if elines else 0
    label_h = int(h * 0.055)
    unit_h = label_h + h_h + (28 + e_h if e_h else 0)

    place = IP.choose_placement(canvas.convert("RGB"), block_h=min(0.92, unit_h / h),
                               cream=cream, step=0.03, margin=0.04)
    y = int(place.band.y0 * h)
    ink = place.ink
    body_ink = ink if place.treatment == IP.TREATMENT_PLAIN else (238, 234, 221)

    pad = int(w * 0.035)
    draw_backing(canvas, (margin - pad, y - pad, w - margin + pad, y + unit_h + pad),
                 place.treatment, scrim, radius=14)

    lf = get_font(SANS, "bold", max(18, int(w * 0.026)))
    draw.text((margin, y), f"{src.topic.upper()}  /  {spec['label'].upper()}", font=lf, fill=accent)
    y += label_h
    y = draw_lines(draw, (margin, y), hlines, hf, ink)
    if elines:
        y += 28
        draw_lines(draw, (margin, y), elines, bf, body_ink)

    ff = get_font(SANS, "regular", max(18, int(w * 0.024)))
    fw = draw.textlength(defaults["footer"], font=ff)
    draw.text((w - margin - fw, h - margin), defaults["footer"], font=ff, fill=(230, 226, 213))
    stamp_not_approved(canvas, w, h)

    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(out, quality=92, optimize=True)
    return {
        "path": str(out.relative_to(REPO_ROOT)), "kind": f"social:{fmt_name}", "size": [w, h],
        "placement": place.as_dict(), "headline_px": hpx,
        "headline_thumbnail_ok": IP.thumbnail_ok(hpx, w),
        "headline_thumb_cap_px": round(IP.thumb_cap_px(hpx, w), 2),
    }


def contact_sheet(paths: list[Path], out: Path, cols: int, cell: tuple[int, int]) -> Path:
    rows = math.ceil(len(paths) / cols)
    label_h = 40
    sheet = Image.new("RGB", (cols * cell[0], rows * (cell[1] + label_h)), (22, 22, 24))
    d = ImageDraw.Draw(sheet)
    f = get_font(SANS, "regular", 20)
    for i, p in enumerate(paths):
        im = Image.open(p).convert("RGB")
        im.thumbnail(cell, Image.Resampling.LANCZOS)
        cx, cy = (i % cols) * cell[0], (i // cols) * (cell[1] + label_h)
        sheet.paste(im, (cx + (cell[0] - im.width) // 2, cy))
        d.text((cx + 10, cy + cell[1] + 10), p.stem.replace("waystream_", "")[:34], font=f, fill=(228, 228, 228))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, quality=88, optimize=True)
    return out


# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ramp", choices=("smoke", "pilot", "scale"), default="smoke")
    ap.add_argument("--topics", nargs="*", help="explicit topic list (overrides --ramp)")
    ap.add_argument("--out", type=Path, default=CURATION / "examples_v2")
    ap.add_argument("--uncurated-bank", action="store_true",
                    help="allow the UNREVIEWED raw-bank fallback for topics with no curated row "
                         "(carries face/logo/sensitive-topic risk; default: abstract background)")
    ap.add_argument("--source-root", type=Path, default=REPO_ROOT,
                    help="root holding the untracked local image bank (default: repo root)")
    args = ap.parse_args()

    reg = yaml.safe_load(REGISTRY.read_text())
    defaults, topics_cfg = reg["defaults"], reg["topics"]

    if args.topics:
        topics = list(args.topics)
    elif args.ramp == "smoke":
        topics = list(SMOKE_TOPICS)
    elif args.ramp == "pilot":
        topics = list(PILOT_TOPICS)
    else:
        topics = sorted(topics_cfg)

    unknown = [t for t in topics if t not in topics_cfg]
    if unknown:
        print(f"ERROR: not in registry: {unknown}", file=sys.stderr)
        return 2

    curated = _load_curated()
    out_root: Path = args.out
    rendered: list[dict] = []
    missing: list[str] = []
    cover_paths: list[Path] = []
    social_paths: list[Path] = []

    for topic in topics:
        rec = topics_cfg[topic]
        src = resolve_source(topic, curated, args.source_root, allow_bank=args.uncurated_bank)
        if src is None:
            missing.append(topic)
            print(f"  {topic:14s} NO SOURCE IMAGE (bank absent) — skipped", file=sys.stderr)
            continue

        cov = render_cover(rec, src, out_root / "covers" / f"waystream_{topic}_cover.jpg", defaults)
        cover_paths.append(REPO_ROOT / cov["path"])

        fmts = list(PLATFORM_FORMATS) if (args.ramp == "pilot" and topic in PILOT_TOPICS) else [DEFAULT_SOCIAL]
        socs = []
        for fmt in fmts:
            s = render_social(rec, src, fmt, out_root / "social" / fmt / f"waystream_{topic}_{fmt}.jpg", defaults)
            socs.append(s)
            if fmt == DEFAULT_SOCIAL:
                social_paths.append(REPO_ROOT / s["path"])

        prov = {
            "asset_id": src.asset_id, "provider": src.provider, "source_url": src.source_url,
            "local_path": (str(src.path.relative_to(args.source_root))
                           if src.path and src.path.is_relative_to(args.source_root)
                           else (str(src.path) if src.path else None)),
            "license_status": src.license_status, "image_status": src.image_status,
            "attribution_text": src.attribution_text, "metaphor": src.metaphor,
        }
        rendered.append({
            "topic": topic, "plan_status": rec["plan_status"], "symbol": rec["symbol"],
            "approval": NOT_APPROVED, "source": prov, "cover": cov, "social": socs,
        })
        t = cov["placement"]
        print(f"  {topic:14s} {src.image_status:26s} title_band=y{t['band']['y0']:.2f} "
              f"{t['treatment']:11s} var={t['band']['variance']:6.0f} edge={t['band']['edge']:5.1f}")

    if not rendered:
        print("\nERROR: nothing rendered — local image bank is absent.\n"
              f"  expected under: {args.source_root / BANK}\n"
              "  The bank is local-only provenance and is not tracked in git.", file=sys.stderr)
        return 1

    sheets = []
    if len(cover_paths) > 1:
        sheets.append(contact_sheet(cover_paths, out_root / "contact_sheet_covers.jpg", 4, (360, 576)))
    if len(social_paths) > 1:
        sheets.append(contact_sheet(social_paths, out_root / "contact_sheet_social.jpg", 4, (360, 450)))

    n_box = sum(1 for r in rendered if r["cover"]["placement"]["treatment"] == IP.TREATMENT_BOX)
    n_plain = sum(1 for r in rendered if r["cover"]["placement"]["treatment"] == IP.TREATMENT_PLAIN)
    n_scrim = sum(1 for r in rendered if r["cover"]["placement"]["treatment"] == IP.TREATMENT_SCRIM)

    manifest = {
        "schema_version": 1,
        "status": NOT_APPROVED,
        "production_ready_count": 0,
        "ramp": args.ramp,
        "registry": str(REGISTRY.relative_to(REPO_ROOT)),
        "determinism": {
            "source_rule": "curated verified-first by cover_score then asset_id; else first raw-bank file in sorted order",
            "crop_rule": "center crop to target ratio, LANCZOS",
            "placement_rule": "quietest candidate band by (variance/BUSY_VAR + edge/BUSY_EDGE) on a 220px greyscale downsample",
            "treatment_rule": "quiet->plain, mid->scrim, busy->backing_box (thresholds imported from templates.py)",
            "type_rule": "no baked text; PIL composites all type; subtitle floored at the thumbnail legibility rule",
        },
        "license_note": "No example is license-verified for production. Uncurated rows are raw-bank placeholders.",
        "topics_covered": len(rendered),
        "examples_rendered": sum(1 + len(r["social"]) for r in rendered),
        "treatment_mix": {"plain": n_plain, "scrim": n_scrim, "backing_box": n_box},
        "topics_missing_source": missing,
        "sheets": [str(s.relative_to(REPO_ROOT)) for s in sheets],
        "rows": rendered,
    }
    mp = out_root / "examples_manifest.json"
    mp.parent.mkdir(parents=True, exist_ok=True)
    mp.write_text(json.dumps(manifest, indent=2) + "\n")

    print(f"\n  topics={len(rendered)} examples={manifest['examples_rendered']} "
          f"treatments: plain={n_plain} scrim={n_scrim} box={n_box}")
    print(f"  manifest: {mp.relative_to(REPO_ROOT)}")
    print(f"  {NOT_APPROVED} — production_ready_count=0")
    if missing:
        print(f"  WARNING: no source image for: {missing}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
