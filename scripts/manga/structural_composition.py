#!/usr/bin/env python3
"""Structural Composition MVP — runtime legality / support / contact layer.

Separate from PANEL_TYPE_SYSTEM_V1 (storytelling taxonomy). This module owns:
  - support surfaces, contact regions, support edges
  - shared ResolvedTransform model (plan + validate + overlay + render consume)
  - hard fails: missing graph, unknown category, support cycle, unsupported rotation
  - seated contact via point-in-polygon (+ px tolerance), NOT area ratio

Doctrine singleton remains:
  artifacts/qa/MANGA_CANON_SCENE_ASSEMBLY_CHECKLIST.md

Does NOT re-canonize the universal horizon-ratio law (SCALE-001 conflict).
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[2]
DEFAULT_VALIDATION = REPO / "config" / "manga" / "composition_validation.yaml"
DEFAULT_TEMPLATES = REPO / "config" / "manga" / "structural_templates.yaml"
DEFAULT_BRIDGE = REPO / "config" / "manga" / "panel_type_structural_bridge.yaml"

TRANSFORM_MODEL = "structural_mvp_v1"


class StructuralHardFail(Exception):
    """Hard fail for structural legality (fail-closed)."""

    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(f"{code}: {message}")


@dataclass(frozen=True)
class ResolvedTransform:
    """Single shared transform model — validation, overlay, and render MUST use this."""

    tx_pct: float
    ty_pct: float
    uniform_scale: float
    rotation_deg: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "tx_pct": self.tx_pct,
            "ty_pct": self.ty_pct,
            "uniform_scale": self.uniform_scale,
            "rotation_deg": self.rotation_deg,
            "transform_model": TRANSFORM_MODEL,
        }

    def to_canvas_xy(self, canvas_w: int, canvas_h: int) -> tuple[float, float]:
        return (self.tx_pct / 100.0 * canvas_w, self.ty_pct / 100.0 * canvas_h)


@dataclass
class StructuralIssue:
    code: str
    severity: str  # hard_fail | warn
    message: str
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_validation_profile(path: Path | None = None) -> dict[str, Any]:
    return load_yaml(path or DEFAULT_VALIDATION)


def load_templates(path: Path | None = None) -> dict[str, Any]:
    return load_yaml(path or DEFAULT_TEMPLATES)


def load_bridge(path: Path | None = None) -> dict[str, Any]:
    return load_yaml(path or DEFAULT_BRIDGE)


def bridge_for_panel_type(
    panel_type_id: str,
    *,
    bridge: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Additive bridge lookup: panel_type_id → structural template + relations + proof."""
    data = bridge if bridge is not None else load_bridge()
    mappings = data.get("mappings") or {}
    row = mappings.get(panel_type_id)
    if not row:
        raise StructuralHardFail(
            "BRIDGE_UNKNOWN_PANEL_TYPE",
            f"no structural bridge mapping for panel_type_id={panel_type_id!r}",
        )
    return dict(row)


def bridge_hint_from_archetype(
    archetype: str | None,
    *,
    bridge: dict[str, Any] | None = None,
) -> str | None:
    data = bridge if bridge is not None else load_bridge()
    hints = data.get("archetype_hints") or {}
    if not archetype:
        return None
    return hints.get(archetype)


def _threshold(profile: dict[str, Any], key: str) -> float:
    row = (profile.get("thresholds") or {}).get(key) or {}
    if "current_value" not in row:
        raise StructuralHardFail(
            "THRESHOLD_UNBOUND",
            f"threshold {key!r} missing current_value (THRESHOLD-001)",
        )
    return float(row["current_value"])


def point_in_polygon(
    point: tuple[float, float],
    polygon: list[tuple[float, float]],
    *,
    tolerance: float = 0.0,
) -> bool:
    """Ray-casting point-in-polygon with optional outward tolerance (px or same units).

    Contact validation MUST use this (or equivalent), NOT area-ratio heuristics.
    """
    if len(polygon) < 3:
        return False
    x, y = point
    if tolerance > 0:
        # Expand polygon radially from centroid by tolerance for near-edge contact.
        cx = sum(p[0] for p in polygon) / len(polygon)
        cy = sum(p[1] for p in polygon) / len(polygon)
        expanded: list[tuple[float, float]] = []
        for px, py in polygon:
            dx, dy = px - cx, py - cy
            dist = math.hypot(dx, dy) or 1.0
            expanded.append((px + dx / dist * tolerance, py + dy / dist * tolerance))
        polygon = expanded
    inside = False
    n = len(polygon)
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > y) != (yj > y)) and (
            x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-12) + xi
        ):
            inside = not inside
        j = i
    return inside


