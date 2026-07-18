# Atom Cohesion — Chunk: Thesis de-templating (engine-keyed → topic-keyed)

**Status:** GATED, post-flip. Fire when the first R2 EPUB batch ships (skeleton freeze lifted).
**Lane:** Atom Cohesion (chunked plan A–F). Sequenced BEFORE the adjacency selector chunk.
**Authored:** 2026-06-30. Persisted from session for durability; scheduled via Jul 1 runbook backlog.

---

```
ROLE: Pearl_Editor + Pearl_Writer (thesis authoring = Claude Tier-1, free) + light Pearl_Dev (wiring).
/Users/ahjan/phoenix_omega. GPU-free, NO paid LLM. STAGE a PR (≤180 files). Atom Cohesion lane, next chunk.

=== GATE (STOP if unmet) ===
- DO NOT FIRE until the flip→assemble pilot has shipped the first R2 EPUB batch (Q-DRIFT-01 freeze lifted).
  Confirm config/governance/skeleton_freeze.yaml active:false OR operator says go.

=== PROBLEM (confirmed) ===
config/planning/chapter_thesis_bank.yaml is keyed intent → engine_type → thesis (20 intents × 4 engines:
watcher/false_alarm/shame/grief). So the SAME thesis sentence is reused across every (persona×topic) cell on
that engine — the QA sweep measured this across 128 cells. Books read templated because the load-bearing thesis
sentences don't vary by topic. ALSO: Spiral/Overwhelm/Comparison theses are still TBD (header note) = coverage gap.

=== READ FIRST ===
- artifacts/atom_cohesion/{SCHEMA.md, SELECTOR_DIAGNOSIS.md, PARTITION_NOTE.md, WORKED_MAP_gen_z_professionals_anxiety.md}
  (chunks A+E — build on these, do NOT reinvent the schema).
- docs/CHAPTER_THESIS_BANK.md + config/planning/chapter_thesis_bank.yaml (the canonical bank — EDIT in place).
- config/rendering/mechanism_thesis_families.yaml ; phoenix_v4/rendering/golden_chapter_synthesis.py +
  phoenix_v4/planning/enrichment_select.py (how thesis is read).
- artifacts/qa/plan_scale_qa_sweep_20260630/ (the repetition census — your before/after oracle).
- Project memory [Atom cohesion chunked plan], [Integration-pacing priority], [Naming engine] (theses are
  authored content, not generated — Tier-1 authoring is correct).

=== MISSION ===
Add a TOPIC dimension to the thesis bank so the thesis varies by (intent × engine × topic), not just engine —
killing the cross-cell reuse — and fill the missing engine coverage. Theses are authored (Pearl_Writer Tier-1),
edit-in-place, no new file.

=== DELIVERABLES ===
1. Re-key chapter_thesis_bank.yaml to intent → engine → topic → thesis, with a topic-agnostic ENGINE BASELINE
   retained as fallback (so cells without a topic override still resolve — no regressions). Author topic-specific
   theses for the highest-volume topics first (anxiety, burnout, boundaries, overthinking, self_worth, grief…).
2. Fill the coverage gap: author Spiral / Overwhelm / Comparison engine theses (currently TBD).
3. Expand pool depth so a 12-chapter book never repeats a thesis (the ~12-entry pool under-covers 12 intents
   across variants — ensure ≥1 distinct thesis per chapter slot per cell).
4. Light wiring: make the thesis reader (golden_chapter_synthesis / enrichment_select) resolve topic→engine
   baseline. MINIMIZE edits to enrichment_select.py (see deconfliction) — prefer the resolution live in the
   thesis-bank loader / golden_chapter_synthesis.
5. Validate: rebuild ≥3 cells that share an engine but differ in topic (e.g. *_watcher across anxiety vs
   burnout vs grief); prove the theses now DIFFER, register still PASS, repetition census drops vs the
   20260630 baseline.

=== DECONFLICTION ===
- enrichment_select.py is the OPD-20260629-002 composer lane's live file (#3110/#3123). If it's still open and
  touching that file, SERIALIZE — do your wiring in the thesis-bank loader / golden_chapter_synthesis instead,
  or wait for that PR to land. Never edit enrichment_select.py in parallel with the composer lane.
- Sibling-PR search: `gh pr list --search "thesis bank OR atom cohesion OR de-templat" --state all`.

=== DO NOT ===
- Do NOT greenfield a new thesis file (edit the canonical bank). Do NOT use a paid/GPU LLM (Tier-1 authoring).
- Do NOT drop the engine baseline (it's the fallback). Do NOT edit register_gate.py (composer lane resource).
- Do NOT git add -A; surgical staging.

=== DISCOVERY REPORT (before authoring) ===
The re-key schema (confirm against atom_cohesion/SCHEMA.md); topic priority list; coverage gaps you'll fill;
the wiring point (and confirm it avoids enrichment_select.py collision); your before/after repetition metric.

=== GOLDEN BRANCH + PR ===
Branch agent/thesis-de-templating-<date> off origin/main. push-guard + preflight + check_rap_compliance.

=== CLOSEOUT_RECEIPT ===
STATUS · full SHA · PR# · re-key done (intent×engine×topic + baseline kept) · topics authored + engines
filled (spiral/overwhelm/comparison) · pool depth proof (no repeat in 12-ch) · ≥3-cell same-engine-diff-topic
proof (theses differ + register PASS) · repetition census before→after · enrichment_select.py untouched/serialized
· DECISIONS + alt · NEXT_ACTION (hand to Prompt 2 adjacency selector).
```
