#!/usr/bin/env python3
"""
Bestseller-grade canary: single-chapter slice aligned with scripts/run_pipeline.py EI path.

Mirrors the pipeline slice where assembled chapter prose is scored (dimension gates +
heuristic safety). Does not run full Stage 1–3 compile; reads sentinel atom banks
the same way readiness checks use atoms/{persona}/{topic}/{engine}/CANONICAL.txt.

Usage:
  PYTHONPATH=. python3 scripts/canary/run_bestseller_canary.py
  PYTHONPATH=. python3 scripts/canary/run_bestseller_canary.py --evidence-dir artifacts/canary/manual_run
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

def _ei_v2_config_path(repo_root: Path) -> Path:
    return repo_root / "config" / "quality" / "ei_v2_config.yaml"


def _canary_override_path(repo_root: Path) -> Path:
    return repo_root / "config" / "canary" / "bestseller_canary_overrides.yaml"

_KEYLIKE_METADATA_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_ ]{0,40}\s*:\s*.+$")

# Slot / structural dirs under topic (not narrative engine banks)
_ATOM_SLOT_DIRS = frozenset({
    "HOOK", "SCENE", "STORY", "REFLECTION", "EXERCISE", "INTEGRATION", "COMPRESSION",
})


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml
    except ImportError:
        return {}
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data if isinstance(data, dict) else {}


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for k, v in override.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_merged_ei_config(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    """Load ei_v2_config.yaml and merge canary overrides (read-only base file)."""
    base = _load_yaml(_ei_v2_config_path(repo_root))
    override = _load_yaml(_canary_override_path(repo_root))
    return deep_merge(base, override)


def extract_first_proseful_section(path: Path, min_words: int = 6) -> str:
    """First ## section with enough prose (same spirit as run_pipeline readiness)."""
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    best = ""
    for section in re.split(r"(?m)^##\s+", text):
        section = section.strip()
        if not section:
            continue
        lines = section.splitlines()
        prose_lines: list[str] = []
        for line in lines[1:]:
            stripped = line.strip()
            if not stripped or stripped == "---":
                continue
            if _KEYLIKE_METADATA_RE.match(stripped):
                continue
            prose_lines.append(stripped)
        blob = " ".join(prose_lines)
        if len(blob.split()) >= min_words:
            return blob
    return best


def list_engine_candidates(topic_dir: Path) -> List[str]:
    engines: list[str] = []
    if not topic_dir.is_dir():
        return engines
    for p in sorted(topic_dir.iterdir()):
        if not p.is_dir():
            continue
        name = p.name
        if name in _ATOM_SLOT_DIRS:
            continue
        canon = p / "CANONICAL.txt"
        if canon.is_file():
            engines.append(name)
    return engines


def resolve_sentinel_tuple(
    repo_root: Path,
    merged: dict[str, Any],
) -> Tuple[str, str, str, str, Path, str]:
    """
    Returns persona, topic, engine_used, format_id, canonical_path, chapter_text.
    Prefers canary.sentinel_* engine if that bank exists; otherwise first engine with prose.
    """
    canary_meta = merged.get("canary") or {}
    persona = str(canary_meta.get("sentinel_default_persona") or "gen_z_professionals")
    topic = str(canary_meta.get("sentinel_default_topic") or "overthinking")
    preferred_engine = str(canary_meta.get("sentinel_default_engine") or "reflection")
    fmt = str(canary_meta.get("sentinel_default_format") or "standard_20ch")

    topic_dir = repo_root / "atoms" / persona / topic
    engines = list_engine_candidates(topic_dir)
    engine_used = preferred_engine if preferred_engine in engines else (engines[0] if engines else "")
    if not engine_used:
        return persona, topic, "", fmt, Path(), ""

    story_path = topic_dir / engine_used / "CANONICAL.txt"
    prose = extract_first_proseful_section(story_path)
    return persona, topic, engine_used, fmt, story_path, prose


def _import_dimension_gates() -> Tuple[Optional[Any], Optional[str]]:
    try:
        from phoenix_v4.quality.ei_v2 import dimension_gates as dg

        return dg, None
    except ImportError as e:
        return None, str(e)


