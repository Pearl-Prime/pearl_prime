"""Phoenix Omega translation-quality pipeline scaffolding.

This package is infrastructure only: deterministic validators, candidate
LLM client wrappers, COMET scoring integration, a calibration harness, an
acceptance-gate engine, a repair/retry state machine, and consistency-pass
tooling. It makes NO translation-quality judgment calls itself (no
glossary decisions, no evaluation scoring, no accept/reject calls) — those
are produced by Claude Code (Lane 02 of the
docs/agent_prompt_packs/20260721_zh_tw_translation_quality_program/ pack)
and fed into this package's deterministic consumers.

See pipeline_config.yaml (this directory) for every schema this package
and Lane 02 agree on.
"""
