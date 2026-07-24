# EXECUTE — Lane 07 — Genre checklists: machine-readable + wired into gates

**AGENT:** Pearl_Dev + Pearl_Editor · **SUBSYSTEM:** manga_pipeline · **WAVE:** 2

## GATE CHECK
Proceed when BOTH `manga-mc-endurance-research-merged=<sha>` AND
`manga-craft-bibles-complete=<sha>` exist (durable surface). Partial start allowed against the
26 already-full bibles if the dispatcher flags Lane 05 as slow — but the final PR must cover all
bibles current at merge time.

## EXECUTION CONTRACT (binding, in-band)
- EXECUTE end-to-end; terminal = signal token or ONE BLOCKER (evidence + pushed work +
  NEXT_ACTION). STARTUP_RECEIPT / CLOSEOUT_RECEIPT bracket the work.
- Re-verify premises live; DISCOVERY REPORT before writes; sibling-PR search "checklist".
- Reuse-first: the enforcement surface ALREADY EXISTS — `config/manga/story_excellence_gates.yaml`
  + `phoenix_v4/manga/story_quality/excellence_gate.py` (threshold 85, per-genre
  genre_core_evidence). You are DEEPENING that system, not building a second checker. A parallel
  checklist engine is a reject-at-review offense (agent_brief §18 "beside" rule).
- Substrate: plumbing for configs; sparse-cone worktree allowed for code+tests (≥20 GB free,
  poison protocol: reset index to origin/main first, explicit adds, staged-diff gate).
- **Hot-file order:** LAST in the `manga_craft/index.md` chain (05 → 04 → 07).
- Landing: MERGED (checks read + named) or BLOCKED. Cleanup ledger + handoff
  `artifacts/coordination/handoffs/manga_process_uplift_lane07_2026-07-24.md`.
- PROVENANCE: research=craft bibles + `manga_mc_endurance_study` + `manga_arc_cadence_study`;
  documents=`MANGA_STORY_EXCELLENCE_REALIZATION_GATE_SPEC.md`; builds_on=`story_excellence_gates`,
  `excellence_gate.py`, `mc_endurance_checklists.yaml`; inventory=EXTENDS.

## READ FIRST
`docs/specs/MANGA_STORY_EXCELLENCE_REALIZATION_GATE_SPEC.md`,
`config/manga/story_excellence_gates.yaml` (current axes + per-genre evidence classes),
`phoenix_v4/manga/story_quality/excellence_gate.py` (GATE_* constants),
`config/manga/mc_endurance_checklists.yaml` (Lane 04 output — schema header),
`docs/research/manga_craft/index.md` + 3 representative bibles,
`config/manga/gate_registry.yaml`, `scripts/manga/validate_story_excellence.py`.

## MISSION
Turn the craft bibles' prose wisdom into **checklists that are consumed at authoring time and
enforced at gate time** — the operator's core complaint is that research existed but writing
didn't check against it.

1. **Per-genre checklist compilation:** `config/manga/genre_craft_checklists.yaml` — one block
   per canonical genre, compiled FROM the bibles (each item carries `source:` bible §-anchor):
   `story_elements_must[]` / `story_elements_should[]` (bible §1/§3/§6 distilled to testable
   one-liners), `mc_items[]` (imported by key from `mc_endurance_checklists.yaml` — reference,
   don't duplicate), `dialogue_rules[]` (§4), `panel_grammar_items[]` (§2/§8 — for the
   storyboarder), `failure_modes[]` (§6 anti-patterns). NEW-ARTIFACT-JUSTIFIED (no machine
   checklist file exists); registry row in same PR; clears `check_manga_wiring.py` by having a
   real consumer (below) in the same PR.
2. **Wire into the excellence gate:** extend `story_excellence_gates.yaml` per-genre blocks to
   reference checklist keys (evidence classes for must-items; anti-pattern lint from
   failure_modes) and extend `excellence_gate.py` minimally to load + score them (additive axes
   or evidence enrichment — do NOT lower threshold 85, do NOT remove existing axes). Also flip
   `mc_endurance_checklists.yaml` from `status: unwired` to wired (consumer = gate).
3. **Storyboarder lint hook:** extend `scripts/ci/check_manga_arc_storyboard.py` (landed by Lane
   01 — verify) to check `panel_grammar_items` conformance signals present in storyboard YAML
   (advisory sub-check).
4. **Editor QA pass definition:** add §"Editor pass" to the excellence-gate spec: the QA flow is
   (a) automated gate ≥85, then (b) Pearl_Editor structured read using the SAME checklist file
   (per-item verdict lines in a review artifact, schema'd in the spec) — so human QA and machine
   gate share one checklist source. This section is what Lane 08's manga-editor skill binds to.
5. **Tests, mutation-proofed:** fixture scripts that PASS; mutated fixtures (missing must-item
   evidence, present anti-pattern) that FAIL. A gate that stays green under mutation is not
   accepted (agent_brief §14). Run the full existing manga test set for regressions
   (`pytest tests/manga -x` — first-failure cascade context applies; name pre-existing reds).

## SMOKE → PILOT → SCALE
Smoke: 1 genre (supernatural_mystery) checklist + gate wiring + tests green. Pilot: +4 genres.
Scale: all. Commit per stage.

## WRITE SCOPE
`config/manga/genre_craft_checklists.yaml`, `config/manga/story_excellence_gates.yaml`,
`phoenix_v4/manga/story_quality/excellence_gate.py`, `scripts/ci/check_manga_arc_storyboard.py`
(advisory sub-check), `docs/specs/MANGA_STORY_EXCELLENCE_REALIZATION_GATE_SPEC.md` (§Editor pass),
`config/manga/mc_endurance_checklists.yaml` (status flip only), tests, `manga_craft/index.md`
(serialized, if a row is needed), handoff. **OUT OF SCOPE:** bible content, thresholds downward,
gate_registry gate REMOVALS, skills (Lane 08).

## DO NOT
- Never weaken a gate to make a fixture pass; precision-fix only with regression proof (§15).
- Don't duplicate MC items into the new yaml — reference by key.
- Don't build a standalone checker script competing with `validate_story_excellence.py`.

## SIGNAL
`manga-genre-checklists-wired=<full merge SHA>`
