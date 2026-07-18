"""
ei.corpus — read-only loaders for the Phoenix Omega corpora.

Everything here READS. Nothing writes to SOURCE_OF_TRUTH or production config.
This is the shared data layer for all P0 modules.

Inputs:
  - 15 teacher banks  : SOURCE_OF_TRUTH/teacher_banks/<id>/approved_atoms/<TYPE>/*.yaml
                        + .../doctrine/doctrine.yaml (forbidden_claims, etc.)
  - 15 composite docs : SOURCE_OF_TRUTH/composite_doctrine/<topic>/CANONICAL.txt
                        (multiple "## COMPOSITE_DOCTRINE vNN" synthesis blocks)
  - gold-ref books    : artifacts/pipeline_examples/<teacher>/book_<teacher>_<topic>_15min.txt
  - personas          : config/catalog_planning/canonical_personas.yaml
  - somatic spine     : config/spines/somatic_healing_spine.yaml
  - KB EI v2 loads    : artifacts/research/kb/entries.jsonl (the 15-entry marketing KB)
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

import yaml

from . import config as C


# ---------------------------------------------------------------------------
# Atoms
# ---------------------------------------------------------------------------
@dataclass
class Atom:
    atom_id: str
    teacher_id: str
    atom_type: str          # COMPRESSION, HOOK, INTEGRATION, ...
    band: str               # universal | <persona band>
    body: str
    path: str = ""
    extra: dict = field(default_factory=dict)

    @property
    def text(self) -> str:
        return self.body or ""


def _read_yaml(path: Path) -> dict:
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def iter_atoms(teacher_ids: list[str] | None = None,
               atom_types: list[str] | None = None) -> Iterator[Atom]:
    """Yield every approved Atom (optionally filtered by teacher / type)."""
    teachers = teacher_ids or C.all_teacher_ids()
    for tid in teachers:
        approved = C.TEACHER_BANKS / tid / "approved_atoms"
        if not approved.is_dir():
            continue
        for type_dir in sorted(approved.iterdir()):
            if not type_dir.is_dir():
                continue
            atype = type_dir.name
            if atom_types and atype not in atom_types:
                continue
            for yml in sorted(type_dir.glob("*.yaml")):
                d = _read_yaml(yml)
                if not d:
                    continue
                body = d.get("body") or d.get("text") or ""
                if not isinstance(body, str) or not body.strip():
                    continue
                t = d.get("teacher") or {}
                tid_actual = (t.get("teacher_id") if isinstance(t, dict) else None) or tid
                yield Atom(
                    atom_id=str(d.get("atom_id") or yml.stem),
                    teacher_id=str(tid_actual),
                    atom_type=atype,
                    band=str(d.get("band") or "universal"),
                    body=body.strip(),
                    path=str(yml.relative_to(C.REPO_ROOT)) if str(yml).startswith(str(C.REPO_ROOT)) else str(yml),
                    extra={k: v for k, v in d.items() if k not in {"atom_id", "teacher", "band", "body"}},
                )


_ATOM_CACHE = {}


def load_atoms(use_cache: bool = True, **kw) -> list[Atom]:
    """
    Load atoms. With use_cache (default) and no filters, persist the parsed atom
    list to one pickle so re-runs skip the slow 2,418-file YAML parse (the FS is
    heavily contended on this host). In-process memo also avoids re-parsing.
    """
    key = (tuple(sorted(kw.get("teacher_ids") or [])), tuple(sorted(kw.get("atom_types") or [])))
    if use_cache and key in _ATOM_CACHE:
        return _ATOM_CACHE[key]

    # disk cache only for the full unfiltered load (the expensive common case)
    if use_cache and not kw.get("teacher_ids") and not kw.get("atom_types"):
        import pickle
        C.ensure_dirs()
        p = C.CACHE_DIR / "atoms_all.pkl"
        if p.exists():
            try:
                atoms = pickle.loads(p.read_bytes())
                _ATOM_CACHE[key] = atoms
                return atoms
            except Exception:
                pass
        atoms = list(iter_atoms(**kw))
        try:
            p.write_bytes(pickle.dumps(atoms))
        except Exception:
            pass
        _ATOM_CACHE[key] = atoms
        return atoms

    atoms = list(iter_atoms(**kw))
    if use_cache:
        _ATOM_CACHE[key] = atoms
    return atoms


# ---------------------------------------------------------------------------
# Doctrine (forbidden_claims / prohibited_outcomes / prohibited_terms)
# ---------------------------------------------------------------------------
@dataclass
class Doctrine:
    teacher_id: str
    display_name: str
    tradition: str
    core_principles: str
    forbidden_claims: list[str] = field(default_factory=list)
    prohibited_outcomes: list[str] = field(default_factory=list)
    prohibited_terms: list[str] = field(default_factory=list)
    glossary: list[str] = field(default_factory=list)
    raw: dict = field(default_factory=dict)


def _as_list(v) -> list[str]:
    if v is None:
        return []
    if isinstance(v, str):
        return [v]
    if isinstance(v, list):
        return [str(x) for x in v]
    return []


def load_doctrine(teacher_id: str) -> Doctrine | None:
    p = C.TEACHER_BANKS / teacher_id / "doctrine" / "doctrine.yaml"
    d = _read_yaml(p)
    if not d:
        return None
    return Doctrine(
        teacher_id=str(d.get("teacher_id") or teacher_id),
        display_name=str(d.get("display_name") or teacher_id),
        tradition=str(d.get("tradition") or ""),
        core_principles=str(d.get("core_principles") or ""),
        forbidden_claims=_as_list(d.get("forbidden_claims")),
        prohibited_outcomes=_as_list(d.get("prohibited_outcomes")),
        prohibited_terms=_as_list(d.get("prohibited_terms")),
        glossary=_as_list(d.get("glossary")),
        raw=d,
    )


def all_doctrines() -> dict[str, Doctrine]:
    out = {}
    for tid in C.all_teacher_ids():
        doc = load_doctrine(tid)
        if doc:
            out[tid] = doc
    return out


def doctrine_corpus_text(teacher_id: str) -> str:
    """A flat text blob of a teacher's doctrine for embedding (the 15 doctrines)."""
    doc = load_doctrine(teacher_id)
    if not doc:
        return ""
    parts = [doc.display_name, doc.tradition, doc.core_principles]
    parts += doc.glossary
    return "\n".join(p for p in parts if p)


