#!/usr/bin/env python3
"""
Lightweight HTTP server coordinating 30 browser-tab translation workers.

zh-TW tabs 1-10   → Qwen Chat (qwen.ai)
zh-CN tabs 11-20  → Qwen Chat (qwen.ai)
ja-JP tabs 21-30  → Rakuten AI Chat (ai.rakuten.co.jp)

Endpoints:
    GET  /next?locale=zh-TW&tab=3   → next pending atom JSON or {"done": true}
    POST /submit                     → write result, update state
    GET  /status                     → JSON progress per locale
    GET  /dashboard                  → HTML progress page (auto-refresh 10s)

State persists in artifacts/translation/browser_queues/{locale}_state.json
(survives server restart).

Usage:
    python3 scripts/translation/browser_queue_server.py --port 8765
"""
from __future__ import annotations

import html
import json
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Optional
from urllib.parse import parse_qs, urlparse

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

QUEUES_DIR = REPO_ROOT / "artifacts/translation/browser_queues"
FAILURES_DIR = REPO_ROOT / "artifacts/translation/browser_failures"

# Chat service URLs (informational — shown in dashboard)
CHAT_SERVICES = {
    "zh-TW": "https://chat.qwen.ai",
    "zh-CN": "https://chat.qwen.ai",
    "ja-JP": "https://ai.rakuten.co.jp",
}

# System prompts (from spec Section 3 — paste as first message in each tab)
SYSTEM_PROMPTS = {
    "zh-TW": (
        "You are a professional translator specializing in therapeutic self-help content.\n"
        "Translate English text into Traditional Chinese (繁體中文) for Taiwan audiences.\n"
        "Use a warm, direct, second-person voice — address the reader as 「你」, never 「人們」 or 「讀者」.\n"
        "Do not use clinical or academic language. Write as a wise, caring friend would speak.\n"
        "Preserve emotional tension and short punch lines as short punch lines.\n\n"
        "CRITICAL FORMAT RULES — follow exactly:\n"
        "1. Copy ALL format markers character-for-character, NEVER translate them:\n"
        '   - Lines matching "--- variant: v\\d+" → copy exactly\n'
        '   - Lines that are exactly "---" → copy exactly\n'
        '   - Lines matching "## [A-Z_]+ v\\d+" → copy exactly (e.g. "## HOOK v01")\n'
        '   - Lines matching "### SOURCE: ..." → copy exactly\n'
        "   - YAML-like lines (key: value) between --- markers → copy exactly\n"
        '   - Lines matching "path: ..." → copy exactly\n'
        '   - Lines matching "[A-Z_]+: \\d+" → copy exactly (metadata)\n'
        "2. Translate ONLY the prose text paragraphs between format markers.\n"
        "3. Do NOT add any commentary, headings, or notes of your own.\n"
        "4. Do NOT wrap the output in code blocks.\n"
        "5. Preserve blank lines exactly as they appear in the source.\n\n"
        "Reply ONLY with the translated text. No preamble. No explanation."
    ),
    "zh-CN": (
        "You are a professional translator specializing in therapeutic self-help content.\n"
        "Translate English text into Simplified Chinese (简体中文) for Mainland China audiences.\n"
        "Use a warm, direct, second-person voice — address the reader as 「你」.\n"
        "Do not use clinical or academic language. Write as a wise, caring friend would speak.\n"
        "Preserve emotional tension and short punch lines as short punch lines.\n\n"
        "CRITICAL FORMAT RULES — follow exactly:\n"
        "1. Copy ALL format markers character-for-character, NEVER translate them:\n"
        '   - Lines matching "--- variant: v\\d+" → copy exactly\n'
        '   - Lines that are exactly "---" → copy exactly\n'
        '   - Lines matching "## [A-Z_]+ v\\d+" → copy exactly\n'
        "   - YAML-like lines between --- markers → copy exactly\n"
        "2. Translate ONLY the prose text paragraphs between format markers.\n"
        "3. Do NOT add commentary, headings, or notes.\n"
        "4. Do NOT wrap output in code blocks.\n"
        "5. Preserve blank lines exactly.\n\n"
        "Reply ONLY with the translated text. No preamble. No explanation."
    ),
    "ja-JP": (
        "You are a professional translator specializing in therapeutic self-help content.\n"
        "Translate English text into Japanese (日本語).\n"
        "Use warm, natural です/ます style — address the reader as 「あなた」.\n"
        "Do not use clinical or academic language. Write with warmth and directness.\n"
        "Preserve emotional tension and short punch lines as short punch lines.\n\n"
        "CRITICAL FORMAT RULES — follow exactly:\n"
        "1. Copy ALL format markers character-for-character, NEVER translate them:\n"
        '   - Lines matching "--- variant: v\\d+" → copy exactly\n'
        '   - Lines that are exactly "---" → copy exactly\n'
        '   - Lines matching "## [A-Z_]+ v\\d+" → copy exactly\n'
        "   - YAML-like lines between --- markers → copy exactly\n"
        "2. Translate ONLY the prose text paragraphs between format markers.\n"
        "3. Do NOT add commentary, headings, or notes.\n"
        "4. Do NOT wrap output in code blocks.\n"
        "5. Preserve blank lines exactly.\n\n"
        "Reply ONLY with the translated text. No preamble. No explanation."
    ),
}

