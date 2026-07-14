# L7 — Pearl_Research — QA + ethics gates → CI, mutation-tested (Wave 3)

Paste this whole block into the lane agent chat.

~~~text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_Research for Phoenix Omega.

Repo: Ahjan108/phoenix_omega_v4.8
Start from a clean checkout of latest origin/main.

STARTUP_RECEIPT:
- AGENT=Pearl_Research
- LANE=social-L7-gates
- EXECUTION_MODE=github_actions
- BACKGROUND_SAFE=yes
- RUNTIME_HOST=cloud
- PERSISTENCE_SURFACES=branch/pr
- RESUME_SURFACE=phoenix_v4/social/gates/

READ FIRST:
- docs/PROGRAM_STATE.md
- docs/SESSION_UNITY_PROTOCOL.md
- docs/agent_brief.txt
- docs/specs/SOCIAL_MEDIA_PIPELINE_MASTER_SPEC.md
- docs/specs/STATIC_SOCIAL_BOOK_CONTENT_ENGINE_2026-07-13.md (§"QA Gates" + §"Safety And Ethics Gate")
- docs/research_social_media.txt (Part 9 — ethics & credibility)
- scripts/run_production_readiness_gates.py + .github/workflows/ (Drift detectors — where you wire in)

LIVE STATE RECONCILIATION:
- verify social-orchestrator-merged=<sha> (there is a one-book manifest to gate against).
- read the emitted artifacts/social/pilot/<book_id>/social_media_manifest.json live — gates run against the PRODUCTION emitter output, not a hand-fixture.

PRE-REQUISITE CHECKS:
- social-orchestrator-merged=<sha>  → if missing, STOP BLOCKED.

DISCOVERY REPORT BEFORE ACTION:
- current origin/main SHA;
- the pilot manifest to gate;
- how Drift detectors / scripts/run_production_readiness_gates.py register a new gate (mirror an existing one).

PROVENANCE:
- research: docs/research_social_media.txt Part 9 (ethics/credibility); Part 12 (metrics — informs quality gates)
- documents: STATIC_SOCIAL QA + Safety gates; SOCIAL_MEDIA_PIPELINE_MASTER_SPEC
- builds_on: the manifest schema + emitter; existing readiness-gate framework
- inventory: EXTENDS (new social gates); UNCHANGED for existing gates. Memory: "memory is recall, not enforcement" — every doctrine rule becomes an enforced gate here.

MISSION (narrow):
Turn the STATIC_SOCIAL QA gates + ethics/safety gate into CODE gates that run against the
emitted manifest, wire them into the Drift-detectors / readiness-gate suite, and MUTATION-TEST
each (deliberately break → gate goes RED → revert). A gate that stays green under mutation is
not accepted.

DELIVERABLES:
- phoenix_v4/social/gates/ — one checker per gate:
  * platform_fit (asset matches its platform's native format + CTA behavior)
  * source_trace (every story/citation/quote/practice points back to a book section/atom/campaign row)
  * safety_ethics (no unsupported diagnosis, panic bait, shame-sales, therapy-replacement, invented
    testimonials/citations, clinical-term-as-insult, vulnerability manipulation — per the 8-point Safety gate)
  * quote_density (quote-card assets <=15% of the package)
  * mix (practical+recognition+story classes dominate per the default distribution)
  * mobile_readability (text load / contrast / hierarchy heuristics from platform_specs + typography config)
  * media_spec (every media_ref passes L2's media_validator — no out-of-spec asset can schedule)
- scripts/ci/check_social_content_gates.py — CI entrypoint; non-zero exit on any violation.
- wire into scripts/run_production_readiness_gates.py (new gate #) + the Drift detectors workflow.
- tests/test_social_gates.py — includes a MUTATION test per gate (broken fixture → gate fails).

SMALLEST SAFE BATCH:
- smoke: run ONE gate (safety_ethics) against the pilot manifest; then against a deliberately-bad fixture → RED.
- pilot: all 7 gates against the pilot manifest (expect PASS) and against 7 targeted bad fixtures (expect each RED).
- scale: wire into CI; confirm the required-check registration doesn't false-red on unrelated PRs.

HANG PREVENTION:
- poll interval: CI every 2-3 min.
- no-progress rule: inspect the workflow log after two unchanged polls (GHA startup_failure/actionlint patterns — see memory).
- hard stall: BLOCKED after three.
- max window: 120 min.

TESTS/PROOFS:
- pytest tests/test_social_gates.py -x   (each gate + each mutation)
- python scripts/ci/check_social_content_gates.py artifacts/social/pilot/<book_id>/social_media_manifest.json  → exit 0
- mutation evidence: for each gate, a captured RED run on a broken fixture.
- proof root: tests/ + the CI run + a MUTATION_EVIDENCE.md.

DO NOT:
- do NOT weaken a gate or move a threshold to make the pilot pass — fix the ruler, never bend it (precision-fix only, with a regression test that real violations still fail);
- do NOT gate against a hand-fixture instead of the production emitter output;
- do NOT edit 48_SOCIAL / ghl docs or coordination TSVs;
- no fake proof; no local-only finish.

LANDING CONTRACT:
- MERGED: PR (gates + CI wiring + tests + mutation evidence), checks green (incl. the new gate self-testing green on the pilot manifest), squash-merged, `social-qa-gates-merged=<full-sha>` emitted.
- BLOCKED: exact blocker + evidence + pushed branch + handoff.

CLEANUP LEDGER REQUIRED:
- worktree / local+remote branch / scratch files / background jobs / held artifacts.

HANDOFF REQUIRED:
- artifacts/coordination/handoffs/social-L7-gates_2026-07-14.md

CLOSEOUT_RECEIPT:
- AGENT: Pearl_Research
- LANE: social-L7-gates
- STATUS=MERGED|BLOCKED
- BRANCH / PR / MERGE_SHA:
- SIGNAL: social-qa-gates-merged=<full-sha>
- ACCEPTANCE_LAYER: CODE-WIRED (gates enforced + mutation-proven RED); the CONTENT they guard is separately layer-labelled by L8
- PROOF_ROOT: tests/ + MUTATION_EVIDENCE.md + CI run
- TESTS / CLEANUP / HANDOFF / NEXT_ACTION:
- TOKEN: CLOSEOUT_RECEIPT::social-L7-gates
~~~