def pct_poly_to_px(
    poly_pct: list[list[float]],
    canvas_w: int,
    canvas_h: int,
) -> list[tuple[float, float]]:
    return [(p[0] / 100.0 * canvas_w, p[1] / 100.0 * canvas_h) for p in poly_pct]


def pct_point_to_px(
    pt_pct: list[float],
    canvas_w: int,
    canvas_h: int,
) -> tuple[float, float]:
    return (pt_pct[0] / 100.0 * canvas_w, pt_pct[1] / 100.0 * canvas_h)


def apply_transform_to_point_pct(
    local_pct: list[float],
    transform: ResolvedTransform,
) -> tuple[float, float]:
    """Apply shared transform in percent-space (origin at placement tx/ty)."""
    lx = local_pct[0] * transform.uniform_scale
    ly = local_pct[1] * transform.uniform_scale
    rad = math.radians(transform.rotation_deg)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    rx = lx * cos_a - ly * sin_a
    ry = lx * sin_a + ly * cos_a
    return (transform.tx_pct + rx, transform.ty_pct + ry)


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def compute_plan_hash(plan_body: dict[str, Any]) -> str:
    """Hash plan_body only — NEVER include plan_hash itself (not self-referential)."""
    payload = canonical_json(plan_body).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def verify_plan_hash(envelope: dict[str, Any]) -> None:
    body = envelope.get("plan_body")
    claimed = envelope.get("plan_hash")
    if not isinstance(body, dict) or not claimed:
        raise StructuralHardFail("PLAN_HASH_MISSING", "envelope missing plan_body or plan_hash")
    actual = compute_plan_hash(body)
    if actual != claimed:
        raise StructuralHardFail(
            "PLAN_HASH_MISMATCH",
            f"renderer refused plan: hash mismatch (claimed={claimed[:12]}… actual={actual[:12]}…)",
        )


