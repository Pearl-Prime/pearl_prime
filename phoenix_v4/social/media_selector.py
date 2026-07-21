"""Deterministic media-bank selector — Lane 06 of the Social Media Media-Bank pack.

Reads the three Lane 03/04/05 banks (video, audio, image), normalizes every row into the
unified shape in ``schemas/social/media_bank_asset.schema.json``, and deterministically resolves
one asset for a storyboard-beat / post-slot request. Speaks the same request envelope
``phoenix_v4/social/deterministic_social.py`` already uses (platform, surface, persona, topic,
...) so it can be called from the existing assembly seam without forking a parallel system.

Authority:
  - docs/specs/SOCIAL_MEDIA_BANK_R2_LAYOUT_2026-07-19.md
  - schemas/social/media_bank_asset.schema.json
  - docs/agent_prompt_packs/20260719_social_media_media_bank_deterministic_assembly/06_r2_layout_manifest_and_selector.md

Hard rules (do not relax without an operator decision):
  - No wall-clock, no ``random`` — every decision is a pure function of the request + the
    on-disk banks. Same request -> same asset_id, forever (until the banks themselves change).
  - A ``look_gate: PENDING`` or ``INTERIM`` asset is NEVER returned as a FINAL selection unless
    the caller explicitly opts in via ``pilot_mode=True`` / ``allow_interim=True`` — and even then
    the result is labeled INTERIM_PREVIEW_ONLY, never silently presented as final.
  - An empty compatible pool is a labeled gap (``is_gap=True`` + ``gap_reason``), never a silent
    cap or a fabricated asset_id.
"""
from __future__ import annotations

import csv
import hashlib
import sys
from dataclasses import dataclass, asdict
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

import yaml

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from phoenix_v4.planning.doctrine_rotation import spacing_window  # noqa: E402  (REUSE-FIRST — do not reinvent bounded-reuse spacing)

VIDEO_MANIFEST = ROOT / "artifacts/social_media_video_bank_2026-07-19/MANIFEST.tsv"
AUDIO_MANIFEST = ROOT / "artifacts/social_media_audio_bank_2026-07-19/MANIFEST.tsv"
IMAGE_MANIFEST = ROOT / "artifacts/social_media_image_bank_2026-07-19/MANIFEST.tsv"
CURATED_IMAGE_WINNERS = ROOT / "config/social/curated_image_winners.yaml"
PLATFORM_SPECS = ROOT / "config/social/platform_specs.yaml"
MEDIA_BANK_SIZING = ROOT / "config/social/media_bank_sizing_20260719.yaml"

# surface media_kind (config/social/platform_specs.yaml) -> media_type(s) that can fill it.
# video_or_storyboard surfaces need BOTH a video snippet and an audio bed (two separate
# selector calls sharing the same request envelope) — see deterministic_social.py wiring.
SURFACE_MEDIA_TYPE_COMPAT: dict[str, set[str]] = {
    "image": {"image"},
    "image_carousel": {"image"},
    "document_slide": {"image"},
    "video_or_storyboard": {"video", "audio"},
}

# platform_specs.yaml aspect_ratio string -> canonical aspect bucket used by the video/image
# bank builders (config/social/media_bank_sizing_20260719.yaml aspect_buckets). Nearest-match
# for surfaces whose exact ratio isn't one of the 5 bucket ratios (x_image, bluesky_image,
# google_business_square, youtube_community_image).
ASPECT_RATIO_TO_BUCKET: dict[str, str] = {
    "9:16": "VERTICAL_9_16",
    "1:1": "SQUARE_1_1",
    "4:5": "PORTRAIT_4_5",
    "2:3": "TALL_2_3",
    "16:9": "LANDSCAPE_WIDE",
    "1.91:1": "LANDSCAPE_WIDE",
    "2:1": "LANDSCAPE_WIDE",
}


class MediaSelectorError(RuntimeError):
    pass


def _to_bool(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "pass", "ok"}


def _to_int(value: Any) -> Optional[int]:
    try:
        if value in (None, "", "None"):
            return None
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _to_float(value: Any) -> Optional[float]:
    try:
        if value in (None, "", "None"):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _seconds_to_ms(value: Any) -> Optional[int]:
    seconds = _to_float(value)
    return None if seconds is None else int(round(seconds * 1000))


