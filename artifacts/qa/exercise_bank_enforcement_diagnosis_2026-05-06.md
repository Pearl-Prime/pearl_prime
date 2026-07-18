# EXERCISE Bank Enforcement — Diagnosis & Pearl_Architect Routing Options (2026-05-06)

**Author:** Pearl_Dev
**Triggering finding:** smoke run on `gen_z_professionals × anxiety × compact_book_8ch_30min` (PR #892 verification, 2026-05-06) emitted `EXERCISE FALLBACK: Using library_34 for chapter X` warnings on every chapter.
**Operator concern (verbatim):** EXERCISE should resolve from EXACTLY ONE of two canonical banks: (A) the 37 somatic exercises bank, or (B) the 9 exercise types bank, each entry carrying the 5-part structure: `intro · desc · guidance · ah-ha · integration`. The `library_34` fallback is wrong for production runs.

**Verdict:** **Phase 3.B escalation** — the actual situation is more nuanced than the operator's framing implies, AND the smallest fix sites are outside this session's WRITE_SCOPE. Concrete options for Pearl_Architect ruling at the end.

---

## Phase 1 findings — bank discovery

### Bank A — the 37-somatic bank

| Field | Value |
|---|---|
| **Path on disk** | `SOURCE_OF_TRUTH/practice_library/inbox/exercises_ab_tady_37_PRODUCTION_READY.json` (101 KB) |
| **Item count** | 39 (file says `total_count: 39`; operator's "37" is approximate) |
| **5-part structure present?** | **YES** — every item has `components: {bridge, intro, description, aha, integration}` with both `full` and `lean` variants |
| **Map to operator's vocabulary** | `intro` ✓, `description` ≈ "desc" or "guidance" (the how-to-do-it prose), `aha` ✓, `integration` ✓; the bank's `bridge` is an extra component (lead-in framing) |
| **In canonical store?** | **NO** — `exercises_ab_tady_37_PRODUCTION_READY.json` is in `inbox/` but the ingest script (`scripts/practice/ingest_practice_libraries.py:60-90`) **strips the `components` field**, writing only `text` to `practice_items.jsonl`. Result: 0 `ab37_*` items in the canonical store. |

### Bank B — the 9-types bank

| Field | Value |
|---|---|
| **Path on disk** | `SOURCE_OF_TRUTH/practice_library/inbox/{8 content_types}_library_34_PRODUCTION_READY.json` |
| **Content types found** | `affirmations, body_awareness, integration_bridges, meditations, reflections, self_inquiry, sensory_grounding, thought_experiments` (**8 of 9 present**; `gratitude_practices` named in README but absent on disk) |
| **Item count** | 8 × 34 = 272 items (across 8 PRODUCTION_READY files) |
| **5-part structure present?** | **YES** — same `components: {bridge, intro, description, aha, integration}` schema as Bank A |
| **In canonical store?** | **NO** — same ingest issue: `_ingest_library_34` reads the SKINNY `*_library_34.json` files (15-20 KB each, no components) and ignores the `*_PRODUCTION_READY.json` files (65-75 KB each, with components). The 272 items in `practice_items.jsonl` carry only `text` + null `blocks: {setup, instruction, prompt, close}`. |

### What's actually in the canonical store today

`SOURCE_OF_TRUTH/practice_library/store/practice_items.jsonl` — 272 items, all `source: "library_34"`, all 8 content types, **zero items with the 5-part structure**. The `blocks` field is uniformly `{setup: null, instruction: null, prompt: null, close: null}` (a 4-part NULL placeholder, NOT the 5-part operator schema).

---

## Phase 2 findings — resolver-path tracing

### Two parallel consumers of the practice library

The codebase has **two independent paths** reading the practice library:

#### Path 1 — `phoenix_v4/exercises/practice_library_loader.py:load_practice_library()`
- Reads from inbox `*_PRODUCTION_READY.json` directly (line 70).
- Loads the FULL data including the `components` field (5-part structure preserved).
- Cached via `_LIBRARY_CACHE` module-global.
- Used by `get_random_exercise_for_chapter` (line 213) which composes `bridge + intro + description + aha + integration` (line 218 docstring) and emits the misleading `EXERCISE FALLBACK: Using library_34` warning at line 235.
- This path's output **already carries the 5-part structure** to the rendered book.

#### Path 2 — `phoenix_v4/planning/practice_selector.py:get_practice_prose_map()` → `practice_items.jsonl`
- Reads the canonical store at `SOURCE_OF_TRUTH/practice_library/store/practice_items.jsonl`.
- Only sees the SKINNY items (text only; no components).
- Used by `phoenix_v4/rendering/prose_resolver.py:336` to populate the `prose_map` for slot resolution.

The two paths feed different stages of the pipeline:
- `prose_resolver.get_practice_prose_map()` → contributes `practice_id → text` mapping (no 5-part structure).
- `chapter_composer` (via `practice_library_loader`) → composes 5-part exercises directly.

### Where `library_34` log message comes from

**File:** `phoenix_v4/exercises/practice_library_loader.py:230-237`
```python
logger.warning(
    "EXERCISE FALLBACK: Using library_34 for chapter %d topic %s persona %s. "
    "No registry or teacher exercise was available for this slot — add EXERCISE coverage upstream if this is unexpected.",
    chapter_index,
    topic_id or "(unknown)",
    persona_id or "(unknown)",
)
```

This warning is **misleading by name**. The function `get_random_exercise_for_chapter` actually loads BOTH the 8 `library_34_*` types AND the 39 `ab37_*` exercises via `load_practice_library()` from PRODUCTION_READY inbox files (line 70). Calling its output "library_34" is residual naming from before the ab_tady_37 file was added.

### What audit JSON actually records

For the gen_z×anxiety smoke run (`/tmp/bestseller_smoke_ssot_refactor_genz/enrichment_audit.json`), the EXERCISE sections (chapters 5 and 7) record:
```json
{
  "chapter": 5, "slot_index": 3, "slot_type": "EXERCISE",
  "source": "practice_library",
  "source_id": "practice_library",   <-- generic; loses which specific ab37 / lib34 item was used
  "variant_id": "",
  "words": 155
}
```

So the audit calls it `"practice_library"` (which IS the spec §4.5 third source name) — NOT `"library_34"`. The "library_34" label only appears in the warning log, not the structured audit.

### Production-vs-draft branching

`grep -rn "quality_profile" phoenix_v4/planning/enrichment_select.py scripts/run_pipeline.py` shows quality_profile threads through the pipeline (production / draft / debug / flagship) but **does not currently restrict EXERCISE source selection by profile**. The same fallback chain runs regardless of profile.

### What's actually in the rendered book.txt

Looking at `/tmp/bestseller_smoke_ssot_refactor_genz/book.txt` chapter 1, the EXERCISE block contains all 5 components in sequence (extracted excerpt):

> **[description/guidance]** "Place both feet on the floor and name what supports your weight. Do this with the part of your body that reacted first. Breath is the one system you can regulate consciously and immediately."
> **[intro]** "This is a breath-based practice. You are not trying to breathe perfectly or deeply. You are giving your nervous system a rhythm it can follow…"
> **[bridge]** "Before you keep reading. Not to fix anything. Just to give yourself a different input for a moment."
> **[intro #2]** "This is Transition Ritual. Bring it with you…"
> **[integration]** "As you move from this practice back into your day, create a simple transition ritual…"
> **[aha]** "Now, I want you to notice something. Notice what you want to do differently…"
> **[aha #2]** "Now, before you move on, try it once. see what happens. Nothing has to change from this moment forward. Keep going."

**The 5-part structure IS reaching the rendered output.** Multiple practice items are being concatenated within one EXERCISE slot (suggesting word-target driven multi-item assembly), and the parts arrive interleaved rather than in canonical `intro→desc→guidance→aha→integration` order.

---

## Why the operator's "library_34 fallback wrong" framing maps imperfectly to the code reality

| Operator framing | Code reality |
|---|---|
| "library_34 fallback is wrong for production" | The string `library_34` is in the warning log message, but the audit records `source: "practice_library"` (spec §4.5 third source). The 39 ab37 + 272 lib34 items reach the resolver via the same loader. |
| "EXERCISE should resolve from EXACTLY ONE bank" | Currently `practice_library_loader` loads BOTH banks into one pool and selects one item per slot. Operator may want per-format or per-quality-profile bank selection. |
| "Each entry has 5-part structure" | The PRODUCTION_READY files DO have 5-part structure. They're delivered to chapter_composer via `get_random_exercise_for_chapter`. The composed text ends up in book.txt with all 5 parts visible (though sometimes interleaved across multiple items in a single slot). |
| "Eliminate the library_34 fallback for production" | The deeper concern is probably: production should hit a HIGHER-priority source (persona-atom canonical or teacher_banks) BEFORE falling through to practice_library. For gen_z×anxiety the higher sources are empty (#887 atom-backfill deferred EXERCISE) → fall-through is the spec §4.5 behavior, not a bug. |

---

## Smallest possible fix sites

| Issue | Fix site | Lines | In WRITE_SCOPE? |
|---|---|---:|---|
| Misleading `EXERCISE FALLBACK: Using library_34` log message | `phoenix_v4/exercises/practice_library_loader.py:230-237` (rename to "EXERCISE: Using practice_library per spec §4.5 third source") | ~5 | **NO** |
| Audit `source_id: "practice_library"` loses specific practice_id traceability (e.g., `lib34_meditations_03`, `ab37_breath_regulation_01`) | `phoenix_v4/rendering/chapter_composer.py:1748-1908` (where `exercise_from_library_34` is set + audit row is emitted) | ~10 | **NO** |
| Two parallel paths (`practice_library_loader` reads PRODUCTION_READY; `practice_selector` reads `practice_items.jsonl`) drift on schema | Either: (a) re-ingest with `components` preserved (`scripts/practice/ingest_practice_libraries.py` + `normalize_practice_items.py`); (b) collapse to one loader. | ~50–100 | **NO** (multi-file across scripts/ + phoenix_v4/) |
| Production quality_profile permits fall-through to practice_library when persona-atom + teacher_banks are empty | `scripts/run_pipeline.py` could add a `quality_profile=production` strict gate that raises `EnrichmentGapError` when EXERCISE falls through. | ~20-30 | **YES** (one allowed file) |
| Missing 9th content type (`gratitude_practices`) absent from inbox + store | Content authoring | n/a | **NO** (operator scope: "do NOT write new exercises") |

**None of the receipt's 5 in-scope files** (`enrichment_select.py`, `prose_resolver.py`, `content_banks/loader.py`, `content_banks/selector.py`, `run_pipeline.py`) **carry the misleading log message OR the schema-bridge issue.** Only the production-strict-gate option lives in scope, and that one ENFORCES the operator's intent (force higher-priority sources, fail explicitly when they're empty) without touching the misleading-name issues.

---

## ESCALATION — three options for Pearl_Architect

### Option 1 — Strict-canonical EXERCISE for production quality_profile (in scope)
**Scope:** ~20–30 lines in `scripts/run_pipeline.py`, single file, single PR.
**Implementation:** Add a `quality_profile=production` check that raises `EnrichmentGapError` (or equivalent) when an EXERCISE slot would resolve via `practice_library` (the spec §4.5 third source). Force `production` to use only persona-atom canonical OR teacher_banks. Draft / debug / flagship profiles untouched.
**Pros:**
- Stays in WRITE_SCOPE.
- Most strictly honors operator's "production must use canonical banks" framing.
- Makes the content gap explicit (gen_z×anxiety EXERCISE absence becomes a hard fail instead of silent fall-through).
**Cons:**
- **Blocks all current production renders** until #887 atom backfill extends to EXERCISE for every (persona, topic) combo we want to ship — and that's content-authoring work, not code.
- Doesn't address the misleading log message or the ingest-script `components`-stripping (those remain).
- Reframes the operator's concern from "the bank is wrong" to "we don't have enough atom coverage" — the underlying truth, but a harder ask.

### Option 2 — Re-ingest with `components` preserved + collapse to one path (out of scope; structural)
**Scope:** ~50–100 lines across `scripts/practice/ingest_practice_libraries.py` + `scripts/practice/normalize_practice_items.py` + `phoenix_v4/planning/practice_selector.py` + tests. Multi-file.
**Implementation:** Update ingest to preserve the `components` field; update `PracticeItem` schema to allow `components`; update `practice_selector.get_practice_prose_map()` to expose components; remove the parallel `practice_library_loader` path or unify it with `practice_selector`.
**Pros:**
- Fixes the schema-bridge issue at root.
- Makes both paths see the 5-part structure.
- The misleading "library_34" log message naturally goes away because the loader is rewritten.
**Cons:**
- Out of receipt's WRITE_SCOPE.
- Multi-file structural change; needs cap-entry authority before Pearl_Dev can ship.
- Re-architects the practice-library data pipeline; risk of subtle behavior drift.
- Doesn't enforce production-vs-draft branching (orthogonal to operator's concern).

### Option 3 — Cosmetic naming + audit traceability fix (out of scope; small)
**Scope:** ~15 lines across `phoenix_v4/exercises/practice_library_loader.py` + `phoenix_v4/rendering/chapter_composer.py`. Two files.
**Implementation:** Rename the log message; set audit `source_id` to actual practice_id; do NOT change resolution logic.
**Pros:**
- Eliminates the operator's most visible complaint (the misleading log).
- Minimal surface area; minimal risk.
**Cons:**
- **Doesn't actually change EXERCISE resolution behavior** — it's pure log-message cleanup + traceability.
- Out of receipt's WRITE_SCOPE (different files).
- Doesn't address production-strictness or the schema-bridge issue.
- May not satisfy the operator's "library_34 fallback wrong for production" intent if their underlying concern is content-quality, not log-name.

---

## Recommended path

**Option 1** preserves operator intent ("production must use canonical banks") with the smallest in-scope code change, AND surfaces the content gap (#887 EXERCISE-deferral) as an explicit operator decision instead of silent fall-through.

**Option 2** is the right long-term fix for the schema-bridge issue (two parallel paths is a real design smell), but it's a structural change that should be its own cap entry + Pearl_Dev session.

**Option 3** alone is cosmetic and won't satisfy the operator's framing.

**Best combination:** ratify Option 1 immediately to honor production strictness; queue Option 2 as a separate Pearl_Architect cap entry for the schema-bridge unification; treat Option 3's log-rename as a free-rider opportunity to fold into Option 1 or Option 2 (whichever lands first).

The 9th content-type (`gratitude_practices`) absence + the #887 EXERCISE atom-backfill scope-deferral are content-authoring escalations to Pearl_Editor + Pearl_Writer, independent of the architectural ruling.

---

## Pearl_Architect cap-entry skeleton (suggested ID: EXERCISE-BANK-RESOLUTION-01)

> **Status:** ratified
> **Context:** Pearl_Dev STOP 2026-05-06 surfaced that the operator's "library_34 fallback wrong for production" concern actually conflates four distinct issues: (i) misleading log message, (ii) audit traceability gap, (iii) two parallel practice-library code paths with different schemas, (iv) production-quality runs falling through to the spec §4.5 third source because higher sources are empty.
> **Decision:** [pick Option 1 / 2 / 3 / hybrid; cap entry says which]
> **Action items:** [Pearl_Dev follow-up under existing or new ws]
> **Handoffs:** [Pearl_Editor + Pearl_Writer for #887 EXERCISE atom backfill]

---

## Appendix — exact paths searched in Phase 1.3

| Search | Result |
|---|---|
| `find . -name '*somatic*' -type f` | 25 hits — `registry/somatic_healing.yaml`, `template_expand2/qaudiobook_template_v2_somatic.zip`, etc. None matched the 37-bank shape. |
| `grep -rln "37.*somatic\|37.*exercise"` | 18 hits — mostly docs/spec references; ingest script names the file. |
| `grep -rln 'intro:' SOURCE_OF_TRUTH/ \| xargs grep -l 'guidance' \| xargs grep -l 'ah[-_ ]?ha\|aha'` | 1 hit — `SOURCE_OF_TRUTH/practice_library/inbox/thought_experiments_library_34_PRODUCTION_READY.json` |
| `find . -name 'exercises_v4'` | not present |
| `ls SOURCE_OF_TRUTH/practice_library/inbox/` | 17 files: `*_library_34.json` (8 skinny), `*_library_34_PRODUCTION_READY.json` (8 rich), `exercises_ab_tady_37_PRODUCTION_READY.json` (1 rich) |
