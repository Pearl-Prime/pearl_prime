"""
EI V2 learner: load/save learned params and feedback log for hybrid override tuning.
Fail-open; used by hybrid_selector for override_margin and composite_weights.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, List

_OVERRIDE_MARGIN_MIN = 0.05
_OVERRIDE_MARGIN_MAX = 0.30

DEFAULT_COMPOSITE_WEIGHTS = {
    "rerank": 0.35,
    "domain": 0.25,
    "safety": 0.2,
    "tts": 0.1,
    "emotion_arc": 0.1,
}


@dataclass
class LearnedParams:
    version: int = 1
    override_margin: float = 0.12
    total_observations: int = 0
    composite_weights: dict[str, float] = field(default_factory=lambda: dict(DEFAULT_COMPOSITE_WEIGHTS))

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "override_margin": self.override_margin,
            "total_observations": self.total_observations,
            "composite_weights": self.composite_weights,
        }


def load_learned_params(path: Path | None = None) -> LearnedParams:
    """Load learned params from JSON; return defaults if file missing."""
    if path is None or not path.exists():
        return LearnedParams()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        weights = data.get("composite_weights") or {}
        for k, v in DEFAULT_COMPOSITE_WEIGHTS.items():
            if k not in weights:
                weights[k] = v
        return LearnedParams(
            version=int(data.get("version", 1)),
            override_margin=float(data.get("override_margin", 0.12)),
            total_observations=int(data.get("total_observations", 0)),
            composite_weights=weights,
        )
    except (json.JSONDecodeError, OSError):
        return LearnedParams()


def save_learned_params(params: LearnedParams, path: Path) -> None:
    """Write learned params to JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(params.to_dict(), indent=2), encoding="utf-8")


@dataclass
class FeedbackRecord:
    timestamp: str
    slot: str
    chapter_index: int
    persona_id: str
    topic_id: str
    v1_chosen_id: str
    v2_chosen_id: str
    hybrid_chosen_id: str
    override_applied: bool
    # Optional calibration fields (human / pipeline feedback for learning)
    accepted: bool = False
    v1_score: float = 0.0
    v2_score: float = 0.0
    margin_delta: float = 0.0
    dimension_scores: dict[str, float] = field(default_factory=dict)


def log_feedback(record: FeedbackRecord, path: Path) -> None:
    """Append one feedback record as JSONL line."""
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(asdict(record), ensure_ascii=False) + "\n"
    with open(path, "a", encoding="utf-8") as f:
        f.write(line)


def load_feedback(path: Path) -> List[FeedbackRecord]:
    """Load all feedback records from JSONL."""
    if not path.exists():
        return []
    records = []
    for line in path.read_text(encoding="utf-8").strip().splitlines():
        if not line:
            continue
        try:
            d = json.loads(line)
            dim_raw = d.get("dimension_scores")
            dimension_scores: dict[str, float] = {}
            if isinstance(dim_raw, dict):
                for k, v in dim_raw.items():
                    try:
                        dimension_scores[str(k)] = float(v)
                    except (TypeError, ValueError):
                        continue
            records.append(FeedbackRecord(
                timestamp=d.get("timestamp", ""),
                slot=d.get("slot", ""),
                chapter_index=int(d.get("chapter_index", 0)),
                persona_id=d.get("persona_id", ""),
                topic_id=d.get("topic_id", ""),
                v1_chosen_id=d.get("v1_chosen_id", ""),
                v2_chosen_id=d.get("v2_chosen_id", ""),
                hybrid_chosen_id=d.get("hybrid_chosen_id", ""),
                override_applied=bool(d.get("override_applied", False)),
                accepted=bool(d.get("accepted", False)),
                v1_score=float(d.get("v1_score", 0.0)),
                v2_score=float(d.get("v2_score", 0.0)),
                margin_delta=float(d.get("margin_delta", 0.0)),
                dimension_scores=dimension_scores,
            ))
        except (json.JSONDecodeError, KeyError, ValueError, TypeError):
            continue
    return records


