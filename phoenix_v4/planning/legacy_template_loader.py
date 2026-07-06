"""
Load legacy audiobook template slices (YAML under extracted trees, bridges markdown).

Never raises for missing content — returns structured dataclasses with warnings.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Per-library roots: cached list of .yaml/.yml paths for fallback resolution.
_LIBRARY_YAML_CACHE: Dict[str, List[Path]] = {}

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


def resolve_template_library(
    topic: str,
    persona: str,
    runtime_format: str,
    routing_config_path: str = "config/templates/catalog_template_routing.yaml",
) -> str:
    """
    Returns template library name for topic × persona × format.
    Always returns a string. Falls back to 'spine_only' on any miss.
    Cells with a twelve_shape continuity plan route to spine_only (promise_engine spine).
    """
    try:
        from phoenix_v4.planning.chapter_object_continuity import load_chapter_continuity_plan

        if load_chapter_continuity_plan(persona, topic):
            return "spine_only"
    except ImportError:
        pass
    try:
        import yaml as _yaml
    except ImportError:
        return "spine_only"
    try:
        cfg = _yaml.safe_load(open(routing_config_path))
    except FileNotFoundError:
        return "spine_only"

    topic_family = next(
        (fam for fam, topics in cfg["topic_families"].items()
         if topic in topics), None)
    persona_tier = next(
        (tier for tier, personas in cfg["persona_tiers"].items()
         if persona in personas), None)

    if topic_family and persona_tier:
        library = (cfg["routing"]
                   .get(topic_family, {})
                   .get(persona_tier, {})
                   .get(runtime_format, cfg["fallback"]))
    else:
        library = cfg["fallback"]

    return library or cfg["fallback"]


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


def _maybe_descend_sections_somatic_v2(root: Path) -> Path:
    """
    When the index path is the zip wrapper (qaudiobook_template_v2_somatic/),
    section YAML lives under sections_somatic_v2/. Descend if that child exists.
    """
    nested = root / "sections_somatic_v2"
    return nested if nested.is_dir() else root


def _unwrap_single_dir_root(root: Path) -> Path:
    """
    If the archive extracted as a single top-level folder (e.g. one wrapper dir),
    descend so chapter_* lives directly under the effective root.
    """
    cur = root
    for _ in range(4):
        if not cur.is_dir():
            return cur
        subs = [p for p in cur.iterdir() if p.is_dir()]
        files = [p for p in cur.iterdir() if p.is_file()]
        if files or len(subs) != 1:
            return cur
        only = subs[0]
        if only.name.startswith("chapter_"):
            return cur
        cur = only
    return cur


def _candidate_roots_for_library(
    library_id: str,
    spec: Dict[str, Any],
    repo_root: Path,
) -> List[Path]:
    """Ordered search roots: index path, _extracted/<zip stem>, _extracted/<library_id>."""
    roots: List[Path] = []
    rel = str(spec.get("path") or "").strip()
    if rel:
        roots.append(repo_root / rel)
    arch = spec.get("archive")
    if arch:
        arch_path = Path(str(arch))
        stem = arch_path.stem
        if str(arch_path).startswith("template_expand2/"):
            roots.append(repo_root / "template_expand2" / "_extracted" / stem)
        else:
            roots.append(repo_root / "template_expand" / "_extracted" / stem)
    roots.append(repo_root / "template_expand" / "_extracted" / library_id)
    roots.append(repo_root / "template_expand2" / "_extracted" / library_id)

    seen: set[str] = set()
    out: List[Path] = []
    for r in roots:
        key = str(r.resolve()) if r.exists() else str(r)
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def _chapter_section_dir_names(chapter: int, section: int) -> tuple[List[str], List[str]]:
    ch_dirs = [f"chapter_{chapter:02d}", f"chapter_{chapter}"]
    sec_dirs = [f"section_{section:02d}", f"section_{section}"]
    return ch_dirs, sec_dirs


def _variant_f_filename(variant_family: str) -> tuple[str, str]:
    """
    Somatic v2 layout uses f1.yaml … f5.yaml (lowercase) under section_NN_type dirs.
    """
    fam = variant_family.strip().upper()
    if fam.startswith("F") and fam[1:].isdigit():
        n = int(fam[1:])
        base = f"f{n}.yaml"
        return base, f"f{n}.yml"
    return "f1.yaml", "f1.yml"


def _resolve_somatic_v2_section_path(
    root: Path,
    chapter: int,
    section: int,
    variant_family: str,
) -> Optional[Path]:
    """
    Resolve sections_somatic_v2 layout:
      chapter_NN/section_NN_<type>/fN.yaml
    Section index 1..10 maps to the single directory whose name starts with section_NN_.
    """
    f_yaml, f_yml = _variant_f_filename(variant_family)
    for ch_name in (f"chapter_{chapter:02d}", f"chapter_{chapter}"):
        ch_dir = root / ch_name
        if not ch_dir.is_dir():
            continue
        prefix = f"section_{section:02d}_"
        matches = sorted(
            p for p in ch_dir.iterdir() if p.is_dir() and p.name.startswith(prefix)
        )
        if not matches:
            continue
        sec_dir = matches[0]
        for fn in (f_yaml, f_yml):
            p = sec_dir / fn
            if p.is_file():
                return p
    return None


def _list_yaml_under_root(root: Path) -> List[Path]:
    key = str(root.resolve())
    if key not in _LIBRARY_YAML_CACHE:
        if not root.is_dir():
            _LIBRARY_YAML_CACHE[key] = []
        else:
            _LIBRARY_YAML_CACHE[key] = [
                p
                for p in root.rglob("*")
                if p.is_file() and p.suffix.lower() in (".yaml", ".yml")
            ]
    return list(_LIBRARY_YAML_CACHE[key])


def clear_legacy_template_path_cache() -> None:
    """Tests or extraction reruns may call this to drop cached scans."""
    _LIBRARY_YAML_CACHE.clear()


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

    fam = variant_family.strip().upper()
    if not fam.startswith("F"):
        fam = f"F{fam}" if fam.isdigit() else fam
    fname_yaml = f"variant_{fam}.yaml"
    fname_yml = f"variant_{fam}.yml"

    rel = str(spec.get("path") or "").strip()
    primary = repo_root / rel if rel else None
    ch_names, sec_names = _chapter_section_dir_names(chapter, section)

    for raw_root in _candidate_roots_for_library(library_id, spec, repo_root):
        root = _maybe_descend_sections_somatic_v2(_unwrap_single_dir_root(raw_root))
        if not root.is_dir():
            continue
        for cd in ch_names:
            for sd in sec_names:
                for fn in (fname_yaml, fname_yml):
                    p = root / cd / sd / fn
                    if p.is_file():
                        return p, warnings

        p2 = _resolve_somatic_v2_section_path(root, chapter, section, variant_family)
        if p2 is not None:
            return p2, warnings

    # Fallback: scan cached yaml list for chapter_NN/section_NN/variant_{fam}.*
    ch_tag = f"chapter_{chapter:02d}"
    sec_tag = f"section_{section:02d}"
    fam_lower = fam.lower()
    for raw_root in _candidate_roots_for_library(library_id, spec, repo_root):
        root = _maybe_descend_sections_somatic_v2(_unwrap_single_dir_root(raw_root))
        if not root.is_dir():
            continue
        for p in _list_yaml_under_root(root):
            parts_lower = [x.lower() for x in p.relative_to(root).parts]
            try:
                ci = parts_lower.index(ch_tag)
                parts_lower.index(sec_tag, ci)
            except ValueError:
                continue
            leaf = p.name.lower()
            if leaf.startswith("variant_") and fam_lower in leaf:
                return p, warnings

    # Somatic v2 fallback: chapter_NN/section_NN_*/fN.yaml
    f_expect, _ = _variant_f_filename(variant_family)
    f_expect_l = f_expect.lower()
    sec_prefix = f"section_{section:02d}_"
    for raw_root in _candidate_roots_for_library(library_id, spec, repo_root):
        root = _maybe_descend_sections_somatic_v2(_unwrap_single_dir_root(raw_root))
        if not root.is_dir():
            continue
        for p in _list_yaml_under_root(root):
            parts_lower = [x.lower() for x in p.relative_to(root).parts]
            try:
                ci = parts_lower.index(ch_tag)
            except ValueError:
                continue
            if not any(x.startswith(sec_prefix) for x in parts_lower[ci + 1 :]):
                continue
            if p.name.lower() == f_expect_l:
                return p, warnings

    if primary and not primary.exists():
        warnings.append(f"library_path_missing:{rel}")
    else:
        warnings.append(
            f"section_yaml_not_found:{library_id}:ch{chapter:02d}:sec{section:02d}:{fname_yaml}"
        )
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

    # Try _extracted/{library_id} under template_expand and template_expand2
    for sub in ("template_expand", "template_expand2"):
        extracted = root / sub / "_extracted" / library_id
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
