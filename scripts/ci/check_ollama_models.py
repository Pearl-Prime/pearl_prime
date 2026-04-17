#!/usr/bin/env python3
"""Exit 0 if Ollama /api/tags lists gemma and qwen families; else 1 (operator visibility)."""
from __future__ import annotations

import json
import os
import sys
import urllib.request


def main() -> int:
    host = (os.environ.get("PEARL_STAR_OLLAMA_HOST") or os.environ.get("PEARL_STAR_IP") or "192.168.1.101").strip()
    url = f"http://{host}:11434/api/tags"
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=12) as r:
            data = json.loads(r.read().decode())
    except OSError as e:
        print(f"OLLAMA_UNREACHABLE:{url}:{e}", file=sys.stderr)
        return 1
    names = " ".join((m.get("name") or "") for m in (data.get("models") or [])).lower()
    ok_gemma = "gemma" in names
    ok_qwen = "qwen" in names
    if ok_gemma and ok_qwen:
        print("OK: gemma and qwen families present on", url)
        return 0
    print(f"MISSING_MODELS gemma={ok_gemma} qwen={ok_qwen}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
