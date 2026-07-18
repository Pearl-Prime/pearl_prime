#!/usr/bin/env python3
"""Exit 0 if a runner with label pearl-star-gpu is online; else exit 1 (no wait)."""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

REPO = os.environ["GITHUB_REPOSITORY"]
TOKEN = os.environ["GH_TOKEN"]
LABEL = os.environ.get("RUNNER_LABEL", "pearl-star-gpu")


def main() -> int:
    req = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/actions/runners?per_page=100",
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/vnd.github+json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            data = json.loads(r.read().decode())
    except (urllib.error.HTTPError, OSError) as e:
        print("API error:", e, file=sys.stderr)
        return 1

    for x in data.get("runners") or []:
        if x.get("status") != "online":
            continue
        for lab in x.get("labels") or []:
            if lab.get("name") == LABEL:
                print(f"OK: runner online ({x.get('name')})")
                return 0
    print(f"No online runner with label {LABEL!r}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
