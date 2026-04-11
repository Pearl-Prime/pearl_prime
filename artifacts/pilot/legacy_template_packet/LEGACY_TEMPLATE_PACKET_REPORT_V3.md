# Legacy Template Packet V3 — Real Vendor Archives (Not Available)

**Topic:** anxiety (pilot not re-run; see below)  
**Persona:** gen_z_professionals  
**Teacher:** ahjan  
**Runtime format:** standard_book (unchanged from V1/V2)  
**Date:** 2026-04-11  
**Evidence:** PR [#385](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/385) merged to `main` as squash (`a57a3fc22ef0b8de7061f3f61c0e5be1c54c4192`).

---

## V3 scope

This report records the **attempted** swap from bootstrap/test-fixture zips to **full vendor** `audiobook_template_v4*.zip` and `audiobook_template_v2*.zip` / `audiobook_templates_v2_BOTH.zip` archives. Per session protocol, **no extraction or pilot re-run** was performed because the **canonical vendor archives were not located** on disk. **V3 does not claim new word-count or legacy-hit metrics** beyond what V2 already established with the bootstrap tree.

---

## Archive status

| Archive (expected name) | Found | Notes |
|-------------------------|-------|--------|
| `audiobook_template_v4.zip` (full vendor) | **No** | Repo `template_expand/audiobook_template_v4.zip` after PR #385 is the **bootstrap** zip from fixtures (~1.7 KB), not a commercial 12×10 library. |
| `audiobook_template_v2_full.zip` | **No** | `find` under `/Users/ahjan/` for `audiobook_template_v2*.zip` returned **no** matches. |
| `audiobook_template_v2_bestseller.zip` | **No** | Same. |
| `audiobook_template_v2_somatic.zip` | **No** (exact name) | **Alternate:** `/Users/ahjan/Downloads/qaudiobook_template_v2_somatic.zip` (~576 KB) exists with prefix `q` and internal layout `sections_somatic_v2/chapter_*/section_*_role/f*.yaml` — **not** the indexed path `chapter_NN/section_NN/variant_F*.yaml`. Treated as **non-canonical**; not copied into `template_expand/` for this workstream. |
| `audiobook_templates_v2_BOTH.zip` | **No** | Not found. |

**Downloads scan:** `ls ~/Downloads/*.zip` shows `files.zip` … `files (4).zip` and related bundles; `files (3).zip` contains `audiobook_template_contrarian*.zip` (different product line), not the V4/V2 vendor set.

**Conclusion:** Real **named** V4/V2/BOTH vendor archives are **not on this machine** in a form we can honestly label “real template bridge validation.” Owner must place the expected zips under `template_expand/` (or supply paths) before re-extract, index update, and pilot.

---

## V1 → V2 → V3 progression

| Metric | V1 (none) | V2 (bootstrap) | V3 (real) | Target |
|--------|-----------|------------------|-----------|--------|
| Total words | 9,170 | 8,566 | **N/A — not run** (archives missing) | 54,000 |
| Legacy sections | 0/102 | 2/102 | **N/A** | full grid |
| Bridges | 11 | 0 | **N/A** | 11 |
| Avg words/section | ~90 | ~84 | **N/A** | ~450 |

**V3 vs V1/V2:** No new measured row. **Best available data remain V1 and V2** in `LEGACY_TEMPLATE_PACKET_REPORT.md` and `LEGACY_TEMPLATE_PACKET_REPORT_V2.md`.

---

## Source breakdown (V3)

Not applicable — pilot outputs under `artifacts/pilot/legacy_template_packet_v3/` were **not** generated.

---

## Honest assessment

- **Did real templates close the gap?** **Cannot tell** — real vendor archives were **not** available; we did not fabricate a V3 run.
- **What is still missing to reach 54k?** Same as V2: **`deep_book_6h`** (or equivalent) per-slot budgets, full YAML grids, bridges on disk, and enrichment depth — not extraction alone.
- **Plumbing vs content:** PR #385 is **plumbing** (extraction mechanics, loader, pilot bootstrap). **Content-scale validation** remains blocked on **archive delivery**.
- **Next step:** Owner provides `audiobook_template_v4.zip`, V2 zips, and optionally `audiobook_templates_v2_BOTH.zip` at expected names → extract under `template_expand/_extracted/` only → re-measure index → adjust loader if layout differs → re-run anxiety pilot → fill this table with **measured** V3 numbers.

---

## IF ARCHIVES NOT FOUND (this session)

- Real vendor archives were **not** available under the expected names/paths.
- Bootstrap fixture results in PR #385 remain the **only** honest end-to-end proof in-repo.
- **No further progress** on “real template bridge vs 54k” until owner supplies archives.
- Optional follow-up: rename or symlink `qaudiobook_template_v2_somatic.zip` and extend `legacy_template_loader.py` for the `sections_somatic_v2/.../f*.yaml` layout — **separate, explicit PR**; out of scope for this STOP gate.
