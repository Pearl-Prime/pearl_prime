"""Face-distance QA harness — V2 manga pipeline Phase A.3.

Per CHARACTER_INDIVIDUATION_PIPELINE_SPEC §2.5: post-render face-distance gate
to catch identity drift that the constraint solver couldn't see at design time.

Architecture:
    Primary backend = facenet-pytorch (commercial-clean VGGFace2 weights).
    MTCNN detects faces; InceptionResnetV1 (pretrained=vggface2) embeds them.
    Cosine distance between embeddings becomes the per-pair similarity metric.
    Fallback = DeepFace (Facenet512 model) for cross-validation when
    facenet-pytorch yields a borderline result. DeepFace is lazy-imported
    only when needed because it pulls TensorFlow which has heavy startup
    cost and noisy mutex traces during first-import.

Thresholds (PROPOSED per spec §2.5; empirical calibration deferred to Phase E):
    < 0.4  → fail (too similar — same person)
    0.4-0.55 → borderline (manual operator review)
    ≥ 0.55 → pass (distinct)

Public API:
    distance(face_a_path, face_b_path, *, backend="facenet")
        → float   (cosine distance ∈ [0, 2]; lower = more similar)
    classify(distance) → "fail" | "borderline" | "pass"
    find_collisions(new_face_path, catalog_dir, *, fail_threshold=0.4)
        → list[(catalog_path, distance)] sorted ascending — catches the
        designs that look "too close to existing cast" before commit.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

# Cap at the borderline threshold for "fail" classification
DEFAULT_FAIL_THRESHOLD = 0.4
DEFAULT_BORDERLINE_THRESHOLD = 0.55

# ── facenet-pytorch backend (primary; loads at first call) ───────────────────

_FACENET_MODELS: dict[str, object] = {}


def _facenet_models():
    """Lazy-load facenet-pytorch MTCNN + InceptionResnetV1. Cached after first call."""
    if "mtcnn" not in _FACENET_MODELS:
        from facenet_pytorch import MTCNN, InceptionResnetV1  # type: ignore
        _FACENET_MODELS["mtcnn"] = MTCNN(image_size=160, margin=0, post_process=True)
        _FACENET_MODELS["resnet"] = InceptionResnetV1(pretrained="vggface2").eval()
    return _FACENET_MODELS["mtcnn"], _FACENET_MODELS["resnet"]


def _facenet_embed(image_path: Path):
    """Return a 512-d embedding tensor for the face in image_path. Returns
    None if no face detected."""
    from PIL import Image  # type: ignore
    import torch  # type: ignore

    mtcnn, resnet = _facenet_models()
    img = Image.open(image_path).convert("RGB")
    face = mtcnn(img)
    if face is None:
        return None
    with torch.no_grad():
        emb = resnet(face.unsqueeze(0))
    return emb[0].cpu()


def _cosine_distance(a, b) -> float:
    import torch  # type: ignore
    return float(1.0 - torch.nn.functional.cosine_similarity(a.unsqueeze(0), b.unsqueeze(0))[0])


# ── DeepFace fallback (lazy-imported on demand only) ─────────────────────────

def _deepface_distance(face_a_path: Path, face_b_path: Path) -> float:
    """DeepFace's Facenet512 backend. Used for borderline cross-validation."""
    from deepface import DeepFace  # type: ignore
    res = DeepFace.verify(
        img1_path=str(face_a_path),
        img2_path=str(face_b_path),
        model_name="Facenet512",
        distance_metric="cosine",
        enforce_detection=False,
    )
    return float(res.get("distance", 0.0))


# ── Public API ───────────────────────────────────────────────────────────────

class FaceNotDetected(Exception):
    """Raised when MTCNN can't find a face in the input image."""


def distance(face_a_path: str | Path, face_b_path: str | Path, *, backend: str = "facenet") -> float:
    """Cosine distance between the two face embeddings. ∈ [0, 2]; smaller = more similar."""
    a = Path(face_a_path)
    b = Path(face_b_path)
    if backend == "facenet":
        emb_a = _facenet_embed(a)
        emb_b = _facenet_embed(b)
        if emb_a is None:
            raise FaceNotDetected(f"no face in {a}")
        if emb_b is None:
            raise FaceNotDetected(f"no face in {b}")
        return _cosine_distance(emb_a, emb_b)
    if backend == "deepface":
        return _deepface_distance(a, b)
    raise ValueError(f"unknown backend: {backend}")