def build_gate_registry(dg: Any, dg_cfg: dict[str, Any]) -> dict[str, Callable[..., Any]]:
    cohesion_cfg = dg_cfg.get("cohesion") if isinstance(dg_cfg.get("cohesion"), dict) else {}
    listen_cfg = dg_cfg.get("listen_experience") if isinstance(dg_cfg.get("listen_experience"), dict) else {}
    return {
        "uniqueness": lambda text, **kw: dg.gate_uniqueness(
            text, kw.get("other_texts") or [], int(kw.get("chapter_index", 0))
        ),
        "engagement": lambda text, **kw: dg.gate_engagement(text, int(kw.get("chapter_index", 0))),
        "somatic_precision": lambda text, **kw: dg.gate_somatic_precision(text),
        "cohesion": lambda text, **kw: dg.gate_cohesion(
            text,
            kw.get("other_texts") or [],
            int(kw.get("chapter_index", 0)),
            cohesion_cfg,
        ),
        "listen_experience": lambda text, **kw: dg.gate_listen_experience(text, listen_cfg),
    }


def run_blocked_dimension_gates(
    merged_cfg: dict[str, Any],
    chapter_text: str,
    dg_mod: Any,
) -> Tuple[List[dict[str, Any]], List[str], List[str], List[str]]:
    """
    Run gates listed in dimension_gates.blocked_dimensions.
    Returns (gate_records, passed, blocked, missing).
    """
    dg_cfg = merged_cfg.get("dimension_gates") or {}
    blocked_dims: List[str] = list(dg_cfg.get("blocked_dimensions") or [])
    registry = build_gate_registry(dg_mod, dg_cfg)

    records: list[dict[str, Any]] = []
    passed: list[str] = []
    blocked: list[str] = []
    missing: list[str] = []

    for dim in blocked_dims:
        fn = registry.get(dim)
        if fn is None:
            missing.append(dim)
            records.append(
                {
                    "dimension": dim,
                    "status": "MISSING",
                    "implementation": False,
                    "score": None,
                    "issues": ["no gate function in this checkout (awaiting bestseller-grade wiring)"],
                }
            )
            continue
        try:
            gr = fn(chapter_text, other_texts=[], chapter_index=0)
            d = gr.to_dict()
            d["implementation"] = True
            records.append(d)
            st = gr.status
            if st == "PASS":
                passed.append(dim)
            elif st == "FAIL":
                blocked.append(dim)
            else:
                # WARN — treat as blocked under canary strict enforcement
                blocked.append(dim)
        except Exception as exc:
            records.append(
                {
                    "dimension": dim,
                    "status": "ERROR",
                    "implementation": True,
                    "score": None,
                    "issues": [str(exc)],
                }
            )
            blocked.append(dim)

    return records, passed, blocked, missing


def run_heuristic_safety(chapter_text: str, merged_cfg: dict[str, Any]) -> dict[str, Any]:
    from phoenix_v4.quality.ei_v2.safety_classifier import classify_safety

    scfg = dict(merged_cfg.get("safety_classifier") or {})
    return classify_safety(chapter_text, cfg=scfg, full_cfg=merged_cfg)


