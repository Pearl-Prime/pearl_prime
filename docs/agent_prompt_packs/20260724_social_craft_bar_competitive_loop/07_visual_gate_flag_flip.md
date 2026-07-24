# Lane 07 — Visual-Gate Flag Flip + Golden Freeze (execute the #96 OPD)

~~~text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_QA (+ Pearl_GitHub for landing) for Phoenix Omega.

Repo: Pearl-Prime/pearl_prime. Substrate: fresh branch off latest origin/main
(agent/social-visual-flag-flip-20260724). Explicit-path staging; poison protocol.

STARTUP_RECEIPT:
- AGENT=Pearl_QA
- LANE=social_visual_flag_flip_20260724
- EXECUTION_MODE=local_fallback ; BACKGROUND_SAFE=yes
- PERSISTENCE_SURFACES=branch/PR/bank-TSVs/golden
- RESUME_SURFACE=artifacts/coordination/handoffs/social_visual_flag_flip_2026-07-24.md

READ FIRST:
- PR #96 (MERGED: "docs(governance): record operator approval — social visual license + look
  gate") — read the FULL PR body + the OPD row it added to operator_decisions_log.tsv. The exact
  wording of what the operator approved is this lane's entire authority. Quote it in your
  DISCOVERY REPORT.
- artifacts/coordination/handoffs/deterministic_social_visual_license_operator_gate_2026-07-18.md
  (records STATUS=BLOCKED_RELEASE_GATE, LIVE_PUBLISHING_AUTHORIZED=no, 0/405 production-ready)
- docs/SOCIAL_VISUAL_PUBLISHABLE_QUALITY_SPEC_2026-07-18.md
- scripts/social/freeze_social_visual_golden.py + apply_media_bank_lookgate.py (the existing
  execution tools — use them, never re-author)
- phoenix_v4/social/media_selector.py (strict pool: provenance=REAL + look_gate=PASS)

PRE-REQUISITE CHECK (the load-bearing one):
- The #96 OPD row EXPLICITLY authorizes flipping production_ready / look_gate on the identified
  rows. If the OPD wording approves the LICENSE finding but NOT the look/flag-flip, this lane is
  BLOCKED-ON-OPERATOR — surface the exact quote + a one-line question with recommended default,
  and stop. Do NOT infer authorization from adjacent approvals.

LIVE STATE RECONCILIATION: fetch; re-verify CLAIMS: artifacts/qa/deterministic_social_visual_gate_20260718/
TSVs are ABSENT from the working tree (they may exist on origin/main — check git cat-file first,
restore by checkout, never regenerate if git already has them: drift-recovery-git-first rule);
zero look_gate=PASS rows across media banks (grep the bank TSV/JSONL indexes); current
LIVE_PUBLISHING_AUTHORIZED marker state.

DISCOVERY REPORT before action: current SHA; #96 OPD verbatim quote; gate-artifact recovery path
(git restore vs regenerate via run_visual_license_operator_gate.py); exact row inventory to flip
(expected 405 render rows ← 3 license-verified source visuals); blast radius (which consumers read
look_gate=PASS — media_selector strict pool, assemble/carousel paths).

PROVENANCE:
- research: n/a (execution of a recorded operator decision)
- documents: #96 OPD; SOCIAL_VISUAL_PUBLISHABLE_QUALITY_SPEC; 100PCT plan gap #2 follow-through
- builds_on: freeze_social_visual_golden.py; apply_media_bank_lookgate.py; the 07-18 gate artifacts
- inventory: EXTENDS (flips authorized flags; deletes nothing)

MISSION (narrow):
1. Recover the gate artifact TSVs (git-first; regenerate only if genuinely never committed —
   record which).
2. Apply the authorized flips via apply_media_bank_lookgate.py (or the tool the 07-18 lane
   designated) — ONLY rows the OPD covers. 405 is a CLAIM; the OPD's own row list wins.
3. Fire scripts/social/freeze_social_visual_golden.py --confirm-operator-approved (staged
   golden-freeze that has been waiting since #40) so the approved look is machine-defended
   (sidebar-parity pattern).
4. Verify downstream: media_selector strict pool now returns REAL rows for the approved visuals
   (a 3-line python check in the proof root); INTERIM_PREVIEW_ONLY remains for everything else.
5. Update LIVE_PUBLISHING_AUTHORIZED marker ONLY if the OPD wording covers it; otherwise leave and
   note (publishing authorization ≠ asset production-readiness — keep the distinction).

DELIVERABLES: flipped bank rows; frozen golden + parity check; proof root
artifacts/qa/social_visual_flag_flip_20260724/ (before/after row counts, strict-pool check output);
PR; handoff.

SMALLEST SAFE BATCH: smoke = flip 1 row, strict-pool check sees it; pilot = one source visual's
row family; scale = full authorized set + golden freeze.

HANG PREVENTION: standard 2/3 polling; max window 3 h.

TESTS/PROOFS: pytest targeted media_selector tests; parity/golden check green; row-count math in
handoff (flipped == OPD-authorized count, no more).

DO NOT: flip anything beyond the OPD's explicit scope; regenerate artifacts git already has; touch
render code; weaken the look gate; declare "visuals production-ready" beyond the flipped rows;
touch coordination hot files.

LANDING CONTRACT: MERGED or BLOCKED (the BLOCKED-ON-OPERATOR path above is expected if the OPD is
narrower than claimed — that outcome is a SUCCESS for truth, report it plainly).

CLEANUP LEDGER + HANDOFF: artifacts/coordination/handoffs/social_visual_flag_flip_2026-07-24.md

CLOSEOUT_RECEIPT: standard fields + full MERGE_SHA.
SIGNAL: social-visual-flags-flipped=<full merge SHA> (or BLOCKED with the OPD quote)
ACCEPTANCE LAYER: flipped rows = EXECUTED-REAL production-ready ASSETS; not a publishing claim
(live scheduling remains a ratified non-goal).
~~~
