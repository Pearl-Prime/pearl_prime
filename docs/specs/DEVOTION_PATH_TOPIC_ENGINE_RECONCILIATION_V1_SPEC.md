# DEVOTION_PATH_TOPIC_ENGINE_RECONCILIATION_V1_SPEC

**Status:** DRAFT — architecture decision recommended; **option choice GATED on operator** (size↔speed trade)
**Owner:** Pearl_Architect
**Date:** 2026-06-15
**Project:** PRJ-WORLDWIDE-CATALOG-GO-LIVE-V1
**Subsystems:** catalog_planning, core_pipeline
**Supersedes / amends:** none (new). **Subordinate to:** `specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md` (sole architecture authority).
**Cap entry:** `DEVOTION-PATH-TOPIC-ENGINE-RECONCILE-01` in `docs/PEARL_ARCHITECT_STATE.md`.

---

## 0. TL;DR

The devotion_path (Open Vessel Press / Sai Maa) en_US catalog of **99 book plans** is unbuildable
because its third plan axis is the **anxiety-family engine triad `{false_alarm, overwhelm, spiral}`
cross-applied to three non-anxiety topics** `{burnout, courage, imposter_syndrome}`. This violates
the canonical rule **"Each topic has one engine"** (`PHOENIX_ARC_FIRST_CANONICAL_SPEC.md §4`),
enforced by the hard gate `config/topic_engine_bindings.yaml`. Result: 63/99 plans have no arc, and
even the buildable ones render topic-incoherent prose.

**The catalog is not short of content — it is mis-pointed.** The repo already holds **85
topic-native, engine-legal, arc-backed, atom-backed cells** across these 3 topics; the catalog
just points 68 of its 99 plans at forbidden engines instead. The fix is primarily a
**catalog re-point**, not an authoring marathon.

**Recommendation: Option A′ (re-point to topic-native engines).** Smallest content lift, restores
engine-purity canon, and *grows* the legal catalog from 31 → up to 85. Two sub-variants (A′-ship-now
vs A′-full-85) trade catalog size for ship speed — **that pick is the operator's** (§7).

---

## 1. The defect (verified)

### 1.1 What the catalog encodes

Each plan id is `devotion_path__sai_ma__<persona>__<topic>__<engine>`. Example
`config/source_of_truth/book_plans_en_us/devotion_path__sai_ma__corporate_managers__courage__false_alarm.yaml`:

```yaml
engine: false_alarm
title: "Body Sounding Alarms: A Courage Book"
subtitle: "...When your nervous system scans for danger that isn't there"
long_description: "...you'll work with the body's false-alarm system and why it keeps firing..."
```

The plan is anxiety prose with a "courage" label. The `series_plan`
(`series_plans_en_us/devotion_path__sai_ma__corporate_managers__courage.yaml`) hard-wires all three
installments of every courage series to `{false_alarm, overwhelm, spiral}` — the anxiety triad —
with `master_arc:` pointers most of which do not exist on disk.

### 1.2 The canonical rule it violates

`PHOENIX_ARC_FIRST_CANONICAL_SPEC.md §4 (ENGINE OVERLAY)`:

> Each topic has one engine. Engine defines allowed resolution_types, open-loop permissions,
> identity-shift permissions, tone constraints. If Arc resolution_type violates Engine → compile fails.

The hard-gate implementation `config/topic_engine_bindings.yaml` declares, per topic, an
`allowed_engines` set and an explicit `forbidden_engines` set:

| Topic | `allowed_engines` | `forbidden_engines` (catalog uses these ✗) |
|---|---|---|
| `burnout` | `overwhelm`, `watcher`, `grief` | **`false_alarm`✗, `spiral`✗**, shame, comparison |
| `courage` | `false_alarm`, `shame`, `spiral` | **`overwhelm`✗**, watcher, comparison, grief |
| `imposter_syndrome` | `shame`, `comparison` | **`false_alarm`✗, `overwhelm`✗, `spiral`✗**, watcher, grief |

The catalog's triad `{false_alarm, overwhelm, spiral}` therefore lands on **forbidden** engines for
most (topic × engine) combinations — most severely for `imposter_syndrome`, where **all three**
catalog engines are forbidden (→ zero imposter books are engine-legal as catalogued).

### 1.3 Two orthogonal failures (do not conflate)

