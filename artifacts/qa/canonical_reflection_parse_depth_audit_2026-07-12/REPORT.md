# CANONICAL parse-depth audit

Generated: `2026-07-12T14:06:25.890001+00:00`
Parser: `phoenix_v4.planning.registry_resolver._parse_canonical_txt`

## Totals

- files: **8664**
- headers: **126487**
- usable atoms: **123632**
- parse errors (loud): **25**
- silent zero-atom risk: **0**

## Delimiter shapes

- `pre-delimiter-legacy`: 280
- `single-delimiter`: 197
- `single-section-legacy`: 624
- `two-delimiter`: 6934

## Consumers audited

- `phoenix_v4/planning/registry_resolver.py::_parse_canonical_txt` — persona + composite doctrine/reflection loader (bug surface)
- `phoenix_v4/planning/registry_resolver.py::_load_persona_atoms` — walks atoms/{persona}/{topic}/{slot|engine}/CANONICAL.txt
- `phoenix_v4/planning/registry_resolver.py::_load_composite_doctrine_atoms` — composite_doctrine CANONICAL.txt + REFLECTION/CANONICAL.txt
- `phoenix_v4/quality/composite_doctrine_secular_lint.py` — imports registry_resolver._parse_canonical_txt
- `scripts/qa/assemble_ch1_12shape_preview_v4.py` — imports registry_resolver._parse_canonical_txt
- `phoenix_v4/planning/assembly_compiler.py::_parse_canonical_txt` — strict STORY metadata parser (separate contract; path/band)
- `phoenix_v4/quality/base.py::parse_canonical_blocks` — quality lint two-delimiter block parser
- `phoenix_v4/rendering/prose_resolver.py::_parse_canonical_with_prose` — render-time STORY prose map
- `scripts/localization/run_translation_loop.py::parse_canonical` — translation loop variant splitter
- `scripts/ci/check_canonical_atom_parse_sweep.py` — CI sweep via assembly_compiler strict parser (STORY over-match)

## By slot

- **ANGLE_DEFINITION**: files=2 headers=0 usable=0 errors=0 silent_zero=0
- **COMPRESSION**: files=649 headers=9487 usable=9484 errors=1 silent_zero=0
- **EXERCISE**: files=653 headers=6998 usable=6967 errors=2 silent_zero=0
- **HOOK**: files=733 headers=15579 usable=15579 errors=0 silent_zero=0
- **INTEGRATION**: files=709 headers=13835 usable=12908 errors=7 silent_zero=0
- **PERMISSION**: files=873 headers=8573 usable=8553 errors=1 silent_zero=0
- **PIVOT**: files=896 headers=8819 usable=8799 errors=1 silent_zero=0
- **REFLECTION**: files=723 headers=16472 usable=14727 errors=9 silent_zero=0
- **SCENE**: files=624 headers=11632 usable=11523 errors=4 silent_zero=0
- **STORY**: files=1001 headers=17765 usable=17765 errors=0 silent_zero=0
- **TAKEAWAY**: files=881 headers=8673 usable=8673 errors=0 silent_zero=0
- **TEACHER_DOCTRINE**: files=45 headers=235 usable=235 errors=0 silent_zero=0
- **THREAD**: files=874 headers=8413 usable=8413 errors=0 silent_zero=0
- **TRANSITION**: files=1 headers=6 usable=6 errors=0 silent_zero=0

## Acceptance

Post-fix parser raises CanonicalParseError on header-present empty-prose blocks; silent_zero_risk must be 0 for scanned files.

silent_zero_files: []

## Artifacts

- `SUMMARY.json` — totals / by_slot / acceptance (repo-compliant)
- `PARSE_ERRORS.jsonl` — one JSON object per failing file
- Full per-file rows regenerable locally; not committed (blob policy).

