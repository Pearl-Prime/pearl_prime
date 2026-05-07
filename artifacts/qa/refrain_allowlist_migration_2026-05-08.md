# Refrain Allowlist Migration Log — 2026-05-08

Sprint 1 YELLOW ITEM-1 follow-up.  
Replaces raw `ignored_prefixes` tuple in `_repeated_phrase_violations`
(`phoenix_v4/quality/book_quality_gate.py`) with a YAML-backed
`config/quality/refrain_allowlist.yaml` where each entry has an explicit
`cap_book_wide` and `cap_per_chapter`.

Sprint 1 merge SHA: `635e1a96bf`  
Session A audit artifact: `artifacts/qa/sprint1_ignored_prefixes_conformance_2026-05-08.md`
— **absent at migration time**. All entries classified via inline source comments
and the fallback rule (unclassified → `legitimate_motif`, cap=18).

---

## Entry Migration Table

| Old `ignored_prefixes` entry | Source comment / context | Session A classification | New `classification` | `cap_book_wide` | `cap_per_chapter` | Dropped? |
|---|---|---|---|---|---|---|
| `the point is that` | Original somatic motif | absent → defaulted | `legitimate_motif` | 18 | 2 | No |
| `i want you to` | Original somatic motif | absent → defaulted | `legitimate_motif` | 18 | 2 | No |
| `now i want you` | Original somatic motif | absent → defaulted | `legitimate_motif` | 18 | 2 | No |
| `not to fix anything` | Original somatic exercise phrase | absent → defaulted | `legitimate_motif` | 18 | 2 | No |
| `anything just to` | Fragment of somatic exercise | absent → defaulted | `legitimate_motif` | 18 | 2 | No |
| `fix anything` | Fragment: "not to fix anything" | absent → defaulted | `legitimate_motif` | 18 | 2 | No |
| `to fix anything` | Fragment of somatic exercise | absent → defaulted | `legitimate_motif` | 18 | 2 | No |
| `just to give yourself` | Somatic self-permission phrase | absent → defaulted | `legitimate_motif` | 18 | 2 | No |
| `to give yourself` | Fragment of self-permission phrase | absent → defaulted | `legitimate_motif` | 18 | 2 | No |
| `give yourself a` | Fragment of self-permission phrase | absent → defaulted | `legitimate_motif` | 18 | 2 | No |
| `before you move on` | Chapter transition anchor | absent → defaulted | `legitimate_motif` | 18 | 2 | No |
| `a different input` | Somatic reframe exercise | absent → defaulted | `legitimate_motif` | 18 | 2 | No |
| `different input for` | Fragment of reframe phrase | absent → defaulted | `legitimate_motif` | 18 | 2 | No |
| `input for a` | Fragment of reframe phrase | absent → defaulted | `legitimate_motif` | 18 | 2 | No |
| `one breath at a time` | Scene-anchor grounding phrase | absent → defaulted | `legitimate_motif` | 18 | 2 | No |
| `you have been looking` | Sprint-1 scene-anchor (inline comment: "intentional recurring hook") | absent → source comment | `legitimate_motif` | 18 | 2 | No |
| `have been looking` | Sprint-1 scene-anchor fragment | absent → source comment | `legitimate_motif` | 18 | 2 | No |
| `been looking at` | Sprint-1 scene-anchor fragment | absent → source comment | `legitimate_motif` | 18 | 2 | No |
| `looking at it for` | Sprint-1 scene-anchor fragment | absent → source comment | `legitimate_motif` | 18 | 2 | No |
| `at it for forty` | Sprint-1 scene-anchor fragment | absent → source comment | `legitimate_motif` | 18 | 2 | No |
| `it for forty minutes` | Sprint-1 scene-anchor fragment | absent → source comment | `legitimate_motif` | 18 | 2 | No |
| `the task is open` | Sprint-1 scene-anchor motif sentence | absent → source comment | `legitimate_motif` | 18 | 2 | No |
| `task is open you` | Sprint-1 scene-anchor fragment | absent → source comment | `legitimate_motif` | 18 | 2 | No |
| `is open you have` | Sprint-1 scene-anchor fragment | absent → source comment | `legitimate_motif` | 18 | 2 | No |
| `open you have been` | Sprint-1 scene-anchor fragment | absent → source comment | `legitimate_motif` | 18 | 2 | No |
| `your body knows` | Sprint-1 scene-anchor motif | absent → source comment | `legitimate_motif` | 18 | 2 | No |
| `your nervous system` | Sprint-1 scene-anchor; high-density genre vocab | absent → source comment | `legitimate_motif` | 18 | 2 | No — ITEM-2 deferred |
| `body knows something` | Sprint-1 scene-anchor fragment | absent → source comment | `legitimate_motif` | 18 | 2 | No |
| `knows something your` | Sprint-1 scene-anchor fragment | absent → source comment | `legitimate_motif` | 18 | 2 | No |
| `something your calendar` | Sprint-1 scene-anchor fragment | absent → source comment | `legitimate_motif` | 18 | 2 | No |
| `not forever just` | Sprint-1 scene-anchor phrase | absent → source comment | `legitimate_motif` | 18 | 2 | No |
| `it was the cost` | Sprint-1 scene-anchor phrase | absent → source comment | `legitimate_motif` | 18 | 2 | No |
| `was the cost of` | Sprint-1 scene-anchor fragment | absent → source comment | `legitimate_motif` | 18 | 2 | No |
| `the alarm does not` | Sprint-1 scene-anchor phrase | absent → source comment | `legitimate_motif` | 18 | 2 | No |
| `the alarm dressed` | Sprint-1 scene-anchor phrase | absent → source comment | `legitimate_motif` | 18 | 2 | No |
| `the foundation of contemplative` | Sprint-1 scene-anchor phrase | absent → source comment | `legitimate_motif` | 18 | 2 | No |
| `drawing on ahjan` | TEACHER_DOCTRINE attribution (inline comment) | absent → source comment | `doctrinal_attribution` | 14 | 2 | No |
| `ahjan's mindfulness` | TEACHER_DOCTRINE attribution | absent → source comment | `doctrinal_attribution` | 14 | 2 | No |
| `mindfulness and somatic` | TEACHER_DOCTRINE attribution | absent → source comment | `doctrinal_attribution` | 14 | 2 | No |
| `somatic teaches us` | TEACHER_DOCTRINE attribution | absent → source comment | `doctrinal_attribution` | 14 | 2 | No |
| `according to ahjan` | TEACHER_DOCTRINE attribution | absent → source comment | `doctrinal_attribution` | 14 | 2 | No |
| `that is the part` | TEACHER_DOCTRINE attribution | absent → source comment | `doctrinal_attribution` | 14 | 2 | No |
| `the remote work improved` | TEACHER_DOCTRINE attribution | absent → source comment | `doctrinal_attribution` | 14 | 2 | No |

