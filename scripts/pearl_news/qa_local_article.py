#!/usr/bin/env python3
"""
Run one Pearl News draft and print working QA links (file:// + optional local HTTP).
Optionally push the same article to WordPress (--publish), same meta as daily cycle.

Requires for --publish (any one):
  - Export WORDPRESS_SITE_URL, WORDPRESS_USERNAME, WORDPRESS_APP_PASSWORD, or
  - Repo file .env.wordpress.local (from scripts/integrations/setup_wordpress_local.sh)
    with WORDPRESS_KEYCHAIN_SERVICE + macOS Keychain for the app password

Usage:
  PYTHONPATH=. python3 scripts/pearl_news/qa_local_article.py
  PYTHONPATH=. python3 scripts/pearl_news/qa_local_article.py --topic climate --teacher miki --language ja --v52
  PYTHONPATH=. python3 scripts/pearl_news/qa_local_article.py --v52 --publish
  PYTHONPATH=. python3 scripts/pearl_news/qa_local_article.py --article-json artifacts/pearl_news/qa_cli/article_x.json --publish
"""
from __future__ import annotations

import argparse
import html
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_PUBLISH_LOG = REPO_ROOT / "artifacts" / "pearl_news" / "publish_log.jsonl"


def _bootstrap_wordpress_credentials_from_local() -> None:
    """Load WORDPRESS_* from .env.wordpress.local; fill app password from macOS Keychain if needed.

    Mirrors scripts/integrations/post_wordpress_draft_local.sh so one CLI works without
    manually exporting WORDPRESS_APP_PASSWORD.
    """
    env_file = REPO_ROOT / ".env.wordpress.local"
    if not env_file.is_file():
        return
    for raw in env_file.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip().strip('"').strip("'")
        if key and val and key not in os.environ:
            os.environ[key] = val
    if os.environ.get("WORDPRESS_APP_PASSWORD"):
        return
    user = (os.environ.get("WORDPRESS_USERNAME") or "").strip()
    service = (os.environ.get("WORDPRESS_KEYCHAIN_SERVICE") or "").strip()
    if not user or not service or sys.platform != "darwin":
        return
    try:
        proc = subprocess.run(
            ["security", "find-generic-password", "-a", user, "-s", service, "-w"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if proc.returncode == 0 and (proc.stdout or "").strip():
            os.environ["WORDPRESS_APP_PASSWORD"] = proc.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass


def _write_preview(article_path: Path, out_dir: Path, *, live_url: str | None = None) -> Path:
    data = json.loads(article_path.read_text(encoding="utf-8"))
    title = html.escape(data.get("title") or data.get("article_title") or "Article")
    body = data.get("content") or ""
    json_name = article_path.name
    meta_lines = [
        ("slug", data.get("slug")),
        ("teacher_id", data.get("teacher_id")),
        ("topic", data.get("topic")),
        ("language", data.get("language")),
        ("qc_passed", data.get("qc_passed")),
        ("source_json", json_name),
    ]
    if live_url:
        meta_lines.append(("live_wp_url", live_url))
    meta_html = "<br/>".join(
        f"<code>{html.escape(str(k))}</code>: {html.escape(str(v))}" for k, v in meta_lines
    )
    live_block = ""
    if live_url:
        esc = html.escape(live_url, quote=True)
        live_block = (
            f'<p><strong>Live on WordPress:</strong><br/><a href="{esc}">{html.escape(live_url)}</a></p>'
        )
    preview_path = out_dir / "qa_preview.html"
    file_uri = preview_path.resolve().as_uri()
    json_uri = article_path.resolve().as_uri()

    preview_path.write_text(
        f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>QA — {title}</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 48rem; margin: 2rem auto; padding: 0 1rem; color: #111; }}
    .qa-links {{
      margin-bottom: 1.25rem; padding: 1rem 1.1rem; background: #0f172a; color: #e2e8f0;
      border-radius: 10px; font-size: 0.9rem; line-height: 1.55;
    }}
    .qa-links a {{ color: #7dd3fc; word-break: break-all; }}
    .qa-links h1 {{ font-size: 1rem; margin: 0 0 0.6rem 0; color: #fff; font-weight: 600; }}
    .meta {{ font-size: 0.85rem; color: #555; margin-bottom: 1.5rem; padding: 1rem; background: #f6f6f6; border-radius: 8px; }}
    .meta code {{ font-size: 0.8rem; }}
    article {{ line-height: 1.5; }}
  </style>
</head>
<body>
  <div class="qa-links">
    <h1>Pearl News — QA links</h1>
    {live_block}
    <p><strong>Raw JSON (relative, works with local server):</strong><br/>
      <a href="./{html.escape(json_name, quote=True)}">{html.escape(json_name)}</a></p>
    <p><strong>Same file as file:// (copy if you open this page via file):</strong><br/>
      <a href="{html.escape(json_uri, quote=True)}">Open JSON (file)</a></p>
    <p><strong>This preview as file://:</strong><br/>
      <a href="{html.escape(file_uri, quote=True)}">Reload via file URI</a></p>
  </div>
  <div class="meta"><strong>Article meta</strong><br/>{meta_html}</div>
  <article>{body}</article>
</body>
</html>""",
        encoding="utf-8",
    )
    return preview_path


def _append_publish_log(entry: dict, log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _publish_article_json(article_path: Path, *, status: str) -> str:
    """Post article JSON to WordPress; return public post URL."""
    from pearl_news.publish.wordpress_client import WordPressPublishError, post_article

    data = json.loads(article_path.read_text(encoding="utf-8"))
    title = data.get("title") or data.get("headline", "")
    content = data.get("content") or data.get("body", "")
    if not title or not content:
        raise ValueError(f"Article {article_path} missing title or content")

    featured_image_path = data.get("featured_image_path")
    if featured_image_path:
        featured_image_path = REPO_ROOT / featured_image_path

    try:
        result = post_article(
            title=title,
            content=content,
            status=status,
            slug=data.get("slug"),
            author=data.get("author"),
            meta={
                "pearl_news_layout": "sidebar",
                "pearl_news_template": "sidebar",
            },
            featured_image=data.get("featured_image"),
            featured_image_url=data.get("featured_image_url"),
            featured_image_path=featured_image_path,
        )
    except WordPressPublishError:
        raise
    wp_url = (result.get("link") or "") or (result.get("guid") or {}).get("rendered", "")
    if not wp_url:
        wp_url = str(result.get("id", ""))
    return str(wp_url).strip()


def main() -> int:
    ap = argparse.ArgumentParser(description="Run one Pearl News article and print QA links.")
    ap.add_argument(
        "--article-json",
        type=Path,
        default=None,
        help="Use this article JSON instead of running the pipeline (parent dir = preview out dir)",
    )
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=REPO_ROOT / "artifacts" / "pearl_news" / "qa_cli",
        help="Output directory for drafts + qa_preview.html",
    )
    ap.add_argument("--language", default="en")
    ap.add_argument("--topic", default="mental_health")
    ap.add_argument("--teacher", default="maat")
    ap.add_argument("--limit", type=int, default=1)
    ap.add_argument("--v52", action="store_true", help="Pass --v52 to run_article_pipeline")
    ap.add_argument(
        "--open",
        action="store_true",
        help="On macOS, open the HTML preview in the default browser",
    )
    ap.add_argument("--http-port", type=int, default=8899, help="Suggested port for python -m http.server")
    ap.add_argument(
        "--publish",
        action="store_true",
        help="Post the article to WordPress (needs WORDPRESS_* env vars)",
    )
    ap.add_argument(
        "--wp-status",
        choices=("draft", "publish"),
        default="publish",
        help="WordPress post status when using --publish (default: publish = live)",
    )
    ap.add_argument(
        "--publish-log",
        type=Path,
        default=DEFAULT_PUBLISH_LOG,
        help="Append JSON lines for each publish attempt",
    )
    args = ap.parse_args()

    if args.publish:
        _bootstrap_wordpress_credentials_from_local()

    out_dir = args.out_dir
    if not out_dir.is_absolute():
        out_dir = REPO_ROOT / out_dir

    if args.article_json:
        article_path = args.article_json
        if not article_path.is_absolute():
            article_path = REPO_ROOT / article_path
        if not article_path.is_file():
            print("ERROR: --article-json not found:", article_path, file=sys.stderr)
            return 1
        out_dir = article_path.parent
    else:
        out_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            sys.executable,
            "-m",
            "pearl_news.pipeline.run_article_pipeline",
            "--language",
            args.language,
            "--topic",
            args.topic,
            "--teacher",
            args.teacher,
            "--out-dir",
            str(out_dir),
            "--limit",
            str(args.limit),
        ]
        if args.v52:
            cmd.append("--v52")

        env = {**os.environ, "PYTHONPATH": str(REPO_ROOT)}
        print("Running:", " ".join(cmd), file=sys.stderr)
        r = subprocess.run(cmd, cwd=str(REPO_ROOT), env=env)
        if r.returncode != 0:
            return r.returncode

        articles = sorted(out_dir.glob("article_*.json"))
        if not articles:
            print("ERROR: No article_*.json in", out_dir, file=sys.stderr)
            return 1

        article_path = articles[0]

    live_url: str | None = None
    publish_failed = False
    if args.publish:
        try:
            live_url = _publish_article_json(article_path, status=args.wp_status)
        except Exception as exc:
            publish_failed = True
            print("ERROR: WordPress publish failed:", exc, file=sys.stderr)
            print(
                "Set WORDPRESS_SITE_URL, WORDPRESS_USERNAME, WORDPRESS_APP_PASSWORD and retry.",
                file=sys.stderr,
            )
            log_path = args.publish_log
            if not log_path.is_absolute():
                log_path = REPO_ROOT / log_path
            _append_publish_log(
                {
                    "source": "qa_local_article",
                    "article_path": str(article_path),
                    "published_at": datetime.now(timezone.utc).isoformat(),
                    "status": "failed",
                    "error": str(exc),
                },
                log_path,
            )
        else:
            log_path = args.publish_log
            if not log_path.is_absolute():
                log_path = REPO_ROOT / log_path
            data = json.loads(article_path.read_text(encoding="utf-8"))
            _append_publish_log(
                {
                    "source": "qa_local_article",
                    "teacher_id": data.get("teacher_id"),
                    "language": data.get("language"),
                    "title": data.get("title"),
                    "article_path": str(article_path),
                    "wp_url": live_url,
                    "wp_status": args.wp_status,
                    "published_at": datetime.now(timezone.utc).isoformat(),
                    "status": args.wp_status,
                },
                log_path,
            )

    preview_path = _write_preview(article_path, out_dir, live_url=live_url)
    preview_uri = preview_path.resolve().as_uri()
    json_uri = article_path.resolve().as_uri()

    sep = "=" * 80
    print(sep)
    print("PEARL NEWS — QA (copy into browser or terminal)")
    print(sep)
    print("PREVIEW (file — double-click or paste into address bar):")
    print(" ", preview_uri)
    print()
    print("RAW JSON (file):")
    print(" ", json_uri)
    print()
    print("PREVIEW (HTTP — links inside page work for JSON too):")
    print(f"  cd {out_dir} && python3 -m http.server {args.http_port}")
    print(f"  http://127.0.0.1:{args.http_port}/qa_preview.html")
    print(sep)
    if live_url:
        print(sep)
        print("WORDPRESS — LIVE POST")
        print(sep)
        print(" ", live_url)
        print(sep)

    if args.open and sys.platform == "darwin":
        subprocess.run(["open", str(preview_path)], check=False)
    return 1 if publish_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
