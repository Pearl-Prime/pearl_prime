"""Shared fail-closed parser for atoms/**/CANONICAL.txt block banks.

This module unifies the three historically divergent parsing surfaces used by
assembly, pool selection, and prose resolution. It supports the canonical
two-delimiter shape and the legacy single-section shape, excludes placeholder
bodies from selectable depth, and reports duplicate atom IDs rather than
silently overwriting them.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any, Iterable, Mapping, Sequence

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

HEADER_RE = re.compile(r"^##\s+([A-Z][A-Z0-9_]*)\s+v(\d+)\s*$")
BARE_HEADER_RE = re.compile(r"^([A-Z][A-Z0-9_]*)\s+v(\d+)\s*$")
META_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_. -]{0,80}\s*:\s*.*$")
WORD_RE = re.compile(r"\b[\w’'-]+\b", re.UNICODE)

KNOWN_BARE_HEADERS = frozenset(
    {
        "HOOK", "SCENE", "STORY", "REFLECTION", "PIVOT", "EXERCISE",
        "INTEGRATION", "THREAD", "TAKEAWAY", "PERMISSION", "COMPRESSION",
        "RECOGNITION", "MECHANISM_PROOF", "TURNING_POINT", "EMBODIMENT",
        "COST_REVEAL", "RECKONING", "TRANSITION", "DWELL",
        "ANGLE_DEFINITION", "ANGLE_CALLBACK", "TEACHER_DOCTRINE",
    }
)
PLACEHOLDER_RE = re.compile(
    r"\[[^\]]*\b(?:"
    r"persona-specific|placeholder|missing|silence|tbd|tktk|todo|"
    r"insert|specific|draft|fill(?:\s+this)?|content\s+for"
    r")\b[^\]]*\]",
    re.IGNORECASE,
)
PIPELINE_PLACEHOLDER_RE = re.compile(
    r"\[(?:Placeholder|Missing|Silence)\s*:[^\]]*\]",
    re.IGNORECASE,
)
BARE_VAR_RE = re.compile(
    r"^(?:\{\{[A-Za-z_]\w*\}\}|\{[A-Za-z_]\w*\}|%\([A-Za-z_]\w*\)s)$"
)
LEGIT_BRACKET_RE = re.compile(
    r"^(?:"
    r"\[sic\]|\[emphasis added\]|\[ibid\.?\]|\[\d+\]|"
    r"\[[A-Z][A-Za-z]+(?:\s+et\s+al\.?)?,?\s+\d{4}\]"
    r")$",
    re.IGNORECASE,
)


class CanonicalAtomError(ValueError):
    """Base failure for malformed canonical banks."""


class DuplicateAtomIdError(CanonicalAtomError):
    """Two authored blocks resolve to the same atom ID."""


class EmptyCanonicalAtomError(CanonicalAtomError):
    """A header exists but has no usable prose."""


@dataclass(frozen=True)
class CanonicalAtomBlock:
    label: str
    version: str
    atom_id: str
    metadata: dict[str, Any]
    prose: str
    delimiter_shape: str
    placeholder: bool
    source_line: int

    @property
    def word_count(self) -> int:
        return len(WORD_RE.findall(self.prose or ""))


def is_placeholder_prose(prose: str) -> bool:
    body = (prose or "").strip()
    if not body:
        return True
    if LEGIT_BRACKET_RE.fullmatch(body):
        return False
    if BARE_VAR_RE.fullmatch(body):
        return True
    residue = PLACEHOLDER_RE.sub("", body)
    residue = PIPELINE_PLACEHOLDER_RE.sub("", residue).strip()
    return bool(
        PLACEHOLDER_RE.search(body) or PIPELINE_PLACEHOLDER_RE.search(body)
    ) and not residue


def _parse_metadata(lines: Sequence[str]) -> dict[str, Any]:
    text = "\n".join(lines).strip()
    if not text:
        return {}
    if yaml is not None:
        try:
            data = yaml.safe_load(text)
            if isinstance(data, Mapping):
                return dict(data)
        except Exception:
            pass
    out: dict[str, Any] = {}
    for line in lines:
        stripped = line.strip()
        if not META_RE.match(stripped):
            continue
        key, value = stripped.split(":", 1)
        out[key.strip()] = value.strip()
    return out


def _split_metadata_and_prose(lines: Sequence[str]) -> tuple[list[str], list[str]]:
    metadata: list[str] = []
    prose: list[str] = []
    saw_prose = False
    for raw in lines:
        stripped = raw.strip()
        if not stripped:
            if saw_prose:
                prose.append(raw)
            continue
        if not saw_prose and META_RE.match(stripped):
            metadata.append(raw)
            continue
        saw_prose = True
        prose.append(raw)
    return metadata, prose


def _next_nonempty(lines: Sequence[str], start: int) -> str:
    for index in range(start + 1, len(lines)):
        if lines[index].strip():
            return lines[index].strip()
    return ""


def _is_header(lines: Sequence[str], index: int) -> re.Match[str] | None:
    stripped = lines[index].strip()
    match = HEADER_RE.match(stripped)
    if match:
        return match
    bare = BARE_HEADER_RE.match(stripped)
    if (
        bare
        and bare.group(1) in KNOWN_BARE_HEADERS
        and _next_nonempty(lines, index) == "---"
    ):
        return bare
    return None


def _parse_payload(
    payload: Sequence[str],
    *,
    path: Path,
    header: str,
) -> tuple[dict[str, Any], str, str]:
    delimiter_positions = [
        index for index, line in enumerate(payload) if line.strip() == "---"
    ]
    if not delimiter_positions:
        metadata_lines, prose_lines = _split_metadata_and_prose(payload)
        prose = "\n".join(prose_lines).strip()
        return _parse_metadata(metadata_lines), prose, "no-delimiter"

    first = delimiter_positions[0]
    before = list(payload[:first])
    after_first = list(payload[first + 1 :])

    # Canonical: first delimiter opens metadata, second opens prose.
    later = [i for i, line in enumerate(after_first) if line.strip() == "---"]
    if later:
        second = later[0]
        first_segment = after_first[:second]
        after_second = after_first[second + 1 :]
        third = next(
            (i for i, line in enumerate(after_second) if line.strip() == "---"),
            None,
        )
        prose_segment = after_second if third is None else after_second[:third]

        before_meta, before_prose = _split_metadata_and_prose(before)
        if before_prose:
            # Legacy metadata/prose before a closing delimiter.
            metadata_lines = before_meta
            prose = "\n".join(before_prose).strip()
            return _parse_metadata(metadata_lines), prose, "pre-delimiter-legacy"

        if prose_segment and "\n".join(prose_segment).strip():
            metadata_lines = list(first_segment)
            prose = "\n".join(prose_segment).strip()
            return _parse_metadata(metadata_lines), prose, "two-delimiter"

        # Legacy single-section: content sits between two delimiters.
        metadata_lines, prose_lines = _split_metadata_and_prose(first_segment)
        if prose_lines:
            return (
                _parse_metadata(metadata_lines),
                "\n".join(prose_lines).strip(),
                "single-section-legacy",
            )
        if first_segment and not all(
            META_RE.match(line.strip()) for line in first_segment if line.strip()
        ):
            return {}, "\n".join(first_segment).strip(), "single-section-legacy"
        return _parse_metadata(first_segment), "", "metadata-only"

    # Only one delimiter: split rows after it into metadata prefix and prose.
    metadata_lines, prose_lines = _split_metadata_and_prose(after_first)
    if prose_lines:
        return (
            _parse_metadata(metadata_lines),
            "\n".join(prose_lines).strip(),
            "single-delimiter",
        )

    # A prose-only single delimiter can look key-like in its first sentence only
    # in pathological cases. Metadata-only blocks are intentionally empty.
    return _parse_metadata(metadata_lines), "", "metadata-only"


def parse_canonical_blocks(
    path: Path,
    *,
    persona: str | None = None,
    topic: str | None = None,
    slot_type: str | None = None,
    include_placeholders: bool = False,
    require_unique_ids: bool = False,
    require_usable_if_headers: bool = True,
) -> list[CanonicalAtomBlock]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    headers: list[tuple[int, re.Match[str]]] = []
    for index in range(len(lines)):
        match = _is_header(lines, index)
        if match:
            headers.append((index, match))
    if not headers:
        return []

    resolved_persona = persona or (
        path.parents[2].name if len(path.parents) >= 3 else ""
    )
    resolved_topic = topic or (
        path.parents[1].name if len(path.parents) >= 2 else ""
    )
    resolved_slot = (slot_type or path.parent.name).upper()

    blocks: list[CanonicalAtomBlock] = []
    seen: dict[str, int] = {}
    malformed: list[str] = []

    for header_index, (line_index, match) in enumerate(headers):
        end = (
            headers[header_index + 1][0]
            if header_index + 1 < len(headers)
            else len(lines)
        )
        label, version = match.group(1), match.group(2)
        metadata, prose, shape = _parse_payload(
            lines[line_index + 1 : end],
            path=path,
            header=f"{label} v{version}",
        )
        explicit_id = str(metadata.get("id") or "").strip()
        atom_id = explicit_id or (
            f"{resolved_persona}_{resolved_topic}_{resolved_slot}_v{version}"
        )
        placeholder = is_placeholder_prose(prose)
        if not prose and shape != "metadata-only":
            malformed.append(
                f"{label} v{version} line {line_index + 1}: empty prose"
            )
        block = CanonicalAtomBlock(
            label=label,
            version=version,
            atom_id=atom_id,
            metadata=metadata,
            prose=prose,
            delimiter_shape=shape,
            placeholder=placeholder,
            source_line=line_index + 1,
        )
        if require_unique_ids and atom_id in seen:
            raise DuplicateAtomIdError(
                f"Duplicate atom ID {atom_id!r} in {path}: "
                f"lines {seen[atom_id]} and {line_index + 1}"
            )
        seen[atom_id] = line_index + 1
        if include_placeholders or (prose and not placeholder):
            blocks.append(block)

    if malformed:
        raise EmptyCanonicalAtomError(
            f"Malformed CANONICAL.txt {path}: " + "; ".join(malformed)
        )
    if require_usable_if_headers and not blocks:
        raise EmptyCanonicalAtomError(
            f"Malformed CANONICAL.txt {path}: {len(headers)} headers but "
            "zero usable non-placeholder prose atoms"
        )
    return blocks


def duplicate_atom_ids(
    path: Path,
    *,
    persona: str | None = None,
    topic: str | None = None,
    slot_type: str | None = None,
) -> list[dict[str, Any]]:
    """Return duplicate IDs without raising, for catalog health reporting."""
    if not path.exists():
        return []
    try:
        parse_canonical_blocks(
            path,
            persona=persona,
            topic=topic,
            slot_type=slot_type,
            include_placeholders=True,
            require_unique_ids=True,
            require_usable_if_headers=False,
        )
        return []
    except DuplicateAtomIdError as exc:
        return [{"path": str(path), "error": str(exc)}]
