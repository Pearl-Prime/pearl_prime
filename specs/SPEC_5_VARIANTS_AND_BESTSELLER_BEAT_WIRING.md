# Spec — 5-Variants-Per-Section + Bestseller Beat Injection Wiring

**Version:** 1.0.0
**Date:** 2026-04-27
**Authority:** Pearl_Architect (this spec) → Pearl_Dev (implementation) → Pearl_PM (acceptance)
**Status:** Operator-approved 2026-04-27 ("i need this wired")
**Implements:** Operator directive — "each chapter has 10 sections and 5 variations per section. Use 1 of them always. The inserted stories and exercises and PIVOT/PERMISSION/TAKEAWAY/THREAD/COMPRESSION beats and bestseller injections are added to it."

---

## §1 — Why this spec exists

Today's pipeline (verified 2026-04-27):

| Rule | State | Where |
|---|---|---|
| 10 sections per chapter | ✅ HARD | `phoenix_v4/planning/beatmap_compile.py:42` `SOMATIC_10_SLOT_GRID` |
| STORY at sections 2/5/9 | ✅ HARD | `phoenix_v4/planning/story_planner.py:68` `SCENE_SECTION_INDICES = (2, 5, 9)` |
| EXERCISE at sections 4 + 8 | ✅ HARD | grid positions 3 + 7 (0-indexed) |
| 12 chapters | ⚠️ SOFT default | `phoenix_v4/planning/chapter_planner.py` — configurable |
| Bestseller structure assignment | ✅ HARD | `chapter_planner.py:196` `assign_bestseller_structures` (SHA256-seeded, 12 structures) |
| Bestseller beat slot injection | ⚠️ PARTIAL | `chapter_planner.py:316` `_augment_slots_for_bestseller_structure` adds beat slots; no atom routing |
| **5 variants per section** | ❌ **NOT enforced** | Registry CAN have multiple variants; selector picks 1 via `_deterministic_index`; 5 is a CAP for `extended_book_2h` extra chunks, not a structural rule |
| **Bestseller beat → atom routing** | ❌ **NOT wired** | `BookSlotTracker` is no-op placeholder per [docs/BESTSELLER_ATOM_ROUTING.md](../docs/BESTSELLER_ATOM_ROUTING.md):98–99 |

This spec defines the wiring to make the last two rules HARD.

---

## §2 — Operator's intent (canonical statement)

> "Each chapter has **10 sections** and **5 variations per section**. Use **1 of them always**. The inserted **stories** and **exercises** and **PIVOT/PERMISSION/TAKEAWAY/THREAD/COMPRESSION beats** and **bestseller injections** are added to it."

Decomposed into rules:

**R-1.** Every section type (HOOK / STORY / REFLECTION / EXERCISE / TEACHER_DOCTRINE / INTEGRATION) in every (persona × topic) registry MUST have **≥5 atom variants** authored.

**R-2.** Per book seed, the selector picks **exactly 1** variant per slot deterministically. (Same seed → same variant; predictable, reproducible.)

**R-3.** On top of the chosen base variant, the assembler **OVERLAYS**:
- Named-character STORY content at sections 2, 5, 9 (already wired)
- EXERCISE content at sections 4, 8 (already wired via grid)
- Bestseller-structure beat steps (PIVOT / PERMISSION / TAKEAWAY / THREAD / COMPRESSION) per chapter's assigned bestseller_structure
- Any other beat-specific atom routing per `BESTSELLER_BEAT_STEPS`

**R-4.** Every chapter's emission contains exactly: `10 base-variant section bodies + 0..N beat-step overlays + 3 named-character STORY overlays at sec 2/5/9 + 2 EXERCISE overlays at sec 4/8`.

---

## §3 — Affected code paths

### §3.1 — Registry layer (data)

**Authoring requirement (R-1):** Every `registry/{topic}.yaml` must declare ≥5 variants per section type per persona.

**Validation:** new validator script `scripts/registry/validate_variant_coverage.py`:
- Walks `registry/*.yaml` + `atoms/{persona}/{topic}/{section_type}/*.txt`
- For each (persona × topic × section_type) combination required by `SOMATIC_10_SLOT_GRID`, asserts variant count ≥ 5
- Exits non-zero with a coverage report listing every gap
- Wired into CI as a new gate: `Variant coverage gate (≥5 per section)`

