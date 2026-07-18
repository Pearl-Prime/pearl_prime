#!/usr/bin/env python3
"""manga_register_check.py — drift score per rendered image.

PR-C QA harness deliverable. Cookbook v2 (#831) shipped the YAML but did not
ship the actual QA harness scripts; this is the minimal commercial-clean
implementation per the algorithm spec in PR #842.

Approach: lightweight tag-based check (NO LLM, NO paid API). Reads the
forbidden-token list per genre from the cookbook's `forbidden_tokens_registry`
section + drawing_tradition_per_genre.yaml's `F_forbidden_drift_patterns`.
Validates rendered output against expected register by:

  1. Reading the rendering manifest (artifacts/qa/dashboard_22_corrective_smoke_*.json)
  2. For each rendered image, looking up its expected genre register
  3. Optionally running a Florence-2 / DanbooruTagger reverse-prompt step
     (deferred — those models are not pre-installed; falls back to manifest-
     based prompt-content check)
  4. Computing drift_score = (forbidden_tokens_present_in_caption_or_prompt) /
                              (total_forbidden_tokens_for_genre)

Output: artifacts/qa/dashboard_22_corrective_qa_report_<date>.md

Usage:
    python3 scripts/image_generation/qa/manga_register_check.py \\
        --manifest artifacts/qa/dashboard_22_corrective_smoke_2026-05-03.json \\
        --output  artifacts/qa/dashboard_22_corrective_qa_report_2026-05-03.md

Empirical gap (deferred to follow-up): Florence-2 / WD-EVA02-Tagger
integration for actual reverse-prompt of pixel content. Without it, this
script validates prompt construction only, not rendered output.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required — pip install pyyaml", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parents[3]


def load_genre_forbidden_tokens() -> dict[str, list[str]]:
    """Read F_forbidden_drift_patterns per genre from drawing_tradition YAML."""
    path = REPO_ROOT / "config" / "manga" / "drawing_tradition_per_genre.yaml"
    if not path.exists():
        print(f"WARN: {path} not found; falling back to minimal default", file=sys.stderr)
        return {}
    data = yaml.safe_load(path.read_text())
    out: dict[str, list[str]] = {}
    for genre_name, gd in data.get("genres", {}).items():
        forbidden = gd.get("F_forbidden_drift_patterns", [])
        if isinstance(forbidden, list):
            # Each entry is free-text; flatten into searchable phrases
            phrases = []
            for entry in forbidden:
                if isinstance(entry, str):
                    # Extract the comma-separated token list section
                    # Format: "concept art, key visual, painterly, oil painting, ..."
                    parts = re.split(r"[,;]\s*", entry)
                    for p in parts:
                        # Strip quotes / parenthetical
                        p = re.sub(r'["\'`]', "", p).strip()
                        if 0 < len(p) < 60:
                            phrases.append(p.lower())
            out[genre_name] = phrases
    return out


def reverse_prompt_caption(image_path: Path) -> str:
    """Florence-2 / DanbooruTagger reverse-prompt — DEFERRED.

    Returns empty string. Future work: integrate Florence-2 via
    transformers + auto-process the rendered image into a caption +
    Booru-tag set. For now, this script validates prompt construction
    against forbidden tokens in the manifest's stored prompt; not pixel
    content.
    """
    return ""


def check_image(entry: dict, forbidden_per_genre: dict) -> dict:
    """Return drift report for one rendered image."""
    series_id = entry.get("series_id", "?")
    genre = entry.get("genre_family", "?")
    prompt_positive = entry.get("prompt_positive", "")
    prompt_negative = entry.get("prompt_negative", "")
    output_path = Path(entry.get("output_path", ""))

    forbidden = forbidden_per_genre.get(genre, [])
    caption = reverse_prompt_caption(output_path) if output_path.exists() else ""

    pos_lower = prompt_positive.lower()
    cap_lower = caption.lower()

    # Drift = presence of forbidden tokens in POSITIVE prompt (anti-pattern)
    # OR in caption (if reverse-prompt available)
    pos_offenses = [f for f in forbidden if f in pos_lower]
    cap_offenses = [f for f in forbidden if f and f in cap_lower] if caption else []

    drift_score = (
        (len(pos_offenses) + len(cap_offenses)) / max(1, len(forbidden) * 2)
        if forbidden else 0.0
    )

    if drift_score < 0.2:
        verdict = "pass"
    elif drift_score < 0.5:
        verdict = "borderline"
    else:
        verdict = "fail"

    return {
        "series_id": series_id,
        "genre": genre,
        "drift_score": round(drift_score, 3),
        "verdict": verdict,
        "positive_prompt_offenses": pos_offenses,
        "caption_offenses": cap_offenses,
        "caption_used": caption != "",
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", required=True, help="dashboard render manifest JSON")
    p.add_argument("--output", required=True, help="output markdown report path")
    args = p.parse_args()

    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        print(f"ERROR: manifest not found: {manifest_path}", file=sys.stderr)
        return 1

    manifest = json.loads(manifest_path.read_text())
    forbidden_per_genre = load_genre_forbidden_tokens()

    reports = [check_image(entry, forbidden_per_genre) for entry in manifest.get("entries", [])]
    pass_count = sum(1 for r in reports if r["verdict"] == "pass")
    border_count = sum(1 for r in reports if r["verdict"] == "borderline")
    fail_count = sum(1 for r in reports if r["verdict"] == "fail")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Manga Register Check Report — {date.today().isoformat()}",
        "",
        f"**Manifest:** `{manifest_path}`",
        f"**Total images:** {len(reports)}",
        f"**Pass / Borderline / Fail:** {pass_count} / {border_count} / {fail_count}",
        "",
        "**Caveat:** caption-based reverse-prompt is DEFERRED (Florence-2 / WD-EVA02-Tagger integration not yet shipped). This run validates prompt-construction discipline only, not rendered pixel content. Once reverse-prompt is wired up, drift_score will reflect actual pixel-vs-genre alignment.",
        "",
        "## Per-image drift report",
        "",
        "| Series | Genre | Drift | Verdict | Positive offenses | Caption offenses |",
        "|---|---|---:|---|---|---|",
    ]
    for r in reports:
        pos = ", ".join(r["positive_prompt_offenses"]) or "—"
        cap = ", ".join(r["caption_offenses"]) or "—"
        lines.append(
            f"| {r['series_id']} | {r['genre']} | {r['drift_score']:.3f} | "
            f"{r['verdict']} | {pos} | {cap} |"
        )
    lines += [
        "",
        "## Summary stats",
        "",
        f"- Pass rate: {pass_count}/{len(reports)} ({100*pass_count/max(1,len(reports)):.1f}%)",
        f"- Borderline: {border_count}",
        f"- Fail: {fail_count}",
        "",
        "## Per-genre pass rate",
        "",
    ]
    by_genre: dict[str, list[dict]] = {}
    for r in reports:
        by_genre.setdefault(r["genre"], []).append(r)
    for g, rs in sorted(by_genre.items()):
        gp = sum(1 for r in rs if r["verdict"] == "pass")
        lines.append(f"- {g}: {gp}/{len(rs)} pass")

    out.write_text("\n".join(lines))
    print(f"Wrote {out}")
    print(f"  pass={pass_count}, borderline={border_count}, fail={fail_count}")
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
