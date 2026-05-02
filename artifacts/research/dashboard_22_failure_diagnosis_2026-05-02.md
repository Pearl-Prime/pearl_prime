# Dashboard 22-PNG Failure Diagnosis — Stillness_Press Catalog Visibility

**Date:** 2026-05-02
**Branch:** `agent/manga-drawing-traditions-research-20260502`
**Scope:** The 22 stillness_press series rendered in
`/Users/ahjan/phoenix_omega/.claude/worktrees/dreamy-nightingale-7bd099/artifacts/catalog_visibility/stillness_press_manga_dashboard.html`
(also: `assets/manga_catalog/stillness_press/<series_id>/main_character.png`).

**Methodology:** 6 PNGs visually inspected directly via the Read tool (the 4
operator-flagged failure cases — jp_07, jp_08, jp_11, jp_16 — plus 2 working
anchors — jp_01, pressure_map). The remaining 16 PNGs are diagnosed
**textually** against the 6 visually-confirmed exemplars + their `genre_family`
+ `subgenre` + `visual_grammar` + `line_weight_profile` + `black_fill_ratio`
+ `screentone_profile` from the local source-of-truth manga profile YAMLs
(`config/source_of_truth/manga_profiles/series/stillness_jp_*.yaml` and the
`stillness_press_*_vol1.yaml` family) plus `manga_series_index.json`. Where a
series profile is not in this branch (e.g., `stillness_press_body_letters`,
`stillness_press_ember_and_rest`, `stillness_press_pressure_map`, others not in
the local 24), the diagnosis is **inferred from genre + locale** with the
caveat that textual-only diagnosis is weaker evidence than visual.

**Cross-references (SHA-pinned):**

```yaml
cross_references:
  cookbook_research:
    path: docs/COMFYUI_FLUX_MANGA_PROMPTING_RESEARCH_2026-04-29.md
    sha: 2881dd970bf2433e2225800ac6f73b1dd0281be5
    pr: 802
    sections_referenced: ["§0 (schnell-mismatch)", "§2.2 (genre-anchor tokens)", "§3 (per-genre cookbook)"]
  community_assets_audit:
    path: docs/COMMUNITY_ASSETS_AUDIT_2026-04-29.md
    sha: f4c50142b63df134d2f34c10a4a761bd9015c910
    pr: 803
    sections_referenced: ["Base diffusion model", "Character consistency", "Per-genre LoRAs (4 genres deep)"]
  community_lora_roster:
    path: artifacts/research/community_lora_roster_2026-04-29.yaml
    sha: f4c50142b63df134d2f34c10a4a761bd9015c910
    pr: 803
    sections_referenced: ["mecha", "dark_fantasy", "healing"]
```

---

## Top-line findings (the 22 in aggregate)

The operator's two diagnoses are confirmed by direct visual inspection of the
4 flagged failure cases plus the 2 working anchors:

**Failure 1 — drawing tradition not honoring genre.** All 4 visually-inspected
failure-flagged PNGs (jp_07 dark_fantasy, jp_08 dark_fantasy, jp_11
psychological_horror, jp_16 isekai) render at the *same line economy and ink
density* as the working healing anchor (jp_01). The dark_fantasy panels lack
Berserk-tradition ink weight and atmospheric dread; the horror panels lack
Junji Ito sparse-restraint or Suehiro Maruo dense-stippling — they read as
"slice_of_life with serious expression." This is exactly the failure mode the
brief flagged.

**Failure 2 — character look-alike across protagonists.** The 6 visually
inspected protagonists (5 of which are female, late-20s/early-30s,
contemplative) collapse to a near-identical face geometry: oval-to-heart face
shape, large rounded anime-default eyes with light eyelid lines, soft jaw,
slight upturned nose, bobbed-or-short hair styling, parted lips with neutral
expression. Across these 6 the only *deliberately differentiated* face is
`stillness_jp_08`'s warrior — but it differs in the wrong direction (sharper
chibi-anime eye styling, white-haired waifu register) rather than via the
12-axis individuation vocabulary the catalog needs.

**Aggregate breakdown of the 22:**

| Category | Count | Confidence |
|---|---:|---|
| Pass with no changes (working iyashikei register, distinct-enough face) | 0–2 | Low — even working iyashikei renders share the look-alike face |
| Need prompt-fix only (genre-token fix; no LoRA / no workflow / no individuation) | 0 | Low — every PNG needs at least look-alike fix even if drawing-register is OK |
| Need workflow-fix (the schnell-at-cfg-4 issue from cookbook PR §0) | 22 | High — every PNG inherits the engine misconfiguration; engine fix is a precondition |
| Need character-individuation pipeline (12-axis solver before regen) | 22 | High — every protagonist drifts toward the average-face attractor |
| Need LoRA + multiple fixes (the 4 visually-flagged failures + 1 isekai) | 5 | High — dark_fantasy and psychological_horror need per-genre LoRA per audit PR #803 |

