"""Image generation QC gates — prompt validation and output validation.

Loads gate definitions from config/image_generation/image_gates.yaml.
Returns structured reports with gate_id, severity, status, detail.

Rewritten from .pyc interface spec — see specs/MANGA_QC_AND_EBOOK_PIPELINE_SPEC.md §A.2.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]


REPO_ROOT = Path(__file__).resolve().parents[2]
_GATES_PATH = REPO_ROOT / "config" / "image_generation" / "image_gates.yaml"
_COVER_ART_REGISTRY = REPO_ROOT / "config" / "authoring" / "author_cover_art_registry.yaml"
_AUTHOR_REGISTRY = REPO_ROOT / "config" / "author_registry.yaml"

# Defaults if config is missing
_DEFAULT_GATES: dict[str, dict[str, Any]] = {
    "IMAGE.PROMPT.STRUCTURE": {"severity": "BLOCKER", "description": "Positive prompt must contain subject and quality tokens"},
    "IMAGE.PROMPT.TOKEN_BUDGET": {"severity": "MAJOR", "max_positive_tokens": 120, "max_negative_tokens": 60},
    "IMAGE.OUTPUT.FILE_EXISTS": {"severity": "BLOCKER"},
    "IMAGE.OUTPUT.FORMAT": {"severity": "BLOCKER", "allowed_formats": ["PNG", "JPEG"]},
    "IMAGE.OUTPUT.MIN_FILE_SIZE": {"severity": "MAJOR", "min_bytes": 512},
    "IMAGE.OUTPUT.DIMENSIONS": {"severity": "MAJOR", "tolerance_px": 10},
    "IMAGE.AUTHOR_PIC.PROMPT_HAS_BIO": {"severity": "MAJOR", "min_bio_chars": 50},
}


def _known_author_ids() -> set[str]:
    """Union of author ids from cover-art registry and pen-name author registry."""
    known: set[str] = set()
    if yaml is None:
        return known
    for path in (_COVER_ART_REGISTRY, _AUTHOR_REGISTRY):
        if not path.is_file():
            continue
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except Exception:
            continue
        authors = data.get("authors") or {}
        known |= set(authors.keys())
    return known


def _load_gates() -> dict[str, dict[str, Any]]:
    """Load gate definitions from YAML config. Falls back to defaults."""
    if yaml is not None and _GATES_PATH.is_file():
        with _GATES_PATH.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        gates_list = data.get("gates", [])
        return {g["id"]: g for g in gates_list if "id" in g}
    return dict(_DEFAULT_GATES)


def _sha256_file(path: Path) -> str:
    """SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _png_dimensions(data: bytes) -> tuple[int, int]:
    """Extract width × height from PNG IHDR chunk."""
    if len(data) >= 24 and data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR":
        w = int.from_bytes(data[16:20], "big")
        h = int.from_bytes(data[20:24], "big")
        return w, h
    return 0, 0


def _jpeg_check(data: bytes) -> bool:
    """Check if data starts with JPEG magic bytes."""
    return len(data) >= 2 and data[:2] == b"\xff\xd8"


