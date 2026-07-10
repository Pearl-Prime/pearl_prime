# Overthinking false_alarm/watcher Stub Content Fix + Repo-Wide Scope Audit (2026-07-10)

## What was reported

`atoms/gen_z_professionals/overthinking/{false_alarm,watcher}/CANONICAL.txt` each had 10 of 18
variants (`RECOGNITION v01/v03/v05`, `MECHANISM_PROOF v02/v04`, `TURNING_POINT v01/v03/v05`,
`EMBODIMENT v02/v04`) with a prose body that was literally the bare text of the *next* variant's
header (e.g. the body under `## RECOGNITION v01` was just the string `RECOGNITION v02`, no `##`
prefix). This blocked CJK translation for these two files (found during zh-CN Stage-1 work) and,
more importantly, meant the render-path parser (`prose_resolver._parse_canonical_with_prose`,
which is *not* the same lighter parser `check_tuple_viability` uses) was treating these bare
header-fragments as valid, selectable prose — they are short enough and contain no bracket/stub
markers, so `_is_stub_body()` never flags them. These variants were live in the selectable pool.

## Root cause (confirmed against existing CI history)

This is the **same defect family** `scripts/ci/check_canonical_atom_parse_sweep.py` already
documents in its own docstring (DEFECT-7 / the PR #1590 "over-match" incident): atom variants
whose real prose was never authored, left as a bare `ROLE vNN` label between two `---` fences.
That gate's baseline (`check_canonical_atom_parse_sweep_baseline.txt`, 8,343 lines) already tracks
files exhibiting the *over-matched* symptom (a body line wrongly promoted to a phantom `##` header
by a prior automated repair). **This report is the complementary, un-repaired symptom**: files
where that promotion never happened, so the bare label silently sat as prose instead of raising a
parse error — invisible to both the strict parser (which never fails, so it never trips the sweep
gate) and to `_is_stub_body()` (which only recognizes bracket/pipeline stubs, not bare-header-text
stubs).

## Repo-wide scope (verified, not the 2 originally reported)

Grepped every `atoms/**/CANONICAL.txt` for blocks whose prose body matches `^[A-Z_]+\s+v\d+$`
exactly (script + methodology in this PR):

- **17,195** `CANONICAL.txt` files scanned
- **883** files carry at least one stub variant of this exact shape
- **7,769** total stub variants across those files
- Confirmed present in both English source files and their CJK locale mirrors (translations
  faithfully "translated" the untranslated stub marker, i.e. copied it verbatim)

This is **far larger than the 2 files originally reported** and is a genuine, previously
unquantified-at-this-precision program-level gap — not something this fix attempts to resolve.
**Not fixed here.** Full file list is reproducible via the grep in this PR; not attached inline
(883 entries) to keep this artifact readable — regenerate with the script below.

```python
import re
from pathlib import Path
block = re.compile(r"^##\s+([A-Z_]+)\s+v(\d+)\s*\n---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*?)(?=\n---|\Z)", re.MULTILINE)
stub_re = re.compile(r"^[A-Z_]+\s+v\d+$")
for path in Path("atoms").rglob("CANONICAL.txt"):
    text = path.read_text(encoding="utf-8", errors="replace")
    stubs = sum(1 for m in block.finditer(text) if stub_re.match(m.group(4).strip()))
    if stubs:
        print(stubs, path)
```

## What was fixed here (exactly the 2 files reported, 20 variants)

- `atoms/gen_z_professionals/overthinking/false_alarm/CANONICAL.txt` — 10 stub variants replaced
  with real authored prose, in place (same headers, same metadata, same band/version numbers —
  file still has exactly 18 blocks, no new atoms invented).
- `atoms/gen_z_professionals/overthinking/watcher/CANONICAL.txt` — same, 10 variants.
- Used the block's own `path:` metadata field as the thematic prompt for each stub (e.g. `path:
  the read receipt that means everything` for `RECOGNITION v01`), matched the established
  false_alarm mechanism language ("The alarm system fires danger signals when no real threat
  exists") and watcher mechanism language ("The watcher monitors from a distance, recording
  failures but never engaging") already present in this exact file's real variants, and reused the
  file's own established character cast (Alex, Sam, Zara, Leo, Marco, Jordan, Nia, Suki, Priya,
  Kai) rather than inventing new characters or borrowing from another persona/topic.
- **First attempt at this fix introduced a new bug** (worth noting): an `Edit` call meant to
  replace one stub's prose accidentally manufactured a duplicate, malformed `## EMBODIMENT v05`
  header with no metadata section, which would have re-broken parsing further down the file.
  Caught by the same verification script before landing; the file was rewritten cleanly from
  scratch instead of patched incrementally.
- `atoms/gen_z_professionals/overthinking/{false_alarm,watcher}/locales/zh-CN/CANONICAL.txt` — the
  same 10 stub variants per file, confirmed to mirror the identical defect (English stub markers
  copied verbatim, untranslated), translated via Qwen (`qwen2.5:14b`) on Pearl Star/Ollama —
  CLAUDE.md Tier-2, no paid key used. The other 8 already-correctly-translated variants per file
  were left untouched (only the 10 stub prose bodies were replaced, verified via diff: exactly 20
  changed lines per file, matching 10 replacements).
- `ja-JP` and `zh-TW` locale mirrors for these same 2 files carry the identical 10-stub defect and
  were **not** translated here (out of the scope the user asked for — zh-CN only). Flagged below.

## Verification

- Both English files: 18 blocks (unchanged count), 0 stub variants, 0 duplicate role/version
  pairs, confirmed via the render-path parser (`_parse_canonical_with_prose`): 18/18 real
  (non-stub) prose variants each (up from 8/18).
- `check_tuple_viability` re-run for `gen_z_professionals × overthinking × {false_alarm,watcher} ×
  F006`: both `PASS` (were already `PASS` before, since that lighter gate never caught this defect
  — confirms the gap this fix closes wasn't visible to the existing preflight gate at all).
- Both zh-CN locale files: 18 blocks, 0 stubs, 18/18 real prose variants via the same parser.
- `scripts/check_golden_translation.py --locales zh-CN`: OK (8/8 segments).

## Not fixed here — follow-ups

1. **The other 881 files / 7,749 remaining stub variants repo-wide.** This is a multi-week
   authoring program, not a single-session fix — flagged for the operator to decide how to
   resource (systematic regeneration, priority triage by catalog traffic, etc.), not attempted
   unilaterally here.
2. **`check_canonical_atom_parse_sweep.py` gate extension.** The natural enforcement home for this
   defect class is this existing gate (it already tracks the sibling over-match symptom with a
   baseline-allowlist mechanism). Deliberately not touched in this fix: its own docstring documents
   a prior 1,215-file regression from a similarly well-intentioned automated repair (PR #1590), so
   extending it needs focused, careful attention as its own task, not a rushed addition alongside a
   content fix.
3. **`ja-JP`/`zh-TW` locale mirrors** for these same 2 files need the identical 10-variant
   retranslation once picked up — same source fix, just not translated to those 2 locales in this
   PR (zh-CN only, per what was asked).

## Scope

4 files changed (2 English source + 2 zh-CN locale). No other atoms touched. No code/script/gate
changes.
