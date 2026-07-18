# Brand 2 (cognitive_clarity) ep_001 Ship — Stages A-C Landed; D-H Gated

**Date:** 2026-05-07
**Brand:** cognitive_clarity (seinen, overthinking) — flagship per
`config/manga/canonical_brand_list.yaml`. Chosen over digital_ground
because seinen demographic pairs naturally with ja-JP market.
**Episode:** ep_001 "The Loop Is Not Thinking"
**Author:** ahjan
**Locales (this PR):** en-US (authored) + ja-JP (Tier 1 inline translation;
native-speaker review recommended pre-WEBTOON-Japan publish)
**Closes:** stages A-C of the brand-2 ship runbook. D-H gated on operator
unblocks (see Blockers below).

## What landed in this PR

| Stage | Path | Notes |
|---|---|---|
| A | brand pick + slug + episode anchor | cognitive_clarity, overthinking, "The Loop Is Not Thinking" |
| B | `artifacts/manga/chapter_scripts/cognitive_clarity__ahjan__en_US__overthinking__the_loop_is_not_thinking/ep_001.yaml` | 5 chapters × 5 panels = 25 panels; en-US + ja-JP per-panel `text_by_locale` |
| C | `artifacts/manga/panel_prompts/cognitive_clarity__ahjan__en_US__overthinking__the_loop_is_not_thinking/ep_001.panel_prompts.json` | 25 FLUX-ready prompts (avg 404 chars / max 521 chars); locale-agnostic imagery; explicit no-text negative_prompt |

## Blockers for stages D-H (operator unblocks)

### GATE-OP-1 — R2 secrets missing from Keychain

`scripts/ci/load_integration_env_from_keychain.py` exports nothing for
`R2_ACCOUNT_ID`, `R2_BUCKET`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`.
Registry tracks the names; Keychain entries themselves aren't populated.

**Operator fix:**
```bash
security add-generic-password -a "$USER" -s R2_ACCOUNT_ID -w "<value>"
security add-generic-password -a "$USER" -s R2_BUCKET -w "<value>"
security add-generic-password -a "$USER" -s R2_ACCESS_KEY_ID -w "<value>"
security add-generic-password -a "$USER" -s R2_SECRET_ACCESS_KEY -w "<value>"
```
(Values from Cloudflare R2 dashboard.)

### GATE-OP-2 — Pearl Star SSH unreachable from this worktree

This worktree env has no SSH keys (`/Users/ahjan/.ssh/id_*` are absent).
`pearlstar.tail7fd910.ts.net` rejected with `Permission denied
(publickey,password)`.

**Operator fix:** drop the SSH key into `~/.ssh/` on this Mac, OR run
the Pearl Star steps (FLUX render via `scripts/manga/queue_panel_renders.py`,
marker install) from the primary machine that already has the key.

## Stages D-H (queued; runnable once gates clear)

| Stage | What | Owner |
|---|---|---|
| D | Pearl Star FLUX render of 25 panels at 1080×1920 via `scripts/manga/queue_panel_renders.py` (now committed at 9402 bytes per worktree check) | Pearl_Dev / Pearl_Video — needs GATE-OP-2 |
| E | Bubble compose per locale via `phoenix_v4.manga.chapter.bubble_render` | Pearl_Dev — runs after D |
| F | Webtoon vertical strip via `phoenix_v4.manga.chapter.webtoon_compose` | Pearl_Dev |
| G | R2 upload via `scripts/artifacts/r2_sync.py` + brand_admin manifest.json | Pearl_Int / Pearl_Dev — needs GATE-OP-1 |
| H | WEBTOON Canvas en-US + ja-JP upload via `scripts/publish/webtoon_canvas_upload.py` | **operator** — final click; LINE Manga Indies decision (per runbook §5 E) operator-gated |

## Known caveats

1. **ja-JP Tier 1 translation V1.** Pearl_Localization native-speaker
   review recommended before publishing to WEBTOON Japan or LINE Manga
   Indies. The translation is grammatically defensible but cultural
   register (seinen-specific colloquialisms, polite-form vs casual)
   may need a pass.

2. **Brand voice fidelity.** Voice profile was inferred from
   `canonical_brand_list.yaml` notes ("Overthinking · Psychology ·
   CBT-adjacent · Seinen adult men"). If a richer voice_profile.yaml
   for cognitive_clarity exists or gets authored later, ch_script
   should be re-pass'd against it.

3. **Anchor topic = overthinking.** Chosen as primary_topic per the
   canonical list. Secondary topics (imposter_syndrome, burnout,
   boundaries) reserved for ep_002+.

4. **No clash with brand 1.** stillness_press anchor = anxiety; this
   ep_001 anchor = overthinking. Distinct topics; no content overlap.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
