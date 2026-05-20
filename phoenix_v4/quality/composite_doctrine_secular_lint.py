"""Secular-lint for SOURCE_OF_TRUTH/composite_doctrine/ atoms (OPD-115 Phase B)."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_ALLOWLIST_PATH = REPO_ROOT / "config" / "quality" / "composite_doctrine_allowlist.yaml"

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


def lint_file(
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
        violations.extend(lint_file(path, allowlist=allow))
    return violations


def lint_paths(paths: Sequence[Path], *, allowlist_path: Optional[Path] = None) -> List[SecularLintViolation]:
    allow = _load_allowlist(allowlist_path)
    out: List[SecularLintViolation] = []
    for p in paths:
        if p.is_dir():
            for f in sorted(p.rglob("CANONICAL.txt")):
                out.extend(lint_file(f, allowlist=allow))
        else:
            out.extend(lint_file(p, allowlist=allow))
    return out
