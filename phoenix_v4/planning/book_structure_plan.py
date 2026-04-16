"""Book-level deterministic planning contracts."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

from phoenix_v4.planning.chapter_plan import ChapterPlan, PlanValidationError, validate_chapter_plan


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PLANS_ROOT = REPO_ROOT / "config" / "plans"
EI_V2_CONFIG = REPO_ROOT / "config" / "quality" / "ei_v2_config.yaml"

RUNTIME_ALIASES = {
    "standard_book": "deep_book_6h",
}

RUNTIME_TEMPLATES = {
    "short_book_30": {"tier": "short", "chapter_count": 6, "exercise_cap": 1},
    "standard_book": {"tier": "standard", "chapter_count": 12, "exercise_cap": 2},
    "deep_book_6h": {"tier": "standard", "chapter_count": 12, "exercise_cap": 2},
}


@dataclass(frozen=True)
class BookStructurePlan:
    plan_id: str
    persona_id: str
    topic_id: str
    teacher_id: str
    runtime_format_id: str
    engine_type: str
    chapter_count: int
    tier: str
    chapters: list[ChapterPlan]
    dominant_band_sequence: list[int]
    intensity_sequence: list[int]
    emotional_curve: list[int]
    cost_chapter_index: int
    reflection_strategy_rotation: list[str]
    motif: dict[str, Any]
    resolution_type: str
    word_budget_total: dict[str, Any]
    bestseller_structure_histogram: dict[str, int]
    teacher_anchor: dict[str, Any]
    arc_checkpoint_percent: dict[str, Any]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BookStructurePlan":
        root = data.get("book_structure_plan") if "book_structure_plan" in data else data
        if not isinstance(root, dict):
            raise PlanValidationError("book_structure_plan must be a mapping")
        values = dict(root)
        raw_chapters = values.get("chapters") or []
        values["chapters"] = [ChapterPlan.from_dict(ch) for ch in raw_chapters]
        values.setdefault("emotional_curve", values.get("intensity_sequence", []))
        values.setdefault("reflection_strategy_rotation", [])
        values.setdefault("motif", {})
        values.setdefault("word_budget_total", {})
        values.setdefault("bestseller_structure_histogram", {})
        values.setdefault("teacher_anchor", {})
        values.setdefault("arc_checkpoint_percent", {})
        missing = [name for name in cls.__dataclass_fields__ if name not in values]
        if missing:
            raise PlanValidationError(f"BookStructurePlan missing required fields: {', '.join(sorted(missing))}")
        return cls(**{name: values.get(name) for name in cls.__dataclass_fields__})


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PlanValidationError(message)


def get_runtime_template(runtime_id: str) -> dict[str, Any]:
    key = (runtime_id or "").strip()
    return dict(RUNTIME_TEMPLATES.get(key) or RUNTIME_TEMPLATES.get(RUNTIME_ALIASES.get(key, ""), {}))


def ensure_ei_v2_book_structure_enforcement(repo_root: Path = REPO_ROOT) -> None:
    """Persist the spec-required EI V2 book-structure enforcement switch."""
    if yaml is None:
        return
    path = repo_root / "config" / "quality" / "ei_v2_config.yaml"
    if not path.exists():
        return
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    block = data.setdefault("book_structure", {})
    if block.get("enforce_bestseller_beat_order") is True:
        return
    block["enforce_bestseller_beat_order"] = True
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")


def validate_book_arc(plan: BookStructurePlan) -> BookStructurePlan:
    _require(plan.chapter_count == len(plan.chapters), "chapter_count must match len(chapters)")
    _require(plan.chapter_count > 0, "book must have chapters")
    template = get_runtime_template(plan.runtime_format_id)
    if template:
        _require(plan.tier == template["tier"], f"runtime {plan.runtime_format_id} expects tier {template['tier']}")

    bands = [int(ch.band) for ch in plan.chapters]
    intensities = [int(ch.intensity) for ch in plan.chapters]
    _require(plan.dominant_band_sequence == bands, "dominant_band_sequence must match chapter bands")
    _require(plan.intensity_sequence == intensities, "intensity_sequence must match chapter intensities")
    for idx in range(1, len(bands)):
        _require(abs(bands[idx] - bands[idx - 1]) <= 2, "adjacent BAND step may not exceed 2")
    peak = max(bands)
    _require(bands[-1] < peak, "final chapter may not be the peak BAND")
    _require(0 <= int(plan.cost_chapter_index) < plan.chapter_count - 1, "cost_chapter_index must not be final")

    for idx in range(2, len(intensities)):
        window = intensities[idx - 2 : idx + 1]
        _require(window != [5, 5, 5], "macro cadence forbids three consecutive intensity 5 chapters")
    for idx, value in enumerate(intensities):
        if value >= 4:
            support_window = plan.chapters[idx + 1 : idx + 3]
            if support_window:
                _require(
                    any(ch.regulation_support in {"medium", "high"} for ch in support_window),
                    "intensity 4-5 must be followed by medium/high regulation within 2 chapters",
                )

    structures = [ch.bestseller_structure for ch in plan.chapters]
    for idx in range(2, len(structures)):
        _require(len(set(structures[idx - 2 : idx + 1])) > 1, "same bestseller_structure may not repeat 3 times")

    exercise_cap = int(template.get("exercise_cap", 99)) if template else 99
    for ch in plan.chapters:
        validate_chapter_plan(ch)
        exercises = sum(1 for slot in ch.slot_plans if str(slot.get("type") or slot.get("slot_type")).upper() == "EXERCISE")
        _require(exercises <= exercise_cap, "exercise slots exceed runtime cap")
    final = plan.chapters[-1]
    _require(bool(final.ending_contract), "final chapter requires ending_contract")
    return plan


def _candidate_plan_paths(topic_id: str, persona_id: str, runtime_format_id: str, repo_root: Path) -> list[Path]:
    runtime = (runtime_format_id or "").strip()
    suffixes = [runtime]
    alias = RUNTIME_ALIASES.get(runtime)
    if alias:
        suffixes.append(alias)
    if runtime in {"short_book_30", "micro_book_15", "micro_book_20"}:
        suffixes.append("1h")
    if runtime in {"standard_book", "deep_book_6h", "extended_book_2h", "deep_book_4h"}:
        suffixes.append("6h")
    seen: set[str] = set()
    paths: list[Path] = []
    for suffix in suffixes:
        if not suffix or suffix in seen:
            continue
        seen.add(suffix)
        paths.append(repo_root / "config" / "plans" / f"{topic_id}_{persona_id}_{suffix}.yaml")
    return paths


def load_book_structure_plan(
    topic_id: str,
    persona_id: str,
    runtime_format_id: str,
    repo_root: Path = REPO_ROOT,
) -> BookStructurePlan:
    if yaml is None:
        raise RuntimeError("PyYAML is required to load BookStructurePlan")
    ensure_ei_v2_book_structure_enforcement(repo_root)
    for path in _candidate_plan_paths(topic_id, persona_id, runtime_format_id, repo_root):
        if path.exists():
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            plan = BookStructurePlan.from_dict(data)
            return validate_book_arc(plan)
    candidates = ", ".join(str(p) for p in _candidate_plan_paths(topic_id, persona_id, runtime_format_id, repo_root))
    raise FileNotFoundError(
        f"No deterministic BookStructurePlan for topic={topic_id!r}, persona={persona_id!r}, "
        f"runtime={runtime_format_id!r}. Expected one of: {candidates}"
    )
