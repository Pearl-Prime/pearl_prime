# Manga Layered-Composition Grammar Research — 2026-07-07

**Status:** RESEARCH (Pearl_Research; companion + citation base for `docs/specs/MANGA_COMPOSITION_GRAMMAR_SPEC.md` v1.0.0)
**Method:** internal inventory (this session, byte-level reads of specs/code/bank) + four parallel web-research agents — (A) anime cel/layout production, (B) VN sprite grammar + webtoon studio pipelines, (C) film/VFX compositing grounding fundamentals, (D) manga panel/shot grammar. Every external rule cited inline.
**Taxonomy labels:** findings here are **RESEARCHED**; the designed scheme is **SPECCED** (in the spec doc); nothing is claimed above those layers.
**Mission:** solve "half a person floating in the middle of a room" — current bank assembly pastes a waist-up cutout into a full-perspective room with no grounding.

---

## 1. Internal inventory verdict (what exists, where it stops)

| Artifact | Layer reached | What it gives | Where it stops |
|---|---|---|---|
| `MANGA_LAYER_RENDER_CONTRACT_SPEC.md` §5 framing contracts (CU/MCU/MS/LS/ELS/ECU/insert) | SPECCED (+CODE-WIRED via compile_safe_zones) | per-layer render framing + margins; even knows "ELS figure belongs in L0, not a separate L2" | single-layer render-time rules only; zero combination rules |
| §7 archetype layer maps (19 iyashikei) | CONFIG-EXISTS | archetype→layer recipe; informal BG hints (`bg_softfocus`) | BG hint is a prompt string, not a typed class; no legality matrix |
| §10 composite math + `scripts/manga/assemble_from_bank.py` | CODE-WIRED + EXECUTED-REAL (demo strip 2026-07-03) | deterministic z-order/paste/provenance | min-fit-and-center into pct bbox; no eye-level, no ground contact, no shadow, no occluder, no compatibility check |
| §12 validators | partially CODE-WIRED | per-layer render QA | no composite-geometry gate; `seam_check` is a WARN heuristic |
| §14.B.2/B.3 failure modes | SPECCED | names perspective/scale mismatch | detection-only, post-hoc; nothing constructive |
| §15.D.3 "reusable cinematic grammar" | named future unlock | — | explicitly not built |
| `MANGA_V5_LAYERED_ARCHITECTURE.md` | EXECUTED-REAL (ep_001 35/35 dispatch; operator visual gate pending) | per-panel geometric coherence by single-render decompose | silent on cross-panel bank reuse — when a decomposed subject may sit on a different background |
| `assembly_manifest.schema.json` | CODE-WIRED | archetype/beat_type fields, per-layer bbox+provenance | fields informational; layers carry zero composition metadata |
| Bank assets (April v4_render_cache + image_bank/L2/mira_aoki) | EXECUTED-REAL | 5 L0 plates (+prompt JSONs), 19 L2 pose cutouts, 2 diegetic CU composites, macro crops | metadata = filename + render-lineage provenance JSON; no camera angle, eye-level, crop class, lighting, BG class anywhere |
| Prior research `manga_layer_compositing_research_2026-05-20.md` | RESEARCHED | cutout/decompose model landscape (ToonOut, Qwen-Image-Layered, IC-Light) | covers layer *extraction*, not layer *combination*; §9.6 explicitly flags the geometric-alignment problem as unsolved by cutouts |
| `artifacts/research/manga_quality_bar/02_studio_workflow_gap_analysis.md` | RESEARCHED | pro pipeline stage chain (name/conti → …) | production stages, not composition geometry |
| Live manifest `mira_qwen_pulid_character_strip_v2` (2026-07-07) | EXECUTED-REAL | hand-improvised the fix: "ban flat-cream portrait cards; anchored scene / diegetic CU / insert macro / breath closure" | discipline exists only as per-session hand judgment — no spec, no metadata, no gate |

