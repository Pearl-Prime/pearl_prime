STARTUP_RECEIPT
AGENT:              Pearl_PM
TASK:               ProPrime modes 100% — regular / composite / teacher / music on clean main
PROJECT_ID:         proj_pearl_prime_bestseller_rebase_20260425
SUBSYSTEM:          core_pipeline;teacher_mode;music_mode
AUTHORITY_DOCS:     docs/PROGRAM_STATE.md;docs/SESSION_UNITY_PROTOCOL.md;docs/PEARL_ARCHITECT_STATE.md;docs/DOCS_INDEX.md;docs/PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md;docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md;docs/specs/AGENT_EXECUTION_FABRIC_V1_SPEC.md
READ_PATH_COMPLETE: yes
WRITE_SCOPE:        artifacts/coordination/*;artifacts/qa/proprime_modes_100pct_20260711/*;docs/PROGRAM_STATE.md;artifacts/coordination/ACTIVE_WORKSTREAMS.tsv;fix PRs only if mode blockers found
OUT_OF_SCOPE:       manga_pipeline;localization catalog skeletons;mass deletions
PROVENANCE:         none (verification + bugfix-class; no new capability unless music production gap requires it)
EXECUTION_MODE:     github_actions
BACKGROUND_SAFE:    yes
RUNTIME_HOST:       github_actions (ubuntu-latest Book flagship QA ladder) + pearl-star self-hosted runner online
PERSISTENCE_SURFACES: github_actions_run;remote_branch_or_pr;artifacts/qa/proprime_modes_100pct_20260711
RESUME_SURFACE:     artifacts/coordination/STARTUP_RECEIPT_proprime_modes_100pct_20260711.md; worktree proprime-modes-100pct-20260711; GHA run 29129940199
BLOCKERS:           none at startup — pearl-star online; conflicting open PRs on mode paths = 0 (sampled 80)
READY_STATUS:       ready
ORIGIN_MAIN_SHA:    98187a46982d758601defa322c273ec459742293
