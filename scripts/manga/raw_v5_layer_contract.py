#!/usr/bin/env python3
"""Compile and assess the fail-closed raw Pearl Star V5 layer contract."""
from __future__ import annotations

import argparse
import json
import sys
from collections import deque
from pathlib import Path
from typing import Any

import numpy as np
import yaml
from PIL import Image

REPO = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = REPO / "config" / "manga" / "raw_v5_layer_contract.yaml"


class RawLayerContractError(RuntimeError):
    pass


def load_contract(path: Path = DEFAULT_CONFIG) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(value, dict):
        raise RawLayerContractError("raw layer contract must be a mapping")
    return value


def compile_prompt(
    base_positive: str,
    base_negative: str = "",
    *,
    config: dict[str, Any] | None = None,
) -> tuple[str, str]:
    cfg = config or load_contract()
    pos = [base_positive.strip(), *((cfg.get("prompt_contract") or {}).get("positive") or [])]
    neg = [base_negative.strip(), *((cfg.get("prompt_contract") or {}).get("negative") or [])]
    return ", ".join(str(v).strip() for v in pos if str(v).strip()), ", ".join(
        str(v).strip() for v in neg if str(v).strip()
    )


def _components(mask: np.ndarray) -> list[int]:
    h, w = mask.shape
    seen = np.zeros(mask.shape, dtype=bool)
    sizes: list[int] = []
    for y in range(h):
        for x in np.where(mask[y] & ~seen[y])[0]:
            if seen[y, x]:
                continue
            q: deque[tuple[int, int]] = deque([(int(x), y)])
            seen[y, x] = True
            size = 0
            while q:
                cx, cy = q.popleft()
                size += 1
                for nx, ny in (
                    (cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1),
                ):
                    if 0 <= nx < w and 0 <= ny < h and mask[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        q.append((nx, ny))
            sizes.append(size)
    return sorted(sizes, reverse=True)


def assess_candidate(path: Path) -> dict[str, Any]:
    with Image.open(path) as image:
        rgba = image.convert("RGBA")
    alpha = np.asarray(rgba.getchannel("A"))
    mask = alpha > 16
    opaque = int(mask.sum())
    sizes = _components(mask)
    largest = sizes[0] if sizes else 0
    ratio = largest / max(opaque, 1)
    coverage = opaque / max(mask.size, 1)
    significant = [size for size in sizes if size >= max(64, int(opaque * 0.01))]
    reasons: list[str] = []
    if opaque == 0:
        reasons.append("no_alpha")
    if ratio < 0.75:
        reasons.append("main_component_ratio_low")
    if len(significant) > 1:
        reasons.append("multiple_significant_components")
    if coverage > 0.65:
        reasons.append("coverage_too_high")
    return {
        "path": str(path),
        "opaque_px": opaque,
        "coverage": round(coverage, 6),
        "component_count": len(sizes),
        "significant_component_count": len(significant),
        "main_component_ratio": round(ratio, 4),
        "contamination_suspected": bool(reasons),
        "reasons": reasons,
        "confidence": round(max(0.0, min(1.0, ratio - max(0, len(significant) - 1) * 0.2)), 4),
    }


def assess_panel(panel_root: Path) -> dict[str, Any]:
    reports = [
        assess_candidate(panel_root / name)
        for name in ("layer_02.png", "layer_03.png")
        if (panel_root / name).is_file()
    ]
    if not reports:
        raise RawLayerContractError("no layer_02.png or layer_03.png")
    clean = [row for row in reports if not row["contamination_suspected"]]
    selected = sorted(clean, key=lambda row: (-row["confidence"], row["path"]))[0] if clean else None
    raw_green = bool(reports) and not reports[0]["contamination_suspected"]
    return {
        "raw-v5-layer-roles": "green" if raw_green else "not-green",
        "raw_layer_role_confidence": {
            Path(row["path"]).name: row["confidence"] for row in reports
        },
        "contamination_suspected": any(row["contamination_suspected"] for row in reports),
        "candidate_layer_for_subject": Path(selected["path"]).name if selected else None,
        "selected-component-fallback": "preserved",
        "candidate_reports": reports,
    }


def update_telemetry(panel_root: Path, report: dict[str, Any]) -> Path:
    path = panel_root / "_telemetry.json"
    data = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    data.update({
        "raw_layer_role_confidence": report["raw_layer_role_confidence"],
        "contamination_suspected": report["contamination_suspected"],
        "candidate_layer_for_subject": report["candidate_layer_for_subject"],
        "raw-v5-layer-roles": report["raw-v5-layer-roles"],
        "selected-component-fallback": "preserved",
    })
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel-root", type=Path)
    parser.add_argument("--base-positive", default="")
    parser.add_argument("--base-negative", default="")
    parser.add_argument("--write-telemetry", action="store_true")
    args = parser.parse_args(argv)
    if args.panel_root:
        report = assess_panel(args.panel_root)
        if args.write_telemetry:
            update_telemetry(args.panel_root, report)
        print(json.dumps(report, indent=2))
        return 0 if report["raw-v5-layer-roles"] == "green" else 2
    positive, negative = compile_prompt(args.base_positive, args.base_negative)
    print(json.dumps({"positive": positive, "negative": negative}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