**Summary:**
- Entries migrated: 43
- Entries dropped (MASKED_DEFECT): 0  
  — Session A audit was absent; no MASKED_DEFECT classification could be made.
  — If Session A audit is subsequently produced and reclassifies entries as MASKED_DEFECT,
    those entries must be removed from the YAML in a follow-up PR.
- `your nervous system` retained with `todo: "ITEM-2:remove-when-per-chapter-overlay-active"`

---

## Revalidation Output (Step 8)

No 50,000-word Sprint 1 reference artifact (`artifacts/rendered/spine-anxiety/book.txt` or
equivalent) was present in the worktree at migration time. The largest available `book.txt`
was ~12,274 words — far below the `deep_book_6h` minimum (50,000), so full revalidation
against the Sprint 1 reference book was **skipped**.

**Gate logic was verified via unit tests only (20/20 passed).**

Available book.txt files checked:
- `artifacts/rendered/9417605375c03fa81108009fdb66ccb7/book.txt` — 12,274 words → FAIL (word count + chapter flow)
  - Repeated phrase HOLD was present (`i have come to` ×30, `what i have come` ×30, etc.)
  - These are non-allowlisted phrases correctly flagged by the new gate — behavior is correct.

---

## ITEM-2 Deferral

`your nervous system` is deliberately retained in `refrain_allowlist.yaml` with:

```yaml
todo: "ITEM-2:remove-when-per-chapter-overlay-active"
```

Removal of this entry is gated on the per-chapter overlay enforcement workstream.
Until that workstream ships, the entry stays in the allowlist at cap_book_wide=18.

---

## Cap Formulas (per §phrase-density)

| Classification | Formula | Cap (12-ch book) |
|---|---|---|
| `legitimate_motif` | `ceil(1.5 × chapter_count)` | 18 |
| `doctrinal_attribution` | `chapter_count + 2` | 14 |

---

## Files Changed

- `phoenix_v4/quality/book_quality_gate.py` — removed `ignored_prefixes` tuple; added `_load_refrain_allowlist()`, `_REFRAIN_ALLOWLIST`, `_match_allowlist_entry()`; refactored `_repeated_phrase_violations()` to use per-entry caps with `matched_allowlist_entry` / `cap_applied` fields in violation dicts.
- `config/quality/refrain_allowlist.yaml` — new YAML allowlist (version 1, 43 entries).
- `tests/quality/test_refrain_allowlist.py` — 20 new pytest tests (all pass).
- `artifacts/qa/refrain_allowlist_migration_2026-05-08.md` — this file.
