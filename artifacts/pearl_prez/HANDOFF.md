# Pearl_Prez — Handoff Document
**Date:** 2026-04-18  
**Status:** NOT STARTED — zero images generated, no artifacts exist yet  
**Prepared by:** Pearl_GitHub (worktree busy-feynman-10910b)

---

## 1. What Is This?

Pearl_Prez is a planned feature to add manga-styled, MP3-synced visuals to the existing Pearl Prime presenter slideshow at:

**https://729184d3.phoenix-command.pages.dev/**

The full agent prompt (the one you just pasted) is the work order. This doc fills in everything the prompt assumed but got wrong or didn't know.

---

## 2. Current State — What Exists

### Slideshow Architecture (DIFFERENT FROM WHAT THE PROMPT ASSUMED)

The prompt assumed **one master MP3 per section** with timestamps. **That is not how this app works.**

| What the prompt assumed | What actually exists |
|---|---|
| One MP3 per section (intro.mp3, marketing.mp3, etc.) | **142 individual MP3 clips** — one per spoken line |
| `timeupdate` event on a continuous audio stream | Sequential playback via `speakLine()` / `playFrom()` JS loop |
| 3 sections (Intro / Marketing / Weekly Tasks) | 9 decks; nav shows **Intro**, **Marketing**, **Work Flow** (= `briefing_us`) |
| Simple `<audio data-section="...">` tag | No single `<audio>` tag — audio is spawned dynamically per line |

### Source Files

| File | What It Is |
|---|---|
| `brand-wizard-app/public/presenter.html` | **Single-file source** — 2,257 lines of HTML+CSS+JS. All scripts, styles, deck definitions, and audio manifests live here. DO NOT touch the dist version — edit source and rebuild. |
| `brand-wizard-app/dist/presenter.html` | Built output — deployed to Cloudflare Pages. Rebuilt via `npm run build` inside `brand-wizard-app/`. |
| `brand-wizard-app/dist/assets/audio/` | All pre-generated MP3 clips, organized by deck subfolder |

### Audio Files Already Generated

```
brand-wizard-app/dist/assets/audio/
├── intro/          62 MP3 clips  (e.g. intro/00_00_en.mp3 … intro/24_01_en.mp3)
├── marketing/      60 MP3 clips  (e.g. marketing/00_00_en.mp3 … marketing/13_03_zh-cn.mp3)
├── briefing_us/    20 MP3 clips  (e.g. briefing_us/00_00_en.mp3 … briefing_us/05_02_en.mp3)
├── briefing_jp/    (also present)
├── briefing_kr/    (also present)
├── briefing_fr/    (also present)
├── briefing_de/    (also present)
├── briefing_tw/    (also present)
├── briefing_cn/    (also present)
├── audiobook_chapters/
├── podcast/
└── showcase/
```

**Total for the 3 nav-visible decks: 142 MP3 clips.** Each clip = one spoken line = one image cue.

### Script Lines Per Deck (= image count target)

| Deck | Nav label | Text lines | Images needed |
|---|---|---|---|
| `intro` | Intro | 64 | ~60–64 |
| `marketing` | Marketing | 63 | ~60–63 |
| `briefing_us` | Work Flow | 20 | ~20 |
| **Total** | | **147** | **~147** |

These are real counts from the HTML. NOT the 180–200 estimated in the prompt.

---

## 3. How the JS Playback Works (Critical for Image Sync)

The audio engine is entirely in `presenter.html`. Key functions:

```
playFrom(idx)         — starts playback from section index idx
speakLine(ln, li, session, cb)  — plays one line (ln=section, li=line index)
  → looks up getAudioPath(sectionIdx, lineIdx) from AUDIO_MANIFEST
  → if MP3 exists: new Audio(mp3).play()
  → if MP3 missing: browser TTS fallback
  → calls cb() when done → loops to next line
```

**AUDIO_MANIFEST** (hardcoded in presenter.html) is the full map:
```js
var AUDIO_MANIFEST = {
  intro: [
    ["intro/00_00_en.mp3", "intro/00_01_en.mp3", "intro/00_02_en.mp3"],  // section 0
    ["intro/01_00_en.mp3", "intro/01_01_en.mp3", "intro/01_02_en.mp3"],  // section 1
    ...
  ],
  marketing: [...],
  briefing_us: [...],
  ...
}
```

File naming: `<deck>/<section_idx>_<line_idx>_<lang>.mp3`  
e.g. `intro/03_01_en.mp3` = intro deck, section 3, line 1, English

### Correct Image Sync Approach

**Do NOT use `timeupdate` on a continuous audio element.** Instead:

Hook into the `speakLine` call. The right place is in the `playFrom` loop or by wrapping `speakLine`. Add image-swap logic at the point where a new line begins:

```js
// In the speakLine function (around line 1168 in presenter.html),
// just before the audio plays, fire:
showPrezImage(activeDeck, sectionIdx, lineIdx);
```

Each `(deck, sectionIdx, lineIdx)` triple maps to one image file:
```
artifacts/pearl_prez/images/<deck>/<sectionIdx>_<lineIdx>_v1.png
// Served from dist as: assets/pearl_prez/images/intro/03_01_v1.png
```

