# Podcast platform marketing research (13 markets)

Machine-readable aggregate: `config/podcast/platform_marketing_config.yaml`.  
Distribution map: `config/podcast/platform_distribution.yaml`.

## artwork + RSS anchors (global)

- **Spotify show art:** [Dos and don’ts of show art](https://creators.spotify.com/resources/create/dos-donts-showart) (accessed 2026-04-09).
- **Apple Podcasts artwork + RSS:** [Episode art template](https://podcasters.apple.com/support/5516-episode-art-template); feed troubleshooting: [Artwork issues](https://podcasters.apple.com/support/902-troubleshooting-artwork-issues) (accessed 2026-04-09).

## Title + description SEO (non-exhaustive)

- Keep **primary therapeutic keywords in the first 120–160 characters** of the description (visible without “more” taps in many clients).
- Prefer **education / nervous system / practice** vocabulary over clinical diagnosis copy except where a market explicitly expects it (see per-market framing in `brand_podcast_plans.yaml`).
- zh-CN: plan for **synthetic-voice disclosure** and platform upload flows that differ from RSS-first markets — see `platform_distribution.yaml` and PRC regulatory notes in Pearl governance; do not assume RSS-only.

## Social clip formats

- Vertical **9:16** clips (approx. **15–60s**) remain the default cross-post pattern for TikTok / Reels / Shorts; re-verify each platform’s max duration annually in official help centers (URLs vary by product surface).

## monetization

Treat monetization claims as **hypothesis until backed by a specific network insertion order / contract**. Use `platform_marketing_config.yaml` only for **enum-level planning** (e.g., Ximalaya paid columns), not for CPM assertions without a primary finance source.

## regulatory

China / Japan / EU / US podcast rules evolve on **platform policies + broadcast/ad law**, not RSS alone. Anything labeled “mandatory” in Phoenix work must cite **a primary regulator or platform document with date** in the Pearl research archive — not this summary.
