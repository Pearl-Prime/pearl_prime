"""Serial spine + continuity state loader for manga planning/runtime."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Optional

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

_SERIAL_SPINES_DIR = Path("config/manga/serial_spines")
_CONTINUITY_DIR = Path("config/manga/continuity")
_ADOPTED_REGISTRY = _SERIAL_SPINES_DIR / "_adopted_series.yaml"

_REQUIRED_SPINE_FIELDS = (
    "serial_engine",
    "long_arc_spine",
    "renewable_unit",
    "volume_arcs",
    "named_pressures",
    "set_piece_registry",
)
_REQUIRED_CONTINUITY_FIELDS = (
    "volume_arc_position",
    "settled_state",
    "rival_state",
    "motif_state",
    "active_pressures",
    "unresolved_hooks",
    "next_episode_mandate",
)


def default_repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _load_yaml(path: Path) -> dict[str, Any] | None:
    if yaml is None or not path.is_file():
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else None


def load_adopted_registry(repo_root: Path | None = None) -> list[dict[str, str]]:
    root = repo_root or default_repo_root()
    data = _load_yaml(root / _ADOPTED_REGISTRY) or {}
    rows = data.get("adopted_series") or []
    return [r for r in rows if isinstance(r, dict) and r.get("series_id")]


def is_series_adopted(series_id: str, repo_root: Path | None = None) -> bool:
    return any(r.get("series_id") == series_id for r in load_adopted_registry(repo_root))


def serial_spine_path(series_id: str, repo_root: Path | None = None) -> Path:
    root = repo_root or default_repo_root()
    return root / _SERIAL_SPINES_DIR / f"{series_id}.yaml"


def continuity_state_path(series_id: str, repo_root: Path | None = None) -> Path:
    root = repo_root or default_repo_root()
    return root / _CONTINUITY_DIR / f"{series_id}.yaml"


def load_serial_spine(
    series_id: str,
    *,
    repo_root: Path | None = None,
) -> dict[str, Any] | None:
    return _load_yaml(serial_spine_path(series_id, repo_root))


def load_continuity_state(
    series_id: str,
    *,
    repo_root: Path | None = None,
) -> dict[str, Any] | None:
    return _load_yaml(continuity_state_path(series_id, repo_root))


def validate_serial_spine(spine: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if spine.get("artifact_type") != "serial_spine":
        errors.append("artifact_type must be serial_spine")
    for field in _REQUIRED_SPINE_FIELDS:
        if not spine.get(field):
            errors.append(f"missing or empty serial_spine field: {field}")
    arcs = spine.get("volume_arcs") or []
    if not isinstance(arcs, list) or len(arcs) < 5:
        errors.append("volume_arcs must list 5 volumes")
    long_arc = str(spine.get("long_arc_spine") or "")
    if len(long_arc.split()) < 12:
        errors.append("long_arc_spine must be >= 12 words")
    return errors


def validate_continuity_state(state: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if state.get("artifact_type") != "series_continuity_state":
        errors.append("artifact_type must be series_continuity_state")
    for field in _REQUIRED_CONTINUITY_FIELDS:
        if field not in state or state.get(field) in (None, ""):
            errors.append(f"missing continuity field: {field}")
    mandate = state.get("next_episode_mandate") or {}
    if not isinstance(mandate, dict) or not mandate.get("must_rebreak"):
        errors.append("next_episode_mandate.must_rebreak required")
    return errors


def build_serial_context(
    series_id: str,
    *,
    chapter_number: int = 1,
    repo_root: Path | None = None,
) -> dict[str, Any] | None:
    """Merge spine + continuity for architect/writer consumption."""
    spine = load_serial_spine(series_id, repo_root=repo_root)
    if spine is None:
        return None
    continuity = load_continuity_state(series_id, repo_root=repo_root) or {}
    vol_pos = continuity.get("volume_arc_position") or {}
    current_vol = int(vol_pos.get("volume") or 1)
    volume_arc = next(
        (a for a in (spine.get("volume_arcs") or []) if int(a.get("volume", -1)) == current_vol),
        {},
    )
    ctx: dict[str, Any] = {
        "series_id": series_id,
        "chapter_number": chapter_number,
        "serial_engine": spine.get("serial_engine"),
        "long_arc_spine": spine.get("long_arc_spine"),
        "renewable_unit": spine.get("renewable_unit"),
        "escalation_axis": spine.get("escalation_axis"),
        "current_volume": current_vol,
        "current_volume_title": volume_arc.get("title") or vol_pos.get("volume_title"),
        "current_volume_logline": volume_arc.get("logline"),
        "named_pressures": spine.get("named_pressures") or [],
        "active_pressures": continuity.get("active_pressures") or [],
        "set_piece_registry": spine.get("set_piece_registry") or [],
        "set_pieces_fired": continuity.get("set_pieces_fired") or [],
        "rival_state": continuity.get("rival_state") or [],
        "motif_state": continuity.get("motif_state") or {},
        "settled_state": continuity.get("settled_state"),
        "unresolved_hooks": continuity.get("unresolved_hooks") or [],
    }
    mandate = continuity.get("next_episode_mandate") or {}
    target_ep = f"ep_{chapter_number:03d}"
    if mandate.get("episode_id") == target_ep or chapter_number > 1:
        ctx["episode_mandate"] = mandate
    return ctx


def build_episode_architect_input(
    series_id: str,
    *,
    chapter_number: int,
    arc_id: str = "arc_001",
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Deterministic follow-up episode planning input (e.g. ep_002 anti-one-shot proof)."""
    ctx = build_serial_context(series_id, chapter_number=chapter_number, repo_root=repo_root)
    if ctx is None:
        raise ValueError(f"No serial spine for series_id={series_id!r}")
    spine = load_serial_spine(series_id, repo_root=repo_root) or {}
    return {
        "schema_version": "1.0.0",
        "artifact_type": "serial_episode_architect_input",
        "series_id": series_id,
        "arc_id": arc_id,
        "chapter_number": chapter_number,
        "chapter_id": f"ep_{chapter_number:03d}",
        "genre": spine.get("genre"),
        "mode": spine.get("mode"),
        "serial_context": ctx,
        "carries_forward": {
            "settled_state": ctx.get("settled_state"),
            "rival_state": ctx.get("rival_state"),
            "motif_state": ctx.get("motif_state"),
            "unresolved_hooks": ctx.get("unresolved_hooks"),
        },
        "episode_mandate": ctx.get("episode_mandate") or {},
    }


