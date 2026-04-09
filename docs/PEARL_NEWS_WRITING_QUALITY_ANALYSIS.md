# Pearl News — Writing Quality Analysis (Baseline + Routing Prep)

**Date:** 2026-04-09  
**PROJECT_ID:** proj_state_convergence_20260328  
**Authority:** [docs/PEARL_NEWS_WRITER_SPEC.md](./PEARL_NEWS_WRITER_SPEC.md), [docs/research/PEARL_NEWS_QWEN_DEEP_RESEARCH_ENGINE.md](./research/PEARL_NEWS_QWEN_DEEP_RESEARCH_ENGINE.md)

## Method

1. Ran `python3 -m pearl_news.pipeline.run_article_pipeline --language {en,ja,zh-cn} --limit 1 --expand --validate` against live UN RSS (single-item smoke per locale).  
2. Scored outputs against writer-spec criteria below.  
3. **Environment note (this run):** `ANTHROPIC_API_KEY` was absent (Claude path correctly failed fast and fell back per config). Pearl Star Ollama returned `404` for `qwen3:14b` (model not present on that host from this runner’s perspective). Expansion therefore did not mutate drafts; scores reflect **assembler placeholders + pipeline gates + EI v2** on that baseline HTML.

## Per-sample scoring (0–10)

Article: UN story “Iran ceasefire raises hopes…” (feed id `f565a3628a8c1f7d`), template `hard_news_spiritual_response`. Placeholder teacher + generic youth block.

| Locale | Structure | Voice | Cultural fit | Teacher integration | Factual anchoring | Readability | Notes |
|--------|-------------|-------|--------------|---------------------|-------------------|-------------|-------|
| EN | 5 | 4 | 5 | 2 | 4 | 6 | Generic youth block; “We aim…” triggers banned phrase gate; no contradiction in youth section |
| JA | 5 | 4 | 3 | 2 | 4 | 6 | Same English placeholder body; no JA-specific keigo or 引きこもり/juken layer in text |
| ZH-CN | 5 | 4 | 3 | 2 | 4 | 6 | Same structural gap; no gaokao/tangping framing in placeholder |

**EI v2 (EN sample, post-expansion slot in pipeline):** composite ≈ **0.80** (safety risk 0; TTS/readability moderate; stealth clean on placeholder text).

**Validation (8 gates):** Failed **`named_teacher`**, **`youth_anchor`**, **`no_banned_phrases`** (`\bwe\b` in “We aim…”). Confirms gates fire on placeholder/default content when expansion does not run.

## Checklist vs PEARL_NEWS_WRITER_SPEC

| Criterion | EN (baseline) | JA | ZH-CN |
|-----------|---------------|-----|-------|
| Contradiction test in youth impact | No | No | No |
| Teacher: named, 3 distinct tradition-specific points | No (Forum placeholder) | No | No |
| SDG: number + title + specific target | Title present; target shallow | Same | Same |
| Anchor density (stats/places/behaviors per ~500 words) | Low | Low | Low |
| Voice: no banned patterns, active voice, short lede | Lede ok; **“we”** fails | Same | Same |
| CJK cultural markers | N/A (English text) | Missing | Missing |

## Top 5 writing weaknesses (across samples)

1. **Unexpanded assembler defaults** — Generic youth paragraphs and Forum placeholder teacher do not meet named-teacher or youth-anchor gates.  
2. **No contradiction test** — Youth section reads as flat affirmation, not generational tension (writer spec §7).  
3. **Teacher atoms English-only** — CJK runs still inherit English placeholders when atoms/roster resolve to fallback; hurts cultural fit until expansion succeeds in-language.  
4. **Register slips** — “We aim…” violates voice rules and validation (`\bwe\b`).  
5. **Single-model legacy** — Prior architecture ran one Qwen prompt for all locales; prose and register hints could not select provider-level behavior.

## Recommendations (implemented in routing branch)

- Route **EN → Claude** (slot engine + `expansion_system_en.txt`), **CJK6 → Qwen** on Pearl Star with `expansion_system_cjk.txt`.  
- Keep **shared** `expansion_teacher_block.txt` for consistent bullets across providers.  
- Run **EI v2** between expansion and validation; treat safety/stealth breaches as hard review.  
- Operational: ensure `QWEN_MODEL` matches a pulled Ollama tag on `192.168.1.112:11434` and load `ANTHROPIC_API_KEY` for EN.

## Comparative expectation (after healthy credentials)

| Path | Expectation |
|------|-------------|
| EN + Claude | Stronger English lede, anchors, contradiction articulation |
| CJK + Qwen | Better locale register (keigo, 高考/躺平, HK/TW/SG markers per prompt) |
| CJK + Qwen vs API | Lower latency on LAN Pearl Star vs cloud Claude |
