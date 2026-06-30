#!/usr/bin/env python3
"""After ``run_manga_pipeline``: upload exports to R2 and email digest links (SendGrid)."""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts.manga.r2_manga_release import DEFAULT_PRESIGN_SEC, upload_manga_release_dir  # noqa: E402


def resolve_exports_dir(out_root: Path) -> Path:
    """Prefer ``out_root/exports``; else latest ``out_root/chapter_*/exports`` with files."""
    direct = out_root / "exports"
    if direct.is_dir() and any(direct.iterdir()):
        return direct
    candidates = sorted(out_root.glob("chapter_*/exports"))
    for c in reversed(candidates):
        if c.is_dir() and any(c.iterdir()):
            return c
    return direct


def _send_digest_email(*, subject: str, body: str) -> None:
    key = (os.environ.get("SENDGRID_API_KEY") or "").strip()
    to = (os.environ.get("WEEKLY_ROLLOUT_OPERATOR_EMAIL") or "").strip()
    if not key or not to:
        out = REPO_ROOT / "artifacts" / "weekly_digests" / "SMOKE_DIGEST_PENDING.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(f"# {subject}\n\n{body}\n", encoding="utf-8")
        print("Wrote digest draft (missing SendGrid or operator email):", out)
        return
    import urllib.request

    payload = json.dumps(
        {
            "personalizations": [{"to": [{"email": to}]}],
            "from": {"email": "noreply@phoenix-omega.local", "name": "Phoenix Manga Smoke"},
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
    urllib.request.urlopen(req, timeout=25)
    print("Sent digest email to", to)


def main() -> int:
    ap = argparse.ArgumentParser(description="R2 upload + digest for manga smoke exports")
    ap.add_argument("--brand", required=True)
    ap.add_argument("--topic", required=True)
    ap.add_argument("--genre", required=True)
    ap.add_argument(
        "--exports-dir",
        type=Path,
        default=None,
        help="Directory with PDF/CBZ/EPUB (default: resolve under smoke out root)",
    )
    ap.add_argument(
        "--smoke-out-root",
        type=Path,
        default=None,
        help="If set with no --exports-dir, resolve exports from this tree (e.g. artifacts/manga_smoke)",
    )
    ap.add_argument("--date-slug", default="", help="R2 path date (default UTC today)")
    ap.add_argument("--upload-to-r2", action="store_true")
    ap.add_argument("--send-digest", action="store_true")
    args = ap.parse_args()

    if args.exports_dir is not None:
        exports = args.exports_dir.resolve()
    elif args.smoke_out_root is not None:
        exports = resolve_exports_dir(args.smoke_out_root.resolve())
    else:
        print("Provide --exports-dir or --smoke-out-root", file=sys.stderr)
        return 1

    if args.send_digest and not args.upload_to_r2:
        print("ERROR: --send-digest requires --upload-to-r2 (digest lists signed URLs from upload)", file=sys.stderr)
        return 1

    if not exports.is_dir():
        print(f"Exports dir missing: {exports}", file=sys.stderr)
        return 1

    date_slug = args.date_slug or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    summary: dict = {"exports_dir": str(exports), "upload": None}

    if args.upload_to_r2:
        summary["upload"] = upload_manga_release_dir(
            local_dir=exports,
            brand_id=args.brand,
            date_slug=date_slug,
            expires_in=DEFAULT_PRESIGN_SEC,  # < R2's 1-week ceiling (clamped again in presigned_get_url)
            dry_run=False,
        )
        (REPO_ROOT / "artifacts" / "manga_smoke").mkdir(parents=True, exist_ok=True)
        (REPO_ROOT / "artifacts" / "manga_smoke" / "smoke_r2_summary.json").write_text(
            json.dumps(summary, indent=2) + "\n", encoding="utf-8"
        )

    if args.send_digest:
        lines = [
            f"Manga smoke — {args.brand} / {args.topic} / {args.genre}",
            f"Date: {date_slug}",
            "",
            "Downloads:",
        ]
        for obj in (summary.get("upload") or {}).get("objects") or []:
            lines.append(f"- {obj.get('key')}: {obj.get('presigned_url')}")
        if not lines[-1].startswith("-"):
            lines.append("(no upload objects — run with --upload-to-r2)")
        _send_digest_email(subject=f"Manga smoke digest — {args.topic} — {date_slug}", body="\n".join(lines))

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
