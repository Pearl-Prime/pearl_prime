# Manga Genre Prompting System Research — 2026-07-10

**Agent:** Pearl_Research  
**Project:** `proj_manga_catalog_reconciliation_20260426`  
**Subsystem:** `manga_pipeline`  
**Status:** AUTHORITY (research lane — implementation follows in Pearl_Dev)  
**Companion JSON:** `artifacts/research/manga_genre_prompting_system_2026-07-10.json`  
**Live anchor:** `origin/main` @ `234ff8a16db0ffd19d11a0ce66ed21fac16af12e` (verified 2026-07-10)  
**Acceptance layer:** authored candidate — research authority, not system-working, not PROVEN-AT-BAR

---

## 1. Problem Statement

**Blob failure anchor (verified visually, 2026-07-10):**

`artifacts/manga/warrior_calm_cultivation__master_wu__en_US__burnout__the_chassis_is_listening/assembled/ep_001_human_readability_proof/ep_001_from_continuity_strip.jpg`

Direct inspection of this strip and its source bank layers shows **visually unusable output**:

- Eight vertical panels of stippled blue/cyan noise blobs with no readable line art, screentone grammar, character identity, or mecha register.
- Source layer `image_bank/L2/seated_cockpit.png` is itself a grainy stipple blob (~3.5 MB) — not a cutout character in manga register.
- Assembled panel `ep001_003.png` repeats the same failure: humanoid noise mass inside a white frame on dark background.

**Why this is not acceptable proof:**

1. **Human readability fails** — no operator can read character, action, or genre from the strip.
2. **Register fails** — output reads as corrupted diffusion noise, not seinen mecha manga (Evangelion/Gundam/Patlabor register per `docs/research/manga_craft/mecha.md`).
3. **Byte-gate false positive** — `_provenance.json` reports 12/12 REAL layers with bytes ≥ 50k and `gate_report.json` reports PASS, but **bytes ≠ manga register**. Current blob gate (`scripts/manga/bank_layer_blob_gate.py`) cannot detect stipple-noise blobs that exceed byte thresholds.
4. **Wrong citation in gap report** — `artifacts/qa/MANGA_NOW_VS_100PCT_GAP_REPORT_2026-07-10.md` §2 and §6 labels this strip the "strongest legitimate layered proof." That claim is **false on visual inspection** and must be superseded by this research.

**Root cause summary (synthesized from repo autopsy + external docs):**

| Cause class | Evidence |
|---|---|
| Missing register anchors | `artifacts/research/drift_autopsy_2026-04-29.md` — no mandatory `manga panel / screentone / black-and-white ink` in legacy scaffolds |
| Model misroute | `scripts/manga/prompt_authority.py` defaults non-qwen/non-animagine tasks to `flux_schnell`; mecha L2 renders may not receive Qwen H_token_mapping |
| Style collision | `config/manga/cross_genre_blending_rules.yaml` `mecha_plus_iyashikei` — mecha tokens drag panel toward density; iyashikei/watercolor wash bleeds into mecha when blend rules not enforced |
| Prompt negation in positive slot | FLUX/Qwen both harmed by inline `no text` in positive (`docs/COMFYUI_FLUX_MANGA_PROMPTING_RESEARCH_2026-04-29.md` §0, §2) |
| No visual QA after render | Byte gate PASS with blob output proves gate is necessary but insufficient |
| Locale weakeners | `en_US` locale hints that say "American setting" or "manga-illustrated portrait" weaken manga-panel prior (`drift_autopsy` Autopsy 8) |

---

## 2. Source Ledger

