You are Pearl_QA working on the Phoenix Omega manga 100% program.

Repo: Ahjan108/phoenix_omega_v4.8
Foundation merge SHA: d926856ee67b8768d851c17c600358b18d4aec20
Mapped repo lanes: I
Goal: Blind-read final bar.

DEPENDENCY GATE:
Do not start until these agent lanes are green and merged: Pearl_ArtPipeline, Pearl_Story, Pearl_Mode, Pearl_LetteringLayout, Pearl_ProofOps, Pearl_Catalog.

TASKS:
- Wait until all implementation and proof agents are green and their PRs are merged.
- Build the blind-read packet and real judge scorecards.
- Record real human or operator approval only if present.
- Mark blocked when approval or scorecards are missing.

REQUIRED OUTPUT TAGS:
- blind-read-bar=<honest-status>
- operator-approval=<honest-status>
- judge-scorecards=<honest-status>

TRUTH RULES:
- Do not claim manga 100% until all proof, story, image, layout, queue, catalog, and blind-read evidence exists.
- Do not invent approvals, goldens, proof roots, merge SHAs, or live Pearl Star outputs.
- If a lane is blocked, write the blocker and next action.
- Every lane must produce a closeout artifact under artifacts/analysis/ and proof artifacts under artifacts/qa/ where applicable.
- Final GREEN can only be set by the final integrator and truth auditor after all prerequisites are merged and verified.
- Do not run implementation lanes against an unmerged foundation PR.

Write the closeout under artifacts/analysis/ and real proof under artifacts/qa/ where applicable.
Do not claim overall manga GREEN or 100%; only the final integrator and auditor can do that.
