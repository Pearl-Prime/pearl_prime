"""Secular-lint + WISDOM_ESSENCE shape gate for composite_doctrine atoms (OPD-115 Phase B).

Every composite teaching atom (``COMPOSITE_DOCTRINE vNN`` block) must be exactly
three paragraphs and pass the secular register scan on its prose body.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_ALLOWLIST_PATH = REPO_ROOT / "config" / "quality" / "composite_doctrine_allowlist.yaml"
REQUIRED_TEACHING_PARAGRAPHS = 3

_DEITY_TERMS = (
    "buddha", "krishna", "christ", "mary", "mahāvairocana", "dainichi",
    "amaterasu", "shiva", "kali", "lakshmi",
)
_UNTRANSLATED_TERMS = (
    "dukkha", "anatta", "samsara", "sunyata", "kensho", "satori",
    "tathata", "bhakti",
)
_LINEAGE_PHRASES = (
    "as the buddha taught",
    "in the zen tradition",
    "shingon teaches",
    "the dharma says",
    "bhakti tradition holds",
)
_CHANNELING_TERMS = (
    "ascended masters", "cosmic council", "light language",
    "channeling", "starseed",
)
_RITUAL_TERMS = ("sutra", "goma", "mudrā", "puja")
_CAPITAL_NOUN_TERMS = ("yoga", "mantra")


@dataclass(frozen=True)
class SecularLintViolation:
    path: str
    line: int
    matched_tell: str
    excerpt: str = ""
    atom_id: str = ""


def _split_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def _parse_composite_atoms(path: Path) -> list[dict]:
    from phoenix_v4.planning.registry_resolver import _parse_canonical_txt

    return _parse_canonical_txt(path, slot_type="COMPOSITE_DOCTRINE")


def lint_atom_shape(path: Path, atoms: Sequence[dict]) -> List[SecularLintViolation]:
    """Hard shape rule: each composite teaching atom = exactly 3 paragraphs."""
    violations: List[SecularLintViolation] = []
    for atom in atoms:
        if not isinstance(atom, dict):
            continue
        atom_id = str(atom.get("atom_id") or "").strip()
        content = str(atom.get("content") or "").strip()
        if not atom_id or not content:
            continue
        para_count = len(_split_paragraphs(content))
        if para_count == REQUIRED_TEACHING_PARAGRAPHS:
            continue
        violations.append(
            SecularLintViolation(
                path=str(path),
                line=0,
                matched_tell=(
                    f"shape:paragraph_count:{para_count} "
                    f"(expected {REQUIRED_TEACHING_PARAGRAPHS})"
                ),
                excerpt=content[:120],
                atom_id=atom_id,
            )
        )
    return violations


def _load_allowlist(path: Optional[Path] = None) -> set[str]:
    p = path or DEFAULT_ALLOWLIST_PATH
    if not p.exists():
        return set()
    try:
        import yaml
    except ImportError:
        return set()
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    entries = data.get("allowlist") or data.get("terms") or []
    return {str(t).strip().lower() for t in entries if str(t).strip()}


def _has_capitalized_noun(line: str, term: str) -> bool:
    """True when term appears as a capitalized noun (not sentence-start adjective)."""
    for m in re.finditer(rf"\b{re.escape(term)}\b", line, re.IGNORECASE):
        if m.group(0)[:1].isupper():
            return True
    return False


def _scan_line(
    line: str,
    line_no: int,
    path: Path,
    allowlist: set[str],
) -> List[SecularLintViolation]:
    violations: List[SecularLintViolation] = []
    lower = line.lower()

    def _add(tell: str) -> None:
        if tell.lower() in allowlist:
            return
        violations.append(
            SecularLintViolation(
                path=str(path),
                line=line_no,
                matched_tell=tell,
                excerpt=line.strip()[:120],
            )
        )

    for term in _DEITY_TERMS + _UNTRANSLATED_TERMS + _CHANNELING_TERMS + _RITUAL_TERMS:
        if term in lower:
            _add(term)

    for phrase in _LINEAGE_PHRASES:
        if phrase in lower:
            _add(phrase)

    for term in _CAPITAL_NOUN_TERMS:
        if _has_capitalized_noun(line, term):
            _add(f"{term} (capitalized)")

    return violations


def lint_file_secular(
    path: Path,
    *,
    allowlist: Optional[set[str]] = None,
) -> List[SecularLintViolation]:
    allow = allowlist if allowlist is not None else _load_allowlist()
    if not path.exists() or not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    out: List[SecularLintViolation] = []
    for i, line in enumerate(text.splitlines(), start=1):
        if not line.strip() or line.strip().startswith("#"):
            continue
        out.extend(_scan_line(line, i, path, allow))
    return out


def lint_file(
    path: Path,
    *,
    allowlist: Optional[set[str]] = None,
) -> List[SecularLintViolation]:
    """Secular register scan only (backward-compatible entry for existing tests)."""
    return lint_file_secular(path, allowlist=allowlist)


def lint_canonical_file(
    path: Path,
    *,
    allowlist: Optional[set[str]] = None,
) -> List[SecularLintViolation]:
    """Full composite-doctrine lint: secular register + exactly-3-paragraph shape."""
    violations = lint_file_secular(path, allowlist=allowlist)
    if path.exists() and path.is_file():
        violations.extend(lint_atom_shape(path, _parse_composite_atoms(path)))
    return violations


def lint_composite_doctrine_tree(
    root: Optional[Path] = None,
    *,
    allowlist_path: Optional[Path] = None,
) -> List[SecularLintViolation]:
    base = root or (REPO_ROOT / "SOURCE_OF_TRUTH" / "composite_doctrine")
    if not base.exists():
        return []
    allow = _load_allowlist(allowlist_path)
    violations: List[SecularLintViolation] = []
    for path in sorted(base.rglob("CANONICAL.txt")):
        violations.extend(lint_canonical_file(path, allowlist=allow))
    return violations


def lint_paths(paths: Sequence[Path], *, allowlist_path: Optional[Path] = None) -> List[SecularLintViolation]:
    allow = _load_allowlist(allowlist_path)
    out: List[SecularLintViolation] = []
    for p in paths:
        if p.is_dir():
            for f in sorted(p.rglob("CANONICAL.txt")):
                out.extend(lint_canonical_file(f, allowlist=allow))
        else:
            out.extend(lint_canonical_file(p, allowlist=allow))
    return out
