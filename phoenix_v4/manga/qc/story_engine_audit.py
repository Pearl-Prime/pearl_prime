"""Batch audit helpers for governed story-engine conformance."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from phoenix_v4.manga.qc.genre_engine_gate import evaluate_genre_engine
from phoenix_v4.manga.story_engine_loader import (
    governed_genres,
    is_engine_governed,
    resolve_engine_genre,
    validate_architect_chapters,
)
from phoenix_v4.manga.story_strategy_loader import strategy_bank_exists


def _load_yaml_mapping(path: Path) -> dict[str, Any] | None:
    try:
        import yaml
    except ImportError:
        return None
    if not path.is_file():
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else None


def audit_chapter_script_engine(
    path: Path,
    *,
    repo_root: Path,
) -> dict[str, str]:
    """Return one audit row; empty failure_reasons means PASS."""
    try:
        rel = str(path.relative_to(repo_root))
    except ValueError:
        rel = str(path)
    row: dict[str, str] = {
        "series_id": path.parent.name,
        "script_path": rel,
        "declared_genre": "",
        "engine_genre": "",
        "governed": "no",
        "failure_reasons": "",
        "status": "PASS",
    }
    data = _load_yaml_mapping(path)
    if data is None:
        row["status"] = "SKIP"
        row["failure_reasons"] = "missing or unparseable script"
        return row

    declared = str(data.get("genre") or data.get("genre_id") or "")
    row["declared_genre"] = declared
    if not declared:
        row["status"] = "SKIP"
        row["failure_reasons"] = "no declared genre"
        return row

    canon = resolve_engine_genre(declared, repo_root)
    row["engine_genre"] = canon
    if not is_engine_governed(declared, repo_root):
        row["governed"] = "no"
        row["status"] = "SKIP"
        return row

    row["governed"] = "yes"
    findings = evaluate_genre_engine(data, genre_id=declared)
    blockers = [f for f in findings if f.get("severity") == "BLOCKER"]
    if blockers:
        row["status"] = "FAIL"
        row["failure_reasons"] = "; ".join(
            str(f.get("description") or f.get("issue_code") or "") for f in blockers
        )
    return row


def discover_chapter_script_paths(
    repo_root: Path,
    *,
    series_ids: list[str] | None = None,
    glob_pattern: str = "**/*.yaml",
    roots: tuple[str, ...] = (
        "artifacts/manga/chapter_scripts",
        "artifacts/manga/pilots",
    ),
) -> list[Path]:
    """Collect chapter_script YAML paths under known manga artifact roots."""
    if series_ids:
        out: list[Path] = []
        for sid in series_ids:
            for root_name in roots:
                base = repo_root / root_name
                if (base / sid).is_dir():
                    out.extend(sorted((base / sid).glob(glob_pattern)))
                for p in base.rglob(f"{sid}/*.yaml"):
                    if p.is_file():
                        out.append(p)
        return sorted(set(out))

    paths: list[Path] = []
    for root_name in roots:
        base = repo_root / root_name
        if not base.is_dir():
            continue
        paths.extend(sorted(base.glob(glob_pattern)))
    return sorted(set(paths))


def audit_chapter_script_corpus(
    repo_root: Path,
    *,
    series_ids: list[str] | None = None,
    only_governed: bool = True,
) -> list[dict[str, str]]:
    """Full-scan governed chapter scripts (pilots + chapter_scripts)."""
    rows: list[dict[str, str]] = []
    for path in discover_chapter_script_paths(repo_root, series_ids=series_ids):
        row = audit_chapter_script_engine(path, repo_root=repo_root)
        if only_governed and row["status"] == "SKIP" and row["governed"] == "no":
            continue
        rows.append(row)
    return rows


def audit_architect_governed_genres(
    repo_root: Path,
    *,
    genre_topic_pairs: list[tuple[str, str]] | None = None,
) -> list[dict[str, str]]:
    """Probe architect output for every governed genre with a strategy bank."""
    from phoenix_v4.manga.series.story_architect import build_story_architecture_internal

    pairs = genre_topic_pairs or _default_architect_probe_pairs(repo_root)
    rows: list[dict[str, str]] = []
    for genre, topic in pairs:
        row = {
            "series_id": f"engine_audit__{genre}__{topic}",
            "script_path": f"architect_probe:{genre}:{topic}",
            "declared_genre": genre,
            "engine_genre": resolve_engine_genre(genre, repo_root),
            "governed": "yes",
            "failure_reasons": "",
            "status": "PASS",
        }
        if not strategy_bank_exists(genre):
            row["status"] = "FAIL"
            row["failure_reasons"] = f"missing strategy bank for governed genre {genre!r}"
            rows.append(row)
            continue
        try:
            internal = build_story_architecture_internal(
                series_id=f"strat_{topic}_{genre}",
                arc_id="a",
                genre_id=genre,
                topic=topic,
                repo_root=repo_root,
            )
            validate_architect_chapters(internal["chapters"], genre, repo_root=repo_root)
        except Exception as exc:
            row["status"] = "FAIL"
            row["failure_reasons"] = str(exc)
        rows.append(row)
    return rows


def _default_architect_probe_pairs(repo_root: Path) -> list[tuple[str, str]]:
    defaults: dict[str, str] = {
        "psychological_horror": "anxiety",
        "workplace_drama": "burnout",
        "action_battle": "courage",
        "romance_josei_drama": "social_anxiety",
        "sports_competition": "perfectionism",
        "dark_fantasy": "grief",
        "psychological_thriller": "paranoia",
        "cultivation_martial": "discipline",
    }
    return [(g, defaults.get(g, "courage")) for g in governed_genres(repo_root)]


def write_audit_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fields = (
        "series_id",
        "script_path",
        "declared_genre",
        "engine_genre",
        "governed",
        "status",
        "failure_reasons",
    )
    with out_path.open("w", encoding="utf-8", newline="") as fh:
        fh.write("\t".join(fields) + "\n")
        for row in rows:
            fh.write("\t".join(str(row.get(f, "")).replace("\t", " ") for f in fields) + "\n")


def merge_audit_rows(*groups: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[str] = set()
    out: list[dict[str, str]] = []
    for group in groups:
        for row in group:
            key = row.get("script_path") or row.get("series_id") or ""
            if key in seen:
                continue
            seen.add(key)
            out.append(row)
    return out
