#!/usr/bin/env python3
"""Repair lane-fix corruption in the spiral STORY CANONICAL.txt.

Root cause (VERIFY-1 diagnosis): the lane fix that populated
atoms/gen_z_professionals/financial_anxiety/spiral/CANONICAL.txt appended
valid band-fill/capacity-fill atoms (v06+) but left behind 10 EMPTY stub
blocks (header + lone '---', no `path:` line, no body):
  RECOGNITION v02/v04, MECHANISM_PROOF v01/v03/v05,
  TURNING_POINT v02/v04, EMBODIMENT v01/v03/v05
phoenix_v4.planning.assembly_compiler.validate_canonical_atom_file rejects
the WHOLE file on any missing-path block -> _load_story_atoms_for_engine
returns [] -> tuple-viability gate aborts the build with NO_STORY_POOL
(a hard entry gate, before Stage 1).

Fix: drop the empty stub blocks; keep every block that has a real `path:`.
Re-emit in canonical block format. This is corruption removal, not content
authoring -- the stubs hold zero content.
"""
import re
import sys
from pathlib import Path

SRC = Path("atoms/gen_z_professionals/financial_anxiety/spiral/CANONICAL.txt")

text = SRC.read_text()

# Split on header lines "## ROLE vNN". Keep the headers via capture.
parts = re.split(r"(?m)^(##\s+[A-Z_]+\s+v\d+\s*)$", text)
# parts[0] = preamble before first header; then alternating (header, body)...
preamble = parts[0]
blocks = []  # list of (header_text, body_text)
i = 1
while i < len(parts):
    header = parts[i].strip()
    body = parts[i + 1] if i + 1 < len(parts) else ""
    blocks.append((header, body))
    i += 2

kept = []
dropped = []
for header, body in blocks:
    if "path:" in body:
        kept.append((header, body))
    else:
        dropped.append(header)

# Re-emit canonically. Each kept block: header, then its body verbatim
# (body already begins with "\n---\n...path:...\n---\n"). Normalise so each
# block is separated by exactly one blank line and ends with a closing '---'.
out_lines = []
out_lines.append("")  # leading blank to match original style
for header, body in kept:
    # Strip leading/trailing whitespace on the body, then ensure it is
    # wrapped as ---\n<meta/content>\n---
    b = body.strip("\n")
    # body as captured starts with the '---' opener; keep as-is but collapse
    # any trailing blank lines.
    out_lines.append(header)
    out_lines.append(b)
    out_lines.append("")  # one blank line between blocks

out_text = "\n".join(out_lines).rstrip("\n") + "\n"

print(f"blocks total       : {len(blocks)}")
print(f"blocks kept (path) : {len(kept)}")
print(f"blocks dropped     : {len(dropped)}")
print("dropped headers    :")
for d in dropped:
    print("   ", d)

if "--write" in sys.argv:
    SRC.write_text(out_text)
    print(f"\nWROTE repaired file: {SRC} ({len(out_text)} bytes)")
else:
    # dry-run: write to a sidecar for inspection
    side = Path("artifacts/pearl_prime/fix_wave_rebuild_20260614/book3/spiral_STORY_CANONICAL.REPAIRED_preview.txt")
    side.write_text(out_text)
    print(f"\nDRY-RUN preview -> {side} ({len(out_text)} bytes)")
