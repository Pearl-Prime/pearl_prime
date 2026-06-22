# Archive Manifest — 2026-06-22

**Quarantine Reason:** Misleading artifacts ground on May 2026 planning baselines (259-cell model) instead of June 2026 execution reality.

| Path | Why Superseded | SSOT Pointer | Verified 0 Refs ✓ |
|------|---------------|--------------|-------------------|
| `worldwide_catalog_plan_en_US_2026-05-10.tsv` | Stale May baseline; predates June en_US 1,519-book listings. | `docs/PROGRAM_STATE.md` | ✓ |
| `worldwide_catalog_plan_ja_JP_2026-05-10.tsv` | Stale May baseline; predates current manga status. | `docs/PROGRAM_STATE.md` | ✓ |
| `worldwide_catalog_plan_zh_2026-05-10.tsv` | Stale May baseline; predates localization status. | `docs/PROGRAM_STATE.md` | ✓ |

## SAFE-TO-ACTUALLY-DELETE (Proposed)
The following clusters are confirmed stale and unreferenced. Ready for `rm` on operator approval:
- `./archive/superseded_2026-06-22/*.tsv` (The 3 archived plans above)
- `./old_chat_specs/*.txt` (Stale chat exports — 32 files)
- `./old_chat_specs/*.rtfd` (Stale Rich Text bundles)
