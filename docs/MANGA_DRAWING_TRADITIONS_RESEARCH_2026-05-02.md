# Manga Drawing Traditions + Character Individuation — Research (2026-05-02)

**Status:** AUTHORITY (new, this PR — research-only).
**Branch:** `agent/manga-drawing-traditions-research-20260502`
**Scope:** Per-genre drawing-tradition deep-dive (top-8 priority genres, 17 schema-complete stubs); 12-axis character-individuation pipeline spec; cross-genre blending rules (20 pairs); popular-genre ranking (Q4); license-clean corpus framework (Q5 — partial); diagnosis of 22 stillness_press dashboard PNGs.
**Companion deliverables:**
- `docs/CHARACTER_INDIVIDUATION_PIPELINE_SPEC_2026-05-02.md`
- `config/manga/drawing_tradition_per_genre.yaml`
- `config/manga/cross_genre_blending_rules.yaml`
- `config/manga/character_design_axes.yaml`
- `config/manga/character_design_template.yaml`
- `artifacts/research/popular_genre_ranking_2026-05-02.md`
- `artifacts/research/per_genre_drawing_tradition_corpus_2026-05-02.yaml`
- `artifacts/research/average_face_problem_eval_2026-05-02.md`
- `artifacts/research/mangaka_exemplar_registry_2026-05-02.yaml`
- `artifacts/research/dashboard_22_failure_diagnosis_2026-05-02.md`