# ---------------------------------------------------------------------------
# Composite doctrine — the human-authored cross-teacher synthesis (the oracle).
# Each CANONICAL.txt holds multiple "## COMPOSITE_DOCTRINE vNN" blocks, each
# beginning with a one-line THESIS, then prose.
# ---------------------------------------------------------------------------
@dataclass
class CompositeSynthesis:
    topic: str
    version: str           # "v01", "v02", ...
    thesis: str            # the opening one-line claim
    body: str              # full prose block


_BLOCK_RE = re.compile(r"##\s*COMPOSITE_DOCTRINE\s*(v\d+)\s*", re.IGNORECASE)


def load_composite(topic: str) -> list[CompositeSynthesis]:
    p = C.COMPOSITE_DOCTRINE / topic / "CANONICAL.txt"
    if not p.exists() or p.stat().st_size == 0:
        # NOTE (real finding 2026-06-13): on origin/main only `anxiety` has
        # authored content (34KB, 15 vNN blocks). The other 14 topic
        # CANONICAL.txt files are committed as the empty blob
        # (e69de29b...). The composite_doctrine oracle is therefore
        # ANXIETY-ONLY today. This is surfaced honestly in EI_P0_RESULTS.md;
        # it sharpens the lead experiment rather than weakening it.
        return []
    text = p.read_text(encoding="utf-8", errors="replace")
    out: list[CompositeSynthesis] = []
    # split on the version headers
    parts = _BLOCK_RE.split(text)
    # parts = [pre, v01, body01, v02, body02, ...]
    for i in range(1, len(parts) - 1, 2):
        ver = parts[i].strip()
        body = parts[i + 1]
        # strip leading separators/blank lines, take first non-empty line as thesis
        lines = [ln.rstrip() for ln in body.splitlines()]
        cleaned = []
        thesis = ""
        for ln in lines:
            s = ln.strip()
            if not s or set(s) <= set("-—_= "):
                if not cleaned:
                    continue  # skip leading separators
            if not thesis and s and not (set(s) <= set("-—_= ")):
                thesis = s
            cleaned.append(ln)
        body_text = "\n".join(cleaned).strip()
        if body_text:
            out.append(CompositeSynthesis(topic=topic, version=ver, thesis=thesis, body=body_text))
    return out


def all_composites() -> list[CompositeSynthesis]:
    out: list[CompositeSynthesis] = []
    for topic in C.composite_topics():
        out.extend(load_composite(topic))
    return out


# ---------------------------------------------------------------------------
# Gold-ref books (for the Reader Council)
# ---------------------------------------------------------------------------
def find_gold_ref_books() -> list[Path]:
    if not C.PIPELINE_EXAMPLES.exists():
        return []
    return sorted(C.PIPELINE_EXAMPLES.glob("*/book_*_15min.txt"))


def load_gold_ref(path: Path) -> str:
    return Path(path).read_text(encoding="utf-8", errors="replace")


def pick_gold_ref(teacher: str | None = None, topic: str | None = None) -> Path | None:
    books = find_gold_ref_books()
    for b in books:
        name = b.name
        if teacher and f"book_{teacher}_" not in name:
            continue
        if topic and f"_{topic}_" not in name:
            continue
        return b
    return books[0] if books else None


# ---------------------------------------------------------------------------
# Personas
# ---------------------------------------------------------------------------
def load_persona_ids() -> list[str]:
    p = C.CONFIG_DIR / "catalog_planning" / "canonical_personas.yaml"
    d = _read_yaml(p)
    return [str(x) for x in (d.get("personas") or [])]


# ---------------------------------------------------------------------------
# The KB EI v2 actually loads (the motivating fact: it's marketing, not doctrine)
# ---------------------------------------------------------------------------
def load_ei_v2_kb() -> list[dict]:
    if not C.KB_ENTRIES.exists():
        return []
    out = []
    for line in C.KB_ENTRIES.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    return out