| # | Failure | Owner / lane | Fixed by |
|---|---|---|---|
| **F-ENGINE** | catalog points at forbidden engines; 63 arcs missing | catalog_planning (this spec) | re-pointing plans to topic-native engines (no prose) |
| **F-COHERENCE** | composer pulls atoms by `engine` key, ignoring `topic`, so even an engine-*legal* plan (e.g. `courage__false_alarm`) renders as anxiety prose with the topic string-substituted | composer-frontier lane (#1589 engine · #1590 atoms · #1601 register) | topic-aware atom routing + scaffolding-repetition fix |

The arc YAMLs are correctly tagged (`topic: courage`, `engine: false_alarm`) with valid emotional
curves; the incoherence the stand-down observed is **downstream of the arc**, in atom selection.
**Re-pointing engines (F-ENGINE) is a necessary precondition but does NOT by itself produce coherent
prose** — F-COHERENCE must also land before any production assembly. This spec resolves F-ENGINE and
*gates* the assembly re-dispatch on F-COHERENCE (§8).

A separate, already-tracked blocker (`production` profile emits no manuscript;
"spine-default gate failure" frontier — `READINESS_MANIFEST` B2) is **not** in scope here; it is a
Pearl_Dev release-profile contract decision and is named as a co-gate in §8.

---

## 2. Coverage evidence

Full matrix: `artifacts/analysis/devotion_path_topic_engine_reconciliation_20260615/`
(`catalog_plan_verdicts.tsv`, `topic_engine_coverage_matrix.tsv`, `README.md`).

### 2.1 The 99 catalog plans, by verdict

| Verdict | Count |
|---|---|
| `BUILDABLE_LEGAL` (arc exists + engine allowed) | **31** |
| `BUILDS_BUT_ENGINE_ILLEGAL` (arc exists, engine forbidden — 5× `gen_z_student` F006 seeds) | **5** |
| `MISSING_ARC_ENGINE_LEGAL` (no arc, engine allowed — 2× `gen_z_student` courage) | **2** |
| `MISSING_ARC_ENGINE_ILLEGAL` (no arc, engine forbidden — re-point, do NOT author) | **61** |
| **TOTAL** | **99** |

### 2.2 Topic-native authored capacity (independent of how the catalog points)

| Topic | Allowed engines with arcs + atoms | Native buildable cells |
|---|---|---|
| `burnout` | overwhelm (11/11), watcher (11/11), grief (11/11) | **33** |
| `courage` | false_alarm (10/11), spiral (10/11), shame (10/11) | **30** |
| `imposter_syndrome` | shame (11/11), comparison (11/11) | **22** |
| **TOTAL** | | **85** |

(11 personas; `gen_z_student` courage is 10/11 because its courage arcs are F003 seeds, not F006 —
2 legal cells short, the `MISSING_ARC_ENGINE_LEGAL` rows.)

**Read this carefully:** the binding-legal authored surface (85) is **larger** than the catalog's
buildable surface (31). The problem is not scarcity; it is mis-pointing.

---

## 3. Options

Each option has a different downstream owner and a different size/speed profile. All three keep the
Open Vessel Press imprint, Sai Maa byline, and the composite-brief cover split (style_dp / saima_dp;
imposter_syndrome = PIL type-dominant, burnout/courage = FLUX).

### Option A′ — Re-point to topic-native engines *(recommended; refines the handoff's Option (a))*

Rewrite each series_plan/book_plan engine axis from the anxiety triad to that topic's
`allowed_engines`. No new arcs for 97/99; author only the 2 legal `gen_z_student` courage cells if
that persona is retained.

- **Content lift:** near-zero (catalog YAML edits; 0–2 arcs).
- **Canon:** restores §4 engine-purity; every plan becomes binding-legal.
- **Catalog size:** **grows** 31 → up to **85** legal cells (vs the as-written 99, of which 68 were
  illegal/unbuildable). Shapes:
  - **A′-full-85** — expose all 85 native cells (burnout & imposter pick up their 2nd/3rd legal
    engines). Largest legal catalog, mild title/positioning rework per new engine.
  - **A′-mirror-N** — keep the catalog's *shape* (≈3 engines/topic where legal): burnout→
    {overwhelm, watcher, grief}, courage→{false_alarm, spiral, shame}, imposter→{shame, comparison}
    (only 2 legal engines exist) → **≈ 30 + 30 + 22 = 82** cells, structurally closest to the
    original 99 intent.
- **Owner:** Pearl_PM / catalog_planning (plan re-point) → then composer-frontier (F-COHERENCE) →
  gated Pearl_Prime assembly.

### Option B — Author the 63 missing arcs on the *current* anxiety engines *(rejected)*

Preserve the literal 99 by authoring 63 arcs on `{false_alarm, overwhelm, spiral}`.

- **Blocking objection:** **61 of the 63** are on engines the topic explicitly **forbids**. Authoring
  them manufactures engine-illegal arcs and *entrenches* the canon violation that caused the
  stand-down. This is not a cost trade — it is architecturally illegal under §4. **Rejected.**
  (Only the 2 legal `gen_z_student` courage arcs from this set are worth authoring, and Option A′
  already covers them.)

### Option C — Ship the buildable 31 now, author the rest in waves *(fast-first-ship; viable as an A′ schedule, not a rival design)*

Ship the 31 `BUILDABLE_LEGAL` plans as a launch subset immediately; backfill later.

- **Caveat:** all 31 are already on legal engines, so C is really *"A′ restricted to the 31 plans the
  catalog happens to already point correctly"* — it does **not** require Option B's illegal arcs.
- **Use:** the fastest first-ship **schedule of A′**, not a different architecture. Folded into A′ as
  the **wave-1 = 31** ship slice (§7).

---

## 4. Decision (recommended)

**Adopt Option A′: re-point the devotion_path catalog's engine axis to each topic's
`allowed_engines` per `config/topic_engine_bindings.yaml`. Reject Option B (illegal). Treat Option C
as the A′ wave-1 ship slice.**

Rationale:
1. **Canon-restoring** — the only option that satisfies `PHOENIX_ARC_FIRST_CANONICAL_SPEC.md §4`.
2. **Smallest lift** — 0–2 arcs authored vs Option B's 61 (illegal) arcs.
3. **Grows the catalog** — 31 → up to 85 legal cells; the operator's ship goal is *better* served,
   not merely unblocked.
4. **Separates concerns** — fixes F-ENGINE cleanly and gates assembly on F-COHERENCE rather than
   masking the composer defect behind more catalog churn.

**Not decided here (operator-gated, §7):** *which A′ shape* — the size↔speed pick (full-85 vs
mirror-82 vs wave-1=31-then-backfill). That trade is the operator's call; this spec halts on it.

---

## 5. Engine re-point map (normative, for the catalog_planning ws)

When A′ executes, the series_plan/book_plan engine axis MUST be drawn from:

```
burnout            → overwhelm, watcher, grief          # drop false_alarm, spiral
courage            → false_alarm, spiral, shame          # drop overwhelm
imposter_syndrome  → shame, comparison                   # drop all of false_alarm/overwhelm/spiral
```

Rules:
1. Engine axis values MUST be a subset of the topic's `allowed_engines`. A re-pointed plan whose
   engine is in `forbidden_engines` is a hard error.
2. Re-pointing changes the canonical `book_id` (`...__<topic>__<engine>`). Treat as **new plan ids**;
   retire the illegal ids (do not silently rename in place — preserve provenance per the
   anti-drift registry).
3. Plan metadata (title, subtitle, description, keywords) MUST be regenerated from the *new* engine's
   framing — the existing anxiety-framed copy (e.g. "body's false-alarm system") is part of the
   defect and MUST NOT carry over verbatim. Engine→angle copy source:
   `config/catalog_planning/engine_title_angles.yaml`.
4. The 5 `BUILDS_BUT_ENGINE_ILLEGAL` `gen_z_student` F006 seed arcs on forbidden engines are
   **excluded**; if `gen_z_student` is retained, use its legal-engine cells instead.
5. F006 structural format and `duration: standard_book_60min` are preserved (not in scope to change).

---

## 6. What re-pointing does NOT fix (gate, do not skip)

Re-pointing yields engine-legal, arc-backed plans — but **prose coherence is a separate gate**:

- **F-COHERENCE (composer-frontier #1589/#1590/#1601):** the composer must route atoms by
  `(topic, engine)`, not `engine` alone, and the scaffolding-repetition / register defects must be
  fixed, before any production assembly. A re-validated proof slice MUST pass coherence + quality
  gates first.
- **B2 release-profile contract (Pearl_Dev):** `--quality-profile production` currently emits no
  `book.txt` (gates hard-fail). The production-vs-draft emission contract must be decided before a
  *production/release* assembly run (a draft-profile proof slice is fine for coherence validation).

Both are co-gates on §8's assembly re-dispatch.

---

## 7. OPERATOR DECISION REQUIRED — A′ shape (size ↔ speed)

> **STOP / operator-gated.** Option A′ is the architecture call (canon-mandated). But *which A′
> shape* trades catalog size for first-ship speed, which is the operator's decision, not the
> architect's. Pick one:

| Shape | Wave-1 ship | Backfill | Catalog ceiling | Trade |
|---|---|---|---|---|
| **A′-wave1-31** (≡ Option C schedule) | the 31 already-legal plans, immediately after F-COHERENCE | re-point the other ~51–54 cells in later waves | up to 85 | **fastest first ship**, smaller day-1 catalog |
| **A′-mirror-82** | re-point all to ~3 legal engines/topic (82), ship after F-COHERENCE | none | 82 | closest to original 99 shape; one re-point pass |
| **A′-full-85** | re-point to all native engines (85), ship after F-COHERENCE | none | 85 | largest legal catalog; most title/positioning rework |

**Pearl_Architect recommendation:** **A′-wave1-31 → backfill toward A′-full-85.** Ship the 31
already-correct plans as the launch subset (fastest path to the operator's first Open Vessel Press
ebooks), then re-point the remaining cells in waves toward the full 85. This sequences first-revenue
ahead of completeness without ever shipping an engine-illegal book.

Routing if the operator wants the size/speed call brokered rather than made directly:
`Pearl_Operator_Proxy` per `docs/PEARL_OPERATOR_PROXY_SPEC.md`, logged to
`artifacts/coordination/operator_decisions_log.tsv`.

---

## 8. Follow-on workstreams (precise)

| # | Workstream | Owner | Trigger / gate | Scope |
|---|---|---|---|---|
| W1 | `ws_devotion_path_engine_repoint_20260615` | Pearl_PM / Pearl_Editor (catalog_planning) | this cap entry merged **+ operator A′-shape pick (§7)** | re-point series_plan + book_plan engine axis per §5 map; regenerate plan metadata from `engine_title_angles.yaml`; retire illegal book_ids; author only the ≤2 legal `gen_z_student` courage arcs if that persona is kept |
| W2 | composer-frontier (existing) #1589 engine · #1590 atoms · #1601 register | Pearl_Dev / Pearl_Editor | independent; **co-gates W4** | topic-aware atom routing `(topic, engine)`; scaffolding-repetition + register fixes; this is **F-COHERENCE** |
| W3 | release-profile emission contract (B2) | Pearl_Dev | independent; **co-gates W4** for a *production/release* run | decide `--quality-profile production` emission vs draft; "spine-default gate failure" frontier |
| W4 | **gated Pearl_Prime assembly re-dispatch** | Pearl_Prime | **W1 done AND W2 (F-COHERENCE) landed AND a re-validated proof slice passes coherence + gates** (W3 if production-profile) | assemble the chosen A′ slice using the **CORRECTED COMPOSITE brief**: composite mode, Open Vessel Press imprint, Sai Maa byline, style_dp/saima_dp covers (imposter=PIL type-dominant, burnout/courage=FLUX), `--pipeline-mode spine`, draft-or-production per W3 |

**Arc authoring note:** unlike the stand-down's worst case, A′ requires **0–2** authored arcs, not 63.
If the operator instead directs preserving specific illegal combos (not recommended), that would
reopen the §4 canon question and require a new operator AMENDMENT — it is explicitly out of this
spec's envelope.

---

## 9. Anti-drift checks

- Does **not** author atoms/arcs, does **not** run the assembly, does **not** touch composer/register/F1
  lanes (decision + spec only).
- Does **not** edit `config/topic_engine_bindings.yaml` or the canonical spec — it *applies* them.
- Does **not** rename book_ids in place (provenance preserved; W1 retires-and-recreates).
- Subordinate to `PHOENIX_ARC_FIRST_CANONICAL_SPEC.md`; if any clause here conflicts, the canonical
  spec wins.
- The size↔speed pick is left to the operator (§7); the architect does **not** silently choose
  catalog size.

## 10. Authority

This spec + cap `DEVOTION-PATH-TOPIC-ENGINE-RECONCILE-01` (`docs/PEARL_ARCHITECT_STATE.md`) +
`specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md §4` + `config/topic_engine_bindings.yaml` +
`artifacts/analysis/devotion_path_topic_engine_reconciliation_20260615/` +
`artifacts/release/2026-W25/devotion_path/HANDOFF_devotion_path_catalog_readiness_20260615.md`.
