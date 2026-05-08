"""Whole-book quality gate for rendered Phoenix manuscripts.

This gate is intentionally deterministic. It does not claim a book is a
commercial bestseller; it catches release-blocking assembly failures that make a
manuscript unfit to call bestseller-ready.
"""
from __future__ import annotations

import json
import re
import yaml as _yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from phoenix_v4.quality.chapter_flow_gate import evaluate_chapter_flow, flow_profile_for_runtime_format

_OVERLAY_RULE_IDS = frozenset(
    {
        "none",
        "density_ceiling",
        "presence_floor",
        "drift_detection",
        "absence_guard",
    }
)


def _normalize_overlay_fields(entry: dict) -> None:
    raw = entry.get("overlay_rule")
    rule_id = str(raw).strip().lower() if raw is not None else "none"
    if rule_id not in _OVERLAY_RULE_IDS:
        rule_id = "none"
    entry["overlay_rule"] = rule_id
    op = entry.get("overlay_param")
    if op is None or not isinstance(op, dict):
        entry["overlay_param"] = {}


def _load_refrain_allowlist() -> dict[str, dict]:
    """Return phrase -> entry dict (longest-match-wins via iteration order).

    Phrases are stored lower-cased and sorted longest-first so the lookup loop
    can short-circuit on the first (longest) match.  If the YAML is missing or
    malformed, returns an empty dict so the gate degrades to the plain >12 cap.
    """
    path = Path(__file__).resolve().parents[2] / "config" / "quality" / "refrain_allowlist.yaml"
    try:
        data = _yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}
    result: dict[str, dict] = {}
    for entry in data.get("entries", []):
        phrase = (entry.get("phrase") or "").strip().lower()
        if not phrase:
            continue
        # Require at least cap_book_wide to be present; skip malformed entries.
        if "cap_book_wide" not in entry:
            continue
        _normalize_overlay_fields(entry)
        result[phrase] = entry
    # Sort longest-first so the matching loop finds the most-specific entry first.
    return dict(sorted(result.items(), key=lambda kv: -len(kv[0])))


_REFRAIN_ALLOWLIST: dict[str, dict] = _load_refrain_allowlist()


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


def _tokenize_book_words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9']+", (text or "").lower())


def _count_word_phrase_occurrences(norm_words: list[str], phrase_lc: str) -> int:
    needle = phrase_lc.strip().lower().split()
    if not needle:
        return 0
    nlen = len(needle)
    c = 0
    for i in range(0, max(0, len(norm_words) - nlen + 1)):
        if norm_words[i : i + nlen] == needle:
            c += 1
    return c


def _indices_for_overlay_class(class_name: str, total_chapters: int, compression_chapters_1based: frozenset[int]) -> frozenset[int]:
    tn = total_chapters
    if tn < 1:
        return frozenset()
    if class_name == "opening":
        return frozenset({1}) if tn >= 1 else frozenset()
    if class_name == "mid":
        return frozenset({i for i in range(4, 9) if i <= tn})
    if class_name == "climax":
        return frozenset({i for i in (9, 10) if i <= tn})
    if class_name == "compression_chapters":
        return frozenset({i for i in compression_chapters_1based if 1 <= i <= tn})
    return frozenset()


def _chapter_word_lists(chapters: list[str]) -> list[list[str]]:
    return [_tokenize_book_words(ch) for ch in chapters]


def _runtime_word_range(runtime_format_id: str) -> Optional[tuple[int, int]]:
    try:
        from phoenix_v4.rendering.book_renderer import _runtime_word_range as _book_renderer_runtime_word_range

        return _book_renderer_runtime_word_range(runtime_format_id)
    except Exception:
        return None


def _match_allowlist_entry(phrase: str, allowlist: dict[str, dict]) -> dict | None:
    """Return the allowlist entry whose key is a prefix of *phrase*, or None.

    The allowlist is pre-sorted longest-first so the first match found is the
    most specific (longest-match-wins).
    """
    for key, entry in allowlist.items():
        if phrase.startswith(key):
            return entry
    return None


