#!/usr/bin/env python3
"""Audit the latest zh-TW Gen Z anxiety render and write an exact repair backlog.

This does not auto-translate or rewrite content. It identifies failing chapters,
selected source IDs/files, placeholder leaks, and mixed-English prose so a native
writer can repair the exact source bank rather than patching rendered output.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

LATIN_RUN_RE = re.compile(r"\b[A-Za-z][A-Za-z'-]{2,}(?:\s+[A-Za-z][A-Za-z'-]{2,}){2,}\b")
PLACEHOLDER_RE = re.compile(
    r"\[[^\]]*(?:placeholder|persona-specific|integration content|todo|tbd)[^\]]*\]",
    re.IGNORECASE,
)
ALLOW_LATIN = {
    "Gen Z", "Slack", "Zoom", "Instagram", "TikTok", "YouTube", "ADHD",
    "PTSD", "HR", "CEO", "OKR", "KPI",
}


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _find_first(root: Path, names: Sequence[str]) -> Path | None:
    for name in names:
        direct = root / name
        if direct.is_file():
            return direct
    for path in root.rglob("*.json"):
        if path.name in names:
            return path
    return None


def _mixed_english(text: str) -> list[str]:
    hits: list[str] = []
    for match in LATIN_RUN_RE.finditer(text or ""):
        value = match.group(0).strip()
        if any(allowed in value for allowed in ALLOW_LATIN):
            continue
        hits.append(value)
    return hits


def _selected_rows(render_dir: Path) -> list[dict[str, Any]]:
    path = _find_first(
        render_dir,
        ("selected_content_variants.json", "section_packet_audit.json"),
    )
    if path is None:
        return []
    data = _load_json(path)
    if isinstance(data, list):
        return [dict(row) for row in data if isinstance(row, Mapping)]
    if isinstance(data, Mapping):
        for key in ("rows", "selected", "sections", "variants"):
            value = data.get(key)
            if isinstance(value, list):
                return [dict(row) for row in value if isinstance(row, Mapping)]
    return []


def build_backlog(repo: Path, render_dir: Path) -> dict[str, Any]:
    flow_path = _find_first(render_dir, ("chapter_flow_report.json",))
    if flow_path is None:
        return {
            "status": "BLOCKED",
            "blocker": f"chapter_flow_report.json missing under {render_dir}",
            "chapters": [],
        }
    flow = _load_json(flow_path)
    failed = {
        int(row.get("chapter") or row.get("chapter_index") or 0): row
        for row in (flow.get("chapters") or [])
        if str(row.get("status") or "").upper() != "PASS"
    }
    rows = _selected_rows(render_dir)
    by_chapter: dict[int, list[dict[str, Any]]] = {}
    for row in rows:
        chapter = int(row.get("chapter") or row.get("chapter_index") or 0)
        by_chapter.setdefault(chapter, []).append(row)

    chapter_backlog = []
    for chapter, gate in sorted(failed.items()):
        selected = []
        for row in by_chapter.get(chapter, []):
            prose = str(
                row.get("content")
                or row.get("body")
                or row.get("selected_prose")
                or ""
            )
            source_path = str(
                row.get("source_path")
                or row.get("path")
                or row.get("canonical_path")
                or ""
            )
            selected.append(
                {
                    "slot_type": row.get("slot_type") or row.get("type"),
                    "atom_id": row.get("atom_id") or row.get("variant_id"),
                    "source_path": source_path,
                    "mixed_english": _mixed_english(prose),
                    "placeholder_hits": PLACEHOLDER_RE.findall(prose),
                    "word_count": len(prose.split()),
                }
            )
        chapter_backlog.append(
            {
                "chapter": chapter,
                "gate_errors": gate.get("errors") or gate.get("issues") or [],
                "selected_sources": selected,
                "exact_files_needing_work": sorted(
                    {
                        row["source_path"]
                        for row in selected
                        if row["source_path"]
                    }
                ),
                "repair_requirements": [
                    "native zh-TW clear point",
                    "native zh-TW bridge/transition",
                    "remove mixed-English fallback",
                    "preserve Taiwanese register",
                ],
            }
        )

    manuscript = _find_first(render_dir, ("book.txt", "rendered_book.txt"))
    manuscript_hits = []
    placeholder_hits = []
    if manuscript:
        content = manuscript.read_text(encoding="utf-8")
        manuscript_hits = _mixed_english(content)
        placeholder_hits = PLACEHOLDER_RE.findall(content)

    status = "PASS" if not failed and not manuscript_hits and not placeholder_hits else "NEEDS_WRITER_REPAIR"
    return {
        "status": status,
        "render_dir": str(render_dir.relative_to(repo)) if render_dir.is_relative_to(repo) else str(render_dir),
        "chapter_flow_report": str(flow_path.relative_to(repo)) if flow_path.is_relative_to(repo) else str(flow_path),
        "failing_chapter_count": len(failed),
        "chapters": chapter_backlog,
        "manuscript_mixed_english_hits": manuscript_hits[:200],
        "manuscript_placeholder_hits": placeholder_hits[:200],
        "fresh_render_required_after_repair": True,
        "acceptance": {
            "chapter_flow": "PASS",
            "book_pass": "PASS",
            "book_quality": "Pass or acceptable advisory Hold",
            "mixed_english_fallback": 0,
            "placeholder_leaks": 0,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--render-dir", type=Path, required=True)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("artifacts/qa/zhtw_genz_anxiety_repair_20260714"),
    )
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    render = args.render_dir.resolve()
    out = args.out if args.out.is_absolute() else repo / args.out
    out.mkdir(parents=True, exist_ok=True)
    payload = build_backlog(repo, render)
    (out / "repair_backlog.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    lines = ["# zh-TW Gen Z Anxiety Repair Backlog", "", f"Status: **{payload['status']}**", ""]
    for chapter in payload.get("chapters", []):
        lines.append(f"## Chapter {chapter['chapter']}")
        lines.append("")
        lines.append("- Gate errors: " + ", ".join(map(str, chapter["gate_errors"])))
        for file in chapter["exact_files_needing_work"]:
            lines.append(f"- `{file}`")
        lines.append("")
    (out / "repair_backlog.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
