"""Render Waystream covers + QC proof contact sheets.

  python3 -m scripts.publish.waystream_covers.render --qc-pilot
  python3 -m scripts.publish.waystream_covers.render --proof
  python3 -m scripts.publish.waystream_covers.render --sync-catalog --all --deploy
"""
from __future__ import annotations
import argparse
from pathlib import Path

from PIL import Image, ImageDraw

from . import assign as A
from . import templates as T
from .fonts import get_font

OUT = A.ROOT / "artifacts/waystream/covers"
SERVED = A.SERVED_COVERS
THUMB_W = 280

# Named offenders + variety sample (operator 2026-07-05 QC round 3)
QC_OFFENDER_IDS = [
    "way_stream_sanctuary__default_teacher__corporate_managers__burnout__grief",
    "way_stream_sanctuary__default_teacher__corporate_managers__burnout__overwhelm",
    "way_stream_sanctuary__default_teacher__corporate_managers__burnout__overwhelm__1hr",
    "way_stream_sanctuary__default_teacher__corporate_managers__burnout__watcher__1hr",
    "way_stream_sanctuary__default_teacher__corporate_managers__overthinking__watcher",
]

QC_SAMPLE_IDS = [
    "way_stream_sanctuary__default_teacher__corporate_managers__burnout__grief",
    "way_stream_sanctuary__default_teacher__corporate_managers__burnout__overwhelm",
    "way_stream_sanctuary__default_teacher__corporate_managers__burnout__watcher",
    "way_stream_sanctuary__default_teacher__corporate_managers__anxiety__false_alarm",
    "way_stream_sanctuary__default_teacher__corporate_managers__anxiety__overwhelm",
    "way_stream_sanctuary__default_teacher__tech_finance_burnout__burnout__grief",
    "way_stream_sanctuary__default_teacher__healthcare_rns__burnout__grief",
    "way_stream_sanctuary__default_teacher__gen_z_professionals__burnout__watcher__1hr",
    "way_stream_sanctuary__default_teacher__entrepreneurs__burnout__watcher__1hr",
    "way_stream_sanctuary__default_teacher__first_responders__overthinking__spiral",
    "way_stream_sanctuary__default_teacher__corporate_managers__depression__grief",
    "way_stream_sanctuary__default_teacher__corporate_managers__boundaries__shame",
    "way_stream_sanctuary__default_teacher__corporate_managers__courage__spiral",
    "way_stream_sanctuary__default_teacher__corporate_managers__sleep_anxiety__overwhelm",
]