def validate_prompt(compiled: dict[str, Any]) -> dict[str, Any]:
    """Validate a compiled prompt dict against prompt gates.

    Returns {status, gates: [{gate_id, severity, status, detail}], blockers, majors}.
    """
    gates_config = _load_gates()
    results: list[dict[str, Any]] = []

    # Gate: STRUCTURE — has subject (non-empty positive) and quality tokens
    positive = compiled.get("positive", "")
    has_quality = any(tok in positive.lower() for tok in ["masterpiece", "best quality"])
    has_subject = bool(positive) and len(positive.strip()) > len("masterpiece, best quality") + 5

    if has_subject and has_quality:
        results.append({
            "gate_id": "IMAGE.PROMPT.STRUCTURE",
            "severity": "BLOCKER",
            "status": "passed",
            "detail": "Prompt has subject and quality tokens",
        })
    else:
        detail_parts = []
        if not has_subject:
            detail_parts.append("missing subject content")
        if not has_quality:
            detail_parts.append("missing quality tokens")
        results.append({
            "gate_id": "IMAGE.PROMPT.STRUCTURE",
            "severity": "BLOCKER",
            "status": "failed",
            "detail": "; ".join(detail_parts),
        })

    # Gate: TOKEN_BUDGET
    pos_tokens = compiled.get("positive_token_count", 0)
    neg_tokens = compiled.get("negative_token_count", 0)
    gate_cfg = gates_config.get("IMAGE.PROMPT.TOKEN_BUDGET", _DEFAULT_GATES["IMAGE.PROMPT.TOKEN_BUDGET"])
    max_pos = gate_cfg.get("max_positive_tokens", 120)
    max_neg = gate_cfg.get("max_negative_tokens", 60)

    if pos_tokens <= max_pos and neg_tokens <= max_neg:
        results.append({
            "gate_id": "IMAGE.PROMPT.TOKEN_BUDGET",
            "severity": "MAJOR",
            "status": "passed",
            "detail": f"Tokens: positive={pos_tokens}/{max_pos}, negative={neg_tokens}/{max_neg}",
        })
    else:
        results.append({
            "gate_id": "IMAGE.PROMPT.TOKEN_BUDGET",
            "severity": "MAJOR",
            "status": "failed",
            "detail": f"Over budget: positive={pos_tokens}/{max_pos}, negative={neg_tokens}/{max_neg}",
        })

    # Check provenance hash exists
    provenance = compiled.get("provenance", {})
    if not provenance.get("prompt_hash"):
        results.append({
            "gate_id": "IMAGE.PROMPT.PROVENANCE",
            "severity": "MAJOR",
            "status": "failed",
            "detail": "Missing provenance hash",
        })

    # Check negative is not empty
    negative = compiled.get("negative", "")
    if not negative.strip():
        results.append({
            "gate_id": "IMAGE.PROMPT.NEGATIVE",
            "severity": "MAJOR",
            "status": "failed",
            "detail": "Empty negative prompt",
        })

    # Aggregate
    blockers = [r for r in results if r["severity"] == "BLOCKER" and r["status"] == "failed"]
    majors = [r for r in results if r["severity"] == "MAJOR" and r["status"] == "failed"]
    status = "failed" if blockers else ("passed_with_warnings" if majors else "passed")

    return {
        "status": status,
        "gates": results,
        "blockers": [b["gate_id"] for b in blockers],
        "majors": [m["gate_id"] for m in majors],
    }


def validate_output(
    image_path: Path,
    expected_width: int = 0,
    expected_height: int = 0,
    min_bytes: int = 512,
) -> dict[str, Any]:
    """Validate a generated image file against output gates.

    Returns {status, gates, blockers, majors, content_sha256?, file_size?}.
    """
    results: list[dict[str, Any]] = []

    # Gate: FILE_EXISTS
    if not image_path.is_file():
        results.append({
            "gate_id": "IMAGE.OUTPUT.FILE_EXISTS",
            "severity": "BLOCKER",
            "status": "failed",
            "detail": f"File not found: {image_path}",
        })
        return _build_output_report(results, image_path, b"")

    data = image_path.read_bytes()
    results.append({
        "gate_id": "IMAGE.OUTPUT.FILE_EXISTS",
        "severity": "BLOCKER",
        "status": "passed",
        "detail": f"File exists: {len(data)} bytes",
    })

    # Gate: FORMAT
    is_png = data[:8] == b"\x89PNG\r\n\x1a\n" if len(data) >= 8 else False
    is_jpeg = _jpeg_check(data)
    if is_png or is_jpeg:
        fmt = "PNG" if is_png else "JPEG"
        results.append({
            "gate_id": "IMAGE.OUTPUT.FORMAT",
            "severity": "BLOCKER",
            "status": "passed",
            "detail": f"Valid {fmt} format",
        })
    else:
        results.append({
            "gate_id": "IMAGE.OUTPUT.FORMAT",
            "severity": "BLOCKER",
            "status": "failed",
            "detail": "File is not valid PNG or JPEG",
        })

    # Gate: MIN_FILE_SIZE
    if len(data) >= min_bytes:
        results.append({
            "gate_id": "IMAGE.OUTPUT.MIN_FILE_SIZE",
            "severity": "MAJOR",
            "status": "passed",
            "detail": f"File size {len(data)} >= {min_bytes}",
        })
    else:
        results.append({
            "gate_id": "IMAGE.OUTPUT.MIN_FILE_SIZE",
            "severity": "MAJOR",
            "status": "failed",
            "detail": f"File size {len(data)} < minimum {min_bytes}",
        })

    # Gate: DIMENSIONS
    if expected_width > 0 and expected_height > 0 and is_png:
        w, h = _png_dimensions(data)
        tolerance = 10
        w_ok = abs(w - expected_width) <= tolerance
        h_ok = abs(h - expected_height) <= tolerance
        if w_ok and h_ok:
            results.append({
                "gate_id": "IMAGE.OUTPUT.DIMENSIONS",
                "severity": "MAJOR",
                "status": "passed",
                "detail": f"Dimensions {w}x{h} within tolerance of {expected_width}x{expected_height}",
            })
        else:
            results.append({
                "gate_id": "IMAGE.OUTPUT.DIMENSIONS",
                "severity": "MAJOR",
                "status": "failed",
                "detail": f"Dimensions {w}x{h} outside tolerance of {expected_width}x{expected_height}",
            })

    return _build_output_report(results, image_path, data)


