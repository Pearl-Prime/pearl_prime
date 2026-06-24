#!/usr/bin/env python3
"""Ensure flagship landings have data-ghl-webhook on <body> for phoenix_lead.js."""
from __future__ import annotations

import os
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CONFIG = REPO / "config/freebies/ghl_funnel_capture.yaml"


def _load_yaml(p: Path) -> dict:
    import yaml
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def _inject_body(path: Path, webhook: str) -> bool:
    text = path.read_text(encoding="utf-8")
    if "data-ghl-webhook" in text:
        text = re.sub(
            r'<body([^>]*)\sdata-ghl-webhook="[^"]*"',
            f'<body\\1 data-ghl-webhook="{webhook}"',
            text,
            count=1,
        )
        if webhook and f'data-ghl-webhook="{webhook}"' not in text:
            text = re.sub(
                r"<body([^>]*)>",
                f'<body\\1 data-ghl-webhook="{webhook}">',
                text,
                count=1,
            )
    else:
        text = re.sub(
            r"<body([^>]*)>",
            f'<body\\1 data-ghl-webhook="{webhook}">',
            text,
            count=1,
        )
    if text != path.read_text(encoding="utf-8"):
        path.write_text(text, encoding="utf-8")
        return True
    return False


def _page_paths(cfg: dict) -> list[str]:
    pages: list[str] = []
    for entry in cfg.get("funnel_pages") or []:
        if isinstance(entry, dict):
            rel = entry.get("path") or ""
        else:
            rel = str(entry)
        if rel:
            pages.append(rel)
    if not pages:
        pages = list(cfg.get("flagship_pages") or [])
    return pages


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Inject GHL webhook URL into funnel landings")
    parser.add_argument(
        "--require-env",
        action="store_true",
        help="Exit 1 if PHOENIX_GHL_FUNNEL_WEBHOOK is unset (production deploy gate)",
    )
    parser.add_argument(
        "--webhook-file",
        default=str(REPO / "config/local/ghl_funnel_webhook.url"),
        help="Fallback file with inbound webhook URL (one line, gitignored)",
    )
    args = parser.parse_args()
    cfg = _load_yaml(CONFIG)
    env_name = cfg.get("webhook_env") or "PHOENIX_GHL_FUNNEL_WEBHOOK"
    env_webhook = os.environ.get(env_name, "").strip()
    webhook = env_webhook
    if not webhook and not args.require_env:
        wf = Path(args.webhook_file)
        if wf.is_file():
            lines = [
                ln.strip()
                for ln in wf.read_text(encoding="utf-8").splitlines()
                if ln.strip()
            ]
            webhook = lines[0] if lines else ""
    pages = _page_paths(cfg)
    n = 0
    for rel in pages:
        path = REPO / rel
        if not path.exists():
            print(f"missing: {path}")
            continue
        if _inject_body(path, webhook):
            n += 1
            print(f"patched {rel}")
    if not webhook:
        print(f"note: {env_name} unset — body attr left empty (capture skips until deploy)")
        if args.require_env and not env_webhook:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