**Estimated cost to regenerate all 22 with corrective spec** (per cookbook §0 economics):
- Engine fix (FLUX-schnell→Animagine XL 4.0 base or FLUX-schnell-at-correct-cfg) — operator-effort cost, $0 API
- Cookbook prompt fix (positive + negative split, genre-anchor + artist-anchor tokens) — $0 API, ~30 min operator
- 12-axis character-design YAMLs (one per series) — ~15 min operator each = ~5.5 hr total for 22 series
- Per-character image regen at $0.04/image × 22 = **$0.88** API spend
- Per-character LoRA training (only for named cast — most stillness_press characters don't need LoRAs at this stage; PuLID-FaceNet from a one-shot reference photo is sufficient for individuation) — optional
- Operator review + iteration time — significant

**Total estimated $: <$5 API; ~6-8 hr operator time.** The ROI per fix is enormous
relative to the cost.

---

## Per-PNG diagnosis (22)

Each PNG below is referenced as `<series_id>` and pulls from
`assets/manga_catalog/stillness_press/<series_id>/main_character.png` in the
dreamy-nightingale-7bd099 worktree. Genre / subgenre / visual_grammar metadata
from the local source-of-truth YAML (where present in this branch) or the
`manga_series_index.json`. PNGs marked **(visual)** were inspected directly;
the others are textual-only with caveat.

### Group 1 — healing / iyashikei (15 of 22)

The genre-register itself is correct here — Animagine XL 4.0 base covers
healing per audit PR #803 finding. The *only* failure across this group is
the look-alike-protagonist problem (failure 2). Drawing-tradition (failure 1)
is acceptable for this group.

#### 1.1 `stillness_jp_01` — "After Work, Eating Alone" (visual) ✅
- **Genre/subgenre:** healing / iyashikei_daily_life
- **Visual grammar:** iyashikei_minimalism, light line, 0.05 black-fill, minimal screentone
- **Drawing-tradition pass:** YES. Light line, sparse background, contemplative expression. Reads cleanly as iyashikei.
- **Look-alike pass:** NO. Face is the catalog-default oval/heart-shape with anime-default rounded eyes — Saki could be jp_11's protagonist, jp_16's protagonist, or pressure_map's protagonist with no audience-level distinction.
- **Corrective action:** character-design YAML lock for Saki (the named protagonist) — face shape: heart, eye geometry: small almond with downturned outer corner, hair: chin-length asymmetric bob, build: 5'4" small frame, age: late-30s with visible smile lines, wardrobe: copywriter-cardigan + warm earth palette. Then re-gen with the locked design tokens in prompt.

#### 1.2 `stillness_jp_02` — healing
- **Diagnosis (textual):** Same group as jp_01 — likely healing register passes, look-alike fails. Apply same character-design YAML lock methodology with a deliberately-different design (e.g., square face, narrow eyes, longer hair, different age signal).

#### 1.3 `stillness_jp_03` — healing
- **Diagnosis (textual):** Same as jp_02. Locking individuation YAML differentiates. The healing genre register itself is fine.

#### 1.4 `stillness_jp_04` — healing
- **Diagnosis (textual):** Same as jp_02.

#### 1.5 `stillness_jp_05` — healing
- **Diagnosis (textual):** Same as jp_02.

#### 1.6 `stillness_jp_06` — healing
- **Diagnosis (textual):** Same as jp_02.

#### 1.7 `stillness_press_anxiety_vol1` — healing (en_US locale)
- **Diagnosis (textual):** Same group; en_US locale loses the ja_JP-locale prior (per cookbook §2.6) so artist-anchor tokens (Yotsuba register / Mushishi atmosphere / Yokohama Kaidashi Kikou) become more important. Apply individuation YAML.

#### 1.8 `stillness_press_sleep_vol1` — healing (en_US)
- **Diagnosis (textual):** Same as anxiety_vol1.

#### 1.9 `stillness_press_somatic_vol1` — healing (en_US)
- **Diagnosis (textual):** Same.

#### 1.10 `stillness_press_the_alarm_within` — healing (en_US)
- **Diagnosis (textual):** Same.

#### 1.11 `stillness_press_ember_and_rest` — healing (en_US)
- **Diagnosis (textual):** Same. Title implies "embers" theme — corrective prompt should add "warm hearth-light" register tokens to differentiate from the cold-window healing.

#### 1.12 `stillness_press_body_letters` — healing (en_US)
- **Diagnosis (textual):** Same group. Topic implies somatic-healing; consider adding "letter-writing posture, journaling" tokens to differentiate panel scenes.

#### 1.13 `stillness_press_the_forest_edge` — healing (en_US)
- **Diagnosis (textual):** Forest setting; can use "Yokohama Kaidashi Kikou pastoral" anchor. Same individuation issue.

#### 1.14 `stillness_press_the_held_breath` — healing (en_US)
- **Diagnosis (textual):** Same.

#### 1.15 `stillness_press_window_season` — healing (en_US)
- **Diagnosis (textual):** Same.

### Group 2 — slice_of_life (2 of 22)

#### 2.1 `stillness_press_pressure_map` — slice_of_life (visual) ⚠️
- **Diagnosis (visual):** Drawing-register passes (light line, sparse bg). Look-alike protagonist FAILS — face is identical-class to jp_01's Saki.
- **Corrective:** distinct character-design YAML; if the series is "pressure-map workplace stress" themed, lock to a different age (mid-40s manager? early-20s entry-level?), different build (taller? shorter?), and different wardrobe register (suit-and-blazer vs cardigan).

#### 2.2 `stillness_press_somatic_field_notes` — slice_of_life
- **Diagnosis (textual):** Same.

### Group 3 — dark_fantasy (2 of 22) — VISUAL FAILURES ❌

This group's drawing-tradition is the operator's biggest-leverage failure. The
audit PR #803 already identified dark_fantasy as "needs LoRA fork-test (DARK
FANTASY XL v1.1 on Animagine 4.0)." Combined with the cookbook PR's mecha-
adjacent note, the corrective stack is: per-genre LoRA + Berserk/Miura-anchor
prompt + the engine fix.