def ensure_evidence_dir(repo_root: Path, explicit: Path | None) -> Path:
    if explicit is not None:
        d = explicit if explicit.is_absolute() else repo_root / explicit
    else:
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        d = repo_root / "artifacts" / "canary" / ts
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_bestseller_canary(
    repo_root: Path = REPO_ROOT,
    evidence_dir: Optional[Path] = None,
) -> tuple[int, dict[str, Any]]:
    """
    Execute canary; write evidence under evidence_dir.
    Returns (exit_code, summary_dict).
    """
    lines: list[str] = []
    fatal: list[str] = []

    def log(msg: str) -> None:
        lines.append(msg)

    summary: dict[str, Any] = {
        "canary_version": 1,
        "pipeline_reference": "scripts/run_pipeline.py (EI slice: chapter prose + dimension gates + safety)",
        "repo_root": str(repo_root),
        "gates_passed": [],
        "gates_blocked": [],
        "gates_missing": [],
        "missing_modules": [],
        "errors": [],
        "overall_status": "ERROR",
    }

    try:
        merged = load_merged_ei_config(repo_root)
    except Exception as exc:
        summary["errors"].append(f"config_load: {exc}")
        summary["overall_status"] = "ERROR"
        return 2, summary

    base_cfg = _ei_v2_config_path(repo_root)
    if not base_cfg.exists():
        summary["errors"].append(f"missing_base_config:{base_cfg}")
        return 2, summary

    ev = ensure_evidence_dir(repo_root, evidence_dir)
    summary["evidence_dir"] = str(ev)

    persona, topic, engine_used, fmt, story_path, chapter_text = resolve_sentinel_tuple(repo_root, merged)
    try:
        atoms_rel = str(story_path.relative_to(repo_root))
    except ValueError:
        atoms_rel = str(story_path)
    summary["sentinel"] = {
        "persona_id": persona,
        "topic_id": topic,
        "engine_id": engine_used,
        "format_id": fmt,
        "atoms_canonical_path": atoms_rel,
    }

    if not chapter_text.strip():
        summary["errors"].append("no_chapter_prose: check atoms path / engine resolution")
        summary["overall_status"] = "ERROR"
        _write_evidence(ev, summary, lines, chapter_text, [], {}, fatal)
        return 2, summary

    dg_mod, import_err = _import_dimension_gates()
    if dg_mod is None:
        summary["missing_modules"].append("phoenix_v4.quality.ei_v2.dimension_gates")
        summary["errors"].append(import_err or "import_error")
        summary["overall_status"] = "ERROR"
        _write_evidence(ev, summary, lines, chapter_text, [], {}, fatal)
        return 2, summary

    gate_records, passed, blocked, missing = run_blocked_dimension_gates(
        merged_cfg=merged,
        chapter_text=chapter_text,
        dg_mod=dg_mod,
    )
    summary["gates_passed"] = passed
    summary["gates_blocked"] = blocked
    summary["gates_missing"] = missing

    dg_cfg = merged.get("dimension_gates") or {}
    fail_mode = str(dg_cfg.get("fail_mode") or "warn")
    summary["dimension_gates_fail_mode"] = fail_mode
    summary["dimension_gate_phase"] = dg_cfg.get("dimension_gate_phase")

    safety = run_heuristic_safety(chapter_text, merged)
    summary["safety_classifier"] = {
        "risk_score": safety.get("risk_score"),
        "reason_codes": safety.get("reason_codes"),
        "mode": safety.get("mode"),
    }

    # Overall status
    has_fail = bool(blocked) or bool(missing)
    if fail_mode == "block" and has_fail:
        summary["overall_status"] = "FAIL"
        code = 1
    else:
        summary["overall_status"] = "PASS"
        code = 0

    log(f"Canary overall_status={summary['overall_status']} exit={code}")
    log(f"gates_passed={passed}")
    log(f"gates_blocked={blocked}")
    log(f"gates_missing={missing}")

    _write_evidence(ev, summary, lines, chapter_text, gate_records, safety, fatal)
    return code, summary


def _write_evidence(
    ev: Path,
    summary: dict[str, Any],
    log_lines: list[str],
    chapter_text: str,
    gate_records: list[dict[str, Any]],
    safety: dict[str, Any],
    fatal: list[str],
) -> None:
    summary["fatal_errors"] = fatal
    (ev / "canary_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (ev / "chapter_gates_detail.json").write_text(
        json.dumps({"gates": gate_records, "excerpt_word_count": len(chapter_text.split())}, indent=2, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
    (ev / "safety_classifier_snapshot.json").write_text(
        json.dumps(safety, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (ev / "canary_stdout.txt").write_text("\n".join(log_lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Bestseller-grade canary (single-chapter EI slice)")
    ap.add_argument(
        "--evidence-dir",
        default=None,
        help="Evidence output directory (default: artifacts/canary/<UTC timestamp>)",
    )
    ap.add_argument(
        "--repo-root",
        default=None,
        help="Override repo root (tests)",
    )
    args = ap.parse_args(argv)
    root = Path(args.repo_root).resolve() if args.repo_root else REPO_ROOT
    ev_path = Path(args.evidence_dir) if args.evidence_dir else None
    try:
        code, summary = run_bestseller_canary(repo_root=root, evidence_dir=ev_path)
    except Exception as exc:
        # Last-resort capture (should be rare; prefer structured errors inside run_bestseller_canary)
        sys.stderr.write(f"canary_crash: {exc}\n{traceback.format_exc()}")
        return 2
    print(json.dumps({"exit_code": code, "overall_status": summary.get("overall_status"), "evidence_dir": summary.get("evidence_dir")}, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main())
