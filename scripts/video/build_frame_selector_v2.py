#!/usr/bin/env python3
"""
build_frame_selector_v2.py
Generate frame_selector_v2.html — ONE SECTION = ONE PICTURE.

Each row is a single picture slot the operator chooses an image for:
  - Beats longer than MAX_SEC are split into N sections (one per sub-frame),
    so a long beat that needs 2-4 pictures becomes 2-4 sections — never
    multiple picture inputs crammed into one row.
  - Beats shorter than MIN_SEC (0.5s) and zero-duration tail beats are merged
    forward into a neighbour so NO section is shorter than half a second.
  - Every section shows its own image choices: the chosen frame plus the
    natural alternative for each render version (v3.1-v3.7), and for every
    frame BOTH its REGULAR render and its MANGA counterpart.
  - Two-axis pick per section: WHICH frame + REGULAR vs MANGA.
  - Export = a flat per-picture manifest (one row per section) a future mixed
    regular/manga assembler can read directly.
"""

import csv
import math
from pathlib import Path

CSV_PATH = "/Users/ahjan/Downloads/frame_selection_chosen.csv"
FRAMES_DIR = Path("/Users/ahjan/phoenix_omega/artifacts/video/yt_starseed_ahjan_update_20260610/frames")
MANGA_DIR  = Path("/Users/ahjan/phoenix_omega/artifacts/video/yt_starseed_ahjan_update_20260610/manga_frames")
OUT_HTML = Path("/Users/ahjan/phoenix_omega/artifacts/video/yt_starseed_ahjan_update_20260610/frame_selector_v2.html")

MIN_SEC    = 0.5   # hard floor: no section may be shorter than this
MAX_SEC    = 3.0   # sections longer than this are split into multiple pictures
TARGET_SEC = 2.5   # aim for ~this many seconds per picture when splitting

# version label -> base frame number (frame_{base+beat_idx}.png = natural frame for beat)
VERSION_BASES = [
    ("v3.1", 3000),
    ("v3.2", 4000),
    ("v3.3", 5000),
    ("v3.4", 6000),
    ("v3.5", 7000),
    ("v3.6", 8000),
    ("v3.7", 9000),
]

SLOT_LETTERS = "ABCDEFGH"

def esc(s):
    return (str(s)
            .replace("&","&amp;")
            .replace("<","&lt;")
            .replace(">","&gt;")
            .replace('"',"&quot;")
            .replace("'","&#39;"))

def manga_name(fname):
    """Deterministic manga counterpart of a regular frame filename.
    Mirrors assemble_manga_v3_8.py::manga_path  (manga_{base}, jpg/jpeg -> png)."""
    base = fname.replace(".jpg", ".png").replace(".jpeg", ".png")
    return f"manga_{base}"

def n_pics_for(dur):
    """How many pictures (sections) a unit of `dur` seconds becomes.
    1 picture if it already fits in MAX_SEC; otherwise the fewest parts that keep
    every part <= MAX_SEC (so no section runs longer than 3s) — which also keeps
    each part well above the MIN_SEC floor."""
    if dur <= MAX_SEC + 1e-9:
        return 1
    n = math.ceil(dur / MAX_SEC)
    n = min(n, max(1, int(dur / MIN_SEC)))   # never make a part < MIN_SEC
    return max(2, n)

