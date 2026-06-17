# EN_US_CATALOG_ENGINE_REPOINT_V1_SPEC

**Status:** ADOPTED — A′-full (topic-native engines, arc-backed only). Mirrors the
devotion_path reconciliation; same method, all 8 en_US brands.
**Owner:** Pearl_Architect / Pearl_Prime
**Date:** 2026-06-17
**Project:** PRJ-WORLDWIDE-CATALOG-GO-LIVE-V1
**Subsystems:** catalog_planning, core_pipeline
**Supersedes / amends:** none (new). **Subordinate to:** `specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md` (sole architecture authority).
**Template / prior art:** `docs/specs/DEVOTION_PATH_TOPIC_ENGINE_RECONCILIATION_V1_SPEC.md` (devotion_path; this spec extends its method to the other 7 brands).

---

## 0. TL;DR

The anxiety-family engine triad `{false_alarm, overwhelm, spiral}` was cross-applied to
**every en_US brand's** topics — not just devotion_path. Across the **8 en_US brands** the
catalog encodes its third plan axis as that triad regardless of the topic's canonical engine,
violating **"Each topic has one engine"** (`PHOENIX_ARC_FIRST_CANONICAL_SPEC.md §4`), enforced
by the hard gate `config/topic_engine_bindings.yaml`.

