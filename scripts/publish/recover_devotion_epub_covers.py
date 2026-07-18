#!/usr/bin/env python3
"""Render real-FLUX covers and inject them into every Devotion e-book EPUB.

The delivered Devotion EPUBs (``brand-wizard-app/public/deliveries/devotion_path/
<week>/amazon_kdp/*.epub``) shipped with NO cover. This batch adds a real cover
via the canonical two-stage pipeline, then injects it *in place* (no rebuild
from source — every chapter is preserved byte-for-byte):

  Stage 1  render_imagery_for_template — FLUX imagery, rendered ONCE per
           image-bearing genre (schnell / Apache-2.0, never flux1-dev). Devotion
           stems map by leading token: ``burnout_*`` -> burnout, ``courage_*`` ->
           courage (both image-bearing), ``imposter_syndrome_*`` ->
           imposter_syndrome (type-dominant: ``imagery_zone: null`` -> flat
           colour, NO FLUX). So just 2 GPU renders cover all 80 books.
  Stage 2  render_kdp_cover — PIL composites title/subtitle/author over the
           (shared) imagery into the genre template -> 1600x2560 PNG.
  Inject   add EPUB/cover.png + EPUB/cover.xhtml, patch content.opf (manifest
           cover-image + <meta name="cover"> + spine itemref first), re-zip with
           mimetype stored-first. Mirrors the verified pilot (#1727).

Robustness:
  * Each EPUB's BASE bytes are read from ``origin/main`` (not the drifted working
    tree), so the committed diff is purely the cover addition.
  * Covered EPUBs are written to ``--out-dir`` (a staging dir); the working tree
    is never modified. The caller hash-objects the staging files for a plumbing
    commit.
  * Title-too-long -> drop subtitle, then shorten the title (logged, never
    silent).
  * Every output kept < 1 MB (deliveries are plain git blobs under the
    no-binary-blobs cap); covers are re-compressed if needed.

  COMFYUI_URL=http://100.92.68.74:8188 PYTHONPATH=. python3 \
      scripts/publish/recover_devotion_epub_covers.py \
      --out-dir /tmp/devotion_covered --i-have-confirmed-pearl-star

Licence: flux1-schnell-fp8 (Apache-2.0) only; no paid LLM/image API.
"""
from __future__ import annotations

import argparse
import io
import os
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from scripts.publish.render_imagery_for_template import (  # noqa: E402
    ImageryPlan,
    compose_negative_prompt,
    compose_positive_prompt,
    flux_dimensions,
    imagery_aspect_for_genre,
    load_cookbook,
    load_templates,
    submit_to_comfyui,
)
from scripts.publish.render_kdp_cover import (  # noqa: E402
    TitleTooLongForTemplateError,
    render_kdp_cover,
)

DELIVERIES = REPO / "brand-wizard-app" / "public" / "deliveries" / "devotion_path"
MAX_EPUB_BYTES = 1_048_576          # no-binary-blobs CI cap (exact)
COVER_RETRY_BUDGET = 850_000        # cover-png target on the recompress retry
SEED = 837_204

COVER_XHTML = (
    '<?xml version="1.0" encoding="utf-8"?>\n'
    "<!DOCTYPE html>\n"
    '<html xmlns="http://www.w3.org/1999/xhtml" '
    'xmlns:epub="http://www.idpf.org/2007/ops">\n'
    '<head><meta charset="utf-8"/><title>Cover</title>\n'
    "<style>html,body{margin:0;padding:0}"
    "img{display:block;width:100%;height:auto}</style></head>\n"
    '<body epub:type="cover"><div><img src="cover.png" alt="Cover"/></div></body>\n'
    "</html>\n"
)

_H1 = re.compile(r"<h1[^>]*>(.*?)</h1>", re.S | re.I)
_SUB = re.compile(r"<p[^>]*color:\s*#555[^>]*>(.*?)</p>", re.S | re.I)
_CREATOR = re.compile(r"<dc:creator[^>]*>(.*?)</dc:creator>", re.S | re.I)
_BOOK_SUFFIX = re.compile(r":\s*A\s+[\w/&; ]+?\s+Book\s*$", re.I)


def stem_of(epub: Path) -> str:
    return epub.stem.split("__", 1)[0]


def genre_of(stem: str) -> str:
    if stem.startswith("burnout"):
        return "burnout"
    if stem.startswith("courage"):
        return "courage"
    if stem.startswith("imposter_syndrome"):
        return "imposter_syndrome"
    raise ValueError(f"no genre mapping for stem {stem!r}")


def _strip_tags(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)
    s = (s.replace("&amp;", "&").replace("&#8217;", "’")
          .replace("&#8212;", "—").replace("&quot;", '"')
          .replace("&#39;", "'").replace("&lt;", "<").replace("&gt;", ">"))
    return " ".join(s.split()).strip()


