"""Pass-B reading graph builder and validator for manga page flow."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from phoenix_v4.manga.chapter.spread_layout_solver import normalize_reading_direction


def _coerce_panel_bbox(bbox: Sequence[float]) -> tuple[float, float, float, float]:
    if len(bbox) != 4:
        raise ValueError(f"expected 4 values in bbox, got {bbox!r}")
    x0, y0, third, fourth = (float(v) for v in bbox)
    if third > x0 and fourth > y0:
        # Supports [x1, y1, x2, y2].
        if third > 1.0 or fourth > 1.0:
            return (x0, y0, third, fourth)
    # Default to [x, y, w, h].
    return (x0, y0, x0 + third, y0 + fourth)


def _center(bbox: Sequence[float]) -> tuple[float, float]:
    x1, y1, x2, y2 = (float(v) for v in bbox)
    return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)


def _height(bbox: Sequence[float]) -> float:
    return abs(float(bbox[3]) - float(bbox[1]))


def _width(bbox: Sequence[float]) -> float:
    return abs(float(bbox[2]) - float(bbox[0]))


def _ordered_ids_by_geometry(
    nodes: Sequence[Mapping[str, Any]],
    *,
    reading_direction: str,
) -> list[str]:
    rd = normalize_reading_direction(reading_direction)
    prepared = [
        {
            "id": str(node["id"]),
            "bbox": tuple(float(v) for v in node["bbox"]),
            "center": _center(node["bbox"]),
        }
        for node in nodes
    ]
    if rd == "vertical_scroll":
        prepared.sort(key=lambda row: (row["center"][1], row["center"][0]))
        return [row["id"] for row in prepared]

    rows: list[dict[str, Any]] = []
    row_tol = max((_height(row["bbox"]) for row in prepared), default=0.1) * 0.55
    for row in sorted(prepared, key=lambda item: (item["center"][1], item["center"][0])):
        cy = row["center"][1]
        if not rows or abs(cy - rows[-1]["anchor_y"]) > row_tol:
            rows.append({"anchor_y": cy, "items": [row]})
            continue
        rows[-1]["items"].append(row)
        rows[-1]["anchor_y"] = (rows[-1]["anchor_y"] + cy) / 2.0

    out: list[str] = []
    reverse = rd == "rtl"
    for row in rows:
        row["items"].sort(key=lambda item: item["center"][0], reverse=reverse)
        out.extend(str(item["id"]) for item in row["items"])
    return out


def _bubble_nodes_for_panel(
    panel_assignment: Mapping[str, Any],
    bubble_layout: Mapping[str, Any] | Sequence[Mapping[str, Any]] | None,
) -> list[dict[str, Any]]:
    if bubble_layout is None:
        return []
    rows = (
        list(bubble_layout.get("bubbles") or [])
        if isinstance(bubble_layout, Mapping)
        else list(bubble_layout)
    )
    if not rows:
        return []

    panel_bbox_norm = panel_assignment.get("bbox_norm")
    panel_bbox = panel_assignment.get("bbox")
    if panel_bbox_norm is not None:
        if not isinstance(panel_bbox_norm, Sequence):
            return []
        px1, py1, px2, py2 = _coerce_panel_bbox(panel_bbox_norm)
    else:
        if not isinstance(panel_bbox, Sequence) or len(panel_bbox) != 4:
            return []
        # Canonical graph nodes already store bbox as [x1, y1, x2, y2].
        px1, py1, px2, py2 = (float(v) for v in panel_bbox)
    # Panel bboxes may be normalized fractions for half-page / quarter-page cells.
    # Clamp only to a tiny epsilon so local bubble coordinates still scale into
    # the actual panel footprint instead of being stretched to a full-page unit.
    panel_w = max(1e-6, px2 - px1)
    panel_h = max(1e-6, py2 - py1)
    panel_size = bubble_layout.get("panel_size") if isinstance(bubble_layout, Mapping) else None
    if (
        isinstance(panel_size, Sequence)
        and len(panel_size) == 2
        and float(panel_size[0]) > 0
        and float(panel_size[1]) > 0
    ):
        local_w = float(panel_size[0])
        local_h = float(panel_size[1])
    else:
        local_w = panel_w
        local_h = panel_h

    nodes: list[dict[str, Any]] = []
    for idx, row in enumerate(rows):
        if str(row.get("type") or "") not in {"dialogue", "caption"}:
            continue
        bbox = row.get("bbox")
        if not isinstance(bbox, Sequence) or len(bbox) != 4:
            continue
        bx1, by1, bx2, by2 = (float(v) for v in bbox)
        nx1 = px1 + (bx1 / max(local_w, 1.0)) * panel_w
        ny1 = py1 + (by1 / max(local_h, 1.0)) * panel_h
        nx2 = px1 + (bx2 / max(local_w, 1.0)) * panel_w
        ny2 = py1 + (by2 / max(local_h, 1.0)) * panel_h
        nodes.append(
            {
                "id": f"bubble:{panel_assignment['panel_id']}:{idx}",
                "kind": str(row.get("type") or "dialogue"),
                "panel_id": str(panel_assignment["panel_id"]),
                "text": row.get("text"),
                "bbox": [round(nx1, 4), round(ny1, 4), round(nx2, 4), round(ny2, 4)],
                "declared_index": idx,
            }
        )
    return nodes


def analyze_page_reading_graph(
    *,
    page_number: int,
    panel_assignments: Sequence[Mapping[str, Any]],
    bubble_layouts_by_panel: Mapping[str, Mapping[str, Any] | Sequence[Mapping[str, Any]]] | None = None,
    reading_direction: str = "rtl",
) -> dict[str, Any]:
    """Build and validate a machine-checkable page reading graph."""
    rd = normalize_reading_direction(reading_direction)
    bubble_layouts_by_panel = bubble_layouts_by_panel or {}

    panel_nodes = [
        {
            "id": f"panel:{row['panel_id']}",
            "kind": "panel",
            "panel_id": str(row["panel_id"]),
            "bbox": list(_coerce_panel_bbox(row["bbox_norm"])),
            "declared_index": idx,
            "page_side": row.get("page_side"),
        }
        for idx, row in enumerate(panel_assignments)
    ]
    actual_panel_ids = [str(row["id"]) for row in panel_nodes]
    geometric_panel_ids = _ordered_ids_by_geometry(panel_nodes, reading_direction=rd)

    issues: list[dict[str, Any]] = []
    if actual_panel_ids != geometric_panel_ids:
        issues.append(
            {
                "rule_id": "panel_order_mismatch",
                "severity": "hard",
                "detail": "declared panel order does not match geometric reading flow",
                "expected": geometric_panel_ids,
                "actual": actual_panel_ids,
            }
        )

    bubble_nodes: list[dict[str, Any]] = []
    bubble_edges: list[dict[str, Any]] = []
    contains_edges: list[dict[str, Any]] = []
    reading_sequence: list[str] = []

    for panel in panel_nodes:
        pid = str(panel["panel_id"])
        local_bubbles = _bubble_nodes_for_panel(panel, bubble_layouts_by_panel.get(pid))
        bubble_nodes.extend(local_bubbles)
        actual = [str(row["id"]) for row in local_bubbles]
        expected = _ordered_ids_by_geometry(local_bubbles, reading_direction=rd)
        if actual and actual != expected:
            issues.append(
                {
                    "rule_id": "bubble_order_mismatch",
                    "severity": "hard",
                    "panel_id": pid,
                    "detail": "bubble sequence backtracks against page flow",
                    "expected": expected,
                    "actual": actual,
                }
            )
        if actual:
            contains_edges.extend(
                {
                    "from": str(panel["id"]),
                    "to": bubble_id,
                    "relation": "contains",
                }
                for bubble_id in actual
            )
            reading_sequence.extend(actual)
            bubble_edges.extend(
                {
                    "from": actual[idx],
                    "to": actual[idx + 1],
                    "relation": "bubble_sequence",
                }
                for idx in range(len(actual) - 1)
            )

    panel_edges = [
        {
            "from": actual_panel_ids[idx],
            "to": actual_panel_ids[idx + 1],
            "relation": "panel_sequence",
        }
        for idx in range(len(actual_panel_ids) - 1)
    ]
    graph_nodes = panel_nodes + bubble_nodes
    edges = panel_edges + contains_edges + bubble_edges

    metrics = {
        "panel_count": len(panel_nodes),
        "bubble_count": len(bubble_nodes),
        "panel_mismatch_count": sum(1 for issue in issues if issue["rule_id"] == "panel_order_mismatch"),
        "bubble_mismatch_count": sum(1 for issue in issues if issue["rule_id"] == "bubble_order_mismatch"),
    }
    return {
        "schema_version": "1.0.0",
        "artifact_type": "page_reading_graph",
        "page_number": int(page_number),
        "reading_direction": rd,
        "nodes": graph_nodes,
        "edges": edges,
        "reading_sequence": reading_sequence,
        "validation": {
            "ok": len(issues) == 0,
            "issues": issues,
            "metrics": metrics,
        },
    }
