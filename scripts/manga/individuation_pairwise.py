#!/usr/bin/env python3
"""individuation_pairwise.py — pairwise face-distance matrix for the 22.

PR-C Step 4 deliverable. Implements the Q2 metric chosen in PR #842
(`config/manga/character_individuation_metric.yaml`):

  PRIMARY: DeepFace + FaceNet-512 cosine distance
  FALLBACK: open_clip ViT-B/32 image-image cosine

Reads:
  --inputs <dir>  : directory of rendered PNGs (e.g.,
                    /Users/ahjan/phoenix_omega/assets/manga_catalog/<brand>/<series>/main_character_v2.png)
  Or --manifest <path> : a JSON manifest like
                    artifacts/qa/dashboard_22_corrective_smoke_*.json

Writes:
  CSV:   artifacts/qa/dashboard_22_individuation_matrix_<date>.csv
  Summary MD: artifacts/qa/dashboard_22_individuation_matrix_summary_<date>.md

Thresholds (per PR #842 character_individuation_metric.yaml):
  pair_distance >= 0.40 → distinct
  0.25 <= distance < 0.40 → borderline
  distance < 0.25 → look-alike risk

These thresholds are PROPOSED — empirical calibration against the actual
22 dashboard PNGs is required to lock them in (see Phase 4 of the
methodology doc).

Usage:
    python3 scripts/manga/individuation_pairwise.py \\
        --manifest artifacts/qa/dashboard_22_corrective_smoke_2026-05-03.json \\
        --csv      artifacts/qa/dashboard_22_individuation_matrix_2026-05-03.csv \\
        --summary  artifacts/qa/dashboard_22_individuation_matrix_summary_2026-05-03.md
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date
from itertools import combinations
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# ── Thresholds (per character_individuation_metric.yaml) ──
DISTINCT_FLOOR = 0.40
LOOKALIKE_CEILING = 0.25


def load_metric():
    """Load DeepFace + FaceNet-512. Falls back to CLIP if DeepFace fails."""
    try:
        from deepface import DeepFace  # noqa: F401
        return "deepface_facenet512"
    except ImportError:
        pass
    try:
        import open_clip  # noqa: F401
        return "open_clip_vitb32"
    except ImportError:
        return None


def compute_distance_deepface(img_a: str, img_b: str) -> float:
    """FaceNet-512 cosine distance via DeepFace.verify."""
    from deepface import DeepFace
    try:
        result = DeepFace.verify(
            img1_path=img_a,
            img2_path=img_b,
            model_name="Facenet512",
            distance_metric="cosine",
            enforce_detection=False,
            silent=True,
        )
        return float(result.get("distance", 1.0))
    except Exception as e:
        print(f"WARN: deepface failed on {img_a} vs {img_b}: {e}", file=sys.stderr)
        return 1.0  # max distance = different


def compute_distance_clip(img_a: str, img_b: str) -> float:
    """CLIP ViT-B/32 image-image cosine distance (1 - similarity)."""
    import open_clip
    import torch
    from PIL import Image

    model, _, preprocess = open_clip.create_model_and_transforms(
        "ViT-B-32", pretrained="openai"
    )
    model.eval()
    with torch.no_grad():
        a = preprocess(Image.open(img_a).convert("RGB")).unsqueeze(0)
        b = preprocess(Image.open(img_b).convert("RGB")).unsqueeze(0)
        ea = model.encode_image(a)
        eb = model.encode_image(b)
        ea = ea / ea.norm(dim=-1, keepdim=True)
        eb = eb / eb.norm(dim=-1, keepdim=True)
        sim = (ea @ eb.T).item()
        return 1.0 - sim


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", required=True)
    p.add_argument("--csv", required=True)
    p.add_argument("--summary", required=True)
    args = p.parse_args()

    metric = load_metric()
    if metric is None:
        print("ERROR: neither deepface nor open_clip is installed.", file=sys.stderr)
        print("Install: pip install --user deepface OR pip install --user open-clip-torch", file=sys.stderr)
        return 1
    print(f"Using metric: {metric}", file=sys.stderr)

    manifest = json.loads(Path(args.manifest).read_text())
    entries = manifest.get("entries", [])
    images = [(e.get("series_id"), e.get("output_path")) for e in entries]

    # Filter to images that actually exist on disk
    images = [(sid, path) for (sid, path) in images if path and Path(path).exists()]
    if len(images) < 2:
        print(f"ERROR: need >=2 images on disk; found {len(images)}", file=sys.stderr)
        print("If you're running this BEFORE the rendering step, that's expected — defer to post-render.", file=sys.stderr)
        return 1

    # Compute pairwise
    rows = []
    for (sid_a, path_a), (sid_b, path_b) in combinations(images, 2):
        if metric == "deepface_facenet512":
            dist = compute_distance_deepface(path_a, path_b)
        else:
            dist = compute_distance_clip(path_a, path_b)
        rows.append((sid_a, sid_b, dist))

    # Write CSV
    csv_path = Path(args.csv)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["series_a", "series_b", "cosine_distance"])
        for sid_a, sid_b, d in rows:
            w.writerow([sid_a, sid_b, f"{d:.4f}"])
    print(f"Wrote CSV: {csv_path}")

    # Summary
    n_total = len(rows)
    distinct = sum(1 for _, _, d in rows if d >= DISTINCT_FLOOR)
    borderline = sum(1 for _, _, d in rows if LOOKALIKE_CEILING <= d < DISTINCT_FLOOR)
    look_alike = sum(1 for _, _, d in rows if d < LOOKALIKE_CEILING)

    # Worst pairs (lowest distance = most similar)
    rows_sorted = sorted(rows, key=lambda r: r[2])

    summary_path = Path(args.summary)
    lines = [
        f"# Individuation Matrix Summary — {date.today().isoformat()}",
        "",
        f"**Metric:** {metric}",
        f"**Total pairs:** {n_total}",
        f"**Distinct (≥{DISTINCT_FLOOR}):** {distinct} ({100*distinct/max(1,n_total):.1f}%)",
        f"**Borderline ([{LOOKALIKE_CEILING}, {DISTINCT_FLOOR})):** {borderline} ({100*borderline/max(1,n_total):.1f}%)",
        f"**Look-alike risk (<{LOOKALIKE_CEILING}):** {look_alike} ({100*look_alike/max(1,n_total):.1f}%)",
        "",
        f"**Acceptance criterion (per brief):** ≥208 of 231 pairs above {DISTINCT_FLOOR}.",
        f"**Status:** {'PASS' if distinct >= 208 else 'FAIL'} ({distinct}/231 above threshold)",
        "",
        "## Worst 5 pairs (lowest distance = highest look-alike risk)",
        "",
        "| Series A | Series B | Distance |",
        "|---|---|---:|",
    ]
    for sid_a, sid_b, d in rows_sorted[:5]:
        lines.append(f"| {sid_a} | {sid_b} | {d:.4f} |")
    lines += [
        "",
        "## Caveat",
        "",
        "Thresholds are PROPOSED per PR #842 `config/manga/character_individuation_metric.yaml`. Empirical calibration against the original 22 dashboard PNGs is required to confirm the thresholds reflect operator-eyeballed look-alike judgment. See `docs/CORRECTIVE_ACTION_METHODOLOGY_2026-05-03.md` Phase 4 for the calibration procedure.",
    ]
    summary_path.write_text("\n".join(lines))
    print(f"Wrote summary: {summary_path}")
    print(f"  distinct={distinct}, borderline={borderline}, look_alike={look_alike}")
    return 0 if distinct >= 208 else 2


if __name__ == "__main__":
    sys.exit(main())