def _learner_cfg(cfg: dict | None) -> dict[str, float | int]:
    """Resolve learner knobs; defaults match config/quality/ei_v2_config.yaml."""
    defaults = {"ema_alpha": 0.15, "learning_window": 200, "min_observations": 10}
    if not cfg:
        return defaults
    learner = cfg.get("learner")
    if not isinstance(learner, dict):
        return defaults
    out = dict(defaults)
    if "ema_alpha" in learner:
        out["ema_alpha"] = float(learner["ema_alpha"])
    if "learning_window" in learner:
        out["learning_window"] = int(learner["learning_window"])
    if "min_observations" in learner:
        out["min_observations"] = int(learner["min_observations"])
    return out


def _mean(values: List[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / float(len(values))


def _clamp_override_margin(x: float) -> float:
    return max(_OVERRIDE_MARGIN_MIN, min(_OVERRIDE_MARGIN_MAX, x))


def learn_from_feedback(
    feedback_path: Path,
    params_path: Path,
    cfg: dict | None = None,
) -> LearnedParams:
    """
    EMA update of composite_weights and override_margin from JSONL feedback.
    Deterministic: same file order and contents -> same LearnedParams.
    """
    lc = _learner_cfg(cfg)
    min_obs = int(lc["min_observations"])
    window_n = int(lc["learning_window"])
    alpha = float(lc["ema_alpha"])

    records = load_feedback(feedback_path)
    current = load_learned_params(params_path)

    if len(records) < min_obs:
        return current

    window = records[-window_n:] if window_n > 0 else records

    # Merge current weights with defaults so every dimension exists
    weights: dict[str, float] = {k: float(current.composite_weights.get(k, v)) for k, v in DEFAULT_COMPOSITE_WEIGHTS.items()}
    accepted = [r for r in window if r.accepted]

    new_weights: dict[str, float] = {}
    for dim in DEFAULT_COMPOSITE_WEIGHTS:
        cur_w = weights[dim]
        vals = [r.dimension_scores[dim] for r in accepted if dim in r.dimension_scores]
        avg_contrib = _mean(vals) if vals else cur_w
        new_weights[dim] = alpha * avg_contrib + (1.0 - alpha) * cur_w

    total = sum(new_weights.values())
    if total > 0:
        new_weights = {k: new_weights[k] / total for k in new_weights}

    override_rows = [r for r in window if r.override_applied]
    cur_margin = float(current.override_margin)
    if override_rows:
        deltas = [float(r.margin_delta) for r in override_rows]
        avg_delta = _mean(deltas)
    else:
        avg_delta = cur_margin
    new_margin = alpha * avg_delta + (1.0 - alpha) * cur_margin
    new_margin = _clamp_override_margin(new_margin)

    updated = LearnedParams(
        version=current.version,
        override_margin=new_margin,
        total_observations=len(records),
        composite_weights=new_weights,
    )
    save_learned_params(updated, params_path)
    return updated


def calibration_report(params: LearnedParams, previous: LearnedParams) -> dict[str, Any]:
    """Diff of composite weights and override_margin for logging / telemetry."""
    comp: dict[str, Any] = {}
    for dim in DEFAULT_COMPOSITE_WEIGHTS:
        prev_w = float(previous.composite_weights.get(dim, DEFAULT_COMPOSITE_WEIGHTS[dim]))
        cur_w = float(params.composite_weights.get(dim, DEFAULT_COMPOSITE_WEIGHTS[dim]))
        comp[dim] = {
            "previous": prev_w,
            "current": cur_w,
            "delta": cur_w - prev_w,
        }
    return {
        "override_margin": {
            "previous": float(previous.override_margin),
            "current": float(params.override_margin),
            "delta": float(params.override_margin) - float(previous.override_margin),
        },
        "composite_weights": comp,
    }
