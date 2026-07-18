# SCHEMA — atom cohesion metadata ("how atoms go together")

**Author:** Pearl_Editor · **Chunk A of 5 (THE core deliverable)** · **Date:** 2026-06-16
**Project:** proj_pearl_prime_bestseller_rebase_20260425 (bestseller-quality / composer-frontier thread)
**Status:** schema definition (analysis only — no code, no atom edits). Proven on `gen_z_professionals × anxiety`.

This schema makes atom adjacency a **decidable** property at selection time. It has two halves:
**(A)** per-atom tags that *predict* cohesion, and **(B)** pairwise compatibility rules that decide whether atom N may precede atom N+1. It is consumed by EI v2's **existing** machinery (`cross_encoder_reranker`, `emotion_arc_validator`) — **no new scorer is built**.

---

## 0. Design constraints (from the diagnosis)

1. **Adjacency-aware, not per-atom-aware.** The defect is that `_base_rank` scores atoms in isolation (SELECTOR_DIAGNOSIS §1-2). The schema must express a relation between *two* atoms, plus a small set of absolute facts about *one* atom that gate which atoms it can neighbour.
2. **Leverage, don't rebuild.** `cross_encoder_reranker.rerank_candidates(thesis, texts, ids)` is already a **pairwise text-vs-text** heuristic scorer (`cross_encoder_reranker.py:127`, default `mode="heuristic"`, zero deps, deterministic). Feed it `(prev_atom_text, candidate_text)` to get a flow score; the tags below *bias and gate* that score. `emotion_arc_validator` already owns cross-chapter valence (`emotion_arc_validator.py:112`).
3. **Deterministic + local.** No paid LLM/image API. All tag values are closed vocabularies; all rules are table lookups. Re-renders at the same seed reproduce.
4. **Backward-compatible & optional.** Missing tags must degrade gracefully (atom still selectable; adjacency term contributes 0), exactly like the existing `_metadata_field_bonus` graceful-fallback pattern (`enrichment_select.py:325-326`).
5. **Reuses existing family tags.** `compression_family` / `family` stay as **repetition-decay** axes (orthogonal). The new tags are a **separate `cohesion:` block**, not a rename.

---

## A. Per-atom cohesion tags

All live under a single `cohesion:` mapping in the atom's metadata block (storage in §5). Every field is **optional** and drawn from a **closed vocabulary**.

| Field | Vocabulary (closed) | What it predicts | Example (cluster) |
|---|---|---|---|
| `opening_move` | `scene_drop`, `direct_address`, `aphorism`, `mechanism_name`, `continuation`, `question`, `permission`, `imperative`, `recap` | The *first beat* a reader hits; the primary adjacency hinge. | `INTEGRATION v29` = `recap` ("Seven chapters in…") |
| `closing_move` | `lands_on_body`, `opens_loop`, `completes_claim`, `invites_practice`, `hands_to_next`, `resolves`, `dangling` (defect) | The *last beat*; what the next atom must accept. | wrapper tail = `dangling` |
| `register` | `intimate_2p` (you-now), `clinical_explain`, `aphoristic`, `vignette_3p`, `instructional`, `confessional_1p` (I-have-observed) | Voice/altitude; drives the soft clash matrix. | COMPRESSION = `intimate_2p`; TEACHER_DOCTRINE = `aphoristic` |
| `person_tense` | `2p_present`, `3p_past`, `1p_present`, `imperative`, `mixed` | Grammatical footing; hard-clash on abrupt swaps. | recognition STORY = `3p_past` |
| `emotional_temperature` | integer −3…+3 (−3 peak distress … 0 neutral/observational … +3 relief/agency) | Continuity of felt arc; maps onto `emotion_arc_validator` valence. | DOCTRINE ≈ 0; turning_point INTEGRATION ≈ +2 |
| `position_affinity` | `any`, `opening` (ch1-2), `early`, `middle`, `late` (ch7+), `closing` (final ch) | Legal chapter range for position-presupposing atoms. | `INTEGRATION v29` = `late` (was mis-placed at ch1) |
| `cohesion_family` *(optional)* | free short string (e.g. `alarm_body`, `attachment_meta`) | Thematic clustering distinct from de-dup `family`; used only as a tiebreak, never a hard gate. | — |

