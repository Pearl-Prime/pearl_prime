#!/usr/bin/env python3
"""Emit config/video/upload_config.yaml as JSON for PhoenixControl."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = REPO_ROOT / "config" / "video" / "upload_config.yaml"


def main() -> int:
    if not CONFIG_PATH.is_file():
        print(json.dumps({"error": "missing_config", "path": str(CONFIG_PATH)}))
        return 1
    try:
        import yaml  # type: ignore
    except ImportError:
        print(json.dumps({"error": "pyyaml_required"}))
        return 1
    data = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    print(json.dumps(data, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
