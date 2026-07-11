#!/usr/bin/env python3
"""
Single-book manga production runner (QA smoke + weekly rollout building block).

Stages (replay path, default):
  1. Series setup (phoenix_v4.manga.series.emit)
  2. Chapter DAG through CHAPTER_VISUAL (noop backend — prompts only)
  3. Panel images from image_bank/ replay map
  4. Remaining DAG stages through SERIES_MEMORY_MERGE
  5. Optional exports: PDF, CBZ, minimal EPUB under --output-dir

Usage:
  PYTHONPATH=. python3 scripts/run_manga_pipeline.py \\
    --brand stillness_press --topic burnout --persona gen_z_professionals \\
    --genre shonen --render-book --output-dir artifacts/manga_smoke/

See docs/MANGA_PRODUCTION_PIPELINE.md for Cloudflare / weekly integration.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.manga.image_backend import (  # noqa: E402
    ComfyUIBackend,
    FixtureReplayImageBackend,
    NoopImageBackend,
    RunComfyImageBackend,
)
from phoenix_v4.manga.models import stage_ids as sid  # noqa: E402
from phoenix_v4.manga.runner.chapter_runner import run_chapter_dag  # noqa: E402
from phoenix_v4.manga.series.emit import emit_series_setup  # noqa: E402
from scripts.manga._config import config_snapshot_hash  # noqa: E402


def count_topic_panel_pngs(repo_root: Path, brand_id: str, topic_id: str) -> int:
    bank = repo_root / "image_bank" / brand_id / topic_id
    if not bank.is_dir():
        return 0
    return sum(1 for p in bank.iterdir() if p.suffix.lower() == ".png" and p.is_file())


def _persona_to_demographic(persona: str) -> str:
    if not persona:
        return "anxious_millennials_urban"
    return persona.replace("-", "_")


def _check_service(url: str, timeout_s: float = 5.0) -> tuple[bool, str]:
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            _ = resp.read(64)
        return True, "ok"
    except urllib.error.HTTPError as e:
        return e.code < 500, str(e)
    except Exception as e:
        return False, str(e)


def build_replay_map_absolute(
    *,
    panel_prompts_path: Path,
    bank_dir: Path,
    map_out: Path,
) -> Path:
    pp = json.loads(panel_prompts_path.read_text(encoding="utf-8"))
    panels = pp.get("panels") or []
    pngs = sorted(p for p in bank_dir.iterdir() if p.suffix.lower() == ".png" and p.is_file())
    if not pngs:
        raise FileNotFoundError(f"No PNG panels under {bank_dir}")
    mapping: dict[str, str] = {}
    for i, panel in enumerate(panels):
        pid = str(panel.get("panel_id") or "")
        if not pid:
            continue
        src = pngs[i % len(pngs)]
        mapping[pid] = str(src.resolve())
    map_out.parent.mkdir(parents=True, exist_ok=True)
    map_out.write_text(json.dumps(mapping, indent=2) + "\n", encoding="utf-8")
    return map_out


def _export_pdf(ws: Path, dest: Path) -> Path | None:
    try:
        from PIL import Image
    except ImportError:
        return None
    comp = ws / "final_page_composite"
    pages = sorted(comp.glob("page_*.png"))
    if not pages:
        return None
    dest.parent.mkdir(parents=True, exist_ok=True)
    images = [Image.open(p).convert("RGB") for p in pages]
    try:
        if len(images) == 1:
            images[0].save(dest, format="PDF")
        else:
            images[0].save(dest, format="PDF", save_all=True, append_images=images[1:])
    finally:
        for im in images:
            im.close()
    return dest


def _export_cbz(ws: Path, dest: Path) -> Path | None:
    comp = ws / "final_page_composite"
    pages = sorted(comp.glob("page_*.png"))
    if not pages:
        return None
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in pages:
            zf.write(p, arcname=p.name)
    return dest


def _export_epub_minimal(ws: Path, dest: Path, *, title: str) -> Path | None:
    comp = ws / "final_page_composite"
    pages = sorted(comp.glob("page_*.png"))
    if not pages:
        return None
    try:
        import uuid
        from xml.sax.saxutils import escape
    except ImportError:
        return None
    uid = f"urn:uuid:{uuid.uuid4()}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    mimetype = "application/epub+zip"
    container = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""
    nav = """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en">
