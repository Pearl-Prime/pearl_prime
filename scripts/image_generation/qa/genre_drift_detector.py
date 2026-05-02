#!/usr/bin/env python3
"""genre_drift_detector.py — per-image genre register drift detector.

PR-C QA harness deliverable. Companion to manga_register_check.py.

Where manga_register_check.py focuses on FORBIDDEN tokens (anti-pattern),
this script focuses on EXPECTED tokens (pro-pattern). For each rendered
image, the script verifies the prompt contains at least N tokens from the
genre's `H_token_mapping.animagine_xl_4_0.positive` set in
drawing_tradition_per_genre.yaml.

Output: artifacts/qa/dashboard_22_corrective_drift_<date>.md

Usage:
    python3 scripts/image_generation/qa/genre_drift_detector.py \\
        --manifest artifacts/qa/dashboard_22_corrective_smoke_2026-05-03.json \\
        --output  artifacts/qa/dashboard_22_corrective_drift_2026-05-03.md
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parents[3]


def load_expected_tokens() -> dict[str, list[str]]:
    """Read H_token_mapping.animagine_xl_4_0.positive per genre."""
    path = REPO_ROOT / "config" / "manga" / "drawing_tradition_per_genre.yaml"
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text())
    out: dict[str, list[str]] = {}
    for genre_name, gd in data.get("genres", {}).items():
        h = gd.get("H_token_mapping", {})
        ani = h.get("animagine_xl_4_0", {}) if isinstance(h, dict) else {}
        pos = ani.get("positive", "") if isinstance(ani, dict) else ""
        if isinstance(pos, str):
            tokens = [t.strip().lower() for t in pos.split(",") if t.strip()]
            out[genre_name] = tokens
    return out


def check(entry: dict, expected: dict) -> dict:
    series_id = entry.get("series_id", "?")
    genre = entry.get("genre_family", "?")
    prompt = entry.get("prompt_positive", "").lower()

    expected_tokens = expected.get(genre, [])
    if not expected_tokens:
        return {
            "series_id": series_id,
            "genre": genre,
            "expected_count": 0,
            "matched_count": 0,
            "match_ratio": 0.0,
            "verdict": "no_expected_tokens_defined",
        }

    matched = [t for t in expected_tokens if t in prompt]
    ratio = len(matched) / len(expected_tokens)

    if ratio >= 0.6:
        verdict = "pass"
    elif ratio >= 0.3:
        verdict = "borderline"
    else:
        verdict = "fail"

    return {
        "series_id": series_id,
        "genre": genre,
        "expected_count": len(expected_tokens),
        "matched_count": len(matched),
        "match_ratio": round(ratio, 3),
        "verdict": verdict,
        "missing_tokens": [t for t in expected_tokens if t not in prompt][:5],
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()

    manifest = json.loads(Path(args.manifest).read_text())
    expected = load_expected_tokens()

    reports = [check(e, expected) for e in manifest.get("entries", [])]
    pass_n = sum(1 for r in reports if r["verdict"] == "pass")
    border = sum(1 for r in reports if r["verdict"] == "borderline")
    fail = sum(1 for r in reports if r["verdict"] == "fail")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Genre Drift Detector Report — {date.today().isoformat()}",
        "",
        f"**Pass / Borderline / Fail:** {pass_n} / {border} / {fail}",
        "",
        "## Per-image",
        "",
        "| Series | Genre | Match | Verdict | Missing tokens (first 5) |",
        "|---|---|---:|---|---|",
    ]
    for r in reports:
        miss = ", ".join(r.get("missing_tokens", [])) or "—"
        lines.append(
            f"| {r['series_id']} | {r['genre']} | "
            f"{r['matched_count']}/{r['expected_count']} ({r['match_ratio']:.2f}) | "
            f"{r['verdict']} | {miss} |"
        )
    out.write_text("\n".join(lines))
    print(f"Wrote {out}; pass={pass_n}, borderline={border}, fail={fail}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
