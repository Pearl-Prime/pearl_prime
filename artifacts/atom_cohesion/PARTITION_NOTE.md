# PARTITION_NOTE — sizing & fan-out for chunk B

**Author:** Pearl_Editor · **Chunk A of 5** · **Date:** 2026-06-16
**Purpose:** hand chunk B a concrete partition for applying SCHEMA.md across the full atom corpus.

---

## 1. Volume chunk B must cover (measured, not estimated)

| Quantity | Count | Source |
|---|---:|---|
| Persona dirs (`atoms/*`) | **14** | `corporate_managers, educators, entrepreneurs, first_responders, gen_alpha_students, gen_x_sandwich, gen_z_professionals, gen_z_student, healthcare_rns, midlife_women, millennial_women_professionals, nyc_executives, tech_finance_burnout, working_parents` |
| Topics under a populated persona | ~**15** | e.g. `gen_z_professionals` has 15 topic dirs |
| **Persona × topic clusters (upper bound)** | **~210** | 14 × 15 (sparse — not every cell is populated; real count ≤ this) |
| `CANONICAL.txt` files (slot banks) | **16,292** | `find atoms -name CANONICAL.txt` |
| **Total `## ` atom variants** | **217,534** | `grep -rhcE '^## ' atoms --include=CANONICAL.txt` |
| Variants in the proven cluster | **660** | this cluster, 22 slot dirs |

So chunk A characterized **660 / 217,534 ≈ 0.3%** of the corpus. Chunk B is a ~330× scale-up.

**Tagging cost reality:** the two highest-value tags (`opening_move`, `register`, SCHEMA §A) are **derivable by deterministic heuristic** from atom prose (opening-move from the first sentence shape; register from the EI v2 `_SEMANTIC_FIELDS` / person-tense detection already in `cross_encoder_reranker.py`). So chunk B is **mostly a heuristic batch-tag pass + targeted human review of low-confidence atoms**, NOT 217k hand-authored tags. `emotional_temperature` maps from the existing `_VALENCE_LEXICON`. Only `position_affinity` and `closing_move==dangling` need careful per-slot-type rules. This keeps chunk B tractable.

---

## 2. Recommended partition axis: **slot-type-pair**, not persona×topic

Two candidate axes:

- **Persona × topic** (~210 shards): natural unit, but **wrong for cohesion** — the adjacency rules (`MOVE_COMPAT`, `REG_COMPAT`) are **slot-type-driven and largely persona/topic-invariant** (a `recap` opener jars after a `lands_on_body` close in *every* cluster; WORKED_MAP §4 generalizes). Sharding by persona×topic would re-derive the same compatibility tables 210× and risk 210 inconsistent tables.
- **Slot-type-pair** (the realized adjacencies): the schema's tables are keyed on `(slot_type_N, slot_type_N+1)` × `(move, register)`. There are ~16 slot types but only the **realized** transitions matter — from the cluster's beat structures (BESTSELLER_ATOM_ROUTING §1, `bestseller_structure_map.py` 12 structures), the live adjacency set is on the order of **~30-40 distinct ordered slot-type pairs** (HOOK→STORY, STORY→REFLECTION, REFLECTION→EXERCISE, COMPRESSION→TEACHER_DOCTRINE, STORY→INTEGRATION, …).

**Recommendation:** partition chunk B in **two layers**:
1. **Layer 1 — compatibility tables (do once, centrally):** author the full `MOVE_COMPAT` / `REG_COMPAT` tables + the hard-gate set over the ~30-40 realized slot-type pairs. Persona/topic-invariant. This is the *intelligence*; it must be single-sourced to stay consistent. ~1 focused agent.
2. **Layer 2 — per-atom tagging (fan-out, mechanical):** apply the heuristic tagger to populate `cohesion:` headers across the 14 personas. Shard **by persona** (14 shards), each agent batch-tagging that persona's ~15 topics × ~22 slots, then flagging low-confidence atoms for review. Per-persona keeps each shard's disk/LFS footprint bounded and avoids the cross-persona bleed class entirely (each agent only ever touches one persona's tree).

This mirrors the corpus's own structure (persona-partitioned dirs) and the repo's proven worktree-disk discipline.

---

## 3. Multi-agent fan-out recommendation

**Yes, fan out — but gated and layered:**

- **Layer 1 (tables): single agent, serial, FIRST.** The compatibility tables are the schema's core logic and must not diverge. One agent authors + validates them against ≥3 clusters (this cluster + two others, e.g. a boundaries and a financial_anxiety cluster, to confirm persona/topic-invariance) before any tagging starts. **Gate Layer 2 on Layer 1 merge.**
- **Layer 2 (tagging): fan out up to 14 agents, one per persona, AFTER Layer 1.** Each is mechanical (heuristic tag + flag), low-collision (disjoint persona subtrees), and individually small enough for push-guard. **Disk gate:** worktree dispatch is ~3.2GB/agent via LFS smudge (per repo memory); prune `.claude/worktrees/` and cap concurrency to what disk allows — do **not** fan all 14 simultaneously if disk is tight; batch (e.g. 4-5 at a time). Each persona shard commits via the **plumbing-commit** path (object-DB temp index off `origin/main^{tree}`, `GIT_LFS_SKIP_SMUDGE=1`), never a worktree, since these are hot atom files (same hazard as the composer-frontier content lanes).
- **Validation agent (last): single, serial.** Re-render 2-3 clusters with the adjacency term wired (chunk C dependency) and confirm `flow_score` rises + the §A/§C JAR seams clear. Gate any scale-up on this, per the *validation-before-scaling* rule.

**Do NOT** start Layer 2 tagging or the validation re-render until (a) Layer 1 tables are merged and (b) the chunk-C code edge (feed `prev_selected_atom` into the ranker; apply hard gates as pool pre-filter — SCHEMA §B.3) has a landed PR — otherwise tags exist but nothing consumes them.

---

## 4. Dependency ordering (hand-off chain)

```
A (this chunk: method + SCHEMA + this partition)              ── done, this PR
        │
        ▼
B-Layer-1  author MOVE_COMPAT/REG_COMPAT/hard-gates           ── 1 agent, serial, validate on ≥3 clusters
        │   (persona/topic-invariant core logic)
        ▼
C (code)   wire prev_selected_atom + hard-gate pre-filter      ── enrichment_select.py edge (separate code PR; plumbing-commit)
        │   into the candidate sort (SCHEMA §B.3)
        ▼
B-Layer-2  heuristic batch-tag `cohesion:` headers             ── fan out ≤14 by persona, disk-gated, plumbing-commit
        │   across 14 personas (mechanical + flag-for-review)
        ▼
Validate   re-render 2-3 clusters, confirm flow_score↑          ── 1 agent, serial; GATE scale-up here
```

---

## 5. Bottom line for chunk B

- **Cover:** ~210 (≤) persona×topic clusters, 16,292 banks, 217,534 variants.
- **Partition:** two layers — central **slot-type-pair** compatibility tables (once), then **per-persona** mechanical tagging (fan-out ≤14).
- **Fan-out:** yes for Layer 2 only, disk-gated + plumbing-commit; Layer 1 and validation stay single-agent serial.
- **Gate:** Layer 2 waits on Layer 1 merge **and** the chunk-C consumer edge; scale-up waits on the validation re-render. Tags without a consumer are inert (the exact trap the live `chapter_flow_report` signal already fell into).
