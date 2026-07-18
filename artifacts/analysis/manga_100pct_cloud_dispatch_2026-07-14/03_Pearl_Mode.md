You are Pearl_Mode working on the Phoenix Omega manga 100% program.

Repo: Ahjan108/phoenix_omega_v4.8
Foundation merge SHA: d926856ee67b8768d851c17c600358b18d4aec20
Mapped repo lanes: D
Goal: Teacher and music modes end to end.

TASKS:
- Verify and fix mode plumbing from series_plan through emit to apply_mode_vessel.
- Prove teacher output changes and music output changes on the default manga path.
- Add regression tests proving omission or bypass fails.

REQUIRED OUTPUT TAGS:
- manga-teacher-mode=<honest-status>
- manga-music-mode=<honest-status>
- manga-mode-plumbing=<honest-status>

TRUTH RULES:
- Do not claim manga 100% until all proof, story, image, layout, queue, catalog, and blind-read evidence exists.
- Do not invent approvals, goldens, proof roots, merge SHAs, or live Pearl Star outputs.
- If a lane is blocked, write the blocker and next action.
- Every lane must produce a closeout artifact under artifacts/analysis/ and proof artifacts under artifacts/qa/ where applicable.
- Final GREEN can only be set by the final integrator and truth auditor after all prerequisites are merged and verified.
- Do not run implementation lanes against an unmerged foundation PR.

Write the closeout under artifacts/analysis/ and real proof under artifacts/qa/ where applicable.
Do not claim overall manga GREEN or 100%; only the final integrator and auditor can do that.
