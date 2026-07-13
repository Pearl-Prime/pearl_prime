#!/usr/bin/env python3
"""Repo-wide Phoenix atom-bank health audit.

Scans every ``atoms/<persona>/<topic>/**/CANONICAL.txt`` and every matching
``config/source_of_truth/master_arcs/*.yaml``. Produces:

- atom_bank_health.tsv
- tuple_health_summary.md
- writer_backlog.md
- high_risk_tuples.json

Health is deliberately stronger than parse success:
- placeholder blocks never count as usable;
- line-level placeholder debt is reported even inside otherwise real prose;
- STORY/engine band coverage is matched to each master arc;
- HOOK depth, engine depth, thin prose, and likely extended_book_2h source
  capacity are evaluated separately;
- locale presence never hides a shallow base-English bank.

This is a preflight risk audit, not a substitute for full production gates.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import statistics
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required: python3 -m pip install pyyaml") from exc


SCHEMA_VERSION = "1.0.0"
DEFAULT_ARTIFACT_ROOT = Path("artifacts/qa/atom_bank_health_20260714")
CANONICAL_NAME = "CANONICAL.txt"

# Explicit requested thresholds.
THIN_ATOM_WORDS = 40
HOOK_MIN_USABLE = 12

# Advisory preflight thresholds. These are intentionally named and emitted in
# reports so they cannot masquerade as hidden bestseller science.
ENGINE_MIN_USABLE = 15
ENGINE_MIN_PER_REQUIRED_BAND = 2
ENGINE_TARGET_WORDS_PER_ARC_CHAPTER = 115
TUPLE_TARGET_WORDS_PER_ARC_CHAPTER = 330
THIN_RATIO_HIGH_RISK = 0.35

SLOT_TARGETS: dict[str, dict[str, int]] = {
    "HOOK": {"min_atoms": HOOK_MIN_USABLE, "target_words_per_atom": 60},
    "STORY": {"min_atoms": 12, "target_words_per_atom": 140},
    "SCENE": {"min_atoms": 12, "target_words_per_atom": 100},
    "REFLECTION": {"min_atoms": 12, "target_words_per_atom": 65},
    "EXERCISE": {"min_atoms": 12, "target_words_per_atom": 120},
    "INTEGRATION": {"min_atoms": 12, "target_words_per_atom": 90},
    "TRANSITION": {"min_atoms": 12, "target_words_per_atom": 55},
    "COMPRESSION": {"min_atoms": 12, "target_words_per_atom": 70},
    "PIVOT": {"min_atoms": 8, "target_words_per_atom": 75},
    "TAKEAWAY": {"min_atoms": 8, "target_words_per_atom": 55},
    "THREAD": {"min_atoms": 8, "target_words_per_atom": 55},
    "PERMISSION": {"min_atoms": 8, "target_words_per_atom": 55},
}
DEFAULT_SLOT_TARGET = {"min_atoms": 8, "target_words_per_atom": 80}

ROLE_LIKE_FAMILIES = frozenset(SLOT_TARGETS)
LOCALE_DIR_NAMES = frozenset({"locales", "locale"})

WORD_RE = re.compile(r"\b[\w’'-]+\b", re.UNICODE)
HEADER_RE = re.compile(
    r"(?m)^##\s+(?P<label>[A-Za-z0-9_:-]+)\s+v(?P<version>\d+)\s*$"
)
KEY_VALUE_RE = re.compile(
    r"^(?P<key>[A-Za-z_][A-Za-z0-9_ -]{0,60})\s*:\s*(?P<value>.*?)\s*$"
)
BAND_RE = re.compile(r"^(?:BAND|band)\s*:\s*([1-5])\s*$", re.MULTILINE)

# Mirrors the hardened runtime's placeholder intent while retaining line-level
# accounting for embedded unresolved editorial markers.
LEGIT_BRACKET_RE = re.compile(
    r"^(?:"
    r"\[sic\]"
    r"|\[emphasis added\]"
    r"|\[ibid\.?\]"
    r"|\[\d+\]"
    r"|\[[A-Z][A-Za-z]+(?:\s+et\s+al\.?)?,?\s+\d{4}\]"
    r")$",
    re.IGNORECASE,
)
BRACKET_STUB_RE = re.compile(
    r"\[[^\]]*\b(?:"
    r"persona-specific|hook for|placeholder|missing|silence|tbd|tktk|todo|"
    r"insert|specific|draft|write here|fill(?:\s+this)?|stub"
    r")\b[^\]]*\]",
    re.IGNORECASE,
)
BARE_ELLIPSIS_RE = re.compile(r"^\[\s*(?:\.\.\.|…)\s*\]$")
BARE_VAR_RE = re.compile(
    r"^(?:\{\{[A-Za-z_]\w*\}\}|\{[A-Za-z_]\w*\}|%\([A-Za-z_]\w*\)s)$"
)
EDITORIAL_LINE_RE = re.compile(
    r"^\s*(?:TODO|TBD|TKTK|PLACEHOLDER|MISSING|DRAFT|STUB)\b",
    re.IGNORECASE,
)
LOW_INFORMATION_BODY_RE = re.compile(
    r"^(?:"
    r"crisis\.?\s*breakthrough\.?\s*the moment of maximum intensity\.?"
    r"|the mechanism deepens\.?\s*stakes rise\.?\s*the cost becomes clear\.?"
    r"|opening hook\.?"
    r"|story goes here\.?"
    r"|reflection question\.?"
    r")$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class AtomBlock:
    label: str
    version: int
    metadata: dict[str, str]
    body: str
    raw_text: str
    parse_ok: bool
    placeholder: bool
    placeholder_line_count: int
    word_count: int
    band: int | None
    low_information: bool


@dataclass
class BankHealth:
    path: str
    persona: str
    topic: str
    family: str
    family_kind: str
    locale: str
    parse_ok: bool
    parsed_atom_count: int
    usable_atom_count: int
    placeholder_atom_count: int
    placeholder_line_count: int
    low_information_atom_count: int
    duplicate_atom_id_count: int
    duplicate_atom_ids: list[str]
    total_source_words: int
    median_words_per_atom: float
    thin_atom_count: int
    thin_atom_ratio: float
    bands_present: list[int]
    bands_missing_1_5: list[int]
    arc_ids: list[str] = field(default_factory=list)
    required_arc_bands: list[int] = field(default_factory=list)
    required_arc_bands_missing: list[int] = field(default_factory=list)
    min_required_band_depth: int = 0
    hook_depth_risk: bool = False
    engine_depth_risk: bool = False
    likely_extended_book_2h_word_budget_risk: bool = False
    locale_base_english_shallow_risk: bool = False
    exact_writer_target_added_words: int = 0
    risk_reasons: list[str] = field(default_factory=list)
    healthy: bool = False

    def to_tsv_row(self) -> dict[str, Any]:
        return {
            "persona": self.persona,
            "topic": self.topic,
            "family": self.family,
            "family_kind": self.family_kind,
            "locale": self.locale,
            "path": self.path,
            "parse_ok": str(self.parse_ok).lower(),
            "parsed_atom_count": self.parsed_atom_count,
            "usable_atom_count": self.usable_atom_count,
            "placeholder_atom_count": self.placeholder_atom_count,
            "placeholder_line_count": self.placeholder_line_count,
            "low_information_atom_count": self.low_information_atom_count,
            "duplicate_atom_id_count": self.duplicate_atom_id_count,
            "duplicate_atom_ids": ",".join(self.duplicate_atom_ids),
            "total_source_words": self.total_source_words,
            "median_words_per_atom": f"{self.median_words_per_atom:.1f}",
            "thin_atom_count_under_40_words": self.thin_atom_count,
            "thin_atom_ratio": f"{self.thin_atom_ratio:.3f}",
            "bands_present": _join_ints(self.bands_present),
            "bands_missing_1_5": _join_ints(self.bands_missing_1_5),
            "matching_arc_ids": ",".join(self.arc_ids),
            "required_arc_bands": _join_ints(self.required_arc_bands),
            "required_arc_bands_missing": _join_ints(
                self.required_arc_bands_missing
            ),
            "min_required_band_depth": self.min_required_band_depth,
            "hook_depth_risk": str(self.hook_depth_risk).lower(),
            "engine_depth_risk": str(self.engine_depth_risk).lower(),
            "likely_extended_book_2h_word_budget_risk": str(
                self.likely_extended_book_2h_word_budget_risk
            ).lower(),
            "locale_base_english_shallow_risk": str(
                self.locale_base_english_shallow_risk
            ).lower(),
            "target_added_words": self.exact_writer_target_added_words,
            "healthy": str(self.healthy).lower(),
            "risk_reasons": " | ".join(self.risk_reasons),
        }


@dataclass(frozen=True)
class ArcSpec:
    path: str
    arc_id: str
    persona: str
    topic: str
    engine: str
    chapter_count: int
    required_bands: tuple[int, ...]
    parse_ok: bool
    error: str = ""


def _join_ints(values: Iterable[int]) -> str:
    return ",".join(str(value) for value in sorted(set(values)))


def _word_count(text: str) -> int:
    return len(WORD_RE.findall(text or ""))


def _strip_fences(text: str) -> str:
    lines = (text or "").splitlines()
    while lines and lines[0].strip() in {"", "---"}:
        lines.pop(0)
    while lines and lines[-1].strip() in {"", "---"}:
        lines.pop()
    return "\n".join(lines).strip()


def _looks_like_metadata(text: str) -> bool:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return False
    keylike = [line for line in lines if KEY_VALUE_RE.match(line)]
    return len(keylike) >= 1 and len(keylike) / len(lines) >= 0.6


def _parse_metadata(text: str) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for line in text.splitlines():
        match = KEY_VALUE_RE.match(line.strip())
        if not match:
            continue
        metadata[match.group("key").strip()] = match.group("value").strip()
    return metadata


def _placeholder_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if LEGIT_BRACKET_RE.match(stripped):
        return False
    return bool(
        BRACKET_STUB_RE.search(stripped)
        or BARE_ELLIPSIS_RE.match(stripped)
        or BARE_VAR_RE.match(stripped)
        or EDITORIAL_LINE_RE.match(stripped)
    )


def _is_placeholder_body(body: str) -> bool:
    stripped = _strip_fences(body)
    if not stripped:
        return True
    if LEGIT_BRACKET_RE.match(stripped):
        return False
    if BARE_ELLIPSIS_RE.match(stripped) or BARE_VAR_RE.match(stripped):
        return True
    lines = [line for line in stripped.splitlines() if line.strip()]
    if lines and all(_placeholder_line(line) for line in lines):
        return True
    residue = BRACKET_STUB_RE.sub("", stripped)
    if BRACKET_STUB_RE.search(stripped) and not residue.strip():
        return True
    if LOW_INFORMATION_BODY_RE.match(" ".join(stripped.split())):
        return True
    return False


def _split_header_payload(payload: str) -> tuple[dict[str, str], str, bool]:
    """Parse metadata/body after a header.

    Canonical files usually encode:
      header
      ---
      metadata (possibly empty)
      ---
      prose
      ---

    Some slot files encode:
      header
      ---
      prose
      ---

    This parser accepts both and marks malformed ambiguity via parse_ok=False.
    """
    payload = payload.strip()
    if not payload:
        return {}, "", False

    chunks = re.split(r"(?m)^\s*---\s*$", payload)
    chunks = [chunk.strip() for chunk in chunks]
    while chunks and chunks[0] == "":
        chunks.pop(0)
    while chunks and chunks[-1] == "":
        chunks.pop()

    if not chunks:
        return {}, "", False
    if len(chunks) == 1:
        chunk = _strip_fences(chunks[0])
        return {}, chunk, bool(chunk)

    first = chunks[0]
    if _looks_like_metadata(first):
        metadata = _parse_metadata(first)
        body = _strip_fences("\n---\n".join(chunks[1:]))
        return metadata, body, bool(body)

    # Empty metadata often leaves prose as the second chunk after normalization.
    if first == "":
        body = _strip_fences("\n---\n".join(chunks[1:]))
        return {}, body, bool(body)

    # Non-story block with prose immediately after first fence.
    body = _strip_fences("\n---\n".join(chunks))
    return {}, body, bool(body)


def parse_canonical_text(text: str) -> tuple[list[AtomBlock], list[str]]:
    headers = list(HEADER_RE.finditer(text))
    errors: list[str] = []
    if not headers:
        return [], ["no_atom_headers"]

    blocks: list[AtomBlock] = []
    for index, header in enumerate(headers):
        start = header.end()
        end = headers[index + 1].start() if index + 1 < len(headers) else len(text)
        payload = text[start:end]
        metadata, body, parse_ok = _split_header_payload(payload)
        if not parse_ok:
            errors.append(
                f"empty_or_malformed_body:{header.group('label')}:v"
                f"{header.group('version')}"
            )
        placeholder_lines = sum(
            1 for line in body.splitlines() if _placeholder_line(line)
        )
        placeholder = _is_placeholder_body(body)
        low_information = bool(
            body and LOW_INFORMATION_BODY_RE.match(" ".join(body.split()))
        )
        band_value: int | None = None
        for key, value in metadata.items():
            if key.strip().upper() == "BAND":
                try:
                    parsed = int(value)
                except ValueError:
                    errors.append(
                        f"invalid_band:{header.group('label')}:v"
                        f"{header.group('version')}:{value}"
                    )
                    break
                if 1 <= parsed <= 5:
                    band_value = parsed
                else:
                    errors.append(
                        f"out_of_range_band:{header.group('label')}:v"
                        f"{header.group('version')}:{parsed}"
                    )
                break

        blocks.append(
            AtomBlock(
                label=header.group("label"),
                version=int(header.group("version")),
                metadata=metadata,
                body=body,
                raw_text=text[header.start():end],
                parse_ok=parse_ok,
                placeholder=placeholder,
                placeholder_line_count=placeholder_lines,
                word_count=_word_count(body),
                band=band_value,
                low_information=low_information,
            )
        )
    return blocks, errors


def _path_identity(path: Path, atoms_root: Path) -> tuple[str, str, str, str]:
    rel = path.relative_to(atoms_root)
    parts = rel.parts
    if len(parts) < 4 or parts[-1] != CANONICAL_NAME:
        raise ValueError(f"unexpected atom path shape: {rel}")

    persona, topic = parts[0], parts[1]
    middle = list(parts[2:-1])
    locale = "en-US"

    if "locales" in middle:
        idx = middle.index("locales")
        if idx + 1 >= len(middle):
            raise ValueError(f"locale directory missing locale slug: {rel}")
        locale = middle[idx + 1]
        family_parts = middle[:idx]
    elif "locale" in middle:
        idx = middle.index("locale")
        if idx + 1 >= len(middle):
            raise ValueError(f"locale directory missing locale slug: {rel}")
        locale = middle[idx + 1]
        family_parts = middle[:idx]
    else:
        family_parts = middle

    family = "/".join(family_parts) if family_parts else "<root>"
    top = family_parts[0].upper() if family_parts else "<ROOT>"
    family_kind = "slot" if top in ROLE_LIKE_FAMILIES else "engine"
    return persona, topic, family, locale, family_kind


def load_arcs(repo_root: Path) -> tuple[list[ArcSpec], list[dict[str, str]]]:
    arc_root = repo_root / "config/source_of_truth/master_arcs"
    arcs: list[ArcSpec] = []
    errors: list[dict[str, str]] = []
    if not arc_root.is_dir():
        return arcs, [{"path": str(arc_root), "error": "master_arc_root_missing"}]

    for path in sorted(arc_root.glob("*.yaml")):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            curve = data.get("emotional_curve") or []
            required_bands = sorted(
                {
                    int(value)
                    for value in curve
                    if isinstance(value, (int, float, str))
                    and str(value).strip().isdigit()
                    and 1 <= int(value) <= 5
                }
            )
            persona = str(data.get("persona") or "").strip()
            topic = str(data.get("topic") or "").strip()
            engine = str(data.get("engine") or "").strip()
            arc_id = str(data.get("arc_id") or path.stem).strip()
            chapter_count = int(
                data.get("chapter_count") or len(curve) or 0
            )
            parse_ok = bool(
                persona
                and topic
                and engine
                and chapter_count > 0
                and required_bands
            )
            error = "" if parse_ok else "missing_identity_chapters_or_bands"
            arcs.append(
                ArcSpec(
                    path=str(path.relative_to(repo_root)),
                    arc_id=arc_id,
                    persona=persona,
                    topic=topic,
                    engine=engine,
                    chapter_count=chapter_count,
                    required_bands=tuple(required_bands),
                    parse_ok=parse_ok,
                    error=error,
                )
            )
            if not parse_ok:
                errors.append(
                    {
                        "path": str(path.relative_to(repo_root)),
                        "error": error,
                    }
                )
        except Exception as exc:  # noqa: BLE001
            errors.append(
                {
                    "path": str(path.relative_to(repo_root)),
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
    return arcs, errors


def _slot_target(family: str, family_kind: str) -> dict[str, int]:
    top = family.split("/", 1)[0].upper()
    if family_kind == "engine":
        return {
            "min_atoms": ENGINE_MIN_USABLE,
            "target_words_per_atom": 125,
        }
    return SLOT_TARGETS.get(top, DEFAULT_SLOT_TARGET)


def _target_added_words(
    *,
    family: str,
    family_kind: str,
    usable_words: Sequence[int],
    usable_count: int,
    required_bands: Sequence[int],
    band_counts: Mapping[int, int],
) -> int:
    target = _slot_target(family, family_kind)
    min_atoms = target["min_atoms"]
    target_words = target["target_words_per_atom"]
    missing_atoms = max(0, min_atoms - usable_count)
    add_for_missing = missing_atoms * target_words

    add_for_thin = sum(
        max(0, THIN_ATOM_WORDS - count)
        for count in usable_words
        if count < THIN_ATOM_WORDS
    )

    add_for_band_depth = 0
    if family_kind == "engine":
        for band in required_bands:
            deficit = max(
                0,
                ENGINE_MIN_PER_REQUIRED_BAND - int(band_counts.get(band, 0)),
            )
            add_for_band_depth += deficit * target_words

    # Avoid double-counting the same missing atoms twice. The larger authored
    # requirement controls, plus direct thin-atom top-ups.
    return max(add_for_missing, add_for_band_depth) + add_for_thin


def scan_banks(repo_root: Path, arcs: Sequence[ArcSpec]) -> tuple[
    list[BankHealth],
    list[dict[str, str]],
]:
    atoms_root = repo_root / "atoms"
    if not atoms_root.is_dir():
        raise FileNotFoundError(f"atoms root missing: {atoms_root}")

    arc_index: dict[tuple[str, str, str], list[ArcSpec]] = defaultdict(list)
    for arc in arcs:
        if arc.parse_ok:
            arc_index[(arc.persona, arc.topic, arc.engine)].append(arc)

    banks: list[BankHealth] = []
    scan_errors: list[dict[str, str]] = []

    for path in sorted(atoms_root.rglob(CANONICAL_NAME)):
        try:
            persona, topic, family, locale, family_kind = _path_identity(
                path, atoms_root
            )
            text = path.read_text(encoding="utf-8")
            blocks, parse_errors = parse_canonical_text(text)
            id_counts: Counter[str] = Counter(
                f"{block.label}_v{block.version:02d}" for block in blocks
            )
            duplicate_ids = sorted(
                atom_id for atom_id, count in id_counts.items() if count > 1
            )
            usable = [
                block
                for block in blocks
                if block.parse_ok and not block.placeholder
            ]
            placeholders = [block for block in blocks if block.placeholder]
            usable_words = [block.word_count for block in usable]
            thin = [
                block
                for block in usable
                if block.word_count < THIN_ATOM_WORDS
            ]
            bands_present = sorted(
                {
                    block.band
                    for block in usable
                    if block.band is not None
                }
            )
            band_counts = Counter(
                block.band
                for block in usable
                if block.band is not None
            )

            matching_arcs = (
                arc_index.get((persona, topic, family), [])
                if family_kind == "engine" and locale == "en-US"
                else []
            )
            required_bands = sorted(
                {
                    band
                    for arc in matching_arcs
                    for band in arc.required_bands
                }
            )
            required_missing = sorted(set(required_bands) - set(bands_present))
            min_required_band_depth = (
                min((band_counts.get(band, 0) for band in required_bands), default=0)
            )

            top_family = family.split("/", 1)[0].upper()
            hook_risk = (
                top_family == "HOOK"
                and len(usable) < HOOK_MIN_USABLE
            )
            engine_risk = (
                family_kind == "engine"
                and (
                    len(usable) < ENGINE_MIN_USABLE
                    or bool(required_missing)
                    or (
                        bool(required_bands)
                        and min_required_band_depth
                        < ENGINE_MIN_PER_REQUIRED_BAND
                    )
                )
            )

            arc_chapters = max(
                (arc.chapter_count for arc in matching_arcs),
                default=0,
            )
            engine_word_capacity_risk = (
                family_kind == "engine"
                and bool(matching_arcs)
                and (
                    sum(usable_words)
                    < arc_chapters * ENGINE_TARGET_WORDS_PER_ARC_CHAPTER
                    or len(usable) < max(
                        ENGINE_MIN_USABLE,
                        math.ceil(arc_chapters * 0.75),
                    )
                )
            )
            thin_ratio = len(thin) / max(len(usable), 1)
            likely_budget_risk = bool(
                engine_word_capacity_risk
                or (
                    family_kind == "engine"
                    and bool(matching_arcs)
                    and thin_ratio >= THIN_RATIO_HIGH_RISK
                )
            )

            reasons: list[str] = []
            if parse_errors:
                reasons.append("parse_errors:" + ",".join(parse_errors[:8]))
            if duplicate_ids:
                reasons.append("duplicate_atom_ids=" + ",".join(duplicate_ids))
            if placeholders:
                reasons.append(
                    f"placeholder_atoms={len(placeholders)}"
                )
            placeholder_lines = sum(
                block.placeholder_line_count for block in blocks
            )
            if placeholder_lines:
                reasons.append(
                    f"placeholder_lines={placeholder_lines}"
                )
            low_information_count = sum(
                1 for block in blocks if block.low_information
            )
            if low_information_count:
                reasons.append(
                    f"low_information_atoms={low_information_count}"
                )
            if hook_risk:
                reasons.append(
                    f"HOOK_real_depth={len(usable)}<{HOOK_MIN_USABLE}"
                )
            if engine_risk:
                reasons.append(
                    f"engine_depth_or_band_deficit:usable={len(usable)};"
                    f"missing_bands={_join_ints(required_missing) or 'none'};"
                    f"min_band_depth={min_required_band_depth}"
                )
            if likely_budget_risk:
                reasons.append(
                    "likely_extended_book_2h_word_budget_risk"
                )
            if thin:
                reasons.append(
                    f"thin_atoms_under_{THIN_ATOM_WORDS}={len(thin)}"
                )

            parse_ok = bool(blocks) and not parse_errors
            target_words = _target_added_words(
                family=family,
                family_kind=family_kind,
                usable_words=usable_words,
                usable_count=len(usable),
                required_bands=required_bands,
                band_counts=band_counts,
            )

            bank = BankHealth(
                path=str(path.relative_to(repo_root)),
                persona=persona,
                topic=topic,
                family=family,
                family_kind=family_kind,
                locale=locale,
                parse_ok=parse_ok,
                parsed_atom_count=len(blocks),
                usable_atom_count=len(usable),
                placeholder_atom_count=len(placeholders),
                placeholder_line_count=placeholder_lines,
                low_information_atom_count=low_information_count,
                duplicate_atom_id_count=len(duplicate_ids),
                duplicate_atom_ids=duplicate_ids,
                total_source_words=sum(usable_words),
                median_words_per_atom=(
                    float(statistics.median(usable_words))
                    if usable_words
                    else 0.0
                ),
                thin_atom_count=len(thin),
                thin_atom_ratio=thin_ratio,
                bands_present=bands_present,
                bands_missing_1_5=sorted(
                    set(range(1, 6)) - set(bands_present)
                )
                if bands_present or family_kind == "engine"
                else [],
                arc_ids=[arc.arc_id for arc in matching_arcs],
                required_arc_bands=required_bands,
                required_arc_bands_missing=required_missing,
                min_required_band_depth=min_required_band_depth,
                hook_depth_risk=hook_risk,
                engine_depth_risk=engine_risk,
                likely_extended_book_2h_word_budget_risk=likely_budget_risk,
                exact_writer_target_added_words=target_words,
                risk_reasons=reasons,
            )
            banks.append(bank)
        except Exception as exc:  # noqa: BLE001
            rel = (
                str(path.relative_to(repo_root))
                if path.is_relative_to(repo_root)
                else str(path)
            )
            scan_errors.append(
                {
                    "path": rel,
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )

    # Locale/base-English cross-check.
    by_identity = {
        (bank.persona, bank.topic, bank.family, bank.locale): bank
        for bank in banks
    }
    for bank in banks:
        if bank.locale == "en-US":
            continue
        base = by_identity.get(
            (bank.persona, bank.topic, bank.family, "en-US")
        )
        if base is None:
            bank.locale_base_english_shallow_risk = True
            bank.risk_reasons.append("locale_exists_base_english_missing")
            continue
        shallow = bool(
            not base.parse_ok
            or base.hook_depth_risk
            or base.engine_depth_risk
            or base.usable_atom_count
            < _slot_target(base.family, base.family_kind)["min_atoms"]
            or base.placeholder_atom_count > 0
        )
        if shallow:
            bank.locale_base_english_shallow_risk = True
            bank.risk_reasons.append(
                f"locale_exists_base_english_shallow:{base.path}"
            )

    for bank in banks:
        bank.healthy = bool(
            bank.parse_ok
            and bank.usable_atom_count > 0
            and bank.placeholder_atom_count == 0
            and bank.placeholder_line_count == 0
            and bank.low_information_atom_count == 0
            and bank.duplicate_atom_id_count == 0
            and not bank.hook_depth_risk
            and not bank.engine_depth_risk
            and not bank.likely_extended_book_2h_word_budget_risk
            and not bank.locale_base_english_shallow_risk
            and bank.thin_atom_ratio < THIN_RATIO_HIGH_RISK
        )
    return banks, scan_errors


def _base_banks(
    banks: Sequence[BankHealth],
) -> dict[tuple[str, str, str], BankHealth]:
    return {
        (bank.persona, bank.topic, bank.family): bank
        for bank in banks
        if bank.locale == "en-US"
    }


def build_tuple_matrix(
    banks: Sequence[BankHealth],
    arcs: Sequence[ArcSpec],
) -> list[dict[str, Any]]:
    base = _base_banks(banks)
    topic_slots: dict[tuple[str, str], list[BankHealth]] = defaultdict(list)
    for bank in banks:
        if bank.locale == "en-US":
            topic_slots[(bank.persona, bank.topic)].append(bank)

    rows: list[dict[str, Any]] = []
    for arc in arcs:
        if not arc.parse_ok:
            continue
        engine_bank = base.get((arc.persona, arc.topic, arc.engine))
        topic_banks = topic_slots.get((arc.persona, arc.topic), [])
        shared = [
            bank for bank in topic_banks
            if bank.family_kind == "slot"
        ]
        relevant_banks = [*shared]
        if engine_bank is not None:
            relevant_banks.append(engine_bank)
        hook = next(
            (
                bank
                for bank in shared
                if bank.family.split("/", 1)[0].upper() == "HOOK"
            ),
            None,
        )

        # Count only tuple-relevant source: shared slot banks plus the selected
        # engine. Other engines for the same persona/topic must not inflate this
        # tuple's word-capacity estimate.
        tuple_words = sum(
            bank.total_source_words for bank in relevant_banks
        )
        tuple_usable = sum(
            bank.usable_atom_count for bank in relevant_banks
        )
        high_risk_reasons: list[str] = []

        if engine_bank is None:
            high_risk_reasons.append(
                f"missing_engine_bank:atoms/{arc.persona}/{arc.topic}/"
                f"{arc.engine}/{CANONICAL_NAME}"
            )
        else:
            if not engine_bank.parse_ok:
                high_risk_reasons.append("engine_parse_fail")
            if engine_bank.engine_depth_risk:
                high_risk_reasons.append("engine_depth_or_band_deficit")
            if engine_bank.required_arc_bands_missing:
                high_risk_reasons.append(
                    "missing_required_arc_bands:"
                    + _join_ints(
                        engine_bank.required_arc_bands_missing
                    )
                )
            if (
                engine_bank.min_required_band_depth
                < ENGINE_MIN_PER_REQUIRED_BAND
            ):
                high_risk_reasons.append(
                    "required_band_depth_below_"
                    f"{ENGINE_MIN_PER_REQUIRED_BAND}"
                )
            if engine_bank.likely_extended_book_2h_word_budget_risk:
                high_risk_reasons.append(
                    "engine_extended_book_2h_word_capacity_risk"
                )

        if hook is None:
            high_risk_reasons.append(
                f"missing_hook_bank:atoms/{arc.persona}/{arc.topic}/"
                f"HOOK/{CANONICAL_NAME}"
            )
        elif hook.hook_depth_risk:
            high_risk_reasons.append(
                f"HOOK_real_depth={hook.usable_atom_count}<"
                f"{HOOK_MIN_USABLE}"
            )

        unhealthy_shared = [
            bank
            for bank in shared
            if not bank.healthy
            and (
                bank.family_kind == "slot"
                or bank.family == arc.engine
            )
        ]
        placeholder_banks = [
            bank.path
            for bank in unhealthy_shared
            if bank.placeholder_atom_count
            or bank.placeholder_line_count
        ]
        if placeholder_banks:
            high_risk_reasons.append(
                f"placeholder_debt_in_{len(placeholder_banks)}_banks"
            )

        tuple_word_floor = (
            arc.chapter_count * TUPLE_TARGET_WORDS_PER_ARC_CHAPTER
        )
        likely_word_budget_risk = bool(
            tuple_words < tuple_word_floor
            or (
                engine_bank is not None
                and engine_bank.likely_extended_book_2h_word_budget_risk
            )
            or hook is None
            or (hook is not None and hook.hook_depth_risk)
        )
        if tuple_words < tuple_word_floor:
            high_risk_reasons.append(
                f"tuple_source_words={tuple_words}<"
                f"advisory_floor={tuple_word_floor}"
            )

        writer_files = sorted(
            {
                bank.path
                for bank in unhealthy_shared
                if (
                    bank.exact_writer_target_added_words > 0
                    or bank.placeholder_atom_count
                    or bank.placeholder_line_count
                    or not bank.parse_ok
                )
            }
        )
        if engine_bank is None:
            writer_files.append(
                f"atoms/{arc.persona}/{arc.topic}/{arc.engine}/"
                f"{CANONICAL_NAME}"
            )
        if hook is None:
            writer_files.append(
                f"atoms/{arc.persona}/{arc.topic}/HOOK/{CANONICAL_NAME}"
            )

        target_added_words = sum(
            bank.exact_writer_target_added_words
            for bank in unhealthy_shared
        )
        high_risk = bool(
            high_risk_reasons
            or likely_word_budget_risk
            or any(not bank.parse_ok for bank in unhealthy_shared)
        )
        rows.append(
            {
                "arc_id": arc.arc_id,
                "arc_path": arc.path,
                "persona": arc.persona,
                "topic": arc.topic,
                "engine": arc.engine,
                "chapter_count": arc.chapter_count,
                "required_bands": list(arc.required_bands),
                "engine_bank_path": (
                    engine_bank.path if engine_bank else ""
                ),
                "engine_usable_atom_count": (
                    engine_bank.usable_atom_count
                    if engine_bank
                    else 0
                ),
                "engine_total_source_words": (
                    engine_bank.total_source_words
                    if engine_bank
                    else 0
                ),
                "engine_bands_present": (
                    engine_bank.bands_present if engine_bank else []
                ),
                "engine_required_bands_missing": (
                    engine_bank.required_arc_bands_missing
                    if engine_bank
                    else list(arc.required_bands)
                ),
                "hook_bank_path": hook.path if hook else "",
                "hook_usable_atom_count": (
                    hook.usable_atom_count if hook else 0
                ),
                "tuple_usable_atom_count": tuple_usable,
                "tuple_total_source_words": tuple_words,
                "advisory_tuple_word_floor": tuple_word_floor,
                "likely_extended_book_2h_word_budget_risk": (
                    likely_word_budget_risk
                ),
                "parse_only_healthy_forbidden": True,
                "high_risk": high_risk,
                "risk_reasons": high_risk_reasons,
                "exact_files_needing_writer_work": writer_files,
                "target_added_words": target_added_words,
            }
        )
    return rows


def _risk_score(bank: BankHealth) -> int:
    score = 0
    score += 100 if not bank.parse_ok else 0
    score += min(60, bank.placeholder_atom_count * 4)
    score += min(40, bank.placeholder_line_count * 2)
    score += 35 if bank.hook_depth_risk else 0
    score += 45 if bank.engine_depth_risk else 0
    score += 35 if bank.likely_extended_book_2h_word_budget_risk else 0
    score += 25 if bank.locale_base_english_shallow_risk else 0
    score += min(30, bank.thin_atom_count * 2)
    score += min(25, bank.low_information_atom_count * 5)
    score += min(60, bank.duplicate_atom_id_count * 20)
    score += len(bank.required_arc_bands_missing) * 12
    return score


def _write_tsv(path: Path, banks: Sequence[BankHealth]) -> None:
    rows = [bank.to_tsv_row() for bank in banks]
    fields = list(rows[0]) if rows else [
        "persona",
        "topic",
        "family",
        "family_kind",
        "locale",
        "path",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fields,
            delimiter="\t",
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


def _write_summary(
    path: Path,
    *,
    repo_root: Path,
    banks: Sequence[BankHealth],
    arcs: Sequence[ArcSpec],
    tuples: Sequence[Mapping[str, Any]],
    scan_errors: Sequence[Mapping[str, str]],
    arc_errors: Sequence[Mapping[str, str]],
) -> None:
    high_risk = [row for row in tuples if row["high_risk"]]
    healthy = [bank for bank in banks if bank.healthy]
    placeholder_banks = [
        bank
        for bank in banks
        if bank.placeholder_atom_count or bank.placeholder_line_count
    ]
    engine_deficits = [bank for bank in banks if bank.engine_depth_risk]
    hook_deficits = [bank for bank in banks if bank.hook_depth_risk]
    budget_risks = [
        row
        for row in tuples
        if row["likely_extended_book_2h_word_budget_risk"]
    ]

    corporate = next(
        (
            row
            for row in tuples
            if row["persona"] == "corporate_managers"
            and row["topic"] == "burnout"
            and row["engine"] == "overwhelm"
        ),
        None,
    )

    lines = [
        "# Atom Bank Health — 2026-07-14",
        "",
        "## Truth boundary",
        "",
        "This is a static preflight risk audit. It detects shallow or structurally",
        "incomplete source banks before a full book run. It does not replace a",
        "production build, manuscript review, translation review, or final quality gates.",
        "",
        "A bank is **not healthy merely because it parses**. Healthy requires usable",
        "non-placeholder depth, no placeholder debt, acceptable thin-atom ratio,",
        "required arc-band coverage, and no configured word-capacity risk.",
        "",
        "## Scan summary",
        "",
        f"- Repo root: `{repo_root}`",
        f"- Canonical banks scanned: **{len(banks)}**",
        f"- Master arcs parsed: **{len([a for a in arcs if a.parse_ok])}**",
        f"- Healthy banks: **{len(healthy)}**",
        f"- Banks with placeholder debt: **{len(placeholder_banks)}**",
        f"- HOOK depth deficits: **{len(hook_deficits)}**",
        f"- Engine depth/band deficits: **{len(engine_deficits)}**",
        f"- High-risk tuples: **{len(high_risk)}**",
        f"- Likely extended_book_2h word-budget-risk tuples: **{len(budget_risks)}**",
        f"- Scan errors: **{len(scan_errors)}**",
        f"- Master-arc errors: **{len(arc_errors)}**",
        "",
        "## Requested acceptance sentinel",
        "",
    ]
    if corporate is None:
        lines.extend(
            [
                "- `corporate_managers/burnout/overwhelm`: **NOT FOUND**",
                "  - This is itself a blocker: the matching master arc or tuple row",
                "    could not be resolved.",
            ]
        )
    else:
        verdict = "HIGH RISK" if corporate["high_risk"] else "NOT FLAGGED"
        lines.extend(
            [
                f"- `corporate_managers/burnout/overwhelm`: **{verdict}**",
                f"  - HOOK usable: `{corporate['hook_usable_atom_count']}`",
                f"  - Engine usable: `{corporate['engine_usable_atom_count']}`",
                "  - Missing required bands: `"
                + (_join_ints(corporate["engine_required_bands_missing"]) or "none")
                + "`",
                f"  - Tuple source words: `{corporate['tuple_total_source_words']}`",
                "  - Reasons: "
                + ("; ".join(corporate["risk_reasons"]) or "none"),
            ]
        )

    lines.extend(
        [
            "",
            "## Thresholds",
            "",
            f"- Thin atom: `< {THIN_ATOM_WORDS}` usable words.",
            f"- HOOK minimum: `{HOOK_MIN_USABLE}` real authored atoms.",
            f"- Engine minimum: `{ENGINE_MIN_USABLE}` usable atoms.",
            f"- Required-band minimum: `{ENGINE_MIN_PER_REQUIRED_BAND}` usable atoms per required band.",
            f"- Engine source capacity: `{ENGINE_TARGET_WORDS_PER_ARC_CHAPTER}` words × arc chapters.",
            f"- Tuple source capacity: `{TUPLE_TARGET_WORDS_PER_ARC_CHAPTER}` words × arc chapters.",
            "",
            "These are explicit advisory preflight thresholds. They may be ratcheted",
            "from build evidence; they are not represented as empirically proven",
            "bestseller laws.",
            "",
            "## Highest-risk tuples",
            "",
        ]
    )
    for row in sorted(
        high_risk,
        key=lambda item: (
            -len(item["risk_reasons"]),
            item["persona"],
            item["topic"],
            item["engine"],
        ),
    )[:30]:
        lines.append(
            f"- `{row['persona']}/{row['topic']}/{row['engine']}` — "
            + "; ".join(row["risk_reasons"])
        )

    if scan_errors or arc_errors:
        lines.extend(["", "## Parse/scan errors", ""])
        for item in [*scan_errors, *arc_errors][:100]:
            lines.append(f"- `{item['path']}` — {item['error']}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_backlog(
    path: Path,
    banks: Sequence[BankHealth],
) -> list[BankHealth]:
    candidates = [
        bank
        for bank in banks
        if (
            not bank.healthy
            and (
                bank.exact_writer_target_added_words > 0
                or bank.placeholder_atom_count > 0
                or bank.placeholder_line_count > 0
                or not bank.parse_ok
                or bank.required_arc_bands_missing
            )
        )
    ]
    ordered = sorted(
        candidates,
        key=lambda bank: (
            -_risk_score(bank),
            bank.persona,
            bank.topic,
            bank.family,
            bank.locale,
        ),
    )

    grouped: dict[tuple[str, str], list[BankHealth]] = defaultdict(list)
    for bank in ordered:
        grouped[(bank.persona, bank.topic)].append(bank)

    lines = [
        "# Atom Writer Backlog",
        "",
        "Grouped by persona/topic/slot or engine. Added-word targets are computed",
        "from explicit per-family atom minima, required-band depth, and direct",
        "top-up of usable atoms below 40 words. Placeholder text contributes zero",
        "usable depth.",
        "",
        "## Top 20 fixes",
        "",
    ]
    for index, bank in enumerate(ordered[:20], start=1):
        lines.extend(
            [
                f"{index}. `{bank.persona}/{bank.topic}/{bank.family}`"
                f" (`{bank.locale}`)",
                f"   - File: `{bank.path}`",
                f"   - Target added words: **{bank.exact_writer_target_added_words}**",
                f"   - Usable/parsed: `{bank.usable_atom_count}/{bank.parsed_atom_count}`",
                f"   - Placeholder atoms/lines: `{bank.placeholder_atom_count}/{bank.placeholder_line_count}`",
                f"   - Missing required bands: `{_join_ints(bank.required_arc_bands_missing) or 'none'}`",
                f"   - Reasons: {'; '.join(bank.risk_reasons) or 'unhealthy bank'}",
            ]
        )

    lines.extend(["", "## Full grouped backlog", ""])
    for (persona, topic), group in sorted(grouped.items()):
        lines.append(f"### {persona} / {topic}")
        lines.append("")
        for bank in group:
            lines.extend(
                [
                    f"- **{bank.family}** (`{bank.locale}`)",
                    f"  - File: `{bank.path}`",
                    f"  - Target added words: `{bank.exact_writer_target_added_words}`",
                    f"  - Add/replace atoms until usable depth reaches "
                    f"`{_slot_target(bank.family, bank.family_kind)['min_atoms']}`.",
                    f"  - Replace all `{bank.placeholder_atom_count}` placeholder atoms; "
                    f"repair `{bank.placeholder_line_count}` placeholder lines.",
                    f"  - Thin usable atoms under 40 words: `{bank.thin_atom_count}`.",
                    f"  - Required-band deficits: "
                    f"`{_join_ints(bank.required_arc_bands_missing) or 'none'}`.",
                ]
            )
        lines.append("")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return ordered


def write_outputs(
    *,
    repo_root: Path,
    artifact_root: Path,
    banks: Sequence[BankHealth],
    arcs: Sequence[ArcSpec],
    tuples: Sequence[Mapping[str, Any]],
    scan_errors: Sequence[Mapping[str, str]],
    arc_errors: Sequence[Mapping[str, str]],
) -> dict[str, Any]:
    artifact_root.mkdir(parents=True, exist_ok=True)
    _write_tsv(artifact_root / "atom_bank_health.tsv", banks)
    _write_summary(
        artifact_root / "tuple_health_summary.md",
        repo_root=repo_root,
        banks=banks,
        arcs=arcs,
        tuples=tuples,
        scan_errors=scan_errors,
        arc_errors=arc_errors,
    )
    backlog = _write_backlog(
        artifact_root / "writer_backlog.md",
        banks,
    )

    high_risk = [dict(row) for row in tuples if row["high_risk"]]
    payload = {
        "schema_version": SCHEMA_VERSION,
        "artifact_root": str(artifact_root.relative_to(repo_root))
        if artifact_root.is_relative_to(repo_root)
        else str(artifact_root),
        "thresholds": {
            "thin_atom_words": THIN_ATOM_WORDS,
            "hook_min_usable": HOOK_MIN_USABLE,
            "engine_min_usable": ENGINE_MIN_USABLE,
            "engine_min_per_required_band": (
                ENGINE_MIN_PER_REQUIRED_BAND
            ),
            "engine_target_words_per_arc_chapter": (
                ENGINE_TARGET_WORDS_PER_ARC_CHAPTER
            ),
            "tuple_target_words_per_arc_chapter": (
                TUPLE_TARGET_WORDS_PER_ARC_CHAPTER
            ),
            "thin_ratio_high_risk": THIN_RATIO_HIGH_RISK,
            "status": "advisory_preflight_thresholds",
        },
        "tuples_scanned": len(tuples),
        "high_risk_count": len(high_risk),
        "high_risk_tuples": high_risk,
        "scan_errors": list(scan_errors),
        "arc_errors": list(arc_errors),
        "top_20_writer_fixes": [
            {
                "persona": bank.persona,
                "topic": bank.topic,
                "family": bank.family,
                "locale": bank.locale,
                "path": bank.path,
                "target_added_words": (
                    bank.exact_writer_target_added_words
                ),
                "risk_reasons": bank.risk_reasons,
            }
            for bank in backlog[:20]
        ],
        "dev_gate_recommendations": [
            (
                "Run this audit as a required changed-bank CI check; fail when "
                "new placeholders, parse errors, or required-band regressions "
                "are introduced."
            ),
            (
                "Keep catalog-wide historical debt report-only initially, then "
                "ratchet thresholds by touched persona/topic cells."
            ),
            (
                "Before extended_book_2h production, hard-block tuples with "
                "missing engine banks, missing required arc bands, or HOOK "
                "usable depth below 12."
            ),
            (
                "Treat word-capacity results as preflight risk signals until "
                "correlated with fresh build outcomes; do not present them as "
                "guaranteed final word counts."
            ),
            (
                "Require locale-bank PRs to report base-English health so "
                "translation volume cannot hide shallow source writing."
            ),
        ],
    }
    (artifact_root / "high_risk_tuples.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return payload


def audit_repo(
    repo_root: Path,
    artifact_root: Path,
) -> dict[str, Any]:
    arcs, arc_errors = load_arcs(repo_root)
    banks, scan_errors = scan_banks(repo_root, arcs)
    tuples = build_tuple_matrix(banks, arcs)
    payload = write_outputs(
        repo_root=repo_root,
        artifact_root=artifact_root,
        banks=banks,
        arcs=arcs,
        tuples=tuples,
        scan_errors=scan_errors,
        arc_errors=arc_errors,
    )

    sentinel = next(
        (
            row
            for row in tuples
            if row["persona"] == "corporate_managers"
            and row["topic"] == "burnout"
            and row["engine"] == "overwhelm"
        ),
        None,
    )
    payload["acceptance_sentinel"] = {
        "tuple": "corporate_managers/burnout/overwhelm",
        "found": sentinel is not None,
        "high_risk": bool(sentinel and sentinel["high_risk"]),
        "risk_reasons": (
            sentinel["risk_reasons"] if sentinel else ["tuple_not_found"]
        ),
    }
    # Rewrite after sentinel addition.
    (artifact_root / "high_risk_tuples.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return payload


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
    )
    parser.add_argument(
        "--artifact-root",
        type=Path,
        default=None,
    )
    parser.add_argument(
        "--fail-on-high-risk",
        action="store_true",
        help=(
            "Exit 3 when any high-risk tuple exists. Intended for a future "
            "ratcheted CI lane, not initial catalog-debt adoption."
        ),
    )
    args = parser.parse_args(argv)

    repo_root = args.repo_root.expanduser().resolve()
    artifact_root = (
        args.artifact_root.expanduser().resolve()
        if args.artifact_root
        else repo_root / DEFAULT_ARTIFACT_ROOT
    )

    payload = audit_repo(repo_root, artifact_root)
    print(
        json.dumps(
            {
                "artifact_root": str(artifact_root),
                "tuples_scanned": payload["tuples_scanned"],
                "high_risk_count": payload["high_risk_count"],
                "acceptance_sentinel": payload["acceptance_sentinel"],
            },
            indent=2,
        )
    )
    if args.fail_on_high_risk and payload["high_risk_count"]:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
