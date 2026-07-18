"""Render covers for ANY brand, reusing the proven waystream_covers engine.

  PYTHONPATH=. python3 -m scripts.publish.brand_covers.render_brand --brand stillness_press --contact
  PYTHONPATH=. python3 -m scripts.publish.brand_covers.render_brand --brand stillness_press --all

Image-family authors use a FLUX pool at artifacts/covers/<brand>/author_pools/<aid>/
when present; without a pool they degrade to a gradient (so a proof renders with
zero GPU). Pools are generated separately by pools.py and reused across locales.
"""
from __future__ import annotations
import argparse
import hashlib
from pathlib import Path

import yaml
from PIL import Image, ImageDraw

from scripts.publish.waystream_covers import palette as P
from scripts.publish.waystream_covers import templates as T
from scripts.publish.waystream_covers.fonts import get_font
from . import assignment as A
from . import adapter as AD

ROOT = Path(__file__).resolve().parents[3]
DISPLAY_NAMES = ROOT / "config/catalog_planning/brand_display_names.yaml"


def _seed(s: str) -> int:
    return int(hashlib.sha1(s.encode()).hexdigest()[:8], 16)


def imprint_for(brand_id: str) -> str:
    try:
        data = yaml.safe_load(DISPLAY_NAMES.read_text())

        def find(o):
            if isinstance(o, dict):
                if brand_id in o:
                    v = o[brand_id]
                    if isinstance(v, str):
                        return v
                    if isinstance(v, dict):
                        return v.get("display") or v.get("imprint") or v.get("name")
                for v in o.values():
                    r = find(v)
                    if r:
                        return r
            return None
        r = find(data)
        if r:
            return str(r).upper()
    except Exception:
        pass
    return brand_id.replace("_", " ").upper()


def pool_image(brand_id, author_id, book_id, family):
    if family not in A.IMAGE_FAMILIES:
        return None
    d = ROOT / f"artifacts/covers/{brand_id}/author_pools/{author_id}"
    imgs = sorted(d.glob("*.png")) if d.exists() else []
    if not imgs:
        return None
    return Image.open(imgs[_seed(book_id) % len(imgs)]).convert("RGB")


def spec_for(row, card, imprint):
    return T.Spec(
        title=row["title"] or "Untitled", subtitle=row["subtitle"] or "",
        author_display=card["display"], imprint=imprint,
        series_name=row["series_name"], book_num=row["installment"], count=row["installment"],
        topic=row["topic"], motif=A.topic_motif(row["topic"]),
        serif=card["serif"], sans=card["sans"], title_case=card["title_case"],
        deep=P.hex_rgb(card["deep"]), field=P.hex_rgb(card["field"]), accent=P.hex_rgb(card["accent"]),
        seed=_seed(row["book_id"]), family=card["family"],
    )


def render_one(brand_id, row, card, imprint, out: Path):
    img = pool_image(brand_id, row["author_id"], row["book_id"], card["family"])
    cover = T.render(spec_for(row, card, imprint), img)
    out.parent.mkdir(parents=True, exist_ok=True)
    cover.save(out)
    return out


def contact(brand_id, rows, cards, imprint, out_path: Path, cols=4, thumb_w=420):
    by_author = {}
    for r in rows:
        by_author.setdefault(r["author_id"], r)   # one representative per author
    items = []
    for aid, r in by_author.items():
        out = ROOT / f"artifacts/covers/{brand_id}/proof/{r['book_id']}.png"
        render_one(brand_id, r, cards[aid], imprint, out)
        items.append((r, cards[aid], out))

    th_w, th_h = thumb_w, int(thumb_w * 1.6)
    pad, lab, head = 24, 96, 84
    cols = min(cols, max(1, len(items)))
    rows_n = (len(items) + cols - 1) // cols
    Wd = cols * th_w + (cols + 1) * pad
    Hs = head + rows_n * (th_h + lab + pad) + pad
    sheet = Image.new("RGB", (Wd, Hs), (24, 24, 27))
    dr = ImageDraw.Draw(sheet)
    dr.text((pad, 26), f"{imprint} — cover system proof (en_US)", font=get_font("Avenir Next", "bold", 36), fill=(238, 233, 225))
    lf = get_font("Avenir Next", "demibold", 22)
    sf = get_font("Avenir Next", "regular", 19)
    for i, (r, card, out) in enumerate(items):
        rr, cc = divmod(i, cols)
        x = pad + cc * (th_w + pad)
        y = head + rr * (th_h + lab + pad)
        sheet.paste(Image.open(out).convert("RGB").resize((th_w, th_h), Image.LANCZOS), (x, y))
        dr.text((x, y + th_h + 8), card["display"], font=lf, fill=(232, 196, 120))
        dr.text((x, y + th_h + 38), f'{card["family"]} · {r["topic"]} · BK{r["installment"]}', font=sf, fill=(214, 210, 202))
        dr.text((x, y + th_h + 64), f'{card["serif"]} / {card["sans"]}', font=sf, fill=(150, 150, 156))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path)
    return out_path, items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brand", required=True)
    ap.add_argument("--contact", action="store_true")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()

    rows = AD.rows_for_brand(args.brand)
    if not rows:
        print(f"no book_plans for {args.brand}")
        return
    author_ids = sorted({r["author_id"] for r in rows})
    cards = {aid: A.assign_author(args.brand, aid) for aid in author_ids}
    imprint = imprint_for(args.brand)
    print(f"{args.brand}: {len(rows)} books · {len(author_ids)} authors · imprint={imprint}")
    print("ASSIGNMENT (author -> family / serif / sans / palette):")
    for aid in author_ids:
        c = cards[aid]
        img = "IMG" if c["family"] in A.IMAGE_FAMILIES else "   "
        print(f"  [{img}] {c['display']:<18} {c['family']:<14} {c['serif']:<16} {c['sans']:<14} {c['deep']}")

    if args.all:
        for r in rows:
            render_one(args.brand, r, cards[r["author_id"]], imprint, ROOT / f"artifacts/covers/{args.brand}/all/{r['book_id']}.png")
        print(f"rendered {len(rows)} covers -> artifacts/covers/{args.brand}/all/")
    else:
        out, items = contact(args.brand, rows, cards, imprint, ROOT / f"artifacts/covers/{args.brand}/contact_sheet_en_US.png")
        print(f"CONTACT SHEET ({len(items)} distinct authors): {out}")


if __name__ == "__main__":
    main()
