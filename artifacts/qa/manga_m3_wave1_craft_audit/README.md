# M3 Wave 1 craft audit pack

| File | Role |
|---|---|
| `WAVE1_MANIFEST.tsv` | brand → genre → topic → series_id |
| `GATE_RESULTS.tsv` | byte-verified gate lines |
| `COVERAGE_TABLE.md` | operator-facing coverage |
| `REFUTER_SPOT_AUDIT_OF_5.md` | honest adversarial audit |

Reproduce gate:

```bash
PYTHONPATH=scripts/ci:. python3 -c "
from pathlib import Path
from check_manga_story_authored import assert_story_authored
for row in Path('artifacts/qa/manga_m3_wave1_craft_audit/WAVE1_MANIFEST.tsv').read_text().splitlines()[1:]:
    sid = row.split('\t')[3]
    assert_story_authored(Path('artifacts/manga/chapter_scripts')/sid/'ep_001.yaml')
    print('PASS', sid)
"
```
