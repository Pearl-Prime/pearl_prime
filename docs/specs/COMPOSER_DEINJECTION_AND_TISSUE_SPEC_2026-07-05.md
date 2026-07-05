# Composer De-Injection + Connective-Tissue Spec — 2026-07-05

**Lanes:** subtract = Cursor (`agent/composer-deinjection-complete-20260705`);
authored tissue = Pearl_Writer (`agent/connective-tissue-pilot-20260705`).
**Serialize on `phoenix_v4/rendering/chapter_composer.py`.**

**Doctrine:** SUBTRACT the render-time glue; do NOT add a new glue family; do NOT
tune F14/ONTGP/register (they *rewarded* the glue); do NOT gut authored atoms.
Target = "authored candidate" (Layer 2), claimable only on the operator's read.

All line numbers are against `origin/main` @ `d1e0844654` (composer = 3,645 lines).
Pearl_Writer independently reproduced everything in **Part A/B** and the constant/
truncation lines. Items in **Part C are as-reported, NOT independently reproduced** —
Cursor must locate and confirm before changing. Say so in the closeout.

---

## Part A — Glue family kill-list (VERIFIED on main)

Four render-time template families are loaded and injected on the compose path.
Add ONE module-level kill-switch, **default OFF on the spine/production path**:

```python
# near the config-path constants (~line 98)
_RENDER_GLUE_ENABLED = os.environ.get("PHOENIX_ENABLE_RENDER_GLUE", "0") == "1"
```

Each injection entry point early-returns the un-glued value when disabled (return
`""` for a standalone bridge sentence; return the raw atom text for wrappers).
Do not delete the loaders/selectors — gate their *call sites* so the A/B is a flip.

| Family | config | loader | inject entry points to gate |
|---|---|---|---|
| bridge_transition | `config/rendering/bridge_transition_families.yaml` | `_load_bridge_transition_families` :241 | `_bridge_after_opening` :1314, `_bridge_before_story` :1388, `_bridge_before_exercise` :1452, `_bridge_before_integration` :1510 (each calls `_select_bridge_candidate` :882) |
| mechanism_thesis | `config/rendering/mechanism_thesis_families.yaml` | `_load_mechanism_thesis_families` :211 | `_select_mechanism_thesis_candidate` :1037, call site :1294–1297 |
| exercise_wrapper | `config/rendering/exercise_wrapper_families.yaml` | `_load_exercise_wrapper_families` :226 | wrapper builder @ :1149 |
| within_slot_bridge (**the triple/quad exercise intro**) | `config/rendering/within_slot_bridge_families.yaml` | `_load_within_slot_bridge_families` :325 | `_bridge_story_introduction` :1584, `_bridge_within_slot` :1674 |

**Exercise intro (kill the triple):** an exercise must render ONLY its own
`practice_library` components (bridge/intro/description/aha/integration) — exactly
one intro, the exercise's own. Gate off `within_slot` story/exercise intro (:1584,
:1674) AND any `intro_templates` / `introduction_templates` / `bridge_templates`
stacking so the "Now we're going to do a breath practice. This is a breath-based
practice…" pile-up collapses to a single authored intro.

## Part B — Hardcoded appends/fallbacks (VERIFIED on main) — delete/disable

| What | line(s) | emits |
|---|---|---|
| `_takeaway_fallback` | :2201 | `"Remember this: {core} Keep it concrete…"` |
| constant chapter handoff | :2268–2269 | `"The next chapter begins where insight usually thins out…"` (identical every book) |
| `_append_anxiety_chapter_one_scan_practice` | def :2667, call :3154 | a Ch1 practice from NO bank |

Gate these behind `_RENDER_GLUE_ENABLED` too (default OFF). When off, TAKEAWAY
renders the selected authored TAKEAWAY atom with no fallback string; the chapter
handoff is omitted; Ch1 uses only its selected EXERCISE atom.

## Part C — Wiring bugs (AS-REPORTED — Cursor to reproduce before fixing)

