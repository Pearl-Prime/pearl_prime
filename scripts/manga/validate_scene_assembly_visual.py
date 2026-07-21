#!/usr/bin/env python3
"""Structural + visual candidate acceptance / quarantine routing.

Enforces candidate lifecycle:
  plans/ → structural_validation/ → candidates/ → visual_validation/
  → accepted/ | rejected/  (+ promotion_records/)

Rules:
  - candidate with no operator verdict stays quarantined (not accepted)
  - stale verdict cannot promote a changed candidate (plan_hash mismatch)
  - --accepted-only refuses non-accepted sources

Usage:
  PYTHONPATH=scripts/manga python3 scripts/manga/validate_scene_assembly_visual.py \\
    --candidate-root <root> --plan <plans/foo_plan.json> [--verdict pass|fail]
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "manga"))

from structural_composition import (  # noqa: E402
    StructuralHardFail,
    emit_support_overlay,
    render_from_verified_plan,
    verify_plan_hash,
)

QUARANTINE_SUBDIRS = (
    "plans",
    "structural_validation",
    "candidates",
    "visual_validation",
    "accepted",
    "rejected",
    "promotion_records",
)


def ensure_quarantine_tree(root: Path) -> None:
    for sub in QUARANTINE_SUBDIRS:
        (root / sub).mkdir(parents=True, exist_ok=True)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, doc: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def run_structural_validation(plan_path: Path, root: Path) -> dict[str, Any]:
    envelope = load_json(plan_path)
    report: dict[str, Any] = {
        "plan_path": str(plan_path),
        "plan_hash": envelope.get("plan_hash"),
        "status": "pass",
        "failures": [],
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        verify_plan_hash(envelope)
        # Renderer consumption check — must verify hash, not recompute placement
        consumed = render_from_verified_plan(envelope, require_hash=True)
        report["renderer_consume"] = {
            "ok": True,
            "recomputed_placement": consumed["recomputed_placement"],
            "placement_count": len(consumed["resolved_placements"]),
        }
        overlay = emit_support_overlay(
            envelope,
            out_path=root / "structural_validation" / f"{envelope['plan_body']['panel_id']}_overlay.png",
        )
        report["support_overlay"] = {
            "same_resolved_transform_path": overlay["same_resolved_transform_path"],
            "json_path": overlay.get("json_path"),
            "png_path": overlay.get("png_path"),
        }
    except StructuralHardFail as e:
        report["status"] = "fail"
        report["failures"].append({"code": e.code, "message": str(e)})

    out = root / "structural_validation" / f"{Path(plan_path).stem}_validation.json"
    write_json(out, report)
    report["validation_path"] = str(out)
    return report


def stage_candidate(plan_path: Path, root: Path, structural_report: dict[str, Any]) -> Path:
    """Copy plan into candidates/ only after structural validation record exists."""
    ensure_quarantine_tree(root)
    envelope = load_json(plan_path)
    cand_id = f"{envelope['plan_body']['panel_id']}__{envelope['plan_hash'][:12]}"
    cand_dir = root / "candidates" / cand_id
    cand_dir.mkdir(parents=True, exist_ok=True)
    dest = cand_dir / "plan_envelope.json"
    shutil.copy2(plan_path, dest)
    write_json(cand_dir / "structural_validation.json", structural_report)
    write_json(cand_dir / "status.json", {
        "candidate_id": cand_id,
        "plan_hash": envelope["plan_hash"],
        "quarantined": True,
        "operator_verdict": None,
        "promotion": None,
        "note": "No operator verdict — stays quarantined (ACCEPT-001 / candidate routing)",
    })
    return cand_dir


def apply_operator_verdict(
    candidate_dir: Path,
    *,
    verdict: str,
    operator: str = "operator",
    expected_plan_hash: str | None = None,
) -> dict[str, Any]:
    """Promote or reject. Stale verdict (hash mismatch) cannot promote."""
    root = candidate_dir.parents[1] if candidate_dir.parent.name == "candidates" else candidate_dir.parent
    # candidate_dir = root/candidates/<id>
    root = candidate_dir.parent.parent
    ensure_quarantine_tree(root)

    envelope = load_json(candidate_dir / "plan_envelope.json")
    current_hash = envelope["plan_hash"]
    status = load_json(candidate_dir / "status.json")

    if expected_plan_hash is not None and expected_plan_hash != current_hash:
        record = {
            "result": "refused_stale_verdict",
            "expected_plan_hash": expected_plan_hash,
            "current_plan_hash": current_hash,
            "operator": operator,
            "verdict_attempted": verdict,
            "at": datetime.now(timezone.utc).isoformat(),
        }
        write_json(
            root / "promotion_records" / f"{candidate_dir.name}_stale_refused.json",
            record,
        )
        raise StructuralHardFail(
            "STALE_VERDICT",
            "stale verdict cannot promote changed candidate "
            f"(expected={expected_plan_hash[:12]}… current={current_hash[:12]}…)",
        )

    status["operator_verdict"] = verdict
    status["operator"] = operator
    status["verdict_at"] = datetime.now(timezone.utc).isoformat()

    visual_doc = {
        "candidate_id": candidate_dir.name,
        "plan_hash": current_hash,
        "operator_verdict": verdict,
        "operator": operator,
        "at": status["verdict_at"],
    }
    write_json(root / "visual_validation" / f"{candidate_dir.name}_visual.json", visual_doc)

    if verdict == "pass":
        dest = root / "accepted" / candidate_dir.name
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(candidate_dir, dest)
        status["quarantined"] = False
        status["promotion"] = "accepted"
        promo = {
            "result": "accepted",
            "candidate_id": candidate_dir.name,
            "plan_hash": current_hash,
            "operator": operator,
            "at": status["verdict_at"],
        }
    elif verdict == "fail":
        dest = root / "rejected" / candidate_dir.name
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(candidate_dir, dest)
        status["quarantined"] = False
        status["promotion"] = "rejected"
        promo = {
            "result": "rejected",
            "candidate_id": candidate_dir.name,
            "plan_hash": current_hash,
            "operator": operator,
            "at": status["verdict_at"],
        }
    else:
        raise StructuralHardFail("BAD_VERDICT", f"verdict must be pass|fail, got {verdict!r}")

    write_json(candidate_dir / "status.json", status)
    write_json(root / "promotion_records" / f"{candidate_dir.name}_{promo['result']}.json", promo)
    return promo


def assert_accepted_only(source_path: Path, candidate_root: Path) -> None:
    """Accepted-only mode: refuse sources not under accepted/."""
    accepted = (candidate_root / "accepted").resolve()
    src = source_path.resolve()
    try:
        src.relative_to(accepted)
    except ValueError as e:
        raise StructuralHardFail(
            "ACCEPTED_ONLY_REFUSED",
            f"accepted-only mode refuses non-accepted source: {source_path}",
        ) from e


def candidate_has_operator_verdict(candidate_dir: Path) -> bool:
    status = load_json(candidate_dir / "status.json")
    return status.get("operator_verdict") in ("pass", "fail")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--candidate-root", type=Path, required=True)
    ap.add_argument("--plan", type=Path, help="Plan envelope under plans/ or elsewhere")
    ap.add_argument("--candidate-dir", type=Path, help="Existing candidates/<id> dir")
    ap.add_argument("--verdict", choices=["pass", "fail"], default=None)
    ap.add_argument("--operator", default="operator")
    ap.add_argument(
        "--expected-plan-hash",
        default=None,
        help="If set, must match current candidate plan_hash or promotion is refused",
    )
    ap.add_argument(
        "--accepted-only",
        action="store_true",
        help="Refuse any --plan / --candidate-dir not under accepted/",
    )
    ap.add_argument("--stage-only", action="store_true", help="Validate + stage; no verdict")
    args = ap.parse_args(argv)

    root = args.candidate_root
    ensure_quarantine_tree(root)

    try:
        if args.accepted_only:
            target = args.candidate_dir or args.plan
            if not target:
                raise StructuralHardFail("ACCEPTED_ONLY_NO_TARGET", "need --plan or --candidate-dir")
            assert_accepted_only(target, root)

        if args.plan:
            report = run_structural_validation(args.plan, root)
            if report["status"] != "pass":
                print(json.dumps(report, indent=2))
                return 1
            cand = stage_candidate(args.plan, root, report)
            print(json.dumps({
                "staged": str(cand),
                "quarantined": True,
                "operator_verdict": None,
                "structural_validation": report["validation_path"],
            }, indent=2))
            if args.stage_only or not args.verdict:
                # No verdict → stays quarantined
                return 0
            promo = apply_operator_verdict(
                cand,
                verdict=args.verdict,
                operator=args.operator,
                expected_plan_hash=args.expected_plan_hash,
            )
            print(json.dumps(promo, indent=2))
            return 0

        if args.candidate_dir:
            if not candidate_has_operator_verdict(args.candidate_dir) and not args.verdict:
                status = load_json(args.candidate_dir / "status.json")
                print(json.dumps({
                    "candidate_dir": str(args.candidate_dir),
                    "quarantined": True,
                    "operator_verdict": status.get("operator_verdict"),
                    "note": "no operator verdict — stays quarantined",
                }, indent=2))
                return 0
            if not args.verdict:
                print("ERROR: --verdict required to promote", file=sys.stderr)
                return 2
            promo = apply_operator_verdict(
                args.candidate_dir,
                verdict=args.verdict,
                operator=args.operator,
                expected_plan_hash=args.expected_plan_hash,
            )
            print(json.dumps(promo, indent=2))
            return 0

        print("ERROR: provide --plan and/or --candidate-dir", file=sys.stderr)
        return 2
    except StructuralHardFail as e:
        print(json.dumps({"ok": False, "code": e.code, "error": str(e)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
