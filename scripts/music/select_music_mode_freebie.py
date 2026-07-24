#!/usr/bin/env python3
"""Select music-mode freebie from brand_wizard + survey YAML (gt30d D08 / C05).

Hard-errors if inputs missing. No hardcoded freebie catalog.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


def _load(path: Path) -> dict:
    if yaml is None:
        raise RuntimeError("PyYAML required")
    if not path.exists():
        raise FileNotFoundError(f"required YAML missing: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML must be a mapping: {path}")
    return data


def select_freebie(brand_wizard: dict, survey: dict) -> dict:
    """Deterministic selection from inputs — never a module-level hardcoded list."""
    brand_id = (
        brand_wizard.get("brand_id")
        or brand_wizard.get("id")
        or brand_wizard.get("brand", {}).get("id")
    )
    if not brand_id:
        raise ValueError("brand_wizard missing brand_id/id")
    candidates = (
        survey.get("freebie_candidates")
        or survey.get("preferred_freebies")
        or survey.get("freebies")
        or []
    )
    if not candidates:
        # allow nested musician reflections shape
        reflections = survey.get("musician_reflections") or survey.get("reflections") or {}
        if isinstance(reflections, dict):
            candidates = reflections.get("freebie_candidates") or []
    if not candidates:
        raise ValueError(
            "musician survey YAML has no freebie_candidates/preferred_freebies — "
            "refusing hardcoded fallback"
        )
    # normalize to list of ids
    ids = []
    for c in candidates:
        if isinstance(c, str):
            ids.append(c)
        elif isinstance(c, dict):
            ids.append(str(c.get("id") or c.get("freebie_id") or c.get("name")))
    ids = [i for i in ids if i]
    if not ids:
        raise ValueError("freebie candidate list empty after normalize")
    digest = hashlib.sha256(f"{brand_id}|{'|'.join(ids)}".encode()).hexdigest()
    pick = ids[int(digest[:8], 16) % len(ids)]
    return {
        "brand_id": brand_id,
        "freebie_bundle_id": pick,
        "rationale": {
            "method": "sha256_mod_len",
            "candidate_count": len(ids),
            "inputs": ["brand_wizard.yaml", "musician_reflections_survey.yaml"],
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--brand-wizard", type=Path, default=None)
    ap.add_argument("--survey", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        # ephemeral fixtures in memory via temp files
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            bw = td_path / "brand.yaml"
            sv = td_path / "survey.yaml"
            bw.write_text("brand_id: test_music_brand\n", encoding="utf-8")
            sv.write_text(
                "freebie_candidates:\n  - hook_pack_a\n  - lyric_workbook_b\n",
                encoding="utf-8",
            )
            result = select_freebie(_load(bw), _load(sv))
            assert result["freebie_bundle_id"] in ("hook_pack_a", "lyric_workbook_b")
            try:
                select_freebie(_load(bw), {"no": "candidates"})
                raise AssertionError("expected hard error")
            except ValueError:
                pass
        print("OK: music-mode freebie selector self-test passed")
        return 0

    if not args.brand_wizard or not args.survey:
        print("ERROR: --brand-wizard and --survey required (or use --self-test)", file=sys.stderr)
        return 2

    try:
        result = select_freebie(_load(args.brand_wizard), _load(args.survey))
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    text = json.dumps(result, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