def classify(
    d: float,
    *,
    fail_threshold: float = DEFAULT_FAIL_THRESHOLD,
    borderline_threshold: float = DEFAULT_BORDERLINE_THRESHOLD,
) -> str:
    """Spec §2.5 thresholds. Returns 'fail' | 'borderline' | 'pass'."""
    if d < fail_threshold:
        return "fail"
    if d < borderline_threshold:
        return "borderline"
    return "pass"


@dataclass
class Collision:
    catalog_path: Path
    distance: float
    classification: str

    def to_dict(self) -> dict:
        return {
            "catalog_path": str(self.catalog_path),
            "distance": round(self.distance, 4),
            "classification": self.classification,
        }


def find_collisions(
    new_face_path: str | Path,
    catalog_dir: str | Path,
    *,
    fail_threshold: float = DEFAULT_FAIL_THRESHOLD,
    borderline_threshold: float = DEFAULT_BORDERLINE_THRESHOLD,
    image_globs: tuple[str, ...] = ("*.png", "*.jpg", "*.jpeg"),
    backend: str = "facenet",
) -> list[Collision]:
    """Compare a candidate face against every face in catalog_dir; return the
    list of catalog faces whose distance < borderline_threshold (i.e. fail OR
    borderline; clearly-distinct faces are NOT in the result)."""
    catalog_dir = Path(catalog_dir)
    if not catalog_dir.is_dir():
        raise FileNotFoundError(f"catalog_dir not found: {catalog_dir}")
    candidates: list[Path] = []
    for g in image_globs:
        candidates.extend(catalog_dir.rglob(g))

    out: list[Collision] = []
    for cat_path in candidates:
        try:
            d = distance(new_face_path, cat_path, backend=backend)
        except FaceNotDetected:
            continue
        cls = classify(d, fail_threshold=fail_threshold, borderline_threshold=borderline_threshold)
        if cls in {"fail", "borderline"}:
            out.append(Collision(catalog_path=cat_path, distance=d, classification=cls))
    out.sort(key=lambda c: c.distance)
    return out


# ── CLI ──────────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description="Face-distance QA harness CLI.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_pair = sub.add_parser("pair", help="Distance between two face images.")
    p_pair.add_argument("face_a")
    p_pair.add_argument("face_b")
    p_pair.add_argument("--backend", default="facenet", choices=["facenet", "deepface"])

    p_scan = sub.add_parser("scan", help="Scan a catalog dir for collisions with one face.")
    p_scan.add_argument("face")
    p_scan.add_argument("catalog_dir")
    p_scan.add_argument("--backend", default="facenet", choices=["facenet", "deepface"])
    p_scan.add_argument("--fail-threshold", type=float, default=DEFAULT_FAIL_THRESHOLD)
    p_scan.add_argument("--borderline-threshold", type=float, default=DEFAULT_BORDERLINE_THRESHOLD)
    p_scan.add_argument("--json", action="store_true", help="Emit JSON instead of text")

    args = ap.parse_args()

    if args.cmd == "pair":
        try:
            d = distance(args.face_a, args.face_b, backend=args.backend)
        except FaceNotDetected as e:
            print(f"FaceNotDetected: {e}", file=sys.stderr)
            return 2
        cls = classify(d)
        print(f"distance={d:.4f}  classification={cls}")
        return 0 if cls != "fail" else 3

    if args.cmd == "scan":
        try:
            collisions = find_collisions(
                args.face, args.catalog_dir,
                fail_threshold=args.fail_threshold,
                borderline_threshold=args.borderline_threshold,
                backend=args.backend,
            )
        except FaceNotDetected as e:
            print(f"FaceNotDetected: {e}", file=sys.stderr)
            return 2
        if args.json:
            print(json.dumps([c.to_dict() for c in collisions], indent=2))
        else:
            if not collisions:
                print("no collisions (all catalog faces ≥ borderline_threshold)")
            for c in collisions:
                print(f"  {c.classification:10s} d={c.distance:.4f}  {c.catalog_path}")
        return 0 if not any(c.classification == "fail" for c in collisions) else 3

    ap.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