# Stale timeout: atoms in_progress for >5 min are reset to pending
STALE_TIMEOUT_SECONDS = 300

# ── state management ──────────────────────────────────────────────────────

_state_lock = threading.Lock()


def _state_path(locale: str) -> Path:
    return QUEUES_DIR / f"{locale}_state.json"


def _queue_path(locale: str) -> Path:
    return QUEUES_DIR / f"{locale}.jsonl"


def _load_state(locale: str) -> dict[str, dict]:
    """Load {atom_id: {status, worker, claimed_at, attempts, out_path}} from state file."""
    p = _state_path(locale)
    if p.is_file():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _save_state(locale: str, state: dict) -> None:
    p = _state_path(locale)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_queue(locale: str) -> list[dict]:
    """Load all items from the JSONL queue file."""
    p = _queue_path(locale)
    if not p.is_file():
        return []
    items = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                items.append(json.loads(line))
            except Exception:
                pass
    return items


def _get_or_init_state(locale: str) -> tuple[list[dict], dict]:
    """Return (queue_items, state_dict). Initialises state from queue if new."""
    queue = _load_queue(locale)
    state = _load_state(locale)
    # Ensure all queue items are in state
    for item in queue:
        if item["id"] not in state:
            state[item["id"]] = {
                "status": "pending",
                "worker": None,
                "claimed_at": None,
                "attempts": 0,
                "out_path": item["out_path"],
            }
    return queue, state


def _status_counts(state: dict) -> dict[str, int]:
    counts: dict[str, int] = {"pending": 0, "in_progress": 0, "done": 0, "failed": 0}
    for v in state.values():
        s = v.get("status", "pending")
        counts[s] = counts.get(s, 0) + 1
    return counts


def _reset_stale(state: dict) -> int:
    now = time.time()
    reset = 0
    for v in state.values():
        if v.get("status") == "in_progress":
            claimed_at = v.get("claimed_at") or now
            if now - claimed_at > STALE_TIMEOUT_SECONDS:
                v["status"] = "pending"
                v["worker"] = None
                v["claimed_at"] = None
                reset += 1
    return reset


# ── HTTP handler ──────────────────────────────────────────────────────────


