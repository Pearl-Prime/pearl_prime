# Lane 03 — Assembly Variety Repair (break the five-beat monotony)

~~~text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_Social_Media_Writer for Phoenix Omega. Prose authoring is Tier-1 (Claude,
operator-present) per the LLM Tier Policy — you write the variety by hand into config/atoms; you do
NOT add any runtime LLM call to the deterministic assembly path.

Repo: Pearl-Prime/pearl_prime. Substrate: fresh branch off latest origin/main
(agent/social-variety-repair-20260724). Explicit-path staging; poison protocol.

STARTUP_RECEIPT:
- AGENT=Pearl_Social_Media_Writer
- LANE=social_variety_repair_20260724
- EXECUTION_MODE=local_fallback ; BACKGROUND_SAFE=yes
- PERSISTENCE_SURFACES=branch/PR/proof-root
- RESUME_SURFACE=artifacts/coordination/handoffs/social_variety_repair_2026-07-24.md

READ FIRST:
- docs/PEARL_SOCIAL_MEDIA_WRITER_AGENT_SPEC_2026-07-18.md (voice + platform rules — binding)
- docs/social_media_YT4.txt (hook-and-demo format; non-talking formats; text-on-screen),
  docs/social_media_YT5.txt (6–10-word hooks; outlier-derived topics), docs/social_media_YT3.txt
  (carousel cover-hook + slide structure) — tracked post-Lane-01
- phoenix_v4/social/deterministic_social.py (generate_copy_package; the hardcoded rotation
  sentences; carousel builder) ; config/social/words_bank.yaml (hook_families) ;
  config/social/platform_specs.yaml
- scripts/ci/check_social_post_craft.py (Lane 02's gate — your acceptance harness)
- artifacts/qa/social_craft_gate_20260724/ (the failing verdicts on current posts = your worklist)

PRE-REQUISITE CHECK: social-craft-gate-live=<sha> exists (Lane 02 merged). Missing → STOP, BLOCKED.
Rationale: variety without an enforcing gate regresses next quarter (memory-is-recall rule).

LIVE STATE RECONCILIATION: fetch; re-verify the CLAIMS: five-beat skeleton on all pilot posts;
token-swapped CTA (RESET/FACTS/GROUND); literal "Mechanism:" labels + "Free guide in bio"
placeholders in Path-A captions; ~8 hardcoded rotation sentences in deterministic_social.py; APAC
rows with stage-directions in post_text and English bodies.

DISCOVERY REPORT before action: current SHA; exact template inventory (every f-string caption
scaffold + rotation list in generate_copy_package, with counts); hook-grammar census across the
atom bank (how many distinct hook grammars exist TODAY); which atoms vs which scaffolds produce the
monotony (the deficit is SHAPE, not count — measure before authoring).

PROVENANCE:
- research: YT3/YT4/YT5 transcripts (hook variety, format variety) + platform research docs
- documents: PEARL_SOCIAL_MEDIA_WRITER_AGENT_SPEC (Writing Standard); SOCIAL_MEDIA_100PCT plan
- builds_on: generate_copy_package + words_bank.yaml + evergreen_social_atom_bank (EDIT IN PLACE —
  no parallel composer, no new bank file family)
- inventory: EXTENDS (new grammars/variants added; existing atoms untouched except where a scaffold
  label leaked into atom text)

MISSION (narrow): make assembled posts pass Lane 02's gate through REAL variety, not gate erosion:
1. **Hook grammars:** author ≥8 distinct hook grammars per platform family (beyond
  "<persona>: <belief> is not the whole story") into words_bank.yaml / the template layer —
  question hooks, specific-moment hooks, number/count hooks, mistaken-belief hooks, direct-address
  hooks, curiosity-gap hooks, first-person-observed hooks, contrarian (the current one, retained as
  1-of-N). 6–10-word target per YT5; first-125-char discipline per platform rules.
2. **CTA variety:** ≥6 CTA grammars with rotation driven by the existing cooldown selector — kill
  the one-token-swap CTA.
3. **De-scaffold:** remove literal "Mechanism:" / "Try this:" / "Save this:" beat labels from final
  copy (beats remain as internal structure, labels do not ship); purge "Free guide in bio"
  placeholders — CTA must reference a real, named deliverable or drop the line.
4. **Rotation lists → atom-driven:** replace the hardcoded rotation sentences in
  deterministic_social.py with selection from the bank (add rows if a family is thin — measure
  first per the shape-not-count lens).
5. **APAC leak repair:** strip stage-directions from post_text on the APAC pilot rows; where the
  body is English under a CJK locale, mark the row review_status=draft (do NOT fake-localize;
  CJK6 authoring beyond this is the plan's gap #5/#7 territory, not yours).
Keep the assembly deterministic: same seeds → same output; variety comes from richer banks +
grammar-aware selection, not randomness or runtime LLM.

DELIVERABLES: words_bank.yaml + template-layer diffs; atom-bank additions (JSONL rows with real
citations per the bank schema); deterministic_social.py de-scaffold diff; regenerated 18-post pilot
set; proof root artifacts/qa/social_variety_repair_20260724/ with BEFORE/AFTER post pairs + Lane-02
gate verdicts (before: FAIL expected; after: PASS required) + anti-spam gate PASS
(check_social_post_variation.py); tests updated.

SMALLEST SAFE BATCH: smoke = 1 platform (instagram_feed) × 2 posts pass both gates; pilot = 6 posts
across 3 platforms; scale = regenerate the full 18-post pilot set + full gate sweep.

HANG PREVENTION: poll ≤10 min; standard 2/3 rules; max window 6 h.

TESTS/PROOFS: pytest -x targeted social tests; both gates green on the AFTER set; byte-determinism
check (two runs, same seed → identical output); audit_llm_callers.py clean.

DO NOT: touch Lane 02's gate thresholds (if the gate false-positives, file the evidence and route a
precision-fix with regression test — never self-serve); introduce runtime LLM; fork a parallel
composer/template system; edit flagship/book atom banks; touch coordination hot files; claim
"posts are good now" — that is Lane 04's blind read to decide.

LANDING CONTRACT: MERGED (PR "feat(social): assembly variety repair — hook/CTA grammars,
de-scaffolded copy, atom-driven rotation", checks green, squash-merged, signal, cleanup) or BLOCKED.

CLEANUP LEDGER + HANDOFF: artifacts/coordination/handoffs/social_variety_repair_2026-07-24.md

CLOSEOUT_RECEIPT: standard fields + full MERGE_SHA.
SIGNAL: social-variety-repair-landed=<full merge SHA>
ACCEPTANCE LAYER: EXECUTED-REAL (regenerated posts passing wired gates). NOT PROVEN-AT-BAR until
Lane 04's operator blind read.
~~~
