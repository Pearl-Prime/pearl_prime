"""Speech-bubble tail geometry: auto mouth targeting and orientation.

Maps a speaker label + optional layout hints to a mouth pixel on the panel,
then derives tail direction for SVG/raster bubble compositing.

Resolution order (first hit wins):
    1. ``line["mouth_anchor"]`` — normalized (0–1) panel coordinates
    2. ``panel["character_head_bboxes"][speaker]`` — fractional head box
       (mouth = horizontal center, ~top 15% of box height from top edge)
    3. Optional MediaPipe face detection (lazy import; skipped if unavailable)
    4. ``position_hint`` zone heuristic — a *face-band* estimate (see
       ``_hint_to_mouth``): the tail reaches toward the upper portion of the
       speaker's zone where a manga figure's head sits, NOT the panel midline
       (the old midline fallback landed tails on torsos / knees).

No hard dependency on YOLOv8/MediaPipe — Pearl Star and CI stay green when
those wheels are absent.
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Mapping

BBoxPx = tuple[int, int, int, int]  # x1, y1, x2, y2


# Per-zone face-band fallback target (normalized x, y).
#
# Why these numbers: when a dialogue line's only positional signal is its
# bubble *zone*, the speaking figure is conventionally framed so their head/face
# sits toward the upper part of that zone (manga composes the bubble above and
# to the speaker's outer side, tail pointing DOWN-IN toward the face). The prior
# mapping put every target at y≈0.45–0.60 (panel midline = torso/waist), so the
# tail visibly pointed at a body or "the knees". These y-values sit in the
# head/upper-chest band (0.30–0.46) so the bare-zone fallback already lands near
# a face. x stays on the speaker's side. Authors who supply ``mouth_anchor`` or
# ``character_head_bboxes`` override this entirely (see ``resolve_mouth_pixel``).
_ZONE_FACE_TARGET: dict[str, tuple[float, float]] = {
    "top_left": (0.22, 0.34),
    "top_right": (0.78, 0.34),
    "top_center": (0.50, 0.36),
    "bottom_left": (0.22, 0.62),
    "bottom_right": (0.78, 0.62),
    "bottom_center": (0.50, 0.64),
    "center_left": (0.20, 0.44),
    "center_right": (0.80, 0.44),
}


def _hint_to_mouth(position_hint: str | None, pw: int, ph: int) -> tuple[int, int]:
    """Face-band mouth estimate from a bubble zone hint.

    Targets the head/upper-chest band of the speaker's zone (not the panel
    midline) so a tail drawn toward it lands on a face rather than a torso.
    Bottom-row zones intentionally sit lower (the figure is lower in frame) but
    still above the panel floor.
    """
    hint = position_hint or "top_right"
    fx, fy = _ZONE_FACE_TARGET.get(hint, (0.5, 0.4))
    return int(pw * fx), int(ph * fy)


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


# ── Anime/manga face detection (optional: cv2 + bundled cascade) ─────────────
# lbpcascade_animeface (nagadomi, MIT) detects stylised faces that the stock
# OpenCV real-face Haar cascades miss (and which they false-positive on, e.g. a
# framed portrait on the wall). Used to anchor a bubble tail at the speaker's
# ACTUAL face when the zone heuristic would otherwise point the tail at empty
# background. Fully optional: when cv2 or the cascade is absent, detection
# returns [] and callers fall back to the head-box / zone heuristic — so Pearl
# Star and CI stay green without the wheel.
_ANIME_CASCADE_PATH = Path(__file__).resolve().parents[1] / "assets" / "lbpcascade_animeface.xml"
_ANIME_CASCADE_CACHE: Any = None  # None = unprobed, False = unavailable, else classifier


def _get_anime_cascade() -> Any:
    global _ANIME_CASCADE_CACHE
    if _ANIME_CASCADE_CACHE is not None:
        return _ANIME_CASCADE_CACHE or None
    try:
        import cv2  # type: ignore

        if _ANIME_CASCADE_PATH.is_file():
            cc = cv2.CascadeClassifier(str(_ANIME_CASCADE_PATH))
            _ANIME_CASCADE_CACHE = cc if not cc.empty() else False
        else:
            _ANIME_CASCADE_CACHE = False
    except Exception:
        _ANIME_CASCADE_CACHE = False
    return _ANIME_CASCADE_CACHE or None


def detect_anime_face_boxes(panel_rgba: Any) -> list[BBoxPx]:
    """Detect stylised face boxes (pixel coords) on a panel. [] when unavailable."""
    cc = _get_anime_cascade()
    if cc is None or panel_rgba is None:
        return []
    try:
        import cv2  # type: ignore
        import numpy as np  # type: ignore

        img = panel_rgba.convert("RGB") if hasattr(panel_rgba, "convert") else None
        if img is None:
            return []
        w, h = img.size
        gray = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2GRAY)
        found = cc.detectMultiScale(
            gray,
            scaleFactor=1.05,
            minNeighbors=3,
            minSize=(max(12, int(w * 0.05)), max(12, int(h * 0.05))),
        )
        return [(int(x), int(y), int(x + bw), int(y + bh)) for (x, y, bw, bh) in found]
    except Exception:
        return []


def mouth_from_face_box(box: BBoxPx) -> tuple[int, int]:
    """Mouth point of a detected face box: horizontal centre, lower third."""
    x1, y1, x2, y2 = box
    return (x1 + x2) // 2, int(y1 + (y2 - y1) * 0.72)


def resolve_mouth_pixel(
    *,
    panel_w: int,
    panel_h: int,
    line: Mapping[str, Any],
    panel_lettering: Mapping[str, Any] | None = None,
    panel_rgba: Any | None = None,
    detected_faces: list[BBoxPx] | None = None,
) -> tuple[int, int]:
    """Pick the tail target mouth coordinate in panel pixel space.

    Resolution order: explicit ``mouth_anchor`` → nearest detected anime face →
    authored/derived head box → MediaPipe → zone face-band. ``detected_faces``
    may be passed in to avoid re-detecting once per dialogue line.
    """
    pw, ph = panel_w, panel_h
    panel_lettering = panel_lettering or {}

    # 1. Explicit author anchor wins outright.
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
    head_box = boxes.get(speaker) if isinstance(boxes, Mapping) else None

    # Speaker locator = head-box mouth if known, else the zone face-band. Used to
    # pick the nearest detected face and as the final fallback.
    locator = _hint_to_mouth(str(line.get("position_hint") or ""), pw, ph)
    if isinstance(head_box, Mapping):
        try:
            locator = mouth_from_head_bbox_fraction(head_box, pw, ph)
        except (KeyError, TypeError, ValueError):
            pass

    # 2. Anime-face detection → anchor at the speaker's ACTUAL face. Pick the
    # face nearest the locator ("nearest-character"); only trust it when it sits
    # near the speaker's expected zone, so a stray detection elsewhere (or a
    # background portrait) cannot hijack the tail.
    faces = detected_faces
    if faces is None and panel_rgba is not None:
        faces = detect_anime_face_boxes(panel_rgba)
    if faces:
        mouths = [mouth_from_face_box(b) for b in faces]
        best = min(mouths, key=lambda m: (m[0] - locator[0]) ** 2 + (m[1] - locator[1]) ** 2)
        if math.hypot(best[0] - locator[0], best[1] - locator[1]) <= 0.33 * math.hypot(pw, ph):
            return best

    # 3. Authored / derived head box.
    if isinstance(head_box, Mapping):
        try:
            return mouth_from_head_bbox_fraction(head_box, pw, ph)
        except (KeyError, TypeError, ValueError):
            pass

    # 4. MediaPipe real-face detection (no-op when the wheel is absent).
    if panel_rgba is not None:
        detected = mouth_from_mediapipe_face(panel_rgba)
        if detected is not None:
            return detected

    # 5. Zone face-band heuristic.
    return locator


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