<head><meta charset="utf-8"/><title>Nav</title></head>
<body>
<nav epub:type="toc" id="toc"><h1>Contents</h1><ol></ol></nav>
</body></html>"""

    manifest_lines = [
        '<item id="nav" properties="nav" href="nav.xhtml" media-type="application/xhtml+xml"/>'
    ]
    spine_lines: list[str] = []
    for idx, _png in enumerate(pages, start=1):
        iid = f"img{idx:03d}"
        hid = f"h{idx:03d}"
        fname = f"images/page_{idx:03d}.png"
        manifest_lines.append(f'<item id="{iid}" href="{fname}" media-type="image/png"/>')
        manifest_lines.append(
            f'<item id="{hid}" href="xhtml/chapter{idx:03d}.xhtml" media-type="application/xhtml+xml"/>'
        )
        spine_lines.append(f'<itemref idref="{hid}"/>')
    opf = f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="bookid" version="3.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="bookid">{uid}</dc:identifier>
    <dc:title>{escape(title)}</dc:title>
    <dc:language>en</dc:language>
    <meta property="dcterms:modified">{datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}</meta>
  </metadata>
  <manifest>
    {chr(10).join(manifest_lines)}
  </manifest>
  <spine>
    {chr(10).join(spine_lines)}
  </spine>
</package>"""

    with zipfile.ZipFile(dest, "w") as zf:
        zf.writestr("mimetype", mimetype, compress_type=zipfile.ZIP_STORED)
        zf.writestr("META-INF/container.xml", container)
        zf.writestr("OEBPS/nav.xhtml", nav)
        zf.writestr("OEBPS/content.opf", opf)
        for idx, png in enumerate(pages, start=1):
            zf.write(png, arcname=f"OEBPS/images/page_{idx:03d}.png")
            body = f"""<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en"><head><meta charset="utf-8"/><title>Page {idx}</title></head>
<body><img src="../images/page_{idx:03d}.png" alt="page {idx}"/></body></html>"""
            zf.writestr(f"OEBPS/xhtml/chapter{idx:03d}.xhtml", body)
    return dest


