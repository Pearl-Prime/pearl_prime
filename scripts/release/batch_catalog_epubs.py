#!/usr/bin/env python3
"""Batch catalog EPUB assembly for one brand (cloud campaign worker).

Per buildable book plan:
  0. create_job.py + acknowledge_guide.py
  1. run_pipeline.py --pipeline-mode spine --quality-profile <P> --render-book
  2. build_epub.py
  3. validate_epub.py (verdict recorded; WARN does not abort)
  4. upload EPUB to R2 (never git)

Writes/updates artifacts/catalog/assembly_manifests/{brand}_{locale}.json

  PYTHONPATH=. python3 scripts/release/batch_catalog_epubs.py \\
      --brand way_stream_sanctuary --quality-profile flagship --limit 5
  PYTHONPATH=. python3 scripts/release/batch_catalog_epubs.py \\
      --brand devotion_path --quality-profile flagship --resume
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
PLANS_ROOT = REPO / "config/source_of_truth/book_plans_en_us"
ARCS = REPO / "config/source_of_truth/master_arcs"
REG = REPO / "config/brand_management/global_brand_registry_unified.yaml"
MANIFEST_DIR = REPO / "artifacts/catalog/assembly_manifests"
EPUB_ROOT = REPO / "artifacts/epubs"
RENDER_ROOT = REPO / "artifacts/rendered/catalog_assembly"
PIPELINE_TIMEOUT_SEC = int(os.environ.get("CATALOG_ASSEMBLY_PIPELINE_TIMEOUT_SEC", "300"))

_RUNTIME_ALIASES = {"standard_book_60min": "standard_book"}


def _load_yaml(p: Path) -> dict:
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def _resolve_runtime(plan: dict) -> str:
    raw = (plan.get("runtime_format_id") or plan.get("duration") or "standard_book").strip()
    return _RUNTIME_ALIASES.get(raw, raw)


def _humanize(s: str) -> str:
    return " ".join(w.capitalize() for w in s.replace("_", " ").split())


def _resolve_imprint(brand: str, locale_lane: str = "en_US") -> str:
    reg = _load_yaml(REG)
    for rec in (reg.get("brands") or {}).values():
        if rec.get("brand_archetype_id") == brand and rec.get("lane_id") == locale_lane:
            return rec.get("display_name") or rec.get("publication_corp") or _humanize(brand)
    return _humanize(brand)


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
    arc = ARCS / f"{persona}__{topic}__{engine}__{fmt}.yaml"
    if arc.is_file():
        return arc
    raise FileNotFoundError(f"no arc for {plan['book_id']}")


def _load_books(brand: str, limit: int | None, offset: int) -> list[tuple[Path, dict]]:
    files = sorted(PLANS_ROOT.glob(f"{brand}__*.yaml"))
    out: list[tuple[Path, dict]] = []
    for f in files:
        d = _load_yaml(f)
        if d.get("_needs_authoring") is True or not d.get("book_id"):
            continue
        try:
            _arc_for_book(d)
        except FileNotFoundError:
            continue
        out.append((f, d))
    if offset:
        out = out[offset:]
    if limit is not None:
        out = out[:limit]
    return out


def _pipeline_env() -> dict[str, str]:
    return {**os.environ, "PYTHONPATH": str(REPO)}


def _r2_client():
    import boto3
    from botocore.config import Config

    account = os.environ.get("R2_ACCOUNT_ID", "").strip()
    key_id = (os.environ.get("R2_ACCESS_KEY_ID") or os.environ.get("CF_R2_ACCESS_KEY") or "").strip()
    secret = (os.environ.get("R2_SECRET_ACCESS_KEY") or os.environ.get("CF_R2_SECRET_KEY") or "").strip()
    if not all([account, key_id, secret]):
        raise SystemExit("Missing R2_ACCOUNT_ID / R2_ACCESS_KEY_ID / R2_SECRET_ACCESS_KEY")
    endpoint = (os.environ.get("R2_ENDPOINT") or "").strip() or f"https://{account}.r2.cloudflarestorage.com"
    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=key_id,
        aws_secret_access_key=secret,
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )


def _bucket() -> str:
    return (os.environ.get("R2_BUCKET") or os.environ.get("CF_R2_BUCKET") or "phoenix-omega-artifacts").strip()


def _r2_key(brand: str, locale: str, book_id: str) -> str:
    return f"brand/{brand}/catalog/{locale}/{book_id}.epub"


def _r2_exists(client, key: str) -> bool:
    try:
        client.head_object(Bucket=_bucket(), Key=key)
        return True
    except Exception:
        return False


def _ensure_ebook_job(render_dir: Path, brand: str, plan: dict, arc: Path) -> tuple[bool, str]:
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
            brand,
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


def _rendered_txt(render_dir: Path, book_id: str) -> Path | None:
    d = render_dir
    if not d.is_dir():
        return None
    txts = sorted(d.glob("*.txt"))
    if txts:
        return txts[0]
    nested = list(d.glob("**/*.txt"))
    return nested[0] if nested else None


def _word_count(txt_path: Path) -> int:
    try:
        return len(txt_path.read_text(encoding="utf-8").split())
    except OSError:
        return 0


def _validate_epub(epub_path: Path) -> dict:
    cmd = [
        sys.executable,
        str(REPO / "scripts/publish/validate_epub.py"),
        "--json",
        str(epub_path),
    ]
    r = subprocess.run(cmd, cwd=str(REPO), env=_pipeline_env(), capture_output=True, text=True, timeout=120)
    try:
        data = json.loads(r.stdout)
    except json.JSONDecodeError:
        data = {"verdict": "error", "exit_code": r.returncode, "raw": (r.stderr or r.stdout)[-500:]}
    data["exit_code"] = r.returncode
    data["verdict"] = "pass" if r.returncode == 0 else "fail"
    return data


def run_one(
    brand: str,
    locale: str,
    plan: dict,
    *,
    quality_profile: str,
    dry_run: bool,
    force: bool,
    skip_r2: bool,
    imprint: str,
) -> dict:
    bid = plan["book_id"]
    r2_key = _r2_key(brand, locale, bid)
    out_epub = EPUB_ROOT / brand / f"{bid}.epub"
    cover = REPO / f"brand-wizard-app/public/assets/covers/{brand}/{bid}.png"

    if not force and not dry_run and not skip_r2:
        try:
            client = _r2_client()
            if _r2_exists(client, r2_key):
                return {
                    "book_id": bid,
                    "status": "skip_r2",
                    "r2_key": r2_key,
                }
        except SystemExit:
            pass

    if out_epub.is_file() and not force and not dry_run:
        return {"book_id": bid, "status": "skip_local", "path": str(out_epub), "r2_key": r2_key}

    parts = bid.split("__")
    persona = parts[2]
    topic = plan.get("topic") or parts[3]
    engine = plan.get("engine") or parts[4].removesuffix("__1hr")
    runtime = _resolve_runtime(plan)
    arc = _arc_for_book(plan)
    render_dir = RENDER_ROOT / brand / bid
    plan_json = render_dir / "plan.json"

    if dry_run:
        return {
            "book_id": bid,
            "status": "dry_run",
            "arc": str(arc.relative_to(REPO)),
            "r2_key": r2_key,
            "quality_profile": quality_profile,
        }

    render_dir.mkdir(parents=True, exist_ok=True)
    ok_job, job_err = _ensure_ebook_job(render_dir, brand, plan, arc)
    if not ok_job:
        return {"book_id": bid, "status": "job_setup_fail", "error": job_err, "gate_verdict": "blocked"}

    cmd = [
        sys.executable,
        str(REPO / "scripts/run_pipeline.py"),
        "--topic",
        topic,
        "--persona",
        persona,
        "--teacher",
        "default_teacher",
        "--angle",
        engine,
        "--arc",
        str(arc),
        "--pipeline-mode",
        "spine",
        "--runtime-format",
        runtime,
        "--render-book",
        "--render-dir",
        str(render_dir),
        "--workspace",
        str(render_dir),
        "--out",
        str(plan_json),
        "--quality-profile",
        quality_profile,
        "--seed",
        bid,
    ]
    r = subprocess.run(
        cmd,
        cwd=str(REPO),
        env=_pipeline_env(),
        capture_output=True,
        text=True,
        timeout=PIPELINE_TIMEOUT_SEC,
    )
    gate_verdict = "pass" if r.returncode == 0 else "pipeline_fail"
    gate_tail = (r.stderr or r.stdout)[-800:] if r.returncode != 0 else ""

    txt = _rendered_txt(render_dir, bid)
    if not txt or not txt.is_file():
        return {
            "book_id": bid,
            "status": "missing_txt",
            "gate_verdict": gate_verdict,
            "error": gate_tail or "no rendered txt",
        }

    ap = plan.get("author_positioning") or {}
    author = _humanize(ap.get("byline_author") or f"{brand} Author")
    out_epub.parent.mkdir(parents=True, exist_ok=True)
    epub_cmd = [
        sys.executable,
        str(REPO / "scripts/release/build_epub.py"),
        "--input",
        str(txt),
        "--title",
        plan.get("title") or bid,
        "--subtitle",
        plan.get("subtitle") or "",
        "--author",
        author,
        "--publisher",
        imprint,
        "--output",
        str(out_epub),
        "--topic",
        topic,
    ]
    if cover.is_file():
        epub_cmd += ["--cover", str(cover)]
    r2 = subprocess.run(epub_cmd, cwd=str(REPO), capture_output=True, text=True, timeout=600)
    if r2.returncode != 0:
        return {
            "book_id": bid,
            "status": "epub_fail",
            "gate_verdict": gate_verdict,
            "error": (r2.stderr or r2.stdout)[-500:],
        }

    validation = _validate_epub(out_epub)
    words = _word_count(txt)

    uploaded = False
    if not skip_r2:
        client = _r2_client()
        body = out_epub.read_bytes()
        client.put_object(
            Bucket=_bucket(),
            Key=r2_key,
            Body=body,
            ContentType="application/epub+zip",
        )
        uploaded = True

    return {
        "book_id": bid,
        "status": "ok",
        "path": str(out_epub.relative_to(REPO)),
        "r2_key": r2_key,
        "size": out_epub.stat().st_size,
        "sha256": hashlib.sha256(out_epub.read_bytes()).hexdigest(),
        "words": words,
        "gate_verdict": gate_verdict,
        "validation": validation.get("verdict"),
        "validation_exit_code": validation.get("exit_code"),
        "uploaded": uploaded,
        "quality_profile": quality_profile,
        "assembled_at": datetime.now(timezone.utc).isoformat(),
    }


def _load_manifest(path: Path) -> dict:
    if path.is_file():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--brand", required=True)
    ap.add_argument("--locale", default="en_US")
    ap.add_argument("--quality-profile", default="flagship", choices=["flagship", "production", "draft", "debug"])
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--resume", action="store_true", help="skip books already in manifest with status ok/skip_r2")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--skip-r2", action="store_true", help="local/CI smoke without R2 credentials")
    args = ap.parse_args()

    manifest_path = MANIFEST_DIR / f"{args.brand}_{args.locale}.json"
    prev = _load_manifest(manifest_path)
    prev_by_id = {r["book_id"]: r for r in prev.get("books", []) if r.get("book_id")}

    books = _load_books(args.brand, args.limit, args.offset)
    imprint = _resolve_imprint(args.brand, args.locale)
    results: list[dict] = []

    for _, plan in books:
        bid = plan["book_id"]
        if args.resume and not args.force:
            old = prev_by_id.get(bid)
            if old and old.get("status") in ("ok", "skip_r2", "skip_local"):
                results.append(old)
                continue
        results.append(
            run_one(
                args.brand,
                args.locale,
                plan,
                quality_profile=args.quality_profile,
                dry_run=args.dry_run,
                force=args.force,
                skip_r2=args.skip_r2,
                imprint=imprint,
            )
        )

    ok_status = {"ok", "skip_r2", "skip_local", "dry_run"}
    ok = sum(1 for r in results if r.get("status") in ok_status)
    fail = [r for r in results if r.get("status") not in ok_status]

    manifest = {
        "brand": args.brand,
        "locale": args.locale,
        "quality_profile": args.quality_profile,
        "bucket": _bucket() if not args.skip_r2 and not args.dry_run else None,
        "prefix": f"brand/{args.brand}/catalog/{args.locale}/",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "run_date": date.today().isoformat(),
        "books": results,
        "summary": {
            "total": len(results),
            "ok": ok,
            "fail": len(fail),
            "gate_fail": sum(1 for r in results if r.get("gate_verdict") not in (None, "pass")),
        },
    }

    if not args.dry_run:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        print(f"wrote manifest {manifest_path.relative_to(REPO)}")

    print(f"batch {args.brand}: n={len(results)} ok={ok} fail={len(fail)} profile={args.quality_profile}")
    for r in fail[:10]:
        print(f"  FAIL {r['book_id']}: {r.get('error') or r.get('status')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
