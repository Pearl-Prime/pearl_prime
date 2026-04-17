"""Whole-book quality gate for rendered Phoenix manuscripts.

This gate is intentionally deterministic. It does not claim a book is a
commercial bestseller; it catches release-blocking assembly failures that make a
manuscript unfit to call bestseller-ready.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from phoenix_v4.quality.chapter_flow_gate import evaluate_chapter_flow, flow_profile_for_runtime_format


@dataclass
class BookQualityReport:
    release_band: str
    fail_reasons: list[str] = field(default_factory=list)
    hold_reasons: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)

    @property
    def status(self) -> str:
        if self.release_band == "Reject":
            return "FAIL"
        if self.release_band == "Hold":
            return "WARN"
        return "PASS"

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "release_band": self.release_band,
            "fail_reasons": self.fail_reasons,
            "hold_reasons": self.hold_reasons,
            "metrics": self.metrics,
        }


_ARTIFACT_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("unresolved_placeholder", re.compile(r"\{[A-Za-z_][A-Za-z0-9_]*\}")),
    ("raw_separator", re.compile(r"---")),
    ("slot_header", re.compile(r"##\s+(HOOK|SCENE|STORY|REFLECTION|PIVOT|EXERCISE|INTEGRATION|THREAD|TAKEAWAY)\b", re.I)),
    ("python_repr", re.compile(r"\{['\"][^'\"]+['\"]\s*:")),
    ("content_gap", re.compile(r"\[CONTENT GAP", re.I)),
)


def _extract_chapters(text: str) -> list[str]:
    chapters: list[str] = []
    current: list[str] = []
    in_chapter = False
    for line in (text or "").splitlines():
        if re.match(r"^\s*Chapter\s+\d+\s*$", line.strip()):
            if in_chapter and current:
                chapters.append("\n".join(current).strip())
            current = [line]
            in_chapter = True
        elif in_chapter:
            current.append(line)
    if in_chapter and current:
        chapters.append("\n".join(current).strip())
    return [c for c in chapters if c]


def _runtime_word_range(runtime_format_id: str) -> Optional[tuple[int, int]]:
    try:
        from phoenix_v4.rendering.book_renderer import _runtime_word_range as _book_renderer_runtime_word_range

        return _book_renderer_runtime_word_range(runtime_format_id)
    except Exception:
        return None


def _repeated_phrase_violations(text: str, *, cap: int = 12) -> list[dict[str, Any]]:
    words = re.findall(r"[a-z0-9']+", (text or "").lower())
    counts: dict[str, int] = {}
    ignored_prefixes = (
        "the point is that",
        "i want you to",
        "now i want you",
        "not to fix anything",
        "anything just to",
        "fix anything",
        "to fix anything",
        "just to give yourself",
        "to give yourself",
        "give yourself a",
        "before you move on",
        "a different input",
        "different input for",
        "input for a",
        "one breath at a time",
    )
    for n in (4, 5, 6):
        for i in range(0, max(0, len(words) - n + 1)):
            phrase = " ".join(words[i : i + n])
            if any(phrase.startswith(prefix) for prefix in ignored_prefixes):
                continue
            counts[phrase] = counts.get(phrase, 0) + 1
    offenders = [
        {"phrase": phrase, "count": count}
        for phrase, count in counts.items()
        if count > cap
    ]
    offenders.sort(key=lambda x: (-int(x["count"]), str(x["phrase"])))
    return offenders[:20]


def evaluate_book_quality(
    prose: str,
    *,
    runtime_format_id: str = "",
    governance_report: dict | None = None,
    slot_sequences: list | None = None,
    frame: str = "somatic_first",
    policy_override: bool = False,
) -> BookQualityReport:
    del slot_sequences, frame

    text = (prose or "").strip()
    fail_reasons: list[str] = []
    hold_reasons: list[str] = []

    chapters = _extract_chapters(text)
    word_count = len(text.split())
    bounds = _runtime_word_range(runtime_format_id)
    if not text:
        fail_reasons.append("manuscript is empty")
    if len(chapters) == 0:
        fail_reasons.append("no Chapter N sections found")

    if bounds:
        lo, hi = bounds
        if word_count < lo:
            fail_reasons.append(f"word count below {runtime_format_id} minimum ({word_count} < {lo})")
        elif word_count > int(hi * 1.25):
            hold_reasons.append(f"word count materially above {runtime_format_id} range ({word_count} > {hi})")

    artifact_hits = [
        label for label, pattern in _ARTIFACT_PATTERNS if pattern.search(text)
    ]
    if artifact_hits:
        fail_reasons.append("delivery artifacts present: " + ", ".join(sorted(artifact_hits)))

    flow_profile = flow_profile_for_runtime_format(runtime_format_id)
    flow_failures: list[dict[str, Any]] = []
    for idx, chapter in enumerate(chapters):
        res = evaluate_chapter_flow(chapter, flow_profile=flow_profile)
        if res.status != "PASS":
            flow_failures.append({"chapter": idx + 1, "errors": res.errors})
    if flow_failures:
        fail_reasons.append(f"chapter flow failed in {len(flow_failures)} chapter(s)")

    repeated = _repeated_phrase_violations(text)
    if repeated:
        hold_reasons.append("repeated phrase density above book cap")

    if governance_report:
        governance_errors = [
            str(v) for k, v in governance_report.items()
            if "error" in str(k).lower() and v
        ]
        if governance_errors:
            hold_reasons.append("governance report contains error entries")

    if policy_override and fail_reasons and all("word count below" in r for r in fail_reasons):
        hold_reasons.extend(fail_reasons)
        fail_reasons = []

    release_band = "Reject" if fail_reasons else ("Hold" if hold_reasons else "Pass")
    return BookQualityReport(
        release_band=release_band,
        fail_reasons=fail_reasons,
        hold_reasons=hold_reasons,
        metrics={
            "runtime_format_id": runtime_format_id,
            "word_count": word_count,
            "word_range": list(bounds) if bounds else None,
            "chapter_count": len(chapters),
            "flow_profile": flow_profile,
            "flow_failures": flow_failures,
            "artifact_hits": artifact_hits,
            "repeated_phrase_violations": repeated,
        },
    )


def write_book_quality_report(report: BookQualityReport, output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")


def load_book_quality_config() -> dict[str, Any]:
    import yaml

    path = Path(__file__).resolve().parents[2] / "config" / "quality" / "book_quality_gate.yaml"
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}