Pearl_Writer could NOT independently reproduce these from `origin/main` greps
(no literal `v05`/`v30`, no obvious registry-hook stack in the composer). They
likely live at the **enrichment → compose boundary** (`book_structure_plan` /
the enrichment/selection layer), not in `chapter_composer.py` alone. Locate,
write a failing repro, then fix:

1. **Hook stacking** — registry-derived hook emitted *in addition to* the atom
   HOOK (two openers). Start at the opening assembly `:2906–2920` and trace where
   a second hook source is concatenated. Expected: one hook per slot.
2. **Reflection-on-doctrine append** — registry reflection appended onto the
   TEACHER_DOCTRINE block (two occupants in one slot). Expected: one occupant/slot.
3. **INTEGRATION wrong-atom pull** — compose renders a different INTEGRATION
   variant than enrichment SELECTED (reported v05 vs v30). Find where the selected
   atom id is resolved at compose time and make compose render the SELECTED id.
4. **Ch1 truncation** — source line `:2268` is intact ("…It is the first honest
   place this pattern asks for practice."); the clip happens at RENDER time. Find
   the length/paragraph cap that truncates the final Ch1 sentence and fix the cut.

## Part D — NEW authored-transition consumer slot (unblocks Pearl_Writer Phase 2b)

The composer knows slots HOOK/STORY/REFLECTION/EXERCISE/INTEGRATION/
TEACHER_DOCTRINE/TAKEAWAY/THREAD — **no TRANSITION slot exists**. Today's
transitions ARE the bridge glue being removed in Part A. To let authored
transitions replace them (not re-introduce glue):

- Add a `TRANSITION` (and optional `DWELL`) authored-atom slot the selector reads
  from the atom bank, keyed by `(topic, engine, boundary)` where boundary ∈
  {after_opening, before_story, before_exercise, before_integration}.
- At each former bridge site, if `_RENDER_GLUE_ENABLED` is off AND an authored
  TRANSITION atom exists for that `(topic, engine, boundary)`, emit it; else emit
  nothing (a clean cut — never fall back to a template).
- This is a **selector read of authored atoms**, not a template generator. Do not
  synthesize transition text.

Pearl_Writer authors the TRANSITION/DWELL atoms once this slot exists
(`agent/connective-tissue-pilot-20260705`, task blocked-by this spec).

## Part E — Identity-contract enforcement hook (consumes authored config)

Config authored + present, `status: unwired`:
`config/planning/book_identity_contracts/{anxiety,financial_stress}.yaml`
(schema in that dir's `README.md`). Implement at selection:

1. Soft-penalize any atom whose text contains a `banned_phrases` entry (penalty,
   not hard reject).
2. Guarantee `identity_line` is emitted in chapter 1 and the final chapter
   (`identity_line_placement: [1, last]`).
3. Prefer atoms whose imagery matches `engine_metaphors[engine]` for the chapter's
   engine (tie-breaker).

Flip each contract's `status: unwired` → `status: wired` in the same PR that lands
the consumer.

## Part F — Chapter-aware HOOK dedup

The "29 lines repeating 2–3× across 12 chapters" is pool depth + no selection
memory. Add a book-scoped `used_hooks` set so a HOOK line is never served twice in
one book (mirror the existing BridgeMemory book-distinct pattern). Pool *depth* is
Pearl_Writer's authoring (Phase 2b); the *dedup memory* is this item.

## Part G — Proof protocol (both lanes, at the end)

1. Re-render the anxiety cell (booklz's cell) + a financial_stress cell with the
   four-piece chord `--pipeline-mode spine --quality-profile production
   --exercise-journeys`, once with glue OFF (default) — and, for the A/B, once with
   `PHOENIX_ENABLE_RENDER_GLUE=1`.
2. Diff old vs new Ch1. Every quoted glue line from Parts A/B must be GONE:
   "Turn it into motion:", "Now we're going to do a … practice", "Remember this:",
   "The next chapter begins where insight usually thins out…".
3. Same-length sanity: subtraction, not gutting — authored atoms still present,
   flowing directly.
4. `open` both books. Honest layer verdict; "authored candidate" only on the
   operator's read.