**Cross-references (SHA-pinned):**
- Cookbook research: `docs/COMFYUI_FLUX_MANGA_PROMPTING_RESEARCH_2026-04-29.md` @ `2881dd970bf2433e2225800ac6f73b1dd0281be5` (#802)
- Community audit: `docs/COMMUNITY_ASSETS_AUDIT_2026-04-29.md` @ `f4c50142b63df134d2f34c10a4a761bd9015c910` (#803)
- Community LoRA roster: `artifacts/research/community_lora_roster_2026-04-29.yaml` @ `f4c50142b63df134d2f34c10a4a761bd9015c910` (#803)

---

## §0 The two failures this research addresses

The operator inspected the stillness_press manga dashboard at
`/Users/ahjan/phoenix_omega/.claude/worktrees/dreamy-nightingale-7bd099/artifacts/catalog_visibility/stillness_press_manga_dashboard.html` (22 series; 22/22 with images; distribution: 15 healing, 2 dark_fantasy, 2 psychological_horror, 2 slice_of_life, 1 isekai). Two visual-quality failures observed:

1. **Drawing tradition not honoring genre.** Horror panels drawn with the same line economy as healing. Mecha framed like Western concept art. Dark fantasy looks like a fantasy book cover. The drawing *style* per genre — line weight, ink density, screentone, panel framing, expression vocabulary — isn't differentiated even when the prompt says different things.

2. **Character look-alike problem.** Across 22 main_character.png images, the protagonists read as variations of the same person — same face shape, same age, same hair construction, same expression range. No two characters are visually distinct enough to function as separate series leads.

**Direct visual inspection of 6 representative PNGs (this research PR) confirmed both failures.** The 4 operator-flagged failures (jp_07/08 dark_fantasy, jp_11 psychological_horror, jp_16 isekai) plus 2 working anchors (jp_01 healing, pressure_map slice_of_life) — 5 of 6 protagonists collapse to a near-identical face geometry. Full diagnosis at `artifacts/research/dashboard_22_failure_diagnosis_2026-05-02.md`.

---

## §1 What the prior PRs established (cookbook + audit)

Before stating what this PR adds, the prior PRs' findings:

**Cookbook PR #802** (`2881dd970bf2433e2225800ac6f73b1dd0281be5`):
- §0: schnell-at-cfg-4 oversampling is the single-largest available quality win (engine fix needed before any prompt-level fix)
- §1.2: hybrid pipeline — SDXL+Pony for B&W panel, FLUX-dev for color webtoon — but...
- §2.2: per-genre token framework (manga panel + screentone + artist anchor)
- §6: PuLID-FLUX for FLUX pipelines, IP-Adapter FaceID for SDXL — but...

**Community Audit PR #803** (`f4c50142b63df134d2f34c10a4a761bd9015c910`) — CRITICAL FINDING that revises the cookbook:

**FLUX-dev, Pony V6, Illustrious-XL, NoobAI are ALL commercial-blocked.** Phoenix Omega ships commercial product. The commercial-clean stack is:
- **Qwen-Image (Apache 2.0)** primary
- **Animagine XL 4.0 (RAIL++-M)** secondary
- **FLUX-schnell (Apache 2.0)** legacy fallback

InstantID + IP-Adapter-FaceID are also commercial-blocked (InsightFace AntelopeV2 dependency). Use **PuLID-FLUX-FaceNet** (`lldacing/ComfyUI_PuLID_Flux_ll`) — Apache 2.0 + commercial-clean facenet-pytorch VGGFace2.

**This PR's token recommendations all map to the commercial-clean stack.**

---

## §2 What this PR adds — the drawing-tradition layer

The cookbook established WHICH tokens trigger each genre. This PR adds WHAT each genre's drawing tradition actually LOOKS like — line, ink, expression, panel framing, palette, mangaka exemplars — and how those visual properties map onto the commercial-clean bases.

### §2.1 Per-genre A–H structure

For each of the **top-8 priority genres** (full deep spec) and **17 deferred genres** (schema-complete stubs), this PR documents:

- **A. Line tradition** — weight profile, stroke economy, construction-line discipline, inking pressure
- **B. Ink density + tonal grammar** — quantified black-fill ratios, screentone strategy, halftone-vs-solid, hatching style, white-space treatment
- **C. Body language + expression vocabulary** — face proportions, expression frequency cap, pose vocabulary, hand drawing tradition
- **D. Panel + framing tradition** — camera distance distribution, page rhythm, background detail density, speed-line + impact-frame usage
- **E. Color treatment** — palette per sub-register, color anchor mangaka, B&W vs spot vs full-color
- **F. Genre-specific drawing rules** — the "don't do this" list (3-5 forbidden patterns per genre)
- **G. Mangaka exemplar set** — 5-8 mangaka per top-8 genre (2-3 named anchors per deferred-stub genre); each with works, dates, public-reference URL, one-line note. **Phase-tagged** wherever the mangaka has material career-register shifts (Otomo, Inoue, Tezuka, Mizuki, Urasawa, Asano, Miura, Toriyama, Hara, Murata, Shirow, Junji Ito, Amano, Azuma, Arawi, Higashimura, Yarō Abe — 17 phase-tagged mangaka in this PR's `mangaka_exemplar_registry`).
- **H. Token mapping for commercial-clean bases** — Animagine XL 4.0, Qwen-Image, FLUX-schnell — positive prompt fragments + negative prompt + empirical caveats per base

Full structured spec: `config/manga/drawing_tradition_per_genre.yaml`.

### §2.2 The top-8 priority genres

Operator preempted the top-8 to avoid gating on Q4 ranking. This PR's full A–H spec covers:
1. **healing/iyashikei** — operator's tentpole working register (15/22 dashboard); WHY it works on Animagine 4.0 base alone documented
2. **dark_fantasy** — operator-flagged failure (2/22); Berserk-style ink density vs the rendered "fantasy book cover" failure
3. **psychological_horror** — operator-flagged failure (2/22); SUBGENRE SPLIT recommended (`_sparse` Ito-pole vs `_dense` Maruo-pole) because one config can't trigger both poles
4. **mecha** — multi-PR-flagged failure; Yasuhiko/Otomo/Shirow/Kondo lineage vs the rendered "Western concept art" failure
5. **romance (josei-adult)** — operator-explicitly NOT shojo-teen; Asano/Okazaki/Higashimura tradition
6. **slice_of_life** — 2/22 working; SOL/iyashikei/comedy boundary documented
7. **fantasy_adventure (incl. isekai)** — widest-spectrum genre; 4 mainline registers + 3 isekai sub-registers
8. **comedy** — central rule "must use deformation"; Arawi anchor

### §2.3 The 17 deferred-stub genres

Per operator I1+ override: schema-complete stubs (all A-H sub-blocks present, populated only with `status: deferred_phase2` + 1-line scope note + 2-3 named mangaka anchors). The cookbook follow-up PR fills content; structural rework is forbidden.

The 17: battle, sports, mystery, horror (general), workplace, essay, food, family, procedural, historical, cultivation, sci_fi_cyberpunk, supernatural_everyday, school, memoir, social_issue, graphic_medicine. Plus battle_internal as a sub of battle.

---

## §3 The character individuation pipeline (Q3)

The 12-axis vocabulary (`config/manga/character_design_axes.yaml`):

1. face_shape, 2. eye_geometry, 3. nose_construction, 4. mouth_jaw, 5. hair, 6. build, 7. wardrobe_register, 8. posture_default, 9. age_signaling, 10. skin_treatment, 11. accessories, 12. color_signal

Each axis: allowed values + mangaka-tradition vocabulary (Adachi-fringe vs CLAMP-fringe vs Asano-fringe; Toriyama-spike vs Oda-anatomy vs Frieren-twin-tail) + diffusion-token reliability per commercial-clean base.

**9 of 12 axes are "lockout axes"** — the constraint solver checks these against the existing catalog and rejects new entries that collide on ≥5 same-brand or ≥7 cross-brand locked axes.

**Forbidden axis combinations** documented (e.g., `bow_mouth + josei` rejected pre-solver because modern josei-adult has moved past 1990s shojo conventions).

**The pipeline** (`docs/CHARACTER_INDIVIDUATION_PIPELINE_SPEC_2026-05-02.md`): author fills template per series → constraint solver validates → prompt builder emits axis tokens → render pass with optional PuLID-FaceNet reference → QA harness pairwise face-distance metric.

**Implementation roadmap**: 6 phases, ~10 engineering days. Out of scope for this research PR; queued as follow-up engineering PRs.

**Q3.D average-face problem** (`artifacts/research/average_face_problem_eval_2026-05-02.md`): partial — qualitative ranking based on prior PR knowledge. Animagine 4.0 has the strongest attractor (heavily anime-trained); Qwen-Image has the weakest. Empirical literature scan + model comparison deferred to follow-up PR.

---

## §4 Cross-genre blending rules (20 pairs)

`config/manga/cross_genre_blending_rules.yaml` documents the 20 most common cross-genre pairs from the brief, each with:
- Which genre's drawing tradition wins (line economy, ink density, panel framing)
- Which genre's expression / palette wins
- Token-weighting rule per commercial-clean base
- Failed-blend mode catalog (named drift mode + corrective)
- Working anchor mangaka

**Token-weighting empirics across the 3 commercial-clean bases:**
- **Animagine XL 4.0** — `(token:1.2)` syntax via lpw_stable_diffusion_xl pipeline; most expressive (https://huggingface.co/docs/diffusers/using-diffusers/weighted_prompts)
- **FLUX-schnell** — supports weighting via sd_embed `get_weighted_text_embeddings_flux1` but capped at 1.3 effective ("doesn't necessarily help for newer models like Flux which already has very good prompt adherence")
- **Qwen-Image** — Qwen2.5-VL T5-family encoder; **inert to (token:weight) syntax** — must rewrite as natural-language prose ("strongly emphasizing X")

**Operator's flagged failing pair — mecha + iyashikei** ("After the Cockpit"): the token-stack is fighting itself; mecha tokens have stronger training-set gravity. Fix: force iyashikei dominance via `(soft iyashikei atmosphere:1.4)` + move mecha to silhouette + Qwen-Image preferred over Animagine because Qwen de-emphasizes "mecha" tokens vs Animagine's anime-trained bias.

---

## §5 Q4 popular-genre ranking

`artifacts/research/popular_genre_ranking_2026-05-02.md` — full Q4 ranking.

**Empirical global ranking** (2024-2026 evidence-weighted, per Oricon JP / ICv2 US / Webtoon / anime-pipeline / Phoenix portfolio):
1. **shonen-battle / dark-fantasy hybrids** — JJK / Dandadan / Berserk; Phoenix portfolio UNDERWEIGHTED
2. **fantasy_adventure** (incl. isekai) — Frieren / Solo Leveling / 32 new isekai 2025
3. **romance** — Webtoon romance = 39.4% global webtoon share
4. **healing/iyashikei** — Phoenix's #1 by allocation mass (920 pct, 3.4× next)
5. mystery / cozy-mystery
6. horror / supernatural-comedy
7. **sports** — operator's preempted top-8 EXCLUDES; empirical evidence forces inclusion
8. slice_of_life
9. mecha (niche-but-high-monetization)
10. comedy

**Two flags for operator:**
- **Sports is empirically top-7-8** but Phoenix has only 4 rows / 14 pct. High-ROI portfolio expansion if any teacher brand has sports affinity.
- **Fantasy_adventure under-allocation** (20 rows vs ~50 for romance/mystery/SoL) is the largest portfolio-vs-empirical gap.

**Operator's preempted top-8 is portfolio-defensible, not globally-empirical** — the healing-tentpole strategy is intentional given the teacher-brand audience.

---

## §6 Corpus framework (Q5 — partial)

`artifacts/research/per_genre_drawing_tradition_corpus_2026-05-02.yaml` — partial. Framework + stubs only; full corpus assembly deferred to follow-up PR.

**License framework** (deferred to follow-up):
- Public-domain manga (Japanese 70-year rule; Tezuka 2059 horizon; Mizuki 2085)
- Creative-Commons-licensed manga (deferred discovery via Wikimedia / Internet Archive / creator sites)
- Public-domain reference art — Hokusai Manga (PD), Kuniyoshi ukiyo-e (PD), Yoshitoshi (PD), classical sumi-e
- Publisher sample-page policies (deferred — Shueisha / Kodansha / Shogakukan / Kadokawa / MangaPlus)
- Synthetic reference (commercial-clean: derivative of Phoenix's own model weights, not training data)
- Manga109 license (deferred verification)
- CLIP-similarity-based curation against Phoenix's own 624-PNG catalog

---

## §7 Dashboard 22-failure diagnosis (this PR's smoke-test target list)

Full at `artifacts/research/dashboard_22_failure_diagnosis_2026-05-02.md`.

**Aggregate findings:**
- 22 of 22 need workflow fix (engine — schnell-at-cfg-4 issue from cookbook §0)
- 22 of 22 need character-individuation pipeline (12-axis solver before regen)
- 5 of 22 need LoRA + multiple fixes (dark_fantasy + psychological_horror + isekai)
- 0 of 22 currently pass without changes (every PNG inherits at least the look-alike attractor failure)

**Estimated cost to regenerate all 22 with corrective spec:**
- Engine fix (operator-effort, $0 API)
- Cookbook prompt fix (~30 min operator)
- 12-axis YAMLs (~5.5 hr operator total for 22)
- Per-character regen ($0.04 × 22 = **$0.88** API)
- Per-character LoRA training (only for named cast — most don't need at this stage; PuLID-FaceNet sufficient)

**Total: <$5 API + ~6-8 hr operator time.** ROI per fix is enormous relative to cost.

---

## §8 Top-line operator-facing answers (CLOSEOUT-aligned)

1. **Most popular 5 genres globally (empirical):** battle, fantasy_adventure (incl. isekai), romance, healing/iyashikei, mystery
2. **Highest-ROI drawing-tradition fix to apply now:** mecha — currently failing across cookbook + audit + this PR; corrective is medium anchor (`monochrome, manga, comic, panel`) + subject anchor with framing (`mecha, mecha pilot, cockpit interior, low angle shot`) + negative western-concept basin. Combined with engine fix from cookbook §0, drift severity drops dramatically.
3. **Average-face problem diagnosis:** Animagine 4.0 has the strongest attractor (heavily anime-trained); Qwen-Image has the weakest. Recommended workaround layered approach: 12-axis prompt stack → PuLID-FaceNet reference → per-character LoRA for named cast → pairwise face-distance QA gate.
4. **Character individuation pipeline ready to build?** YES — spec is complete in this PR; gating items for follow-up PR are the constraint solver implementation (~1 engineering day) and the QA harness threshold calibration.
5. **Cross-genre pair that consistently fails:** mecha + iyashikei ("After the Cockpit"). Recommendation: prefer Qwen-Image over Animagine for this blend; force iyashikei dominance via `(soft iyashikei atmosphere:1.4)` + move mecha to silhouette.

---

## §9 NEXT_ACTION (post this PR)

1. **Update cookbook YAML** with `drawing_tradition:` block per genre (separate PR; uses this PR's `drawing_tradition_per_genre.yaml`)
2. **Implement character individuation constraint solver** per pipeline spec (separate engineering PR; ~1 day)
3. **Regenerate the 22 stillness_press dashboard PNGs** with corrective prompts + engine fix + 12-axis YAML lock (separate PR; gates on smoke-test pass)
4. **Train per-genre LoRAs** for the corrective failures (separate PR per LoRA): psychological_horror (high), dark_fantasy (high), mecha (high — Phoenix-native if Super Robot Diffusion XL doesn't transfer to Animagine 4.0)
5. **Backfill drawing_tradition_per_genre.yaml** for the 17 deferred genres (separate cookbook follow-up PR; structural rework forbidden — fill content only)
6. **Run the deferred follow-up PRs** for character-individuation literature scan (Mark Crilley + Manga University + ArcFace metric calibration) and corpus license research (Manga109 + Tezuka PD + publisher sample policies)
7. **Calibrate sports + fantasy_adventure portfolio gap** — operator decision: lift sports allocation (high-ROI per Q4) and/or lift fantasy_adventure allocation across solar_return / qi_foundation / devotion_path?
8. **Cross-pollinate findings** into Phase 2 of the production campaign

---

## §10 Coverage summary (CLOSEOUT)

| Item | Coverage | Notes |
|---|---|---|
| Genres covered (full A-H per Q1) | 8 of 25 (top-8 deep) + 17 schema-complete stubs | Operator I1+ |
| Cross-genre pairs (Q2) | 20 of 20 | Complete |
| Character-design axes (Q3.A) | 12 of 12 | Complete; per-axis vocabulary partial (deferred sources) |
| Mangaka exemplars per top-8 genre | 5-8 each (avg ~7) | Per Q1 H |
| Mangaka phase-tagged | 17 (no count cap per I10+) | Tagged where shift is material |
| Average-face workarounds (Q3.D) | 8 ranked workarounds | Empirical literature scan deferred |
| Popular-genre ranking (Q4) | top-10 with rationale | Operator's preempted top-8 validated/refuted per slot |
| License-clean corpus per genre (Q5) | framework + stubs only | Full corpus deferred |
| Dashboard 22 PNGs diagnosed | 22 of 22 (6 visual + 16 metadata-derived) | Per I3 |
| Cookbook + community-audit cross-references | All SHA-pinned with section numbers | Per operator constraint |

---

## §11 Citation grounding

- Wikipedia mangaka pages (~50 cited)
- ANN / Comics Beat / Manga Brog / The Comics Journal — primary mangaka interviews
- CivitAI / OpenArt / HuggingFace model cards — token validation
- Oricon / ICv2 / BookScan / Webtoon — Q4 ranking
- arXiv (FLUX paper, partial) — average-face problem
- HuggingFace diffusers + sd_embed — token-weighting empirics

Date range: 2024-2026 for community/diffusion sources; mangaka-tradition citations span 1947 (Tezuka Astro Boy) through 2026 (Frieren).

---

*End of MANGA_DRAWING_TRADITIONS_RESEARCH_2026-05-02.md.*
