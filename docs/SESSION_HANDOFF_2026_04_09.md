# Session Handoff — 2026-04-09

**Agents:** Pearl_PM + Pearl_Architect + Pearl_GitHub + Pearl_Dev
**Duration:** Full day session (14+ hours)
**Worktree:** nice-shaw
**Git user:** Nihala (Ma'at)

---

## PRs Merged (9)

| PR | Title | Files | Key Change |
|----|-------|-------|------------|
| #298 | Exercise template expansion (4→12) + PipelineView teacher fields | 6 | 2,985,984 combos/category. Restored overlay craft rule. Fixed flow gate cues. |
| #299 | Ubuntu production server setup reference | 1 | Pearl Star server docs |
| #301 | Close content inventory + brand lane architecture workstreams | 1 | ACTIVE_WORKSTREAMS.tsv updated |
| #302 | Wire Pearl Star server as default provider | 12 | ComfyUI image backend, Ollama LLM, CosyVoice2 TTS. Provider chain: local→cloud→free. |
| #303 | Full content production catalog — 37 brands, manga mode split | 7 | 13 illustration styles + 24 standard brands. 87 series. 50 LoRAs. CJK translation queue. Build order. |
| #304 | Voice system — CosyVoice2 + scoring matrix + 92 brand-locale voices | 10 | 3 profiles × 15 topics × 48 personas. 159 zh-TW templates. Locale voice routing. |
| #305 | Two-pass bestseller cover system + 13 teacher covers | 14 | FLUX background + PIL typography. Research-backed: title 50-70% visual weight. |
| #306 | Teacher showcase — video, audio, manga, covers + HTML wiring | 85 | 26 videos, 26 audio, 39 manga views, 14 audiobook covers. All wired into teacher_showcase.html. |

## PRs Open (1)

| PR | Title | Status | What's Left |
|----|-------|--------|-------------|
| #307 | Locale-native book assembly — --locale flag for CJK pipeline | 6 commits, +1601/-49 | Translation running (330/5183 zh-TW atoms). Merge after translation completes or merge code now, translate separately. |

---

## Major Systems Built/Changed

### 1. Pearl Star Server — Fully Operational
- **IP:** 192.168.1.112 (LAN)
- **SSH:** `ssh pearl_star` (user: ahjan108, key: ~/.ssh/id_ed25519_pearl_star)
- **Services:** ComfyUI :8188, Ollama :11434, CosyVoice2 :9880, SSH :22
- **GPU:** RTX 5070 Ti (16 GB VRAM)
- **Model:** qwen2.5:14b (qwen3:14b and qwen3.5:9b REMOVED — thinking overhead)
- **Keychain:** PEARL_STAR_IP, COMFYUI_URL, COSYVOICE_URL, QWEN_BASE_URL all set

### 2. Provider Migration Complete (PR #302)
| Service | Old Default | New Default | Fallback |
|---------|-------------|-------------|----------|
| Image gen | RunComfy cloud | ComfyUI @ pearl_star:8188 | RunComfy |
| CJK LLM | DashScope cloud | Ollama/qwen2.5:14b @ pearl_star:11434 | DashScope → LM Studio |
| CJK TTS | ElevenLabs | CosyVoice2 @ pearl_star:9880 | Edge-TTS → ElevenLabs |
| EN TTS | ElevenLabs | ElevenLabs (no change) | Edge-TTS |

### 3. Locale-Native Pipeline (PR #307)
- `--locale zh-TW` flag on run_pipeline.py
- Atom resolution: `locales/{locale}/CANONICAL.txt` → English fallback
- Teacher bank loading: locale-aware `_load_teacher_prose()`
- Exercise templates: `config/pearl_practice/locales/zh-TW/component_templates.yaml` (359 strings)
- Pipeline templates: `config/localization/pipeline_templates_zh_TW.yaml` (222 strings)
- chapter_composer.py: `_pick_variant()` auto-translates via `_gt(locale)`
- book_renderer.py: post-processing `localize_rendered_text()` pass
- **Result:** zh-TW book = 33% Chinese (up from 0%). Remaining 67% needs atom translation.

### 4. Content Production Catalog (PR #303)
- 37 brands (13 teacher + 24 standard) × 12 lanes = 444 brand instances
- Manga mode: teacher brands have 1 teacher/student series; standard brands all regular
- 87 series in heavy lanes, 50 LoRAs planned, ~70K manga panels estimated
- Build order: LoRA → Covers → CJK Translation → Manga → Video → TTS

### 5. Voice System (PR #304)
- 92 brand-locale voice assignments (EN ElevenLabs + CJK CosyVoice2)
- Voice-persona-topic scoring matrix (3 profiles × 15 topics × 48 personas)
- 7 CosyVoice2 built-in voices + 11 cloned archetypes planned
- Locale voice routing: CJK → cosyvoice2 → edge_tts → elevenlabs

### 6. Teacher Showcase (PR #306)
- 105 assets generated: 26 videos, 26 audio, 39 manga views, 14 audiobook covers
- All wired into teacher_showcase.html with playable `<video>` and `<audio>` tags
- Videos/audio gitignored (389 MB) — regenerate via scripts
- Deployed to: https://a339ad77.phoenix-command.pages.dev/teacher_showcase.html

### 7. Bestseller Cover System (PR #305)
- Two-pass: FLUX background (no text) + PIL typography overlay
- 13 teacher covers + 1 adi_da cover = 14 total
- Filenames match teacher_select.html references exactly
- Size reduction: 12.8 MB → 0.9 MB (93% smaller)

---

## Background Processes

### zh-TW Atom Translation
- **Status:** STOPPED (killed to free GPU for ComfyUI)
- **Progress:** 330/5,183 atoms translated (~6.4%)
- **Model:** qwen2.5:14b on Pearl Star (no thinking overhead, ~3s/atom)
- **Resume:** `PYTHONPATH=. python3 -u scripts/localization/translate_atoms_to_locale.py --locale zh-TW --workers 4 --model qwen2.5:14b`
- **ETA:** ~12 hours for remaining 4,853 atoms at ~4/min
- **Note:** Cannot run simultaneously with ComfyUI (GPU memory conflict)

---

## Naughty-Banzai Evaluation (completed)

Session handoff 2026-04-07 evaluated. 13 deliverables:
- 8 LANDED, 1 SUPERSEDED (presenter.html), 1 LANDED with minor gap
- 3 GAP — LOST (light-theme spine HTML, i18n additions, briefing audio were never committed)
- Naughty-banzai branch: ARCHIVE (no unique promotable content remains)

---

## Files Created This Session

### New Scripts (7)
| Path | Purpose |
|------|---------|
| scripts/image_generation/generate_bestseller_covers.py | Two-pass cover generator (FLUX bg + PIL typography) |
| scripts/image_generation/generate_manga_character_views.py | 3-view manga character portraits (placeholder/ComfyUI) |
| scripts/audio/generate_teacher_showcase_audio.py | Edge-TTS narration from book text (full + hook) |
| scripts/video/generate_teacher_showcase_videos.py | FFmpeg Descript-style videos (YouTube 10min + TikTok 90s) |
| scripts/localization/translate_atoms_to_locale.py | Batch atom translation via Ollama (parallel, resumable) |
| phoenix_v4/rendering/locale_templates.py | Pipeline template loader (get_template, localize_rendered_text) |
| (modified) scripts/localization/translate_atoms_to_locale.py | Updated: qwen2.5:14b, /api/generate endpoint, 4 workers |

### New Configs (12)
| Path | Contents |
|------|----------|
| config/manga/brand_illustration_styles.yaml | 37 unique illustration styles |
| config/manga/brand_lora_plans.yaml | 13 character + 37 style LoRAs |
| config/catalog_planning/brand_series_plans.yaml | 87 series (manga mode: teacher/regular) |
| config/catalog_planning/brand_cover_art_specs.yaml | 37 brands × 4 cover formats |
| config/video/brand_video_styles.yaml | 37 brand video identities |
| config/tts/voice_persona_topic_scores.yaml | 3 profiles × 15 topics × 48 personas |
| config/tts/cosyvoice_reference_audio_plan.yaml | 7 built-in + 11 cloned voice archetypes |
| config/tts/locale_voice_routing.yaml | CJK/EN provider chains per locale |
| config/tts/brand_narrator_voice_map.yaml | 92 brand-locale voice assignments |
| config/localization/pipeline_templates_zh_TW.yaml | 222 translated pipeline strings |
| config/pearl_practice/locales/zh-TW/component_templates.yaml | 359 translated exercise strings |
| (multiple) atoms/gen_z_student/anxiety/*/locales/zh-TW/CANONICAL.txt | 11 translated atom files |

### New Docs (5)
| Path | Contents |
|------|----------|
| docs/CJK_ATOM_TRANSLATION_QUEUE.md | Priority queue: ja→ko→zh-CN→zh-TW/HK/SG |
| docs/CONTENT_BANK_BUILD_ORDER.md | 6-phase build: LoRA→Covers→Translation→Manga→Video→TTS |
| docs/VOICE_PERSONA_TOPIC_RESEARCH.md | Voice psychology, CJK cultural preferences, CosyVoice2 assessment |
| docs/SESSION_HANDOFF_2026_04_09.md | This file |
| (modified) docs/INTEGRATION_CREDENTIALS_REGISTRY.md | Pearl Star section + SSH details + hardware |

### Generated Assets (not in git — regenerate via scripts)
| Type | Count | Location | Regenerate |
|------|-------|----------|------------|
| Teacher covers (KDP) | 14 | brand-wizard-app/public/assets/covers/ | `python3 scripts/image_generation/generate_bestseller_covers.py` |
| Audiobook covers (square) | 14 | brand-wizard-app/public/assets/covers/audiobook/ | `--format audiobook_square` |
| Manga character views | 39 | brand-wizard-app/public/assets/manga_covers/ | `python3 scripts/image_generation/generate_manga_character_views.py` |
| YouTube videos (10min) | 13 | artifacts/showcase/video/youtube/ | `python3 scripts/video/generate_teacher_showcase_videos.py` |
| TikTok videos (90s) | 13 | artifacts/showcase/video/tiktok/ + brand-wizard-app/public/assets/video/tiktok/ | same script |
| Audio narration (full) | 13 | artifacts/showcase/audio/ | `python3 scripts/audio/generate_teacher_showcase_audio.py` |
| Audio narration (hook) | 13 | brand-wizard-app/public/assets/audio/showcase/ | same script |
| zh-TW test books | 2 | artifacts/rendered/ba658dc0a8debfc34c4908e702ba3771/ + 660a6ffe3e72d1324a2e84b41c1ecd3c/ | run_pipeline.py with --locale zh-TW |

---

## Pre-Existing Issues (unchanged from session start)

| Issue | Status | Notes |
|-------|--------|-------|
| test_marketing_validator: gen_z_student persona not in validator | Pre-existing on main | Not in scope |
| test_resolver_allows_universal_story: API mismatch (teacher_story_fallback) | Pre-existing on main | Not in scope |
| change-impact.yml workflow broken | Broken on all branches | Workflow file issue, not code |
| Atom content gaps: 45 missing STORY, 15 missing non-STORY | Pre-existing | Content authoring needed |
| 9/13 teacher brands still skeleton (need P1 author expansion) | Pre-existing | Author onboarding needed |

---

## Queued Prompts (ready to paste into next session)

Owner has 5 prompts prepared for future sessions:

1. **Pearl_Prez + Pearl_Research:** Brand admin HTML redesign (interactive, page-by-page with owner feedback)
2. **Pearl_PM + Pearl_Dev:** Full catalog generation (12 markets × 37 brands) + assembly + bestseller analysis
3. **Pearl_Research:** Global podcast market research (12 markets) + podcast format design
4. **Pearl_Dev:** English master TXT extraction (every pipeline string for TTS recording)
5. **(Ongoing):** Resume zh-TW atom translation when GPU available

---

## Key Decisions Made This Session

1. **Pearl Star is primary provider** — cloud APIs are fallbacks only
2. **qwen2.5:14b replaces qwen3:14b** — thinking mode makes qwen3 unusable for batch translation (33s vs 2.7s per call)
3. **Manga mode split** — teacher brands have 1 teacher/student series; standard brands all regular
4. **Two-pass covers** — never put text in FLUX prompt; PIL overlay handles typography
5. **CosyVoice2 for CJK TTS** — but Gradio API (not REST), needs wrapper for programmatic use
6. **Edge-TTS for showcase narration** — free, fast, good EN quality; CosyVoice2 for CJK production
7. **Videos/audio gitignored** — too large for git; scripts are reproducible
8. **Locale post-processing** — template string replacement after chapter composition (pragmatic vs full refactor)

---

## Recovery Commands

```bash
# Load all env vars
eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"

# Verify Pearl Star
ssh pearl_star "hostname && ollama list && ss -tlnp | grep -E '8188|9880|11434'"

# Resume zh-TW translation (STOP ComfyUI first if GPU needed)
PYTHONPATH=. python3 -u scripts/localization/translate_atoms_to_locale.py --locale zh-TW --workers 4 --model qwen2.5:14b

# Regenerate teacher covers
PYTHONPATH=. python3 scripts/image_generation/generate_bestseller_covers.py --mode gradient

# Regenerate showcase videos
PYTHONPATH=. python3 scripts/video/generate_teacher_showcase_videos.py

# Assemble EN book
PYTHONPATH=. python3 scripts/run_pipeline.py --topic anxiety --persona gen_z_student --teacher adi_da --arc config/source_of_truth/master_arcs/corporate_managers__anxiety__spiral__F006.yaml --quality-profile draft --skip-quality-gates --render-book

# Assemble zh-TW book
# (same as above + --locale zh-TW)

# Run content inventory scanner
PYTHONPATH=. python3 scripts/inventory/scan_content_inventory.py

# Check push-guard
PYTHONPATH=. python3 scripts/git/push_guard.py
```
