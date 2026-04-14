# Frame enforcement v2 — pilot checklist

**Purpose:** Prove policy-driven frame actions (warn / soften / strip / hard_fail) and telemetry in `quality_summary.json`.

## Regenerate

```bash
PYTHONPATH=. python3 -c "
from pathlib import Path
import json
from phoenix_v4.planning.enrichment_select import EnrichedBook, EnrichedChapter, EnrichedSlot
from phoenix_v4.rendering.chapter_composer import compose_from_enriched_book

out_dir = Path('artifacts/pilots/frame_enforcement_v2_verify')
# … same fixture as scripts note in repo history / test expectations …
"
```

Or run the generator block from the Frame Enforcement v2 PR description (mirrors CI fixture).

## Acceptance criteria

- [ ] **Somatic body (ch1):** disallowed absolute phrasing (`love melts all` in non-doctrine slot) is **removed** (strip_sentence), not only logged.
- [ ] **Doctrine chapter (ch2):** same phrase in `TEACHER_DOCTRINE` slot is **preserved**; telemetry shows **warn_only** style violation entry without strip.
- [ ] **Early spiritual (ch3, before configured spiritual entry chapter):** `chakra` is **softened** via `lexicon_softeners`, not bluntly deleted unless policy says strip.
- [ ] **`quality_summary.json` / governance report** lists `frame_softened_sentences`, `frame_stripped_sentences`, `frame_hard_fail_reasons`, and per-chapter `frame_governance_chapters` with `softened` / `stripped` arrays.
- [ ] **No LLM:** all decisions are config + phrase lists (`frame_registry.yaml`).
- [ ] **Tests:** `pytest tests/test_frame_governance.py tests/test_book_renderer.py` pass.

## Authority

- `config/source_of_truth/frame_registry.yaml` — policies + softeners
- `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` — craft alignment
- `docs/SESSION_UNITY_PROTOCOL.md` — workstream receipts
