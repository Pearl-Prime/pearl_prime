# Lane 02 — Post-Copy Craft Gate (validator_contract → real, wired code)

~~~text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_Dev (+ Pearl_QA for gate calibration) for Phoenix Omega.

Repo: Pearl-Prime/pearl_prime. Substrate: fresh branch off latest origin/main
(agent/social-craft-gate-20260724). Explicit-path staging only; poison protocol before commit.

STARTUP_RECEIPT:
- AGENT=Pearl_Dev
- LANE=social_craft_gate_20260724
- EXECUTION_MODE=local_fallback ; BACKGROUND_SAFE=yes
- PERSISTENCE_SURFACES=branch/PR/proof-root
- RESUME_SURFACE=artifacts/coordination/handoffs/social_craft_gate_2026-07-24.md

READ FIRST:
- docs/PEARL_SOCIAL_MEDIA_WRITER_AGENT_SPEC_2026-07-18.md (Writing Standard + Platform Rules — the
  paper bar this lane turns into code)
- the atom bank validator_contract draft (locate under SOURCE_OF_TRUTH/social_media_atoms/manifests/
  or artifacts/social_media_atoms/ — it is SPECCED, not wired; this lane wires it)
- phoenix_v4/social/deterministic_social.py (validate_copy_package, validate_asset,
  generate_copy_package)
- scripts/ci/check_social_post_variation.py (the one real gate — extend its pattern, do not fork it)
- docs/agent_brief.txt §14 (enforcement promotion), §15 (precision-fix vs gate-weakening)

PRE-REQUISITE CHECK (verifiable signal, not narrative):
- social-research-landed=<sha> exists on a merged PR/handoff (Lane 01). If missing → STOP, BLOCKED.

LIVE STATE RECONCILIATION: fetch origin/main; re-read the CLAIMS below against live code — line
numbers are 2026-07-24 claims: validate_copy_package checks only length/hashtag/banned-phrase/
alt-text; validate_asset text_fit + contrast are hardcoded "pass" (never computed); no hook-strength
or template-fingerprint gate exists anywhere; check_social_post_variation.py covers caption-body
3-gram Jaccard only.

DISCOVERY REPORT before action: current SHA; exact current validator inventory (function → checks
performed); location of pilot posts (artifacts/social_media_atoms/pearl_social_media_writer_20260718/
pilot_posts.jsonl + SOURCE_OF_TRUTH/social_media_atoms/pilot_posts/); overlap check vs open PRs.

PROVENANCE:
- research: docs/social_media_YT1–6.txt (hook-first, 6–10-word hooks, first-125-char rule, platform-
  native formats) + docs/research_gemini_social_media_templates_english.txt (validation model) —
  all tracked post-Lane-01
- documents: PEARL_SOCIAL_MEDIA_WRITER_AGENT_SPEC_2026-07-18.md; validator_contract draft;
  SOCIAL_MEDIA_100PCT_PRODUCTION_PLAN_2026-07-22.md (this is the "clearest open territory" it names)
- builds_on: check_social_post_variation.py (gate pattern), validate_copy_package (extend in place)
- inventory: EXTENDS (new checks added; zero existing checks removed)

MISSION (narrow): make the paper craft bar ENFORCED. Implement, as real computed checks:
1. **Template-fingerprint / monotony gate** — detect the five-beat skeleton reuse across a post
   batch: shared scaffold phrases ("is not the whole story", "The mechanism is simple:", "Try
   this:", "Save this:"), CTA sameness (identical CTA sentence with one token swapped), and
   scaffold-label leakage (literal "Mechanism:" / "Hook:" / "Slide N:" labels, "Free guide in bio"
   placeholders) in final copy. Batch-level: max share of posts sharing the same hook grammar.
2. **Hook gate** — first-line/first-125-char check per platform (from platform_specs.yaml rules):
   hook present, within word bounds (6–10-word target from research), not persona-prefix boilerplate
   ("<persona>: <thesis> is not the whole story" counts as ONE grammar, not a pass-all).
3. **Stage-direction-leak gate** — writer instructions embedded in post_text (e.g. "です・ます調で…",
   "先用繁體中文…", English bodies under CJK locale rows) FAIL.
4. **Compute the decorative checks** — text_fit and contrast in validate_asset become real
   computations (PIL measurements), not hardcoded "pass".
Wire all of it as `scripts/ci/check_social_post_craft.py` (single entry, JSON verdict per post +
batch) + hook into `scripts/run_production_readiness_gates.py` as the next free gate number, and
into validate_copy_package for build-time enforcement. Mutation-test: deliberately feed the current
five-beat pilot posts → gate must FAIL them; feed a hand-varied set → PASS; break the gate → RED →
revert (record all three runs in the proof root).

DELIVERABLES: check_social_post_craft.py; deterministic_social.py validator wiring; gate registry
row; tests (tests/test_social_post_craft_gate.py — include the mutation cases); proof root
artifacts/qa/social_craft_gate_20260724/ (before/after verdicts on the 18 existing pilot posts);
handoff.

SMALLEST SAFE BATCH: smoke = gate runs on 1 pilot post with correct verdict; pilot = all 18 pilot
posts + verdict table reviewed for false positives (§15: word-boundary precision, no substring
false-flags); scale = wire into readiness gates + validate_copy_package.

HANG PREVENTION: poll CI ≤10 min; two unchanged → logs; three → BLOCKED. Max window 4 h.

TESTS/PROOFS: pytest tests/test_social_post_craft_gate.py -x; python3 scripts/ci/audit_llm_callers.py
(no new LLM calls — this gate is deterministic heuristics); full mutation-test transcript in proof
root. Calibration note: the gate targets ASSEMBLY monotony, not atom prose — atoms are sentence-level
decent (verified); do not flag atom-level somatic language as cliché without evidence.

DO NOT: weaken or re-tune check_social_post_variation.py thresholds; add a runtime LLM to the
deterministic path; move any threshold to make current posts pass (they SHOULD fail — that is the
point); touch words_bank/templates themselves (Lane 03 owns content); touch coordination hot files.

LANDING CONTRACT: MERGED (PR "feat(social): enforced post-copy craft gate — template-fingerprint +
hook + stage-direction-leak + computed text_fit/contrast", checks green, squash-merged, signal,
branches cleaned) or BLOCKED (blocker + evidence + pushed branch + handoff).

CLEANUP LEDGER + HANDOFF: artifacts/coordination/handoffs/social_craft_gate_2026-07-24.md

CLOSEOUT_RECEIPT: standard fields + full MERGE_SHA.
SIGNAL: social-craft-gate-live=<full merge SHA>
ACCEPTANCE LAYER: gate = CODE-WIRED + mutation-proven. This does NOT make posts good — it makes
"template prose" mechanically detectable. Layer-honest reporting required.
~~~
