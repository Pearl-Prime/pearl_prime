# HANDOFF — Pearl Star Image Pipeline + Manga Author/Cover Art Canonical (2026-05-04)

**Session date:** 2026-05-04
**Operator:** Nihala (Ma'at)
**Branch:** `agent/kind-swanson-c0deed` (worktree)
**Outcome:** Pearl Star ComfyUI wired as canonical default for ALL image generation. Old manga-author + cover-art system retired. 377 FLUX images shipped. Pearl Books catalog dashboard built.

---

## TL;DR — What changed and why it matters

1. **Pearl Star ComfyUI is now the canonical image-gen backend for Phoenix Omega.** Every "make an image / cover / manga panel" request auto-routes through Pearl Star on the Tailscale URL. Free, owned hardware. RunComfy / Cloudflare Workers AI are now fallback-only.
2. **The OLD manga-author + cover-art system is fully retired.** EI character-authors (in `config/authoring/manga_authors/`) are the only canonical manga author system. Cover art uses the two-stage pattern (FLUX bg + PIL typography) — no more pre-generated static base PNGs.
3. **Pearl Books dashboard built.** 25 brands × 1,228 series × cover/description/marketing/EI-author per book, browsable in one HTML page.
4. **377 FLUX images generated this session.** US Brand 1 (stillness_press) and JP Brand 1 (warrior_calm) are at 100% cover coverage; warrior_calm now has its own image bank for the first time.

---

## 1. The new canonical recipe — image generation

**Authority:** [`docs/PEARL_STAR_IMAGE_GENERATION_PROTOCOL.md`](./PEARL_STAR_IMAGE_GENERATION_PROTOCOL.md)
**Operational entry:** [`skills/pearl-image/SKILL.md`](../skills/pearl-image/SKILL.md)
**Sister agent for installs/restarts:** [`skills/pearl-int/SKILL.md`](../skills/pearl-int/SKILL.md)

### Hard defaults (NEVER deviate without explicit operator instruction)

| Setting | Value |
|---|---|
| **Endpoint** | `http://pearlstar.tail7fd910.ts.net:8188` (Tailscale, FREE) |
| **Checkpoint** | `flux1-schnell-fp8.safetensors` |
| **Workflow (preferred)** | `scripts/image_generation/comfyui_workflows/flux_video_bank.json` (already targets schnell) |
| **Backend (preferred)** | `scripts/video/flux_client.py` `call_comfyui()` |
| **Cover pattern** | Two-stage: FLUX renders imagery, PIL composites text |
| **Retry policy** | 3× with 5/10/15s backoff for batches >10 calls |
| **Cost** | FREE (owned hardware) |

### Trigger phrases (auto-route to Pearl_Image)

"make an image", "generate a cover", "render a manga panel", "do the pics", "build the image bank", "create cover art", "ComfyUI", "FLUX", "Pearl Star", or any mention of book/manga/KDP cover work.

### Banned behaviors

- ❌ Never call paid cloud (RunComfy, Cloudflare Workers AI, Replicate) when Pearl Star is reachable.
- ❌ Never put title / author / subtitle text in the FLUX prompt — typography is composited via PIL after.
- ❌ Never use `192.168.1.112` from outside the LAN — always Tailscale.
- ❌ Never accept gradient placeholders as "done" when FLUX is the requested deliverable.
- ❌ Never silently fall back to gradient on FLUX failure — log, retry 3×, then escalate.

### Standard launch shape

```bash
cd /Users/ahjan/phoenix_omega/.claude/worktrees/kind-swanson-c0deed
export PYTHONPATH=.
export COMFYUI_URL="http://pearlstar.tail7fd910.ts.net:8188"
nohup env PYTHONPATH=. COMFYUI_URL="$COMFYUI_URL" \
    python3 -u scripts/image_generation/<generator>.py --mode comfyui \
    > /tmp/<generator_name>.log 2>&1 &
```

---

## 2. The new canonical — manga authors & cover art

**Authority:** [`specs/MANGA_AUTHOR_AND_COVER_ART_CANONICAL_SPEC.md`](../specs/MANGA_AUTHOR_AND_COVER_ART_CANONICAL_SPEC.md)
**Schema:** `config/authoring/manga_authors/schema.yaml`
**Authors directory:** `config/authoring/manga_authors/<author_id>.yaml`
**Companions:**
- `docs/CHARACTER_INDIVIDUATION_PIPELINE_SPEC_2026-05-02.md` — 12-axis protagonist vocabulary
- `docs/CHARACTER_INDIVIDUATION_PROMPT_ALGORITHM_2026-05-03.md` — token budgets

### Core principle (from the schema, verbatim)

> Manga authors are EI (Enlightened Intelligence) character-authors. They are NOT pen name authors (`pen_name_teacher_profiles.yaml`). Each manga author IS a character in the genre world. **EI authorship is a feature: full disclosure, positioned as novel/transparent.**

### Author profile required fields

| Field | Purpose |
|---|---|
| `author_id` | snake_case unique (e.g. `hana_tidecalm_en_us_001`) |
| `display_name` | Locale-aware (e.g. "Hana Tidecalm" / "月影 靜") |
| `genre_tie_in` | iyashikei / seinen / shonen / shojo / josei / sports / horror / slice_of_life / cultivation / manhwa_psychological / webtoon_romance / isekai |
| `ei_disclosure_text` | Full disclosure, locale-appropriate. Must contain "AI / enlightened intelligence" concept. |
| `brand_id` | From `config/manga/canonical_brand_list.yaml` |
| `target_demographic` | Persona demographic (e.g. `anxious_millennials_urban`) |
| `visual_style_notes` | How signature maps to brand visual DNA |
| `bio_blurb` | 2-4 sentence character bio in locale language |

### Cover art rule (architectural, operator-set)

> **FLUX renders imagery only. PIL composites text. Every cover is unique imagery — no shared base PNGs.**

`scripts/image_generation/generate_bestseller_covers.py` is the reference two-stage implementation.

### Pen-name audiobook system — kept, scoped

`config/authoring/pen_name_teacher_profiles.yaml` and `docs/PEN_NAME_AUTHOR_SYSTEM.md` are **NOT** retired. They govern the **audiobook** pipeline, a different domain. They are also consulted by `scripts/manga/generate_manga_author.py` for `display_name` collision detection.

---

## 3. What was deleted (operator-approved cleanup)

**Total: 34 files** (9 source-controlled + 25 binary PNGs).

| Path | Why old |
|---|---|
| `specs/archive/MANGA_AUTHOR_SYSTEM_SPEC.md` | Pre-EI manga author spec |
| `specs/archive/MANGA_MODE_SYSTEM_SPEC.md` | Pre-EI manga mode wrapper |
| `specs/archive/DEFERRED_2026_04_26.md` | Defunct backlog of old specs |
| `docs/authoring/AUTHOR_COVER_ART_SYSTEM.md` | Static-base-PNG cover art doc |
| `config/authoring/author_cover_art_registry.yaml` | Registry for static base PNGs |
| `scripts/generate_author_cover_art_bases.py` | Pure-zlib gradient placeholder |
| `scripts/generate_author_cover_art_flux.py` | Cloudflare Workers AI (paid) |
| `scripts/ci/check_author_cover_art.py` | CI checker for old registry |
| `phoenix_v4/planning/author_cover_art_resolver.py` | Runtime resolver for old registry |
| `assets/authors/cover_art/*.png` (15) | Pre-generated base PNGs (10 teachers) |
| `assets/authors/cover_art/_legacy_gradients_2026-03-05/*.png` (10) | Earlier gradient bases |

**Patched:** `scripts/image_generation/image_qc.py` no longer references the deleted registry. It now reads:
- Legacy `config/author_registry.yaml` (if present)
- `config/authoring/pen_name_teacher_profiles.yaml` (audiobook authors)
- `config/authoring/manga_authors/*.yaml` (NEW EI character-authors)

Verified imports cleanly with `python3 -c "from scripts.image_generation import image_qc"`.

---

## 4. Files added this session

### Specs / docs (canonical authority)

| File | Purpose |
|---|---|
| `docs/PEARL_STAR_IMAGE_GENERATION_PROTOCOL.md` | Canonical image-gen recipe (Pearl Star, two-stage, retry, fallback ladder) |
| `specs/MANGA_AUTHOR_AND_COVER_ART_CANONICAL_SPEC.md` | Single source of truth for manga authors + cover art |
| `skills/pearl-image/SKILL.md` | Operational entry skill (auto-loads on trigger phrases) |
| `docs/HANDOFF_PEARL_STAR_IMAGE_PIPELINE_2026-05-04.md` | This handoff |

### Code (generators, dashboard, templates)

| File | Purpose |
|---|---|
| `scripts/dashboards/build_pearl_books_dashboard.py` | Builds the Pearl Books HTML dashboard |
| `/tmp/upgrade_per_series_covers_to_flux.py` | Per-series cover background upgrade (gradient → FLUX bg + retain PIL typography). 3× retry. Reference template for any brand. |
| `/tmp/generate_warrior_calm_image_bank.py` | warrior_calm image bank generator (61 assets). Reference template for any brand. |
| `/tmp/generate_warrior_calm_covers.py` | Warrior_calm gradient covers (replaced by FLUX upgrade) |

### Files patched

| File | Change |
|---|---|
| `CLAUDE.md` | Added "Image Generation — ALWAYS Pearl Star ComfyUI" section after Read First |
| `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` | §0 Tailscale URL canonicalized; checkpoint truth recorded |
| `docs/DOCS_INDEX.md` | Task table entry for "Generate any image / cover / manga panel" |
| `scripts/image_generation/generate_teacher_showcase_triptych.py` | `DEFAULT_COMFY_URL` → Tailscale; `DEFAULT_CHECKPOINT` constant added |
| `scripts/image_generation/generate_bestseller_covers.py` | Env fallback to Tailscale (was empty) |
| `scripts/image_generation/generate_kdp_all_formats.py` | Env fallback to Tailscale (was 192.168.1.112) |
| `scripts/image_generation/generate_brand_wizard_visual_proof.py` | Env fallback to Tailscale; docstring URLs updated |
| `scripts/image_generation/image_qc.py` | Read EI authors from `manga_authors/` instead of deleted registry |

---

## 5. Images generated this session (377 total FLUX, all on Pearl Star)

| Generator | Output | Count | Avg size |
|---|---|---|---|
| `generate_teacher_showcase_triptych.py` | `brand-wizard-app/public/assets/manga_covers/<teacher>_{portrait,scene,symbolic}.png` | 39 | ~700 KB |
| `generate_bestseller_covers.py` | `brand-wizard-app/public/assets/covers/cover_<teacher>_<topic>.png` | 13 | ~1.7 MB |
| `generate_kdp_all_formats.py` | `brand-wizard-app/public/assets/covers/kdp/<teacher>_<format>.png` | 51 (+1 outlier) | ~1-12 MB |
| `generate_warrior_calm_image_bank.py` (template) | `artifacts/manga/image_bank/warrior_calm/<category>/...` | 61 | ~1.58 MB |
| `upgrade_per_series_covers_to_flux.py` (template) | per-series `cover.png` (157 stillness_press + 56 warrior_calm) | 213 | stillness ~2.2 MB / warrior ~5.5 MB |

### End-state coverage for US + JP brand 1

| Layer | stillness_press (US Brand 1) | warrior_calm (JP Brand 1) |
|---|---|---|
| `main_character.png` | 157/157 | 56/56 |
| `cover.png` (FLUX) | **157/157 ✅** | **56/56 ✅** |
| image_bank assets | 116 (en_US) | **61 (ja_JP) — NEW this session** |

### One outlier

- `brand-wizard-app/public/assets/covers/kdp/master_sha_podcast.png` — 244 KB (gradient fallback, FLUX failed twice). Re-run when Pearl Star queue is fully idle.

---

## 6. Pearl Books dashboard

**Path:** `/Users/ahjan/phoenix_omega/qa_books_2026-05-04/pearl_books_dashboard.html` (HTML) + `pearl_books_dashboard.json` (manifest sidecar)

**Re-run anytime:** `python3 scripts/dashboards/build_pearl_books_dashboard.py`

**Open:** `open /Users/ahjan/phoenix_omega/qa_books_2026-05-04/pearl_books_dashboard.html`

### What it shows

- **Top header:** total brands, total series, cover coverage %, FLUX %, EI author count.
- **TOC chips:** quick-jump to each brand.
- **Per-brand section:**
  - Tier badge (flagship / core / niche), demographic, primary topic, brand notes
  - Stats row: series count, covers, FLUX-quality, main_character coverage
  - **EI Character-Authors panel** — display names, locales, genre tie-ins
  - **Locale filter buttons** (per-brand)
  - **Book grid** — one card per series:
    - Cover thumbnail (with FLUX/placeholder/missing badge)
    - Title, locale, genre, teacher
    - Reader promise (italic, bordered)
    - Marketing angle
    - Description fallback if no promise
    - EI author display name footer

### Current state (2026-05-04)

| Metric | Value |
|---|---|
| Brands tracked | 25 |
| Total series | 1,228 |
| Series with `main_character.png` | 1,228 (100%) |
| Series with `cover.png` | 213 (17%) |
| Series with FLUX-quality cover | 213 (17%) |
| Registered EI character-authors | 6 |

The 17% cover coverage = stillness_press (157) + warrior_calm (56). The other 23 brands have main_character but no cover yet.

---

## 7. Pearl Star ops cheat sheet (Pearl_Int territory)

### Health check
```bash
curl -s --max-time 10 "http://pearlstar.tail7fd910.ts.net:8188/system_stats" | head -c 200
curl -s --max-time 10 "http://pearlstar.tail7fd910.ts.net:8188/queue" | python3 -c "import json,sys; d=json.load(sys.stdin); print('running', len(d['queue_running']), 'pending', len(d['queue_pending']))"
```

### SSH access
```bash
ssh pearl_star "hostname"
# user: ahjan108, key: ~/.ssh/id_ed25519_pearl_star
```

### Restart ComfyUI
```bash
ssh pearl_star "sudo systemctl restart comfyui.service && sleep 8 && \
  curl -s http://localhost:8188/system_stats | head -c 200"
```

### View logs
```bash
ssh pearl_star "sudo journalctl -u comfyui -f --since '5 min ago'"
```

### Available checkpoints (verified 2026-05-04)
- ✅ `flux1-schnell-fp8.safetensors` (17 GB, installed)
- ❌ `flux1-dev-fp8.safetensors` (NOT installed — 1.5 MB partial; HF anonymous rate-limit blocks the 17 GB download at ~100 KB/s = 45 h ETA)

### To install flux1-dev (when operator wants higher quality)
1. Add `HF_TOKEN` to macOS Keychain:
   ```bash
   security add-generic-password -a "$USER" -s HF_TOKEN -w "<paste-token>"
   ```
2. Resume on Pearl Star:
   ```bash
   ssh pearl_star "cd /home/ahjan108/phoenix_server/ComfyUI/models/checkpoints/ && \
     wget --header=\"Authorization: Bearer <token>\" --continue --tries=20 \
       'https://huggingface.co/Comfy-Org/flux1-dev/resolve/main/flux1-dev-fp8.safetensors'"
   ssh pearl_star "sudo systemctl restart comfyui.service"
   ```
3. Update workflows that override checkpoint at runtime.

---

## 8. Reference call shape — the two-stage cover pattern

```python
import io
from PIL import Image, ImageDraw
from scripts.video.flux_client import call_comfyui

COMFYUI_URL = "http://pearlstar.tail7fd910.ts.net:8188"

# Stage 1: FLUX background only — NO TEXT in prompt
prompt = (
    "abstract minimalist book cover background, contemplative mood, "
    "gradient tones of slate and warm sand, atmospheric, soft focus, "
    "clean composition, generous negative space, professional publishing quality, "
    "no objects, no people"
)
negative = (
    "text, letters, words, typography, title, author name, "
    "face, person, hand, fingers, realistic photo, busy, cluttered, "
    "low quality, watermark, signature, logo, border, frame"
)

# 3× retry with backoff
import time
last_err = None
for attempt in range(3):
    try:
        img_bytes = call_comfyui(COMFYUI_URL, prompt, negative,
                                 width=1024, height=1024, seed=seed + attempt * 1000)
        bg = Image.open(io.BytesIO(img_bytes)).convert("RGB").resize((1600, 2560), Image.LANCZOS)
        break
    except Exception as e:
        last_err = e
        time.sleep(5 * (attempt + 1))
else:
    # fallback to gradient (or skip)
    raise last_err

# Stage 2: PIL typography overlay
draw = ImageDraw.Draw(bg, "RGBA")
# title (with shadow for legibility on busy bg) + subtitle + author + accent + colophon + genre tag
# ... see scripts/image_generation/generate_bestseller_covers.py for the reference implementation
bg.save(out_path, "PNG", optimize=True)
```

---

## 9. Known gaps / future work

1. **Other 23 brands (~1,015 series)** still have `main_character.png` only — no `cover.png`. Adapt `/tmp/upgrade_per_series_covers_to_flux.py` per brand (clone the `collect_warrior_series` + `render_warrior` pattern; new prompt mood per brand).
2. **Image bank for the other 23 brands.** `/tmp/generate_warrior_calm_image_bank.py` is the template — adapt prompts per `config/manga/brand_illustration_styles.yaml` entry.
3. **flux1-dev-fp8** not installed on Pearl Star (see §7 above).
4. **`generate_manga_character_views.py`** ComfyUI mode is unimplemented (line 171 TODO). Generates 39 placeholder front/three_quarter/profile PNGs at ~15 KB each. Triptych covers the portrait/scene/symbolic complement at FLUX quality.
5. **`master_sha_podcast.png`** KDP outlier (244 KB, gradient fallback). Re-run when Pearl Star queue is idle:
   ```bash
   PYTHONPATH=. COMFYUI_URL="http://pearlstar.tail7fd910.ts.net:8188" \
     python3 scripts/image_generation/generate_kdp_all_formats.py \
     --mode comfyui --teacher master_sha --format podcast
   ```
6. **More EI character-authors.** Currently 6 registered; many brands × locales need their author profiles authored:
   ```bash
   python3 scripts/manga/generate_manga_author.py \
       --brand-id <brand> --genre <genre> --locale <locale> \
       --topic <topic> --demographic <persona>
   ```

---

## 10. QA verification checklist

Run these to confirm the session's work landed correctly:

```bash
# 1. Specs / docs
ls -la docs/PEARL_STAR_IMAGE_GENERATION_PROTOCOL.md \
       docs/HANDOFF_PEARL_STAR_IMAGE_PIPELINE_2026-05-04.md \
       specs/MANGA_AUTHOR_AND_COVER_ART_CANONICAL_SPEC.md \
       skills/pearl-image/SKILL.md

# 2. CLAUDE.md trigger phrases
grep -n "Pearl_Image\|pearl-image\|PEARL_STAR_IMAGE_GENERATION" CLAUDE.md

# 3. Deleted files (should all return "No such file")
ls specs/archive/MANGA_AUTHOR_SYSTEM_SPEC.md \
   specs/archive/MANGA_MODE_SYSTEM_SPEC.md \
   docs/authoring/AUTHOR_COVER_ART_SYSTEM.md \
   config/authoring/author_cover_art_registry.yaml \
   scripts/generate_author_cover_art_flux.py \
   2>&1 | grep "No such file"

# 4. image_qc.py imports cleanly
PYTHONPATH=. python3 -c "from scripts.image_generation import image_qc; print('ok', len(image_qc._known_author_ids()), 'author ids')"

# 5. Cover counts
echo "stillness_press: $(ls /Users/ahjan/phoenix_omega/assets/manga_catalog/stillness_press/*/cover.png 2>/dev/null | wc -l) covers"
echo "warrior_calm:    $(ls /Users/ahjan/phoenix_omega/assets/manga_catalog/warrior_calm/*/cover.png 2>/dev/null | wc -l) covers"

# 6. Pearl Star reachable
curl -s --max-time 10 "http://pearlstar.tail7fd910.ts.net:8188/system_stats" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['system']['comfyui_version'], d['devices'][0]['name'])"

# 7. Re-render dashboard
PYTHONPATH=. python3 scripts/dashboards/build_pearl_books_dashboard.py

# 8. Open dashboard
open /Users/ahjan/phoenix_omega/qa_books_2026-05-04/pearl_books_dashboard.html

# 9. Spot-check a FLUX cover
open /Users/ahjan/phoenix_omega/assets/manga_catalog/warrior_calm/warrior_calm_battle_ja_jp_01/cover.png
open /Users/ahjan/phoenix_omega/assets/manga_catalog/stillness_press/stillness_jp_20/cover.png
```

---

## 11. Read-First (canonical sources of truth)

In order, before doing any image-generation or manga-author work:

1. `CLAUDE.md` — top-level trigger phrases + non-negotiable defaults
2. `docs/PEARL_STAR_IMAGE_GENERATION_PROTOCOL.md` — canonical image-gen recipe
3. `skills/pearl-image/SKILL.md` — operational entry point with trigger detection
4. `specs/MANGA_AUTHOR_AND_COVER_ART_CANONICAL_SPEC.md` — manga authors + covers authority
5. `config/authoring/manga_authors/schema.yaml` — EI author schema
6. `docs/CHARACTER_INDIVIDUATION_PIPELINE_SPEC_2026-05-02.md` — protagonist 12-axis vocabulary
7. `docs/CHARACTER_INDIVIDUATION_PROMPT_ALGORITHM_2026-05-03.md` — token budgets
8. `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` §0 — Pearl Star endpoints
9. `skills/pearl-int/SKILL.md` — sister agent for installs/restarts
10. `qa_books_2026-05-04/0_IMAGE_GENERATION_SUMMARY.txt` — most recent batch artifact

---

## 12. NEXT_ACTION (for the next agent / session)

1. **Operator QA the Pearl Books dashboard** — verify stillness_press + warrior_calm covers look right. Approve or request adjustments.
2. **Decide flux1-dev install** — if higher-quality renders are wanted for hero covers, add `HF_TOKEN` to Keychain and Pearl_Int will resume the download.
3. **Pick the next brand** to upgrade to FLUX covers (cognitive_clarity is the third flagship). Adapt `/tmp/upgrade_per_series_covers_to_flux.py` and `/tmp/generate_warrior_calm_image_bank.py` for that brand.
4. **Author more EI character-authors** for the brands × locales currently at 0 EI authors.
5. **Re-run KDP podcast for master_sha** when Pearl Star is idle (the 1 outlier).
6. **Land this session as a PR** via Pearl_GitHub:
   - branch: `agent/pearl-star-image-pipeline-canonical-20260504`
   - title: `chore: Pearl Star image-gen canonical + retire old manga-author/cover-art system`
   - includes: 4 new docs/specs/skills, 8 patched files, 34 deletions, dashboard generator
7. **DOCS_INDEX entry already added** for the new protocol; consider also adding entries for the canonical manga-author spec and this handoff.

---

**End of handoff.** Pearl Star image pipeline is canonical, old way is retired, and 377 FLUX images are on disk.