| # | URL | Type | Access date | Confidence | Inference begins |
|---|---|---|---|---|---|
| S1 | https://github.com/QwenLM/Qwen-Image | Official (Qwen) | 2026-07-10 | High | Model capability claims beyond repo README |
| S2 | https://docs.qwencloud.com/developer-guides/image-generation/text-to-image | Official (Qwen Cloud) | 2026-07-10 | High | Phoenix-specific routing defaults |
| S3 | https://help.aliyun.com/en/model-studio/qwen-image-api | Official (Alibaba Model Studio) | 2026-07-10 | High | Production API parameter defaults for Pearl Star |
| S4 | https://github.com/QwenLM/Qwen-Image/blob/main/src/examples/tools/prompt_utils.py | Official (Qwen prompt utils) | 2026-07-10 | High | Edit-mode rules; `polish_prompt_en/zh` behavior |
| S5 | https://developers.googleblog.com/en/how-to-prompt-gemini-2-5-flash-image-generation-for-the-best-results/ | Official (Google) | 2026-07-10 | High | Gemini-specific; mapped to cross-model doctrine |
| S6 | https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/gemini-image-generation-best-practices | Official (Google Cloud) | 2026-07-10 | High | Enterprise API framing |
| S7 | https://corporate.rakuten.co.jp/news/press/2025/0730_01.html | Official (Rakuten press) | 2026-07-10 | Medium | Product scope only — **no image-prompt API docs** |
| S8 | https://ai.rakuten.co.jp/ | Official (Rakuten AI product) | 2026-07-10 | Low for prompting | UI exists; **no public prompt-engineering spec** |
| S9 | https://scottmccloud.com/2-print/1-uc/ | Primary craft (McCloud) | 2026-07-10 | High | Application to diffusion prompting |
| S10 | https://en.wikipedia.org/wiki/Understanding_Comics | Secondary craft | 2026-07-10 | Medium | Panel transition taxonomy cross-check |
| S11 | `docs/COMFYUI_FLUX_MANGA_PROMPTING_RESEARCH_2026-04-29.md` @ origin/main | Internal authority | 2026-07-10 | High | FLUX-specific engine recovery — partially superseded on model routing |
| S12 | `artifacts/research/drift_autopsy_2026-04-29.md` @ origin/main | Internal empirical | 2026-07-10 | High | Still valid for negation + locale defects |
| S13 | `config/manga/drawing_tradition_per_genre.yaml` @ origin/main | Internal authority | 2026-07-10 | High | H_token_mapping per engine — **under-consumed by render path** |
| S14 | `config/manga/cross_genre_blending_rules.yaml` @ origin/main | Internal authority | 2026-07-10 | High | Blend failure modes |
| S15 | `config/manga/forbidden_tokens_registry.yaml` @ origin/main | Internal authority | 2026-07-10 | High | Negative slot baseline |
| S16 | `docs/research/manga_craft/*.md` @ origin/main (24 lanes) | Internal craft bibles | 2026-07-10 | High | Genre visual contracts; some lanes deferred in drawing_tradition |
| S17 | `docs/CHARACTER_INDIVIDUATION_PIPELINE_SPEC_2026-05-02.md` @ origin/main | Internal authority | 2026-07-10 | Medium | §2.3–2.4 model table — **routing table updated by this research** |
| S18 | `scripts/image_generation/comfyui_workflows/qwen_image_txt2img_manga.json` @ origin/main | Internal workflow | 2026-07-10 | High | Pearl Star Qwen defaults |
| S19 | Civitai/fal Qwen guides (community mirrors of official behavior) | Secondary | 2026-07-10 | Medium | CFG/steps only — not primary authority |

**Rakuten coverage gap (explicit):** Rakuten AI public material (S7, S8) confirms image generation exists at `ai.rakuten.co.jp` with Japanese natural-language input, but **publishes no prompt grammar, negative-prompt slot, model routing, or genre-register guidance**. Third-party blog posts are anecdotal only and are **not** cited as authority. Phoenix must not invent Rakuten-specific prompt rules until official docs appear.