PROOF_PLAN = [
    ("Lena Frost", "anxiety", 1), ("Sam Meridian", "grief", 7),
    ("Daniel Cho", "sleep_anxiety", 3), ("Jonah Kim", "boundaries", 5),
    ("Theo Castellan", "burnout", 2), ("Nina Vazquez", "courage", 6),
    ("Ravi Chandra", "overthinking", 4), ("Oscar Bello", "self_worth", 3),
    ("Mara Okonkwo", "social_anxiety", 5), ("Grace Adeyemi", "depression", 2),
    ("Devon Hale", "courage", 7), ("Ana Reyes", "imposter_syndrome", 1),
    ("Elena Petrova", "overthinking", 4), ("Marcus Reed", "financial_anxiety", 6),
    ("Cole Bennett", "anxiety", 5), ("Hannah Stern", "somatic_healing", 3),
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
    thumb_path = out_path.with_name(out_path.stem + "_thumb.png")
    thumb = cover.resize((THUMB_W, int(THUMB_W * cover.height / cover.width)), Image.LANCZOS)
    thumb.save(thumb_path)
    return {
        "book_id": row["book_id"], "author": row["author"], "author_id": aid,
        "family": spec.family, "layout_variant": spec.layout_variant,
        "topic": row["topic"], "book_num": spec.book_num,
        "plan_title": row.get("title", ""), "plan_subtitle": row.get("subtitle", ""),
        "title_case": spec.title_case,
        "drawn_title": T.LAST_TITLE_DRAWN, "drawn_subtitle": T.LAST_SUBTITLE_DRAWN,
        "overlap_report": dict(T.LAST_LAYOUT_REPORT),
        "pool_src": pool_src, "out": out_path, "thumb": thumb_path,
    }


def _text_match(plan: str, drawn: str, title_case: str = "sentence") -> bool:
    p, d = (plan or "").strip(), (drawn or "").strip()
    if p == d:
        return True
    if title_case in ("upper", "small_caps") and p.upper() == d:
        return True
    return False


def qc_contact_sheet(items, out_path, cols=2):
    """Full + thumbnail + plan vs drawn title/subtitle for look-approval."""
    full_w, thumb_w = 320, THUMB_W
    full_h, thumb_h = int(full_w * 1.6), int(thumb_w * 1.6)
    text_w = 520
    cell_w = full_w + thumb_w + text_w + 48
    pad, head = 20, 72
    rows_n = (len(items) + cols - 1) // cols
    sheet_h = head + rows_n * (max(full_h, thumb_h) + 200 + pad) + pad
    sheet_w = cols * cell_w + (cols + 1) * pad
    sheet = Image.new("RGB", (sheet_w, sheet_h), (24, 24, 27))
    dr = ImageDraw.Draw(sheet)
    hf = get_font("Avenir Next", "bold", 32)
    dr.text((pad, 18), "WAYSTREAM QC — plan text vs rendered (full + thumbnail)", font=hf, fill=(238, 233, 225))
    tf = get_font("Avenir Next", "regular", 17)
    bf = get_font("Avenir Next", "demibold", 18)
    ok_c, bad_c = (120, 200, 140), (220, 120, 110)
    for i, it in enumerate(items):
        r, c = divmod(i, cols)
        x = pad + c * (cell_w + pad)
        y = head + r * (max(full_h, thumb_h) + 200 + pad)
        full = Image.open(it["out"]).convert("RGB").resize((full_w, full_h), Image.LANCZOS)
        sheet.paste(full, (x, y))
        tx = x + full_w + 12
        ty = y + (full_h - thumb_h) // 2
        thumb = Image.open(it["thumb"]).convert("RGB")
        sheet.paste(thumb, (tx, ty))
        lx = tx + thumb_w + 16
        ly = y
        t_ok = _text_match(it["plan_title"], it["drawn_title"], it.get("title_case", "sentence"))
        s_ok = _text_match(it["plan_subtitle"], it["drawn_subtitle"])
        dr.text((lx, ly), f'{it["family"]} · {it["layout_variant"]}', font=bf, fill=(232, 196, 120))
        dr.text((lx, ly + 28), f'PLAN TITLE:', font=bf, fill=(180, 176, 168))
        dr.text((lx, ly + 50), (it["plan_title"] or "")[:70], font=tf, fill=(214, 210, 202))
        dr.text((lx, ly + 78), f'DRAWN: {"OK" if t_ok else "MISMATCH"}', font=bf, fill=ok_c if t_ok else bad_c)
        if not t_ok:
            dr.text((lx, ly + 100), (it["drawn_title"] or "")[:70], font=tf, fill=bad_c)
        dr.text((lx, ly + 130), f'PLAN SUB:', font=bf, fill=(180, 176, 168))
        dr.text((lx, ly + 152), (it["plan_subtitle"] or "")[:70], font=tf, fill=(214, 210, 202))
        dr.text((lx, ly + 180), f'DRAWN: {"OK" if s_ok else "MISMATCH"}', font=bf, fill=ok_c if s_ok else bad_c)
        if not s_ok:
            dr.text((lx, ly + 202), (it["drawn_subtitle"] or "")[:70], font=tf, fill=bad_c)
        ov = it.get("overlap_report") or {}
        ov_n = ov.get("overlap_count", "?")
        dr.text((lx, ly + 230), f'OVERLAPS: {ov_n} (required 0)', font=bf,
                fill=ok_c if ov_n == 0 else bad_c)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path)
    return out_path


