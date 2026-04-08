# Content Bank Build Order

**Owner:** Pearl_PM
**Last updated:** 2026-04-08
**Infrastructure:** Pearl Star server (192.168.1.112) — ComfyUI :8188, Ollama :11434, CosyVoice2 :9880

## Current State

| Asset Type | Configured | Built | Coverage |
|-----------|------------|-------|----------|
| book_text | 7,923 | 12 | 0.15% |
| epub | 7,923 | 11 | 0.14% |
| cover | 7,923 | 0 | 0% |
| manga_cover | ~663 | 0 | 0% |
| manga_panels | ~69,704 | 0 | 0% |
| video_rendered | ~484,503 | 0 | 0% |
| audio_presenter | ~230 decks | 0 | 0% |
| atoms_canonical | 4,531 EN | 4,531 EN | 100% EN / 4.7% CJK |

## Phased Build Order

### Phase 0: LoRA Training (prerequisite for all visual content)

**Duration:** ~2-3 days
**Server:** Pearl Star ComfyUI

| Task | Count | Estimated Time |
|------|-------|---------------|
| Teacher character LoRAs | 13 | ~1.5h each = ~20h |
| Brand style LoRAs (teacher) | 13 | ~2h each = ~26h |
| Brand style LoRAs (standard) | 24 | ~2h each = ~48h |
| Validation (20 test images each) | 50 × 20 = 1,000 | ~8h |
| **Total** | **50 LoRAs** | **~102h (4-5 days)** |

Config: `config/manga/brand_lora_plans.yaml`
Output: `~/content_bank/loras/{brand_id}/`

Validation: Same character recognizable across cover, manga panel, video thumbnail, social post (CLIP face similarity > 0.85).

### Phase 1: Covers (unblocks catalog listings)

**Duration:** ~3-4 days
**Server:** Pearl Star ComfyUI
**Dependency:** Phase 0 (LoRAs)

| Task | Count | Estimated Time |
|------|-------|---------------|
| Base covers (37 brands × 4 formats) | 148 | ~24h |
| Locale variants (12 lanes) | ~1,776 | ~290h |
| Manga series covers | 87 | ~14h |
| **Total** | **~1,863 covers** | **~328h (~14 days)** |

Config: `config/catalog_planning/brand_cover_art_specs.yaml`
CLI: `scripts/image_generation/runcomfy_batch.py --backend comfyui`

### Phase 2: CJK Atom Translation (unblocks CJK book production)

**Duration:** ~60h total (~2.5 days continuous)
**Server:** Pearl Star Ollama (Qwen3:14b)
**Dependency:** None (can run in parallel with Phase 1)

| Locale | Atoms | Est. Time |
|--------|-------|-----------|
| ja-JP | 4,531 | ~10h |
| ko-KR | 4,531 | ~10h |
| zh-CN | 4,531 | ~10h |
| zh-TW | 4,531 | ~10h |
| zh-HK | 4,531 | ~10h |
| zh-SG | 4,531 | ~10h |
| **Total** | **~25,912** | **~60h** |

Config: `config/localization/translation_loop_config.yaml`
Queue: `docs/CJK_ATOM_TRANSLATION_QUEUE.md`
CLI: `scripts/localization/translate_atoms_all_locales.py`

### Phase 3: Manga Assets (manga-heavy lanes)

**Duration:** ~30 days
**Server:** Pearl Star ComfyUI
**Dependency:** Phase 0 (LoRAs) + Phase 2 (CJK atoms for text)

Build order by lane:
1. **Japan** (highest manga market value)
2. **Korea** (webtoon native format)
3. **France** (bande dessinée tradition)
4. **China/Taiwan** (manhua market)

| Task | Per Brand | Total (13 brands × 5 heavy lanes) |
|------|-----------|------------------------------------|
| Character sheets | 4 poses | 260 images |
| Series A panels | ~460 | ~29,900 |
| Series B panels | ~340 | ~22,100 |
| Series C panels | ~140 | ~9,100 |
| Webtoon assembly | per episode | ~280 episodes |
| **Total heavy** | | **~61,360 panels** |