Notes:
- `emotional_temperature` is a **signed int**, deliberately mappable to the `_VALENCE_LEXICON` range in `emotion_arc_validator.py:25-57` (which is roughly [−0.8, +0.4]); the validator can ingest it directly as an arc waypoint.
- `closing_move: dangling` is the **defect marker** for broken/truncated tails (the wrapper fragment). An atom (or rendered wrapper) tagged `dangling` is *never* a legal predecessor (§B rule H3).
- `register` and `opening_move` are the two highest-value fields (they decide §A's HARD-JAR). If an authoring budget forces a subset, author those two first.

---

## B. Pairwise / adjacency compatibility

Cohesion of the seam `(N → N+1)` = **gate ∧ score**.

### B.1 Hard gates (a TRUE gate ⇒ the pair is forbidden; candidate is dropped from the slot pool)

| ID | Rule | Rationale (cluster evidence) |
|---|---|---|
| **H1** | `N+1.opening_move == recap` is forbidden unless `chapter_index ∈ position_affinity` range. | `INTEGRATION v29` "Seven chapters in…" at ch1 (WORKED_MAP §C). |
| **H2** | `N+1.position_affinity` must include the current `chapter_index`. | same defect, generalized. |
| **H3** | `N.closing_move == dangling` ⇒ N may not be a predecessor of anything (and should fail a delivery guard). | wrapper tail island (WORKED_MAP §A line 8). |
| **H4** | Hard register-clash set: `{intimate_2p, confessional_1p} → aphoristic` with **no** intervening bridge beat is forbidden. | COMPRESSION→TEACHER_DOCTRINE seam (WORKED_MAP §A). |

### B.2 Soft compatibility (contributes a signed term to the slot rank key; does not drop the candidate)

For seam `(N → N+1)`:

```
adjacency_term(N, N+1) =
      w_flow   * rerank_pair_score(N.text, candidate.text)          # EI v2 heuristic, [0,1]
    + w_move   * MOVE_COMPAT[N.closing_move][candidate.opening_move] # table, [-1,+1]
    + w_reg    * REG_COMPAT[N.register][candidate.register]          # table, [-1,+1]
    - w_temp   * abs(candidate.emotional_temperature - N.emotional_temperature) / 6.0   # whiplash penalty, [0,1]
```

- `rerank_pair_score` = call `cross_encoder_reranker.rerank_candidates(thesis=N.text, texts=[cand.text], ids=[cand.id])[0]["score"]` — **reuses the existing pairwise heuristic verbatim** (`cross_encoder_reranker.py:127-158`); the "thesis" slot simply carries the previous atom's text. No new model.
- `MOVE_COMPAT` / `REG_COMPAT` are small closed tables (vocab × vocab). Seed values (proven directions, full tables authored in chunk B per partition):
  - `MOVE_COMPAT[lands_on_body][continuation] = +1.0`; `[completes_claim][continuation] = +0.8` (WORKED_MAP §B FLOW).
  - `MOVE_COMPAT[*][recap] = -1.0` (always jarring unless position-gated; belt-and-suspenders with H1).
  - `REG_COMPAT[intimate_2p][vignette_3p] = +0.6` (purposeful, WORKED_MAP §E); `REG_COMPAT[intimate_2p][aphoristic] = -1.0` (WORKED_MAP §A).
- Weights `w_flow≈0.4, w_move≈0.3, w_reg≈0.2, w_temp≈0.1` (start point; tunable like the EMA weights in EI_V2_REGISTRY_LEARNING; **not** a GA — deterministic).

### B.3 Where it plugs into the live ranker

Add `adjacency_term(prev_selected, candidate)` as an **additive component** alongside `_metadata_field_bonus` and `_collision_family_penalty` in the enrichment_select candidate sort (the sort sites at `enrichment_select.py:1489-1491 / 1546-1550 / 425-429`), where `prev_selected` is the atom chosen for the immediately-preceding slot in render order. This is the **one missing edge**: the ranker gains a reference to atom[N] when scoring atom[N+1]. (Wiring is chunk-C/code work — OUT OF SCOPE here; the schema only specifies the contract.) The hard gates (B.1) filter the pool *before* the SHA pick, mirroring how governance/band filters already prune `available` in `slot_resolver.py:200-234`.

---

## 5. Storage decision

**Chosen: atom-header field (a `cohesion:` block in the existing `## <SLOT> vNN` metadata), with a generated sidecar index for fast pairwise lookup.**

Rationale:
- The atoms **already carry header metadata** in exactly this shape — `compression_family: C1` and `family: F2` live in the `---`-delimited header under each `## ` variant (verified: `atoms/gen_z_professionals/anxiety/COMPRESSION/CANONICAL.txt:7,14,…`). Adding a `cohesion:` block is **the same mechanism the selector already parses**, so no new parser path and graceful-fallback comes for free.
- Header-local keeps the tag **co-located with the prose it describes** (authoring + review happen in one file; no drift between a sidecar and the text).
- A **derived** sidecar `artifacts/atom_cohesion/index/<persona>__<topic>.cohesion.json` (generated from headers, never hand-edited) gives EI v2 an O(1) `{atom_id → cohesion tags}` map and lets the adjacency term avoid re-parsing CANONICAL.txt per seam. Sidecar is a cache, headers are SSOT.

**Rejected:** a pure standalone sidecar as SSOT (drifts from prose; repeats the gap_matrix-TSV staleness failure mode). **Rejected:** a new YAML registry (reinvention; the header path exists).

### 5.1 Header shape (illustrative; tags shown, prose elided — NO atom is edited in this chunk)
```
## INTEGRATION v29
---
cohesion:
  opening_move: recap
  closing_move: resolves
  register: intimate_2p
  person_tense: 2p_present
  emotional_temperature: 2
  position_affinity: late
  cohesion_family: pattern_seen
---
<atom prose…>
```

### 5.2 EI v2 consumption contract
- `cross_encoder_reranker.rerank_candidates` consumes the **prose** pairwise (already does) — schema adds the `MOVE_COMPAT`/`REG_COMPAT`/temperature terms around it.
- `emotion_arc_validator.validate_emotion_arc` consumes `emotional_temperature` as an arc waypoint (maps to its valence range, `emotion_arc_validator.py:25-57,74-87`) so the cross-chapter check uses authored intent, not only lexicon estimate.
- `domain_embeddings.domain_thesis_similarity` is **unaffected** (it scores atom-vs-thesis relevance, a different axis we keep).

---

## 6. Graceful-degradation & determinism guarantees

- Any missing `cohesion:` field ⇒ its term contributes **0** and its hard gate is **not applied** (atom remains selectable). Identical to `_metadata_field_bonus` returning 0 on absent metadata (`enrichment_select.py:325-326`).
- All tables are static; `rerank_pair_score` is heuristic/deterministic. Same seed ⇒ same book. No GA, no online learning, no network.
- Adjacency term is **additive**, so it cannot by itself starve a slot (the SHA pick still runs over whatever survives the hard gates, and HOOK/SCENE reuse-fallback at `slot_resolver.py:236` still applies).

---

## 7. Two fully-filled worked pairs

### 7.1 ✅ FLOW pair (fully filled)

Seam: STORY/turning_point (`book.txt:33`) → INTEGRATION body (`book.txt:35`). WORKED_MAP §B.

```
N   (predecessor)                         N+1 (candidate)
atom: STORY …turning_point:overwhelm:v08  atom: INTEGRATION v29 (body)
cohesion:                                 cohesion:
  opening_move: mechanism_name              opening_move: continuation
  closing_move: completes_claim             closing_move: resolves
  register: intimate_2p                     register: intimate_2p
  person_tense: 2p_present                  person_tense: 2p_present
  emotional_temperature: 0                  emotional_temperature: +2
  position_affinity: any                    position_affinity: late
```
Gate check: H1/H2 — candidate opening_move=`continuation` (not `recap`) ⇒ pass; H3 — N.closing_move=`completes_claim` (not `dangling`) ⇒ pass; H4 — `intimate_2p → intimate_2p` ⇒ pass.
Score:
```
w_flow * rerank("The pattern is this…","What changes at this point…")  ≈ 0.4 * 0.72 = 0.29   (shared tokens: pattern/alarm/anxiety + body field)
w_move * MOVE_COMPAT[completes_claim][continuation]                     = 0.3 * (+0.8) = +0.24
w_reg  * REG_COMPAT[intimate_2p][intimate_2p]                           = 0.2 * (+1.0) = +0.20
w_temp * |(+2)-(0)|/6                                                   = 0.1 * 0.333  = -0.03
-------------------------------------------------------------------------------------------
adjacency_term ≈ +0.70   → strongly preferred; reads as one continuous thought.
```
*(Caveat: only the **body** of `INTEGRATION v29` flows here; its real shipped **opener** is `recap` — which is precisely the §7.2 problem. The fix authors the opener as `continuation`, or H1 drops it from ch1.)*

### 7.2 ❌ JAR pair (fully filled)

Seam: COMPRESSION (`book.txt:6`) → TEACHER_DOCTRINE v01 (`book.txt:10`). WORKED_MAP §A (the broken wrapper tail at line 8 is itself an H3 `dangling` island between them).

```
N   (predecessor)                         N+1 (candidate)
atom: COMPRESSION (calendar/body)         atom: TEACHER_DOCTRINE v01 (attachment/darkness)
cohesion:                                 cohesion:
  opening_move: direct_address              opening_move: aphorism
  closing_move: lands_on_body               closing_move: completes_claim
  register: intimate_2p                     register: aphoristic
  person_tense: 2p_present                  person_tense: 3p_present
  emotional_temperature: -1                 emotional_temperature: 0
  position_affinity: any                    position_affinity: any
```
Gate check: **H4 FIRES** — `intimate_2p → aphoristic` with no intervening bridge beat is a hard register-clash ⇒ **candidate dropped from the pool** (the ranker is forced to pick a doctrine variant whose opener bridges, or to insert a PIVOT/PERMISSION beat first).
If H4 did not gate, the soft score would also reject it:
```
w_flow * rerank("…body is running something else…","Attachment grows in darkness…")  ≈ 0.4 * 0.10 = 0.04   (near-zero token/field overlap)
w_move * MOVE_COMPAT[lands_on_body][aphorism]                                         = 0.3 * (-0.6) = -0.18
w_reg  * REG_COMPAT[intimate_2p][aphoristic]                                          = 0.2 * (-1.0) = -0.20
w_temp * |(0)-(-1)|/6                                                                 = 0.1 * 0.167  = -0.02
-------------------------------------------------------------------------------------------
adjacency_term ≈ -0.36   → strongly dispreferred; matches the reader's gear-grind.
```
And the line-8 wrapper tail (`closing_move: dangling`) is independently rejected by **H3** as a hand-off point — closing the third defect in this seam.

---

## 8. Summary (for chunk B + the operator)

- **What it is:** a `cohesion:` header block (7 closed-vocab per-atom tags) + a pairwise gate∧score over `(opening_move, closing_move, register, person_tense, emotional_temperature, position_affinity)`.
- **What it fixes:** the three rendered defect classes in the cluster — register collision (H4/REG_COMPAT), position-presupposing openers (H1/H2/position_affinity), and dangling-tail islands (H3) — i.e. the operator's "jarring, choppy."
- **What it reuses (no rebuild):** `cross_encoder_reranker.rerank_candidates` for the pairwise flow score; `emotion_arc_validator` for cross-chapter temperature; the existing header-metadata parser + graceful-fallback for storage.
- **What stays orthogonal:** `compression_family`/`family`/`collision_family` remain repetition-decay (variety), unchanged.
- **The one code edge (chunk C, not here):** feed `prev_selected_atom` into the enrichment_select candidate sort so the adjacency term can be computed; apply hard gates as a pool pre-filter.