def _index_nodes(nodes: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for n in nodes:
        nid = n.get("node_id")
        if not nid:
            raise StructuralHardFail("NODE_ID_MISSING", "node missing node_id")
        if nid in out:
            raise StructuralHardFail("NODE_ID_DUP", f"duplicate node_id={nid!r}")
        out[nid] = n
    return out


def _detect_support_cycle(edges: list[dict[str, Any]]) -> list[str] | None:
    """Support edges form a directed graph from → to; cycle is a hard fail."""
    adj: dict[str, list[str]] = {}
    for e in edges:
        adj.setdefault(str(e["from_node"]), []).append(str(e["to_node"]))
    visiting: set[str] = set()
    done: set[str] = set()
    stack: list[str] = []

    def dfs(u: str) -> list[str] | None:
        visiting.add(u)
        stack.append(u)
        for v in adj.get(u, []):
            if v in visiting:
                if v in stack:
                    i = stack.index(v)
                    return stack[i:] + [v]
                return [u, v, u]
            if v not in done:
                cyc = dfs(v)
                if cyc:
                    return cyc
        visiting.discard(u)
        stack.pop()
        done.add(u)
        return None

    for node in list(adj):
        if node not in done:
            cyc = dfs(node)
            if cyc:
                return cyc
    return None


def resolve_placement_transforms(
    placements: list[dict[str, Any]],
    *,
    profile: dict[str, Any],
) -> dict[str, ResolvedTransform]:
    max_rot = _threshold(profile, "max_rotation_deg")
    max_scale = _threshold(profile, "max_uniform_scale")
    min_scale = _threshold(profile, "min_uniform_scale")
    resolved: dict[str, ResolvedTransform] = {}
    for p in placements:
        nid = p["node_id"]
        t = p.get("transform") or {}
        if "sx" in t or "sy" in t:
            sx = float(t.get("sx", t.get("uniform_scale", 1.0)))
            sy = float(t.get("sy", t.get("uniform_scale", 1.0)))
            if abs(sx - sy) > 1e-9:
                raise StructuralHardFail(
                    "UNSUPPORTED_NONUNIFORM_SCALE",
                    f"node={nid}: non-uniform scale sx={sx} sy={sy} forbidden",
                )
        scale = float(t.get("uniform_scale", 1.0))
        rot = float(t.get("rotation_deg", 0.0))
        if abs(rot) > max_rot:
            raise StructuralHardFail(
                "UNSUPPORTED_ROTATION",
                f"node={nid}: rotation_deg={rot} exceeds max_rotation_deg={max_rot}",
            )
        if scale > max_scale or scale < min_scale:
            raise StructuralHardFail(
                "UNSUPPORTED_SCALE",
                f"node={nid}: uniform_scale={scale} outside [{min_scale}, {max_scale}]",
            )
        resolved[nid] = ResolvedTransform(
            tx_pct=float(t.get("tx_pct", 0.0)),
            ty_pct=float(t.get("ty_pct", 0.0)),
            uniform_scale=scale,
            rotation_deg=rot,
        )
    return resolved


def validate_support_graph(
    bundle: dict[str, Any],
    *,
    profile: dict[str, Any] | None = None,
    templates: dict[str, Any] | None = None,
) -> list[StructuralIssue]:
    """Validate structural bundle. Returns issues; hard_fail codes raise or listed."""
    profile = profile or load_validation_profile()
    templates = templates or load_templates()
    issues: list[StructuralIssue] = []

    tid = bundle.get("structural_template_id")
    tmpl_root = (templates.get("templates") or {})
    if tid not in tmpl_root:
        raise StructuralHardFail(
            "UNKNOWN_TEMPLATE",
            f"structural_template_id={tid!r} not in registry (scope: seated_table + standing_room)",
        )
    tmpl = tmpl_root[tid]

    nodes = bundle.get("nodes")
    edges = bundle.get("edges")
    if not nodes or not isinstance(nodes, list):
        raise StructuralHardFail("MISSING_GRAPH", "bundle.nodes missing or empty")
    if edges is None or not isinstance(edges, list):
        raise StructuralHardFail("MISSING_GRAPH", "bundle.edges missing (support graph required)")
    if len(edges) == 0:
        raise StructuralHardFail("MISSING_GRAPH", "bundle.edges empty — no support edges")

    known_cats = set(profile.get("known_node_categories") or [])
    known_rels = set(profile.get("known_relations") or [])
    allowed_rels = set(tmpl.get("allowed_relations") or known_rels)

    by_id = _index_nodes(nodes)
    for n in nodes:
        cat = n.get("category")
        if cat not in known_cats:
            raise StructuralHardFail(
                "UNKNOWN_CATEGORY",
                f"node={n.get('node_id')}: category={cat!r} not in known_node_categories",
            )

    for e in edges:
        rel = e.get("relation")
        if rel not in known_rels:
            raise StructuralHardFail(
                "UNKNOWN_RELATION",
                f"edge={e.get('edge_id')}: relation={rel!r} unknown",
            )
        if rel not in allowed_rels:
            raise StructuralHardFail(
                "RELATION_NOT_ALLOWED",
                f"edge={e.get('edge_id')}: relation={rel!r} not allowed for template={tid}",
            )
        if e.get("from_node") not in by_id or e.get("to_node") not in by_id:
            raise StructuralHardFail(
                "EDGE_DANGLING",
                f"edge={e.get('edge_id')}: from/to node missing from graph",
            )

    cyc = _detect_support_cycle(edges)
    if cyc:
        raise StructuralHardFail(
            "SUPPORT_CYCLE",
            f"support graph cycle detected: {' -> '.join(cyc)}",
        )

    # Required support proof
    required_proof = list(tmpl.get("required_support_proof") or [])
    present_rels = {e.get("relation") for e in edges}
    for need in required_proof:
        if need not in present_rels:
            raise StructuralHardFail(
                "REQUIRED_SUPPORT_PROOF_MISSING",
                f"template={tid} requires support proof relation={need!r}",
            )

    canvas = bundle.get("canvas") or {}
    W = int(canvas.get("width") or 0)
    H = int(canvas.get("height") or 0)
    if W <= 0 or H <= 0:
        raise StructuralHardFail("CANVAS_INVALID", "canvas.width/height must be positive ints")

    placements = bundle.get("placements") or []
    transforms = resolve_placement_transforms(placements, profile=profile)

    # Contact checks — point-in-polygon, not area ratio
    seated_tol = _threshold(profile, "seated_contact_px_tolerance")
    standing_tol = _threshold(profile, "standing_contact_px_tolerance")

    for e in edges:
        rel = e["relation"]
        if rel not in ("seated_on", "standing_on", "resting_on"):
            continue
        subject = by_id[e["from_node"]]
        support = by_id[e["to_node"]]
        if support.get("category") != "support_surface":
            raise StructuralHardFail(
                "SUPPORT_TARGET_INVALID",
                f"edge={e.get('edge_id')}: to_node must be support_surface for {rel}",
            )
        poly_pct = support.get("support_polygon_pct") or e.get("contact_region_pct")
        if not poly_pct:
            raise StructuralHardFail(
                "SUPPORT_POLYGON_MISSING",
                f"edge={e.get('edge_id')}: support polygon required for contact check",
            )
        contact_pct = subject.get("contact_point_pct")
        if not contact_pct:
            raise StructuralHardFail(
                "CONTACT_POINT_MISSING",
                f"node={subject.get('node_id')}: contact_point_pct required",
            )
        # Apply subject transform to contact point when placement exists
        if subject["node_id"] in transforms:
            # contact_point_pct stored in local subject space relative to placement origin
            world_pct = apply_transform_to_point_pct(contact_pct, transforms[subject["node_id"]])
        else:
            world_pct = (float(contact_pct[0]), float(contact_pct[1]))
        # Support polygon is in canvas percent (world)
        poly_px = pct_poly_to_px(poly_pct, W, H)
        pt_px = pct_point_to_px(list(world_pct), W, H)
        tol = seated_tol if rel == "seated_on" else standing_tol
        if not point_in_polygon(pt_px, poly_px, tolerance=tol):
            raise StructuralHardFail(
                "CONTACT_FAIL",
                f"edge={e.get('edge_id')} relation={rel}: contact point not in support polygon "
                f"(point-in-polygon; tolerance_px={tol})",
            )

    # Floating readable-room torso / prop guards (graph-level)
    chars = [n for n in nodes if n.get("category") == "character"]
    props = [n for n in nodes if n.get("category") == "prop"]
    supported_from = {e["from_node"] for e in edges if e["relation"] in ("seated_on", "standing_on", "resting_on", "held_by")}
    for c in chars:
        if c["node_id"] not in supported_from:
            raise StructuralHardFail(
                "FLOATING_READABLE_ROOM_TORSO",
                f"character node={c['node_id']} has no seated_on/standing_on/resting_on/held_by edge",
            )
    for p in props:
        if p["node_id"] not in supported_from and p.get("requires_support", True):
            raise StructuralHardFail(
                "FLOATING_READABLE_ROOM_PROP",
                f"prop node={p['node_id']} has no support/held edge",
            )

    return issues


def build_plan_envelope(
    bundle: dict[str, Any],
    *,
    panel_type_id: str | None = None,
    profile: dict[str, Any] | None = None,
    templates: dict[str, Any] | None = None,
    bridge: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build resolved plan envelope. Validates graph first; stamps plan_hash on envelope."""
    profile = profile or load_validation_profile()
    templates = templates or load_templates()
    validate_support_graph(bundle, profile=profile, templates=templates)

    tid = bundle["structural_template_id"]
    tmpl = (templates.get("templates") or {})[tid]
    ptid = panel_type_id or bundle.get("panel_type_id")
    if ptid:
        bridged = bridge_for_panel_type(ptid, bridge=bridge)
        if bridged["structural_template_id"] != tid:
            raise StructuralHardFail(
                "BRIDGE_TEMPLATE_MISMATCH",
                f"panel_type_id={ptid} maps to {bridged['structural_template_id']} but bundle has {tid}",
            )

    transforms = resolve_placement_transforms(bundle.get("placements") or [], profile=profile)
    resolved_placements = []
    for nid, tr in transforms.items():
        resolved_placements.append({"node_id": nid, "transform": tr.to_dict()})

    plan_body = {
        "panel_id": bundle.get("panel_id") or bundle.get("bundle_id"),
        "canvas": dict(bundle["canvas"]),
        "structural_template_id": tid,
        "panel_type_id": ptid,
        "required_support_proof": list(tmpl.get("required_support_proof") or []),
        "allowed_relations": list(tmpl.get("allowed_relations") or []),
        "support_graph": {
            "nodes": bundle["nodes"],
            "edges": bundle["edges"],
        },
        "resolved_placements": resolved_placements,
        "transform_model": TRANSFORM_MODEL,
    }
    plan_hash = compute_plan_hash(plan_body)
    envelope = {
        "schema_version": "1.0.0",
        "envelope_id": f"plan_{plan_body['panel_id']}",
        "transform_model": TRANSFORM_MODEL,
        "structural_template_id": tid,
        "panel_type_id": ptid,
        "plan_body": plan_body,
        "plan_hash": plan_hash,  # on envelope, not inside plan_body
        "validation": {"status": "pass", "failures": []},
    }
    return envelope


def render_from_verified_plan(
    envelope: dict[str, Any],
    *,
    require_hash: bool = True,
) -> dict[str, Any]:
    """Renderer consumes verified plan envelope — does NOT recompute placement.

    Verifies plan_hash before returning the resolved placements for paste.
    """
    if require_hash:
        verify_plan_hash(envelope)
    if envelope.get("transform_model") != TRANSFORM_MODEL:
        raise StructuralHardFail(
            "TRANSFORM_MODEL_MISMATCH",
            f"expected {TRANSFORM_MODEL}, got {envelope.get('transform_model')!r}",
        )
    body = envelope["plan_body"]
    return {
        "panel_id": body["panel_id"],
        "canvas": body["canvas"],
        "resolved_placements": body["resolved_placements"],
        "support_graph": body["support_graph"],
        "plan_hash": envelope["plan_hash"],
        "recomputed_placement": False,
    }


def emit_support_overlay(
    envelope: dict[str, Any],
    *,
    out_path: Path | None = None,
) -> dict[str, Any]:
    """Emit support overlay from the SAME resolved transform path used by contact validation.

    Returns overlay descriptor (+ optional PNG if Pillow available and out_path set).
    A second independent transform implementation here is treated as a defect — we only
    read envelope.plan_body.resolved_placements.
    """
    verify_plan_hash(envelope)
    body = envelope["plan_body"]
    canvas = body["canvas"]
    W, H = int(canvas["width"]), int(canvas["height"])
    nodes_by_id = {n["node_id"]: n for n in body["support_graph"]["nodes"]}
    placements = {
        p["node_id"]: ResolvedTransform(
            tx_pct=p["transform"]["tx_pct"],
            ty_pct=p["transform"]["ty_pct"],
            uniform_scale=p["transform"]["uniform_scale"],
            rotation_deg=p["transform"]["rotation_deg"],
        )
        for p in body["resolved_placements"]
    }

    regions = []
    for e in body["support_graph"]["edges"]:
        support = nodes_by_id[e["to_node"]]
        subject = nodes_by_id[e["from_node"]]
        poly = support.get("support_polygon_pct") or e.get("contact_region_pct") or []
        contact = subject.get("contact_point_pct") or [0, 0]
        tr = placements.get(subject["node_id"])
        if tr:
            world_contact = apply_transform_to_point_pct(contact, tr)
        else:
            world_contact = (float(contact[0]), float(contact[1]))
        regions.append({
            "edge_id": e.get("edge_id"),
            "relation": e.get("relation"),
            "support_polygon_pct": poly,
            "contact_point_pct": list(world_contact),
            "transform_model": TRANSFORM_MODEL,
            "transform_source": "envelope.plan_body.resolved_placements",
        })

    overlay_doc = {
        "schema_version": "1.0.0",
        "kind": "structural_support_overlay",
        "panel_id": body["panel_id"],
        "plan_hash": envelope["plan_hash"],
        "canvas": {"width": W, "height": H},
        "transform_model": TRANSFORM_MODEL,
        "regions": regions,
        "same_resolved_transform_path": True,
    }

    if out_path is not None:
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        # JSON sidecar always
        json_path = out_path.with_suffix(".json") if out_path.suffix.lower() in (".png", ".jpg") else out_path
        if json_path.suffix != ".json":
            json_path = Path(str(out_path) + ".json")
        json_path.write_text(json.dumps(overlay_doc, indent=2) + "\n", encoding="utf-8")
        overlay_doc["json_path"] = str(json_path)

        # Optional PNG visualization from same transforms
        try:
            from PIL import Image, ImageDraw

            img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            for reg in regions:
                poly_px = [
                    (p[0] / 100.0 * W, p[1] / 100.0 * H) for p in (reg["support_polygon_pct"] or [])
                ]
                if len(poly_px) >= 3:
                    draw.polygon(poly_px, outline=(0, 200, 80, 220), fill=(0, 200, 80, 40))
                cx = reg["contact_point_pct"][0] / 100.0 * W
                cy = reg["contact_point_pct"][1] / 100.0 * H
                r = 6
                draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(220, 40, 40, 230))
            png_path = out_path if out_path.suffix.lower() == ".png" else Path(str(json_path.with_suffix(".png")))
            img.save(png_path)
            overlay_doc["png_path"] = str(png_path)
        except ImportError:
            overlay_doc["png_path"] = None

    return overlay_doc


__all__ = [
    "StructuralHardFail",
    "ResolvedTransform",
    "TRANSFORM_MODEL",
    "point_in_polygon",
    "compute_plan_hash",
    "verify_plan_hash",
    "validate_support_graph",
    "build_plan_envelope",
    "render_from_verified_plan",
    "emit_support_overlay",
    "bridge_for_panel_type",
    "load_validation_profile",
    "load_templates",
    "load_bridge",
]