def stable_hash(*parts: Any, length: int = 16) -> str:
    raw = "::".join(str(p) for p in parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:length]


def _file_ext(path: Optional[str], default: str) -> str:
    if not path:
        return default
    suffix = Path(path).suffix.lstrip(".")
    return suffix or default


def canonical_r2_key(*, media_type: str, topic_or_market: str, family_or_layer: str, aspect_or_mood: str, asset_id: str, ext: str) -> str:
    """The one place the canonical key shape (R2 layout doc §1) is assembled.

    ``_normalize_audio_row``/``_normalize_image_row`` call this INSTEAD OF trusting the
    ``r2_key`` / ``r2_key_planned`` columns already in the Lane 04/05 source manifests, because
    those columns were populated before this lane's convention existed and use different, older
    prefixes (``social_media/audio_bank/...`` and ``brand/way_stream_sanctuary/...``
    respectively — see the R2 layout doc's "legacy key remediation" note). The video bank
    (Lane 03) already anticipated this convention correctly, so its manifest's own
    ``r2_key_planned`` is trusted verbatim.
    """
    return f"social-media-bank/v1/{media_type}/{topic_or_market}/{family_or_layer}/{aspect_or_mood}/{asset_id}.{ext}"


def _read_tsv(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


@lru_cache(maxsize=1)
def load_platform_specs() -> dict[str, Any]:
    return yaml.safe_load(PLATFORM_SPECS.read_text(encoding="utf-8")) or {}


@lru_cache(maxsize=1)
def load_media_bank_sizing() -> dict[str, Any]:
    return yaml.safe_load(MEDIA_BANK_SIZING.read_text(encoding="utf-8")) or {}


def mood_cluster_for_topic(topic: Optional[str]) -> Optional[str]:
    """Cross-media mood key for a topic, per audio_bank.mood_registers.clusters.

    Returns None for a topic outside the 15 native families / not yet clustered — callers
    treat that as "no mood-cluster constraint" rather than raising, since not every topic
    handed to the selector is guaranteed to be one of the 15 native families yet.
    """
    if not topic:
        return None
    clusters = (load_media_bank_sizing().get("audio_bank") or {}).get("mood_registers", {}).get("clusters", {})
    for register, topics in clusters.items():
        if topic in topics:
            return register
    return None


def _aspect_bucket_for_surface(surface_id: str) -> Optional[str]:
    surfaces = (load_platform_specs().get("surfaces") or {})
    spec = surfaces.get(surface_id)
    if not spec:
        return None
    return ASPECT_RATIO_TO_BUCKET.get(spec.get("aspect_ratio", ""))


def _media_kind_for_surface(surface_id: str) -> Optional[str]:
    surfaces = (load_platform_specs().get("surfaces") or {})
    spec = surfaces.get(surface_id)
    if not spec:
        return None
    return spec.get("media_kind")


# ─── Manifest normalization: source rows -> unified schema shape ───────────────────────────


def _normalize_video_row(row: dict[str, Any]) -> dict[str, Any]:
    production_ready = _to_bool(row.get("production_ready"))
    review_status = (row.get("review_status") or "").strip().lower()
    # Honor explicit operator look_gate column when present (Lane 07 apply script).
    # Fall back to production_ready / review_status only when the column is empty.
    explicit_look = (row.get("look_gate") or "").strip().upper()
    if explicit_look in {"PASS", "FAIL", "HOLD", "PENDING", "REJECTED"}:
        look_gate = "REJECTED" if explicit_look == "FAIL" else explicit_look
    elif production_ready:
        look_gate = "PASS"
    elif review_status == "rejected":
        look_gate = "REJECTED"
    else:
        look_gate = "PENDING"
    topic = row.get("topic_native_family") or None
    aspect_bucket = row.get("aspect_bucket") or None
    return {
        "asset_id": row.get("asset_id"),
        "media_type": "video",
        "topic": topic,
        "persona_scope": "shared",
        "family_or_layer": row.get("family"),
        "aspect_or_mood": aspect_bucket,
        "aspect_buckets": [aspect_bucket] if aspect_bucket else [],
        "mood_cluster": row.get("mood_register") or mood_cluster_for_topic(topic),
        "beat_role": row.get("beat_role") or None,
        "duration_ms": _seconds_to_ms(row.get("duration_s_actual")),
        "width": _to_int(row.get("width")),
        "height": _to_int(row.get("height")),
        "fps": _to_int(row.get("fps")),
        "seed": _to_int(row.get("seed")),
        "license_class": row.get("license_status") or "unknown",
        "license_verified": False,
        "provenance": (row.get("content_provenance") or "INTERIM").strip().upper(),
        "look_gate": look_gate,
        "production_ready": production_ready,
        "r2_key_planned": row.get("r2_key_planned") or None,
        "r2_uploaded": row.get("r2_uploaded") or "unknown",
        "r2_key": (row.get("r2_key_planned") if str(row.get("r2_uploaded") or "").lower() in {"true", "1", "yes"} else None),
        "local_path": row.get("local_path") or None,
        "sha256": row.get("sha256_16") or None,
        "bytes": _to_int(row.get("bytes")),
        "generated_by": row.get("generated_by"),
        "generated_at": row.get("generated_at"),
        "source_manifest": "video",
        "source_row": dict(row),
    }


def _normalize_audio_row(row: dict[str, Any]) -> dict[str, Any]:
    # Honor explicit operator look_gate when present; otherwise PENDING (never invent PASS
    # from render success alone). FAIL maps to REJECTED for the final filter.
    status = (row.get("status") or "").strip().lower()
    explicit_look = (row.get("look_gate") or "").strip().upper()
    if explicit_look in {"PASS", "FAIL", "HOLD", "PENDING", "REJECTED"}:
        look_gate = "REJECTED" if explicit_look == "FAIL" else explicit_look
    elif status in {"rejected", "blocked"}:
        look_gate = "REJECTED"
    else:
        look_gate = "PENDING"
    mood = row.get("mood") or None
    market = row.get("market") or "all"
    ext = _file_ext(row.get("local_path"), "mp3")
    r2_key_planned = (
        canonical_r2_key(
            media_type="audio",
            topic_or_market=market,
            family_or_layer=row.get("layer") or "unknown_layer",
            aspect_or_mood=mood or "unknown_mood",
            asset_id=row.get("audio_id") or "unknown_asset",
            ext=ext,
        )
        if row.get("audio_id")
        else None
    )
    return {
        "asset_id": row.get("audio_id"),
        "media_type": "audio",
        "topic": None,
        "persona_scope": "shared",
        "family_or_layer": row.get("layer"),
        "aspect_or_mood": mood,
        "aspect_buckets": [],
        "mood_cluster": mood if row.get("topic_adjacency") == "mood_keyed_shared" else None,
        "beat_role": None,
        "duration_ms": _to_int(row.get("duration_ms")),
        "lufs_integrated": _to_float(row.get("lufs_integrated")),
        "true_peak_dbtp": _to_float(row.get("true_peak_dbtp")),
        "loopable": _to_bool(row.get("loopable")),
        "seed": None,
        "license_class": row.get("license_class") or "unknown",
        "license_verified": row.get("license_class") == "owned_original",
        "provenance": (row.get("provenance") or "INTERIM").strip().upper(),
        "look_gate": look_gate,
        "production_ready": False,
        "r2_key_planned": r2_key_planned,
        "r2_uploaded": row.get("r2_uploaded") or "unknown",
        "r2_key": (
            r2_key_planned
            if str(row.get("r2_uploaded") or "").lower() in {"true", "1", "yes"}
            else None
        ),
        "legacy_r2_key": row.get("r2_key") or None,
        "local_path": row.get("local_path") or None,
        "sha256": row.get("sha256") or None,
        "bytes": _to_int(row.get("bytes")),
        "generated_by": row.get("source_engine"),
        "generated_at": None,
        "topic_adjacency": row.get("topic_adjacency"),
        "market": row.get("market"),
        "source_manifest": "audio",
        "source_row": dict(row),
    }


def _normalize_image_row(row: dict[str, Any]) -> dict[str, Any]:
    look_gate = (row.get("look_gate") or "PENDING").strip().upper()
    coverage = row.get("aspect_bucket_coverage") or []
    aspect_buckets = [c["bucket"] for c in coverage if isinstance(c, dict) and c.get("crop_feasible")]
    checks = row.get("automated_checks") or {}
    topic = row.get("topic") or None
    persona = row.get("persona") or "shared_all_personas"
    design_family = row.get("design_family")
    primary_bucket = aspect_buckets[0] if aspect_buckets else "unspecified_aspect"
    ext = _file_ext(row.get("local_path"), "jpg")
    r2_key_planned = (
        canonical_r2_key(
            media_type="image",
            topic_or_market=topic or "unknown_topic",
            family_or_layer=design_family or "unknown_family",
            aspect_or_mood=primary_bucket.lower(),
            asset_id=row.get("image_id") or "unknown_asset",
            ext=ext,
        )
        if row.get("image_id")
        else None
    )
    return {
        "asset_id": row.get("image_id"),
        "media_type": "image",
        "topic": topic,
        "persona_scope": "shared" if str(persona).startswith("shared") else f"keyed:{persona}",
        "family_or_layer": design_family,
        "aspect_or_mood": ",".join(aspect_buckets) if aspect_buckets else (row.get("aspect_native") or None),
        "aspect_buckets": aspect_buckets,
        "mood_cluster": mood_cluster_for_topic(topic),
        "beat_role": None,
        "text_safe_zones": row.get("text_safe_zones"),
        "width": checks.get("width"),
        "height": checks.get("height"),
        "seed": None,
        "license_class": row.get("license_class") or "unknown",
        "license_verified": bool(row.get("license_verified")),
        "provenance": (row.get("provenance") or "REAL").strip().upper(),
        "look_gate": look_gate,
        "production_ready": bool(row.get("production_ready")),
        "r2_key": None,
        "r2_key_planned": r2_key_planned,
        "r2_uploaded": "planned_not_uploaded" if r2_key_planned else "no_key_planned_yet",
        "legacy_r2_key_planned": row.get("r2_key_planned") or None,
        "local_path": row.get("local_path") or None,
        "sha256": None,
        "bytes": checks.get("bytes"),
        "generated_by": row.get("graduated_by"),
        "generated_at": row.get("graduated_at"),
        "source_manifest": "image",
        "source_row": row,
    }


@lru_cache(maxsize=1)
def load_unified_media_bank() -> tuple[dict[str, Any], ...]:
    """Load + normalize all three banks into the unified schema shape (§ media_bank_asset).

    Cached — the on-disk manifests are treated as immutable within one process lifetime.
    Call ``load_unified_media_bank.cache_clear()`` (e.g. in tests) after mutating a manifest.
    """
    rows: list[dict[str, Any]] = []
    rows.extend(_normalize_video_row(r) for r in _read_tsv(VIDEO_MANIFEST))
    rows.extend(_normalize_audio_row(r) for r in _read_tsv(AUDIO_MANIFEST))
    if CURATED_IMAGE_WINNERS.exists():
        winners = yaml.safe_load(CURATED_IMAGE_WINNERS.read_text(encoding="utf-8")) or {}
        rows.extend(_normalize_image_row(r) for r in (winners.get("rows") or []))
    else:
        rows.extend(_normalize_image_row(r) for r in _read_tsv(IMAGE_MANIFEST))
    return tuple(rows)


def family_media_types_index() -> dict[str, set[str]]:
    """family_or_layer value -> set of media_types it appears under, built dynamically.

    Not a 1:1 map — e.g. "object_metaphor" is both a video family (Lane 03) AND an image
    design_family (Lane 05), by design (same visual metaphor, different medium). Callers must
    disambiguate via the surface's allowed media_type(s) (see ``_resolve_media_type``), never
    by picking "whichever the loader happened to see first".
    """
    index: dict[str, set[str]] = {}
    for row in load_unified_media_bank():
        family = row.get("family_or_layer")
        if family:
            index.setdefault(family, set()).add(row["media_type"])
    return index


# ─── Request / result envelope ──────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class MediaSelectionRequest:
    surface: str
    persona: str
    topic: str
    platform: Optional[str] = None
    objective: Optional[str] = None
    awareness_stage: Optional[str] = None
    visual_type: Optional[str] = None
    beat_role: Optional[str] = None
    aspect_bucket: Optional[str] = None
    rotation_index: int = 0
    media_type: Optional[str] = None
    pilot_mode: bool = False
    allow_interim: bool = False

    def interim_allowed(self) -> bool:
        return bool(self.pilot_mode or self.allow_interim)

    def rotation_key(self) -> str:
        return f"{self.persona}|{self.topic}|{self.surface}"


@dataclass(frozen=True)
class MediaSelectionResult:
    request: dict[str, Any]
    asset_id: Optional[str]
    media_type: Optional[str]
    r2_key: Optional[str]
    r2_key_planned: Optional[str]
    local_path: Optional[str]
    provenance: Optional[str]
    look_gate: Optional[str]
    selection_label: str
    is_gap: bool
    gap_reason: Optional[str]
    pool_size: int
    no_repeat_window: int
    deterministic_rank: Optional[int]
    candidate_pool_asset_ids: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["candidate_pool_asset_ids"] = list(self.candidate_pool_asset_ids)
        return d


# ─── Compatibility filter ───────────────────────────────────────────────────────────────────


def _resolve_media_type(req: MediaSelectionRequest) -> Optional[str]:
    """Infer media_type from (explicit override > visual_type ∩ surface-allowed > surface alone).

    ``visual_type`` alone can be ambiguous (see ``family_media_types_index`` docstring — e.g.
    "object_metaphor" is both a video family and an image design_family). Intersecting with the
    surface's allowed media_type(s) resolves that in every case the current banks exercise; if
    it's still ambiguous (e.g. a video_or_storyboard surface with a family that is itself
    video+audio — not the case today) this returns None and leaves the hard media_type gate off,
    relying on the family_or_layer + surface-media-kind filters in ``_compatible`` to narrow it.
    """
    if req.media_type:
        return req.media_type

    surface_kind = _media_kind_for_surface(req.surface)
    surface_allowed = SURFACE_MEDIA_TYPE_COMPAT.get(surface_kind or "", set())

    candidates: Optional[set[str]] = None
    if req.visual_type:
        candidates = family_media_types_index().get(req.visual_type)

    if candidates and surface_allowed:
        narrowed = candidates & surface_allowed
        if len(narrowed) == 1:
            return next(iter(narrowed))
        return None  # still ambiguous after narrowing — let per-row filters do the work
    if candidates and len(candidates) == 1:
        return next(iter(candidates))
    if len(surface_allowed) == 1:
        return next(iter(surface_allowed))
    return None


def _compatible(row: dict[str, Any], req: MediaSelectionRequest, media_type: Optional[str]) -> tuple[bool, Optional[str]]:
    if media_type and row["media_type"] != media_type:
        return False, "media_type_mismatch"

    surface_kind = _media_kind_for_surface(req.surface)
    if surface_kind:
        allowed = SURFACE_MEDIA_TYPE_COMPAT.get(surface_kind)
        if allowed is not None and row["media_type"] not in allowed:
            return False, "surface_media_kind_mismatch"

    if row["media_type"] == "audio":
        adjacency = row.get("topic_adjacency") or ""
        if adjacency == "mood_keyed_shared":
            req_cluster = mood_cluster_for_topic(req.topic)
            if req_cluster and row.get("mood_cluster") and req_cluster != row.get("mood_cluster"):
                return False, "mood_cluster_mismatch"
        # market_agnostic / brand_level_market_agnostic rows are topic-agnostic by design.
    else:
        if row.get("topic") and req.topic and row["topic"] != req.topic:
            return False, "topic_mismatch"

    if req.visual_type and row.get("family_or_layer") != req.visual_type:
        return False, "family_or_layer_mismatch"

    if req.aspect_bucket and row["media_type"] in ("video", "image"):
        buckets = row.get("aspect_buckets") or []
        if buckets and req.aspect_bucket not in buckets:
            return False, "aspect_bucket_mismatch"

    if req.beat_role and row.get("beat_role") and row["beat_role"] != req.beat_role:
        return False, "beat_role_mismatch"

    if not row.get("license_class") or row["license_class"] == "unknown":
        return False, "no_license_class"

    return True, None


def _ordered_pool(pool: list[dict[str, Any]], rotation_key: str) -> list[dict[str, Any]]:
    """Deterministic per-rotation_key ordering (stable-hash sort key, never wall-clock/random).

    Different (persona,topic,surface) rotation keys get different — but still fully
    reproducible — orderings, so small pools don't all converge on the same "first" asset.
    """
    return sorted(pool, key=lambda r: (stable_hash(rotation_key, r["asset_id"]), r["asset_id"]))


# ─── Public entry point ─────────────────────────────────────────────────────────────────────


def select_media(req: MediaSelectionRequest) -> MediaSelectionResult:
    media_type = _resolve_media_type(req)
    request_dict = asdict(req)

    all_rows = load_unified_media_bank()
    compat_reasons: list[str] = []
    candidates: list[dict[str, Any]] = []
    for row in all_rows:
        ok, reason = _compatible(row, req, media_type)
        if ok:
            candidates.append(row)
        elif reason:
            compat_reasons.append(reason)

    strict_pool = [r for r in candidates if r["provenance"] == "REAL" and r["look_gate"] == "PASS"]

    if strict_pool:
        pool = strict_pool
        base_label = "FINAL_PASS"
    elif candidates and req.interim_allowed():
        pool = candidates
        base_label = "INTERIM_PREVIEW_ONLY"
    else:
        gap_reason = (
            "no_real_pass_rows_and_pilot_mode_false"
            if candidates
            else f"no_compatible_rows ({', '.join(sorted(set(compat_reasons))) or 'empty_bank'})"
        )
        return MediaSelectionResult(
            request=request_dict,
            asset_id=None,
            media_type=media_type,
            r2_key=None,
            r2_key_planned=None,
            local_path=None,
            provenance=None,
            look_gate=None,
            selection_label="GAP_NO_COMPATIBLE_ASSET",
            is_gap=True,
            gap_reason=gap_reason,
            pool_size=0,
            no_repeat_window=0,
            deterministic_rank=None,
            candidate_pool_asset_ids=(),
        )

    ordered = _ordered_pool(pool, req.rotation_key())
    pool_size = len(ordered)
    window = spacing_window(pool_size, req.rotation_index + 1)
    rank = req.rotation_index % pool_size
    chosen = ordered[rank]

    return MediaSelectionResult(
        request=request_dict,
        asset_id=chosen["asset_id"],
        media_type=chosen["media_type"],
        r2_key=chosen.get("r2_key"),
        r2_key_planned=chosen.get("r2_key_planned"),
        local_path=chosen.get("local_path"),
        provenance=chosen.get("provenance"),
        look_gate=chosen.get("look_gate"),
        selection_label=base_label,
        is_gap=False,
        gap_reason=None,
        pool_size=pool_size,
        no_repeat_window=window,
        deterministic_rank=rank,
        candidate_pool_asset_ids=tuple(r["asset_id"] for r in ordered),
    )


def select_media_asset(
    *,
    surface: str,
    persona: str,
    topic: str,
    platform: Optional[str] = None,
    objective: Optional[str] = None,
    awareness_stage: Optional[str] = None,
    visual_type: Optional[str] = None,
    beat_role: Optional[str] = None,
    aspect_bucket: Optional[str] = None,
    rotation_index: int = 0,
    media_type: Optional[str] = None,
    pilot_mode: bool = False,
    allow_interim: bool = False,
) -> dict[str, Any]:
    """Convenience dict-in/dict-out wrapper for callers that don't want the dataclass."""
    req = MediaSelectionRequest(
        surface=surface,
        persona=persona,
        topic=topic,
        platform=platform,
        objective=objective,
        awareness_stage=awareness_stage,
        visual_type=visual_type,
        beat_role=beat_role,
        aspect_bucket=aspect_bucket if aspect_bucket is not None else _aspect_bucket_for_surface(surface),
        rotation_index=rotation_index,
        media_type=media_type,
        pilot_mode=pilot_mode,
        allow_interim=allow_interim,
    )
    return select_media(req).to_dict()


def _cli(argv: Optional[list[str]] = None) -> int:
    import argparse
    import json

    ap = argparse.ArgumentParser(description="Deterministic media-bank selector smoke CLI.")
    ap.add_argument("--surface", required=True)
    ap.add_argument("--persona", required=True)
    ap.add_argument("--topic", required=True)
    ap.add_argument("--visual-type", default=None)
    ap.add_argument("--beat-role", default=None)
    ap.add_argument("--aspect-bucket", default=None)
    ap.add_argument("--media-type", default=None, choices=["video", "audio", "image"])
    ap.add_argument("--rotation-index", type=int, default=0)
    ap.add_argument("--pilot-mode", action="store_true")
    args = ap.parse_args(argv)

    result = select_media_asset(
        surface=args.surface,
        persona=args.persona,
        topic=args.topic,
        visual_type=args.visual_type,
        beat_role=args.beat_role,
        aspect_bucket=args.aspect_bucket,
        media_type=args.media_type,
        rotation_index=args.rotation_index,
        pilot_mode=args.pilot_mode,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
