#!/usr/bin/env python3
"""Post-render human atom trace for ANY book render directory.

Reads artifacts the pipeline already writes (section_packet_audit.json + book.txt)
and emits the inline beat → source(file:line) → atom name → text QA view in the
same field shape used by the Ch1/Ch2 human atom traces:

  [SLOT_TYPE]
  What this surface does: ...
  Source: <file:line>
  Atom: <type> / <name>
  Status: ...; fallback: ...
  First rendered sentence: ...
  Previous beat: ...; next beat: ...
  Cohesion/read note: ...

Zero hardcoded persona/topic — both are read from plan.json (or inferred).
Never fabricates a source path when unresolvable.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).resolve().parents[2]

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
_HEADER_LINE_RE = re.compile(r"^##\s+(.+?)\s*$")
_ROLE_V_RE = re.compile(r"^[A-Z][A-Z0-9_ ]*\s+v\d+$")


@dataclass
class ResolvedSource:
    rel_path: str
    line: int
    atom_type: str
    atom_id: str
    bank_text: str
    status: str
    fallback: str


@dataclass
class TraceSlot:
    chapter: int
    slot_index: int
    slot_type: str
    source: str
    source_id: str
    variant_id: str
    words: int
    resolved: ResolvedSource
    rendered_text: str


@dataclass
class _AtomHit:
    rel_path: str
    line: int
    atom_id: str
    content: str


@dataclass
class BankIndex:
    """One-pass index of persona + composite CANONICAL banks for a cell."""

    repo_root: Path
    persona_id: str
    topic_id: str
    by_id: dict[str, _AtomHit] = field(default_factory=dict)
    angle_registry_lines: dict[str, int] = field(default_factory=dict)
    _built: bool = False

    def build(self) -> None:
        if self._built:
            return
        self._built = True
        if self.persona_id and self.topic_id:
            root = self.repo_root / "atoms" / self.persona_id / self.topic_id
            if root.is_dir():
                for path in sorted(root.rglob("CANONICAL.txt")):
                    # Skip non-en locale variants unless they are the only copy
                    if "/locales/" in str(path).replace("\\", "/"):
                        continue
                    self._index_canonical(path)
        if self.topic_id:
            for path in (
                self.repo_root
                / "SOURCE_OF_TRUTH"
                / "composite_doctrine"
                / self.topic_id
                / "CANONICAL.txt",
                self.repo_root
                / "SOURCE_OF_TRUTH"
                / "composite_doctrine"
                / self.topic_id
                / "REFLECTION"
                / "CANONICAL.txt",
            ):
                self._index_canonical(path)
        reg = self.repo_root / "config" / "angles" / "angle_registry.yaml"
        if reg.exists():
            for i, line in enumerate(reg.read_text(encoding="utf-8").splitlines(), 1):
                m = re.match(r"^(\s*)([A-Z][A-Z0-9_]+):\s*$", line)
                if m and len(m.group(1)) <= 2:
                    self.angle_registry_lines[m.group(2)] = i

    def _index_canonical(self, path: Path) -> None:
        if not path.exists():
            return
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            return
        rel = _rel(path, self.repo_root)
        i = 0
        while i < len(lines):
            stripped = lines[i].strip()
            header = ""
            if stripped.startswith("## "):
                header = stripped[3:].strip()
            elif _ROLE_V_RE.match(stripped):
                header = stripped
            if header and _ROLE_V_RE.match(header):
                start = i
                # Collect until next header
                j = i + 1
                while j < len(lines):
                    s = lines[j].strip()
                    if s.startswith("## ") or _ROLE_V_RE.match(s):
                        break
                    j += 1
                block = "\n".join(lines[start:j])
                content = _prose_from_block(block)
                # First write wins (slot-type dirs usually appear before engines
                # in sorted order for same id — but STORY engine ids differ).
                if header not in self.by_id and content:
                    self.by_id[header] = _AtomHit(
                        rel_path=rel,
                        line=start + 1,
                        atom_id=header,
                        content=content,
                    )
                i = j
                continue
            i += 1

    def lookup(self, atom_id: str) -> Optional[ResolvedSource]:
        self.build()
        hit = self.by_id.get(atom_id.strip())
        if not hit:
            return None
        role = hit.atom_id.split()[0] if hit.atom_id else "ATOM"
        return ResolvedSource(
            rel_path=hit.rel_path,
            line=hit.line,
            atom_type=role,
            atom_id=hit.atom_id,
            bank_text=hit.content,
            status="resolved",
            fallback="none",
        )


def _rel(path: Path, root: Path = ROOT) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def _prose_from_block(block: str) -> str:
    """Extract prose from a ## header block with --- delimiters."""
    lines = block.splitlines()
    if not lines:
        return ""
    # Drop header line
    body = "\n".join(lines[1:])
    parts = [p.strip() for p in re.split(r"\n---\s*\n", "\n" + body + "\n")]
    parts = [p.strip("\n") for p in parts if p.strip() and p.strip() != "---"]
    # parts[0] may be empty/meta; prefer last non-meta-looking segment with prose
    candidates = []
    for p in parts:
        text = p.strip().strip("-").strip()
        if not text:
            continue
        # Skip pure metadata blobs
        meta_lines = text.splitlines()
        if meta_lines and all(
            (":" in ln and len(ln) < 80) or not ln.strip() for ln in meta_lines[:3]
        ) and len(text) < 200 and "\n\n" not in text:
            # likely metadata only
            if not any(c in text for c in ".!?"):
                continue
        candidates.append(text)
    if not candidates:
        return ""
    return candidates[-1].strip()


