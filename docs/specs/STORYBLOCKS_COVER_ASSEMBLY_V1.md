# Storyblocks Cover Assembly V1

**Status:** WIRED; inventory coverage is independently gated.

**Runtime:** CPU/Pillow only; no GPU and no generated imagery.
**Scope:** all 17 canonical topics and all 14 registered market locales.

## Production contract

`scripts/publish/five_layer_cover_orchestrator.py` is the cover entry point. It selects through `bank_image_picker.py`, then composes through the canonical KDP renderer. Storyblocks is the preferred and only automatic production image bank. A candidate must be a locally downloaded licensed image, have `surface: cover`, contain the exact topic in `metadata.topic_keys`, carry `metadata.topic_verified: true`, and pass the positive/excluded cue rules in `config/publishing/storyblocks_cover_topic_map.yaml`.

No qualifying candidate means `CoverBankPickError`. There is no silent persona-bank or generated-image fallback. `--allow-legacy-bank` / `COVER_ALLOW_LEGACY_BANK=1` is QA-only and must not be used for production.

“Train on our topics” means curate and validate metadata against the topic ontology. Storyblocks media and metadata remain excluded from AI/ML training under the existing license-store wall.

## Five deterministic layers

1. Brand identity from `cover_identity_system.yaml`.
2. Topic blueprint from `bestseller_templates.yaml`.
3. Series continuity passed as `series_id` and recorded in provenance.
4. Book-specific identity and deterministic seed.
5. Locale typography/reflow provenance for the 14 market lanes.

`adhd_focus` uses the `overthinking` blueprint and `mindfulness` uses the `anxiety` blueprint until dedicated blueprints land; imagery matching remains exact to the requested topic.

## Gate and readiness

Run `python scripts/ci/verify_cover_topic_imagery.py`. It exits non-zero unless every canonical topic has at least one valid licensed candidate. Wiring being present does not claim that images are licensed or catalogs are complete. Current committed inventory has no cover-surface license index, so assembly correctly blocks until operators download and verify candidates through the existing Storyblocks confirmation workflow.

The market registry declares all 14 locales, but declaration is not the same as a fully authored book-plan catalog. Cover batches may be assembled only for actual catalog rows after both catalog and image gates pass.