### §3.2 — Selector (R-2)

**Current:** `phoenix_v4/planning/enrichment_select.py:671` `_try_registry_variant` already picks deterministically via `_deterministic_index(seed_key, len(variants))`.

**Change:** add an upfront precondition check — if `len(variants) < 5` for any required slot, the assembler raises `InsufficientVariantsError` rather than degrading silently. This is the runtime mirror of the §3.1 CI gate.

### §3.3 — Beat overlay (R-3)

This is the substantive new code.

**File to modify:** `phoenix_v4/planning/enrichment_select.py` + a new `phoenix_v4/planning/beat_overlay.py`.

**Algorithm:**

```
for each chapter:
  bs_key = chapter.bestseller_structure  # already assigned (chapter_planner.py:196)
  beat_steps = BESTSELLER_BEAT_STEPS[bs_key]  # ordered list of BeatStep
  base_slots = chapter.slots  # 10 slots from SOMATIC_10_SLOT_GRID, already populated by selector
  
  # Apply beat overlays
  for beat_step in beat_steps:
    slot_idx = beat_step.target_slot_index  # 1..10 (1-indexed)
    overlay = pick_beat_atom(beat_step.beat_type, persona, topic, seed)
    base_slots[slot_idx-1].overlay_blocks.append(overlay)
  
  # Apply named-character STORY overlays (already wired via SCENE_SECTION_INDICES)
  for sec_idx in SCENE_SECTION_INDICES:  # (2, 5, 9)
    if base_slots[sec_idx-1].section_type in ("STORY", "SCENE"):
      story_overlay = build_story_overlay(chapter.story_schedule[sec_idx])
      base_slots[sec_idx-1].overlay_blocks.append(story_overlay)
  
  # EXERCISE overlays already enforced via grid; no new code
  
  yield chapter_with_overlays(base_slots)
```

