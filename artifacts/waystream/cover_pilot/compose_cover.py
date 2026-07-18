#!/usr/bin/env python3
"""Pilot cover compositor — per-author IMAGE (from the author's FLUX pool) + brand
typography + topic symbol + SERIES BAND ('BOOK N · SERIES') + byline. Proves the
4-layer identity look (brand/author/series/book) the research prescribes."""
import sys, hashlib
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1600, 2560
SERIF_BOLD = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
SERIF_ITAL = "/System/Library/Fonts/Supplemental/Georgia Italic.ttf"
def sans(sz):
    for p in ("/System/Library/Fonts/Avenir Next.ttc", "/System/Library/Fonts/Supplemental/Arial.ttf"):
        try: return ImageFont.truetype(p, sz)
        except Exception: continue
    return ImageFont.load_default()
def serif(sz, ital=False): return ImageFont.truetype(SERIF_ITAL if ital else SERIF_BOLD, sz)

def _wrap(draw, text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= maxw: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def _vgrad(size, top_a, bot_a, top=True):
    w, h = size; g = Image.new("L", (1, h))
    for y in range(h):
        f = y / max(h - 1, 1)
        a = top_a + (bot_a - top_a) * f
        g.putpixel((0, y), int(a))
    return g.resize((w, h))

def _spaced(draw, xy, text, font, fill, tracking):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill); x += draw.textlength(ch, font=font) + tracking
    return x

def _spaced_w(draw, text, font, tracking):
    return sum(draw.textlength(ch, font=font) + tracking for ch in text) - tracking

SYMBOL = {"anxiety":"breath","boundaries":"divider","self_worth":"circle","overthinking":"sparks",
          "depression":"downslope","grief":"dot","sleep_anxiety":"circle","courage":"upslope"}
def draw_symbol(dr, kind, cx, cy, col, s=46):
    if kind == "divider": dr.line([(cx, cy-s), (cx, cy+s)], fill=col, width=7); dr.ellipse([cx-9,cy+s-2,cx+9,cy+s+16], fill=col)
    elif kind == "breath":
        for r in (s, int(s*0.62), int(s*0.3)): dr.ellipse([cx-r,cy-r,cx+r,cy+r], outline=col, width=5)
    elif kind == "circle": dr.ellipse([cx-s,cy-s,cx+s,cy+s], outline=col, width=7)
    elif kind == "sparks":
        for dx in (-s,0,s): dr.line([(cx+dx,cy+s),(cx+dx,cy-s)], fill=col, width=6)
    elif kind == "downslope": dr.line([(cx-s,cy-s),(cx+s,cy+s)], fill=col, width=8)
    elif kind == "upslope": dr.line([(cx-s,cy+s),(cx+s,cy-s)], fill=col, width=8)
    else: dr.ellipse([cx-12,cy-12,cx+12,cy+12], fill=col)

def compose(img_path, title, subtitle, author, series_name, book_num, sig_rgb, topic, out_path):
    base = Image.open(img_path).convert("RGB")
    # cover-fill crop to W:H
    s = max(W/base.width, H/base.height); base = base.resize((int(base.width*s), int(base.height*s)))
    base = base.crop(((base.width-W)//2, (base.height-H)//2, (base.width-W)//2+W, (base.height-H)//2+H))
    cv = base.copy()
    # top scrim for title legibility (dark at very top fading by 48%)
    top = Image.new("RGB",(W,int(H*0.5)),(8,12,20)); cv.paste(top,(0,0),_vgrad((W,int(H*0.5)),190,0))
    # bottom scrim for series band + byline
    bh=int(H*0.42); bot=Image.new("RGB",(W,bh),(8,10,16)); cv.paste(bot,(0,H-bh),_vgrad((W,bh),0,205))
    dr = ImageDraw.Draw(cv)
    M = 130; col = tuple(sig_rgb)
    # TITLE (dominant, focal-clarity) — shrink to fit <=3 lines
    fs = 196
    while fs > 110:
        tf = serif(fs); ls = _wrap(dr, title, tf, W-2*M)
        if len(ls) <= 3: break
        fs -= 8
    y = int(H*0.11)
    for ln in ls:
        lw = dr.textlength(ln, font=tf); x=(W-lw)//2
        dr.text((x+3,y+4), ln, font=tf, fill=(0,0,0)); dr.text((x,y), ln, font=tf, fill=(247,243,235))
        y += int(fs*1.06)
    # SUBTITLE
    sf = serif(58, ital=True)
    for ln in _wrap(dr, subtitle, sf, W-2*int(M*1.2)):
        lw=dr.textlength(ln,font=sf); dr.text(((W-lw)//2,y+18), ln, font=sf, fill=(232,228,220)); y+=70
    # TOPIC SYMBOL (book layer) — mid lower
    draw_symbol(dr, SYMBOL.get(topic,"dot"), W//2, int(H*0.60), col, 44)
    # SERIES BAND (book N · series) — the operator's ask
    bf = sans(40); label = f"BOOK {book_num}   ·   {series_name.upper()}"
    bw = _spaced_w(dr, label, bf, 6); bx=(W-bw)//2; by=int(H*0.80)
    dr.line([(bx-40,by+22),(bx-14,by+22)], fill=col, width=3); dr.line([(bx+bw+14,by+22),(bx+bw+40,by+22)], fill=col, width=3)
    _spaced(dr,(bx,by), label, bf, col, 6)
    # AUTHOR BYLINE
    af = sans(58); aw=dr.textlength(author.upper(), font=af)
    dr.text(((W-aw)//2, int(H*0.875)), author.upper(), font=af, fill=(245,242,236))
    impf = sans(30); iw=_spaced_w(dr,"WAYSTREAM SANCTUARY",impf,5)
    _spaced(dr,((W-iw)//2,int(H*0.875)+78),"WAYSTREAM SANCTUARY",impf,(190,186,178),5)
    cv.save(out_path); return out_path

if __name__ == "__main__":
    print("compositor ready")
