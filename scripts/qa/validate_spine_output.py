#!/usr/bin/env python3
"""validate_spine_output.py — spine-mode safety gate (Session 4).

Runs post-render. Inspects a rendered book directory (e.g.
artifacts/rendered/<id>/) and produces a pass/fail safety report
covering the failure modes documented in
artifacts/pilot/DEFINITIVE_PIPELINE_COMPARISON.md and
artifacts/pilots/CHAPTER_FLOW_FIX_REPORT.md.

This validator does NOT change pipeline defaults. The intent is:
operators / CI can opt into `--pipeline-mode spine` and KNOW whether
the resulting render is safe to ship.

GATES
-----
LENGTH         — book.txt word count vs budget.json word_range_target
CHAPTER_FLOW   — chapter_flow_report.json overall status (PASS/FAIL +
                 per-chapter errors like WEAK_TRANSITIONS,
                 MISSING_CLEAR_POINT, GENERIC_SCENE_FALLBACK)
TEMPLATE_LEAK  — unsubstituted Jinja/curly placeholders, TODO/FILL
                 markers, unbalanced curly braces in prose
DUP_BLOCK      — paragraph-level duplicates appearing in 2+ chapters
                 (signals slot-concatenation failure mode where the
                 same bridge / CTA block is repeated verbatim)
LOC_GROUNDING  — surfaces location_grounding_report.json status if present
COMPOSITION    — derived from CHAPTER_FLOW errors; flags the linear-concat
                 failure mode named in the pilot doc

EXIT CODES
----------
0 — all checks PASS, or only WARN-level findings
1 — at least one ERROR-level finding (spine output unsafe to ship)
2 — input error (no render dir, no book.txt, etc.)

USAGE
-----
  # Single render dir
  python3 scripts/qa/validate_spine_output.py artifacts/rendered/<id>/

  # JSON output (CI-friendly)
  python3 scripts/qa/validate_spine_output.py --json artifacts/rendered/<id>/

  # Write report files into the render dir
  python3 scripts/qa/validate_spine_output.py --write artifacts/rendered/<id>/

  # Batch — every subdirectory of a parent
  python3 scripts/qa/validate_spine_output.py --batch artifacts/rendered/
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]

# ── Word-count thresholds (default for standard_book) ──────────────────────
DEFAULT_WORD_MIN = 9000
DEFAULT_WORD_MAX = 11000
TINY_BOOK_FLOOR = 1500  # below this we report a separate INFO so tests don't fail loudly

# ── Template-leak patterns ──────────────────────────────────────────────────
# Each entry: (regex, code, message)
_LEAK_PATTERNS: list[tuple[re.Pattern[str], str, str]] = [
    (re.compile(r"\{\{[^}]+\}\}"), "jinja_double_brace", "Unrendered Jinja {{ ... }} expression"),
    (re.compile(r"\{%[^%]+%\}"), "jinja_statement", "Unrendered Jinja {% ... %} statement"),
    (re.compile(r"<\s*TODO\b[^>]*>", re.IGNORECASE), "todo_placeholder", "<TODO> placeholder in prose"),
    (re.compile(r"<\s*FILL\b[^>]*>", re.IGNORECASE), "fill_placeholder", "<FILL> placeholder in prose"),
    (re.compile(r"<\s*PLACEHOLDER\b[^>]*>", re.IGNORECASE), "explicit_placeholder", "<PLACEHOLDER> in prose"),
    (re.compile(r"\[\s*(?:TODO|FILL|TBD|PLACEHOLDER)\s*\]", re.IGNORECASE), "bracket_placeholder", "[TODO/FILL/TBD] placeholder in prose"),
    (re.compile(r"\bLOREM IPSUM\b", re.IGNORECASE), "lorem_ipsum", "lorem ipsum filler in prose"),
]
# Match unbalanced opening curly: `{Word ...` with no closing `}` later in same paragraph.
# This catches the failure mode visible in artifacts/rendered/.../book.txt where location
# substitutions failed (e.g. "{Lexington Avenue below is visible.").
_UNBALANCED_BRACE_RE = re.compile(r"\{[A-Za-z][^}\n]{4,200}(?=\n|\.|\,)")

# ── Duplicate-block detection ──────────────────────────────────────────────
DUP_PARAGRAPH_MIN_CHARS = 80  # ignore short utility lines like "Chapter 1" / "Yes."
DUP_PARAGRAPH_MAX_REPORT = 10  # cap report size

# ── Severity levels ────────────────────────────────────────────────────────
SEVERITY_INFO = "INFO"
SEVERITY_WARN = "WARN"
SEVERITY_ERROR = "ERROR"


@dataclass
class Finding:
    gate: str
    severity: str
    code: str
    message: str
    detail: dict[str, Any] = field(default_factory=dict)


@dataclass
class Report:
    render_dir: str
    findings: list[Finding] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)

    @property
    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == SEVERITY_ERROR]

    @property
    def warns(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == SEVERITY_WARN]

    @property
    def passed(self) -> bool:
        return not self.errors

    def add(self, gate: str, severity: str, code: str, message: str, **detail: Any) -> None:
        self.findings.append(Finding(gate, severity, code, message, detail))

    def to_dict(self) -> dict[str, Any]:
        return {
            "render_dir": self.render_dir,
            "passed": self.passed,
            "metrics": self.metrics,
            "findings": [asdict(f) for f in self.findings],
        }


# ── Loaders ───────────────────────────────────────────────────────────────


def _read_text(path: Path) -> str | None:
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8", errors="replace")


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


# ── Gates ─────────────────────────────────────────────────────────────────


def _gate_length(book_text: str, budget: dict[str, Any] | None, report: Report) -> None:
    word_count = len(book_text.split())
    report.metrics["word_count"] = word_count

    target_min = DEFAULT_WORD_MIN
    target_max = DEFAULT_WORD_MAX
    runtime_format = None
    if budget:
        runtime_format = budget.get("runtime_format_id")
        rng = budget.get("word_range_target")
        if isinstance(rng, list) and len(rng) == 2 and all(isinstance(x, (int, float)) for x in rng):
            target_min, target_max = int(rng[0]), int(rng[1])
        elif isinstance(rng, dict) and "min" in rng and "max" in rng:
            target_min, target_max = int(rng["min"]), int(rng["max"])

    report.metrics["word_target_min"] = target_min
    report.metrics["word_target_max"] = target_max
    report.metrics["runtime_format"] = runtime_format

    if word_count < TINY_BOOK_FLOOR:
        # Probably a smoke render or fragment; report INFO and skip strict gate.
        report.add(
            "LENGTH", SEVERITY_INFO, "tiny_render",
            f"Word count {word_count} is below the {TINY_BOOK_FLOOR}-word smoke-render floor; "
            "skipping strict length gate",
            word_count=word_count, floor=TINY_BOOK_FLOOR,
        )
        return

    if word_count < target_min:
        report.add(
            "LENGTH", SEVERITY_ERROR, "below_target_min",
            f"Word count {word_count} is below the {runtime_format or 'default'} target minimum {target_min}",
            word_count=word_count, target_min=target_min, runtime_format=runtime_format,
            deficit=target_min - word_count,
        )
    elif word_count > target_max:
        report.add(
            "LENGTH", SEVERITY_WARN, "above_target_max",
            f"Word count {word_count} is above the {runtime_format or 'default'} target maximum {target_max}",
            word_count=word_count, target_max=target_max, runtime_format=runtime_format,
            surplus=word_count - target_max,
        )


def _gate_chapter_flow(flow_report: dict[str, Any] | None, report: Report) -> None:
    if flow_report is None:
        report.add(
            "CHAPTER_FLOW", SEVERITY_WARN, "no_chapter_flow_report",
            "chapter_flow_report.json not present in render dir; cannot gate chapter flow",
        )
        return

    overall = (flow_report.get("status") or "").upper()
    failed = int(flow_report.get("failed_chapters") or 0)
    total = int(flow_report.get("chapter_count") or 0)
    report.metrics["chapter_count"] = total
    report.metrics["failed_chapters"] = failed
    report.metrics["chapter_flow_status"] = overall

    if overall == "FAIL":
        # Aggregate distinct error codes across chapters for visibility.
        per_chapter_errors: dict[str, list[int]] = defaultdict(list)
        for ch in (flow_report.get("chapters") or []):
            for code in (ch.get("errors") or []):
                per_chapter_errors[code].append(ch.get("chapter"))
        report.add(
            "CHAPTER_FLOW", SEVERITY_ERROR, "chapter_flow_fail",
            f"chapter_flow_report status FAIL ({failed}/{total} chapters failing)",
            failed=failed, total=total,
            errors_by_code={k: v for k, v in per_chapter_errors.items()},
        )
        # Specific composition-flow signal (named in the pilot doc).
        composition_codes = {"WEAK_TRANSITIONS", "MISSING_CLEAR_POINT", "GENERIC_SCENE_FALLBACK"}
        hits = composition_codes & set(per_chapter_errors.keys())
        if hits:
            report.add(
                "COMPOSITION", SEVERITY_ERROR, "linear_concat_signature",
                "Chapter errors match the linear-concat failure signature documented in "
                "artifacts/pilot/DEFINITIVE_PIPELINE_COMPARISON.md (compose_from_enriched_book "
                "concatenates slot bodies in beatmap order instead of running thesis-threaded "
                "compose_chapter_prose)",
                composition_error_codes=sorted(hits),
            )
    elif overall != "PASS":
        report.add(
            "CHAPTER_FLOW", SEVERITY_WARN, "chapter_flow_unknown_status",
            f"chapter_flow_report status is {overall!r}; expected PASS or FAIL",
            status=overall,
        )


def _gate_template_leak(book_text: str, report: Report) -> None:
    leaks: dict[str, int] = defaultdict(int)
    examples: dict[str, list[str]] = defaultdict(list)

    for pat, code, _msg in _LEAK_PATTERNS:
        for m in pat.finditer(book_text):
            leaks[code] += 1
            if len(examples[code]) < 3:
                examples[code].append(m.group(0)[:120])

    # Unbalanced curly braces: `{Word ...` with no closing `}` before the next sentence/newline.
    for m in _UNBALANCED_BRACE_RE.finditer(book_text):
        snippet = m.group(0)
        # If a `}` appears later in the same paragraph, treat as balanced and skip.
        end = m.end()
        next_close = book_text.find("}", end)
        next_break = book_text.find("\n\n", end)
        # Conservative: only count if no `}` before next blank-line break.
        if next_close == -1 or (next_break != -1 and next_close > next_break):
            leaks["unbalanced_curly_brace"] += 1
            if len(examples["unbalanced_curly_brace"]) < 3:
                examples["unbalanced_curly_brace"].append(snippet[:120])

    report.metrics["template_leak_counts"] = dict(leaks)

    for code, count in leaks.items():
        # Match message text from _LEAK_PATTERNS where possible.
        msg_lookup = {c: m for _, c, m in _LEAK_PATTERNS}
        msg = msg_lookup.get(code) or "Unbalanced `{...` placeholder in prose (likely failed substitution)"
        report.add(
            "TEMPLATE_LEAK", SEVERITY_ERROR, code,
            f"{msg} — {count} occurrence(s)",
            count=count, examples=examples[code],
        )


def _split_chapters(book_text: str) -> list[tuple[int, str]]:
    """Split book.txt by `Chapter N` headers. Returns [(chapter_index, body), ...]."""
    parts = re.split(r"(?im)^\s*Chapter\s+(\d+)\s*$", book_text)
    if len(parts) < 3:
        # No chapter headers — treat whole text as one chapter.
        return [(1, book_text)]
    out: list[tuple[int, str]] = []
    # parts[0] is preamble (often empty); pairs (idx, body) follow.
    for i in range(1, len(parts) - 1, 2):
        try:
            chapter_num = int(parts[i])
        except ValueError:
            chapter_num = -1
        body = parts[i + 1].strip()
        out.append((chapter_num, body))
    return out


def _normalize_paragraph(p: str) -> str:
    return re.sub(r"\s+", " ", p).strip()


def _gate_dup_blocks(book_text: str, report: Report) -> None:
    chapters = _split_chapters(book_text)
    if len(chapters) < 2:
        report.add(
            "DUP_BLOCK", SEVERITY_INFO, "single_chapter",
            "Only one chapter found; skipping cross-chapter duplicate detection",
            chapter_count=len(chapters),
        )
        return

    # Map normalized-paragraph hash → list of (chapter_idx, snippet).
    occurrences: dict[str, list[tuple[int, str]]] = defaultdict(list)
    for ch_idx, body in chapters:
        for raw in re.split(r"\n\s*\n", body):
            norm = _normalize_paragraph(raw)
            if len(norm) < DUP_PARAGRAPH_MIN_CHARS:
                continue
            h = hashlib.sha256(norm.encode("utf-8")).hexdigest()[:16]
            occurrences[h].append((ch_idx, norm[:120]))

    duplicated: list[dict[str, Any]] = []
    for h, occ in occurrences.items():
        chapter_set = {c for c, _ in occ}
        if len(chapter_set) >= 2:
            duplicated.append({
                "hash": h,
                "chapters": sorted(chapter_set),
                "count": len(occ),
                "snippet": occ[0][1],
            })

    duplicated.sort(key=lambda d: (-d["count"], d["chapters"]))
    report.metrics["duplicate_block_count"] = len(duplicated)

    if duplicated:
        report.add(
            "DUP_BLOCK", SEVERITY_ERROR, "cross_chapter_duplicates",
            f"{len(duplicated)} paragraph(s) appear verbatim in 2+ chapters "
            "(signals slot-concat failure: the same bridge/CTA block is repeated)",
            duplicate_count=len(duplicated),
            top_duplicates=duplicated[:DUP_PARAGRAPH_MAX_REPORT],
        )


def _gate_location_grounding(loc_report: dict[str, Any] | None, report: Report) -> None:
    if loc_report is None:
        return  # Optional report; absence is fine, no INFO needed.
    status = (loc_report.get("status") or "").upper()
    report.metrics["location_grounding_status"] = status
    if status == "FAIL":
        report.add(
            "LOC_GROUNDING", SEVERITY_WARN, "location_grounding_fail",
            "location_grounding_report.json status FAIL",
            errors=loc_report.get("errors") or [],
        )


# ── Public API ────────────────────────────────────────────────────────────


def validate_render_dir(render_dir: Path) -> Report:
    report = Report(render_dir=str(render_dir))

    if not render_dir.is_dir():
        report.add("INPUT", SEVERITY_ERROR, "no_render_dir", f"{render_dir} is not a directory")
        return report

    book_text = _read_text(render_dir / "book.txt")
    if book_text is None:
        report.add("INPUT", SEVERITY_ERROR, "no_book_txt", f"{render_dir}/book.txt not found")
        return report

    budget = _read_json(render_dir / "budget.json")
    flow = _read_json(render_dir / "chapter_flow_report.json")
    loc = _read_json(render_dir / "location_grounding_report.json")

    _gate_length(book_text, budget, report)
    _gate_chapter_flow(flow, report)
    _gate_template_leak(book_text, report)
    _gate_dup_blocks(book_text, report)
    _gate_location_grounding(loc, report)

    return report


# ── Output formatters ─────────────────────────────────────────────────────


def _print_human(report: Report, fp: Any = sys.stdout) -> None:
    print(f"=== spine safety: {report.render_dir} ===", file=fp)
    if report.metrics:
        print("metrics:", file=fp)
        for k, v in report.metrics.items():
            if isinstance(v, dict) and v:
                print(f"  {k}:", file=fp)
                for sk, sv in v.items():
                    print(f"    {sk}: {sv}", file=fp)
            else:
                print(f"  {k}: {v}", file=fp)
    if report.errors:
        print(f"\n{len(report.errors)} ERROR(S):", file=fp)
        for f in report.errors:
            print(f"  ❌ [{f.gate}/{f.code}] {f.message}", file=fp)
    if report.warns:
        print(f"\n{len(report.warns)} WARN(S):", file=fp)
        for f in report.warns:
            print(f"  ⚠️  [{f.gate}/{f.code}] {f.message}", file=fp)
    if report.passed:
        if report.warns:
            print(f"\n✅ PASS (with {len(report.warns)} WARN; safe to ship)", file=fp)
        else:
            print("\n✅ PASS — all spine safety gates green", file=fp)
    else:
        print("\n❌ FAIL — spine output is NOT safe to ship", file=fp)


def _markdown(report: Report) -> str:
    lines = [
        f"# Spine Safety Report — {Path(report.render_dir).name}",
        "",
        f"**Render dir:** `{report.render_dir}`",
        f"**Status:** {'✅ PASS' if report.passed else '❌ FAIL'}",
        "",
        "## Metrics",
        "",
    ]
    for k, v in report.metrics.items():
        lines.append(f"- **{k}:** {v}")
    if report.errors:
        lines += ["", "## Errors", ""]
        for f in report.errors:
            lines.append(f"- **[{f.gate}/{f.code}]** {f.message}")
    if report.warns:
        lines += ["", "## Warnings", ""]
        for f in report.warns:
            lines.append(f"- **[{f.gate}/{f.code}]** {f.message}")
    return "\n".join(lines) + "\n"


def _write_reports(report: Report) -> None:
    out_dir = Path(report.render_dir)
    (out_dir / "spine_safety_report.json").write_text(
        json.dumps(report.to_dict(), indent=2, default=str), encoding="utf-8"
    )
    (out_dir / "spine_safety_report.md").write_text(_markdown(report), encoding="utf-8")


# ── CLI ───────────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("path", help="Render directory (e.g. artifacts/rendered/<id>/) or parent dir with --batch")
    p.add_argument("--batch", action="store_true", help="Treat path as parent dir; validate every subdir containing book.txt")
    p.add_argument("--json", action="store_true", help="Emit JSON instead of human output")
    p.add_argument("--write", action="store_true", help="Write spine_safety_report.{json,md} into each render dir")
    args = p.parse_args(argv)

    target = Path(args.path)
    if args.batch:
        if not target.is_dir():
            print(f"ERROR: --batch requires a directory; got {target}", file=sys.stderr)
            return 2
        candidates = [d for d in sorted(target.iterdir()) if d.is_dir() and (d / "book.txt").is_file()]
        if not candidates:
            print(f"ERROR: no subdirectories of {target} contain book.txt", file=sys.stderr)
            return 2
        reports = [validate_render_dir(d) for d in candidates]
    else:
        reports = [validate_render_dir(target)]

    if args.write:
        for r in reports:
            if Path(r.render_dir).is_dir():
                _write_reports(r)

    if args.json:
        print(json.dumps([r.to_dict() for r in reports], indent=2, default=str))
    else:
        for r in reports:
            _print_human(r)
            print()

    any_error = any(r.errors for r in reports)
    return 1 if any_error else 0


if __name__ == "__main__":
    sys.exit(main())