`devotion_path` is already re-pointed (PR #1682). This spec extends the **identical fix** to the
**other 7 en_US brands** so the full en_US catalog becomes 100% engine-legal and planned, the new
way:

| Brand | Teacher | Plans | Topics |
|---|---|---|---|
| `stillness_press` | ahjan | 187 | anxiety, sleep_anxiety, somatic_healing |
| `somatic_wisdom` | pamela_fellows | 143 | compassion_fatigue, self_worth, somatic_healing |
| `digital_ground` | miki | 132 | financial_anxiety, financial_stress, imposter_syndrome, social_anxiety |
| `cognitive_clarity` | kenjin | 132 | boundaries, burnout, imposter_syndrome, overthinking |
| `sleep_restoration` | master_sha | 110 | sleep_anxiety, somatic_healing |
| `solar_return` | ra | 99 | courage, depression, financial_anxiety |
| `heart_balance` | maat | 99 | boundaries, compassion_fatigue, self_worth |

**The catalog is not short of content — it is mis-pointed.** Re-pointing each plan's engine axis
to its topic's `allowed_engines` (arc-backed only) is a **catalog re-point, not an authoring
marathon** — 0 new arcs, 0 hand-written prose, 0 renders. This spec resolves **F-ENGINE** and
*gates* production assembly on **F-COHERENCE** (§6/§8), exactly as the devotion spec does.

---

## 1. The defect (verified)

Each plan id is `<brand>__<teacher>__<persona>__<topic>__<engine>`. The `<engine>` axis is drawn
from the anxiety triad `{false_alarm, overwhelm, spiral}` for every topic, so most (topic × engine)
cells land on engines the topic explicitly **forbids**. Example
`somatic_wisdom__pamela_fellows__corporate_managers__self_worth__false_alarm.yaml`:
`self_worth` allows only `{shame, comparison}` → `false_alarm` is forbidden. The plan is anxiety
prose with a `self_worth` label.

### 1.1 The canonical rule it violates

`PHOENIX_ARC_FIRST_CANONICAL_SPEC.md §4 (ENGINE OVERLAY)`: *"Each topic has one engine. … If Arc
resolution_type violates Engine → compile fails."* The hard-gate `config/topic_engine_bindings.yaml`
declares, per topic, an `allowed_engines` set and an explicit `forbidden_engines` set. The triad
lands on forbidden engines for most topics.

### 1.2 Two orthogonal failures (do not conflate)

| # | Failure | Owner / lane | Fixed by |
|---|---|---|---|
| **F-ENGINE** | catalog points at forbidden engines | catalog_planning (this spec) | re-pointing plans to topic-native engines (no prose) |
| **F-COHERENCE** | composer pulls atoms by `engine` key, ignoring `topic`, so even an engine-*legal* plan renders as anxiety prose with the topic string-substituted | composer-frontier lane (#1589 engine · #1590 atoms · #1601 register) | topic-aware atom routing + scaffolding-repetition fix |

Re-pointing engines (F-ENGINE) is a **necessary precondition** but does NOT by itself produce
coherent prose — F-COHERENCE must also land before any production assembly (§6, §8).

---

## 2. Coverage evidence (verified at origin/main 29c3fd76bc)

Full matrix: `artifacts/analysis/en_us_catalog_engine_repoint_20260617/`
(`<brand>_verdicts.tsv` per brand, `CATALOG_SCORECARD.md`). Re-derivable from repo state.

### 2.1 The 902 plans (7 brands), by engine-legality

| Brand | Plans | `BUILDABLE_LEGAL` (now) | Engine-illegal | % legal NOW |
|---|---|---|---|---|
| stillness_press | 187 | 130 | 55 | 69.5% |
| somatic_wisdom | 143 | 30 | 110 | 21.0% |
| digital_ground | 132 | 50 | 77 | 37.9% |
| cognitive_clarity | 132 | 43 | 88 | 32.6% |
| sleep_restoration | 110 | 53 | 55 | 48.2% |
| solar_return | 99 | 50 | 44 | 50.5% |
| heart_balance | 99 | 20 | 77 | 20.2% |
| **TOTAL (7)** | **902** | **376** | **506** | **41.7%** |

With devotion_path (85, all legal), the full en_US catalog is **461/987 = 46.7%** engine-legal
before this fix.

### 2.2 Verdict taxonomy (identical to the devotion matrix)

- `BUILDABLE_LEGAL` — arc exists AND engine ∈ `allowed_engines` → ship-eligible (subject to F-COHERENCE).
- `MISSING_ARC_ENGINE_LEGAL` — engine allowed, no arc → arc-blocked; **defer** (do not author arcs here).
- `BUILDS_BUT_ENGINE_ILLEGAL` — arc exists, engine forbidden → **retire**; building it violates §4.
- `MISSING_ARC_ENGINE_ILLEGAL` — no arc AND engine forbidden → **re-point** to a topic-native engine.

**Read this carefully:** as with devotion, the binding-legal *authored* surface (arc-backed
topic-native cells) is **larger** than the catalog's currently-buildable surface. The problem is
mis-pointing, not scarcity.

---

## 3. Decision

**Adopt A′-full per brand: re-point every series_plan/book_plan engine axis to each topic's
`allowed_engines` per `config/topic_engine_bindings.yaml`, restricted to the engines that have an
authored arc for that (persona, topic).** Reject authoring arcs on forbidden engines (illegal under
§4). Defer arc-blocked legal cells (`MISSING_ARC_ENGINE_LEGAL`) as tracked backfill.

Rationale (mirrors devotion §4):
1. **Canon-restoring** — the only option that satisfies §4 engine-purity.
2. **Smallest lift** — 0 arcs authored, 0 prose hand-written, 0 renders.
3. **Grows the legal catalog** — each brand reaches ~100% of its arc-backed legal cells.
4. **Separates concerns** — fixes F-ENGINE; gates assembly on F-COHERENCE rather than masking the
   composer defect behind more catalog churn.

---

## 4. Engine re-point map (normative)

Per topic, the series_plan/book_plan engine axis MUST be drawn from `allowed_engines`
(`config/topic_engine_bindings.yaml`), restricted to arc-backed engines. Installment order =
engine order below.

```
anxiety            → false_alarm, spiral, watcher        # full-7 topic; pick the 3 with arcs
boundaries         → shame, comparison, false_alarm       # drop overwhelm, spiral
burnout            → overwhelm, watcher, grief            # drop false_alarm, spiral
compassion_fatigue → overwhelm, watcher, grief            # drop false_alarm, spiral
courage            → false_alarm, spiral, shame           # drop overwhelm
depression         → watcher, grief, overwhelm            # drop false_alarm, spiral
financial_anxiety  → overwhelm, spiral, shame             # drop false_alarm
financial_stress   → overwhelm, spiral, shame             # drop false_alarm
imposter_syndrome  → shame, comparison                    # drop false_alarm/overwhelm/spiral
overthinking       → spiral, watcher, false_alarm         # drop overwhelm
self_worth         → shame, comparison                    # drop false_alarm/overwhelm/spiral
sleep_anxiety      → false_alarm, spiral, overwhelm       # already all-legal
social_anxiety     → false_alarm, shame, comparison       # drop overwhelm, spiral
somatic_healing    → watcher, overwhelm                   # drop false_alarm/spiral/shame/comparison/grief
```

Rules (mirror devotion §5):
1. Engine axis values MUST be a subset of the topic's `allowed_engines`. A re-pointed plan whose
   engine is in `forbidden_engines` is a hard error.
2. A re-pointed engine MUST have an authored arc `<persona>__<topic>__<engine>__F006.yaml` for the
   plan's persona. Engines without an arc are **deferred** (`MISSING_ARC_ENGINE_LEGAL`), NOT authored.
3. Re-pointing changes the canonical `book_id` (`...__<topic>__<engine>`). Treat as **new plan ids**;
   **retire** the illegal/re-pointed-away ids via a provenance ledger (`RETIRED_BOOK_IDS.tsv`) — do
   NOT silently rename in place (anti-drift registry).
4. Plan metadata (`title`, `subtitle`) MUST be **regenerated by the canonical naming engine**
   (`phoenix_v4/naming`, `angle_id = engine`, batch-deduped per series) — the existing
   anxiety-framed copy is part of the defect and MUST NOT carry over verbatim. Persona/topic copy
   (description pain phrase, character, bisac, comps, avatar, voice markers, price) is preserved by
   cloning the per-(persona, topic) source plan. Engine-mechanism spans in `long_description` /
   `cover_tagline` / `short_blurb` are reframed from the new engine's
   `config/catalog_planning/engine_title_angles.yaml` framing.
5. `F006` structural format and `duration: standard_book_60min` are preserved (out of scope).

---

## 5. Per-brand naming-config requirement (anti-spam)

Each brand MUST have a **distinct** `brand_template_preferences` entry in
`omega/title_entropy/subtitle_patterns.yaml` so the same topic produces structurally different
titles/subtitles under different brands (`EXPERIENCE_LAYER_ANTI_SPAM_SPEC §16`).

- **No two brands share the same (subtitle_strategy + content_mix) profile.** Do NOT clone
  devotion's mix across brands. Each brand's mix must match its voice register.
- Every persona a brand uses MUST resolve to a real role in
  `omega/title_entropy/persona_title_flavor.yaml` (else `{PersonaDescription}` falls back to
  "Readers"). **On origin/main all 11 en_US personas are already present** (added with the #1677
  naming-engine repair) — verify, add only if a brand introduces a new persona.
- `engine_title_angles.yaml` already covers all 7 target engines; no edits required.

Distinct family-mix assignment for the 7 brands (each tuned to brand voice; persona_direct used
where it fits the brand):

| Brand | Voice register | Title family lean | content_mix bias |
|---|---|---|---|
| stillness_press | calm/contemplative | metaphor/journey | metaphor-heavy (already on main) |
| cognitive_clarity | evidence/method | method/guide | topic_direct-heavy (already on main) |
| somatic_wisdom | soft-clinical josei, body-paced | metaphor + body | metaphor + body topic_direct, low persona |
| digital_ground | grounded, modern, real-talk | scenario + outcome | persona_direct + topic_direct |
| sleep_restoration | nocturnal, gentle, restorative | journey/metaphor | metaphor-heavy, low persona |
| solar_return | mythic/renewal, empowering | journey + outcome | metaphor + persona |
| heart_balance | tender, relational, weighing | journey + persona | persona_direct + metaphor |

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

Both are co-gates on §8's assembly re-dispatch. **This spec does NOT assemble production.**

---

## 7. Validation (per brand, hard gate before PR)

A re-pointed brand passes ONLY if 100% of its written plans satisfy ALL of:

1. **Parse** — every `book_plan` + `series_plan` is valid YAML against schema 1.0.0.
2. **Engine-legal** — `engine ∈ allowed_engines[topic]`; never in `forbidden_engines`.
3. **Engine-matches-filename** — the `engine:` field equals the `__<engine>` filename suffix and
   the series `arc.installment_N.engine`.
4. **Arc-backed** — `master_arc` file exists for `<persona>__<topic>__<engine>__F006`.
5. **Distinct (title, subtitle)** — no two plans within the brand share an identical (title,
   subtitle) pair (batch-dedupe via the naming engine).
6. **0 `"[Topic] Book"` tails / 0 `"Readers"`** in any title/subtitle; persona-named where the
   template names a persona.

Report **planned coverage %** per brand = written legal plans ÷ (legal arc-backed cells the brand's
(persona × topic) grid supports). Deferred = arc-blocked legal cells (`MISSING_ARC_ENGINE_LEGAL`).

---

## 8. Follow-on workstreams

| # | Workstream | Owner | Trigger / gate | Scope |
|---|---|---|---|---|
| W1 | `ws_en_us_catalog_engine_repoint_20260617` (per-brand) | Pearl_Architect / Pearl_PM (catalog_planning) | this spec | re-point series_plan + book_plan engine axis per §4 map; regenerate title/subtitle via naming engine; retire illegal book_ids with provenance ledgers; defer arc-blocked cells; add per-brand naming config (§5) |
| W2 | composer-frontier (existing) #1589 · #1590 · #1601 | Pearl_Dev / Pearl_Editor | independent; **co-gates W4** | topic-aware atom routing `(topic, engine)`; this is **F-COHERENCE** |
| W3 | release-profile emission contract (B2) | Pearl_Dev | independent; **co-gates W4** for a production run | decide `--quality-profile production` emission vs draft |
| W4 | **gated Pearl_Prime assembly re-dispatch** | Pearl_Prime | **W1 done AND W2 (F-COHERENCE) landed AND a re-validated proof slice passes** | assemble the chosen slice; `--pipeline-mode spine`; draft-or-production per W3 |

**Scale / governance:** W1 is large (7 × ~99 plans). It ships as **per-brand do-NOT-merge PRs**
(one per brand) to stay under governance file caps (warns >200, blocks >500) — never one giant PR.

---

## 9. Anti-drift checks

- Does **not** author atoms/arcs, does **not** run the assembly, does **not** touch
  composer/register/F1 lanes (catalog re-point + naming-config only).
- Does **not** edit `config/topic_engine_bindings.yaml` or the canonical spec — it *applies* them.
- Does **not** rename book_ids in place (provenance preserved via retire-and-recreate ledgers).
- Does **not** hand-write titles/subtitles — the canonical naming engine generates them.
- Subordinate to `PHOENIX_ARC_FIRST_CANONICAL_SPEC.md`; if any clause here conflicts, the canonical
  spec wins.

## 10. Authority

This spec + `specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md §4` + `config/topic_engine_bindings.yaml` +
`docs/specs/DEVOTION_PATH_TOPIC_ENGINE_RECONCILIATION_V1_SPEC.md` (template) +
`artifacts/analysis/en_us_catalog_engine_repoint_20260617/` +
`phoenix_v4/naming` (canonical naming engine, #1677) +
`omega/title_entropy/{subtitle_patterns,persona_title_flavor}.yaml`.