Medium lanes (3): ~10,764 panels
Light lanes (5): ~390 key visuals

Config: `config/catalog_planning/brand_series_plans.yaml`
CLI: `scripts/release/build_manga_webtoon.py`

### Phase 4: Video Bank (all lanes)

**Duration:** ~5 days
**Server:** Pearl Star ComfyUI + FFmpeg
**Dependency:** Phase 0 (LoRAs for brand-consistent thumbnails)

| Task | Count | Estimated Time |
|------|-------|---------------|
| Topic × intent backgrounds | 90 base images | ~15h |
| Brand color grading | 90 × 13 = 1,170 | ~48h |
| Audiobook video renders | per book × 61 videos | continuous |
| **Total base images** | **~1,260** | **~63h (~3 days)** |

Audiobook video production (per book: 20 long + 40 short + 1 full = 61 videos):
- Phase 1 target: 354 books × 61 = 21,594 videos (en_US)
- Ongoing: continuous pipeline as books complete

Config: `config/video/brand_video_styles.yaml`, `config/video/brand_style_tokens.yaml`
CLI: `scripts/video/render_videos.py`, `scripts/video/orchestrate_book_to_video.py`

### Phase 5: CJK TTS Audio (zh/ja/ko audiobook narration)

**Duration:** ~10 days
**Server:** Pearl Star CosyVoice2 + Edge-TTS fallback
**Dependency:** Phase 2 (CJK atoms/text must exist)

| Locale | Books (est.) | Audio Hours |
|--------|-------------|-------------|
| ja-JP | 354 | ~2,000h narration |
| ko-KR | 354 | ~2,000h narration |
| zh-CN | 354 | ~2,000h narration |
| zh-TW/HK/SG | 354 each | ~6,000h narration |
| **Total** | | **~12,000h audio** |

Provider chain: CosyVoice2 (primary for CJK) → Edge-TTS (fallback) → ElevenLabs (final fallback)
EN/FR/DE/ES/PT: ElevenLabs (unchanged)

Config: `config/tts/engines.yaml`, `config/video/multilang_config.yaml`

### Phase 6: Presenter Audio (remaining decks)

**Duration:** ~2 days
**Server:** Pearl Star CosyVoice2 + ElevenLabs
**Dependency:** None

| Deck | Provider | Segments |
|------|----------|----------|
| briefing_jp | CosyVoice2 | ~20 |
| briefing_kr | CosyVoice2 | ~20 |
| briefing_cn | CosyVoice2 | ~20 |
| briefing_tw | CosyVoice2 | ~20 |
| intro | ElevenLabs | ~15 |
| briefing_fr | ElevenLabs | ~20 |
| briefing_de | ElevenLabs | ~20 |
| marketing | ElevenLabs | ~15 |

CLI: `scripts/audio/generate_presenter_audio.py`

## Parallelism

Phases that can run simultaneously on Pearl Star:

| GPU (ComfyUI) | CPU (Ollama) | CPU (CosyVoice2) |
|---------------|-------------|-------------------|
| Phase 0: LoRA training | Phase 2: CJK translation | — |
| Phase 1: Covers | Phase 2 (continued) | — |
| Phase 3: Manga panels | — | Phase 5: CJK TTS |
| Phase 4: Video bank | — | Phase 6: Presenter audio |

Optimal timeline: ~50-60 days with full parallelism (37 brands vs original 13).

## Brand Counts (37 total)
- 13 teacher brands (manga_mode: teacher, 1 teacher/student series each)
- 24 standard brands (manga_mode: regular, no teacher figure)
- Heavy lanes: teacher 3 series + standard 2 series = 87 total series
- Total LoRAs: 50 (13 character + 37 style)

## Monitoring

After each phase, run:
```bash
python3 scripts/inventory/scan_content_inventory.py
```
Check coverage via:
- Web: brand-wizard-app/public/content_inventory.html
- macOS: Phoenix Control → Content inventory
- JSON: artifacts/inventory/content_inventory.json
