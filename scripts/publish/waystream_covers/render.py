"""Render Waystream covers + build proof contact sheets.

  python3 -m scripts.publish.waystream_covers.render --proof
  python3 -m scripts.publish.waystream_covers.render --variation "Cole Bennett" anxiety
  python3 -m scripts.publish.waystream_covers.render --all          # 800 (needs pools)
  python3 -m scripts.publish.waystream_covers.render --book <book_id>
"""
from __future__ import annotations
import argparse
from pathlib import Path

from PIL import Image, ImageDraw

from . import assign as A
from . import templates as T
from .fonts import get_font

OUT = A.ROOT / "artifacts/waystream/covers"

# proof plan: (author_display, topic, target_installment) — one per family x track,
# spread across topics + book numbers 1..7.
PROOF_PLAN = [
    ("Lena Frost", "anxiety", 1),          ("Sam Meridian", "grief", 7),
    ("Daniel Cho", "sleep_anxiety", 3),    ("Jonah Kim", "boundaries", 5),
    ("Theo Castellan", "burnout", 2),      ("Nina Vazquez", "courage", 6),
    ("Ravi Chandra", "overthinking", 4),   ("Oscar Bello", "self_worth", 3),
    ("Mara Okonkwo", "social_anxiety", 5), ("Grace Adeyemi", "depression", 2),
    ("Devon Hale", "courage", 7),          ("Ana Reyes", "imposter_syndrome", 1),
    ("Elena Petrova", "overthinking", 4),  ("Marcus Reed", "financial_anxiety", 6),
    ("Cole Bennett", "anxiety", 5),        ("Hannah Stern", "somatic_healing", 3),
]


def find_row(catalog, author, topic=None, installment=None):
    rows = [r for r in catalog if r["author"] == author]
    if topic:
        rows = [r for r in rows if r["topic"] == topic] or rows
    if installment is not None and rows:
        rows.sort(key=lambda r: abs(int(r["installment"]) - installment))
    return rows[0] if rows else None


def render_row(cfg, row, out_path, allow_fallback=True):
    spec, img_path, pool_src, aid = A.spec_from_row(cfg, row, allow_fallback)
    image = Image.open(img_path).convert("RGB") if img_path else None
    cover = T.render(spec, image)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cover.save(out_path)
    return {"book_id": row["book_id"], "author": row["author"], "author_id": aid,
            "family": spec.family, "topic": row["topic"], "book_num": spec.book_num,
            "pool_src": pool_src, "out": out_path}


def contact_sheet(items, out_path, cols=4, thumb_w=440, title="WAYSTREAM SANCTUARY — cover system proof"):
    th_w, th_h = thumb_w, int(thumb_w * 1.6)
    pad, lab = 26, 96
    rows = (len(items) + cols - 1) // cols
    head = 80
    W = cols * th_w + (cols + 1) * pad
    Hs = head + rows * (th_h + lab + pad) + pad
    sheet = Image.new("RGB", (W, Hs), (24, 24, 27))
    dr = ImageDraw.Draw(sheet)
    hf = get_font("Avenir Next", "bold", 38)
    dr.text((pad, 24), title, font=hf, fill=(238, 233, 225))
    lf = get_font("Avenir Next", "demibold", 23)
    sf = get_font("Avenir Next", "regular", 21)
    for i, it in enumerate(items):
        r, c = divmod(i, cols)
        x = pad + c * (th_w + pad)
        y = head + r * (th_h + lab + pad)
        thumb = Image.open(it["out"]).convert("RGB").resize((th_w, th_h), Image.LANCZOS)
        sheet.paste(thumb, (x, y))
        l1 = f'{it["family"]}'
        l2 = f'{it["author"]} · {it["topic"]} · BK {it["book_num"]}'
        l3 = f'img: {it["pool_src"]}' if it.get("pool_src") and it["pool_src"] != it["author_id"] else ("no-image" if not it.get("pool_src") else "own pool")
        dr.text((x, y + th_h + 8), l1, font=lf, fill=(232, 196, 120))
        dr.text((x, y + th_h + 40), l2, font=sf, fill=(214, 210, 202))
        dr.text((x, y + th_h + 66), l3, font=sf, fill=(150, 150, 156))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path)
    return out_path


def cmd_proof(cfg, catalog):
    items = []
    for author, topic, inst in PROOF_PLAN:
        row = find_row(catalog, author, topic, inst)
        if not row:
            print(f"  ! no row for {author}/{topic}"); continue
        out = OUT / "proof" / f'{row["book_id"]}.png'
        it = render_row(cfg, row, out)
        items.append(it)
        print(f'  {it["family"]:<14} {author:<16} {topic:<18} BK{it["book_num"]}  img={it["pool_src"]}')
    sheet = contact_sheet(items, OUT / "proof_contact_sheet.png", cols=4)
    print(f"\nCONTACT SHEET: {sheet}")
    return sheet


def cmd_variation(cfg, catalog, author, topic):
    import collections
    pool = [r for r in catalog if r["author"] == author and r["topic"] == topic]
    by_series = collections.defaultdict(list)
    for r in pool:
        by_series[r["series_id"]].append(r)
    # pick the single series with the most installments -> clean 1..N count demo
    best = max(by_series.values(), key=len) if by_series else []
    rows = sorted(best, key=lambda r: int(r["installment"]))
    items = []
    for row in rows[:7]:
        out = OUT / "variation" / f'{row["book_id"]}.png'
        items.append(render_row(cfg, row, out))
    sheet = contact_sheet(items, OUT / "variation_contact_sheet.png", cols=len(items) or 1,
                          title=f"PER-BOOK VARIATION — {author} · {topic} · books 1..{len(items)}")
    print(f"VARIATION SHEET: {sheet}")
    return sheet


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--proof", action="store_true")
    ap.add_argument("--variation", nargs=2, metavar=("AUTHOR", "TOPIC"))
    ap.add_argument("--book", metavar="BOOK_ID")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--no-fallback", action="store_true", help="skip covers whose author has no real pool")
    args = ap.parse_args()
    cfg = A.load_cfg()
    catalog = A.load_catalog()

    if args.book:
        row = next((r for r in catalog if r["book_id"] == args.book), None)
        if not row:
            print("book_id not found"); return
        it = render_row(cfg, row, OUT / "single" / f"{args.book}.png", not args.no_fallback)
        print(it["out"]); return
    if args.variation:
        cmd_variation(cfg, catalog, *args.variation); return
    if args.all:
        import collections
        fam = collections.Counter()
        for i, row in enumerate(catalog):
            it = render_row(cfg, row, OUT / "all" / f'{row["book_id"]}.png', not args.no_fallback)
            fam[it["family"]] += 1
            if (i + 1) % 50 == 0:
                print(f"  {i+1}/{len(catalog)}")
        print("DONE", dict(fam)); return
    # default: proof
    cmd_proof(cfg, catalog)


if __name__ == "__main__":
    main()
