# scene_anchor_density ch12 cluster — template-source diagnosis (2026-05-18)

**Owner:** Pearl_Editor
**Project:** proj_pearl_prime_bestseller_rebase_20260425
**Workstream:** ws_teacher_wrapper_intro_variants_diversification_20260518
**Routing OPD:** OPD-20260518-003
**Authority:** docs/PEARL_ARCHITECT_STATE.md TEACHER-MODE-WRAPPER-SEMANTICS-01; PEARL-EDITOR-UPSTREAM-01; PR #1180 (e3a388262) diversification pattern

## TL;DR

scene_anchor_density gate FAIL in `extended_book_2h × ahjan × gen_z_professionals × anxiety × en-US × seed 1` (Round 2, 20260518T043122Z) — single offender `"in ahjan's framework the path begins with"` × 3 paragraphs in chapter 12. The stuck phrase is NOT in ahjan teacher_bank atom bodies. It is a **wrapper template variant** at `config/catalog_planning/teacher_wrapper_templates.yaml:15` (`named.intro_wrapper.variants[0]`) rendered with `{TEACHER_NAME}` substituted to `ahjan`.

## Evidence chain

- Run dir: `artifacts/pearl_prime/extended_book_2h/ahjan_gen_z_professionals_anxiety_en_US_20260518T043122Z/`
- `scene_anchor_density_report.json`:
  ```json
  {"status": "FAIL", "violations": [{"chapter": 12, "cap": 2,
   "offenders": [{"phrase": "in ahjan's framework the path begins with",
                  "paragraph_count": 3}]}]}
  ```
- `grep -rin "in ahjan's framework"` across `SOURCE_OF_TRUTH/teacher_banks/ahjan/`, `atoms/`, `config/content_banks/` → **zero atom matches**
- `grep -rn "framework the path begins"` across `phoenix_v4/`, `scripts/`, `config/` → **single hit** at `config/catalog_planning/teacher_wrapper_templates.yaml:15`

## Why ch12 specifically

F006 (Nervous System Ladder) ch12 has intent `embodied_identity` / role `integration`. The template at `slot_template: [HOOK, SCENE, STORY, REFLECTION, COMPRESSION, EXERCISE, INTEGRATION]` puts ~4 substance slots in scope for `named.intro_wrapper` (HOOK, SCENE, STORY, COMPRESSION — voice-owned slots REFLECTION/INTEGRATION/EXERCISE skip the named-mode intro per TEACHER-MODE-WRAPPER-SEMANTICS-01 wrapper-line-budget rule). With only 4 candidate strings in the `named.intro_wrapper` pool (1 pattern + 3 variants) and a deterministic selector against `seed=1`, the picker lands on the same variant 3× in a single chapter — exceeding the scene_anchor_density cap of 2.

## Doctrinal concern (independent of repetition)

The variant `"In {TEACHER_NAME}'s framework, the path begins with..."` carries Theravada-flavored register ("path", "begins") that **contradicts ahjan's doctrine**: per `SOURCE_OF_TRUTH/teacher_banks/ahjan/doctrine/doctrine.yaml`, ahjan = Tantric Buddhism + mysticism synthesis; `prohibited_outcomes` explicitly includes `"Theravada Buddhist framing"`. The variant is also a weak fit for non-Buddhist teachers in the roster (pamela_fellows = somatic therapist; sai_ma = bhakti; junko = Zen) — they get the same "path begins with" frame regardless of lineage.

## Fix shape (this PR)

**Additive — never delete.** Append 7 sibling variants to `named.intro_wrapper.variants` that:
1. Are **tradition-neutral** (work for ahjan Tantric, miki/junko Zen, joshin Theravada, pamela_fellows somatic, sai_ma bhakti, master_wu Taoist, etc. — register chosen so no variant is doctrinally hostile to any teacher in the roster).
2. Are **register-distinct** (poetic / direct / gestural / contrastive / synthetic — high diversity to dilute selector collision).
3. Use the existing `{TEACHER_NAME}`, `{TRADITION_SHORT}`, `{TEACHING_LINEAGE}` slot placeholders only — no new slot variables.
4. Preserve the wrapper-line-budget rule (single-line, framing-only — never carry mechanism vocabulary).

Pool grows 4 → 11. Selector collision probability against any single string within a 4-substance-slot chapter at seed 1 drops from ~30% (4 picks from 4 candidates, expected collision) to ~9% (4 picks from 11). Empirical verification via Round-3 re-run is the gate.

## Out of scope (for this PR)

- Selector enforcement code (handled by `ws_flow_glue_selector_cap_enforcement_20260517`).
- `phoenix_v4/planning/enrichment_select.py:982-1080` per-slot precedence implementation (handled by `ws_teacher_wrapper_semantics_impl_20260517`).
- Broader ahjan teacher_bank re-author (handled by `ws_ahjan_teacher_bank_framing_reauthor_20260517`, gated on `ws_teacher_wrapper_semantics_impl_20260517`).
- Removal of the existing "path begins with" variant — additive only; if the doctrinal concern needs resolution it warrants a separate ws with operator review of every teacher's compatibility.
- Generalized-mode or composite-mode wrapper diversification — not flagged by this run.

## Verification plan

1. Edit `config/catalog_planning/teacher_wrapper_templates.yaml` — add 7 variants to `named.intro_wrapper.variants`.
2. Re-run canonical CLI (Round 3): `--seed 1` (same seed as failing run for deterministic comparison).
3. Read `scene_anchor_density_report.json`:
   - PASS (`violations: []`) → fix lands; downstream gates triage next.
   - FAIL on same phrase → selector deterministically picks index-0 regardless of pool size; this is a Pearl_Dev selector bug, escalate.
   - FAIL on new phrase → pool size still insufficient OR new cluster surfaced; surface as new ws (do not whack-a-mole per prompt's hard-stop rule).

## Open follow-up (if scene_anchor PASSES under Round 3)

The exit code 0 on Round-2 despite scene_anchor FAIL suggests the gate is currently *advisory* (logs FAIL, doesn't halt). Pipeline produced reports + variants JSON but no book.txt or plan.json — gate prevented book assembly. This is consistent with HARDENING_SPEC §3 "fail-early gate behavior is the desired end state". Surfacing for confirmation; no fix required unless the desired end state is hard-exit-1 on gate FAIL.