def origin_main_bytes(rel: str) -> bytes:
    out = subprocess.run(
        ["git", "show", f"origin/main:{rel}"],
        cwd=REPO, capture_output=True,
    )
    if out.returncode != 0:
        raise FileNotFoundError(f"origin/main:{rel} — {out.stderr.decode()[:200]}")
    return out.stdout


def epub_metadata(base: bytes) -> tuple[str, str, str]:
    with zipfile.ZipFile(io.BytesIO(base)) as z:
        names = z.namelist()
        title_x = next((n for n in names if n.endswith("title.xhtml")), None)
        opf = next((n for n in names if n.endswith(".opf")), None)
        tx = z.read(title_x).decode("utf-8") if title_x else ""
        ox = z.read(opf).decode("utf-8") if opf else ""
    title = subtitle = author = ""
    m = _H1.search(tx)
    if m:
        title = _BOOK_SUFFIX.sub("", _strip_tags(m.group(1))).strip()
    m = _SUB.search(tx)
    if m:
        subtitle = _strip_tags(m.group(1))
    m = _CREATOR.search(ox)
    if m:
        author = _strip_tags(m.group(1))
    if not author:
        m = re.search(r">\s*By\s+([^<]+)<", tx)
        author = m.group(1).strip() if m else "Sai Maa"
    if not title:
        raise ValueError("could not extract <h1> title from title.xhtml")
    return title, subtitle, author


def render_genre_imagery(genre: str, comfy_url: str, out_dir: Path) -> Path:
    templates = load_templates()
    cookbook = load_cookbook()
    tpl = templates["templates"][genre]
    aspect = imagery_aspect_for_genre(tpl)
    if aspect is None:
        raise ValueError(f"genre {genre} has no imagery_zone")
    w, h = flux_dimensions(aspect)
    out = out_dir / f"devotion_imagery_{genre}.png"
    plan = ImageryPlan(
        book_id=f"devotion_{genre}", full_book_id=f"devotion_{genre}", genre=genre,
        width=w, height=h, aspect=round(aspect, 3),
        positive_prompt=compose_positive_prompt(cookbook, genre),
        negative_prompt=compose_negative_prompt(cookbook),
        output_path=out, type_dominant=False,
    )
    img = submit_to_comfyui(plan, comfyui_url=comfy_url, config="schnell", seed=SEED)
    out.write_bytes(img)
    print(f"  Stage1 {genre}: {w}x{h} -> {out.stat().st_size // 1024} KB", file=sys.stderr)
    return out


def build_cover(genre, imagery, title, subtitle, author, out_png) -> str:
    """Composite the cover; fall back gracefully on TitleTooLong. Returns a note."""
    candidates: list[tuple[str, str]] = [(title, subtitle), (title, "")]
    words = title.split()
    for k in range(len(words) - 1, 1, -1):
        candidates.append((" ".join(words[:k]), ""))
    for t, s in candidates:
        try:
            render_kdp_cover(
                illustration_path=imagery, title=t, subtitle=(s or None),
                author=author, genre=genre, output_path=out_png,
            )
            if t != title:
                return f"title-shortened:{t!r}"
            if s != subtitle:
                return "subtitle-dropped"
            return "ok"
        except TitleTooLongForTemplateError:
            continue
    raise TitleTooLongForTemplateError(f"{title!r} cannot fit genre {genre}")


def _compress_png_under(src: Path, budget: int) -> None:
    from PIL import Image
    im = Image.open(src).convert("RGB")
    w, h = im.size
    for colors in (256, 192, 128, 96, 64):
        im.quantize(colors=colors, method=Image.FASTOCTREE).save(
            src, format="PNG", optimize=True)
        if src.stat().st_size <= budget:
            return
    for scale in (0.85, 0.7, 0.6):
        im.resize((int(w * scale), int(h * scale)), Image.LANCZOS).quantize(
            colors=128, method=Image.FASTOCTREE).save(src, format="PNG", optimize=True)
        if src.stat().st_size <= budget:
            return


