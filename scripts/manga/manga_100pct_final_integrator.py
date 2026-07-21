#!/usr/bin/env python3
"""Fail-closed final integrator for manga A-M closeouts."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import yaml

_TAG_RE = re.compile(r"(?m)^\s*[-*]?\s*([a-z0-9][a-z0-9_-]*)=([^\n`]+?)\s*$")


def _tags(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    return {key: value.strip() for key, value in _TAG_RE.findall(path.read_text(encoding="utf-8"))}


def integrate(repo_root: Path, config_path: Path) -> dict[str, Any]:
    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    failures: list[str] = []
    lanes: dict[str, Any] = {}
    for lane, row in (config.get("lanes") or {}).items():
        path = repo_root / str(row.get("closeout"))
        tags = _tags(path)
        lanes[lane] = {"path": str(path), "present": path.is_file(), "tags": tags}
        if not path.is_file():
            failures.append(f"lane {lane}: closeout missing")
            continue
        values = {value.lower() for value in tags.values()}
        if any(value in {"blocked", "partial", "not-green", "not_green", "missing"} for value in values):
            failures.append(f"lane {lane}: closeout contains non-green status")
        if tags.get("overall-manga-green") not in (None, "NOT_PROVEN"):
            failures.append(f"lane {lane}: invalid premature overall green tag")

    i_tags = lanes.get("I", {}).get("tags", {})
    if i_tags.get("blind-read-bar") != "green":
        failures.append("blind-read bar is not green")
    if i_tags.get("operator-approval") != "present":
        failures.append("operator approval missing")
    if i_tags.get("judge-scorecards") != "present":
        failures.append("judge scorecards missing")

    m_tags = lanes.get("M", {}).get("tags", {})
    if m_tags.get("manga-release-readiness") != "green":
        failures.append("release readiness is not green")
    if m_tags.get("manga-queue-repeatability") != "green":
        failures.append("queue repeatability is not green")

    final = "GREEN" if not failures else "NOT_GREEN"
    return {
        "manga-100pct-final": final,
        "lanes": lanes,
        "failures": failures,
        "final_sentence": (
            "FINAL VERDICT: Phoenix Omega manga is GREEN for the explicitly stated production scope."
            if final == "GREEN"
            else "FINAL VERDICT: Phoenix Omega manga is NOT GREEN for the explicitly stated production scope."
        ),
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# Manga 100% Final Verdict — 2026-07-14",
        "",
        f"- manga-100pct-final={report['manga-100pct-final']}",
        "",
        "## Lane evidence",
        "",
    ]
    for lane, row in report["lanes"].items():
        lines.append(
            f"- {lane}: closeout={'present' if row['present'] else 'missing'}; "
            f"tags={json.dumps(row['tags'], sort_keys=True)}"
        )
    lines.extend([
        "",
        "## Failures",
        "",
        *([f"- {failure}" for failure in report["failures"]] or ["- None"]),
        "",
        report["final_sentence"],
        "",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/manga/manga_100pct_lanes.yaml"),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("artifacts/analysis/MANGA_100PCT_FINAL_VERDICT_2026-07-14.md"),
    )
    args = parser.parse_args()
    config_path = args.config if args.config.is_absolute() else args.repo_root / args.config
    out_path = args.out if args.out.is_absolute() else args.repo_root / args.out
    report = integrate(args.repo_root, config_path)
    write_markdown(out_path, report)
    print(json.dumps(report, indent=2))
    return 0 if report["manga-100pct-final"] == "GREEN" else 2


if __name__ == "__main__":
    raise SystemExit(main())
