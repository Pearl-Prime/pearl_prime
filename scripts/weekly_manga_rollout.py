#!/usr/bin/env python3
"""
Weekly manga production lane: pick topics (image-bank gated), run ``run_manga_pipeline``,
upload to R2 under ``{brand}/manga/{date}/``, draft brand digest fragments.

Does not replace prose weekly packages (``scripts/build_weekly_brand_package.py``); it extends
delivery with a manga subsection digest artifact for brand_admin / operators.

Usage:
  PYTHONPATH=. python3 scripts/weekly_manga_rollout.py --dry-run
  PYTHONPATH=. python3 scripts/weekly_manga_rollout.py --single-book --brand stillness_press --topic burnout --genre shonen
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

from scripts.manga.r2_manga_release import DEFAULT_PRESIGN_SEC, upload_manga_release_dir  # noqa: E402
from scripts.run_manga_pipeline import count_topic_panel_pngs, run_one_book  # noqa: E402


def _load_yaml(p: Path) -> dict[str, Any]:
    if not p.exists() or yaml is None:
        return {}
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def _utc_date_slug() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _iso_week() -> int:
    return datetime.now(timezone.utc).isocalendar()[1]


def _check_comfy_url() -> tuple[bool, str]:
    base = (os.environ.get("COMFYUI_URL") or "").strip()
    if not base and os.environ.get("PEARL_STAR_IP"):
        base = f"http://{os.environ['PEARL_STAR_IP'].strip()}:8188"
    if not base:
        return False, "COMFYUI_URL or PEARL_STAR_IP not set"
    url = f"{base.rstrip('/')}/system_stats"
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=8.0) as resp:
            _ = resp.read(32)
        return True, url
    except Exception as e:
        return False, f"{url}: {e}"


def _maybe_send_operator_email(subject: str, body: str) -> None:
    key = (os.environ.get("SENDGRID_API_KEY") or "").strip()
    to = (os.environ.get("WEEKLY_ROLLOUT_OPERATOR_EMAIL") or "").strip()
    if not key or not to:
        path = REPO_ROOT / "artifacts" / "weekly_digests" / "OPERATOR_ALERT_PENDING.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {subject}\n\n{body}\n", encoding="utf-8")
        print("Wrote operator alert draft:", path)
        return
    try:
        import urllib.request

        payload = json.dumps(
            {
                "personalizations": [{"to": [{"email": to}]}],
                "from": {"email": "noreply@phoenix-omega.local", "name": "Phoenix Weekly"},
                "subject": subject,
                "content": [{"type": "text/plain", "value": body}],
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            "https://api.sendgrid.com/v3/mail/send",
            data=payload,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=20)
        print("Sent operator alert via SendGrid to", to)
    except Exception as e:
        print("SendGrid operator alert failed:", e, file=sys.stderr)


def _write_digest(
    *,
    out_dir: Path,
    brand_id: str,
    date_slug: str,
    manga_section_lines: list[str],
    failures: list[str],
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{brand_id}_weekly_digest_{date_slug}.md"
    lines = [
        f"# Weekly digest fragment — {brand_id} — {date_slug}",
        "",
        "## This week's manga",
        "",
    ]
    lines.extend(manga_section_lines or ["- _(no manga titles this week)_"])
    if failures:
        lines.extend(["", "## Manga lane failures (operator)", ""])
        lines.extend(f"- {f}" for f in failures)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def run_weekly_manga_rollout(
    *,
    dry_run: bool,
    replay_fallback: bool,
    single_book: bool,
    single_brand: str | None,
    single_topic: str | None,
    single_genre: str | None,
    config_path: Path,
) -> dict[str, Any]:
    cfg = _load_yaml(config_path)
    lane = ((cfg.get("WEEKLY_ROLLOUT_CONFIG") or {}).get("manga_lane") or {})
    min_cov = int(lane.get("require_image_bank_coverage") or cfg.get("defaults", {}).get("min_panel_images") or 56)
    backend_default = str(lane.get("image_backend") or "replay")
    if replay_fallback:
        backend_default = "replay"
    signed_ttl = int(
        (cfg.get("defaults") or {}).get("signed_url_expiry_seconds")
        or lane.get("signed_url_expiry_seconds")
        or DEFAULT_PRESIGN_SEC  # 6d; R2 rejects an ExpiresIn >= 604800 (clamped in presigned_get_url)
    )

    if backend_default in ("comfyui", "runcomfy"):
        ok, msg = _check_comfy_url()
        if not ok:
            _maybe_send_operator_email("Manga weekly rollout aborted (Pearl Star / ComfyUI)", msg)
            raise RuntimeError(f"Pearl Star unreachable; aborting weekly manga rollout: {msg}")

    brands_cfg = cfg.get("brands") or {}
    week_n = _iso_week()
    genres = list(
        lane.get("genres")
        or (cfg.get("defaults") or {}).get("genres_rotation")
        or ["shonen", "shojo", "seinen"]
    )
    date_slug = _utc_date_slug()
    summary: dict[str, Any] = {
        "date": date_slug,
        "dry_run": dry_run,
        "replay_fallback": replay_fallback,
        "degraded": "pearl_star_offline" if replay_fallback else None,
        "brands": {},
    }

    for brand_id, bcfg in brands_cfg.items():
        if not isinstance(bcfg, dict) or not bcfg.get("enabled", True):
            continue
        if single_book and single_brand and brand_id != single_brand:
            continue

        mlane = dict(lane)
        mlane.update(bcfg.get("manga_lane") or {})
        n_books = int(mlane.get("books_per_week") or 1)
        topics_pref = list(mlane.get("topics_preference") or [])
        image_backend = str(mlane.get("image_backend") or backend_default)
        digest_dir = REPO_ROOT / str(
            (bcfg.get("digest") or {}).get("digest_out_dir") or "artifacts/weekly_digests"
        ).lstrip("/")

        digest_lines: list[str] = []
        failures: list[str] = []
        uploads: list[dict[str, Any]] = []

        for _i in range(n_books):
            if single_book and single_topic:
                topic = single_topic
                genre = single_genre or genres[week_n % len(genres)]
            else:
                genre = genres[(week_n + _i) % len(genres)]
                topic = ""
                for t in topics_pref:
                    if count_topic_panel_pngs(REPO_ROOT, brand_id, t) >= min_cov:
                        topic = t
                        break
                if not topic:
                    failures.append(f"No topic with image bank ≥{min_cov} for {brand_id}; skipping manga this week.")
                    break

            persona = str(bcfg.get("default_persona") or "gen_z_professionals")
            out = REPO_ROOT / "artifacts" / "weekly_manga_runs" / brand_id / date_slug / f"{topic}_{genre}"
            try:
                book = run_one_book(
                    repo_root=REPO_ROOT,
                    brand_id=brand_id,
                    topic_id=topic,
                    persona=persona,
                    genre=genre,
                    output_dir=out,
                    min_panel_images=min_cov,
                    backend=image_backend,
                    skip_pearl_star_check=image_backend == "replay",
                    render_book=True,
                )
            except Exception as e:
                failures.append(f"{brand_id} {topic} {genre}: {e}")
                continue

            exports_dir = out / "exports"
            if dry_run:
                up = upload_manga_release_dir(
                    local_dir=exports_dir,
                    brand_id=brand_id,
                    date_slug=date_slug,
                    expires_in=signed_ttl,
                    dry_run=True,
                )
            else:
                up = upload_manga_release_dir(
                    local_dir=exports_dir,
                    brand_id=brand_id,
                    date_slug=date_slug,
                    expires_in=signed_ttl,
                    dry_run=False,
                )
            uploads.append(up)
            for obj in up.get("objects") or []:
                label = Path(str(obj.get("local", ""))).name
                digest_lines.append(f"- [{label}]({obj.get('presigned_url')})")

        digest_path = _write_digest(
            out_dir=digest_dir,
            brand_id=brand_id,
            date_slug=date_slug,
            manga_section_lines=digest_lines,
            failures=failures,
        )
        summary["brands"][brand_id] = {
            "digest_path": str(digest_path),
            "uploads": uploads,
            "failures": failures,
        }

        if failures and not dry_run:
            _maybe_send_operator_email(
                f"Manga weekly partial failure — {brand_id}",
                "\n".join(failures),
            )

    outp = REPO_ROOT / "artifacts" / "weekly_digests" / f"manga_rollout_summary_{date_slug}.json"
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return summary


def main() -> int:
    ap = argparse.ArgumentParser(description="Weekly manga rollout (R2 + digest fragments)")
    ap.add_argument("--dry-run", action="store_true", help="No R2 upload; presigned placeholders only")
    ap.add_argument(
        "--replay-fallback",
        action="store_true",
        help="Force replay image backend + degraded digest when Pearl Star offline (Hybrid C GHA path)",
    )
    ap.add_argument("--single-book", action="store_true", help="Only process one brand/topic/genre")
    ap.add_argument("--brand", default=None)
    ap.add_argument("--topic", default=None)
    ap.add_argument("--genre", default=None)
    ap.add_argument(
        "--config",
        type=Path,
        default=REPO_ROOT / "config" / "weekly_rollout" / "manga_rollout.yaml",
    )
    args = ap.parse_args()
    if yaml is None:
        print("pyyaml required", file=sys.stderr)
        return 1
    if args.single_book and (not args.brand or not args.topic):
        print("--single-book requires --brand and --topic", file=sys.stderr)
        return 1
    try:
        run_weekly_manga_rollout(
            dry_run=args.dry_run,
            replay_fallback=args.replay_fallback,
            single_book=args.single_book,
            single_brand=args.brand,
            single_topic=args.topic,
            single_genre=args.genre,
            config_path=args.config,
        )
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