**Beat atom routing:**
- `PIVOT` → atoms/{persona}/{topic}/pivot_beat/*.txt
- `PERMISSION` → atoms/{persona}/{topic}/permission_beat/*.txt
- `TAKEAWAY` → atoms/{persona}/{topic}/takeaway_beat/*.txt
- `THREAD` → atoms/{persona}/{topic}/thread_beat/*.txt
- `COMPRESSION` → atoms/{persona}/{topic}/compression_beat/*.txt

Each beat type also requires ≥5 variants per (persona × topic) for parity with R-1.

### §3.4 — BookSlotTracker

`docs/BESTSELLER_ATOM_ROUTING.md:98-99` notes BookSlotTracker is currently a "no-op placeholder." This spec **deletes the placeholder** and replaces with real implementation in `phoenix_v4/planning/beat_overlay.py`:

```python
class BookSlotTracker:
    """Tracks which beat steps have been applied to which (chapter, slot)
    so that across-chapter beat distribution stays balanced and no slot
    accumulates >2 overlays."""
    def __init__(self): ...
    def can_apply(self, chapter_idx, slot_idx, beat_type) -> bool: ...
    def apply(self, chapter_idx, slot_idx, beat_type, atom_id) -> None: ...
    def report(self) -> dict: ...  # for budget.json telemetry
```

### §3.5 — Quality gates

New gates to add to `scripts/canary/run_bestseller_canary.py`:

| Gate | What it checks | Pass criterion |
|---|---|---|
| **Variant coverage** | `validate_variant_coverage.py` exit code | == 0 |
| **Beat overlay applied** | budget.json `chapter_*.beat_overlays_applied` count | matches `len(BESTSELLER_BEAT_STEPS[bs_key])` per chapter |
| **STORY overlay applied** | budget.json `chapter_*.story_overlays_applied` | == 3 (one per SCENE_SECTION_INDICES) |
| **No silent fallback** | budget.json `chapter_*.fallback_count` | == 0 (degraded selection now raises, never silently substitutes) |

---

## §4 — Implementation plan (Pearl_Dev)

### Phase 1 — Authoring + validation gate (small)

1. Write `scripts/registry/validate_variant_coverage.py`
2. Wire it into `.github/workflows/` as a new CI gate
3. Run it against current registries → produce coverage gap report at `artifacts/qa/variant_coverage_gap_2026-04-27.md`
4. Merge as PR-D1

### Phase 2 — Authoring (large, multi-PR)

For each (persona × topic × section_type) gap:
- Author the missing variants (≥5 per family)
- One PR per persona to keep scope reviewable
- Tier-2 (Pearl Star Qwen for CJK6) acceptable for non-hero text per CLAUDE.md tier policy
- Tier-1 (Claude Code) for hero personas (gen_z_professionals, midlife_women)
- Estimated count: ~14 personas × 12 topics × 5 section types × 5 variants = ~4,200 atoms (some already exist; coverage report will quantify)

### Phase 3 — Beat overlay implementation (medium)

1. Write `phoenix_v4/planning/beat_overlay.py` with `BookSlotTracker` + overlay algorithm per §3.3
2. Replace no-op placeholder per `docs/BESTSELLER_ATOM_ROUTING.md`
3. Update `enrichment_select.py` to call overlay after base variant pick
4. Add `chapter_*.beat_overlays_applied` + `chapter_*.story_overlays_applied` to `budget.json`
5. Tests: end-to-end book run → assert structure compliance
6. Merge as PR-D2

### Phase 4 — Beat-atom authoring (large, multi-PR)

For each beat type × persona × topic:
- Author ≥5 atoms (PIVOT/PERMISSION/TAKEAWAY/THREAD/COMPRESSION)
- Estimated count: 5 beat types × ~14 personas × 12 topics × 5 atoms = ~4,200 beat atoms
- Same tier policy as Phase 2
- One PR per beat type to keep scope reviewable

### Phase 5 — Canary gate update (small)

1. Add the 4 gates from §3.5 to `scripts/canary/run_bestseller_canary.py`
2. Run against `gen_z_professionals/overthinking/comparison/standard_20ch` sentinel
3. PASS → spec ratified; FAIL → fix Phase 1-4 before merging

### Phase 6 — Roll out (large)

After Phases 1–5 ship, regenerate:
- All atoms-bearing artifacts under `artifacts/qa/`
- Re-run the canonical Move 4 30-book representative sweep
- Confirm 90%+ pass with the new gates active

---

## §5 — Success criteria (acceptance)

PR-set is accepted when:

1. ✅ `validate_variant_coverage.py` exits 0 against current registries
2. ✅ `BookSlotTracker` no-op placeholder removed; real implementation passes tests
3. ✅ End-to-end book run: every chapter's `budget.json` has `beat_overlays_applied >= 1` and `story_overlays_applied == 3`
4. ✅ Bestseller canary passes all 4 new gates (§3.5)
5. ✅ Move 4 30-book sweep maintains ≥90% pass rate

---

## §6 — Risks + mitigations

| Risk | Mitigation |
|---|---|
| Authoring 4,200 atoms is months of work | Parallelize per-persona PRs; use Tier-2 Qwen for CJK6 non-hero text |
| InsufficientVariantsError breaks current pipeline runs | Phase 1 (gate) ships first as warn-only; flips to fail after coverage authored |
| Beat overlay changes book length significantly | Budget telemetry tracks word-count delta; canary asserts within ±20% of pre-overlay baseline |
| BookSlotTracker conflicts with existing beat-step logic | Real impl shadow-runs against placeholder for 1 week before cutover |

---

## §7 — Out of scope (explicitly)

- Title / cover authoring (separate spec)
- Translation provider routing (separate spec)
- Per-locale beat customization (US PIVOT vs JP PIVOT register differences) — future
- Per-genre beat customization (mecha PIVOT vs iyashikei PIVOT) — future

---

## §8 — Companion docs

- [docs/PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md](../docs/PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md) — single source of truth for book generation
- [docs/BOOK_PLANNING_SYSTEM_SPEC.md](../docs/BOOK_PLANNING_SYSTEM_SPEC.md) — ChapterPlan schema
- [docs/BESTSELLER_ATOM_ROUTING.md](../docs/BESTSELLER_ATOM_ROUTING.md) — 12 structures + beat steps (this spec implements its routing)
- [docs/CONTENT_FRAGMENT_VARIATION_WRITER_SPEC.md](../docs/CONTENT_FRAGMENT_VARIATION_WRITER_SPEC.md) — atom variation authoring
- [docs/SESSION_HANDOFF_2026_04_27.md](../docs/SESSION_HANDOFF_2026_04_27.md) — operator session that surfaced this gap
