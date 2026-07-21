#!/usr/bin/env python3
"""Helper for translation agents: split a CANONICAL.txt into atoms (preserving
header/metadata/separators exactly) and reassemble with translated bodies.

Handles three atom-bank shapes found in the repo:
  A. Canonical double-separator: "## ROLE vNN" / "---" / metadata lines / "---" / body / "---"
  B. Legacy single-separator (some entrepreneurs/first_responders/... INTEGRATION
     banks): "## ROLE vNN" / "---" / pseudo-metadata key: value lines / BLANK LINE /
     body / "---" (no second "---" closing the metadata).
  C. Legacy bare-variant TAKEAWAY banks (some entrepreneurs/first_responders/...
     TAKEAWAY banks): no "## ROLE vNN" header at all, just "--- variant: vNN" then
     one body paragraph then a blank line, repeated. No closing "---" anywhere.

Also tolerates:
  - truncated files missing the final closing "---" (last atom runs to EOF)
  - empty "stub" atoms (header + one "---" then immediately the next atom, no body)

In all cases, ONLY the body substring is ever replaced on reassembly - header,
metadata, and every separator/blank-line byte is sliced verbatim from the
original source text, so output is byte-identical to source except for the
translated body text.

Usage:
  extract  <src_path> <out_json>
      Writes {"format": "A"|"C", "atoms": [{"header": str, "body": str}, ...]}
      to out_json. "body" is the English prose to be translated, in file order.

  assemble <src_path> <translations_json> <out_path>
      translations_json is a JSON list of translated body strings, in the same
      order as returned by extract. Rebuilds the file byte-identically except
      each atom's body is replaced by the corresponding translated string.
"""
import json
import re
import sys
from pathlib import Path

HEADER_RE = re.compile(r"^## \S+ v\d+\s*$")
SEP_RE = re.compile(r"^---\s*$")
VARIANT_RE = re.compile(r"^--- variant: v\d+\s*$")


def _line_offsets(lines):
    offsets = []
    pos = 0
    for ln in lines:
        offsets.append(pos)
        pos += len(ln)
    return offsets


def _extract_body(lines, offsets, text, body_start, stop_fn):
    """Scan forward from body_start until stop_fn(line) is True or EOF.
    Returns (body_text_no_trailing_nl, body_start_off, body_end_off)."""
    k = body_start
    n = len(lines)
    while k < n and not stop_fn(lines[k]):
        k += 1
    body = "".join(lines[body_start:k])
    if body.endswith("\n"):
        body = body[:-1]
    body_start_off = offsets[body_start] if body_start < n else len(text)
    body_end_off = offsets[k] if k < n else len(text)
    return body, body_start_off, body_end_off


def split_file(text: str):
    """Return (fmt, list of atom dicts: {header, body, body_span})."""
    lines = text.splitlines(keepends=True)
    offsets = _line_offsets(lines)
    n = len(lines)

    header_idx = [i for i, ln in enumerate(lines) if HEADER_RE.match(ln.rstrip("\n"))]
    if header_idx:
        atoms = []
        for hi in header_idx:
            header = lines[hi].rstrip("\n")
            i = hi + 1
            if i < n and SEP_RE.match(lines[i].rstrip("\n")):
                meta_start = i + 1
            else:
                # Some legacy blocks skip the opening "---" entirely and go
                # straight from the header into pseudo-metadata/body lines.
                meta_start = i
            # Scan forward to find where the body actually starts: either a
            # closing "---" (format A: real metadata block), a blank line
            # (format B: pseudo-metadata immediately followed by prose), or
            # the next header (a stub atom with no body/metadata at all).
            j = meta_start
            while True:
                if j >= n:
                    body_start = j
                    break
                sline = lines[j].rstrip("\n")
                if SEP_RE.match(sline):
                    body_start = j + 1
                    break
                if HEADER_RE.match(sline):
                    body_start = j
                    break
                if sline.strip() == "":
                    # Blank line: either (a) trailing blank inside an
                    # otherwise-empty metadata block, immediately followed by
                    # its own closing "---" (format A empty-meta shape), or
                    # (b) the meta/body boundary in the legacy
                    # single-separator format (pseudo-metadata directly
                    # followed by prose, no second "---"). Disambiguate by
                    # peeking at the very next line.
                    nxt = lines[j + 1].rstrip("\n") if j + 1 < n else ""
                    if SEP_RE.match(nxt):
                        body_start = j + 2
                    else:
                        body_start = j + 1
                    break
                j += 1

            def stop(ln):
                s = ln.rstrip("\n")
                return SEP_RE.match(s) is not None or HEADER_RE.match(s) is not None

            body, b_start_off, b_end_off = _extract_body(lines, offsets, text, body_start, stop)
            atoms.append({"header": header, "body": body, "body_span": (b_start_off, b_end_off)})
        return "A", atoms

    variant_idx = [i for i, ln in enumerate(lines) if VARIANT_RE.match(ln.rstrip("\n"))]
    if variant_idx:
        atoms = []
        for vi in variant_idx:
            header = lines[vi].rstrip("\n")
            body_start = vi + 1

            def stop(ln):
                s = ln.rstrip("\n")
                return s.strip() == "" or VARIANT_RE.match(s) is not None

            body, b_start_off, b_end_off = _extract_body(lines, offsets, text, body_start, stop)
            atoms.append({"header": header, "body": body, "body_span": (b_start_off, b_end_off)})
        return "C", atoms

    raise SystemExit("no atoms found - check format")


def cmd_extract(src_path, out_json):
    text = Path(src_path).read_text(encoding="utf-8")
    fmt, atoms = split_file(text)
    data = {
        "format": fmt,
        "atoms": [{"header": a["header"], "body": a["body"]} for a in atoms],
    }
    Path(out_json).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"extracted {len(atoms)} atoms (format {fmt}) from {src_path} -> {out_json}")


def cmd_assemble(src_path, translations_json, out_path):
    text = Path(src_path).read_text(encoding="utf-8")
    fmt, atoms = split_file(text)
    translations = json.loads(Path(translations_json).read_text(encoding="utf-8"))
    if len(translations) != len(atoms):
        raise SystemExit(
            f"count mismatch: {len(atoms)} atoms in source vs {len(translations)} translations"
        )

    out = []
    last_end = 0
    for atom, new_body in zip(atoms, translations):
        b_start, b_end = atom["body_span"]
        out.append(text[last_end:b_start])
        if b_start != b_end:
            # There was original content (even if just a blank line) in this
            # span, so exactly one line (ending in \n) always belongs here.
            out.append(new_body + "\n")
        # else: zero-width stub span (header immediately followed by the
        # next atom) - nothing to insert.
        last_end = b_end
    out.append(text[last_end:])
    result = "".join(out)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(result, encoding="utf-8")
    print(f"wrote {out_path} ({len(atoms)} atoms, format {fmt})")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "extract":
        cmd_extract(sys.argv[2], sys.argv[3])
    elif cmd == "assemble":
        cmd_assemble(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print(__doc__)
        sys.exit(1)
