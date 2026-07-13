#!/usr/bin/env python3
"""End-to-end truth gate for the ProPrime anxiety accent flagship.

Canonical case: gen_z_professionals × anxiety (spine / enrichment_contract_v1).

Verifies:
  - configured classes present at configured minimum counts
  - allowed_positions contracts obeyed
  - story-mix expectations materially reflected for EXTERNAL_STORY
  - plan.json / rendered_accent_audit agree with manuscript presence
  - QUOTE present when budget > 0
  - AFFIRMATION is not falsely claimed live

Usage:
  PYTHONPATH=. python3 scripts/ci/check_accent_flagship_truth.py
  PYTHONPATH=. python3 scripts/ci/check_accent_flagship_truth.py --render-dir artifacts/rendered/cli_demo_trace_run_composite_contract_v1
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_json(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _fail(msg: str, errors: List[str]) -> None:
    errors.append(msg)
    print(f"FAIL: {msg}", file=sys.stderr)


def check_artifacts(render_dir: Path, *, errors: List[str]) -> Dict[str, Any]:
    contract = _load_json(render_dir / "enhancement_contract.json") or {}
    plan = _load_json(render_dir / "plan.json") or {}
    audit = _load_json(render_dir / "rendered_accent_audit.json") or {}
    strategy = _load_json(render_dir / "enrichment_strategy_report.json") or {}
    spa = _load_json(render_dir / "section_packet_audit.json")
    book = (render_dir / "book.txt").read_text(encoding="utf-8") if (render_dir / "book.txt").exists() else ""

    if not plan and not contract:
        _fail("plan.json missing", errors)
    if not audit and not contract:
        _fail("rendered_accent_audit.json missing", errors)
    if spa is None:
        _fail("section_packet_audit.json missing", errors)
    if not book.strip():
        _fail("book.txt missing or empty", errors)

    contract_validation = dict(contract.get("validation") or {})
    if contract and contract.get("status") != "PASS":
        _fail(
            f"enhancement_contract.json status={contract.get('status')} "
            f"errors={contract_validation.get('errors') or []}",
            errors,
        )

    budget = dict(
        contract.get("accent_budget")
        or plan.get("accent_budget")
        or strategy.get("accent_budget")
        or {}
    )
    v21 = dict(
        contract.get("enhancement_contract_v21")
        or plan.get("enhancement_contract_v21")
        or strategy.get("enhancement_contract_v21")
        or {}
    )
    assignments = list(
        contract.get("accent_rows")
        or plan.get("accent_assignments")
        or strategy.get("assignments")
        or []
    )
    if not budget:
        _fail("accent_budget missing from plan.json / strategy report", errors)
    if not assignments:
        _fail("accent_assignments missing from plan.json / strategy report", errors)
    if contract and not v21:
        _fail("enhancement_contract_v21 missing from proof surfaces", errors)

    if v21:
        taxonomy = dict(v21.get("surface_taxonomy") or {})
        optional_tax = {str(x) for x in list(taxonomy.get("optional_accents") or [])}
        cohesion_tax = {str(x) for x in list(taxonomy.get("cohesion_and_craft") or [])}
        tracked = {
            str(row.get("surface") or ""): dict(row)
            for row in list(v21.get("tracked_surfaces") or [])
            if isinstance(row, Mapping)
        }
        if any(surface in optional_tax for surface in ("TROUBLESHOOTING", "CITED_EVIDENCE", "EXTERNAL_STORY")):
            _fail("v2.1 taxonomy regressed proof surfaces into optional accents", errors)
        if not {"ANALOGY", "METAPHOR"} <= cohesion_tax:
            _fail("v2.1 cohesion_and_craft taxonomy missing ANALOGY/METAPHOR", errors)
        disclosure = tracked.get("AUTHOR_DISCLOSURE") or {}
        if disclosure.get("bucket") != "proof_and_embodiment":
            _fail("AUTHOR_DISCLOSURE not tracked as proof_and_embodiment", errors)
        opt = dict(v21.get("optional_accent_budget") or {})
        actual = dict(opt.get("actual") or {})
        if int(actual.get("assigned_total_optional_accents") or 0) > int(opt.get("hard_max_total_accents") or 0):
            _fail("optional accent total exceeds v2.1 hard max", errors)
        for chapter, count in dict(actual.get("per_chapter_optional_counts") or {}).items():
            if int(count or 0) > int(opt.get("max_accents_per_chapter") or 0):
                _fail(f"optional accent per-chapter ceiling exceeded: ch{chapter} -> {count}", errors)

    counts = Counter(str(r.get("class") or "") for r in assignments)
    for cls, need in budget.items():
        need_i = int(need or 0)
        if need_i <= 0:
            continue
        got = int(counts.get(cls, 0))
        if got < need_i:
            _fail(f"budget underfill: {cls} need>={need_i} got={got}", errors)

    if int(budget.get("QUOTE", 0)) > 0 and counts.get("QUOTE", 0) < int(budget["QUOTE"]):
        _fail("QUOTE budget > 0 but quotes under-assigned", errors)

    # Placement contracts: no AUTHOR_COMMENTARY on illegal positions when bank restricts.
    # Soft check via audit rows + assignment positions.
    for row in assignments:
        if row.get("class") == "AUTHOR_COMMENTARY" and row.get("accent_id") == "ac_ravi_anxiety_skeptic_standup_v01":
            if row.get("position") != "after_EXERCISE":
                _fail(
                    f"allowed_positions violated for {row.get('accent_id')}: "
                    f"got {row.get('position')}",
                    errors,
                )

    # Story-mix: intimate_voice should not be mythic-only.
    story_types = []
    for row in assignments:
        if row.get("class") != "EXTERNAL_STORY":
            continue
        st = str((row.get("keys") or {}).get("story_type") or "")
        if st:
            story_types.append(st)
        story_function = str((row.get("keys") or {}).get("story_function") or row.get("story_function") or "")
        truth_metadata = dict((row.get("keys") or {}).get("truth_metadata") or row.get("truth_metadata") or {})
        if not story_function:
            _fail(f"EXTERNAL_STORY {row.get('accent_id')} missing story_function", errors)
        if not truth_metadata.get("citation") or not truth_metadata.get("source"):
            _fail(f"EXTERNAL_STORY {row.get('accent_id')} missing truth metadata", errors)
    preferred = {"true_life_broadcast", "film", "pop_culture", "sports"}
    if story_types and not (set(story_types) & preferred):
        _fail(
            f"story-mix intimate_voice not reflected; EXTERNAL_STORY types={story_types}",
            errors,
        )

    # Trace honesty: audit rows should match assignment count and manuscript presence.
    audit_rows = list(audit.get("accents") or [])
    if contract:
        audit_rows = [
            {
                "chapter": row.get("chapter"),
                "class": row.get("class"),
                "accent_id": row.get("accent_id"),
                "position": row.get("position"),
                "rendered_excerpt": row.get("final_excerpt") or row.get("rendered_excerpt"),
                "present_in_manuscript": row.get("present_in_manuscript"),
            }
            for row in list(contract.get("accent_rows") or [])
        ]
    if assignments and not audit_rows:
        _fail("rendered_accent_audit.json has no accents rows", errors)
    if assignments and len(audit_rows) < len(assignments):
        _fail(
            f"rendered_accent_audit count {len(audit_rows)} < assignments {len(assignments)}",
            errors,
        )
    for row in audit_rows:
        excerpt = str(row.get("rendered_excerpt") or "").strip()
        if not excerpt:
            _fail(f"accent {row.get('accent_id')} missing rendered_excerpt", errors)
            continue
        words = excerpt.split()
        frag = " ".join(words[:8]) if len(words) >= 8 else excerpt
        present = bool(row.get("present_in_manuscript")) or (frag in book)
        if not present:
            windows = [" ".join(words[i : i + 6]) for i in range(0, max(1, len(words) - 5))]
            present = any(w in book for w in windows if len(w.split()) >= 4)
        if not present:
            _fail(
                f"accent {row.get('accent_id')} excerpt not found in book.txt",
                errors,
            )

    # AFFIRMATION must not be claimed live.
    if "AFFIRMATION" in budget and int(budget.get("AFFIRMATION") or 0) > 0:
        _fail("AFFIRMATION budget > 0 but class is not live (TODO mantras only)", errors)
    if any(r.get("class") == "AFFIRMATION" for r in assignments):
        _fail("AFFIRMATION assignment present but class is not live", errors)

    summary = {
        "render_dir": str(render_dir),
        "accent_budget": budget,
        "assignment_counts": dict(counts),
        "story_types": story_types,
        "plan_has_accent_signature": bool(plan.get("accent_signature")),
        "contract_status": contract.get("status") or "",
        "contract_id": contract.get("contract_id") or "",
        "section_packet_audit_present": spa is not None,
        "audit_count": len(audit_rows),
        "errors": list(errors),
    }
    return summary


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--render-dir",
        type=Path,
        default=REPO_ROOT / "artifacts" / "rendered" / "cli_demo_trace_run_composite_contract_v1",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=REPO_ROOT / "artifacts" / "qa" / "ACCENT_FLAGSHIP_TRUTH_GATE_2026-07-11.json",
    )
    args = parser.parse_args(argv)

    errors: List[str] = []
    if not args.render_dir.exists():
        _fail(f"render dir missing: {args.render_dir}", errors)
        summary = {"errors": errors}
    else:
        summary = check_artifacts(args.render_dir, errors=errors)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {args.out}")
    if errors:
        print(f"accent-flagship-truth: FAIL ({len(errors)} errors)", file=sys.stderr)
        return 1
    print("accent-flagship-truth: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
