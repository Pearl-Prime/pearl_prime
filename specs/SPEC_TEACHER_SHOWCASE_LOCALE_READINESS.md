# Spec — Teacher Showcase Locale Readiness (Phase 1)

**Version:** 1.0.0
**Date:** 2026-04-29
**Issue:** [#778 — Complete teacher page requirements beyond routing and portraits](https://github.com/Ahjan108/phoenix_omega_v4.8/issues/778)
**Authority:** Pearl_Architect (this spec) → Pearl_Dev (implementation in a future PR) → Pearl_PM (acceptance)
**Status:** **SPEC ONLY — no implementation in this PR.** Operator brief 2026-04-29: "PR-E is spec only. Do NOT build localized pages yet. Stop after plan."
**Scope:** `brand-wizard-app/public/teacher_showcase.html` only (the broader brand-wizard wizard pages already have `wizard-ja.html` / `wizard-tw.html` / `wizard-zh.html`).

---

## §1 — Why this spec exists

Issue #778 audit ([artifacts/audits/teacher_page_requirements_audit_2026-04-28.md](../artifacts/audits/teacher_page_requirements_audit_2026-04-28.md)) found:

- **Req #17 Locale-readiness: 0/13** — `teacher_showcase.html` is en_US only; no language switcher; no per-locale variants exist.
- The catalog has expanded to 8 markets per [PR #738](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/738) but the showcase product surface lags.

This spec defines **Phase 1** locale extension. Phase 2 (5 remaining markets) is explicitly out of scope until Phase 1 ships and is validated.

---

## §2 — Phase 1 decisions (operator-locked)

| Decision | Choice | Source |
|---|---|---|
| **Locales in Phase 1** | `en_US`, `ja_JP`, `zh_TW`, `zh_CN` (4 total) | Operator brief 2026-04-29 |
| **Architecture** | Separate HTML files per locale | Operator brief 2026-04-29 ("separate HTML recommended") |
| **Translation tiers** | UI labels + teacher bio/teaching summary only | Operator brief 2026-04-29 ("UI + bio only") |
| **NOT in Phase 1** | Full book chapter content translation | Implicit — operator excluded by limiting to "UI + bio" |
| **NOT in Phase 1** | `ko_KR`, `es_LA`, `hu_HU`, `zh_HK` localized variants | Implicit — only 4 locales listed |

---

## §3 — File layout (target)

```
brand-wizard-app/public/
  teacher_showcase.html           ← canonical en_US (already exists, 924 KB)
  teacher_showcase_ja.html        ← NEW for Phase 1
  teacher_showcase_zh_tw.html     ← NEW for Phase 1
  teacher_showcase_zh_cn.html     ← NEW for Phase 1
  assets/
    locale/
      teacher_showcase_strings.en_US.json   ← shared UI string registry (refactor)
      teacher_showcase_strings.ja_JP.json
      teacher_showcase_strings.zh_TW.json
      teacher_showcase_strings.zh_CN.json
      teacher_bios.en_US.json               ← per-teacher bio + tradition + focus
      teacher_bios.ja_JP.json
      teacher_bios.zh_TW.json
      teacher_bios.zh_CN.json
```

The 3 new HTML files are **structural clones** of `teacher_showcase.html` with:
- All UI labels swapped from English → locale strings (data-i18n driven, same pattern as existing `wizard-ja.html` / `wizard-tw.html`)
- All per-teacher bios + tradition + focus blocks swapped from `teacher_bios.{locale}.json`
- All asset paths unchanged (audio MP3s, manga panels, KDP covers, video reels — same files; en_US TTS is acceptable for Phase 1 listening)
- Top-nav language switcher links to the other 3 locale variants

### Naming convention

Use **lowercase locale code with underscore** (`teacher_showcase_zh_tw.html` not `teacher_showcase_zh-TW.html`) for filesystem hygiene + URL stability. Maps to BCP 47 in metadata only.

---

## §4 — Translation tier breakdown

### Tier 1 — UI labels (mandatory) — ~80 strings × 4 locales

Categories (all extracted from current `teacher_showcase.html`):
- Top nav labels (Pearl Prime, Markets, Teachers, Intro, Marketing, Dashboard, Matrix, Gallery, Brand Admin)
- Section toggle labels per teacher: "Formats", "Listen — Chapter 1", "Watch", "Read Manga", "Read Book (N words)", "Marketing Brief"
- Format card labels: Ebook, Audiobook, Manga, Podcast, Social
- Listen meta lines (CosyVoice2 voice descriptors)
- CTA buttons (added in PR-C): "Read Free Guide", "Get the Book", "Listen / Podcast"
- Triptych labels: Character Portrait, Teaching Scene, Brand Essence
- Misc microcopy (e.g. "click to play", "TikTok (90s)", "YouTube video — coming soon")

**Total: ~80 unique strings.**

### Tier 2 — Teacher bios (mandatory) — ~200 words × 13 teachers × 3 non-en locales = ~7,800 words

Per-teacher fields to translate (already in current HTML):
- `teacher-tradition` (1 line, e.g. "Theravada Buddhist")
- `teacher-focus` (1 sentence, e.g. "Meditation, mindfulness, inner peace")
- `teacher-stats` (1 line — locale flag stays language-specific; the rest is metadata)
- The "Note on the Teachings of {Name}" introductory paragraph block (~150 words per teacher inside the Read Book section header)

### Tier 3 — Full book chapters (OUT OF SCOPE for Phase 1)

The ~10K-word chapter content per teacher × 13 teachers × 3 non-en locales = ~390K words is explicitly excluded. The Read Book section in non-en variants displays:
1. Translated bio block (Tier 2)
2. A standardized notice: "📖 Full chapter content is currently available in English only. Click here to read in English." (link to `teacher_showcase.html#{teacher}_book`)

This avoids the largest translation cost while still delivering the rich product surface in the operator's stated 4 locales.

---

## §5 — Translation provider routing

Per [`CLAUDE.md` LLM Tier Policy](../CLAUDE.md):

| Tier | Source provider | Justification |
|---|---|---|
| Tier 1 (UI labels) | **Claude Code (Tier 1)** for hero strings; **Pearl Star Qwen3:14b** acceptable for direct CJK label translations | Operator-attended; ~80 strings is small enough for one Claude Code session |
| Tier 2 (bios) | **Pearl Star Qwen3:14b** (CJK6 only — ja/zh-TW/zh-CN are within scope per memory.md `[Qwen vs Pearl_Writer]`) | Tier-2 unattended pipeline; 7,800 words across 3 locales is well within Qwen3:14b throughput |
| Tier 3 (chapters) | n/a | Out of scope Phase 1 |

**Banned:** ElevenLabs (audio), DashScope/Anthropic/OpenAI cloud APIs (text). Per `CLAUDE.md` enforced by `.github/workflows/llm-policy-enforcement.yml`.

---

## §6 — Build + deploy implications

### Vite config update

`brand-wizard-app/vite.config.js` — extend `rollupOptions.input` to include the 3 new HTML files so they bundle into `dist/`:

```js
input: {
  ...existing,
  "teacher_showcase_ja":    resolve(__dirname, "public/teacher_showcase_ja.html"),
  "teacher_showcase_zh_tw": resolve(__dirname, "public/teacher_showcase_zh_tw.html"),
  "teacher_showcase_zh_cn": resolve(__dirname, "public/teacher_showcase_zh_cn.html"),
}
```

### Cloudflare Pages

No deploy-config changes needed — Wrangler ships everything in `dist/`. Per `wrangler.toml` the `bucket = "./dist"` already covers the new pages.

### Deploy size impact

Each locale variant is structurally identical to en_US (~924 KB but the 90% that's chapter HTML stays English in non-en variants per Tier 3 exclusion). Estimated per-locale variant size: **~150 KB** (just the localized header + bio + nav + CTA + structure shell + pointer back to en_US for chapters). Total Phase 1 deploy delta: **~450 KB**. Trivial.

---

## §7 — Per-teacher relevance (do all 13 appear in all 4 locales?)

**Decision: yes, all 13 in all 4.** Reasons:

- The catalog at [config/manga/canonical_brand_list.yaml](../config/manga/canonical_brand_list.yaml) targets all 37 brands (and by extension all 13 teachers) across all locales.
- Hiding teachers per locale would create per-locale "missing teacher" gaps that undermine the showcase's "13 teachers / 13 brands" framing.
- Some teachers have culturally Japanese names already (Joshin, Junko, Miki, Omote) — those translate naturally; the others (Ahjan, Pamela Fellows, etc.) keep romanized names with optional `data-jp` katakana/hiragana subtitle (already present in current HTML).

Cultural sensitivity check (defer to operator if any concern):
- `master_sha`, `master_wu`, `master_feung` — Chinese-tradition framing, fits zh-TW + zh-CN well
- `maat` — Egyptian framing, no specific cultural mismatch in any of the 4
- `ra` — African framing, no specific mismatch
- `adi_da` — sometimes controversial in Hindu/Buddhist contexts — operator may want to gate or rename in zh-CN; flag for operator review

---

## §8 — Acceptance criteria (for the future implementation PR)

When Pearl_Dev implements this spec:

1. ✅ 3 new HTML files exist and pass HTML-validity check
2. ✅ Each new file's `<html lang="...">` matches the locale (`ja`, `zh-Hant`, `zh-Hans`)
3. ✅ Top nav has language-switcher links to the other 3 locales (visible + functional)
4. ✅ All 80 Tier-1 UI strings translated (no English fallthrough in non-en variants except for explicit "available in English only" callouts)
5. ✅ All 13 teacher bios translated for each locale (52 bio strings translated total)
6. ✅ Vite `rollupOptions.input` includes the 3 new files
7. ✅ `npm run build` succeeds with new entries
8. ✅ Browser smoke test on each locale: page renders without console errors; portraits + audio + video all play; CTAs jump to correct anchors
9. ✅ Push-guard + preflight pass
10. ✅ NO `--admin` merge

---

## §9 — Phase 2 (out of scope, deferred)

After Phase 1 ships and is validated:
- Add `ko_KR`, `es_LA`, `hu_HU`, `zh_HK` variants
- Decide Tier 3 (full chapter translation) per locale
- Add audio voice variants (CosyVoice2 already supports `ja_female_warm`, `chinese_male`, `chinese_female`, `ko_female_gentle`)
- Locale-aware CTA destination URLs (per-locale Amazon storefront, etc.) — depends on real ASINs landing first

---

## §10 — What the implementation PR should NOT do

Per operator brief and #778 constraints:
- ❌ No content generation beyond translation of existing strings
- ❌ No LLM API calls to paid providers (banned per `CLAUDE.md`)
- ❌ No `--admin` merge
- ❌ No Cloudflare deploy without explicit operator approval
- ❌ No broad UI redesign — locale variants must be structural clones
- ❌ No Tier 3 (chapter content) translation in this phase
- ❌ No new teachers, no new brands, no new asset directories

---

## §11 — Companion docs

- [Issue #778](https://github.com/Ahjan108/phoenix_omega_v4.8/issues/778) — operator brief
- [artifacts/audits/teacher_page_requirements_audit_2026-04-28.md](../artifacts/audits/teacher_page_requirements_audit_2026-04-28.md) — original audit
- [docs/PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md](../docs/PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md) — book canonical (referenced for teacher-bio source-of-truth)
- [config/manga/canonical_brand_list.yaml](../config/manga/canonical_brand_list.yaml) — 37-brand registry
- [CLAUDE.md](../CLAUDE.md) §"LLM Tier Policy" — translation provider routing constraints
