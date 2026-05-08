"""Speech-bubble tail geometry: auto mouth targeting and orientation.

Maps a speaker label + optional layout hints to a mouth pixel on the panel,
then derives tail direction for SVG/raster bubble compositing.

Resolution order (first hit wins):
    1. ``line["mouth_anchor"]`` — normalized (0–1) panel coordinates
    2. ``panel["character_head_bboxes"][speaker]`` — fractional head box
       (mouth = horizontal center, ~top 15% of box height from top edge)
    3. Optional MediaPipe face detection (lazy import; skipped if unavailable)
    4. ``position_hint`` zone heuristic (same mapping as bubble_render v1)

No hard dependency on YOLOv8/MediaPipe — Pearl Star and CI stay green when
those wheels are absent.
"""
from __future__ import annotations

import math
from typing import Any, Mapping

BBoxPx = tuple[int, int, int, int]  # x1, y1, x2, y2


def _hint_to_mouth(position_hint: str | None, pw: int, ph: int) -> tuple[int, int]:
    """Fallback mouth estimate from zone hint (mirrors bubble_render v1)."""
    hint = position_hint or "top_right"
    mapping = {
        "top_left": (int(pw * 0.20), int(ph * 0.55)),
        "top_right": (int(pw * 0.80), int(ph * 0.55)),
        "top_center": (int(pw * 0.50), int(ph * 0.60)),
        "bottom_left": (int(pw * 0.20), int(ph * 0.45)),
        "bottom_right": (int(pw * 0.80), int(ph * 0.45)),
        "bottom_center": (int(pw * 0.50), int(ph * 0.40)),
        "center_left": (int(pw * 0.15), int(ph * 0.50)),
        "center_right": (int(pw * 0.85), int(ph * 0.50)),
    }
    return mapping.get(hint, (pw // 2, ph // 2))


def mouth_from_head_bbox_fraction(
    box: Mapping[str, float], pw: int, ph: int, *, mouth_depth: float = 0.15
) -> tuple[int, int]:
    """Convert fractional head bbox to mouth pixel.

    ``mouth_depth`` is the distance from the *top* of the head box toward
    the chin, as a fraction of box height (0.15 ≈ upper face / mouth band).
    """
    x1 = float(box["x1"]) * pw
    y1 = float(box["y1"]) * ph
    x2 = float(box["x2"]) * pw
    y2 = float(box["y2"]) * ph
    cx = int((x1 + x2) / 2)
    my = int(y1 + (y2 - y1) * mouth_depth)
    return cx, max(0, min(ph - 1, my))


def resolve_mouth_pixel(
    *,
    panel_w: int,
    panel_h: int,
    line: Mapping[str, Any],
    panel_lettering: Mapping[str, Any] | None = None,
    panel_rgba: Any | None = None,
) -> tuple[int, int]:
    """Pick the tail target mouth coordinate in panel pixel space."""
    pw, ph = panel_w, panel_h
    panel_lettering = panel_lettering or {}

    anchor = line.get("mouth_anchor")
    if isinstance(anchor, Mapping):
        try:
            ax = float(anchor.get("x", 0.5))
            ay = float(anchor.get("y", 0.5))
            return int(ax * pw), int(ay * ph)
        except (TypeError, ValueError):
            pass

    speaker = str(line.get("speaker") or "")
    boxes = panel_lettering.get("character_head_bboxes") or {}
    if speaker and speaker in boxes and isinstance(boxes[speaker], Mapping):
        try:
            return mouth_from_head_bbox_fraction(boxes[speaker], pw, ph)
        except (KeyError, TypeError, ValueError):
            pass

    if panel_rgba is not None:
        detected = mouth_from_mediapipe_face(panel_rgba)
        if detected is not None:
            return detected

    return _hint_to_mouth(str(line.get("position_hint") or ""), pw, ph)


def mouth_from_mediapipe_face(panel_rgba: Any) -> tuple[int, int] | None:
    """Best-effort face landmark → mouth point. Returns None if unavailable."""
    try:
        import mediapipe as mp  # type: ignore
        from PIL import Image
    except ImportError:
        return None

    try:
        if hasattr(panel_rgba, "convert"):
            img = panel_rgba.convert("RGB")
        elif isinstance(panel_rgba, Image.Image):
            img = panel_rgba.convert("RGB")
        else:
            return None
    except Exception:
        return None

    w, h = img.size
    try:
        import numpy as np  # type: ignore
    except ImportError:
        return None
    try:
        with mp.solutions.face_detection.FaceDetection(
            model_selection=0, min_detection_confidence=0.5
        ) as face_det:
            arr = np.asarray(img)
            res = face_det.process(arr)
        if not res.detections:
            return None
        det = res.detections[0]
        rel = det.location_data.relative_bounding_box
        x1 = max(0, int(rel.xmin * w))
        y1 = max(0, int(rel.ymin * h))
        x2 = min(w, int((rel.xmin + rel.width) * w))
        y2 = min(h, int((rel.ymin + rel.height) * h))
        # Mouth band: lower third of detection box (more stable than "top 30% of head")
        cx = (x1 + x2) // 2
        my = int(y1 + (y2 - y1) * 0.72)
        return cx, max(0, min(h - 1, my))
    except Exception:
        return None


def tail_vector(
    bubble_center: tuple[float, float], mouth: tuple[int, int]
) -> tuple[float, float]:
    """Unit vector from bubble center toward mouth."""
    mx, my = mouth
    bx, by = bubble_center
    dx, dy = mx - bx, my - by
    dist = math.hypot(dx, dy) or 1.0
    return dx / dist, dy / dist


def tail_anchor_on_ellipse(
    bubble_bbox: BBoxPx,
    direction: tuple[float, float],
) -> tuple[float, float]:
    """Intersection of ray from bubble center toward ``direction`` with the ellipse outline."""
    x1, y1, x2, y2 = bubble_bbox
    cx = (x1 + x2) / 2.0
    cy = (y1 + y2) / 2.0
    rx = max((x2 - x1) / 2.0, 1.0)
    ry = max((y2 - y1) / 2.0, 1.0)
    dx, dy = direction
    dist = math.hypot(dx, dy) or 1.0
    ux, uy = dx / dist, dy / dist
    # Ellipse centered at origin: (t*ux)^2/rx^2 + (t*uy)^2/ry^2 = 1
    denom = (ux / rx) ** 2 + (uy / ry) ** 2
    if denom <= 0:
        return cx + rx * ux, cy + ry * uy
    t = 1.0 / math.sqrt(denom)
    return cx + t * ux, cy + t * uy