def _first_sentence(text: str) -> str:
    cleaned = " ".join((text or "").split()).strip()
    if not cleaned:
        return ""
    parts = _SENTENCE_SPLIT.split(cleaned, maxsplit=1)
    return parts[0].strip()


def _load_slots(audit_path: Path) -> list[dict[str, Any]]:
    raw = json.loads(audit_path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return [s for s in raw if isinstance(s, dict)]
    if isinstance(raw, dict):
        slots = raw.get("slots")
        if isinstance(slots, list):
            return [s for s in slots if isinstance(s, dict)]
    raise ValueError(f"Unrecognized section_packet_audit shape: {audit_path}")


def _load_plan_context(render_dir: Path) -> dict[str, str]:
    persona = ""
    topic = ""
    locale = "en-US"
    plan_path = render_dir / "plan.json"
    if plan_path.exists():
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        if isinstance(plan, dict):
            persona = str(plan.get("persona_id") or "").strip()
            topic = str(plan.get("topic_id") or "").strip()
            locale = str(plan.get("locale") or locale).strip() or locale
    if not persona or not topic:
        parts = render_dir.name.split("__")
        if len(parts) >= 2:
            persona = persona or parts[0]
            topic = topic or parts[1]
    return {"persona_id": persona, "topic_id": topic, "locale": locale}


def _primary_atom_id(source_id: str) -> str:
    sid = (source_id or "").strip()
    if not sid:
        return ""
    if "+" in sid and not sid.startswith("angle_"):
        return sid.split("+", 1)[0].strip()
    return sid


def _resolve_angle(
    *,
    source_id: str,
    persona_id: str,
    topic_id: str,
    repo_root: Path,
    index: BankIndex,
) -> Optional[ResolvedSource]:
    sid = (source_id or "").strip()
    if sid.startswith("angle_def:"):
        aid = sid.split(":", 1)[1].strip()
        path = (
            repo_root
            / "atoms"
            / persona_id
            / topic_id
            / "ANGLE_DEFINITION"
            / aid
            / "CANONICAL.txt"
        )
        if path.exists():
            body = path.read_text(encoding="utf-8").strip()
            return ResolvedSource(
                rel_path=_rel(path, repo_root),
                line=1,
                atom_type="ANGLE_DEFINITION",
                atom_id=sid,
                bank_text=body,
                status="resolved",
                fallback="none",
            )
        index.build()
        line = index.angle_registry_lines.get(aid, 0)
        if line:
            return ResolvedSource(
                rel_path=_rel(repo_root / "config" / "angles" / "angle_registry.yaml", repo_root),
                line=line,
                atom_type="ANGLE_REGISTRY",
                atom_id=sid,
                bank_text="",
                status="registry_pointer",
                fallback="none",
            )
        return None
    if sid.startswith("angle_cb:"):
        parts = sid.split(":")
        aid = parts[1] if len(parts) > 1 else ""
        layer = parts[2][1:] if len(parts) > 2 and parts[2].startswith("L") else ""
        if aid and layer:
            path = (
                repo_root
                / "atoms"
                / persona_id
                / topic_id
                / "ANGLE_CALLBACK"
                / aid
                / f"level_{layer}.yaml"
            )
            if path.exists():
                body = ""
                try:
                    import yaml

                    data = yaml.safe_load(path.read_text(encoding="utf-8"))
                    if isinstance(data, dict):
                        body = str(data.get("body") or data.get("content") or "").strip()
                except Exception:
                    body = path.read_text(encoding="utf-8")
                return ResolvedSource(
                    rel_path=_rel(path, repo_root),
                    line=1,
                    atom_type="ANGLE_CALLBACK",
                    atom_id=sid,
                    bank_text=body,
                    status="resolved",
                    fallback="none",
                )
        return None
    return None


def _resolve_accent_narrow(
    source_id: str, topic_id: str, repo_root: Path
) -> Optional[ResolvedSource]:
    """Narrow accent lookup — topic entries only (no full-tree scan)."""
    sid = (source_id or "").strip()
    if not sid or not topic_id:
        return None
    banks = repo_root / "SOURCE_OF_TRUTH" / "accent_banks"
    if not banks.is_dir():
        return None
    for path in sorted(banks.glob(f"*/{topic_id}/entries.yaml")):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if sid not in text:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if sid in line:
                return ResolvedSource(
                    rel_path=_rel(path, repo_root),
                    line=i,
                    atom_type="ACCENT",
                    atom_id=sid,
                    bank_text="",
                    status="resolved",
                    fallback="none",
                )
    return None


def resolve_slot_source(
    *,
    slot: dict[str, Any],
    persona_id: str,
    topic_id: str,
    repo_root: Path,
    index: BankIndex,
) -> ResolvedSource:
    source = str(slot.get("source") or "").strip()
    source_id = str(slot.get("source_id") or "").strip()
    slot_type = str(slot.get("slot_type") or "").strip().upper()
    primary_id = _primary_atom_id(source_id)

    unresolved = ResolvedSource(
        rel_path=f"<unresolved:{source_id or source or slot_type or 'unknown'}>",
        line=0,
        atom_type=source or slot_type or "UNKNOWN",
        atom_id=source_id or primary_id or slot_type or "UNKNOWN",
        bank_text="",
        status="unresolved",
        fallback="unresolved",
    )

    if not source_id and not source:
        return unresolved

    if source.startswith("angle") or source_id.startswith("angle_"):
        hit = _resolve_angle(
            source_id=source_id,
            persona_id=persona_id,
            topic_id=topic_id,
            repo_root=repo_root,
            index=index,
        )
        return hit or unresolved

    if "composite" in source or primary_id.upper().startswith("COMPOSITE_"):
        hit = index.lookup(primary_id)
        if hit:
            return hit
        return unresolved

    if source.startswith("persona_atom") or _ROLE_V_RE.match(primary_id):
        hit = index.lookup(primary_id)
        if hit:
            if "+" in source_id:
                hit.atom_id = source_id
                hit.status = "resolved_persona_half"
            return hit

    # Accents only when id looks accent-like (avoid scanning on every miss)
    if source_id.startswith("rq_") or source_id.startswith("ext_") or "accent" in source:
        hit = _resolve_accent_narrow(source_id, topic_id, repo_root)
        if hit:
            return hit

    hit = index.lookup(primary_id)
    if hit:
        return hit
    return unresolved


def slice_rendered_texts(
    book_text: str,
    slots: list[dict[str, Any]],
    resolved: list[ResolvedSource],
) -> list[str]:
    """Prefer locating bank prose in book.txt; fall back to word-count walk."""
    cursor = 0
    out: list[str] = []
    words = book_text.split()
    word_cursor = 0

    for slot, res in zip(slots, resolved):
        claimed = int(slot.get("words") or 0)
        text = ""
        bank = (res.bank_text or "").strip()
        if bank:
            bank_words = bank.split()
            probes = []
            for n in (40, 24, 16, 12, 8, 5):
                if len(bank_words) >= n:
                    probes.append(" ".join(bank_words[:n]))
            if bank_words:
                probes.append(bank_words[0])
            found_at = -1
            matched_probe = ""
            search_from = max(0, cursor - 200)
            for probe in probes:
                idx = book_text.find(probe, search_from)
                if idx < 0:
                    idx = book_text.find(probe)
                if idx >= 0:
                    found_at = idx
                    matched_probe = probe
                    break
            if found_at >= 0:
                window_words = book_text[found_at:].split()
                take = claimed if claimed > 0 else len(bank_words)
                take = min(take, len(window_words)) if take else min(len(bank_words), len(window_words))
                text = " ".join(window_words[:take]).strip() if take else matched_probe
                cursor = found_at + max(len(text), len(matched_probe))
                word_cursor = len(book_text[:found_at].split()) + len(text.split())
        if not text and claimed > 0 and word_cursor < len(words):
            chunk = words[word_cursor : word_cursor + claimed]
            text = " ".join(chunk).strip()
            word_cursor += claimed
            if chunk:
                idx = book_text.find(chunk[0], cursor)
                if idx >= 0:
                    cursor = idx + len(text)
        if not text and bank:
            text = bank
        out.append(text)
    return out


def surface_purpose(slot_type: str, source: str) -> str:
    st = (slot_type or "SLOT").strip().upper() or "SLOT"
    src = (source or "unknown").strip() or "unknown"
    return f"Rendered {st} surface from {src}."


def render_trace(slots: list[TraceSlot], *, title: str = "Human Atom Trace") -> str:
    """Emit the Ch1/Ch2 human atom trace field shape (exact labels)."""
    lines = [f"# {title}", ""]
    for index, slot in enumerate(slots):
        prev_surface = slots[index - 1].slot_type if index else "START"
        next_surface = slots[index + 1].slot_type if index + 1 < len(slots) else "END"
        src = slot.resolved
        if src.line > 0 and not src.rel_path.startswith("<unresolved:"):
            source_line = f"{src.rel_path}:{src.line}"
        elif src.rel_path.startswith("<unresolved:"):
            source_line = src.rel_path
        else:
            source_line = f"<unresolved:{slot.source_id}>"
        first = _first_sentence(slot.rendered_text) or _first_sentence(src.bank_text) or "(empty)"
        lines.extend(
            [
                f"[{slot.slot_type}]",
                f"What this surface does: {surface_purpose(slot.slot_type, slot.source)}",
                f"Source: {source_line}",
                f"Atom: {src.atom_type} / {src.atom_id}",
                f"Status: {src.status}; fallback: {src.fallback}",
                f"First rendered sentence: {first}",
                f"Previous beat: {prev_surface}; next beat: {next_surface}",
                "Cohesion/read note: Source-backed from section_packet_audit + bank resolution; "
                "rendered text taken from book.txt when locatable.",
                "",
                f"Rendered text ({slot.words} words claimed):",
                slot.rendered_text.strip() if slot.rendered_text.strip() else "(no rendered text recovered)",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def build_atom_trace(
    render_dir: Path,
    *,
    repo_root: Path = ROOT,
    title: Optional[str] = None,
) -> tuple[str, dict[str, Any]]:
    render_dir = render_dir.resolve()
    audit_path = render_dir / "section_packet_audit.json"
    book_path = render_dir / "book.txt"
    if not audit_path.exists():
        raise FileNotFoundError(f"Missing {audit_path}")
    if not book_path.exists():
        raise FileNotFoundError(f"Missing {book_path}")

    ctx = _load_plan_context(render_dir)
    persona_id = ctx["persona_id"]
    topic_id = ctx["topic_id"]
    raw_slots = _load_slots(audit_path)
    book_text = book_path.read_text(encoding="utf-8")

    index = BankIndex(repo_root=repo_root, persona_id=persona_id, topic_id=topic_id)
    index.build()

    resolved: list[ResolvedSource] = [
        resolve_slot_source(
            slot=s,
            persona_id=persona_id,
            topic_id=topic_id,
            repo_root=repo_root,
            index=index,
        )
        for s in raw_slots
    ]
    texts = slice_rendered_texts(book_text, raw_slots, resolved)

    trace_slots: list[TraceSlot] = []
    for s, res, text in zip(raw_slots, resolved, texts):
        trace_slots.append(
            TraceSlot(
                chapter=int(s.get("chapter") or 0),
                slot_index=int(s.get("slot_index") or 0),
                slot_type=str(s.get("slot_type") or "SLOT").strip().upper() or "SLOT",
                source=str(s.get("source") or ""),
                source_id=str(s.get("source_id") or ""),
                variant_id=str(s.get("variant_id") or ""),
                words=int(s.get("words") or 0),
                resolved=res,
                rendered_text=text,
            )
        )

    heading = title or (
        f"Human Atom Trace — {persona_id or '?'} / {topic_id or '?'} — {render_dir.name}"
    )
    body = render_trace(trace_slots, title=heading)
    unresolved = sum(1 for t in trace_slots if t.resolved.status == "unresolved")
    summary = {
        "render_dir": _rel(render_dir, repo_root),
        "persona_id": persona_id,
        "topic_id": topic_id,
        "slot_count": len(trace_slots),
        "resolved_count": len(trace_slots) - unresolved,
        "unresolved_count": unresolved,
        "book_words": len(book_text.split()),
        "indexed_atoms": len(index.by_id),
    }
    return body, summary


def write_atom_trace(
    render_dir: Path,
    *,
    out_path: Optional[Path] = None,
    repo_root: Path = ROOT,
) -> Path:
    body, summary = build_atom_trace(render_dir, repo_root=repo_root)
    dest = out_path or (render_dir / "human_atom_trace.txt")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(body, encoding="utf-8")
    summary_path = dest.with_name(dest.name.replace(".txt", "") + ".summary.json")
    if dest.name == "human_atom_trace.txt":
        summary_path = dest.with_name("human_atom_trace.summary.json")
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return dest


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Emit human_atom_trace.txt for any pipeline render directory."
    )
    parser.add_argument("render_dir", type=Path, help="Directory with section_packet_audit.json + book.txt")
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output path (default: <render_dir>/human_atom_trace.txt)",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=ROOT,
        help="Repository root for atom-bank resolution",
    )
    args = parser.parse_args(argv)
    try:
        dest = write_atom_trace(args.render_dir, out_path=args.out, repo_root=args.repo_root)
        summary_path = dest.with_name("human_atom_trace.summary.json")
        if args.out and args.out.name != "human_atom_trace.txt":
            summary_path = dest.with_suffix(".summary.json")
        if not summary_path.exists():
            # write_atom_trace naming for custom --out
            alt = dest.with_name(dest.stem + ".summary.json")
            summary_path = alt if alt.exists() else summary_path
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"render_atom_trace: ERROR — {exc}", file=sys.stderr)
        return 1
    print(f"Human atom trace: {dest}")
    print(
        f"  slots={summary['slot_count']} resolved={summary['resolved_count']} "
        f"unresolved={summary['unresolved_count']} "
        f"persona={summary['persona_id']!r} topic={summary['topic_id']!r}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
