# Podcast cover art — design system research (Phoenix Omega)

Authority for automation: `config/podcast/cover_art_design_system.yaml` (generated from `config/catalog_planning/brand_identity_system.yaml`).

## Platform image specs (verify before ship)

Primary references consulted **2026-04-09**:

- **Apple Podcasts (show + episode art):** square **1400×1400 to 3000×3000** px, **JPG/PNG**, **RGB**, `itunes:image` over **HTTPS**. Episode art guidance and templates: [Episode Art — Apple Podcasts for Creators](https://podcasters.apple.com/support/5516-episode-art-template); troubleshooting: [Troubleshoot artwork issues](https://podcasters.apple.com/support/902-troubleshooting-artwork-issues).
- **Spotify (show art):** **1:1** ratio, recommended **1400×1400–3000×3000** px, simple high-contrast compositions. [Dos and don’ts of show art — Spotify for Podcasters](https://creators.spotify.com/resources/create/dos-donts-showart); upload flow: [Creating your podcast cover art — Spotify Support](https://support.spotify.com/us/podcasters/article/creating-your-podcast-cover-art/).

For regional platforms (KKBOX, Ximalaya, Podbbang, Noice, etc.), treat `config/podcast/platform_distribution.yaml` as the integration map; **re-check each vendor’s current studio page** before publishing — specs change more often than RSS hosts.

## Design principles (execution checklist)

- **60×60 legibility:** assume the cover is read at thumbnail size in search; limit line count, maximize contrast, avoid thin strokes.
- **Therapeutic positioning:** prefer spacious layouts, no clinical “before/after” implying medical claims; align with EI stealth language policies in production text.
- **Brand × positioning:** use `positioning_variants` in `cover_art_design_system.yaml` (`somatic_companion`, `research_guide`, `elder_stabilizer`) to tint texture/opacity — palettes must remain those in `brand_identity_system.yaml`.

## CJK typography (covers)

Use the font stacks in `cover_art_design_system.yaml` → `cjk_typography`. **Never** substitute zh-TW glyphs for zh-HK or zh-CN; **zh-HK** is Cantonese-market culture, not “generic Chinese.” Furigana is **off** for podcast covers (clean readability at 60×60).

## What we did *not* claim here

No proprietary “algorithm” percentages for third-party apps — discovery mechanics go in `docs/PODCAST_PLATFORM_MARKETING_RESEARCH.md` only with citable sources.