def inject_cover(base: bytes, cover_png: bytes) -> bytes:
    with zipfile.ZipFile(io.BytesIO(base)) as z:
        infos = z.infolist()
        data = {i.filename: z.read(i.filename) for i in infos}
    opf_name = next(n for n in data if n.endswith(".opf"))
    opf_dir = opf_name.rsplit("/", 1)[0] + "/" if "/" in opf_name else ""
    cover_png_name = f"{opf_dir}cover.png"
    cover_xhtml_name = f"{opf_dir}cover.xhtml"

    opf = data[opf_name].decode("utf-8")
    if 'id="cover-image"' not in opf:
        opf = opf.replace(
            "</manifest>",
            '    <item href="cover.png" id="cover-image" media-type="image/png" '
            'properties="cover-image"/>\n'
            '    <item href="cover.xhtml" id="cover" '
            'media-type="application/xhtml+xml"/>\n  </manifest>',
            1,
        )
    if 'name="cover"' not in opf:
        opf = opf.replace(
            "</metadata>",
            '    <meta name="cover" content="cover-image"/>\n  </metadata>', 1)
    if 'idref="cover"' not in opf:
        opf = re.sub(r"(<spine[^>]*>)",
                     r'\1\n    <itemref idref="cover" linear="yes"/>', opf, count=1)

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as out:
        mi = zipfile.ZipInfo("mimetype")
        mi.compress_type = zipfile.ZIP_STORED
        out.writestr(mi, "application/epub+zip")
        for i in infos:
            if i.filename in ("mimetype", cover_png_name, cover_xhtml_name):
                continue
            payload = opf if i.filename == opf_name else data[i.filename]
            out.writestr(i, payload)
        out.writestr(cover_png_name, cover_png)
        out.writestr(cover_xhtml_name, COVER_XHTML)
    return buf.getvalue()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out-dir", type=Path,
                    default=Path(tempfile.gettempdir()) / "devotion_covered")
    ap.add_argument("--comfy-url",
                    default=os.environ.get("COMFYUI_URL", "http://100.92.68.74:8188"))
    ap.add_argument("--only", default=None, help="substring filter on epub path")
    ap.add_argument("--limit", type=int, default=None, help="cap number of books")
    ap.add_argument("--dry-run", action="store_true",
                    help="plan + extract metadata; no GPU, no writes")
    ap.add_argument("--i-have-confirmed-pearl-star", action="store_true")
    args = ap.parse_args(argv)

    epubs = sorted(DELIVERIES.glob("*/amazon_kdp/*.epub"))
    if args.only:
        epubs = [e for e in epubs if args.only in str(e)]
    if args.limit:
        epubs = epubs[: args.limit]
    if not epubs:
        print("no Devotion EPUBs matched", file=sys.stderr)
        return 1
    if not args.dry_run and not args.i_have_confirmed_pearl_star:
        print("error: real run requires --i-have-confirmed-pearl-star (or --dry-run)",
              file=sys.stderr)
        return 2

    tmp = Path(tempfile.mkdtemp(prefix="devotion_imagery_"))
    needed = sorted({genre_of(stem_of(e)) for e in epubs})
    print(f"{len(epubs)} EPUBs · genres={needed}", file=sys.stderr)

    imagery: dict[str, Path | None] = {}
    for g in needed:
        if g == "imposter_syndrome":
            imagery[g] = None
            continue
        if args.dry_run:
            imagery[g] = None
            print(f"[dry] would FLUX-render genre={g}", file=sys.stderr)
            continue
        imagery[g] = render_genre_imagery(g, args.comfy_url, tmp)

    results: list[tuple[str, str, str]] = []
    for e in epubs:
        rel = str(e.relative_to(REPO))
        genre = genre_of(stem_of(e))
        try:
            base = origin_main_bytes(rel)
            title, subtitle, author = epub_metadata(base)
            if args.dry_run:
                results.append((e.name, "planned",
                                f"[{genre}] {title} | {subtitle[:40]}"))
                print(results[-1], file=sys.stderr)
                continue
            cover_png = tmp / f"{e.stem}_cover.png"
            note = build_cover(genre, imagery[genre], title, subtitle, author, cover_png)
            covered = inject_cover(base, cover_png.read_bytes())
            if len(covered) > MAX_EPUB_BYTES:
                _compress_png_under(cover_png, COVER_RETRY_BUDGET)
                covered = inject_cover(base, cover_png.read_bytes())
            dest = args.out_dir / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(covered)
            rc = subprocess.run(
                [sys.executable, str(REPO / "scripts/publish/validate_epub.py"), str(dest)],
                capture_output=True, text=True,
            ).returncode
            size = len(covered)
            ok = rc == 0 and size <= MAX_EPUB_BYTES
            results.append((e.name, "ok" if ok else "CHECK",
                            f"{size}B validate_rc={rc} [{note}]"))
        except Exception as exc:  # noqa: BLE001
            results.append((e.name, "ERROR", str(exc)))
        print(results[-1], file=sys.stderr)

    ok = sum(1 for _, s, _ in results if s in ("ok", "planned"))
    print(f"\nSUMMARY: {ok}/{len(results)} ok; out-dir={args.out_dir}", file=sys.stderr)
    for name, status, detail in results:
        if status not in ("ok", "planned"):
            print(f"  !! {status}: {name} — {detail}", file=sys.stderr)
    return 0 if ok == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
