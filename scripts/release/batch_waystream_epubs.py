#!/usr/bin/env python3
"""Batch Waystream Sanctuary EPUB production (pilot → full 800, resumable).

Per plan book_id:
  0. create_job.py (ebook) + acknowledge_guide.py in workspace
  1. run_pipeline.py --pipeline-mode spine --render-book --workspace <dir>
  2. build_epub.py with plan metadata + plan-keyed cover

Outputs: artifacts/weekly_packages/way_stream_sanctuary/{week}/amazon_kdp/{book_id}.epub

  PYTHONPATH=. python3 scripts/release/batch_waystream_epubs.py --pilot --dry-run
  PYTHONPATH=. python3 scripts/release/batch_waystream_epubs.py --pilot
  PYTHONPATH=. python3 scripts/release/batch_waystream_epubs.py --all --resume
  PYTHONPATH=. python3 scripts/release/cadence_reslice_deliveries.py \\
      --brand-dir artifacts/weekly_packages/way_stream_sanctuary --from-week 2026-W26 --platform amazon_kdp --lane en
  PYTHONPATH=. python3 scripts/onboarding/gen_brand_deliveries.py
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
BRAND = "way_stream_sanctuary"
PLANS = REPO / "config/source_of_truth/book_plans_en_us"
SERIES = REPO / "config/source_of_truth/series_plans_en_us"
COVERS = REPO / "brand-wizard-app/public/assets/covers/way_stream_sanctuary"
RENDERED = REPO / "artifacts/rendered/waystream_batch"
STATE = REPO / "artifacts/waystream/batch_epub_state.json"
PILOT_N = 18
IMPRINT = "Waystream Sanctuary"


def _iso_week() -> str:
    iso = date.today().isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


def _load_yaml(p: Path) -> dict:
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def _humanize(s: str) -> str:
    return " ".join(w.capitalize() for w in s.replace("_", " ").split())


def _arc_for_book(plan: dict) -> Path:
    sp_path = REPO / (plan.get("series_plan") or "")
    if sp_path.is_file():
        sp = _load_yaml(sp_path)
        bid = plan["book_id"]
        for inst in (sp.get("arc") or {}).values():
            if inst.get("book_id") == bid and inst.get("master_arc"):
                return REPO / inst["master_arc"]
    parts = plan["book_id"].split("__")
    persona = parts[2] if len(parts) > 2 else ""
    topic = parts[3] if len(parts) > 3 else plan.get("topic", "")
    engine = plan.get("engine") or (parts[4].removesuffix("__1hr") if len(parts) > 4 else "")
    fmt = plan.get("structural_format_id") or "F006"
    arc = REPO / f"config/source_of_truth/master_arcs/{persona}__{topic}__{engine}__{fmt}.yaml"
    if arc.is_file():
        return arc
    raise FileNotFoundError(f"no arc for {plan['book_id']}")


def load_books(limit: int | None = None, offset: int = 0) -> list[tuple[Path, dict]]:
    files = sorted(PLANS.glob(f"{BRAND}__*.yaml"))
    out = []
    for f in files:
        d = _load_yaml(f)
        if d.get("_needs_authoring") is False and d.get("book_id"):
            out.append((f, d))
    if offset:
        out = out[offset:]
    if limit is not None:
        out = out[:limit]
    return out


def _rendered_txt(book_id: str) -> Path | None:
    d = RENDERED / book_id
    if not d.is_dir():
        return None
    txts = sorted(d.glob("*.txt"))
    return txts[0] if txts else None


def _pipeline_env() -> dict[str, str]:
    return {**os.environ, "PYTHONPATH": str(REPO)}


def _ensure_ebook_job(render_dir: Path, plan: dict, arc: Path) -> tuple[bool, str]:
    """Create job.json and acknowledge guide (required by run_pipeline gate)."""
    jf = render_dir / "job.json"
    parts = plan["book_id"].split("__")
    persona = parts[2]
    topic = plan.get("topic") or parts[3]
    env = _pipeline_env()
    if not jf.is_file():
        cmd = [
            sys.executable,
            str(REPO / "scripts/pipeline/create_job.py"),
            "--pipeline",
            "ebook",
            "--workspace",
            str(render_dir),
            "--brand",
            BRAND,
            "--locale",
            "en-US",
            "--topic",
            topic,
            "--persona",
            persona,
            "--arc",
            str(arc),
            "--teacher",
            "default_teacher",
        ]
        r = subprocess.run(cmd, cwd=str(REPO), env=env, capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            return False, (r.stderr or r.stdout)[-500:]
    need_ack = True
    if jf.is_file():
        job = json.loads(jf.read_text(encoding="utf-8"))
        need_ack = not job.get("guide_acknowledged")
    if need_ack:
        r2 = subprocess.run(
            [
                sys.executable,
                str(REPO / "scripts/pipeline/acknowledge_guide.py"),
                "--workspace",
                str(render_dir),
            ],
            cwd=str(REPO),
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if r2.returncode != 0:
            return False, (r2.stderr or r2.stdout)[-500:]
    return True, "ok"


def run_one(plan: dict, week: str, dry_run: bool, force: bool) -> dict:
    bid = plan["book_id"]
    out_epub = REPO / "artifacts/weekly_packages" / BRAND / week / "amazon_kdp" / f"{bid}.epub"
    if out_epub.is_file() and not force:
        return {"book_id": bid, "status": "skip_exists", "path": str(out_epub)}
    parts = bid.split("__")
    persona = parts[2]
    topic = plan.get("topic") or parts[3]
    engine = plan.get("engine") or parts[4].removesuffix("__1hr")
    runtime = plan.get("runtime_format_id") or "one_hour_book"
    arc = _arc_for_book(plan)
    render_dir = RENDERED / bid
    plan_json = render_dir / "plan.json"

    if dry_run:
        return {
            "book_id": bid, "status": "dry_run",
            "arc": str(arc.relative_to(REPO)),
            "out": str(out_epub.relative_to(REPO)),
        }

    render_dir.mkdir(parents=True, exist_ok=True)
    ok_job, job_err = _ensure_ebook_job(render_dir, plan, arc)
    if not ok_job:
        return {"book_id": bid, "status": "job_setup_fail", "error": job_err}
    cmd = [
        sys.executable, str(REPO / "scripts/run_pipeline.py"),
        "--topic", topic,
        "--persona", persona,
        "--teacher", "default_teacher",
        "--angle", engine,
        "--arc", str(arc),
        "--pipeline-mode", "spine",
        "--runtime-format", runtime,
        "--render-book",
        "--render-dir", str(render_dir),
        "--workspace", str(render_dir),
        "--out", str(plan_json),
        "--quality-profile", "production",
        "--seed", bid,
    ]
    r = subprocess.run(cmd, cwd=str(REPO), env=_pipeline_env(),
                       capture_output=True, text=True, timeout=7200)
    if r.returncode != 0:
        return {"book_id": bid, "status": "pipeline_fail", "error": (r.stderr or r.stdout)[-500:]}

    txt = _rendered_txt(bid)
    if not txt:
        txts = list(render_dir.glob("**/*.txt"))
        txt = txts[0] if txts else None
    if not txt or not txt.is_file():
        return {"book_id": bid, "status": "missing_txt"}

    ap = plan.get("author_positioning") or {}
    author = _humanize(ap.get("byline_author") or "Waystream Author")
    cover = COVERS / f"{bid}.png"
    out_epub.parent.mkdir(parents=True, exist_ok=True)
    epub_cmd = [
        sys.executable, str(REPO / "scripts/release/build_epub.py"),
        "--input", str(txt),
        "--title", plan.get("title") or bid,
        "--subtitle", plan.get("subtitle") or "",
        "--author", author,
        "--publisher", IMPRINT,
        "--cover", str(cover) if cover.is_file() else "",
        "--output", str(out_epub),
        "--topic", topic,
    ]
    epub_cmd = [c for c in epub_cmd if c]
    r2 = subprocess.run(epub_cmd, cwd=str(REPO), capture_output=True, text=True, timeout=600)
    if r2.returncode != 0:
        return {"book_id": bid, "status": "epub_fail", "error": (r2.stderr or r2.stdout)[-500:]}
    return {"book_id": bid, "status": "ok", "path": str(out_epub), "size": out_epub.stat().st_size}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", action="store_true", help=f"first {PILOT_N} books only")
    ap.add_argument("--all", action="store_true", help="full 800-book wave")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--resume", action="store_true", help="skip books with existing EPUB")
    ap.add_argument("--force", action="store_true", help="rebuild even if EPUB exists")
    ap.add_argument("--week", default=None, help="ISO week folder (default: current week)")
    ap.add_argument("--offset", type=int, default=0)
    args = ap.parse_args()
    if not args.pilot and not args.all:
        ap.error("specify --pilot or --all")

    limit = PILOT_N if args.pilot else None
    books = load_books(limit=limit, offset=args.offset)
    week = args.week or _iso_week()
    results = []
    for _, plan in books:
        results.append(run_one(plan, week, args.dry_run, force=args.force))

    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps({"week": week, "results": results}, indent=2), encoding="utf-8")
    ok = sum(1 for r in results if r["status"] in ("ok", "skip_exists", "dry_run"))
    fail = [r for r in results if r["status"] not in ("ok", "skip_exists", "dry_run")]
    print(f"batch: n={len(results)} ok={ok} fail={len(fail)} week={week}")
    for r in fail[:10]:
        print(f"  FAIL {r['book_id']}: {r.get('error') or r['status']}")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
