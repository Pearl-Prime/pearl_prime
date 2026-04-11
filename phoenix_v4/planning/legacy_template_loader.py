"""
Load legacy audiobook template slices (YAML under extracted trees, bridges markdown).

Never raises for missing content — returns structured dataclasses with warnings.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

_CHAPTER_HEADER_RE = re.compile(
    r"\*\*CHAPTER\s+(\d+)\s+-\s+BRIDGES\*\*",
    re.IGNORECASE,
)
_CONCLUSION_RE = re.compile(
    r"\*Chapter Conclusion:\*\s*\"([^\"]*)\"",
    re.DOTALL,
)
_NEXT_BRIDGE_RE = re.compile(
    r"\*Next Chapter Bridge:\*\s*\"([^\"]*)\"",
    re.DOTALL,
)


@dataclass
class LegacyTemplateSection:
    text: str
    library_id: str
    chapter: int
    section: int
    variant_family: str
    word_count: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)


@dataclass
class LegacyTemplateLibrary:
    library_id: str
    root: Path
    status: str  # "available" or "missing"
    role: str
    files_found: int
    total_words: int
    warnings: List[str] = field(default_factory=list)


def _word_count(text: str) -> int:
    return len(text.split()) if text else 0


def load_legacy_template_index(
    path: str = "config/templates/legacy_template_index.yaml",
    repo_root: Optional[Path] = None,
) -> Dict[str, Any]:
    """Load the template index YAML."""
    root = repo_root or REPO_ROOT
    p = root / path
    if yaml is None:
        return {"schema_version": 0, "error": "PyYAML not installed"}
    if not p.exists():
        return {"schema_version": 0, "error": f"missing_index:{p}"}
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {"schema_version": 0, "error": "invalid_yaml"}


def _resolve_section_yaml_path(
    library_id: str,
    chapter: int,
    section: int,
    variant_family: str,
    repo_root: Path,
    index: Dict[str, Any],
) -> tuple[Optional[Path], List[str]]:
    warnings: List[str] = []
    libs = index.get("libraries") or {}
    spec = libs.get(library_id)
    if not isinstance(spec, dict):
        warnings.append(f"unknown_library_id:{library_id}")
        return None, warnings

    rel = spec.get("path") or ""
    primary = repo_root / str(rel).strip()
    fam = variant_family.strip().upper()
    if not fam.startswith("F"):
        fam = f"F{fam}" if fam.isdigit() else fam
    fname = f"variant_{fam}.yaml"
    candidates: List[Path] = []
    if primary.is_dir():
        candidates.append(
            primary
            / f"chapter_{chapter:02d}"
            / f"section_{section:02d}"
            / fname
        )
    extracted_root = repo_root / "template_expand" / "_extracted" / library_id
    candidates.append(
        extracted_root
        / f"chapter_{chapter:02d}"
        / f"section_{section:02d}"
        / fname
    )

    for c in candidates:
        if c.is_file():
            return c, warnings

    if not primary.exists():
        warnings.append(f"library_path_missing:{rel}")
    else:
        warnings.append(f"section_yaml_not_found:{library_id}:ch{chapter:02d}:sec{section:02d}:{fname}")
    return None, warnings


def _yaml_body(data: Any) -> tuple[str, Dict[str, Any]]:
    meta: Dict[str, Any] = {}
    if isinstance(data, str):
        return data.strip(), meta
    if isinstance(data, dict):
        meta = {k: v for k, v in data.items() if k in ("title", "role", "tags")}
        for key in ("text", "content", "body", "prose"):
            if key in data and data[key]:
                return str(data[key]).strip(), meta
    return "", meta


def load_legacy_section(
    library_id: str,
    chapter: int,
    section: int,
    variant_family: str = "F1",
    repo_root: Optional[Path] = None,
) -> LegacyTemplateSection:
    """
    Load one section from a legacy template library.
    If library is missing or file not found, returns empty text and warnings.
    """
    root = repo_root or REPO_ROOT
    warnings: List[str] = []
    index = load_legacy_template_index(repo_root=root)
    path, w2 = _resolve_section_yaml_path(
        library_id, chapter, section, variant_family, root, index
    )
    warnings.extend(w2)

    if path is None or yaml is None:
        return LegacyTemplateSection(
            text="",
            library_id=library_id,
            chapter=chapter,
            section=section,
            variant_family=variant_family,
            word_count=0,
            metadata={},
            warnings=warnings,
        )

    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as e:  # pragma: no cover — defensive
        warnings.append(f"yaml_read_error:{e}")
        return LegacyTemplateSection(
            text="",
            library_id=library_id,
            chapter=chapter,
            section=section,
            variant_family=variant_family,
            word_count=0,
            metadata={},
            warnings=warnings,
        )

    body, meta = _yaml_body(raw)
    wc = _word_count(body)
    return LegacyTemplateSection(
        text=body,
        library_id=library_id,
        chapter=chapter,
        section=section,
        variant_family=variant_family,
        word_count=wc,
        metadata=meta,
        warnings=warnings,
    )


def parse_chapter_bridges_markdown(content: str) -> Dict[int, Dict[str, str]]:
    """
    Parse chapter_bridges_all.md into {chapter: {conclusion, next_bridge}}.
    Chapters are 1-indexed.
    """
    out: Dict[int, Dict[str, str]] = {}
    for m in _CHAPTER_HEADER_RE.finditer(content):
        start = m.end()
        chapter = int(m.group(1))
        next_m = _CHAPTER_HEADER_RE.search(content, pos=start)
        end = next_m.start() if next_m else len(content)
        block = content[start:end]
        c = _CONCLUSION_RE.search(block)
        n = _NEXT_BRIDGE_RE.search(block)
        out[chapter] = {
            "conclusion": c.group(1).strip() if c else "",
            "next_bridge": n.group(1).strip() if n else "",
        }
    return out


def load_transition_bridge_for_chapter_start(
    chapter: int,
    repo_root: Optional[Path] = None,
    bridges_path: str = "template_expand/chapter_bridges_all.md",
) -> Optional[str]:
    """
    Return the *Next Chapter Bridge* text from chapter (chapter-1) that introduces
    the start of `chapter`. Chapters are 1-indexed; returns None for chapter <= 1.
    """
    if chapter <= 1:
        return None
    root = repo_root or REPO_ROOT
    path = root / bridges_path
    if not path.is_file():
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    blocks = parse_chapter_bridges_markdown(text)
    data = blocks.get(chapter - 1)
    if not data:
        return None
    nb = (data.get("next_bridge") or "").strip()
    return nb if nb else None


def load_chapter_bridge(
    chapter: int,
    repo_root: Optional[Path] = None,
    bridges_path: str = "template_expand/chapter_bridges_all.md",
) -> Optional[str]:
    """
    Parse template_expand/chapter_bridges_all.md for the given chapter.
    Returns conclusion + next bridge combined, or None if not found.
    """
    root = repo_root or REPO_ROOT
    path = root / bridges_path
    if not path.is_file():
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    blocks = parse_chapter_bridges_markdown(text)
    data = blocks.get(chapter)
    if not data:
        return None
    parts = [data.get("conclusion") or "", data.get("next_bridge") or ""]
    joined = "\n\n".join(p for p in parts if p.strip())
    return joined if joined.strip() else None


def _walk_count_words(path: Path, extensions: frozenset[str]) -> tuple[int, int]:
    total_w = 0
    nfiles = 0
    if path.is_file():
        if path.suffix.lower() in extensions:
            try:
                data = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                return 0, 0
            return _word_count(data), 1
        return 0, 0
    if not path.is_dir():
        return 0, 0
    for f in path.rglob("*"):
        if f.is_file() and f.suffix.lower() in extensions:
            try:
                data = f.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            total_w += _word_count(data)
            nfiles += 1
    return total_w, nfiles


def estimate_legacy_library_words(
    library_id: str,
    repo_root: Optional[Path] = None,
) -> int:
    """
    Sum words from all available files for a library entry (markdown/yaml/txt/py).
    Returns 0 if the primary path is missing or only a zip exists without extraction.
    """
    root = repo_root or REPO_ROOT
    index = load_legacy_template_index(repo_root=root)
    libs = index.get("libraries") or {}
    spec = libs.get(library_id)
    if not isinstance(spec, dict):
        return 0
    rel = spec.get("path") or ""
    primary = root / str(rel).strip()
    warnings: List[str] = []

    if primary.is_file():
        ext = primary.suffix.lower()
        if ext == ".zip":
            return 0
        try:
            data = primary.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return 0
        return _word_count(data)

    if primary.is_dir():
        w, _ = _walk_count_words(primary, frozenset({".md", ".yaml", ".yml", ".txt", ".py"}))
        return w

    # Try _extracted/{library_id}
    extracted = root / "template_expand" / "_extracted" / library_id
    if extracted.is_dir():
        w, _ = _walk_count_words(extracted, frozenset({".md", ".yaml", ".yml", ".txt"}))
        if w:
            return w

    if rel and not primary.exists():
        warnings.append(f"path_missing:{rel}")
    return 0


def summarize_library(
    library_id: str,
    repo_root: Optional[Path] = None,
) -> LegacyTemplateLibrary:
    """Inventory helper — words + file count for an index entry."""
    root = repo_root or REPO_ROOT
    index = load_legacy_template_index(repo_root=root)
    libs = index.get("libraries") or {}
    spec = libs.get(library_id)
    warnings: List[str] = []
    if not isinstance(spec, dict):
        return LegacyTemplateLibrary(
            library_id=library_id,
            root=root,
            status="missing",
            role="",
            files_found=0,
            total_words=0,
            warnings=["unknown_library"],
        )
    rel = spec.get("path") or ""
    role = str(spec.get("role") or "")
    primary = root / str(rel).strip()
    status = "available" if primary.exists() else "missing"
    if status == "missing":
        warnings.append(f"path_missing:{rel}")
    words = estimate_legacy_library_words(library_id, repo_root=root)
    files_found = 0
    if primary.is_file():
        files_found = 1
    elif primary.is_dir():
        _, files_found = _walk_count_words(
            primary, frozenset({".md", ".yaml", ".yml", ".txt", ".py"})
        )
    return LegacyTemplateLibrary(
        library_id=library_id,
        root=primary,
        status=status,
        role=role,
        files_found=files_found,
        total_words=words,
        warnings=warnings,
    )