def cmd_qc_pilot(cfg, catalog):
    seen = set()
    items = []
    mismatches = []
    for bid in QC_SAMPLE_IDS:
        if bid in seen:
            continue
        seen.add(bid)
        row = next((r for r in catalog if r["book_id"] == bid), None)
        if not row:
            continue
        out = OUT / "qc_pilot" / f"{bid}.png"
        it = render_row(cfg, row, out)
        items.append(it)
        t_ok = _text_match(it["plan_title"], it["drawn_title"], it.get("title_case", "sentence"))
        s_ok = _text_match(it["plan_subtitle"], it["drawn_subtitle"])
        ov = it.get("overlap_report") or {}
        ov_ok = ov.get("overlap_count") == 0
        flag = "OK" if (t_ok and s_ok and ov_ok) else "FAIL"
        if not t_ok or not s_ok or not ov_ok:
            mismatches.append(bid)
        print(f'  [{flag}] {bid} overlaps={ov.get("overlap_count", "?")}')
        if not t_ok:
            print(f'         title plan: {it["plan_title"][:60]}')
            print(f'         title draw: {it["drawn_title"][:60]}')
        if not s_ok:
            print(f'         sub plan:   {it["plan_subtitle"][:60]}')
            print(f'         sub draw:   {it["drawn_subtitle"][:60]}')
    sheet = qc_contact_sheet(items, OUT / "qc_pilot_contact_sheet.png", cols=2)
    print(f"\nQC CONTACT SHEET: {sheet}")
    print(f"TEXT PROOF: {len(items) - len(mismatches)}/{len(items)} cells plan==drawn + 0 overlaps")
    if mismatches:
        print(f"MISMATCHES: {mismatches}")
    else:
        print("ALL CELLS: rendered title/subtitle match plan verbatim.")
    print("LOOK-APPROVAL GATE: review sheet before --all --deploy")
    return sheet


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
        dr.text((x, y + th_h + 8), it["family"], font=lf, fill=(232, 196, 120))
        dr.text((x, y + th_h + 40), f'{it["author"]} · {it["topic"]}', font=sf, fill=(214, 210, 202))
    sheet.save(out_path)
    return out_path


def cmd_proof(cfg, catalog):
    items = []
    for author, topic, inst in PROOF_PLAN:
        row = find_row(catalog, author, topic, inst)
        if not row:
            continue
        out = OUT / "proof" / f'{row["book_id"]}.png'
        items.append(render_row(cfg, row, out))
    sheet = contact_sheet(items, OUT / "proof_contact_sheet.png", cols=4)
    print(f"CONTACT SHEET: {sheet}")
    return sheet


def cmd_all(cfg, catalog, deploy=False, contact=False, allow_fallback=True):
    import collections
    out_root = SERVED if deploy else OUT / "all"
    out_root.mkdir(parents=True, exist_ok=True)
    fam = collections.Counter()
    for i, row in enumerate(catalog):
        out = out_root / f'{row["book_id"]}.png'
        it = render_row(cfg, row, out, allow_fallback)
        fam[it["family"]] += 1
        if (i + 1) % 50 == 0:
            print(f"  {i+1}/{len(catalog)}", flush=True)
    print("DONE", dict(fam), f"-> {out_root}")
    return out_root


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--proof", action="store_true")
    ap.add_argument("--qc-pilot", action="store_true", help="QC pilot with plan-vs-drawn proof sheet")
    ap.add_argument("--book", metavar="BOOK_ID")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--deploy", action="store_true")
    ap.add_argument("--sync-catalog", action="store_true")
    ap.add_argument("--contact", action="store_true")
    ap.add_argument("--no-fallback", action="store_true")
    args = ap.parse_args()
    cfg = A.load_cfg()
    if args.sync_catalog:
        catalog = A.sync_catalog_from_plans()
        print(f"synced catalog: {len(catalog)} rows -> {A.CATALOG}")
    else:
        catalog = A.load_catalog()

    if args.book:
        row = next((r for r in catalog if r["book_id"] == args.book), None)
        if not row:
            print("book_id not found")
            return
        dest = (SERVED if args.deploy else OUT / "single") / f"{args.book}.png"
        it = render_row(cfg, row, dest, not args.no_fallback)
        print(it["out"])
        print(f"plan title:    {it['plan_title']}")
        print(f"drawn title:   {it['drawn_title']}")
        print(f"plan subtitle: {it['plan_subtitle']}")
        print(f"drawn subtitle:{it['drawn_subtitle']}")
        return
    if args.qc_pilot:
        cmd_qc_pilot(cfg, catalog)
        return
    if args.all:
        cmd_all(cfg, catalog, deploy=args.deploy, contact=args.contact,
                allow_fallback=not args.no_fallback)
        return
    cmd_proof(cfg, catalog)


if __name__ == "__main__":
    main()