**The precise void:** the compatibility/grammar layer between the bank and the assembler — (a) composition metadata on assets, (b) deterministic combination legality + grounding rules, (c) a beat→shot→recipe grammar, (d) grounding ops (scale-from-horizon, contact shadow, occluder) in the compositor. The V4 postmortem already proved the cost: 2/35 operator acceptance, root cause "no shared coordinate system + pct-of-canvas bbox heuristic" (V5 spec §1). V5 solved it *within* a panel; nothing solves it *across* the bank, which is exactly the "bank × assembly = many stories" surface.

## 2. External methodology digest

### 2.A Anime cel production — the layout system (レイアウト)

- **One layout, one geometry.** Per cut, a layout sheet fixes camera frame, eye-level + vanishing points, character position/scale vs BG, camera moves; BG painters get the originals, key animators copies — both departments draw FROM the same geometry. (Washi, "Anime Production — Detailed Guide", washiblog.wordpress.com/2011/01/18/; Sakuga Wiki "Layout"; HK Govt press release for the Studio Ghibli Layout Designs exhibition, info.gov.hk/gia/general/201405/13/P201405130561; DeeDee Studio "Different approaches to layout design".)
- **BG genzu procedure** (most procedural public source: Masuyama Ryōji's note.com layout series ⑧/⑨, note.com/masuyama56/n/nc49f0fd4b3de): marked eye level + perspective; **red-line character silhouettes** so the painter paints the BG complete under the character; numeric camera-move lengths; overscan margins (紙足し) against edge exposure.
- **Eye-level discipline:** horizon = camera eye level; crosses all same-height standing figures at the same landmark at every depth; anime tutorials give the iterate-camera-height-in-head-units procedure and the exact failure mode: "the foreground boy seems to sink into the floor." (gyakusan-enshutsu.site/アイレベル探し/; ichi-up.net/2018/013; artyfactory.com/perspective_drawing/perspective_2.html.)
- **Angle buckets:** aori (low) / fukan (high) / eye-level; a cel drawn at one bucket cannot sit on a BG painted at another (foreshortening + horizon crossing + VP directions all disagree). The Tezuka-era **bank system** stored cel + BG as a *pair* for exactly this reason. (quirkydrawingclassroom.com/eyelevel_control; ja.wikipedia.org/wiki/バンクシステム; sadao-tsukioka.com/ja/posts/bank-system/.)
- **BOOK layers:** foreground occluders (grass, pillars, table edges) are separate art-department layers ABOVE the cel — the standard machinery that seats a character IN a scene; stack order `BG < A < B < … < BOOK①…` is an immutable token contract; plane transitions ADD a level, never reorder. (moriodcacjp.cocolog-nifty.com/odcanime/2007/11/book_b795.html; note.com/animeteniwoha/n/n9c4f4071071d; AWN "Animation Layout: OL/UL".)
- **Kumi-sen (組線):** strict registration polylines where cel touches BG (feet on stairs, hands on frames), duplicated into both assets. (Masuyama ⑧; ameblo.jp/lapislazuli2019/entry-12823845694.html.)
- **Registration standards:** ACME 3-peg; AJA layout paper standard Fr01 (camera frame 10"×5.625" 16:9, safety 90%, scan 110%); settei height charts as the relative-scale SSOT. (blog.academyart.edu/evolution-of-a-peg/; aja.gr.jp/jigyou/chousa/aja_layout; DeeDee Studio.)
- History: Miyazaki/Takahata standardized layout-centered production on *Heidi* (1974) — "the animation adapts to the backgrounds," ~300 layouts/week. (fullfrontal.moe/animation-fundamentals-a-short-history-of-layout/; animetudes.com/2021/07/18/heidi-girl-of-the-alps/.)

### 2.B Visual-novel sprite grammar + webtoon studio pipelines

- **Tachi-e conventions:** waist/thigh-up standard crop, base pose + enumerated expression diffs; engines position sprites at **named stage slots** (NScripter `l/c/r`; KiriKiri `left/left_center/center/right_center/right`; Ren'Py xalign 0/0.5/1; Naninovel percent slots), always **bottom-anchored**. (vndev.wiki/Sprite; krkrz.github.io KAG3 tag reference; renpy.org/doc/html/transforms.html; naninovel.com/guide/characters; binaryheaven NScripter tutorial.)
- **Scale registration:** sprites authored so **eye-line ≈ BG horizon**; tallest head just under frame top; shared height chart (hikaku-sitatter.com) — never per-image scaling; sprite ≈ 2/3–1.0 frame height for the display band, masters at 1.4–2× for zoom headroom. (Lemma Soft t=50492/t=47691/t=23117 via search extraction — paraphrase, direct fetch 403; vnpaths.com sprite + BG guides; tips.clip-studio.com/en-us/articles/5445.)
- **When sprites-over-BG reads natural vs fake:** works because the BG set is *built as a stage* — eye-level camera, ONE camera height across the whole BG library, low horizon, empty center stage, interest at edges/midground; close-ups get BG **blur/darken/desaturate**. Documented failure modes = ours: camera-height mismatch, lighting mismatch, overbaked sprite shading, occupied foreground. (vnpaths.com/how-to-make-visual-novel-backgrounds/; forsythiaproductions.itch.io Of Sense and Soul devlog/480454 — dolly-zoom = sprite scale-up + BG defocus; eyematerror.itch.io devlog/976396 — clipped Multiply/Overlay ambient + Add(Glow) rim to sit sprites.)
- **Webtoon factories:** camera angle is fixed at the **conti/콘티 storyboard** stage; BG team shoots a saved-scene camera from a 3D location file (SketchUp/ACON3D or CSP 3D), LT-converts to line+tone; characters drawn over, snapped to the **perspective ruler auto-derived from the 3D camera** — the mainstream mechanism for character/BG geometric agreement. Division of labor: sketcher/inker/colorist/BG artist ≈ 1 episode per 3–5 days; Kenaz ≈ 135 creators/80–100 titles-yr. (tips.clip-studio.com/en-us/articles/5071, /11224, /11512; help.clip-studio.com Perspective_Rulers + Set_camera_angle + LT-conversion manuals; how-to-sketchup.com webtoon-backgrounds articles; comicsbeat.com Sleepy-C/REDICE interview; acon3d.com; UMass WEBTOON art-assistant posting; prnewswire.com Kenaz.)

### 2.C Film/VFX compositing — grounding math (line-art-applicable subset)

- **Horizon-ratio scale law** (Sedgwick 1973–83, via pmc.ncbi.nlm.nih.gov/articles/PMC2929966/ and link.springer.com/content/pdf/10.3758/BF03205483.pdf): for a level camera at height E, subject of height S with feet at image y_f and horizon y_h: `image_height / (y_f − y_h) = S / E` — scale is **linear in feet-Y**, zero at the horizon. Photoshop matte-painting procedure: anchor the transform at the horizon crossing and scale from there. (peachpit.com/articles/article.aspx?p=3150361&seqNum=2; canmom.art/animation/perspective-tricks.)
- **Eye-level crossing check:** standing camera (~1.55–1.65 m) → horizon through eyes of all standing adults; seated (~1.1–1.2 m) → chest/waist; low → ankles. (stephaniebower.blogspot.com "heads align at your eye level"; blog.chaos.com/best-practices-finding-the-right-perspective; portico.space "putting people in your renders".)
- **Contact shadow:** absence = "hovering"; two stacked Multiply layers, color sampled from plate shadows: core ellipse ≈0.8–1.0× subject width, 60–90% opacity, blur ≈5 px; ambient pool ×1.3–1.6, 20–40%, blur ≈25 px, gradient falloff. (photoshoptrainingchannel.com realistic-shadows; expertphotography.com how-to-make-a-shadow; imageworkindia.com floating-shadows; CSP anime-shadow recipes tips.clip-studio.com/en-us/articles/3874, ask.clip-studio.com id=52945.)
- **Occlusion interleave:** interposition is "one of the strongest pictorial cues to depth"; deliberately paste a plate foreground element ABOVE the subject; z-order monotonic with feet-Y (painter's algorithm). (ncbi.nlm.nih.gov/books/NBK11512/; fstoppers.com composite series pt.3; pixel-monkey.com "why your composite falls flat" — final checks: relative scale, shadow direction, occlusion logic.)
- **Edge/level hygiene (line-art applicable):** defringe 1–2 px (kill white/AA halo — the #1 paste giveaway); black/white level match (element ink/paper within plate range); depth attenuation = thinner/fainter lines with distance (canonical manga practice). Photoreal-only (skip): light wrap, grain match, chromatic aberration. (helpx.adobe.com fringe-pixels; photoshopcafe.com halo removal; cglounge.studio/journal/compositing-in-vfx; Brinkmann, *The Art and Science of Digital Compositing* 2nd ed. Ch.14; clipstudio.net/how-to-draw/archives/163108; en.wikipedia.org/wiki/Aerial_perspective.)
- **Scale anchors:** interior door 2.03 m; chair seat 0.46–0.51 m; table top 0.71–0.79 m; adults 1.65–1.8 m, eye 10–15 cm below crown. (up.codes; hernest.com; eurekaergonomic.com; portico.space.)

### 2.D Manga panel grammar — shot types × background classes

**Hypothesis verdict: VERIFIED with refinements.** Waist-up/bust figures conventionally sit on abstract background classes; full-perspective rooms belong to establishing/full-figure panels. Three independent evidence classes:

1. **Craft guidance:** "draw the detailed background in the wide/establishing panel; you don't need detailed backgrounds in every single panel; simplify for character-focused panels" (clipstudio.net design-tips; howtodrawrjr.substack.com — BG removal "only works *after* an establishing shot"; MediBang/Boords guides).
2. **Corpus data:** Japanese manga are dominated by **Mono panels** (single figure, minimal scene), Macros ≈ half as many, Micros ≈10% (Cohn, "Framing Attention in Japanese and American Comics", pmc.ncbi.nlm.nih.gov/articles/PMC3449338/). The environment lives in the Macro/establishing panels; the reader retains it.
3. **A named symbol system fills the non-literal BG slot:** manpu/keiyu — flowers=affection, sparkle=admiration, bubbles=soothing, betaflash=realization, tare-sen=dread, kakeami=suspense, odoro=unease (en.wikipedia.org/wiki/Manga_iconography; japanesewithanime.com/2020/04/background-effects; tcj.com "The Structure of Expressions in Manga" — Natsume Fusanosuke's 形喩).

Refinements: (1) pros use MORE long shots than amateurs, not fewer — "the more successful a Manga is, the more 'Long-shots' are used"; ≥1 per spread (SILENT MANGA AUDITION, manga-audition.com/japanesemanga101_011/); the abstract-BG bust is *purchased* by nearby rendered-BG panels. (2) partial/simplified BG (1–3 signature motifs) is a distinct middle class for spatial retention (mangaflow.studio paneling basics).

Shot vocabulary + beat mapping (full tables in the agent report; encoded as spec §6): establishing (mandatory per scene — Klaus Janson via comicbookglossary.wordpress.com; McCloud *Making Comics* ch.1) · hiki/long · full-figure · medium/waist (ウエストショット) · bust-up (バストアップ) · CU · ECU · insert/object (Cohn Micro) · OTS · POV · fukan/aori angles · hiki-goma page-turn hook (manga-audition.com #013) · tobira-e chapter splash · beat panel (identical repeat = pause, tvtropes Beat Panel) · **pillow shot** — figure-free scenery pause, the Ozu lineage manga inherits via aspect-to-aspect transitions; the iyashikei backbone (Burch via bfi.org.uk pillow-shots feature; McCloud *Understanding Comics* ch.3). Crop hygiene: never crop at a joint (companyfolders.com cropping guide; Clayton Barton). 180°/eyeline: hold left/right speaker sides across a dialogue run (engineeredd.medium.com "Comics and the 180 degree rule"; rivkah.com camera-conventions). Flashback = black gutters (tvtropes Flashback Effects). Frame-break bleed = emphasis currency, spend sparingly (SMA #011).

## 3. Synthesis — the Phoenix scheme (four pillars, all adopted)

1. **Metadata (anime layout + settei):** every banked asset carries `composition_meta` — camera angle bucket, eye-level %, ground/anchor slots with feet lines, crop class, anchor point, light azimuth, real heights. The V5 decompose pair is our bank-system cel+BG pair: geometry single-sourced, cross-referenced, legal by construction.
2. **Legality (VN stage grammar + manga Table B):** a deterministic crop×bg_class matrix; headline row: **waist_up × full_render = ILLEGAL** (unless diegetic pair) — the operator's floating half-person becomes structurally impossible. Defocus-derived plates (blur of the SAME room) are the default dialogue-bust stage: retention for free.
3. **Grounding ops (VFX math + anime BOOK):** horizon-ratio scale replaces min-fit; feet/seat anchored to slot lines; mandatory two-ellipse contact shadow; occluder BOOK layer cropped from the plate itself; defringe + ink-level match.
4. **Grammar (manga craft):** beat → shot_type → legal recipe; scene invariants (establishing mandatory, abstract-only-after-establishing, re-establish triggers, ≥1 long shot per screen-run, figure-free pillow panels, side consistency).

Full scheme: `docs/specs/MANGA_COMPOSITION_GRAMMAR_SPEC.md` (schema §4, gates §5, grammar §6, manifest/ops §7–8).

## 4. Gap analysis (delta to today)

See spec §9 for the build-lane table. Headline: **no re-rendering and no new models required for the pilot** — the whole scheme is annotation (sidecar JSONs) + deterministic PIL ops + lookup gates + a manifest-lint. The only systemic bank gap it surfaces is the already-logged need for object-free L0 plate variants (contract spec §8.2) and per-slot pose coverage at scale. The scheme deliberately stays inside the §1.3 image-first boundary: no 3D, no camera solver; hand-annotated eye-levels first, heuristics only if annotation cost bites at catalog scale.

## 5. Pilot proof plan

Spec §10: annotate 1 plate + 2 cutouts, assemble 4 panels (establishing with grounding ops / bust-over-defocus / insert macro / reaction-over-tone) vs the current naive paste as control; gates pass on the four, fail on the control; byte-verified artifacts; zero GPU; a few Tier-1 hours.

## 6. Recommendation

**Adopt-industry synthesis** (not any single system, not our own invention):

- Anime layout/bank system is the *right discipline* but assumes a human layout artist per cut — we encode its invariants (eye-level, angle buckets, pairs, BOOKs, contact lines) as metadata + gates instead.
- VN stage grammar is the *right legality model* for dialogue/reaction beats but too theatrical for establishing shots — we adopt its crop×BG rules and defocus convention, not its fixed stage.
- VFX math supplies the *only formula in the system* (horizon-ratio) plus shadow/occlusion/edge recipes — small, deterministic, PIL-expressible.
- Manga grammar is the *decision layer* that makes one bank tell many stories: most panels legally need NO room render at all, which multiplies bank leverage — the economic argument for the whole scheme.

Rationale for synthesis over any single adoption: our constraint set (deterministic, GPU-free assembly; single-character iyashikei first; image-first boundary; existing L0–L4 taxonomy) intersects all four industries but matches none exactly. Every rule in the spec carries its industry citation; nothing was invented where a source existed.

**Six-layer status at close:** scheme = SPECCED. Pilot = planned (would take it to EXECUTED-REAL). Nothing above SPECCED is claimed.

**2026-07-07 post-close update:** the §5 pilot executed and merged as PR #4689 (gate module + 3 sidecars + byte-verified 4-panel strip vs naive-paste control; see the pilot dir FINDINGS.md). Scheme status now: SPECCED with §10 pilot EXECUTED-REAL; assembler integration remains ABSENT.

---

*Raw agent reports (4 × ~400-line, with all URLs) retained in session transcript; key citations carried inline above.*