class QueueHandler(BaseHTTPRequestHandler):
    locales: list[str] = ["zh-TW", "zh-CN", "ja-JP"]

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"[{time.strftime('%H:%M:%S')}] {fmt % args}", file=sys.stderr)

    def _send_json(self, data: dict, status: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, content: str) -> None:
        body = content.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if parsed.path == "/next":
            locale = params.get("locale", [""])[0]
            tab = params.get("tab", ["?"])[0]
            if locale not in SYSTEM_PROMPTS:
                self._send_json({"error": f"unknown locale: {locale}"}, 400)
                return
            self._handle_next(locale, tab)

        elif parsed.path == "/status":
            result = {}
            for loc in self.locales:
                with _state_lock:
                    _, state = _get_or_init_state(loc)
                result[loc] = _status_counts(state)
            self._send_json(result)

        elif parsed.path == "/dashboard":
            self._send_html(self._build_dashboard())

        else:
            self.send_response(404)
            self.end_headers()

    def _handle_next(self, locale: str, tab: str) -> None:
        with _state_lock:
            queue, state = _get_or_init_state(locale)
            # Reset stale items first
            _reset_stale(state)
            # Find next pending item
            next_item = None
            for item in queue:
                s = state.get(item["id"], {})
                if s.get("status") == "pending":
                    next_item = item
                    break
            if next_item is None:
                _save_state(locale, state)
                self._send_json({"done": True})
                return
            atom_id = next_item["id"]
            state[atom_id]["status"] = "in_progress"
            state[atom_id]["worker"] = tab
            state[atom_id]["claimed_at"] = time.time()
            state[atom_id]["attempts"] = state[atom_id].get("attempts", 0) + 1
            _save_state(locale, state)

        self._send_json({
            "id": atom_id,
            "src_path": next_item["src_path"],
            "out_path": next_item["out_path"],
            "content": next_item["content"],
            "locale": locale,
            "system_prompt": SYSTEM_PROMPTS[locale],
            "chat_url": CHAT_SERVICES[locale],
        })

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/submit":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self._send_json({"error": "invalid JSON"}, 400)
            return

        atom_id = data.get("id", "")
        locale = data.get("locale", "")
        translation = data.get("translation", "")
        passed = data.get("passed", False)

        if not atom_id or not locale or not translation:
            self._send_json({"error": "id, locale, and translation required"}, 400)
            return

        if locale not in SYSTEM_PROMPTS:
            self._send_json({"error": f"unknown locale: {locale}"}, 400)
            return

        with _state_lock:
            queue, state = _get_or_init_state(locale)
            entry = state.get(atom_id)
            if entry is None:
                self._send_json({"error": "atom_id not found"}, 404)
                return

            if passed:
                # Write to disk
                out_path = REPO_ROOT / entry["out_path"]
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(translation, encoding="utf-8")
                entry["status"] = "done"
                entry["worker"] = None
                _save_state(locale, state)
                self._send_json({"ok": True})
            else:
                attempts = entry.get("attempts", 1)
                if attempts >= 3:
                    # Log to failures file
                    entry["status"] = "failed"
                    _save_state(locale, state)
                    FAILURES_DIR.mkdir(parents=True, exist_ok=True)
                    fail_file = FAILURES_DIR / f"{locale}.jsonl"
                    with open(fail_file, "a", encoding="utf-8") as f:
                        # Find source content from queue
                        src_content = next(
                            (i["content"] for i in queue if i["id"] == atom_id), ""
                        )
                        f.write(json.dumps({
                            "id": atom_id,
                            "locale": locale,
                            "attempts": attempts,
                            "last_translation": translation,
                            "source": src_content,
                        }, ensure_ascii=False) + "\n")
                    self._send_json({"ok": False, "retry": False, "reason": "max_attempts_reached"})
                else:
                    entry["status"] = "pending"
                    entry["worker"] = None
                    entry["claimed_at"] = None
                    _save_state(locale, state)
                    self._send_json({"ok": False, "retry": True})

    def _build_dashboard(self) -> str:
        rows = ""
        for locale in self.locales:
            with _state_lock:
                _, state = _get_or_init_state(locale)
            counts = _status_counts(state)
            total = sum(counts.values())
            done = counts.get("done", 0)
            pct = int(done / total * 100) if total else 0
            bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
            active = counts.get("in_progress", 0)
            failed = counts.get("failed", 0)
            service = CHAT_SERVICES.get(locale, "")
            rows += f"""
            <tr>
                <td><b>{html.escape(locale)}</b></td>
                <td><a href="{html.escape(service)}">{html.escape(service)}</a></td>
                <td><code>[{bar}]</code></td>
                <td>{done:,} / {total:,} ({pct}%)</td>
                <td>{active}</td>
                <td class="{'red' if failed else ''}">{failed}</td>
            </tr>"""

        return f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<meta http-equiv="refresh" content="10">
<title>Translation Dashboard</title>
<style>
body {{ font-family: monospace; background: #1a1a2e; color: #eee; padding: 2em; }}
h1 {{ color: #e94560; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ padding: 8px 14px; text-align: left; border-bottom: 1px solid #333; }}
th {{ background: #16213e; color: #e94560; }}
a {{ color: #4fc3f7; }}
.red {{ color: #e94560; font-weight: bold; }}
</style>
</head><body>
<h1>Browser Translation Dashboard</h1>
<p>Auto-refreshes every 10 seconds.
   zh-TW/zh-CN → <a href="https://chat.qwen.ai">Qwen Chat</a> &nbsp;|&nbsp;
   ja-JP → <a href="https://ai.rakuten.co.jp">Rakuten AI Chat</a>
</p>
<table>
<tr><th>Locale</th><th>Chat Service</th><th>Progress</th><th>Done / Total</th><th>Active</th><th>Failed</th></tr>
{rows}
</table>
<p style="color:#888;font-size:0.85em">Status endpoint: <a href="/status">/status</a></p>
</body></html>"""


# ── stale recovery background thread ─────────────────────────────────────


def _stale_thread(locales: list[str]) -> None:
    while True:
        time.sleep(60)
        for locale in locales:
            with _state_lock:
                _, state = _get_or_init_state(locale)
                n = _reset_stale(state)
                if n:
                    _save_state(locale, state)
                    print(f"[{time.strftime('%H:%M:%S')}] Stale recovery: reset {n} {locale} items", file=sys.stderr)


# ── main ──────────────────────────────────────────────────────────────────


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Browser translation queue server.")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--locales", nargs="+", default=["zh-TW", "zh-CN", "ja-JP"])
    args = parser.parse_args()

    QueueHandler.locales = args.locales

    # Check queue files exist
    missing = [loc for loc in args.locales if not _queue_path(loc).is_file()]
    if missing:
        print(f"[WARN] Queue files not found for: {missing}", file=sys.stderr)
        print("Run browser_translation_prep.py first.", file=sys.stderr)

    threading.Thread(target=_stale_thread, args=(args.locales,), daemon=True).start()

    server = HTTPServer(("localhost", args.port), QueueHandler)
    print(f"Queue server: http://localhost:{args.port}")
    print(f"Dashboard:    http://localhost:{args.port}/dashboard")
    print(f"zh-TW/zh-CN tabs → https://chat.qwen.ai")
    print(f"ja-JP tabs       → https://ai.rakuten.co.jp")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
