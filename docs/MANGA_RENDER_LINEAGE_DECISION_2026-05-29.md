# Manga Render Lineage — Reconciliation Decision

**Date:** 2026-05-29
**Status:** ✅ RATIFIED 2026-05-29 (operator). The recommendation below is the accepted decision; recorded as cap `MANGA-RENDER-LINEAGE-01` in `docs/PEARL_ARCHITECT_STATE.md`.
**Authority context:** `docs/specs/MANGA_V5_LAYERED_ARCHITECTURE.md` (AUTHORITY 2026-05-20)
**Origin:** provenance audit follow-up (the "two parallel render lineages" weak-link)

## Finding (evidence-backed)

Two render lineages exist in the repo, sharing only `continuity_state`:

1. **Active production path — V4/V5 contract-driven.** Hand-authored / generated `continuity_state` YAMLs → `contract_to_prompt_compiler` (V4 spec §5.9) → `scripts/manga/render_v5_episode.py` (Qwen-Image-Layered, V5.1) → recompose. This is what the AUTHORITY V5.1 spec runs (`render_v5_episode.py:117` calls the compiler, **not** `panel_prompts.json`), and what the continuity-state generator (`scripts/manga/continuity_state_generator.py`) feeds. ep_001 rendered 35/35 on Pearl Star.
2. **SpiritualTech agent suite.** `chapter_script.json` → `VISUAL_AGENT` (`scripts/manga/build_panel_prompts.py`) → `panel_prompts.json` (FLUX/SDXL prompts) → render; + `LETTERING_AGENT` + `LAYOUT_AGENT`. **The V5 render chain does not consume `panel_prompts.json`.**

## Recommended decision (operator ratifies)

- **CANONICAL for render:** the V4/V5 contract + `continuity_state` chain — it is what V5.1 runs and what the continuity-state generator scales.
- **SUPERSEDED for the layered-render approach:** `VISUAL_AGENT` / `build_panel_prompts.py` prompt-planning (the `contract_to_prompt_compiler` replaces it for V5.1). Retain `VISUAL_AGENT` as experiment-of-record / for any non-layered fallback.
- **RETAINED:** `LETTERING_AGENT` + `LAYOUT_AGENT` — the post-render text/composition layer is still needed regardless of render engine. Note the *active* lettering path is the V5 lettering-v2 work (PR #945, `agent/manga-lettering-v2-20260507`); reconcile `LETTERING_AGENT` against it.
- **Open prompt-strategy item:** `VISUAL_AGENT` assumes a FLUX/SDXL token strategy; V5.1 renders Qwen-Image-Layered, which wants the natural-language-prose strategy per `docs/CHARACTER_INDIVIDUATION_PIPELINE_SPEC_2026-05-02.md` §2.3. If any `VISUAL_AGENT` logic is reused, align the prompt strategy to Qwen.

## Why (best-manga rationale)

The V4→V5 pivot was operator-directed precisely because the layered/contract approach fixes the geometry + cutout failures that left V4 at 2/35 acceptable. The `continuity_state` contract is the foundation the generator scales. Consolidating on it = one canonical, scalable, best-quality render path.

## Not yet ratified

This doc records the recommendation. The operator decides whether to formally retire/merge the SpiritualTech prompt-planning specs. **No specs are deleted by this doc.** On ratification: mark `VISUAL_AGENT_SPEC.md` superseded-for-layered-render and add a `MANGA-RENDER-LINEAGE-01` cap entry to `docs/PEARL_ARCHITECT_STATE.md`.
