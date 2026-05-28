# stillness_press ja_JP — Continuation Stub (Qwen / Tier 2)

**Status:** NOT STARTED IN THIS SESSION — by design, per CLAUDE.md LLM tier policy.

## Why this is a stub, not prose

The LLM tier policy (CLAUDE.md) is explicit:

> **ja_JP prose** (book text, manga scripts, podcast scripts): route through **Qwen on Pearl Star
> (Tier 2)** via the repo's CJK pipeline. Do **NOT** hand-write Japanese prose with Claude.

Claude (Pearl_Writer, Tier 1) wrote the **en_US** source deliverables in this build. Generating the
Japanese versions with Claude would be a **policy violation**. The ja_JP build is therefore queued
for the Qwen pipeline, which was **unreachable from this session** (Pearl Star is on the operator's
local LAN; `http://192.168.1.112:8188` and the Ollama host both timed out from here).

## The ja_JP build plan (run on Pearl Star LAN, operator-present or scheduled Tier 2)

Source = the committed en_US deliverables under
`artifacts/catalog/brand1_deep/stillness_press/en_US/`.

### Books (4 titles → ja_JP)

The book texts are plain-text with CHAPTER markers (consumed by `scripts/release/build_epub.py`).
Translate each via the CJK localization pipeline (Route 1: Claude meta-prompt already captured in
the en_US text; Qwen does the generation), then rebuild EPUBs with `--language ja`:

```bash
# Qwen on Pearl Star (Tier 2, free, unattended) — DashScope/Ollama backend
# Per scripts/localization/run_locale_batches.py (model defaults to qwen-plus / local qwen)
for slug in anxiety_gen_z_professionals sleep_anxiety_midlife_women \
            overthinking_millennial_women_professionals anxiety_tech_finance_burnout; do
  python3 scripts/localization/translate_atoms_to_locale.py \
    --locale ja_JP \
    --in  artifacts/catalog/brand1_deep/stillness_press/en_US/books/text/book_${slug}.txt \
    --out artifacts/catalog/brand1_deep/stillness_press/ja_JP/books/text/book_${slug}.ja.txt
  python3 scripts/release/build_epub.py \
    --input artifacts/catalog/brand1_deep/stillness_press/ja_JP/books/text/book_${slug}.ja.txt \
    --title "<ja title>" --subtitle "<ja subtitle>" --author "Ahjan" \
    --publisher "Stillness Press" --language ja --topic <topic> \
    --cover artifacts/catalog/brand1_deep/stillness_press/en_US/books/covers/cover_${slug}.png \
    --output artifacts/catalog/brand1_deep/stillness_press/ja_JP/books/epub/book_${slug}.ja.epub
done
```

**Note on the parser:** `build_epub.py:parse_book_text()` already recognizes Japanese chapter
markers (`第…章`, `教導縁起`, `深入修行`) — the Qwen output should use those headers so chapters
parse correctly. The PIL covers are locale-neutral imagery; Japanese title text would be
re-composited via `../en_US/books/make_covers.py` with a CJK font (Noto Sans JP — see
`.github/workflows/no-binary-blobs.yml` CJK-font note) and ja strings.

### Manga (3 series scripts → ja_JP)

The manga chapter scripts carry per-line text. Use the dedicated manga translator (Qwen default):

```bash
python3 scripts/manga/translate_chapter_script.py \
  --in artifacts/manga/chapter_scripts/stillness_press__ahjan__*/ep_001.yaml \
  --target-locales ja_JP
# (backend defaults to Qwen on Pearl Star Ollama — Tier 2, free)
```

For series 1, the 35 rendered panels are language-agnostic art; only the lettering layer
(`text_by_locale` / `narrator_caption_by_locale` / `sfx_by_locale`) is re-translated, then
re-lettered. Per the series plan, ja cadence is **bi-weekly** (vs weekly en) for webtoon.

### Podcast (3 scripts → ja_JP)

Translate the 3 episode scripts via the same Qwen path, then render audio with a Japanese TTS
voice (Edge TTS `ja-JP-NanamiNeural` free tier, or local CosyVoice2 — NOT ElevenLabs, key is 401).

## Acceptance gate for ja_JP

ja_JP is "done" when: 4 ja EPUBs pass `validate_epub.py`, 3 manga scripts have populated
`*_by_locale[ja_JP]`, 3 podcast scripts translated + audio rendered — all via Qwen/Pearl Star,
**zero Claude-authored Japanese prose**, zero paid-API spend (`python3 scripts/ci/audit_llm_callers.py`
clean).
