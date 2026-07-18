"""Phase A character individuation package — V2 manga pipeline foundation.

Implements the load-bearing pieces of CHARACTER_INDIVIDUATION_PIPELINE_SPEC §2.2,
§2.3, and §2.5 plus the cookbook + drawing-tradition + cross-genre + forbidden-tokens
wiring that lifts catalog-wide character distinctness from "hopeful" to
"deterministic before render."

Modules:
    constraint_solver — collision detection across character_design instances
    prompt_builder    — emits axis-specific tokens per base-model strategy
    qa_face_distance  — facenet-pytorch wrapper for post-render QA gate

See docs/PEARL_ARCHITECT_STATE.md::MANGA-LAYERED-PIPELINE-V2-01 for phase scope.
"""