---

## 4. What Pearl_Prez Needs to Actually Do

### Phase 1: Build the cue plan (no Bing yet)

Skip the audio transcription phase — there is no master MP3 to transcribe. The text is already in the HTML as `SCRIPTS_INTRO`, `SCRIPTS_MARKETING`, `SCRIPTS_BRIEFING_US`.

Extract them:
```bash
python3 - <<'PY'
import re, json

html = open('brand-wizard-app/public/presenter.html').read()

# The SCRIPTS_* arrays are JS — extract text fields
# Each entry: {lang:"en", nav:{path:..., slide:...}, text:"..."}
texts = re.findall(r'\{lang:"([^"]+)",nav:\{path:"([^"]+)",slide:([^}]+)\},text:"([^"]+)"\}', html)

cues = []
for deck_name in ['intro', 'marketing', 'briefing_us']:
    # Parse AUDIO_MANIFEST for this deck to get (section, line) tuples
    manifest_match = re.search(rf'{deck_name}:\[(.*?)\](?=,\n\s+\w|\n\})', html, re.DOTALL)
    # ... extract section/line index + mp3 path
    pass

print(f"Found {len(texts)} text lines total")
PY
```

Easier: just read the AUDIO_MANIFEST directly from the HTML. Each entry in `AUDIO_MANIFEST[deck][section][line]` corresponds to one MP3 clip. Pair it with the matching script line from `SCRIPTS_*` to get the spoken text.

Cue plan format (correct version, replaces the one in the Pearl_Prez prompt):
```json
[
  {
    "deck": "intro",
    "section_idx": 0,
    "line_idx": 0,
    "mp3": "intro/00_00_en.mp3",
    "lang": "en",
    "spoken_text": "Welcome to Pearl Prime...",
    "key_concept": "...",
    "manga_style": "shonen",
    "image_prompt": "...",
    "image_path": "intro/00_00_v1.png",
    "status": "pending"
  },
  ...
]
```

Write to: `artifacts/pearl_prez/image_cue_plan.json`

### Phase 2: Generate images via Bing (same 4-tab loop)

All the Bing/Claude-in-Chrome instructions in the original prompt are correct. Just use the updated cue_plan.json structure.

Save images to:
```
artifacts/pearl_prez/images/intro/00_00_v1.png
artifacts/pearl_prez/images/intro/00_01_v1.png
...
```

Before deploy, copy to dist:
```bash
mkdir -p brand-wizard-app/dist/assets/pearl_prez/images/{intro,marketing,briefing_us}
cp -r artifacts/pearl_prez/images/* brand-wizard-app/dist/assets/pearl_prez/images/
```

### Phase 3: Wire image display into presenter.html

Find the `speakLine` function (around line 1168). Add image swap call:

```js
// Add this function near the bottom of <script>:
function showPrezImage(deck, sectionIdx, lineIdx) {
  var stage = document.getElementById('pearl-prez-stage');
  if (!stage) return;
  var key = sectionIdx + '_' + lineIdx;
  var src = 'assets/pearl_prez/images/' + deck + '/' + key + '_v1.png';
  // Check override first
  var override = 'assets/pearl_prez/images/' + deck + '/_overrides/' + key + '.png';
  stage.innerHTML = '<img src="' + src + '" onerror="this.style.display=\'none\'" class="pp-img pp-fade-in" />';
}

// Patch speakLine to call it:
// In speakLine(ln, li, session, cb), before line 1168, add:
// showPrezImage(activeDeck, ln, li);
```

Add the stage div after the existing `#app` container:
```html
<div id="pearl-prez-stage" style="width:100%;max-width:960px;aspect-ratio:16/9;margin:1rem auto;background:#000;overflow:hidden;border-radius:6px;position:relative;"></div>
```

Add CSS:
```css
.pp-img { width:100%; height:100%; object-fit:cover; opacity:0; transition:opacity .5s; }
.pp-fade-in { opacity:1; }
```

### Phase 4: Deploy

```bash
cd brand-wizard-app
npm run build
cd ..
git add brand-wizard-app/dist/ artifacts/pearl_prez/
git commit -m "feat(presentation): Pearl_Prez manga images — 147 images across intro/marketing/briefing_us"
# Then push and Cloudflare Pages auto-deploys from main
```

Deploy workflow: `brand-admin-onboarding-pages.yml`  
Cloudflare creds in Keychain: `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN`

---

## 5. Manga Style Resources in This Repo

The original prompt referenced `config/source_of_truth/manga_story_strategies/*.yaml` — **that path does not exist.** What does exist:

| Path | What it contains |
|---|---|
| `config/source_of_truth/manga_profiles/brands/` | 13 brand-specific manga profile YAMLs (body_memory_shojo, solar_return_isekai, heart_balance_shojo, warrior_calm_cultivation, etc.) |
| `config/video/brand_video_styles.yaml` | Visual style tokens for video |
| `config/video/brand_style_tokens.yaml` | Style tokens |
| `artifacts/research/global_manga_distribution_strategy.md` | Platform/market research |
| `artifacts/research/western_illustrated_styles_2026_04_04.md` | Illustrated style research |

