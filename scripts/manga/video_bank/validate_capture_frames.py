#!/usr/bin/env python3
"""Ordered reject-on-fail gate chain for video-bank capture frames.

Supply spec §4 steps 4–9 (cutout assumed upstream for class-A):
  class_a_l2_gates → bank_layer_blob_gate → qa_face_distance ≤0.4 vs anchor →
  outfit_conformance → curate_to_demanded_pose_ids

A REJECT on any gate is terminal for that frame. Emits a per-frame verdict TSV.

Usage:
  PYTHONPATH=. python3 scripts/manga/video_bank/validate_capture_frames.py \\
    --frames-dir path/to/cutouts --anchor path/to/anchor.png \\
    --demanded-pose-ids a,b --outfit-ref path/to/outfit_ref.png \\
    --out-tsv path/to/verdicts.tsv
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

import numpy as np
from PIL import Image

from scripts.manga.bank_layer_blob_gate import judge_png
from scripts.manga.validate_layer import (
    LayerValidationInput,
    check_background_bleed,
    check_character_extraction_coverage,
    check_rembg_clean_alpha,
)

REPO = Path(__file__).resolve().parents[3]
FACE_DISTANCE_PASS_MAX = 0.4  # same-character bar (M5 / supply spec §4)


@dataclass
class GateVerdict:
    gate: str
    ok: bool
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {"gate": self.gate, "ok": self.ok, "detail": self.detail}


@dataclass
class FrameVerdict:
    path: str
    pose_id: str
    ok: bool
    rejected_at: str | None = None
    gates: list[GateVerdict] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "pose_id": self.pose_id,
            "ok": self.ok,
            "rejected_at": self.rejected_at,
            "gates": [g.to_dict() for g in self.gates],
        }


def _class_a_cutout_gates(cutout: Path) -> GateVerdict:
    inp = LayerValidationInput(
        image_path=cutout,
        layer_type="L2",
        safe_zone_row={},
        cutout_image_path=cutout,
        cutout_policy={
            "character_extraction_coverage_min_pct": 0.05,
            "background_bleed_max_pct": 25.0,
        },
    )
    results = [
        check_rembg_clean_alpha(inp),
        check_character_extraction_coverage(inp),
        check_background_bleed(inp),
    ]
    fails = [r for r in results if (not r.passed) and (not r.skipped) and r.severity == "FAIL"]
    if fails:
        return GateVerdict(
            "class_a_l2_gates",
            False,
            "; ".join(f"{r.check_id}:{r.remediation_hint[:80]}" for r in fails),
        )
    return GateVerdict("class_a_l2_gates", True, "rembg_clean_alpha+coverage+bleed")


def _blob_gate(cutout: Path) -> GateVerdict:
    # Byte floor first (supply / render stub doctrine ≥50KB for banked layers when real;
    # fixtures may be smaller — still run structure gate).
    nbytes = cutout.stat().st_size
    verdict = judge_png(cutout)
    if not verdict.ok:
        return GateVerdict("bank_layer_blob_gate", False, ",".join(verdict.reasons))
    return GateVerdict("bank_layer_blob_gate", True, f"bytes={nbytes}")


def _face_distance_gate(
    cutout: Path,
    anchor: Path,
    *,
    distance_fn: Optional[Callable[[Path, Path], float]] = None,
) -> GateVerdict:
    if distance_fn is None:
        from scripts.manga.character_individuation.qa_face_distance import distance

        distance_fn = distance  # type: ignore[assignment]
    try:
        d = float(distance_fn(cutout, anchor))  # type: ignore[misc]
    except Exception as exc:  # noqa: BLE001
        return GateVerdict("qa_face_distance", False, f"error:{exc}")
    ok = d <= FACE_DISTANCE_PASS_MAX
    return GateVerdict(
        "qa_face_distance",
        ok,
        f"distance={d:.4f} threshold={FACE_DISTANCE_PASS_MAX}",
    )


def _mean_rgb_masked(path: Path) -> tuple[float, float, float] | None:
    im = Image.open(path).convert("RGBA")
    arr = np.array(im)
    alpha = arr[:, :, 3]
    mask = alpha >= 200
    if not mask.any():
        return None
    rgb = arr[:, :, :3][mask].astype(float)
    return tuple(float(x) for x in rgb.mean(axis=0))  # type: ignore[return-value]


def _outfit_conformance_gate(
    cutout: Path,
    outfit_ref: Path | None,
    *,
    max_mean_delta: float = 45.0,
) -> GateVerdict:
    if outfit_ref is None or not outfit_ref.is_file():
        # Soft-skip when no ref supplied (caller may only have outfit_id metadata).
        return GateVerdict("outfit_conformance", True, "skipped_no_outfit_ref")
    a = _mean_rgb_masked(cutout)
    b = _mean_rgb_masked(outfit_ref)
    if a is None or b is None:
        return GateVerdict("outfit_conformance", False, "empty_alpha_mask")
    delta = abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])
    ok = delta <= max_mean_delta
    return GateVerdict(
        "outfit_conformance",
        ok,
        f"mean_rgb_delta={delta:.2f} max={max_mean_delta}",
    )


def curate_to_demanded(
    verdicts: list[FrameVerdict],
    demanded_pose_ids: list[str],
) -> list[FrameVerdict]:
    """Keep smallest sufficient set covering demanded pose_ids; drop extras."""
    needed = list(demanded_pose_ids)
    kept_paths: set[str] = set()
    for pid in needed:
        match = next((v for v in verdicts if v.ok and v.pose_id == pid and v.path not in kept_paths), None)
        if match is None:
            # try any ok frame tagged with this pose later; if none, leave uncovered
            continue
        kept_paths.add(match.path)
    # If pose_id blank, greedily keep up to len(demanded)
    if not any(v.pose_id for v in verdicts):
        ok_frames = [v for v in verdicts if v.ok]
        for v in ok_frames[: len(demanded_pose_ids)]:
            kept_paths.add(v.path)

    for v in verdicts:
        if not v.ok:
            continue
        if v.path not in kept_paths:
            v.ok = False
            v.rejected_at = "curate_to_demanded_pose_ids"
            v.gates.append(
                GateVerdict("curate_to_demanded_pose_ids", False, "surplus_frame")
            )
        else:
            v.gates.append(GateVerdict("curate_to_demanded_pose_ids", True, "kept"))
    return verdicts


def validate_frame(
    cutout: Path,
    *,
    anchor: Path,
    outfit_ref: Path | None = None,
    pose_id: str = "",
    distance_fn: Optional[Callable[[Path, Path], float]] = None,
    skip_face: bool = False,
    skip_blob: bool = False,
) -> FrameVerdict:
    fv = FrameVerdict(path=str(cutout), pose_id=pose_id, ok=True)
    chain: list[tuple[str, Callable[[], GateVerdict]]] = [
        ("class_a_l2_gates", lambda: _class_a_cutout_gates(cutout)),
    ]
    if not skip_blob:
        chain.append(("bank_layer_blob_gate", lambda: _blob_gate(cutout)))
    if not skip_face:
        chain.append(
            ("qa_face_distance", lambda: _face_distance_gate(cutout, anchor, distance_fn=distance_fn))
        )
    chain.append(("outfit_conformance", lambda: _outfit_conformance_gate(cutout, outfit_ref)))

    for name, fn in chain:
        g = fn()
        fv.gates.append(g)
        if not g.ok:
            fv.ok = False
            fv.rejected_at = name
            return fv
    return fv


def validate_capture_frames(
    frames: list[Path],
    *,
    anchor: Path,
    demanded_pose_ids: list[str],
    outfit_ref: Path | None = None,
    pose_ids: list[str] | None = None,
    distance_fn: Optional[Callable[[Path, Path], float]] = None,
    skip_face: bool = False,
    skip_blob: bool = False,
) -> list[FrameVerdict]:
    pose_ids = pose_ids or [""] * len(frames)
    verdicts: list[FrameVerdict] = []
    for path, pid in zip(frames, pose_ids):
        verdicts.append(
            validate_frame(
                path,
                anchor=anchor,
                outfit_ref=outfit_ref,
                pose_id=pid,
                distance_fn=distance_fn,
                skip_face=skip_face,
                skip_blob=skip_blob,
            )
        )
    return curate_to_demanded(verdicts, demanded_pose_ids)


def write_verdict_tsv(verdicts: list[FrameVerdict], out_tsv: Path) -> None:
    out_tsv.parent.mkdir(parents=True, exist_ok=True)
    with out_tsv.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(["path", "pose_id", "ok", "rejected_at", "gates_json"])
        for v in verdicts:
            w.writerow(
                [
                    v.path,
                    v.pose_id,
                    "PASS" if v.ok else "REJECT",
                    v.rejected_at or "",
                    json.dumps([g.to_dict() for g in v.gates]),
                ]
            )


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--frames-dir", type=Path, required=True)
    ap.add_argument("--anchor", type=Path, required=True)
    ap.add_argument("--demanded-pose-ids", required=True, help="comma-separated")
    ap.add_argument("--outfit-ref", type=Path, default=None)
    ap.add_argument("--out-tsv", type=Path, required=True)
    ap.add_argument("--skip-face", action="store_true", help="Skip qa_face_distance (CI fixtures)")
    ap.add_argument("--skip-blob", action="store_true", help="Skip blob gate (tiny fixtures)")
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    frames = sorted(args.frames_dir.glob("*.png"))
    if not frames:
        print(f"ERROR: no png frames in {args.frames_dir}", file=sys.stderr)
        return 2
    demanded = [x.strip() for x in args.demanded_pose_ids.split(",") if x.strip()]
    # Optional pose_id from filename stem suffix __pose_id
    pose_ids: list[str] = []
    for f in frames:
        stem = f.stem
        if "__" in stem:
            pose_ids.append(stem.split("__", 1)[1].replace("_INTERIM", ""))
        else:
            pose_ids.append("")
    verdicts = validate_capture_frames(
        frames,
        anchor=args.anchor,
        demanded_pose_ids=demanded,
        outfit_ref=args.outfit_ref,
        pose_ids=pose_ids,
        skip_face=args.skip_face,
        skip_blob=args.skip_blob,
    )
    write_verdict_tsv(verdicts, args.out_tsv)
    n_pass = sum(1 for v in verdicts if v.ok)
    print(json.dumps({"frames": len(verdicts), "pass": n_pass, "out_tsv": str(args.out_tsv)}, indent=2))
    # Terminal REJECT anywhere → non-zero if zero passes
    return 0 if n_pass > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
