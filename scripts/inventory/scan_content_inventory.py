#!/usr/bin/env python3
"""Scan repo for built vs configured content; emit JSON + Markdown summary.

Output:
  artifacts/inventory/content_inventory.json
  artifacts/inventory/content_inventory_summary.md
  brand-wizard-app/public/data/content_inventory.json (same JSON for static hosting)

Contract: docs/CONTENT_INVENTORY_WORKSTREAM_SPEC.md

Usage:
  python3 scripts/inventory/scan_content_inventory.py [--repo ROOT]
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def safe_glob(root: Path, pattern: str) -> list[Path]:
    if not root.is_dir():
        return []
    return sorted(root.glob(pattern))


def count_lines_csv(path: Path) -> int:
    if not path.is_file():
        return 0
    with path.open(newline="", encoding="utf-8", errors="replace") as f:
        return max(0, sum(1 for _ in f) - 1)


def teacher_slug_from_book_stem(stem: str) -> str:
    if stem.endswith("_book"):
        stem = stem[: -len("_book")]
    parts = stem.split("_")
    if len(parts) >= 2:
        return "_".join(parts[:-1])
    return stem


def discover_teachers(repo: Path) -> list[str]:
    slugs: set[str] = set()
    pe = repo / "artifacts" / "pipeline_examples"
    if pe.is_dir():
        for d in pe.iterdir():
            if d.is_dir() and not d.name.startswith("."):
                slugs.add(d.name)
    tb = repo / "teacher_books"
    if tb.is_dir():
        for p in tb.glob("*.txt"):
            slugs.add(teacher_slug_from_book_stem(p.stem))
    if slugs:
        return sorted(slugs)
    cat = repo / "artifacts" / "catalog" / "full_catalog.csv"
    if not cat.is_file():
        return []
    teachers: Counter[str] = Counter()
    with cat.open(encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            tid = (row.get("teacher_id") or "").strip()
            if tid:
                teachers[tid] += 1
    return [t for t, _ in teachers.most_common(60)]


def has_book_text(repo: Path, teacher: str) -> bool:
    tb = repo / "teacher_books"
    if not tb.is_dir():
        return False
    for p in tb.glob(f"{teacher}_*_book.txt"):
        return True
    for p in tb.glob("*.txt"):
        if p.stem.startswith(f"{teacher}_") and p.stem.endswith("_book"):
            return True
    return False


def collect_covers_primary(repo: Path) -> list[Path]:
    """Spec: brand-wizard-app/public/assets/covers/ cover_*.png (fallback: any raster)."""
    root = repo / "brand-wizard-app" / "public" / "assets" / "covers"
    if not root.is_dir():
        return []
    rasters = [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")]
    primary = [p for p in rasters if p.name.startswith("cover_")]
    return primary if primary else rasters


def collect_manga_covers(repo: Path) -> list[Path]:
    """Spec: *cover* in filename under manga_covers; fallback any raster."""
    root = repo / "brand-wizard-app" / "public" / "assets" / "manga_covers"
    extra = list(repo.glob("artifacts/**/manga_cover*/**/*"))
    paths: list[Path] = []
    if root.is_dir():
        paths.extend(p for p in root.rglob("*") if p.is_file())
    paths.extend(p for p in extra if p.is_file())
    rasters = [p for p in paths if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")]
    primary = [p for p in rasters if "_cover_" in p.name.lower() or p.name.lower().endswith("_cover.png")]
    return primary if primary else rasters


def collect_manga_panels(repo: Path) -> list[Path]:
    """Spec: p*.png under manga_panels; include artifacts manga_book / panels."""
    out: list[Path] = []
    mpd = repo / "brand-wizard-app" / "public" / "assets" / "manga_panels"
    if mpd.is_dir():
        out.extend(p for p in mpd.rglob("*.png") if p.is_file())
    out.extend(repo.glob("artifacts/**/manga_book/**/*.png"))
    out.extend(repo.glob("artifacts/**/panels/**/*.png"))
    return list(dict.fromkeys(out))


def teacher_in_path(tid: str, path: Path) -> bool:
    blob = (path.name + str(path).lower()).lower().replace("_", "")
    t = tid.lower().replace("_", "")
    return tid.lower() in str(path).lower() or (len(t) >= 3 and t in blob)


@dataclass
class TypeStats:
    configured: int
    built: int

    def pct(self) -> float:
        if self.configured <= 0:
            return 100.0 if self.built > 0 else 0.0
        return round(100.0 * self.built / self.configured, 2)


def small_list(lst: list, n: int) -> list:
    return lst[:n] if len(lst) > n else lst


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan content inventory")
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="Repo root")
    args = parser.parse_args()
    repo: Path = args.repo.resolve()

    out_dir = repo / "artifacts" / "inventory"
    out_dir.mkdir(parents=True, exist_ok=True)

    catalog_path = repo / "artifacts" / "catalog" / "full_catalog.csv"
    catalog_rows = count_lines_csv(catalog_path)

    # --- Built counts ---
    book_files = safe_glob(repo / "teacher_books", "*.txt")
    book_built = len([p for p in book_files if "_book" in p.name or p.name.endswith("_book.txt")])

    epub_paths = list(repo.glob("artifacts/**/*.epub"))
    if not epub_paths:
        epub_paths = list(repo.glob("**/*.epub"))
    epub_built = len(epub_paths)

    covers_primary = collect_covers_primary(repo)
    if covers_primary:
        covers_all = list(dict.fromkeys(covers_primary))
    else:
        covers_all = []
        for pat in (
            "brand-wizard-app/public/assets/covers/**/*.png",
            "artifacts/**/covers/**/*.png",
        ):
            covers_all.extend(repo.glob(pat))
        covers_all = list(dict.fromkeys(covers_all))
    cover_built = len(set(covers_primary or covers_all))

    manga_cover_paths = collect_manga_covers(repo)
    manga_cover_built = len(set(manga_cover_paths))

    manga_panel_paths = collect_manga_panels(repo)
    manga_panel_built = len(set(manga_panel_paths))

    video_plans = list(repo.glob("artifacts/pipeline_examples/**/video_plan.json"))
    video_plan_built = len(video_plans)

    vid_yt = list(repo.glob("artifacts/videos/youtube/**/*.mp4")) + list(
        repo.glob("artifacts/videos/youtube/**/*.mov")
    )
    vid_tt = list(repo.glob("artifacts/videos/tiktok/**/*.mp4")) + list(
        repo.glob("artifacts/videos/tiktok/**/*.mov")
    )
    video_youtube_built = len(set(vid_yt))
    video_tiktok_built = len(set(vid_tt))
    video_rendered_built = video_youtube_built + video_tiktok_built

    audio_paths = list(repo.glob("artifacts/audio/presenter/**/*.mp3")) + list(
        repo.glob("brand-wizard-app/public/assets/audio/presenter/**/*.mp3")
    )
    audio_built = len(set(audio_paths))

    canonical_atoms = len(list(repo.glob("atoms/**/CANONICAL.txt")))
    if canonical_atoms == 0:
        canonical_atoms = len(list(repo.glob("SOURCE_OF_TRUTH/**/CANONICAL.txt")))

    panel_index = list(set(manga_panel_paths))

    teachers = discover_teachers(repo)
    per_teacher: list[dict[str, Any]] = []
    missing: list[dict[str, str]] = []

    for tid in teachers:
        bt = has_book_text(repo, tid)
        epub_ok = any(tid in str(p) for p in small_list(epub_paths, 800))
        cover_ok = any(teacher_in_path(tid, p) for p in covers_all[:1200]) or any(
            tid.replace("_", "") in p.name.replace("_", "") for p in covers_all[:1200]
        )
        plan_ok = (repo / "artifacts" / "pipeline_examples" / tid / "video_plan.json").is_file()
        manga_c = any(teacher_in_path(tid, p) for p in manga_cover_paths[:800])
        manga_p = any(teacher_in_path(tid, p) for p in panel_index)
        vid_y = any(tid in str(p) for p in vid_yt[:400])
        vid_t = any(tid in str(p) for p in vid_tt[:400])
        aud = any(tid in str(p) for p in audio_paths[:500])

        per_teacher.append(
            {
                "id": tid,
                "book_text": bt,
                "epub": epub_ok,
                "cover": cover_ok,
                "manga_cover": manga_c,
                "manga_panels": manga_p,
                "manga_any": manga_c or manga_p,
                "video_plan": plan_ok,
                "video_youtube": vid_y,
                "video_tiktok": vid_t,
                "video_rendered_any": vid_y or vid_t,
                "audio_presenter": aud,
            }
        )

        if not bt:
            missing.append(
                {
                    "type": "book_text",
                    "teacher": tid,
                    "topic": "",
                    "lane": "",
                    "action": f"Add teacher book under teacher_books/ for {tid}",
                }
            )
        if bt and not epub_ok:
            missing.append(
                {
                    "type": "epub",
                    "teacher": tid,
                    "topic": "",
                    "lane": "",
                    "action": "python3 scripts/release/build_epub.py  # if script present",
                }
            )
        if bt and not cover_ok:
            missing.append(
                {
                    "type": "cover",
                    "teacher": tid,
                    "topic": "",
                    "lane": "",
                    "action": f"Add cover_*.png under brand-wizard-app/public/assets/covers/ for {tid}",
                }
            )
        if plan_ok and not vid_y:
            missing.append(
                {
                    "type": "video_youtube",
                    "teacher": tid,
                    "topic": "",
                    "lane": "",
                    "action": f"PYTHONPATH=. python3 scripts/video/render_videos.py --teachers {tid}  # if script present",
                }
            )
        if plan_ok and not vid_t:
            missing.append(
                {
                    "type": "video_tiktok",
                    "teacher": tid,
                    "topic": "",
                    "lane": "",
                    "action": f"PYTHONPATH=. python3 scripts/video/render_videos.py --teachers {tid} --platform tiktok  # if supported",
                }
            )

    teachers_with_plan = sum(1 for row in per_teacher if row["video_plan"])
    video_rendered_configured = max(26, teachers_with_plan * 2) if teachers_with_plan else 26

    def stat(conf: int, built: int) -> dict[str, Any]:
        st = TypeStats(configured=conf, built=built)
        return {"configured": st.configured, "built": st.built, "pct": st.pct()}

    by_type: dict[str, dict[str, Any]] = {
        "book_text": stat(max(catalog_rows, 1), book_built),
        "epub": stat(max(catalog_rows, 1), epub_built),
        "cover": stat(max(catalog_rows, 1), cover_built),
        "manga_cover": stat(800, manga_cover_built),
        "manga_panels": stat(500, manga_panel_built),
        "video_plan": stat(26, video_plan_built),
        "video_rendered": stat(video_rendered_configured, video_rendered_built),
        "audio_presenter": stat(200, audio_built),
        "atoms_canonical": stat(6500, canonical_atoms),
    }

    total_built_deliverables = (
        book_built
        + epub_built
        + cover_built
        + manga_cover_built
        + manga_panel_built
        + video_plan_built
        + video_rendered_built
        + audio_built
    )
    total_built_assets = total_built_deliverables + canonical_atoms

    coverage_pct = (
        round(100.0 * total_built_deliverables / max(catalog_rows, 1), 2) if catalog_rows else 0.0
    )

    missing_capped = missing[:500]

    summary_inner = {
        "catalog_rows": catalog_rows,
        "total_configured": catalog_rows,
        "total_built": total_built_deliverables,
        "coverage_pct": coverage_pct,
        "missing_count": len(missing),
        "total_built_assets": total_built_assets,
        "by_type": by_type,
    }

    doc = {
        "scan_date": utc_today(),
        "repo_root": str(repo),
        "summary": summary_inner,
        "teachers": per_teacher,
        "missing": missing_capped,
        "missing_sample": missing[:200],
        "commands": {
            "scan": "python3 scripts/inventory/scan_content_inventory.py",
            "content_coverage": "PYTHONPATH=. python3 scripts/ci/content_coverage_report.py",
            "videos_dry": "python3 scripts/video/render_videos.py --dry-run  # if script present",
            "videos": "python3 scripts/video/render_videos.py  # if script present",
            "manga_assemble": "python3 scripts/release/build_manga_webtoon.py  # if script present",
            "presenter_audio": "PYTHONPATH=. python3 scripts/audio/generate_presenter_audio.py --deck intro  # if script present",
            "epub": "python3 scripts/release/build_epub.py  # if script present",
        },
    }

    json_path = out_dir / "content_inventory.json"
    json_text = json.dumps(doc, indent=2)
    json_path.write_text(json_text, encoding="utf-8")

    public_data = repo / "brand-wizard-app" / "public" / "data"
    public_data.mkdir(parents=True, exist_ok=True)
    public_json = public_data / "content_inventory.json"
    public_json.write_text(json_text, encoding="utf-8")

    md_lines = [
        f"# Content inventory — {doc['scan_date']}",
        "",
        f"- Catalog rows: **{catalog_rows}**",
        f"- Total built (deliverables rollup): **{total_built_deliverables}**",
        f"- Coverage % (vs catalog): **{coverage_pct}%**",
        f"- Missing rows: **{len(missing)}**",
        f"- Teachers: **{len(per_teacher)}**",
        "",
        "## By type",
        "",
    ]
    for k, v in by_type.items():
        md_lines.append(f"- **{k}**: built {v['built']} / configured {v['configured']} (~{v['pct']}%)")
    md_lines.extend(["", "## Missing (sample)", ""])
    for m in missing[:40]:
        md_lines.append(f"- `{m['type']}` — {m.get('teacher', '')} — {m.get('action', '')}")
    md_lines.extend(["", "Regenerate: `python3 scripts/inventory/scan_content_inventory.py`", ""])

    (out_dir / "content_inventory_summary.md").write_text("\n".join(md_lines), encoding="utf-8")
    print(f"Wrote {json_path}")
    print(f"Wrote {public_json}")
    print(f"Wrote {out_dir / 'content_inventory_summary.md'}")


if __name__ == "__main__":
    main()