def run_one_book(
    *,
    repo_root: Path,
    brand_id: str,
    topic_id: str,
    persona: str,
    genre: str,
    output_dir: Path,
    min_panel_images: int,
    backend: str,
    skip_pearl_star_check: bool,
    render_book: bool,
    chapter_id: str = "ch_smoke",
    mode: str | None = None,
) -> dict[str, Any]:
    snap = config_snapshot_hash()
    bank_dir = repo_root / "image_bank" / brand_id / topic_id
    n_bank = count_topic_panel_pngs(repo_root, brand_id, topic_id)
    if n_bank < min_panel_images:
        raise RuntimeError(
            f"Image bank gate: {brand_id}/{topic_id} has {n_bank} PNGs (< {min_panel_images}). "
            "Operator: add panels or lower min_panel_images for dev-only runs."
        )

    if backend in ("comfyui", "runcomfy") and not skip_pearl_star_check:
        base = os.environ.get("COMFYUI_URL", "").strip()
        if not base and os.environ.get("PEARL_STAR_IP"):
            base = f"http://{os.environ['PEARL_STAR_IP'].strip()}:8188"
        if backend == "comfyui":
            if not base:
                raise RuntimeError("COMFYUI_URL or PEARL_STAR_IP required for comfyui backend")
            ok, msg = _check_service(f"{base.rstrip('/')}/system_stats")
            if not ok:
                raise RuntimeError(f"Pearl Star / ComfyUI unreachable ({msg})")

    output_dir.mkdir(parents=True, exist_ok=True)
    ws = output_dir / "workspace"
    ws.mkdir(parents=True, exist_ok=True)

    series_id = f"{brand_id}_{topic_id}_{genre}".replace("-", "_")
    arc_id = f"arc_{topic_id}"
    emit_series_setup(
        ws,
        series_id=series_id,
        arc_id=arc_id,
        genre_id=genre,
        brand_id=brand_id,
        locale="en_US",
        topic=topic_id,
        demographic=_persona_to_demographic(persona),
        auto_generate_author=False,
        mode=mode,
    )

    # Resolve the brand's teacher so the render embeds the right teacher
    # (sai_ma for devotion_path, etc.) instead of the global 'ahjan' default;
    # stamp brand/genre/topic so the bubble genre register + manga profile
    # resolve for this render path.
    from phoenix_v4.planning.teacher_brand_resolver import resolve_teacher_for_brand
    teacher_id = resolve_teacher_for_brand(brand_id) or "ahjan"

    chapter_request = {
        "schema_version": "1.0.0",
        "artifact_type": "chapter_request",
        "series_id": series_id,
        "chapter_id": chapter_id,
        "arc_id": arc_id,
        "brand_id": brand_id,
        "genre_family": genre,
        "topic": topic_id,
        "teacher_id": teacher_id,
    }
    (ws / "chapter_request.json").write_text(json.dumps(chapter_request, indent=2) + "\n", encoding="utf-8")

    run_chapter_dag(ws, image_backend=NoopImageBackend(), to_stage=sid.CHAPTER_VISUAL, config_hash=snap, teacher_id=teacher_id)

    panel_prompts_path = ws / "panel_prompts.json"
    if not panel_prompts_path.is_file():
        raise RuntimeError("panel_prompts.json not produced")

    if backend == "replay":
        mmap = build_replay_map_absolute(
            panel_prompts_path=panel_prompts_path,
            bank_dir=bank_dir,
            map_out=ws / "replay" / "map.json",
        )
        image_backend: Any = FixtureReplayImageBackend.from_json_file(mmap)
    elif backend == "noop":
        image_backend = NoopImageBackend()
    elif backend == "runcomfy":
        image_backend = RunComfyImageBackend(
            output_dir=ws / "panel_images",
            dry_run=False,
        )
    elif backend == "comfyui":
        image_backend = ComfyUIBackend(
            output_dir=ws / "panel_images",
            dry_run=False,
        )
    else:
        raise ValueError(f"Unknown backend {backend!r}")

    run_chapter_dag(ws, image_backend=image_backend, from_stage=sid.CHAPTER_IMAGE_GEN, config_hash=snap, teacher_id=teacher_id)

    exports: dict[str, str] = {}
    if render_book:
        exports_dir = output_dir / "exports"
        exports_dir.mkdir(parents=True, exist_ok=True)
        slug = f"{topic_id}_{genre}_{chapter_id}_smoke"
        pdf = exports_dir / f"{slug}.pdf"
        cbz = exports_dir / f"{slug}.cbz"
        epub = exports_dir / f"{slug}.epub"
        p = _export_pdf(ws, pdf)
        if p:
            exports["pdf"] = str(p)
        c = _export_cbz(ws, cbz)
        if c:
            exports["cbz"] = str(c)
        e = _export_epub_minimal(ws, epub, title=f"{topic_id.replace('_', ' ').title()} — {genre}")
        if e:
            exports["epub"] = str(e)

    return {
        "workspace": str(ws),
        "series_id": series_id,
        "chapter_id": chapter_id,
        "image_bank_png_count": n_bank,
        "exports": exports,
    }


