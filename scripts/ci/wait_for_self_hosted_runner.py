#!/usr/bin/env python3
"""Poll GitHub API until a runner with label pearl-star-gpu is online (or timeout)."""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request

REPO = os.environ["GITHUB_REPOSITORY"]
TOKEN = os.environ["GH_TOKEN"]
LABEL = os.environ.get("RUNNER_LABEL", "pearl-star-gpu")
MAX_WAIT_S = int(os.environ.get("MAX_WAIT_S", "1800"))
INTERVAL_S = int(os.environ.get("INTERVAL_S", "30"))


def fetch_runners() -> list[dict]:
    req = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/actions/runners?per_page=100",
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/vnd.github+json",
        },
    )
    with urllib.request.urlopen(req, timeout=45) as r:
        data = json.loads(r.read().decode())
    return list(data.get("runners") or [])


def has_online_label(runners: list[dict], label: str) -> bool:
    for x in runners:
        if x.get("status") != "online":
            continue
        for lab in x.get("labels") or []:
            if lab.get("name") == label:
                return True
    return False


def main() -> int:
    deadline = time.monotonic() + MAX_WAIT_S
    while time.monotonic() < deadline:
        try:
            runners = fetch_runners()
        except urllib.error.HTTPError as e:
            print("API error:", e, file=sys.stderr)
            time.sleep(INTERVAL_S)
            continue
        except OSError as e:
            print("Network error:", e, file=sys.stderr)
            time.sleep(INTERVAL_S)
            continue
        if has_online_label(runners, LABEL):
            print(f"Runner label {LABEL!r} is online")
            return 0
        print(f"No online runner with label {LABEL!r}; sleeping {INTERVAL_S}s...")
        time.sleep(INTERVAL_S)
    print(f"Timeout after {MAX_WAIT_S}s waiting for {LABEL!r}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
