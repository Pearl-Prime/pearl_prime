# Q11 — Cost & Throughput Envelope

**Date:** 2026-04-29

## A. Caveats up front

- **No invoice access** for this audit. All numbers below are projections from public pricing × repo-visible usage logs. Labeled `[ESTIMATED]`.
- The `audit_llm_callers.py` workflow enforces tier-1 ban on Anthropic API in repo code; tier-2 (Gemma/Qwen on Pearl Star) is local — marginal cost = electricity, not measurable from repo.
- TTS policy (per PR #734 in flight): CosyVoice2 (free, local) + Edge TTS (free, MS) + OpenAI freemium banded. ElevenLabs banned.
- Cloudflare Workers + Pages costs likely sit in free tier given current traffic.

## B. Cost categories actually visible

| category | pricing source | usage log location | mode |
|---|---|---|---|
| Pearl Star electricity (RTX 5070 Ti) | n/a — self-hosted | `pearl-star-health.yml` (currently 0/30 pass) | local, marginal |
| Anthropic (Claude Code subscription) | $200/mo Pro plan tier (operator-attended Tier-1 only) | not in repo | flat |
| OpenAI freemium TTS | $0/$0.015 per 1k chars (paid overage banned per PR #736 if landed) | n/a | freemium |
| Edge TTS | free (MS) | n/a | free |
| CosyVoice2 | free (local) | n/a | local |
| RunComfy GPU rentals (image gen) | public pricing $0.50–$3.00 per render-minute on rented machines | runcomfy_batch.py logs (per render) | per-call |
| Cloudflare R2 storage | $0.015/GB/mo | n/a; depends on uploaded volume | per-GB |
| Cloudflare Workers | free up to 100k req/day | `workers-builds: pearl-prime` per PR #745 | free tier likely |
| Cloudflare Pages | free up to 500 builds/mo, 100k req/day | `pages.yml` | free tier likely |
| WordPress hosting (pearlnewsuna.org) | external — n/a | n/a | flat |

## C. Estimated monthly cost (today, pre-storefront-ship) [ESTIMATED]

| line | low | high | notes |
|---|---:|---:|---|
| Anthropic Pro subscription (operator) | $200 | $200 | Claude Code Tier-1 only |
| Pearl Star electricity (24×7 light load) | $25 | $50 | rough |
| Cloudflare R2 storage (assume 10 GB current artifacts) | $0 | $1 | first 10 GB free historically; check current |
| Cloudflare Workers + Pages | $0 | $5 | free tier likely sufficient |
| RunComfy (per-batch, infrequent today) | $20 | $80 | based on visible image_bank generation activity |
| External SaaS (Apify, etc., trend feeds) | $0 | $50 | budget guard at `scripts/feeds/budget_guard.py` |
| WordPress hosting | $20 | $40 | flat |
| **Total (est.)** | **$265** | **$426** | sub-$500/mo today |

## D. Estimated cost AT SCALE (Phase 4 ship — full automation across all 22 subsystems) [ESTIMATED]

Assumptions:
- Output: ~800 books × 12 locales = ~9,600 book outputs/year (operator's "800 high-confidence configs" target per [`/Users/ahjan/.claude/projects/-Users-ahjan-phoenix-omega/memory/project_800_high_confidence_configs.md`](memory:project_800_high_confidence_configs.md))
- Manga: 1 episode × 5 locales × 26 brands × ~2/month = ~3,120 episode-shipments/year
- Audiobooks: 800 books × 1 audiobook × 2 locales = 1,600 audiobook outputs/year
- Pearl News: ~12 articles/day × 365 = 4,380 articles/year
- Each manga episode = 35 panels × ~$1 RunComfy median = ~$35/episode → $109k/year if no LoRA infra
- LoRA path (one-time + per-brand): GPU upgrade $1,500 OR cloud LoRA training $600/brand × 37 brands = $22,200; reusable

| line | low | high | notes |
|---|---:|---:|---|
| Anthropic Pro (assume one operator) | $200 | $200 | flat |
| Pearl Star electricity (heavy GPU usage) | $80 | $200 | depends on render volume |
| GPU upgrade (24GB+) one-time amortized over 24 months | $60 | $130 | if chosen over cloud |
| RunComfy / cloud GPU (manga renders) | $5,000 | $15,000 | $35-100 per episode × ~3,120 episodes/year ÷ 12 |
| Storage (R2, ~500 GB scaled) | $7 | $10 | $0.015/GB |
| Workers + Pages (paid tier likely needed) | $5 | $30 | depending on traffic |
| Edge TTS / OpenAI freemium / CosyVoice (local) | $0 | $200 | freemium banded; cap per PR #736 |
| KDP / Apple Books / LINE Manga submission (no fee, time only) | $0 | $0 | royalty deducts on sale |
| WordPress + subdomains | $40 | $100 | scaled hosting |
| External SaaS (trend feeds, social) | $50 | $200 | with budget guard |
| **Total per month (steady-state full scale)** | **~$5.5k** | **~$16k** | $66k–$190k/year direct cost |

Per-output unit economics (rough):

- **Per book at scale**: $66k/year ÷ 9,600 books = ~$7-20 / book in tooling cost. Setup-amortized.
- **Per manga episode at scale**: ~$35-100 (GPU dominant). Volume reduces this if LoRA reused.
- **Per Pearl News article**: <$0.01 today (Tier-2 LLM) — already efficient.

## E. Cost cliffs

1. **Manga GPU scaling.** $35-100/episode × volume = the dominant variable. Decision tree:
   - Pearl Star + GPU upgrade ≥24GB ($1,500 one-time): unlocks LoRA training, low marginal cost per episode.
   - Cloud LoRA training only ($600-1500 per brand × 37): high upfront, low marginal.
   - IP-Adapter (no LoRA training): lowest cost but quality risk per PR #623.
   - **Recommend**: GPU upgrade. Unlocks the entire manga roadmap; pays back in <6 months at expected volume.

2. **Translation atom volume.** zh_CN ~2,200 atoms × Tier-2 (Pearl Star Qwen) = effectively free. Tier-1 (operator-attended via Claude Code) would cost real money. **Stay on Tier-2.**

3. **TTS for full audiobooks.** CosyVoice2 (local) is free; Edge TTS is free. ElevenLabs banned. Already disciplined.

4. **External SaaS creep.** Trend feeds, social platform submission tooling, KDP automation libraries — each adds $20-50/mo. Cap proposed by `scripts/feeds/budget_guard.py`. Maintain.

## F. Time-to-cash / payback envelope [ESTIMATED]

- **Phase 1 ship cost** (build EPUB packager + KDP submission): ~$3-5k engineer-days at hired rate ($800/day) = $2.4-4k. AI-only path: 0 cash, ~5-7 operator-days (with Claude Code Tier-1 subscription).
- **Phase 1 revenue floor**: 1 KDP-submitted book × $4 royalty × 1 sale/day (conservative) = ~$120/mo per book. 50 books = $6k/mo. **One-month payback at modest volume.**
- **Phase 3 manga ship cost** (operator-side): ~$1,500 GPU upgrade + ~5 engineer-days = ~$5k all-in.
- **Phase 3 manga revenue floor**: WEBTOON Canvas / KDP Comics royalties; volatile by genre. Conservative $50-200/episode/year.

## G. Recommendation

Total monthly cost today is ~$265-426 (ESTIMATED). Total at scale is ~$5.5k-16k/mo. The dominant variable is manga GPU. **Make the GPU decision (PR #623) within 30 days** — it's the single largest cost lever in the entire system.

**Budget envelope for next 90 days** (Phase 0 + Phase 1 + Phase 3 first ship):
- Tooling + ops: ~$1,200-1,800
- One-time GPU upgrade: ~$1,500 (optional but recommended)
- AI-only path engineer time: ~30-40 operator-days (with current Claude Code subscription)
- Hired-team engineer time: ~$15-20k at $800/day blended rate over 90 days