def write_qa_report(
    *,
    out_path: Path,
    result: dict[str, Any],
    bubble_note: str,
) -> None:
    ws = Path(result["workspace"])
    comp = ws / "final_page_composite"
    pages = sorted(comp.glob("page_*.png")) if comp.is_dir() else []
    pp_path = ws / "panel_prompts.json"
    panel_count = 0
    if pp_path.is_file():
        pp = json.loads(pp_path.read_text(encoding="utf-8"))
        panel_count = len(pp.get("panels") or [])
    ls_path = ws / "lettering_spec.json"
    lettering = {}
    if ls_path.is_file():
        lettering = json.loads(ls_path.read_text(encoding="utf-8"))
    bubbles = lettering.get("bubbles") or lettering.get("speech_bubbles") or []
    bubble_pct = "n/a"
    if pages and isinstance(bubbles, list):
        # spot heuristic: bubbles present in spec vs pages
        bubble_pct = f"spec_bubble_entries={len(bubbles)} (spot-check: see lettering_spec.json)"

    lines = [
        "# Manga smoke QA report",
        "",
        f"- Generated (UTC): {datetime.now(timezone.utc).isoformat()}",
        f"- Workspace: `{result['workspace']}`",
        f"- Panel count (panel_prompts): **{panel_count}**",
        f"- Page count (final_page_composite): **{len(pages)}**",
        f"- Exports: {result.get('exports')}",
        f"- Image bank PNGs used: **{result['image_bank_png_count']}**",
        "",
        "## Speech bubbles",
        "",
        bubble_note,
        f"- Lettering / bubble coverage note: {bubble_pct}",
        "",
        "## Pass/Fail",
        "",
        "- Chapter 1: **PASS** if `revision_queue.json` chapter_clearance is pass and pages exist.",
        "",
    ]
    rq = ws / "revision_queue.json"
    if rq.is_file():
        rqj = json.loads(rq.read_text(encoding="utf-8"))
        lines.append(f"- revision_queue chapter_clearance: `{rqj.get('chapter_clearance')}`")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Run single-book manga pipeline (replay image bank by default).")
    ap.add_argument("--brand", required=True, help="Brand id, e.g. stillness_press")
    ap.add_argument("--topic", required=True)
    ap.add_argument("--persona", default="gen_z_professionals")
    ap.add_argument("--genre", default="shonen", help="Genre id for genre_blueprint (e.g. shonen, shojo, seinen)")
    ap.add_argument(
        "--mode",
        default="",
        choices=("", "teacher", "music"),
        help="Optional mode vessel (teacher|music) woven into story architecture",
    )
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--min-panel-images", type=int, default=56)
    ap.add_argument(
        "--backend",
        choices=("replay", "noop", "runcomfy", "comfyui"),
        default="replay",
        help="Image backend after panel_prompts (default replay from image_bank)",
    )
    ap.add_argument("--skip-pearl-star-check", action="store_true", help="Skip ComfyUI health check (CI only)")
    ap.add_argument("--render-book", action="store_true", help="Write PDF/CBZ/EPUB under output-dir/exports")
    ap.add_argument("--bubble-note", default="", help="Override QA bubble section text")
    ap.add_argument(
        "--chapter-count",
        type=int,
        default=1,
        help="Run N sequential chapter smoke workspaces under output-dir/chapter_NNN/",
    )
    args = ap.parse_args()

    bubble_default = (
        "Speech bubble rendering: **not merged / silent panels** if lettering does not yet emit bubble layers "
        "into composites (see manga speech-bubble sprint). Acceptable for v1."
    )
    bubble_note = args.bubble_note or bubble_default

    if args.chapter_count < 1:
        print("ERROR: --chapter-count must be >= 1", file=sys.stderr)
        return 1

    out_root = args.output_dir.resolve()
    mode = args.mode or None
    try:
        results: list[dict[str, Any]] = []
        if args.chapter_count == 1:
            results.append(
                run_one_book(
                    repo_root=REPO_ROOT,
                    brand_id=args.brand,
                    topic_id=args.topic,
                    persona=args.persona,
                    genre=args.genre,
                    output_dir=out_root,
                    min_panel_images=args.min_panel_images,
                    backend=args.backend,
                    skip_pearl_star_check=args.skip_pearl_star_check,
                    render_book=args.render_book,
                    chapter_id="ch_smoke",
                    mode=mode,
                )
            )
        else:
            for i in range(1, args.chapter_count + 1):
                cid = f"ch_smoke_{i}"
                sub = out_root / f"chapter_{i:03d}"
                results.append(
                    run_one_book(
                        repo_root=REPO_ROOT,
                        brand_id=args.brand,
                        topic_id=args.topic,
                        persona=args.persona,
                        genre=args.genre,
                        output_dir=sub,
                        min_panel_images=args.min_panel_images,
                        backend=args.backend,
                        skip_pearl_star_check=args.skip_pearl_star_check,
                        render_book=args.render_book,
                        chapter_id=cid,
                        mode=mode,
                    )
                )
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    result = results[-1]
    write_qa_report(
        out_path=out_root / "QA_REPORT.md",
        result=result,
        bubble_note=bubble_note,
    )
    if args.chapter_count > 1:
        idx_path = out_root / "QA_REPORT_INDEX.md"
        idx_lines = ["# Multi-chapter smoke index", "", f"- Chapters: **{args.chapter_count}**", ""]
        for r in results:
            idx_lines.append(f"- `{r.get('chapter_id')}` → `{r.get('workspace')}`")
        idx_path.write_text("\n".join(idx_lines) + "\n", encoding="utf-8")
        print("QA index:", idx_path)
    print(json.dumps(result, indent=2))
    print("QA report:", out_root / "QA_REPORT.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