def serial_prompt_block(
    serial_context: Mapping[str, Any] | None,
    *,
    chapter_number: int,
) -> str:
    """Writer/architect prompt appendix — explicit serial memory, not generic flavor."""
    if not serial_context:
        return ""
    lines = [
        "\n\nSerial spine (MANDATORY — do not reset settled state; re-break in new context):",
        f"- serial_engine: {serial_context.get('serial_engine')}",
        f"- long_arc_spine: {serial_context.get('long_arc_spine')}",
        f"- renewable_unit: {serial_context.get('renewable_unit')}",
        f"- volume: V{serial_context.get('current_volume')} "
        f"\"{serial_context.get('current_volume_title')}\"",
        f"- settled_state_at_prior_close: {serial_context.get('settled_state')}",
    ]
    hooks = serial_context.get("unresolved_hooks") or []
    if hooks:
        lines.append("- unresolved_hooks:")
        lines.extend(f"  - {h}" for h in hooks)
    rivals = serial_context.get("rival_state") or []
    if rivals:
        lines.append("- rival_state:")
        for r in rivals:
            if isinstance(r, dict):
                lines.append(
                    f"  - {r.get('rival_id')}: {r.get('state')} "
                    f"(last {r.get('last_seen_episode', '?')})"
                )
    motif = serial_context.get("motif_state") or {}
    if motif:
        lines.append(f"- motif_state: {motif}")
    active = serial_context.get("active_pressures") or []
    if active:
        lines.append(f"- active_pressures: {', '.join(str(p) for p in active)}")
    mandate = serial_context.get("episode_mandate") or {}
    if mandate and chapter_number > 1:
        lines.append(f"- EPISODE MANDATE ({mandate.get('episode_id', f'ep_{chapter_number:03d}')}):")
        if mandate.get("must_rebreak"):
            lines.append(f"  must_rebreak: {mandate['must_rebreak']}")
        for plant in mandate.get("must_plant") or []:
            lines.append(f"  must_plant: {plant}")
        for forbidden in mandate.get("forbidden") or []:
            lines.append(f"  forbidden: {forbidden}")
    lines.append(
        "Do NOT run wound→turn→renewal to a clean cure. Serial memory must bind this "
        "episode to the prior close."
    )
    return "\n".join(lines) + "\n"


def audit_adopted_series(repo_root: Path | None = None) -> list[dict[str, str]]:
    """Return audit rows for CI gate."""
    root = repo_root or default_repo_root()
    rows: list[dict[str, str]] = []
    for entry in load_adopted_registry(root):
        sid = str(entry.get("series_id") or "")
        row = {"series_id": sid, "status": "PASS", "failure_reasons": ""}
        spine = load_serial_spine(sid, repo_root=root)
        if spine is None:
            row["status"] = "FAIL"
            row["failure_reasons"] = "missing serial_spine yaml"
            rows.append(row)
            continue
        errs = validate_serial_spine(spine)
        cont = load_continuity_state(sid, repo_root=root)
        if cont is None:
            errs.append("missing continuity_state yaml")
        else:
            errs.extend(validate_continuity_state(cont))
        if errs:
            row["status"] = "FAIL"
            row["failure_reasons"] = "; ".join(errs)
        rows.append(row)
    return rows
