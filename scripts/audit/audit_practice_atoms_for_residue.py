#!/usr/bin/env python3
"""Audit teacher EXERCISE atoms for RTF/blog residue.

OPD-107 follow-up: after tightening `_is_practice_atom` with negative-evidence
markers (font-stack tells, RTF tokens, HTML residue, blog/marketing CTAs,
mining-tool stamps), walk every teacher's approved + candidate EXERCISE atoms
and report which atoms now flip from pass to fail.

The target false-positive is `ahjan_EXERCISE_064_mined` whose body begins:
    "Helvetica;ArialMT; ;;;;; ;; Creating comparison videos for affiliate
     marketing on YouTube ... Step 1. Choose products ..."
The literal "Step 1." substring trips the positive-evidence pass without the
residue filter; with the filter it gets rejected (Helvetica;, ArialMT;,
"affiliate marketing", "YouTube channel", "Click here", and the blog CTA
"step-by-step guide on how to do it" all hit).

Output: artifacts/qa/practice_atom_residue_audit_<DATE>.json with:
  - per-teacher pass/fail/flip counts
  - newly_rejected: list of {teacher, atom_id, path, residue_markers[]}
  - regression watch: report any teacher whose pool drops > 25%
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Ensure repo root on sys.path
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

# Import after path insert
from phoenix_v4.planning.enrichment_select import (  # noqa: E402
    _RESIDUE_MARKERS,
    _is_practice_atom,
    _PRACTICE_RESIDUE_ALLOWLIST,
)

# yaml lazy-import — we tolerate yaml absence by using a minimal fallback,
# but for atom YAMLs we need real yaml.
try:
    import yaml  # type: ignore
except ImportError:
    print("PyYAML required: pip install pyyaml", file=sys.stderr)
    sys.exit(2)


TEACHER_BANKS_ROOT = REPO_ROOT / "SOURCE_OF_TRUTH" / "teacher_banks"


def _load_atom(path: Path) -> dict:
    """Load a teacher atom YAML and normalize body -> content like the
    registry_resolver does at runtime."""
    try:
        with open(path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
    except Exception as e:
        return {"_load_error": str(e)}
    if not isinstance(data, dict):
        return {}
    content = data.get("body") or data.get("content") or ""
    atom_id = data.get("atom_id") or path.stem
    # Build a planner-shaped dict: registry_resolver puts everything except
    # body/content into "metadata".
    metadata = {k: v for k, v in data.items() if k not in ("body", "content")}
    return {"atom_id": atom_id, "content": content, "metadata": metadata}


def _find_residue_markers(atom: dict) -> list[str]:
    """Return list of markers that match (for diagnostic reporting)."""
    content = str(atom.get("content") or "").strip().lower()
    if not content:
        return []
    hits = []
    for marker in _RESIDUE_MARKERS:
        if marker in content:
            hits.append(marker)
    return hits


def _looked_like_practice_before(atom: dict) -> bool:
    """Apply the legacy practice classifier (positive-evidence only) — what
    the gate accepted prior to the residue filter being added. We re-implement
    the old logic inline rather than importing it, because the new
    `_is_practice_atom` no longer exposes the pre-filter behavior."""
    import re

    if not isinstance(atom, dict):
        return False

    meta = atom.get("metadata") or {}
    if isinstance(meta, dict):
        slot_meta = str(meta.get("slot_type") or "").strip().lower()
        if slot_meta in ("exercise", "practice"):
            return True
        shape_meta = str(meta.get("shape") or meta.get("atom_shape") or "").strip().lower()
        if shape_meta in ("practice", "instruction", "exercise"):
            return True
        atom_type = str(meta.get("atom_type") or meta.get("type") or "").strip().lower()
        if atom_type in ("practice", "exercise", "instruction"):
            return True

    content = str(atom.get("content") or "").strip().lower()
    if not content:
        return False

    # Reuse same positive markers from enrichment_select.
    from phoenix_v4.planning.enrichment_select import (
        _NUMBERED_STEP_RE,
        _PRACTICE_STEP_MARKERS,
    )

    if _NUMBERED_STEP_RE.search(content):
        return True
    for marker in _PRACTICE_STEP_MARKERS:
        if marker in content:
            return True
    return False


def _scan_teacher_pool(
    teacher_id: str, exercise_dir: Path, pool_label: str
) -> dict:
    """Scan a single teacher's EXERCISE atom directory."""
    if not exercise_dir.exists():
        return {
            "teacher": teacher_id,
            "pool": pool_label,
            "total": 0,
            "pass_before": 0,
            "pass_after": 0,
            "flips_to_fail": 0,
            "atoms": [],
        }

    atoms_meta: list[dict] = []
    pass_before = 0
    pass_after = 0
    flips_to_fail: list[dict] = []
    load_errors: list[dict] = []

    for path in sorted(exercise_dir.glob("*.yaml")):
        atom = _load_atom(path)
        if atom.get("_load_error"):
            load_errors.append({"path": str(path), "error": atom["_load_error"]})
            continue
        before = _looked_like_practice_before(atom)
        after = _is_practice_atom(atom)
        if before:
            pass_before += 1
        if after:
            pass_after += 1
        if before and not after:
            flips_to_fail.append(
                {
                    "atom_id": atom.get("atom_id"),
                    "path": str(path.relative_to(REPO_ROOT)),
                    "residue_markers": _find_residue_markers(atom),
                    "content_preview": (str(atom.get("content") or "")[:160] + "..."),
                }
            )

    return {
        "teacher": teacher_id,
        "pool": pool_label,
        "total": len([p for p in exercise_dir.glob("*.yaml")]),
        "pass_before": pass_before,
        "pass_after": pass_after,
        "flips_to_fail": len(flips_to_fail),
        "flips_to_fail_atoms": flips_to_fail,
        "load_errors": load_errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=REPO_ROOT
        / "artifacts"
        / "qa"
        / "practice_atom_residue_audit_2026-05-18.json",
        help="Output JSON report path",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Print per-atom details to stdout"
    )
    args = parser.parse_args()

    if not TEACHER_BANKS_ROOT.exists():
        print(f"Teacher banks root not found: {TEACHER_BANKS_ROOT}", file=sys.stderr)
        return 2

    per_teacher_pools: list[dict] = []
    for teacher_dir in sorted(TEACHER_BANKS_ROOT.iterdir()):
        if not teacher_dir.is_dir():
            continue
        teacher_id = teacher_dir.name
        for sub in ("approved_atoms", "candidate_atoms"):
            ex_dir = teacher_dir / sub / "EXERCISE"
            scan = _scan_teacher_pool(teacher_id, ex_dir, sub)
            if scan["total"] > 0 or scan["flips_to_fail"] > 0:
                per_teacher_pools.append(scan)

    # Aggregate totals
    total_atoms = sum(p["total"] for p in per_teacher_pools)
    total_before = sum(p["pass_before"] for p in per_teacher_pools)
    total_after = sum(p["pass_after"] for p in per_teacher_pools)
    total_flips = sum(p["flips_to_fail"] for p in per_teacher_pools)

    # Disproportionate-impact watchlist: teachers where >25% of previously-
    # passing atoms now fail.
    disproportionate = []
    for p in per_teacher_pools:
        if p["pass_before"] >= 4 and p["flips_to_fail"] > 0:
            ratio = p["flips_to_fail"] / max(p["pass_before"], 1)
            if ratio > 0.25:
                disproportionate.append(
                    {
                        "teacher": p["teacher"],
                        "pool": p["pool"],
                        "pass_before": p["pass_before"],
                        "flips_to_fail": p["flips_to_fail"],
                        "ratio": round(ratio, 3),
                    }
                )

    target_hit = any(
        any(
            a["atom_id"] == "ahjan_EXERCISE_064_mined"
            for a in p.get("flips_to_fail_atoms", [])
        )
        for p in per_teacher_pools
    )

    report = {
        "audit": "OPD-107 follow-up: practice_atom residue filter",
        "date": "2026-05-18",
        "filter_markers_count": len(_RESIDUE_MARKERS),
        "allowlist_size": len(_PRACTICE_RESIDUE_ALLOWLIST),
        "summary": {
            "total_atoms_scanned": total_atoms,
            "pass_before": total_before,
            "pass_after": total_after,
            "newly_rejected": total_flips,
            "target_atom_rejected": target_hit,
        },
        "disproportionate_impact_watchlist": disproportionate,
        "per_teacher": per_teacher_pools,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Audit report: {args.out}")
    print(f"  total scanned: {total_atoms}")
    print(f"  pass before: {total_before}")
    print(f"  pass after: {total_after}")
    print(f"  newly rejected: {total_flips}")
    print(f"  target ahjan_EXERCISE_064_mined rejected: {target_hit}")
    if disproportionate:
        print("  disproportionate-impact watch:")
        for d in disproportionate:
            print(
                f"    - {d['teacher']}/{d['pool']}: {d['flips_to_fail']}/{d['pass_before']}"
                f" ({d['ratio']*100:.1f}%)"
            )
    if args.verbose:
        for p in per_teacher_pools:
            if p["flips_to_fail"] > 0:
                print(f"\n  {p['teacher']}/{p['pool']} newly rejected:")
                for a in p["flips_to_fail_atoms"][:5]:
                    markers = ", ".join(a["residue_markers"][:5])
                    print(f"    - {a['atom_id']}: markers=[{markers}]")
                if len(p["flips_to_fail_atoms"]) > 5:
                    print(f"    ... and {len(p['flips_to_fail_atoms']) - 5} more")

    return 0


if __name__ == "__main__":
    sys.exit(main())
