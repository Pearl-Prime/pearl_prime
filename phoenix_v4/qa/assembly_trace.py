"""Human-readable assembly trace for composite spine renders."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Optional

from phoenix_v4.planning.enrichment_select import EnrichedBook

CONTRACT_V1_ID = "cli_demo_trace_run_composite_contract_v1"


def write_assembly_trace(
    *,
    enriched: EnrichedBook,
    render_dir: Path,
    contract_id: str = CONTRACT_V1_ID,
    topic_id: str = "",
    persona_id: str = "",
    runtime_format: str = "",
) -> Path:
    """Write assembly_trace.md summarizing accent landings and contract frame."""
    audit = enriched.enrichment_audit or {}
    strategy = audit.get("enrichment_strategy_report") or {}
    alignment = audit.get("bestseller_alignment_report") or {}
    spine = enriched.spine_context or {}
    assignments = list(spine.get("accent_assignments") or strategy.get("assignments") or [])

    book_idea = strategy.get("book_idea") or spine.get("book_idea") or ""
    book_motif = strategy.get("book_motif") or spine.get("book_motif") or ""
    provenance = strategy.get("supply_provenance_by_class") or {}
    supported_underfill = alignment.get("supported_underfilled_budget_by_class") or {}

    lines = [
        "# Assembly Trace",
        "",
        f"**Contract:** `{contract_id}`",
        f"**Topic / persona:** `{topic_id or enriched.topic}` × `{persona_id or enriched.persona_id}`",
        f"**Runtime format:** `{runtime_format}`",
        "",
        "## Contract frame",
        "",
        f"- **book_idea:** {book_idea}",
        f"- **book_motif:** {book_motif}",
        f"- **enrichment_strategy_profile:** {strategy.get('enrichment_strategy_profile') or spine.get('story_mix_profile') or ''}",
        f"- **brand_accent_profile:** {strategy.get('brand_accent_profile') or ''}",
        f"- **alignment_status:** {alignment.get('status') or 'unknown'}",
        "",
        "## Supported underfill",
        "",
        "```json",
        json.dumps(supported_underfill, indent=2, ensure_ascii=False),
        "```",
        "",
        "## Supply provenance",
        "",
        "```json",
        json.dumps(provenance, indent=2, ensure_ascii=False),
        "```",
        "",
        "## Accent assignments",
        "",
    ]

    if not assignments:
        lines.append("_No accent assignments recorded._")
    else:
        lines.append("| Chapter | Class | Accent ID | Position | Supply |")
        lines.append("|---:|---|---|---|---|")
        for row in sorted(assignments, key=lambda r: (int(r.get("chapter") or 0), str(r.get("class") or ""))):
            lines.append(
                "| {chapter} | {cls} | `{accent_id}` | {position} | {supply} |".format(
                    chapter=int(row.get("chapter") or 0),
                    cls=str(row.get("class") or ""),
                    accent_id=str(row.get("accent_id") or ""),
                    position=str(row.get("position") or ""),
                    supply=str(row.get("supply_source") or row.get("keys", {}).get("supply_provenance") or ""),
                )
            )

    accent_classes = ("REFLECTION_QUESTION", "TROUBLESHOOTING")
    lines.extend(["", "## Authored enrichment landings", ""])
    for cls in accent_classes:
        rows = [r for r in assignments if str(r.get("class") or "") == cls]
        lines.append(f"### {cls} ({len(rows)} landed)")
        if not rows:
            lines.append("_None landed._")
        else:
            for row in rows:
                lines.append(
                    f"- ch{row.get('chapter')} `{row.get('accent_id')}` "
                    f"via `{row.get('supply_source') or provenance.get(cls, 'unknown')}`"
                )
        lines.append("")

    out_path = render_dir / "assembly_trace.md"
    out_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    return out_path