def _overlay_violations(
    *,
    chapters_tokenized: list[list[str]],
    allowlist: dict[str, dict],
    compression_chapters_1based: frozenset[int],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    n_ch = len(chapters_tokenized)
    for phrase_key, entry in allowlist.items():
        rule_kind = entry.get("overlay_rule") or "none"
        if rule_kind == "none":
            continue
        canonical = entry.get("phrase") or phrase_key
        param = entry.get("overlay_param") or {}

        if rule_kind == "density_ceiling":
            ceiling_n_raw = param.get("N", entry.get("cap_per_chapter", 2))
            try:
                ceiling_n = int(ceiling_n_raw)
            except (TypeError, ValueError):
                ceiling_n = 2
            for idx, words in enumerate(chapters_tokenized, start=1):
                c_here = _count_word_phrase_occurrences(words, phrase_key)
                if c_here > ceiling_n:
                    out.append({
                        "phrase": phrase_key,
                        "count": c_here,
                        "chapter": idx,
                        "matched_allowlist_entry": canonical,
                        "cap_applied": None,
                        "per_chapter_limit": ceiling_n,
                        "rule_fired": "overlay",
                        "overlay_rule_kind": "density_ceiling",
                        "rule": "overlay:density_ceiling",
                    })

        if rule_kind == "drift_detection":
            thr_raw = param.get("drift_threshold", 3)
            try:
                drift_thr = int(thr_raw)
            except (TypeError, ValueError):
                drift_thr = 3
            for idx, words in enumerate(chapters_tokenized, start=1):
                c_here = _count_word_phrase_occurrences(words, phrase_key)
                if c_here >= drift_thr:
                    out.append({
                        "phrase": phrase_key,
                        "count": c_here,
                        "chapter": idx,
                        "matched_allowlist_entry": canonical,
                        "cap_applied": None,
                        "drift_threshold": drift_thr,
                        "rule_fired": "overlay",
                        "overlay_rule_kind": "drift_detection",
                        "rule": "overlay:drift_detection",
                    })

        if rule_kind == "presence_floor":
            classes_raw = param.get("structural_chapters")
            structural = list(classes_raw) if isinstance(classes_raw, list) else ["opening", "mid", "climax"]
            for cls in structural:
                cls_norm = str(cls).strip().lower()
                indices = sorted(_indices_for_overlay_class(cls_norm, n_ch, compression_chapters_1based))
                if not indices:
                    continue
                hits_any = False
                for ch_i in indices:
                    cw = chapters_tokenized[ch_i - 1]
                    if _count_word_phrase_occurrences(cw, phrase_key) >= 1:
                        hits_any = True
                        break
                if not hits_any:
                    out.append({
                        "phrase": phrase_key,
                        "count": 0,
                        "chapter": None,
                        "matched_allowlist_entry": canonical,
                        "cap_applied": None,
                        "structural_class": cls_norm,
                        "rule_fired": "overlay",
                        "overlay_rule_kind": "presence_floor",
                        "rule": "overlay:presence_floor",
                    })

        if rule_kind == "absence_guard":
            excluded_raw = param.get("excluded_chapter_classes")
            excluded_list = list(excluded_raw) if isinstance(excluded_raw, list) else []
            if not excluded_list:
                continue
            for cls in excluded_list:
                cls_norm = str(cls).strip().lower()
                ex_indices = sorted(_indices_for_overlay_class(cls_norm, n_ch, compression_chapters_1based))
                for ch_i in ex_indices:
                    cw = chapters_tokenized[ch_i - 1]
                    presence = _count_word_phrase_occurrences(cw, phrase_key)
                    if presence >= 1:
                        out.append({
                            "phrase": phrase_key,
                            "count": presence,
                            "chapter": ch_i,
                            "matched_allowlist_entry": canonical,
                            "cap_applied": None,
                            "excluded_class": cls_norm,
                            "rule_fired": "overlay",
                            "overlay_rule_kind": "absence_guard",
                            "rule": "overlay:absence_guard",
                        })

    return out


def _repeated_phrase_violations(
    text: str,
    *,
    cap: int = 12,
    allowlist: Optional[dict[str, dict]] = None,
    chapter_texts: Optional[list[str]] = None,
    compression_chapters_1based: Optional[set[int]] = None,
) -> list[dict[str, Any]]:
    """Return n-grams (n=4,5,6) book-wide offenses plus overlay violations.

    Overlay rules fire only when an allowlist entry has ``overlay_rule`` other than
    ``none``. Violation dicts include ``rule_fired`` (`book_wide_cap` or `overlay`),
    ``rule`` (matching PER-CHAPTER overlay spec shorthand), plus prior keys.
    """
    if allowlist is not None:
        alist_norm: dict[str, dict] = {}
        for k, ent in allowlist.items():
            ecopy = dict(ent)
            _normalize_overlay_fields(ecopy)
            key = str(k).strip().lower()
            if key:
                alist_norm[key] = ecopy
        alist = dict(sorted(alist_norm.items(), key=lambda kv: -len(kv[0])))
    else:
        alist = _REFRAIN_ALLOWLIST
    ch_texts = chapter_texts if chapter_texts is not None else _extract_chapters(text)
    comp_ch = frozenset(compression_chapters_1based or ())

    words = _tokenize_book_words(text)
    counts: dict[str, int] = {}
    for n in (4, 5, 6):
        for i in range(0, max(0, len(words) - n + 1)):
            phrase = " ".join(words[i : i + n])
            counts[phrase] = counts.get(phrase, 0) + 1

    offenders_bw: list[dict[str, Any]] = []
    for phrase, count in counts.items():
        entry = _match_allowlist_entry(phrase, alist)
        effective_cap = int(entry["cap_book_wide"]) if entry is not None else cap
        if count > effective_cap:
            offenders_bw.append({
                "phrase": phrase,
                "count": count,
                "chapter": None,
                "matched_allowlist_entry": entry.get("phrase") if entry is not None else None,
                "cap_applied": effective_cap,
                "rule_fired": "book_wide_cap",
                "rule": "book_wide_cap",
            })

    offenders_bw.sort(key=lambda x: (-int(x["count"]), str(x["phrase"])))
    offenders_bw = offenders_bw[:20]

    ch_words = _chapter_word_lists(ch_texts)
    offenders_ov = _overlay_violations(
        chapters_tokenized=ch_words,
        allowlist=alist,
        compression_chapters_1based=comp_ch,
    )
    offenders_ov.sort(key=lambda x: (-int(x["count"]), str(x["phrase"]), int(x.get("chapter") or 0)))

    combined = offenders_bw + offenders_ov
    combined.sort(
        key=lambda x: (-int(x["count"]), str(x["phrase"]), int(x.get("chapter") or 0)),
    )
    return combined[:40]


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
