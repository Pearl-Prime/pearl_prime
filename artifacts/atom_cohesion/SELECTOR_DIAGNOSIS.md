# SELECTOR_DIAGNOSIS — why atom slotting produces jarring adjacencies

**Author:** Pearl_Editor (teacher_mode + atoms authority; consulting EI v2)
**Chunk:** A of 5 (foundation) · **Cluster:** `gen_z_professionals × anxiety`
**Date:** 2026-06-16 · **Scope:** READ-ONLY diagnosis of the selector. No code/atom edits.
**Project:** proj_pearl_prime_bestseller_rebase_20260425 (bestseller-quality / composer-frontier thread)

> **One-liner:** The selector scores and ranks every candidate atom **in isolation** — by its own match to per-chapter planner targets + per-chapter thesis keyword overlap — then picks one by a deterministic hash; it has **no model of atom[N]→atom[N+1] adjacency** (no opening-move/closing-move, register, or tone-transition term anywhere in the rank key), so a per-slot "best" atom is routinely placed next to a neighbour it clashes with. That decoupling is the jarring.

---

## 0. Which selector is live (deprecation note)

There are two resolvers; the diagnosis must target the one that drives **production books**:

- `phoenix_v4/planning/slot_resolver.py` is **DEPRECATED** (`slot_resolver.py:1` — *"DEPRECATED: Atom assembly path. Use section registry pipeline"*). It is retained for topics lacking a registry.
- The **live production path** is `phoenix_v4/planning/enrichment_select.py` (the spine pipeline `run_pipeline.py --pipeline-mode spine`), confirmed by the rendered cluster book using `HOOK v32`/`HOOK v56` (the HOOK bank has 88 variants — far beyond the 30 the deprecated path's pools assume) in `artifacts/pearl_prime/standard_book/ahjan_gen_z_professionals_anxiety_en_US_20260518T011019Z/selected_content_variants.json`.

**Both share the same defect** (per-atom isolation scoring). `slot_resolver.py` is the cleaner illustration of the rank key; `enrichment_select.py` is where it actually ships. Both are cited below.

---

## 1. How a variant is picked per slot (the waterfall)

For each `(slot_type, chapter_idx, slot_idx)` the live path resolves a pool, then **ranks every candidate independently**, then **picks one by SHA-256 hash modulo pool size**. The ranking inputs are *entirely properties of the single atom being scored*.

### 1a. `slot_resolver.py` (deprecated path, clearest statement of the rank key)

`resolve_slot()` (`slot_resolver.py:166-321`):

1. Build `available` = pool minus already-used atoms (`:191`), minus already-used `semantic_family` (`:194-198`), optionally band/role-filtered for STORY (`:200-218`), governance-filtered (`:234`).
2. Rank by `_base_rank` (`:266-270`):
   ```python
   def _base_rank(e):
       m = e.metadata or {}
       b   = _bestseller_metadata_score(m, tgt)            # atom-vs-chapter-target
       ths = _thesis_keyword_overlap(thesis_text, m)       # atom-vs-chapter-thesis
       return (-b, -ths, e.atom_id)
   ```
3. Pick deterministically: `idx = _selector_index(selector_key, len(available)); chosen = available[idx]` (`:313-315`), where `selector_key = prefix:slot_type:chNN:sNN` (`:313`).

**Every input to `_base_rank` is a function of the candidate atom `e` alone.** `tgt` and `thesis_text` are per-*chapter* constants, identical for all candidates in the slot. There is no parameter for the previously chosen atom, the next slot, or any neighbour. The only "sequence-aware" logic is **repetition decay** — `used_semantic_families` (`:32`, `:194-198`, `:317-319`) excludes an atom whose family already appeared. That prevents *the same kind of thing twice*; it says **nothing** about whether two *different* adjacent atoms read smoothly together.

### 1b. `enrichment_select.py` (live path, same isolation property)

The live ranker adds bonuses but keeps them strictly per-atom:

- `_bestseller_metadata_score(metadata, target)` (`slot_resolver.py:90-129`; mirrored as `_bestseller_metadata_score` in enrichment_select) — weighted overlap between **one atom's** metadata and the **chapter's** target dict (`reader_objection 4.0`, `proof_mode 3.0`, `tension_type 3.0`, `private_shame_type 3.0`, `propulsion_type 2.5`, `chapter_intent 2.0`, `callback_role 2.5`, `open_loop 2.0`, `shareability 1.5`). Pure atom→target.
- `_metadata_field_bonus(metadata, ch_tgt)` (`enrichment_select.py:313-354`) — additive per-atom bonus for the same target fields (`reader_objection +0.15`, `proof_mode +0.10`, `tension_type +0.10`, `propulsion_type +0.08`, `shareability≥4 +0.05`). Pure atom→target.
- `_collision_family_penalty(metadata, recent_families)` (`enrichment_select.py:357-371`) — returns `-0.20` **iff** the atom's `collision_family` is in *the previous 2 chapters'* families. This is the **only** cross-position term, and it is again **repetition decay across CHAPTERS**, not within-chapter adjacency flow. Docstring (`:361-363`): *"−0.20 if collision_family matches any family in the recent window … from the previous 2 chapters' selected atoms."*

Candidate ordering is then a deterministic sort/SHA pick (e.g. `enrichment_select.py:1489-1491`, `:1546-1550`, `:425-429`) — keyed on `sha256(seed_key:label:i)`, i.e. atom index, never neighbour text.

---

## 2. What `_bestseller_metadata_score` actually captures (and what it cannot)

It captures **per-atom fit to the chapter's editorial intent**: does this atom answer the chapter's target reader-objection / proof-mode / tension-type / shame-type / propulsion / open-loop / shareability? That is a legitimate *relevance* signal — it ensures each slot's atom is on-topic and on-intent for that chapter.

What it **structurally cannot** capture, because both arguments are `(atom_metadata, chapter_target)` and never `(atom_a, atom_b)`:

| Cohesion property the reader feels | Captured? | Why not |
|---|---|---|
| Does atom N's **closing move** hand off to atom N+1's **opening move**? | **No** | No closing/opening-move field is read; no pair is ever compared. |
| Do adjacent atoms share **register** (intimate 2nd-person vs abstract aphorism vs clinical)? | **No** | No register field; target is chapter-level, identical for all candidates. |
| Do adjacent atoms share **person/tense** (you-now vs I-have-observed vs 3rd-person vignette)? | **No** | Not modeled. |
| Is the **emotional temperature** continuous (no whiplash from calm→peak→calm)? | **No** | Per-atom only; cross-chapter valence is checked *post-render* by `emotion_arc_validator`, never fed back into selection. |
| Is an atom whose opening **presupposes book position** ("Seven chapters in…") placed at a compatible position? | **No** | Thesis-overlap can rank such an atom #1 in chapter 1 (see WORKED_MAP §J). |

The repetition-decay terms (`used_semantic_families`, `_collision_family_penalty`) are a **different axis**: they enforce *variety* (don't repeat a family), which is necessary but **orthogonal** to *flow* (do these two different atoms read smoothly together). You can be perfectly varied and perfectly jarring at the same time — which is exactly the rendered book.

---

## 3. Precisely why this produces jarring adjacencies

The composer lays atoms end-to-end in slot order: `HOOK → STORY → REFLECTION → EXERCISE → STORY → TEACHER_DOCTRINE → REFLECTION → EXERCISE → STORY → INTEGRATION` (verified slot sequence, `selected_content_variants.json` ch1). Each was the **independent argmax** for its own slot. Three failure modes follow directly:

1. **Register collision at the seam.** A COMPRESSION atom in tight present-tense 2nd-person ("Your body is running something else entirely.") can sit directly before an abstract aphoristic TEACHER_DOCTRINE atom ("Attachment grows in darkness…"). Both scored well *for their slots*; nothing scored the **transition** between a somatic-imperative register and a contemplative-aphorism register. The reader feels a gear-grind. (WORKED_MAP §A — the JAR pair, `book.txt:6→10`.)

2. **Opening-move / position mismatch.** `INTEGRATION v29` opens with "**Seven chapters in**, I want you to notice what has quietly shifted" and was selected into **chapter 1, slot 10** (`selected_content_variants.json` ch1; rendered `book.txt:31`). Its *thesis-keyword overlap* (pattern/anxiety/notice) ranked it high; its *opening move* ("Seven chapters in") is a closing/recap move that is incoherent at the front of the book. No field gates opening-move against chapter position. This is the cleanest isolation artifact in the cluster.

3. **Broken-tail islands.** The teacher-wrapper tail "In Ahjan's framework, the path begins with." renders as a standalone dangling-prep fragment **8× across the book** (`book.txt:8`, count verified). The selector treats the wrapped atom as one unit and never inspects whether its *closing move* is a complete sentence that can be followed; the fragment becomes an island between two unrelated atoms. (Source = `teacher_wrapper_templates.yaml` ellipsis/dangling-prep templates per COMPOSER_FRONTIER_FIX_SPEC §register_thesis_counter; surfaced here as a **cohesion** failure, not just a register-gate F2.)

### The signal already exists, unconsumed

The pipeline **already measures** this incohesion downstream and then throws it away:
- `editorial_report.json`: **`flow_score: 0.0`**, `grade: NEEDS_REVISION`; `hook_friction: FAIL` on chapters 2,3,… (cascading seam failures).
- `chapter_flow_report.json`: book `status: FAIL`; native counters **transition×13, flow×12, repetition×11, monotone_pacing×12**; CH1 carries `monotone_pacing: consecutive similar-length sentences`.
- `ei_v2_report.json`: monotonicity flagged ×12.

These reports detect the jarring **after** assembly. Nothing routes that signal **back into** `_base_rank` / the enrichment ranker as an adjacency term. **That missing feedback edge is the entire frontier of chunk A.** The fix is not a new scorer — it is (a) cohesion **metadata** on atoms (SCHEMA.md) and (b) an **adjacency rank term** consuming EI v2's already-pairwise reranker (`cross_encoder_reranker.rerank_candidates`, heuristic mode, zero paid API) at the slot-resolution seam.

---

## 4. Citations index (file:line)

| Claim | Location |
|---|---|
| Deprecated path banner | `phoenix_v4/planning/slot_resolver.py:1` |
| Rank key is per-atom (`_base_rank`) | `phoenix_v4/planning/slot_resolver.py:266-270` |
| Per-atom metadata score (atom-vs-target) | `phoenix_v4/planning/slot_resolver.py:90-129` |
| Deterministic SHA pick, no neighbour input | `phoenix_v4/planning/slot_resolver.py:313-315` |
| Only sequence term = family repetition decay | `phoenix_v4/planning/slot_resolver.py:32, 194-198, 317-319` |
| Live per-atom additive bonus | `phoenix_v4/planning/enrichment_select.py:313-354` |
| Live cross-CHAPTER (not adjacency) penalty | `phoenix_v4/planning/enrichment_select.py:357-371` |
| Live SHA candidate ordering | `phoenix_v4/planning/enrichment_select.py:1489-1491, 1546-1550, 425-429` |
| EI v2 pairwise reranker (the consumer) | `phoenix_v4/quality/ei_v2/cross_encoder_reranker.py:127-158` (heuristic default `:141`) |
| EI v2 cross-chapter arc check (post-render) | `phoenix_v4/quality/ei_v2/emotion_arc_validator.py:112-222` |
| Rendered JAR seam | `artifacts/pearl_prime/standard_book/ahjan_gen_z_professionals_anxiety_en_US_20260518T011019Z/book.txt:6,8,10,31` |
| Slot sequence + atom_ids | `…/selected_content_variants.json` (ch1) |
| Downstream signal already computed | `…/editorial_report.json` (flow_score 0.0), `…/chapter_flow_report.json` (transition/flow/monotone counters) |