#### 3.1 `stillness_jp_07` — "Awakening in the Soul Forest" (visual) ❌
- **Genre/subgenre:** dark_fantasy / somatic_fantasy
- **Visual grammar:** expressive_josei, MEDIUM line weight, 0.25 black-fill, atmospheric screentone (per series YAML)
- **Drawing-tradition FAIL:** the rendered PNG shows a young woman in a hooded robe with light-medium line, soft Asian features, bare-tree branches behind her. This is a **fantasy book cover with a girl in robes** — NOT seinen dark_fantasy. There is no Berserk-style ink density, no Miura cross-hatching, no atmospheric dread. Black-fill ratio reads as ~0.05-0.10 (close to iyashikei), not the 0.25 the YAML targets. The forest is bare and empty rather than dread-dense.
- **Look-alike FAIL:** face is catalog-default — could be Saki from jp_01.
- **Corrective:** per-genre LoRA (DARK FANTASY XL v1.1 cross-tested on Animagine 4.0 per audit), Miura/Berserk artist-anchor in positive prompt, "atmospheric dread, cross-hatched shadow, dense forest, heavy ink" register tokens, individuation YAML lock distinct from healing protagonists. Plus engine fix.

#### 3.2 `stillness_jp_08` — dark_fantasy (visual) ❌
- **Visual grammar (per index):** dark_fantasy
- **Drawing-tradition FAIL:** the rendered PNG shows a young woman with a sword and dragon skull, white hair, sharp anime eyes. This is **anime fantasy waifu**, not seinen dark_fantasy. The face is a different look-alike-class than jp_01 (sharp anime instead of soft anime) but in the wrong direction — moves from healing-protagonist to videogame-fantasy-protagonist, neither of which is the dark_fantasy register the YAML calls for.
- **Look-alike FAIL:** the face is "anime fantasy waifu archetype" — equally non-distinct in a different cluster.
- **Corrective:** same as 3.1, plus deliberate mature-josei-dark-fantasy register (not anime-fantasy-waifu).

### Group 4 — psychological_horror (2 of 22) — VISUAL FAILURES ❌

The operator's stated diagnosis was "horror with same line economy as
healing" — confirmed exactly.

#### 4.1 `stillness_jp_11` — psychological_horror (visual) ❌
- **Genre:** psychological_horror
- **Drawing-tradition FAIL:** the rendered PNG shows a young woman in a library/office, light line, modest screentone. This is **slice_of_life with a serious expression**, NOT psychological horror. There is no Junji Ito sparse-restraint-then-reveal, no Maruo dense-stippling, no Hino cosmic dread, no compressed white space. The protagonist is in a calmly-rendered interior — psychological_horror demands at minimum *unsettling* spatial geometry (off-center camera, claustrophobic crop) or *dread-anchored* face cues (slightly-too-wide eyes, slightly-too-still expression).
- **Look-alike FAIL:** face is catalog-default.
- **Corrective:** per-genre artist-anchor (Junji Ito / Suehiro Maruo / Hideshi Hino — see batch-1 Agent C report when it returns), heavy ink density tokens, "claustrophobic crop, dread-stillness, sparse line economy revealing dread, compressed white space" register prompt. The LoRA roster needs a horror-specific entry the audit PR #803 deferred — this is now a Phase 2 priority. Individuation YAML separately.