Use the manga profile YAMLs to inform style choices. The presenter is for US English audience — lean toward:
- `shonen` for energy/scale/launch content
- `seinen` for business/data/strategy content  
- `iyashikei/shojo` for weekly rhythm/wellness/routine content

---

## 6. Operator Readiness Checklist (unchanged from original prompt)

- [ ] Chrome open, logged into `bing.com/images/create`
- [ ] Claude-in-Chrome MCP plugin active — test: `mcp__Claude_in_Chrome__tabs_context_mcp`
- [ ] 4 Bing Image Creator tabs open and ready
- [ ] This handoff doc read in full before starting
- [ ] Session allocated: ~2–3 hours (147 images ÷ 4-at-a-time = ~37 batches × ~4 min/batch)

---

## 7. Key Corrections vs. the Original Prompt

| Original prompt said | Correct information |
|---|---|
| "3 menu sections: Intro / Marketing / Weekly Tasks" | Nav has: **Intro** (`?deck=intro`), **Marketing** (`?deck=marketing`), **Work Flow** (`?deck=briefing_us`) — not "Weekly Tasks" |
| "one master MP3 per section" | 142 individual MP3 clips, one per spoken line |
| "transcribe with Whisper" | No transcription needed — text is in the HTML as `SCRIPTS_INTRO`, `SCRIPTS_MARKETING`, `SCRIPTS_BRIEFING_US` |
| "~180–200 images total" | 147 total (64 intro + 63 marketing + 20 briefing_us) |
| "sync via `timeupdate` on `<audio data-section=...>`" | Hook into `speakLine()` function — no single audio element exists |
| "`config/source_of_truth/manga_story_strategies/*.yaml`" | That path doesn't exist. Use `config/source_of_truth/manga_profiles/brands/*.yaml` instead |
| "`artifacts/research/manga_cover_design/01_japan_by_genre.md`" | That path doesn't exist. Use `artifacts/research/global_manga_distribution_strategy.md` |

---

## 8. Files to Create (None Exist Yet)

```
artifacts/pearl_prez/
├── image_cue_plan.json          ← Build this first (Phase 1)
├── inventory.md                 ← Summary of slideshow structure
├── images/
│   ├── intro/                   ← 62 images (00_00_v1.png … 24_01_v1.png)
│   │   └── _overrides/          ← Drop PNG here to override Bing output
│   ├── marketing/               ← 60 images
│   │   └── _overrides/
│   └── briefing_us/             ← 20 images
│       └── _overrides/
├── contact_sheet_intro.png      ← Visual QA (Phase 6)
├── contact_sheet_marketing.png
├── contact_sheet_briefing_us.png
└── DEPLOY_REPORT.md             ← Final deliverable
```

---

## 9. Starting Command for the Fresh Session

Paste this at the top of the Pearl_Prez agent prompt to override the incorrect assumptions:

```
CORRECTION BLOCK — READ BEFORE PHASE 1:

The slideshow at https://729184d3.phoenix-command.pages.dev/ uses INDIVIDUAL MP3 CLIPS
per spoken line, not one master MP3 per section. There are 147 total lines across 3 decks:
  - intro: 64 lines  (62 MP3 files at brand-wizard-app/dist/assets/audio/intro/)
  - marketing: 63 lines  (60 MP3 files at brand-wizard-app/dist/assets/audio/marketing/)
  - briefing_us: 20 lines  (20 MP3 files at brand-wizard-app/dist/assets/audio/briefing_us/)

DO NOT attempt to transcribe audio. The scripts are already in presenter.html as
SCRIPTS_INTRO, SCRIPTS_MARKETING, SCRIPTS_BRIEFING_US JavaScript arrays.

Image sync: hook into the speakLine() function in presenter.html (line ~1168),
NOT via timeupdate on an audio element.

Image naming: artifacts/pearl_prez/images/<deck>/<section_idx>_<line_idx>_v1.png
Deploy path: copy to brand-wizard-app/dist/assets/pearl_prez/images/ then npm run build.

See full handoff doc: artifacts/pearl_prez/HANDOFF.md
```

---

## 10. CLOSEOUT_RECEIPT (This Handoff Session)

- **session_id:** pearl-prez-handoff-2026-04-18
- **branch:** busy-feynman-10910b (Pearl_GitHub worktree)
- **work done:** discovery and documentation only — no images generated, no HTML modified
- **artifacts created:** `artifacts/pearl_prez/HANDOFF.md` (this file)
- **images generated:** 0 of 147
- **API spend:** $0
- **NEXT_ACTION:** Open a fresh session with Claude-in-Chrome MCP active + Bing Image Creator ready. Paste the original Pearl_Prez prompt followed by the CORRECTION BLOCK from Section 9 above. The agent will skip Phase 2 (transcription), build the cue plan from the HTML scripts, then run 37 Bing batches to generate 147 images.
