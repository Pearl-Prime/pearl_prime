# Anxiety P0 Overlay-Backing Slice — Closeout

**Date:** 2026-07-10
**Agent:** Pearl_Editor
**Project:** proj_pearl_prime_bestseller_rebase_20260425
**Scope:** `SOURCE_OF_TRUTH/teacher_banks/**` overlay-routed atom authoring (Class 2 per `docs/PEARL_PRIME_ATOM_100PCT_COVERAGE_SSOT.md` §3)

## What was authored

`kenjin` (Sōtō Zen teacher) had a completely empty `approved_atoms/PERMISSION/`
directory — the only overlay slot type where kenjin had zero atoms (every
other overlay type — TEACHER_DOCTRINE=5, and all others — already had real
content). Any Teacher-Mode book routed to `teacher_id: kenjin` would resolve
PERMISSION with an empty pool.

Authored 3 new PERMISSION atoms, anxiety-themed, in kenjin's authentic
Sōtō Zen voice (doctrine-grounded per `doctrine/doctrine.yaml` — mu-shotoku,
shikantaza, shinjin-datsuraku):

- `SOURCE_OF_TRUTH/teacher_banks/kenjin/approved_atoms/PERMISSION/kenjin_PERMISSION_000.yaml`
- `SOURCE_OF_TRUTH/teacher_banks/kenjin/approved_atoms/PERMISSION/kenjin_PERMISSION_001.yaml`
- `SOURCE_OF_TRUTH/teacher_banks/kenjin/approved_atoms/PERMISSION/kenjin_PERMISSION_002.yaml`

This clears kenjin's PERMISSION bank to the ≥3-variant floor
(`SPEC-739-THRESHOLD-01`), matching schema precedent from `ahjan` / `miki` /
`joshin` PERMISSION atoms (`atom_id`, `band`, `body`, `teacher.{teacher_id,
source_refs, synthesis_method}`).

## Discovery correction to the P0 gap matrix (important — do not re-author blind)

`artifacts/qa/pearl_prime_atom_100pct_gap_matrix_20260606.tsv` models
teacher-bank overlay atoms (QUOTE / TEACHER_DOCTRINE / PERMISSION_GRANT) as
**per-(persona, topic) cells** requiring ≥3 variants each. The actual runtime
loader (`phoenix_v4/planning/pool_index.py:_load_teacher_pool` +
`PoolIndex.get_pool`) has **no topic filter at all** — it loads every
`*.yaml` under `teacher_banks/<teacher>/approved_atoms/<slot_type>/`
regardless of topic or persona. The pool is per-**teacher**-per-**slot-type**,
full stop.

Practical implication verified on-disk (counts as of this session):

| Teacher | TEACHER_DOCTRINE | PERMISSION |
|---|---:|---:|
| adi_da | 8 | 20 |
| ahjan | 19 | 15 |
| joshin | 5 | 15 |
| junko | 4 | 15 |
| **kenjin** | 5 | **0 → 3 (this slice)** |
| maat | 5 | 15 |
| master_feung | 4 | 15 |
| master_sha | 4 | 15 |
| master_wu | 4 | 15 |
| miki | 4 | 15 |
| miyuki | 4 | 15 |
| omote | 4 | 15 |
| pamela_fellows | 4 | 15 |
| ra | 5 | 15 |
| sai_ma | 12 | 15 |

Every teacher except kenjin was already at or above the ≥3 floor for both
types **before this session**. The SSOT's "105 P0 rows / 0 current_variants
everywhere" framing is stale against the actual on-disk state and against the
actual (topic-agnostic) runtime schema — it appears to model a
per-(persona,topic)-tagged schema that was never implemented. **kenjin
PERMISSION=0 was the one real, current, code-wired gap** across the
TEACHER_DOCTRINE/PERMISSION axis. This is flagged here rather than silently
re-interpreted; `docs/PEARL_PRIME_ATOM_100PCT_COVERAGE_SSOT.md` §9 gap matrix
itself is out of this lane's WRITE_SCOPE and was not edited.

## QUOTE — explicitly out of scope for this slice (do not author blind)

The SSOT (§3 Class 2, `QUOTE-ATOM-ROUTING-01`) names
`teacher_banks/<teacher>/approved_atoms/QUOTE/*.yaml` as the canonical QUOTE
routing. **This is not wired into the live resolver.**
`phoenix_v4/planning/registry_resolver.py` `_TEACHER_OVERLAY_TYPES` and
`_TEACHER_TYPE_MAP` (the tables that drive which teacher-bank slot dirs get
consulted for a given registry section type) do **not** include `QUOTE`.
Live QUOTE injection instead runs through
`phoenix_v4/planning/accent_planner.py:_load_quotes()`, reading
`SOURCE_OF_TRUTH/accent_banks/quotes/<topic>/<locale>.yaml` — a topic-keyed
bank, unrelated to `teacher_banks/`, built by the just-merged "contract-v1
enrichment" work (PR #5492). Authoring `teacher_banks/<teacher>/approved_atoms/QUOTE/`
content would not be consumed by any current runtime path, so it was
deliberately not touched here (would violate the "provably consumable by the
live path" requirement). Flagging as a real architecture-doc/code drift for
Pearl_Architect: either wire QUOTE into `_TEACHER_TYPE_MAP` or retire the
teacher-bank QUOTE routing claim in the SSOT.

## Proof of consumability (representative)

Ran the live `PoolIndex.get_pool` resolver (the exact class/method
`phoenix_v4/planning/assembly_compiler.py` instantiates for Teacher-Mode
books) directly against the new files:

```
teacher_root = Path('SOURCE_OF_TRUTH/teacher_banks/kenjin/approved_atoms')
pi = PoolIndex(teacher_atoms_root=teacher_root)
pool = pi.get_pool('PERMISSION', 'gen_z_professionals', 'anxiety', required_count=3)
# -> 3 entries: kenjin_PERMISSION_000/001/002, atom_source=teacher_native
```

PASS — all 3 atoms parse, resolve `atom_id`, and load via the real
production code path with no mock/stub involved.

## Scope discipline

- No persona-keyed `atoms/<persona>/**` files touched.
- No edits to `artifacts/qa/pearl_prime_atom_100pct_gap_matrix_20260606.tsv`
  or `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` (out of scope per
  envelope).
- No hot coordination docs (`docs/PROGRAM_STATE.md`,
  `docs/PEARL_ARCHITECT_STATE.md`) touched.
- Prior stale branch commit (`22076dbe5f`, already merged as PR #5492 to
  main under a different subsystem) was abandoned; this work was authored on
  a fresh branch cut from `origin/main`.

## Signals

- `anxiety-p0-overlay-slice-teachers=kenjin`
- `anxiety-p0-overlay-slice-types=PERMISSION`
- `anxiety-p0-overlay-slice-proof=pass`