#### 4.2 `stillness_jp_12` — psychological_horror
- **Diagnosis (textual):** Same as 4.1.

### Group 5 — isekai (1 of 22)

#### 5.1 `stillness_jp_16` — isekai-recovery (visual) ⚠️
- **Genre:** isekai (subgenre likely karoshi-reincarnation iyashikei per `stillness_jp_16` topic mapping = burnout/somatic_healing)
- **Drawing-tradition partial pass:** rendered PNG shows a young woman in a kimono in a doorway with a Buddhist statue behind her. This is **quiet-contemplative** which is *register-correct* for karoshi-reincarnation iyashikei — but it's missing the *isekai signal*. There's no fantasy-world cue (no foreign architecture, no fantasy creature, no portal-element). The viewer reads it as healing, not isekai. So the genre is half-correct: the iyashikei half is right, the isekai half is invisible.
- **Look-alike FAIL:** face is catalog-default Saki-class.
- **Corrective:** add isekai-signal in setting (rural-fantasy-village, low-fantasy backdrop element, traveler-cloak-and-pack wardrobe). Keep the iyashikei tone. Plus individuation lock.

---

## Distillation by failure mode

### A. Engine-level (apply once, fixes all 22)

Per cookbook PR #802 §0: the schnell-at-cfg-4 oversampling is the
single-largest available quality win. Apply the engine fix
(FLUX-schnell→Animagine XL 4.0 OR FLUX-schnell at canonical 4-step + cfg=1.0)
before any prompt-level fix. Per audit PR #803, FLUX-dev is non-commercial so
the cookbook §0 "Option A" recommendation must be revised to **Animagine XL 4.0
+ dpmpp_2m + karras + 30 steps + cfg=7.0** (Pony's settings transfer to
Animagine well per audit) OR **Qwen-Image with its own native pipeline**.

### B. Prompt-level (apply 22× with per-series adjustment)

Add to positive prompt for every series:
- Genre-anchor + artist-anchor (per the per-genre cookbook follow-up PR)
- Individuation tokens from the locked character-design YAML

Move to NEGATIVE-PROMPT NODE (currently appended to positive — actively harmful per cookbook §0):
- Genre-forbidden tokens (per `forbidden_tokens_registry.yaml` deferred
  cookbook PR)
- Hallucinated-typography prevention tokens

### C. Workflow-level (apply once)

Per cookbook §8.2: patch `runcomfy_batch.py::submit_inference()` to override a
real `CLIPTextEncode` negative-prompt node. This is a separate engineering PR
gated on this research landing.

### D. Character-individuation level (apply 22× — most labor-intensive)

For each of the 22 series, fill the character-design YAML template
(`config/manga/character_design_template.yaml` — written by this PR). The
constraint solver checks the new entry against the existing 22's locked YAMLs
and forbids axis-collision on the most distinctive axes. Solver implementation
is a follow-up PR.

### E. LoRA-level (apply for 5 of the 22 — the dark_fantasy + psychological_horror
+ isekai needing visual register shifts)

Per audit PR #803:
- dark_fantasy (jp_07, jp_08): DARK FANTASY XL v1.1 cross-tested on Animagine
  4.0; if degraded, build Phoenix-native dark_fantasy LoRA
- psychological_horror (jp_11, jp_12): Phoenix-native LoRA needed (no clean
  audit pick); train on Junji Ito / Suehiro Maruo / Hideshi Hino reference
  corpus per Q5 corpus research
- isekai (jp_16): the combined "isekai signal in setting" + healing register
  may not need a LoRA; prompt-only fix may suffice

---

## NEXT_ACTION (post this research PR)

1. Engine fix (gates everything; cookbook §0)
2. Cookbook YAML fill-in PR with `drawing_tradition:` block per genre (uses this PR's `drawing_tradition_per_genre.yaml`)
3. Implement constraint solver per character_design pipeline spec (`scripts/manga/character_individuation_solver.py` — 200-400 LOC)
4. Fill character_design YAML for the 22 stillness_press series (uses character_design_template.yaml from this PR)
5. Train psychological_horror LoRA (Phase 2 LoRA priority list — high)
6. Train dark_fantasy LoRA (Phase 2 — high)
7. Regenerate the 22 PNGs as a smoke test of the combined fixes
8. If smoke test passes, propagate methodology to the other 12 brands' main_characters (the 624 PNGs not in the stillness_press 22)

---

*End of dashboard 22-failure diagnosis.*