**Stale internal note:** `config/manga/genre_prompt_cookbook.yaml` (manga panel cookbook referenced in PR #802 research) **does not exist on origin/main**. Only `genre_prompt_cookbook_v2.yaml` exists, and it targets **KDP self-help covers (FLUX)**, not manga panels. Manga panel prompting authority currently lives in `drawing_tradition_per_genre.yaml` H_token_mapping + craft bibles — fragmented, not a single merged doctrine. **This artifact closes that gap.**

---

## 3. Canonical Prompting Doctrine

### 3.1 Universal best practices (all genres, all models)

Phoenix panel prompts MUST separate five slots. Never concatenate into one undifferentiated string.

| Slot | Purpose | Placement |
|---|---|---|
| **REGISTER** | Medium + genre read (`manga panel`, `screentone`, demographic) | **First 15 tokens / first sentence** |
| **SUBJECT** | Character, mecha, object, pose | Middle |
| **COMPOSITION** | Shot type, camera, panel border, scale | After subject |
| **RENDERING** | Line economy, ink density, color policy | After composition |
| **LOCALE/register overlay** | Setting + audience prior | Woven into REGISTER or SUBJECT — never trailing paragraph |

**Iteration protocol:**

1. **Seed-fixed smoke** — one panel, 4 seeds, visual inspect before batch.
2. **Register-first fix** — if blob/noise, add REGISTER anchors before tuning subject nouns.
3. **Negative slot only** — all negations in workflow negative CLIP node, never inline in positive (S11, S12, S18).
4. **Model-native grammar** — see §4; do not feed Animagine tag soup to Qwen or FLUX paragraph prose to Animagine.
5. **Conversational refinement** (Google S5) — for Qwen edit/layered paths: single-axis deltas ("increase screentone density", "sharpen mechanical line weight") not full prompt rewrites.

### 3.2 Phoenix prompt scaffold (production template)

```
REGISTER: {manga panel | manga page} + {genre register} + {demographic register}
SUBJECT: {character/mechanism description — concrete nouns AFTER register}
COMPOSITION: {shot_type}, {camera_angle}, {panel_border}, {scale_marker if mecha}
RENDERING: {line_weight policy}, {screentone/halftone policy}, {color_policy}
SERIES: series register: {title} — trailing, low weight
```

**Qwen prose example (mecha cockpit bust):**

> A monochrome seinen manga panel with clear ink line art and screentone shading. A tired adult male pilot seated in a mecha cockpit, medium close-up, eye-level, panel border visible. Fine mechanical line weight on console edges, bold shadows in joint cavities, minimal screentone on the face. Cockpit interior, pre-dawn ambient light from the left.

**Animagine tag example (same beat):**

> monochrome, greyscale, manga, comic, screentone, panel, cockpit, pilot, seated, mecha, seinen, mechanical detail, medium close-up, masterpiece, high score, year 2005

### 3.3 Qwen-specific doctrine (S1–S4)

- **Natural-language preferred** — Qwen2.5-VL encoder responds to prose; no `(token:1.2)` weights (S13 cross_genre_blending_rules).
- **Structured sentences beat tag lists** — subject → environment → style → lighting (S2, S3).
- **Concise** — 1–3 sentences for single panels; long paragraphs only for complex layouts (S2).
- **Text in images** — double quotes for literal text; Phoenix manga defers dialogue to PIL composite — **forbid in-image text** via negative slot (S4, S18).
- **`prompt_extend`** — Qwen API default true (S2); for Phoenix production, **disable or override** when register anchors are hand-authored (extended prompts may dilute register tokens).
- **Negative prompt required** — anatomy, blur, photorealism, 3d, watermark (S3).

### 3.4 Google cross-model doctrine (S5–S6)

Mapped to Phoenix even when not using Gemini in production:

- Narrative scene description > keyword soup (aligns with Qwen; **contradicts** Animagine tag path).
- Positive framing — describe desired scene, not exclusions in positive.
- Camera language (`low-angle`, `medium close-up`, `85mm portrait lens`) — high leverage for composition slot.
- Iterative refinement — single-attribute follow-ups.
- Sequential art template (S5 § "Sequential art") — direct precedent for manga panel prompts.

### 3.5 Manga craft doctrine (S9–S10, S16)

Genre authenticity requires panel **grammar**, not illustration keywords:

- **Closure** — each panel must imply off-panel continuity (McCloud); aspect-to-aspect transitions dominate iyashikei/mecha stillness beats.
- **Line economy** — genre-specific black-fill ratio (`mecha.md` §2: 0.25–0.40; iyashikei: sub-10%).
- **Forbidden cross-genre cues** — each craft bible §6 failure modes become negative-slot inputs.
- **SFX** — composited post-render; never prompt literal Japanese glyphs (drift autopsy typography hallucination class).

---

## 4. Model Routing Doctrine

| Model | When to use | When NOT to use | Prompt grammar | Primary failure risks |
|---|---|---|---|---|
| **Qwen-Image** | Character L2 cutouts, cockpit interiors, faces, CJK locales, natural-language panel specs | B&W dense crosshatch genres without smoke-test; backgrounds that need FLUX speed | Prose, 1–3 sentences, register-first | Stipple noise blobs when register anchors absent; `prompt_extend` dilution; weak mecha mechanical edge without explicit "ink line art" |
| **Qwen-Image-Layered** | L0/L2/L3 bank decomposition, edit passes, layer isolation | Single-shot cover art; final assembled proof without per-layer visual QA | Edit prompts per S4 `EDIT_SYSTEM_PROMPT`; preserve layer role in prompt | Layer bleed; color wash across layers; treating INTERIM as REAL |
| **FLUX-schnell** | Color webtoon backgrounds, speed drafts, non-register-critical env plates | **Any B&W manga panel**, mecha mechanical cutouts, character faces, monochrome seinen | Short front-loaded clauses; **steps=4, cfg=1.0 ONLY** | schnell@24/cfg=4 oversaturation + blob noise + typography hallucination (S11 §0) |
| **Animagine XL 4.0** | B&W panel register (crosshatch, screentone), tag-native genres, fallback when Qwen mecha smokes fail | Natural-language-only prompts without tag scaffold; color webtoon | Booru tags + `masterpiece, high score, year 20XX`; `(token:1.2)` allowed | Average-face shojo attractor; needs stacked anti-shojo negatives for josei |

**Phoenix default route (this research supersedes CHARACTER spec §2.4 table on primary engine):**

- **Primary:** Qwen-Image for all character/panel generation (operator mandate + distinctiveness, S17 §3).
- **Layered:** Qwen-Image-Layered for bank layer decomposition.
- **Fallback:** Animagine XL 4.0 when Qwen smoke fails register gate on B&W-heavy genres (dark_fantasy, psychological_horror, mecha crosshatch).
- **FLUX-schnell:** L0 environment plates for **color** genres only; never default in `prompt_authority.task_to_base_model()`.

---

## 5. Genre Prompting Matrix

Authority: 25 canonical genres from `config/manga/canonical_genre_list.yaml` + craft bible crosswalk in `docs/research/manga_craft/index.md`.

**Legend:** `prompt_mode`: `natural_language` (Qwen), `tags` (Animagine), `hybrid` (register prose + tag tail for Animagine fallback).

Full machine-readable matrix: `manga_genre_prompting_system_2026-07-10.json`.

### Top-8 priority genres (deep spec in drawing_tradition)

| genre_id | Visual register | Preferred | Fallback | prompt_mode | Anti-blob rescue |
|---|---|---|---|---|---|
| healing | Iyashikei sparse ink, 40–60% white space, soft earth palette | qwen_image | animagine_xl_4_0 | natural_language | Strip action lines; forbid speed lines in negative; reject if black-fill > 15% |
| dark_fantasy | B&W seinen crosshatch, Berserk/Miura ink weight | qwen_image | animagine_xl_4_0 | hybrid | Add "clear ink line art, crosshatching, no grey wash blob"; switch to Animagine if stipple |
| psychological_horror | Gekiga dense ink, high contrast, no iyashikei soft light | qwen_image | animagine_xl_4_0 | hybrid | Explicit "NOT iyashikei, NOT soft pastel"; Ito/Maruo pole selection |
| mecha | Monochrome mechanical line, cockpit scale contrast, screentone on plates | qwen_image | animagine_xl_4_0 | natural_language | **Mandatory** "manga panel, ink line art, screentone"; silhouette mecha at distance for iyashikei blend; reject stipple noise |
| romance | Josei realistic proportions, NOT shojo sparkle | qwen_image | animagine_xl_4_0 | natural_language | Stack anti-shojo negatives; Okazaki/Asano prose anchors |
| slice_of_life | Domestic mid-shot, clean line, low ink density | qwen_image | animagine_xl_4_0 | natural_language | Forbid moe/big-eyes via negative; Azuma/Amano anchors |
| fantasy_adventure | Adventure manga register, not children's book | qwen_image | animagine_xl_4_0 | hybrid | en_US: use "manga panel" not "American setting"; forbid kawaii/children's illustration |
| comedy | Expressive faces, clean line, moderate density | qwen_image | animagine_xl_4_0 | hybrid | Forbid horror crosshatch unless subgenre demands |

### Remaining canonical genres (summary — full JSON has scaffolds)

| genre_id | Preferred | Fallback | Register one-liner |
|---|---|---|---|
| battle | qwen_image | animagine_xl_4_0 | Kinetic shonen/seinen action, speed lines allowed, impact frames rare |
| workplace | qwen_image | animagine_xl_4_0 | Grounded josei/seinen office realism, no fantasy glow |
| mystery | qwen_image | animagine_xl_4_0 | Noir ink, shadow pools, restrained expression |
| horror | qwen_image | animagine_xl_4_0 | Horror manga register — not iyashikei soft |
| sports | qwen_image | animagine_xl_4_0 | Motion lines permitted, sweat SFX post-composite |
| essay | qwen_image | animagine_xl_4_0 | Reflective josei memoir caption density, sparse action |
| food | qwen_image | flux_schnell | Warm color still-life; FLUX only for color food glam |
| family | qwen_image | animagine_xl_4_0 | Domestic warmth, kodomomuke-adjacent only when brand demands |
| procedural | qwen_image | animagine_xl_4_0 | Documentary line, institutional settings |
| historical | qwen_image | animagine_xl_4_0 | Period ink, Vagabond/Vinland register |
| cultivation | qwen_image | animagine_xl_4_0 | Manhwa/manga progression fantasy, not Western D&D cover |
| sci_fi_cyberpunk | qwen_image | animagine_xl_4_0 | Akira/GiTS mechanical ink, not mecha-pilot focus |
| supernatural_everyday | qwen_image | animagine_xl_4_0 | Mushishi quiet register, sparse supernatural |
| school | qwen_image | animagine_xl_4_0 | Youth realism, school uniform specificity |
| memoir | qwen_image | animagine_xl_4_0 | Diaristic josei, caption-forward |
| social_issue | qwen_image | animagine_xl_4_0 | Grounded realism, no fantasy register |
| graphic_medicine | qwen_image | animagine_xl_4_0 | Therapeutic essay visual, moderate clean line |
| battle_internal | qwen_image | animagine_xl_4_0 | Internal philosophical seinen, sparse kinetic |

**Craft bible lanes without separate canonical row** map via `canonical_genre_list.yaml` aliases (e.g. `action_battle` → `battle`, `psychological_thriller` → `mystery`, `webtoon_vertical_romance` → color FLUX path).

---

## 6. Locale Overlay Rules

| Locale | Register overlay (REGISTER slot) | Avoid | Model attractor note |
|---|---|---|---|
| en_US | `manga panel, sequential art register, English-language edition` | "American setting", "manga-illustrated portrait", "cover quality" | Weak manga prior — must front-load panel grammar (S12 Autopsy 8) |
| ja_JP | `日本の漫画パネル、スクリーントーン、モノクロインク` or bilingual `Japanese manga panel, screentone` | Long ethnicity paragraphs | Strong manga prior on Qwen + Animagine |
| zh_TW | `台灣漫畫分格，黑白墨水，網點` + `Taiwan manga panel register` | Simplified-only cues on TW rows | Qwen CJK strength (S1) |
| zh_CN | `中国漫画分镜，黑白线稿，网点纸` | Traditional-only glyphs in prompt | Qwen simplified text rendering tested official (S3) |
| ko_KR | `한국 웹툰 또는 만화 패널` — pick webtoon color vs manga B&W per series format | Mixing vertical scroll cues into panel grid | Webtoon = color FLUX; manga = Qwen/Animagine |

Locale overlays modify **wording**, not genre register. Genre H_token_mapping wins on ink density and line policy.

---

## 7. Forbidden Prompt Patterns

### 7.1 Global anti-blob blacklist

| Pattern | Why forbidden | Example |
|---|---|---|
| `manga catalog cover quality` | Invites single-illustration key art, not panel | drift autopsy § scaffold |
| Inline `no text, no typography` in **positive** | Embeds text concept; hallucinates glyphs | S11 §0 |
| `watercolor wash` in mecha/dark_fantasy positive | Collides with monochrome mechanical register | drift autopsy #4, cross_genre mecha+iyashikei |
| `American setting` for en_US locale | Zero manga prior | drift autopsy #8 |
| Character role nouns before register (`dragon rider`, `ashgrey dragon`) | Concrete noun overwhelms genre overlay | drift autopsy #2 |
| `concept art`, `key visual`, `promotional illustration` | Western poster register | drawing_tradition F_forbidden |
| FLUX-schnell @ steps>4 or cfg>1.0 for panels | Stipple noise + oversaturation | S11 §0 |
| Empty/register-less prompts relying on `style_id` alone | Wrong tradition (healing→dark_psychological bug) | genre_tradition.py header comment |
| Byte-only PASS without visual inspect | Accepts blob proofs | mecha ep_001 strip failure |

### 7.2 Genre-specific forbidden (superset — see JSON + forbidden_tokens_registry)

- **mecha:** `soft iyashikei atmosphere` in positive when mecha visible; `gradient sky`, `key visual`, `photorealistic`
- **healing:** `speed lines`, `impact frame`, `chiaroscuro`, `screaming`
- **dark_fantasy:** `full color`, `oil painting`, `western comic`, `soft lighting`
- **psychological_horror:** `iyashikei`, `pastel`, `sparkle`, `healing`

---

## 8. Repo Drift And Canonical Absorption Targets

| Target file | Absorption action | Priority |
|---|---|---|
| `config/manga/drawing_tradition_per_genre.yaml` | Merge H_token_mapping with this doctrine; add `prompt_mode` + `anti_blob_rules` per genre | P0 |
| `config/manga/forbidden_tokens_registry.yaml` | Add global anti-blob patterns from §7.1 | P0 |
| `config/manga/cross_genre_blending_rules.yaml` | Enforce qwen_prose blend winners; add blob-failure corrective for mecha+iyashikei | P0 |
| **NEW** `config/manga/genre_prompt_cookbook.yaml` | Create manga-panel cookbook (distinct from v2 KDP) sourced from this research | P0 |
| `scripts/manga/prompt_authority.py` | Default route Qwen; remove flux_schnell fallback for panel tasks | P0 |
| `phoenix_v4/manga/genre_tradition.py` | Fail-closed when genre known but tokens empty; log register anchors | P1 |
| `scripts/manga/character_individuation/prompt_builder.py` | Consume JSON schema; per-model grammar split | P1 |
| `scripts/manga/bank_layer_blob_gate.py` | Add visual register heuristic (edge density / line detection) beyond bytes | P1 |
| `scripts/image_generation/comfyui_workflows/qwen_image_txt2img_manga.json` | Pin steps/cfg from S3; disable prompt_extend in production | P1 |
| `scripts/image_generation/comfyui_workflows/qwen_image_layered_decompose.json` | Layer-specific prompt slots from §4 | P1 |
| `artifacts/qa/MANGA_NOW_VS_100PCT_GAP_REPORT_2026-07-10.md` | **Supersede** mecha strip "strongest proof" claim | P0 doc fix |
| `docs/CHARACTER_INDIVIDUATION_PIPELINE_SPEC_2026-05-02.md` | Update §2.4 routing table to Qwen-primary | P2 ratification |

**Superseded in substance (not deleted):**

- Partial mecha H_token_mapping gaps labeled `empirical_gap` in drawing_tradition — superseded by §5 mecha scaffold + JSON.
- COMFYUI research §1.2 "SDXL+Pony primary for B&W" — superseded for Phoenix by Qwen-primary + Animagine fallback (commercial-clean stack constraint from audit #803).
- Gap report mecha proof superiority claim — superseded by §1 visual failure analysis.

---

## 9. Exact Next Implementation Lanes

1. **Pearl_Dev — `ws_manga_prompt_builder_v3_20260710`:** Wire `prompt_authority.py` + `genre_tradition.py` to load `manga_genre_prompting_system_2026-07-10.json`; Qwen-default routing; five-slot scaffold; negative slot only. **Blocks all re-render.**

2. **Pearl_Dev — `ws_manga_visual_blob_gate_20260710`:** Extend `bank_layer_blob_gate.py` with register heuristic (OpenCV edge/entropy check + optional WD tagger reverse prompt); FAIL stipple blobs >50k bytes.

3. **Pearl_Dev — `ws_manga_genre_cookbook_yaml_20260710`:** Author `config/manga/genre_prompt_cookbook.yaml` from JSON companion; CI diff gate against drawing_tradition H_token_mapping drift.

4. **Pearl_Dev — `ws_mecha_native_rerender_20260710`:** Re-render warrior_calm L2/L3 with new doctrine; replace blob bank; re-run human-readability proof; **do not cite until visual PASS**.

---

## 10. Operator Short Verdict

The mecha human-readability strip on `origin/main` is **blob garbage** that passed byte gates and validator JSON — proof that Phoenix's prompting system is structurally broken, not merely untuned. The repo already contains per-genre drawing traditions, forbidden tokens, and cross-genre blend rules, but they are **fragmented, under-wired, and defaulted to FLUX-schnell** in live prompt authority while Qwen H_token_mapping omits mandatory register anchors. This research merges Qwen-first prose doctrine, Google iterative composition patterns, honest Rakuten gap acknowledgment, manga craft panel grammar, and the April–July drift autopsies into one executable authority. **No operator should cite the current mecha strip as proof.** Next lane must wire the JSON into prompt builder + visual blob gate, then re-render.

---

## Appendix A — Blob failure autopsy (warrior_calm ep_001)

**Manifest:** `assembly_manifests/ep_001_from_continuity.yaml` — structurally valid, native-only paths, 12 REAL layers.

**Failure locus:** Render-time prompts for L2 `seated_cockpit`, L2 `threshold_stand`, L3 inserts — not assembly logic.

**Token patterns likely responsible (inference from tradition config + visual output):**

1. Missing `manga panel, ink line art, screentone` register block in dispatched prompt.
2. Possible `prompt_authority` → `flux_schnell` default for render task strings without `qwen` substring.
3. Mecha+iyashikei series brand (`warrior_calm_cultivation`) may inject healing/watercolor tokens via brand tint without blend rule enforcement.
4. Qwen without negative anatomy/photorealism guards → stipple-noise attractor.
5. Byte gate confirms file exists; no visual gate fired.

**Hard ban going forward:** Mark `ep_001_from_continuity_strip.jpg` as `INVALID_VISUAL_PROOF` in QA registries until replaced by visually inspected rerender.

---

*End of research authority. Machine-readable companion required for Pearl_Dev wiring.*