def _build_output_report(
    results: list[dict[str, Any]],
    image_path: Path,
    data: bytes,
) -> dict[str, Any]:
    """Build structured QC report with content_sha256, file_size."""
    blockers = [r for r in results if r["severity"] == "BLOCKER" and r["status"] == "failed"]
    majors = [r for r in results if r["severity"] == "MAJOR" and r["status"] == "failed"]
    status = "failed" if blockers else ("passed_with_warnings" if majors else "passed")

    report: dict[str, Any] = {
        "status": status,
        "gates": results,
        "blockers": [b["gate_id"] for b in blockers],
        "majors": [m["gate_id"] for m in majors],
    }

    if data:
        report["content_sha256"] = hashlib.sha256(data).hexdigest()
        report["file_size"] = len(data)

    return report


def validate_author_pic_prompt(
    compiled: dict[str, Any],
    author_id: str,
) -> dict[str, Any]:
    """All prompt gates + author-specific: bio content length, author tag in continuity.

    Returns same shape as validate_prompt, plus author-specific gates.
    """
    # Run standard prompt validation first
    base_report = validate_prompt(compiled)
    results = list(base_report["gates"])

    # Gate: AUTHOR_PIC.PROMPT_HAS_BIO
    bio_length = compiled.get("bio_length", 0)
    gates_config = _load_gates()
    gate_cfg = gates_config.get("IMAGE.AUTHOR_PIC.PROMPT_HAS_BIO", _DEFAULT_GATES["IMAGE.AUTHOR_PIC.PROMPT_HAS_BIO"])
    min_bio_chars = gate_cfg.get("min_bio_chars", 50)

    if bio_length >= min_bio_chars:
        results.append({
            "gate_id": "IMAGE.AUTHOR_PIC.PROMPT_HAS_BIO",
            "severity": "MAJOR",
            "status": "passed",
            "detail": f"Bio length {bio_length} >= {min_bio_chars}",
        })
    else:
        results.append({
            "gate_id": "IMAGE.AUTHOR_PIC.PROMPT_HAS_BIO",
            "severity": "MAJOR",
            "status": "failed",
            "detail": f"Bio length {bio_length} < minimum {min_bio_chars}",
        })

    # Check author tag in continuity
    continuity = compiled.get("continuity_tags", [])
    author_tag = f"author:{author_id}"
    if author_tag in continuity:
        results.append({
            "gate_id": "IMAGE.AUTHOR_PIC.AUTHOR_TAG",
            "severity": "MAJOR",
            "status": "passed",
            "detail": f"Author tag '{author_tag}' in continuity tags",
        })
    else:
        results.append({
            "gate_id": "IMAGE.AUTHOR_PIC.AUTHOR_TAG",
            "severity": "MAJOR",
            "status": "failed",
            "detail": f"Author tag '{author_tag}' missing from continuity tags",
        })

    # Gate: registry — author must appear in at least one registry when registries define authors
    reg_known = _known_author_ids()
    if reg_known:
        if author_id in reg_known:
            results.append({
                "gate_id": "IMAGE.AUTHOR_PIC.REGISTRY_MATCH",
                "severity": "MAJOR",
                "status": "passed",
                "detail": f"Author '{author_id}' found in author registries",
            })
        else:
            results.append({
                "gate_id": "IMAGE.AUTHOR_PIC.REGISTRY_MATCH",
                "severity": "MAJOR",
                "status": "failed",
                "detail": f"Author '{author_id}' not found in author_cover_art_registry or author_registry",
            })

    # Re-aggregate
    blockers = [r for r in results if r["severity"] == "BLOCKER" and r["status"] == "failed"]
    majors = [r for r in results if r["severity"] == "MAJOR" and r["status"] == "failed"]
    status = "failed" if blockers else ("passed_with_warnings" if majors else "passed")

    return {
        "status": status,
        "gates": results,
        "blockers": [b["gate_id"] for b in blockers],
        "majors": [m["gate_id"] for m in majors],
    }
