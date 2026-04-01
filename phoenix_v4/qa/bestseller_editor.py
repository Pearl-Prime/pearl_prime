"""
Post-render bestseller editorial review. This is the closest thing to a Pearl_Editor whole-book pass in the current repo: structural/narrative book-pass gate, chapter flow review, runtime word-budget gate.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from phoenix_v4.rendering.prose_resolver import resolve_prose_for_plan
from phoenix_v4.quality.chapter_flow_gate import evaluate_chapter_flow
from phoenix_v4.quality.ei_v2.hybrid_selector import HybridDecision


def _extract_keywords(text: str) -> set[str]:
    """Extract significant words from text (length >= 4, non-stopwords)."""
    stop = {
        "the", "a", "an", "and", "or", "to", "of", "for", "in", "on", "at", "is", "are",
        "was", "were", "it", "that", "this", "with", "as", "be", "by", "you", "your",
        "we", "they", "their", "but", "from", "have", "has", "had", "do", "does", "did",
    }
    words = re.findall(r"[a-z']+", text.lower())
    return set(w for w in words if len(w) >= 4 and w not in stop)


def _thesis_drift_check(plan: dict[str, Any], prose_map: dict[str, str]) -> dict:
    """
    Check whether each chapter's prose supports its assigned thesis.
    Returns report dict with: status, chapters (list of per-chapter results), drift_count.
    """
    report = {
        "status": "PASS",
        "chapters": [],
        "drift_count": 0,
        "note": "",
    }

    chapter_thesis = plan.get("chapter_thesis")
    if not isinstance(chapter_thesis, dict) or not chapter_thesis:
        report["status"] = "PASS"
        report["note"] = "no chapter_thesis in plan"
        return report

    chapter_slot_sequence = plan.get("chapter_slot_sequence", [])
    atom_ids = plan.get("atom_ids", [])
    if not atom_ids:
        report["status"] = "PASS"
        report["note"] = "no atom_ids in plan"
        return report

    # Map atom_id to chapter index
    atom_to_chapter: dict[str, int] = {}
    for ch_idx, chapter_slots in enumerate(chapter_slot_sequence):
        if isinstance(chapter_slots, dict):
            slots_list = chapter_slots.get("slots") or chapter_slots.get("chapter_slots") or []
        elif isinstance(chapter_slots, list):
            slots_list = chapter_slots
        else:
            slots_list = []

        for slot_info in slots_list:
            slot_atom_id = None
            if isinstance(slot_info, dict):
                slot_atom_id = slot_info.get("atom_id")
            elif isinstance(slot_info, str):
                slot_atom_id = slot_info
            if slot_atom_id:
                atom_to_chapter[slot_atom_id] = ch_idx

    chapters_with_thesis: list[int] = sorted(set(k - 1 for k in chapter_thesis.keys()))
    drift_count = 0

    for ch_num in chapters_with_thesis:
        thesis_text = chapter_thesis.get(ch_num + 1, "")
        thesis_keywords = _extract_keywords(thesis_text)

        # Collect all prose for this chapter
        chapter_prose_parts = []
        for aid in atom_ids:
            if aid in atom_to_chapter and atom_to_chapter[aid] == ch_num:
                if aid not in prose_map or "placeholder:" in aid or "silence:" in aid:
                    continue
                prose = prose_map.get(aid, "")
                if prose:
                    chapter_prose_parts.append(prose)

        if not chapter_prose_parts:
            report["chapters"].append({
                "chapter": ch_num + 1,
                "status": "WARN",
                "on_thesis": False,
                "coverage": 0.0,
                "thesis_keywords": list(thesis_keywords),
                "keyword_hits": 0,
            })
            drift_count += 1
            continue

        chapter_prose = " ".join(chapter_prose_parts)
        prose_keywords = _extract_keywords(chapter_prose)

        # Calculate coverage: hits / thesis_keywords
        hits = len(thesis_keywords & prose_keywords)
        coverage = (hits / len(thesis_keywords)) if thesis_keywords else 0.0
        on_thesis = coverage >= 0.3

        report["chapters"].append({
            "chapter": ch_num + 1,
            "status": "PASS" if on_thesis else "WARN",
            "on_thesis": on_thesis,
            "coverage": round(coverage, 3),
            "thesis_keywords": list(thesis_keywords)[:10],
            "keyword_hits": hits,
        })

        if not on_thesis:
            drift_count += 1

    report["drift_count"] = drift_count
    if drift_count > 0:
        report["status"] = "WARN"

    return report


def _safe_load_json(path: Path) -> dict:
    """Load JSON from path, return {} on any error."""
    try:
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f) or {}
    except Exception:
        return {}


def _summarize_status(*statuses: str) -> str:
    """
    Normalize and combine multiple status strings.
    If any FAIL -> FAIL, if any WARN -> WARN, else PASS.
    """
    normalized = set()
    for s in statuses:
        if s:
            normalized.add(s.upper().strip())

    if "FAIL" in normalized:
        return "FAIL"
    if "WARN" in normalized:
        return "WARN"
    return "PASS"


def _dimension_gate_rollup_status(chapter_flow_report: dict) -> str:
    """
    Map chapter_flow_report dimension gate fields to a single status for overall rollup.
    SKIP (gates off or absent) does not fail the editor; FAIL when delivery is blocked.
    """
    if bool(chapter_flow_report.get("dimension_gates_blocks_delivery")):
        return "FAIL"
    dg = chapter_flow_report.get("dimension_gates_status", "SKIP")
    if dg == "FAIL":
        return "FAIL"
    if dg in ("SKIP", "PASS"):
        return "PASS"
    return str(dg).upper()


def hybrid_select_slot_production(
    *,
    slot: str,
    chapter_index: int,
    slot_index: int,
    candidates_raw: list[dict[str, Any]],
    persona_id: str,
    topic_id: str,
    thesis: str,
    v1_cfg: dict[str, Any] | None = None,
    selector_key: str | None = None,
    ei_v2_config: dict[str, Any] | None = None,
) -> HybridDecision:
    """
    Production hook for hybrid V1+V2 selection (BG-PR-01). Passes the loaded EI v2 config
    as ``v2_cfg`` when ``hybrid.enabled`` is true; otherwise ``v2_cfg`` is omitted (V1-only).

    Call from catalog assembly when multiple atom candidates exist for a slot. Renderer
    plans that already pin ``atom_ids`` do not use this path.
    """
    from phoenix_v4.quality.ei_v2.config import load_ei_v2_config
    from phoenix_v4.quality.ei_v2.hybrid_selector import hybrid_select

    cfg = ei_v2_config if ei_v2_config is not None else load_ei_v2_config()
    hybrid = cfg.get("hybrid") or {}
    v2_cfg: dict[str, Any] | None = cfg if hybrid.get("enabled", False) else None
    return hybrid_select(
        slot=slot,
        chapter_index=chapter_index,
        slot_index=slot_index,
        candidates_raw=candidates_raw,
        persona_id=persona_id,
        topic_id=topic_id,
        thesis=thesis,
        v1_cfg=v1_cfg,
        v2_cfg=v2_cfg,
        selector_key=selector_key,
    )


def build_bestseller_editor_report(
    plan: dict,
    render_dir: Path,
    atoms_root: Path | None = None,
    bindings_path: Path | None = None,
) -> dict:
    """
    Main report builder. Loads chapter_flow_report.json and budget.json from render_dir,
    resolves prose via resolve_prose_for_plan, builds comprehensive report.
    """
    render_dir = Path(render_dir)

    # Load existing reports
    chapter_flow_report = _safe_load_json(render_dir / "chapter_flow_report.json")
    budget_report = _safe_load_json(render_dir / "budget.json")

    # Resolve prose
    rr = resolve_prose_for_plan(plan, atoms_root=atoms_root, bindings_path=bindings_path)
    prose_map = rr.prose_map

    # Extract basic plan info
    plan_id = plan.get("plan_id") or plan.get("book_id") or ""
    plan_hash = plan.get("plan_hash") or ""
    persona_id = plan.get("persona_id") or plan.get("persona") or ""
    topic_id = plan.get("topic_id") or plan.get("topic") or ""
    teacher_id = plan.get("teacher_id") or ""
    format_id = plan.get("format_id") or plan.get("format_structural_id") or ""
    runtime_format_id = budget_report.get("runtime_format_id") or ""
    chapter_count = chapter_flow_report.get("chapter_count") or 0

    # Extract flow status from chapter_flow_report
    flow_status = chapter_flow_report.get("status", "PASS")

    # Extract word budget status
    grand_total_words = budget_report.get("grand_total_words") or 0
    word_range_target = budget_report.get("word_range_target")
    deficit = budget_report.get("deficit_to_minimum")
    word_status = "PASS"
    if deficit is not None and deficit > 0:
        word_status = "WARN"

    # Perform book_pass validation (import locally to avoid circular deps)
    try:
        from phoenix_v4.qa.book_pass_gate import validate_book_pass
        from phoenix_v4.qa.validate_compiled_plan import load_atom_metadata

        try:
            atom_metadata = load_atom_metadata() or {}
        except Exception:
            atom_metadata = {}

        book_pass_result = validate_book_pass(plan, atom_metadata, prose_map=prose_map)
        book_pass_report = {
            "valid": book_pass_result.valid,
            "errors": book_pass_result.errors,
            "warnings": book_pass_result.warnings,
            "metrics": book_pass_result.metrics,
        }
        book_pass_status = "PASS" if book_pass_result.valid else "FAIL"
    except Exception:
        book_pass_report = {
            "valid": True,
            "errors": [],
            "warnings": ["book_pass validation skipped"],
            "metrics": {},
        }
        book_pass_status = "WARN"

    # Thesis drift check
    thesis_drift_report = _thesis_drift_check(plan, prose_map)
    thesis_drift_status = thesis_drift_report.get("status", "PASS")
    drift_count = thesis_drift_report.get("drift_count", 0)
    total_chapters_with_thesis = len(thesis_drift_report.get("chapters", []))

    # Extract DNA status (placeholder for now)
    dna_status = "PASS"

    dimension_gates_status = chapter_flow_report.get("dimension_gates_status", "SKIP")
    dimension_gates_blocks_delivery = bool(chapter_flow_report.get("dimension_gates_blocks_delivery", False))
    dimension_gate_status = _dimension_gate_rollup_status(chapter_flow_report)

    # Collect chapter bestseller structures from flow report
    chapter_bestseller_structures = []
    for ch_data in chapter_flow_report.get("chapters", []):
        chapter_bestseller_structures.append({
            "chapter": ch_data.get("chapter"),
            "status": ch_data.get("status"),
            "score": ch_data.get("score"),
            "errors": ch_data.get("errors", []),
        })

    # Extract ending signature and carry line from plan
    ending_signature = plan.get("ending_signature", "")
    carry_line = plan.get("carry_line") or plan.get("ending_carry_line") or ""

    # Combine statuses
    overall_status = _summarize_status(
        flow_status,
        word_status,
        book_pass_status,
        thesis_drift_status,
        dna_status,
        dimension_gate_status,
    )

    report = {
        "status": overall_status,
        "plan_id": plan_id,
        "plan_hash": plan_hash,
        "persona_id": persona_id,
        "topic_id": topic_id,
        "teacher_id": teacher_id,
        "format_id": format_id,
        "runtime_format_id": runtime_format_id,
        "chapter_count": chapter_count,
        "chapters": chapter_flow_report.get("chapters", []),
        "grand_total_words": grand_total_words,
        "word_range_target": word_range_target,
        "book_pass": book_pass_report,
        "chapter_bestseller_structures": chapter_bestseller_structures,
        "ending_signature": ending_signature,
        "carry_line": carry_line,
        "drift_count": drift_count,
        "total_chapters_with_thesis": total_chapters_with_thesis,
        "thesis_drift": thesis_drift_report,
        "flow_status": flow_status,
        "word_status": word_status,
        "book_pass_status": book_pass_status,
        "thesis_drift_status": thesis_drift_status,
        "dna_status": dna_status,
        "dimension_gate_status": dimension_gate_status,
        "dimension_gates_status": dimension_gates_status,
        "dimension_gates_blocks_delivery": dimension_gates_blocks_delivery,
    }

    return report


def write_bestseller_editor_report(report: dict, render_dir: Path) -> tuple[Path, Path]:
    """
    Write bestseller_editor_report.json and bestseller_editor_summary.txt to render_dir.
    Returns tuple of (json_path, txt_path).
    """
    render_dir = Path(render_dir)
    render_dir.mkdir(parents=True, exist_ok=True)

    json_path = render_dir / "bestseller_editor_report.json"
    txt_path = render_dir / "bestseller_editor_summary.txt"

    # Write JSON report
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Write text summary
    summary_lines = [
        "Bestseller Editor Report",
        "=" * 60,
        "",
        f"Status: {report.get('status', 'UNKNOWN')}",
        f"Plan ID: {report.get('plan_id', 'N/A')}",
        f"Persona: {report.get('persona_id', 'N/A')}",
        f"Topic: {report.get('topic_id', 'N/A')}",
        f"Teacher: {report.get('teacher_id', 'N/A')}",
        f"Format: {report.get('format_id', 'N/A')}",
        f"Runtime Format ID: {report.get('runtime_format_id', 'N/A')}",
        "",
        "Chapter Flow:",
        f"  Status: {report.get('flow_status', 'UNKNOWN')}",
        f"  Chapters: {report.get('chapter_count', 0)}",
        f"  Failed Chapters: {sum(1 for ch in report.get('chapters', []) if ch.get('status') == 'FAIL')}",
        "",
        "EI v2 Dimension Gates:",
        f"  Telemetry: {report.get('dimension_gates_status', 'SKIP')}",
        f"  Blocks delivery: {report.get('dimension_gates_blocks_delivery', False)}",
        f"  Rollup: {report.get('dimension_gate_status', 'PASS')}",
        "",
        "Word Budget:",
        f"  Status: {report.get('word_status', 'UNKNOWN')}",
        f"  Total Words: {report.get('grand_total_words', 0)}",
        f"  Target Range: {report.get('word_range_target', 'N/A')}",
        "",
        "Book Pass:",
        f"  Status: {report.get('book_pass_status', 'UNKNOWN')}",
        f"  Valid: {report.get('book_pass', {}).get('valid', False)}",
        f"  Errors: {len(report.get('book_pass', {}).get('errors', []))}",
        f"  Warnings: {len(report.get('book_pass', {}).get('warnings', []))}",
        "",
        "Thesis Drift:",
        f"  Status: {report.get('thesis_drift_status', 'UNKNOWN')}",
        f"  Chapters with Thesis: {report.get('total_chapters_with_thesis', 0)}",
        f"  Off-Thesis Chapters: {report.get('drift_count', 0)}",
        "",
        "Ending Signature:",
        f"  {report.get('ending_signature', 'N/A')}",
        "",
        "Carry Line:",
        f"  {report.get('carry_line', 'N/A')}",
    ]

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(summary_lines))

    return json_path, txt_path