def main():
    # ---- Load CSV ----
    beats = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            beats.append(row)

    # ---- Index existing frames (regular + manga) ----
    existing = set(p.name for p in FRAMES_DIR.glob("frame_*.png"))
    manga_existing = set(p.name for p in MANGA_DIR.glob("manga_*.png")) if MANGA_DIR.exists() else set()

    # ---- Parse beats ----
    parsed = []
    for i, b in enumerate(beats):
        parsed.append(dict(
            i=i,
            num=int(b["beat_num"]),
            bid=b["beat_id"],
            start=float(b["start_sec"]),
            end=float(b["end_sec"]),
            dur=float(b["duration_sec"]),
            text=b["script_text"],
            chosen=b.get("chosen_frame", "").strip(),
        ))

    # ---- Coalesce sub-MIN beats forward so every UNIT >= MIN_SEC ----
    # (zero-duration tail beats + any beat under 0.5s get absorbed into a neighbour)
    units = []
    acc = None
    for b in parsed:
        if acc is None:
            acc = dict(start=b["start"], end=b["end"], beats=[b])
        else:
            acc["end"] = b["end"]
            acc["beats"].append(b)
        if (acc["end"] - acc["start"]) >= MIN_SEC - 1e-9:
            acc["dur"] = acc["end"] - acc["start"]
            units.append(acc)
            acc = None
    if acc is not None:                       # leftover shorter than MIN_SEC
        acc["dur"] = acc["end"] - acc["start"]
        if units:
            u = units[-1]
            u["end"] = acc["end"]
            u["dur"] = u["end"] - u["start"]
            u["beats"] += acc["beats"]
        else:
            units.append(acc)

    # ---- Expand units into SECTIONS (one picture each) ----
    sections = []
    for u in units:
        ref = u["beats"][0]
        ref_i = ref["i"]
        texts = [bb["text"] for bb in u["beats"] if bb["text"].strip()]
        utext = " ".join(texts)
        merged_count = len(u["beats"])
        unit_chosen = ""
        for bb in u["beats"]:
            if bb["chosen"]:
                unit_chosen = bb["chosen"]
                break

        n = n_pics_for(u["dur"])
        sub = u["dur"] / n
        for k in range(n):
            s_start = u["start"] + k * sub
            s_end   = u["start"] + (k + 1) * sub
            slot    = SLOT_LETTERS[k] if n > 1 else ""
            chosen_k = unit_chosen if k == 0 else ""   # extra slots start empty — operator picks

            if n > 1:
                status, badge = "SPLIT", f"SPLIT {k+1}/{n}"
            elif merged_count > 1:
                status, badge = "MERGED", "MERGED"
            elif sub < 1.0:
                status, badge = "SHORT", "SHORT"
            else:
                status, badge = "OK", "OK"

            sections.append(dict(
                num=ref["num"], bid=ref["bid"], slot=slot, n_slots=n, slot_k=k,
                start=s_start, end=s_end, dur=sub, text=utext, chosen=chosen_k,
                ref_i=ref_i, merged_count=merged_count, status=status, badge=badge,
            ))

    for sidx, s in enumerate(sections):
        s["sidx"] = sidx
        s["section_no"] = sidx + 1
    n_sections = len(sections)

    stats = {"OK": 0, "SPLIT": 0, "MERGED": 0, "SHORT": 0}
    for s in sections:
        stats[s["status"]] += 1

    # ---- Image helpers (each frame rendered as a REGULAR + MANGA pair) ----
    shown_fnames = set()

    def placeholder(text_html, w, muted=False):
        color = "#6b5a7d" if muted else "#7a5555"
        bg    = "#120e16" if muted else "#160d0d"
        bd    = "#2a1f3a" if muted else "#3a1f1f"
        h     = int(w * 0.56)
        return (f'<div style="width:{w}px;height:{h}px;background:{bg};border:1px dashed {bd};'
                f'border-radius:4px;color:{color};font-size:9px;display:flex;align-items:center;'
                f'justify-content:center;text-align:center;padding:3px;box-sizing:border-box;'
                f'margin:0 auto;line-height:1.2">{text_html}</div>')

    def thumb(path, fname, st, w, sec_i, sel_frame, sel_style):
        if fname == sel_frame and st == sel_style:
            border = "3px solid #22c55e"
        elif fname == sel_frame:
            border = "2px dashed #f59e0b"
        else:
            border = "1px solid #2a2a2a"
        return (f'<img src="file://{path}" width="{w}" loading="lazy"'
                f' data-frame="{esc(fname)}" data-style="{st}"'
                f' style="border:{border};border-radius:4px;display:block;cursor:pointer;margin:0 auto"'
                f' title="{esc(fname)} [{st}]"'
                f' onclick="pick({sec_i},\'{esc(fname)}\',\'{st}\',this)">')

    def pair_html(fname, w, label, sec_i, sel_frame, sel_style):
        """Render a frame as a vertically-stacked REGULAR + MANGA pair."""
        shown_fnames.add(fname)
        mfname = manga_name(fname)
        reg = (thumb(FRAMES_DIR / fname, fname, "regular", w, sec_i, sel_frame, sel_style)
               if fname in existing else placeholder(esc(fname) + "<br>MISSING", w))
        manga = (thumb(MANGA_DIR / mfname, fname, "manga", w, sec_i, sel_frame, sel_style)
                 if mfname in manga_existing else placeholder("manga not<br>generated", w, muted=True))
        return (f'<div style="display:inline-block;vertical-align:top;margin:3px;text-align:center">'
                f'<div style="color:#777;font-size:9px;max-width:{w}px;overflow:hidden;'
                f'text-overflow:ellipsis;white-space:nowrap;margin-bottom:2px">{esc(label)}</div>'
                f'<div style="color:#4ade80;font-size:8px;font-weight:bold;letter-spacing:1px">REGULAR</div>'
                f'{reg}'
                f'<div style="color:#c084fc;font-size:8px;font-weight:bold;letter-spacing:1px;margin-top:3px">MANGA</div>'
                f'{manga}'
                f'</div>')

    # ---- Build HTML rows (one per section) ----
    html_rows = []
    sections_with_manga = 0
    for s in sections:
        i      = s["sidx"]
        status = s["status"]
        ref_i  = s["ref_i"]

        # Natural alternative for each render version at this beat index
        nat = []
        for ver, base in VERSION_BASES:
            fn = f"frame_{base + ref_i}.png"
            if fn in existing:
                nat.append((ver, fn))

        opts = ([s["chosen"]] if s["chosen"] else []) + [fn for _, fn in nat]
        if any(manga_name(c) in manga_existing for c in opts):
            sections_with_manga += 1

        row_bg = {"OK":"#141414","SPLIT":"#0c1020","MERGED":"#160c1c","SHORT":"#1a1400"}[status]
        badge_style = {
            "OK":     "background:#22c55e;color:#000",
            "SPLIT":  "background:#3b82f6;color:#fff",
            "MERGED": "background:#a855f7;color:#fff",
            "SHORT":  "background:#f59e0b;color:#000",
        }[status]

        # Note line
        if status == "SPLIT":
            note = (f'<div class="note blue">✂ Picture {s["slot_k"]+1} of {s["n_slots"]} for this line '
                    f'(~{s["dur"]:.1f}s). Pick a distinct image below.</div>')
        elif status == "MERGED":
            note = (f'<div class="note purple">⛓ Merged {s["merged_count"]} short/zero beats into one '
                    f'{s["dur"]:.2f}s section (floor {MIN_SEC:.1f}s).</div>')
        elif status == "SHORT":
            note = f'<div class="note amber">⏱ {s["dur"]:.2f}s — short, but at/above the {MIN_SEC:.1f}s floor.</div>'
        else:
            note = ""
        if s["n_slots"] > 1 and s["slot_k"] > 0:
            note += '<div class="note" style="background:#101010;color:#666;margin-top:3px">↳ same narration line as the part(s) above</div>'

        # Missing-file warning for a pre-filled chosen frame
        if s["chosen"] and s["chosen"] not in existing:
            note += f'<div class="note red" style="margin-top:3px">⛔ FILE MISSING: {esc(s["chosen"])}</div>'

        # This section's picture (regular+manga pair) — or a prompt if empty
        if s["chosen"]:
            chosen_img = pair_html(s["chosen"], 190, "PICK", i, s["chosen"], "regular")
        else:
            chosen_img = ('<div style="color:#f59e0b;font-size:12px;padding:14px 8px;border:1px dashed #3a3000;'
                          'border-radius:6px;background:#120f00">↓ pick an image below ↓</div>')

        # Alternatives (natural per version) — each shown as a regular+manga pair
        alts = ""
        for ver, fname in nat:
            alts += pair_html(fname, 132, ver, i, s["chosen"], "regular")
        if not alts:
            alts = '<div style="color:#333;font-size:11px">No natural frames found for this section</div>'

        slot_lbl = f' · {s["slot"]}' if s["slot"] else ""
        html_rows.append(f'''<tr id="row_{i}" class="beat-row" data-status="{status}">
  <td class="meta-cell" style="background:{row_bg}">
    <div style="color:#888;font-size:12px;font-weight:bold">§{s['section_no']}</div>
    <div style="color:#555;font-size:10px">beat #{s['num']}{slot_lbl}</div>
    <div style="font-size:9px;font-weight:bold;padding:2px 4px;border-radius:3px;{badge_style};margin:3px 0">{s['badge']}</div>
    <div style="color:#555;font-size:10px">{s['start']:.1f}–{s['end']:.1f}s</div>
    <div style="color:#aaa;font-size:12px;font-weight:bold">{s['dur']:.2f}s</div>
  </td>
  <td class="text-cell" style="background:{row_bg}">
    <div style="color:#ccc;font-size:13px;line-height:1.5">{esc(s['text'])}</div>
    {note}
  </td>
  <td class="chosen-cell" style="background:{row_bg}">
    <div style="color:#444;font-size:10px;margin-bottom:4px">THIS SECTION&#39;S PICK&nbsp;·&nbsp;frame + style</div>
    {chosen_img}
    <input type="text" id="inp_{i}" value="{esc(s['chosen'])}"
      oninput="onType({i},this)"
      placeholder="frame_XXXX.png"
      style="width:196px;background:#0f0f0f;color:#eee;border:1px solid #333;
      border-radius:4px;padding:3px 7px;font-size:11px;margin-top:4px;display:block">
    <div style="margin-top:5px;display:flex;align-items:center;gap:5px;flex-wrap:wrap">
      <span style="color:#555;font-size:10px">style:</span>
      <button id="sty_{i}_regular" class="stybtn" onclick="setStyle({i},'regular')">REGULAR</button>
      <button id="sty_{i}_manga" class="stybtn" onclick="setStyle({i},'manga')">MANGA</button>
      <span id="mwarn_{i}" style="color:#f87171;font-size:9px"></span>
    </div>
  </td>
  <td class="alts-cell" style="background:{row_bg}">
    <div style="color:#444;font-size:10px;margin-bottom:4px">PICK ONE (natural per version) — each shows REGULAR + MANGA</div>
    <div style="display:flex;flex-wrap:wrap">{alts}</div>
  </td>
</tr>''')

    # ---- Derived JS data + coverage stats ----
    shown_manga = sorted(f for f in shown_fnames if manga_name(f) in manga_existing)
    manga_set_js = "[" + ",".join(f'"{esc(f)}"' for f in shown_manga) + "]"
    prefilled = sum(1 for s in sections if s["chosen"])
    needs_pick = n_sections - prefilled

    js_rows_items = []
    for s in sections:
        js_rows_items.append(
            f'{{section:{s["section_no"]},num:{s["num"]},id:"{esc(s["bid"])}",slot:"{s["slot"]}",'
            f'start:{s["start"]:.3f},end:{s["end"]:.3f},dur:{s["dur"]:.3f},'
            f'status:"{s["status"]}",chosen:"{esc(s["chosen"])}"}}'
        )
    js_rows = "[\n" + ",\n".join(js_rows_items) + "\n]"

    table_body = "\n".join(html_rows)

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Frame Selector v2 — 1 section = 1 picture</title>
<style>
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ background:#0a0a0a; color:#eee; font-family:system-ui,-apple-system,sans-serif; }}
  table {{ width:100%; border-collapse:collapse; }}
  .beat-row td {{ border-bottom:1px solid #1e1e1e; }}
  .beat-row:hover td {{ filter:brightness(1.12); }}
  .meta-cell {{ padding:8px 6px; text-align:center; width:72px; vertical-align:top; border-right:1px solid #1e1e1e; }}
  .text-cell {{ padding:10px 12px; vertical-align:top; min-width:200px; max-width:240px; border-right:1px solid #1e1e1e; }}
  .chosen-cell {{ padding:8px; vertical-align:top; min-width:220px; border-right:1px solid #1e1e1e; }}
  .alts-cell {{ padding:8px; vertical-align:top; }}
  .note {{ font-size:11px; margin-top:6px; padding:5px 7px; border-radius:4px; line-height:1.4; }}
  .note.red {{ background:#240808; color:#f87171; }}
  .note.amber {{ background:#1f1500; color:#fbbf24; }}
  .note.blue {{ background:#0a1226; color:#93c5fd; }}
  .note.purple {{ background:#160a22; color:#d8b4fe; }}
  input {{ font-family:inherit; }}
  input:focus {{ outline:2px solid #3b82f6; }}
  .stybtn {{ border:1px solid #333; background:#161616; color:#888; border-radius:3px;
             padding:2px 8px; font-size:10px; cursor:pointer; font-weight:bold; }}
  .stybtn:hover {{ filter:brightness(1.3); }}
  .stybtn.active-reg {{ background:#14532d; color:#bbf7d0; border-color:#22c55e; }}
  .stybtn.active-manga {{ background:#3b0764; color:#e9d5ff; border-color:#c084fc; }}
  .hdr {{ position:sticky; top:0; z-index:100; background:#0a0a0a; border-bottom:1px solid #222;
          padding:10px 14px; display:flex; align-items:center; gap:8px; flex-wrap:wrap; }}
  .chip {{ border-radius:4px; padding:3px 9px; font-size:12px; font-weight:bold; }}
  .btn {{ border:none; border-radius:4px; padding:5px 11px; cursor:pointer; font-size:12px; font-weight:bold; }}
  .btn:hover {{ opacity:0.85; }}
</style>
</head>
<body>

<div class="hdr">
  <span style="font-weight:bold;font-size:15px;color:#fff;margin-right:4px">Frame Selector v2 — 1 section = 1 picture</span>
  <span class="chip" style="background:#2a2a2a;color:#ccc">{n_sections} sections</span>
  <span class="chip" style="background:#3b82f6;color:#fff">✂ Split: {stats['SPLIT']}</span>
  <span class="chip" style="background:#a855f7;color:#fff">⛓ Merged: {stats['MERGED']}</span>
  <span class="chip" style="background:#f59e0b;color:#000">⏱ Short: {stats['SHORT']}</span>
  <span class="chip" style="background:#7e22ce;color:#fff">▦ Manga avail: {sections_with_manga}/{n_sections}</span>
  <span style="color:#333">|</span>
  <button class="btn" onclick="showAll()" style="background:#2a2a2a;color:#ccc">All</button>
  <button class="btn" onclick="showSplit()" style="background:#1d4ed8;color:#fff">Split parts</button>
  <button class="btn" onclick="showNeedsPick()" style="background:#b45309;color:#fff">Needs pick</button>
  <button class="btn" onclick="showShort()" style="background:#92400e;color:#fff">Short</button>
  <button class="btn" onclick="showMerged()" style="background:#7e22ce;color:#fff">Merged</button>
  <span style="margin-left:auto;color:#666;font-size:12px" id="counter">Picked: 0 / {n_sections}</span>
  <button class="btn" onclick="exportCSV()" style="background:#2563eb;color:#fff;font-size:13px;padding:6px 14px">⬇ Export CSV</button>
</div>

<div style="padding:6px 14px;color:#888;font-size:11px;border-bottom:1px solid #161616;background:#0c0c0c;line-height:1.6">
  <b>One row = one picture.</b> Long beats are split into multiple sections (✂), and beats under {MIN_SEC:.1f}s / zero-length
  tails are merged (⛓) so no section is shorter than {MIN_SEC:.1f}s. Every frame shows its
  <span style="color:#4ade80;font-weight:bold">REGULAR</span> render and its
  <span style="color:#c084fc;font-weight:bold">MANGA</span> counterpart — click either thumb to choose that frame
  <b>and</b> that style &nbsp;·&nbsp;
  <span style="border:3px solid #22c55e;padding:0 5px;border-radius:3px">green</span> = selected &nbsp;·&nbsp;
  <span style="border:2px dashed #f59e0b;padding:0 5px;border-radius:3px">amber dashed</span> = same frame, other style &nbsp;·&nbsp;
  split parts after the first start empty so you choose each picture.
</div>

<table>
<tbody id="tbl">
{table_body}
</tbody>
</table>

<script>
const ROWS = {js_rows};
const MANGA_SET = new Set({manga_set_js});   // regular fnames that HAVE a manga render
const chosen = {{}};
const style  = {{}};

// Initialise picks from rendered inputs; default every section to 'regular' style
document.querySelectorAll('input[id^="inp_"]').forEach(el => {{
  const i = +el.id.split('_')[1];
  if (el.value) chosen[i] = el.value;
}});
ROWS.forEach((r, i) => {{ if (style[i] === undefined) style[i] = 'regular'; }});
ROWS.forEach((r, i) => {{ updateStyleToggle(i); }});
updateCounter();

function rehighlight(i) {{
  const row = document.getElementById('row_' + i);
  if (!row) return;
  const f = chosen[i], s = style[i] || 'regular';
  row.querySelectorAll('img[data-frame]').forEach(img => {{
    if (img.dataset.frame === f && img.dataset.style === s) img.style.border = '3px solid #22c55e';
    else if (img.dataset.frame === f) img.style.border = '2px dashed #f59e0b';
    else img.style.border = '1px solid #2a2a2a';
  }});
}}

function pick(i, fname, st, imgEl) {{
  chosen[i] = fname;
  style[i] = st;
  const inp = document.getElementById('inp_' + i);
  if (inp) inp.value = fname;
  rehighlight(i);
  updateStyleToggle(i);
  updateCounter();
}}

function setStyle(i, st) {{
  style[i] = st;
  rehighlight(i);
  updateStyleToggle(i);
  updateCounter();
}}

function onType(i, inp) {{
  chosen[i] = inp.value;
  if (style[i] === undefined) style[i] = 'regular';
  rehighlight(i);
  updateStyleToggle(i);
  updateCounter();
}}

function updateStyleToggle(i) {{
  const rb = document.getElementById('sty_' + i + '_regular');
  const mb = document.getElementById('sty_' + i + '_manga');
  const w  = document.getElementById('mwarn_' + i);
  const s = style[i] || 'regular';
  if (rb) rb.className = 'stybtn' + (s === 'regular' ? ' active-reg' : '');
  if (mb) mb.className = 'stybtn' + (s === 'manga' ? ' active-manga' : '');
  if (w) {{
    const f = chosen[i];
    w.textContent = (s === 'manga' && f && !MANGA_SET.has(f)) ? '⚠ no manga render for this frame' : '';
  }}
}}

function updateCounter() {{
  const keys = Object.keys(chosen).filter(i => chosen[i] && chosen[i].trim());
  const n = keys.length;
  const m = keys.filter(i => style[i] === 'manga').length;
  document.getElementById('counter').textContent = 'Picked: ' + n + ' / {n_sections}  ·  Manga style: ' + m;
}}

function renderPath(fname, st) {{
  if (!fname) return '';
  return (st === 'manga') ? ('manga_frames/manga_' + fname) : ('frames/' + fname);
}}

function rows() {{ return Array.from(document.querySelectorAll('.beat-row')); }}
function showAll()       {{ rows().forEach(r => r.style.display = ''); }}
function showSplit()     {{ rows().forEach(r => r.style.display = r.dataset.status==='SPLIT'  ? '' : 'none'); }}
function showShort()     {{ rows().forEach(r => r.style.display = r.dataset.status==='SHORT'  ? '' : 'none'); }}
function showMerged()    {{ rows().forEach(r => r.style.display = r.dataset.status==='MERGED' ? '' : 'none'); }}
function showNeedsPick() {{ rows().forEach(r => {{ const i = +r.id.split('_')[1];
                            r.style.display = (chosen[i] && chosen[i].trim()) ? 'none' : ''; }}); }}

function exportCSV() {{
  const header = 'section,beat_num,beat_id,slot,start_sec,end_sec,duration_sec,chosen_frame,chosen_style,chosen_render';
  const lines = [header];
  ROWS.forEach((r, i) => {{
    const c  = (chosen[i] !== undefined ? chosen[i] : r.chosen) || '';
    const s  = style[i] || 'regular';
    const rp = renderPath(c, s);
    lines.push([r.section, r.num, r.id, r.slot, r.start.toFixed(3), r.end.toFixed(3),
                r.dur.toFixed(3), c, s, rp].join(','));
  }});
  const blob = new Blob([lines.join('\\n')], {{type:'text/csv'}});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'frame_selection_v2.csv';
  a.click();
}}
</script>
</body>
</html>'''

    OUT_HTML.write_text(html, encoding="utf-8")
    print(f"\nWritten: {OUT_HTML}")
    print(f"\nSection model (1 section = 1 picture):")
    print(f"  beats in CSV:        {len(parsed)}")
    print(f"  units after merge:   {len(units)}  (sub-{MIN_SEC:.1f}s + zero beats coalesced)")
    print(f"  SECTIONS total:      {n_sections}")
    print(f"    OK single:         {stats['OK']}")
    print(f"    SPLIT parts:       {stats['SPLIT']}  (long beats broken into multiple pictures)")
    print(f"    MERGED:            {stats['MERGED']}")
    print(f"    SHORT (≥{MIN_SEC:.1f}s):     {stats['SHORT']}")

    durs = [s["dur"] for s in sections]
    print(f"\n  shortest section:    {min(durs):.2f}s   longest section: {max(durs):.2f}s")
    under = [s for s in sections if s["dur"] < MIN_SEC - 1e-9]
    print(f"  sections < {MIN_SEC:.1f}s:      {len(under)}   (must be 0)")

    print(f"\nPicks + manga:")
    print(f"  pre-filled picks (slot A from CSV):        {prefilled} / {n_sections}")
    print(f"  empty slots awaiting a pick:               {needs_pick} / {n_sections}")
    print(f"  sections with ≥1 manga option:             {sections_with_manga} / {n_sections}")
    print(f"  distinct shown frames with a manga render:  {len(shown_manga)} / {len(shown_fnames)}")

if __name__ == "__main__":
    main()
