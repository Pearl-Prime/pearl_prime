#!/usr/bin/env python3
"""Translate stillness_press manga lettering (captions/dialogue/SFX) to ja_JP.

The rendered panels are language-agnostic art; only the lettering layer is
localized (per the series plans, ja webtoon cadence is bi-weekly). This extracts
the CAP / THT / DLG / SFX lines from each en_US render-ready markdown script and
translates them via Qwen on Pearl Star (Tier 2), emitting a per-series
`<series>_ep001.lettering.ja.json` of {panel_id: {kind, en, ja}}.

NO image re-render needed — the ja lettering is composited over the existing
panels downstream. Tier-2 compliant (Qwen only); audit_llm_callers stays clean.

Usage:
  eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
  python3 translate_manga_lettering_ja.py --series 2
  python3 translate_manga_lettering_ja.py --series 3
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "en_US" / "manga" / "scripts"
SERIES_SCRIPT = {
    "2": "series2_the_night_before_you_sleep_ep001.md",
    "3": "series3_hands_shoulders_breath_ep001.md",
}

SYSTEM = (
    "You are a professional Japanese manga letterer/translator. Translate the "
    "English manga caption or line of dialogue into natural, emotionally faithful "
    "Japanese suitable for lettering into a panel. Keep it concise. Output ONLY "
    "the Japanese — no romaji, no English, no quotes, no notes."
)

PANEL_RE = re.compile(r"^\*\*P(\d+)\*\*")
# lettering lines look like: "> **CAP:** text"  /  "> **THT:** text" / "> **DLG:** text"
LETTER_RE = re.compile(r"^>\s*\*\*(CAP|THT|DLG|SFX)\:?\*\*\s*(.+)$")
# some lines are "> **THT:** a · **THT:** b" — split on the bold markers


def _ollama_host() -> str:
    base = os.environ.get("QWEN_BASE_URL", "").rstrip("/")
    if not base:
        sys.exit('QWEN_BASE_URL not set — load Keychain env first')
    return base[:-3] if base.endswith("/v1") else base


def qwen(text: str, *, model: str = "qwen2.5:14b", retries: int = 4) -> str:
    host = _ollama_host()
    payload = json.dumps({
        "model": model, "prompt": f"{SYSTEM}\n\n---\n{text}\n---",
        "stream": False, "options": {"temperature": 0.3, "num_predict": 512},
    }).encode()
    last = ""
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(host + "/api/generate", data=payload,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=120) as r:
                out = json.loads(r.read())
            reply = re.sub(r"<think>.*?</think>", "", out.get("response", ""),
                           flags=re.DOTALL).strip().strip("「」\"' ")
            if len(reply) >= 1:
                return reply
            last = "empty"
        except Exception as e:  # noqa: BLE001
            last = str(e)
        time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"qwen failed: {last}")


def extract_lettering(script_path: Path) -> list[dict]:
    """Return [{panel_id, kind, en}, ...] for each lettering line."""
    items: list[dict] = []
    cur_panel = None
    for raw in script_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        pm = PANEL_RE.match(line)
        if pm:
            cur_panel = f"ep001_{int(pm.group(1)):03d}"
            continue
        lm = LETTER_RE.match(line)
        if lm and cur_panel:
            kind = lm.group(1)
            body = lm.group(2)
            # split multi-segment lines like "a · **THT:** b"
            segs = re.split(r"\s*·\s*\*\*[A-Z]+\:?\*\*\s*", body)
            for seg in segs:
                seg = seg.replace("**", "").replace("*", "").strip()
                if seg and seg != "(no text)":
                    items.append({"panel_id": cur_panel, "kind": kind, "en": seg})
    return items


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--series", required=True, choices=list(SERIES_SCRIPT))
    args = ap.parse_args()
    script = SCRIPTS / SERIES_SCRIPT[args.series]
    items = extract_lettering(script)
    out_path = HERE / "manga" / f"series{args.series}_ep001.lettering.ja.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"=== Series {args.series}: {len(items)} lettering lines ===")
    for it in items:
        it["ja"] = qwen(it["en"])
        print(f"  {it['panel_id']} [{it['kind']}] {it['en'][:34]!r} -> {it['ja'][:24]!r}")
    out_path.write_text(json.dumps({
        "series": args.series, "episode": "ep_001", "locale": "ja_JP",
        "source_locale": "en_US", "backend": "qwen2.5:14b@pearlstar",
        "lines": items,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {out_path} ({len(items)} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
