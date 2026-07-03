# Manga 100% Production Roadmap — 2026-07-03

<!-- NEW-ARTIFACT-JUSTIFIED: consolidated execution roadmap ROUTING across the
existing ratified vehicles (MANGA-LAYERED-PIPELINE-V2-01 phases B–E, V5 layered
architecture, Phase 2X workstreams, MANGA_MARKET_INTEGRATION_V1_SPEC,
MANGA_PRODUCTION_OPERATIONAL_V1_SPEC, manga_mode_vessels, existing generators).
It replaces none of them; no prior doc sequences all R-axes to 100% with the
operator's stories-first law. Registry row added in the same PR. -->

**Authority inputs:** `artifacts/qa/MANGA_VISION_CONFORMANCE_AUDIT_2026-07-03.md`
(the honest baseline; R1–R8 table) + the operator vision (R1–R8).
**Sequencing law (operator):** STORIES FIRST → per-series IMAGE BANKS → layered
assembly at scale → locale rollout.
**Tier policy:** EN prose = Pearl_Writer (Claude, operator-present); CJK
adaptation = Qwen on Pearl Star; unattended steps = Gemma/Qwen; renders =
Pearl Star flux/qwen/animagine per V5. ZERO paid APIs.
**GPU law:** CJK atom lane holds priority (OPD-20260629-003); every manga
batch below is LOW-priority/off-hours until the operator re-ranks.

---

## 0. Where each R-axis stands (from the audit) → the lever that moves it

| Axis | Now | 100% means | Primary vehicle (existing) |
|---|---|---|---|
| R1 | 30% | 13-locale allocation chain, research→config→plans | MANGA_MARKET_INTEGRATION_V1_SPEC + Phase 2X.4 generator |
| R2 | 45% | every series a compete-grade genre story | Pearl_Writer batch lane + craft-bible completion (Phase 2X.3) |
| R3 | 25% | vessels consumed by story architect; apparatus researched | manga_mode_vessels.yaml + story_architect integration point |
| R4 | 8% | music-mode manga sub-spec + vessels wired | music-mode program docs (#1580 lineage) + vessels config |
| R5 | 34% | per-series banks + deterministic assembly at scale | V5 architecture + assemble_from_bank.py + V2-01 phases B–E |
| R6 | 40% | stories precede banks precede assembly, enforced | story-authored CI gate (M1) |
| R7 | 5% | blind-judged at pro bar | manga blind-10 protocol (audit §3-R7 proposal) |
| R8 | 35% | 13 locales × 37 brands full columns | Phase 2X.4/2X.5 generators + locale rollout waves |

---

## 1. Milestone M1 — Enforcement rails (dispatchable NOW, no GPU)

*The "memory→enforcement" close for this lane's three drift classes. Everything
else in this roadmap builds on rails that make lying-to-ourselves structurally
hard.*

| Deliverable | Detail | Exit PROOF |
|---|---|---|
| `scripts/ci/check_render_progress_bytes.py` | CI hard gate: any RENDER_PROGRESS.tsv row `status=ok` with `bytes < 50_000`, or referencing a path absent from the tree, FAILS the PR (stub-as-done kill) | Gate red on a synthetic stub fixture; green on April tree |
| Story-authored gate | Extend `bestseller_gate.py` substance checks into a render-queue **entry** gate: no series enters `queue_panel_renders.py` / assembly without a parsing chapter_script above the substance floor (listing-as-story kill) | Enqueue attempt on plan-only series exits non-zero with named reason |
| `scripts/ci/check_manga_wiring.py` | Every config under `config/manga/` must have ≥1 non-test consumer on a callable path or carry `status: unwired` in its header (unwired-config kill) | Gate flags manga_mode_vessels.yaml until M4 wires it |
| CLAUDE.md rule | Add: manga status claims MUST carry the six-layer taxonomy label; INTERIM assets never presentable as final | Rule text in CLAUDE.md |
| Provenance rail (landed this session) | `assemble_from_bank.py` refuses unlabeled layers; provenance table on every run | Already EXECUTED-REAL — `_provenance.json` in the demo dir |

Owner: Pearl_Dev. Entry gate: none. Budget: 0 GPU-h. **Blocked on: nothing.**

## 2. Milestone M2 — R1 allocation chain closed (dispatchable NOW)

1. Author `config/manga/locale_genre_allocations.yaml` — per-locale genre mix
   derived from the existing research triad; **encodes the CJK-genre-led vs
   Western-intent-led split** (Q-MANGA-02: US/West = illustrated self-help
   picture books for Gen Z/Alpha). Cite research doc+section per line (R1's
   verifiable chain). NEW-ARTIFACT-JUSTIFIED: the allocation layer exists
   nowhere; registry row in same PR.
2. Commission the missing research: it_IT, zh_SG (zero), hu_HU (upgrade),
   zh_HK (deferred per CJK plan §2). Owner: Pearl_Research. Tier 1.
3. Fix registry flags C-1/C-2 (zh_TW, fr_FR manga tracks missing from
   market_catalog_registry despite declared slices) per
   MANGA_MARKET_INTEGRATION_V1_SPEC §C.
4. Extend `generate_catalog_plan_from_strategic.py` (Phase 2X.4 vehicle) to
   consume the allocation file — plans become allocation-derived, closing
   research→allocation→plan.

Exit PROOF: allocation YAML with 13 locale blocks + research citations; 2X.4
generator run whose output diff shows allocation-driven genre mixes; C-1/C-2
closed in registry. Budget: 0 GPU-h. **Blocked on: nothing** (research
commissioning runs parallel).

## 3. Milestone M3 — R2/R6 stories first, at scale (the long pole)

*Stories before pictures, so this milestone precedes ALL bank/render scale-up.*

1. **Craft-bible completion** (Phase 2X.3 workstream, already proposed):
   44 uncovered genres → Pearl_Research synthesizes from the existing 19-bible
   pattern. Exit: 129/129 canonical genres covered.
2. **Pearl_Writer batch lane** (Tier 1): wave-author chapter scripts through
   the EXISTING orchestration (`run_manga_pipeline.py::run_one_book()` emits
   the handoff; Pearl_Writer replaces the stub at the chapter_script stage).
   Wave 1 = 37 en_US flagship series (1/brand, tentpole genre per brand from
   GENRE_PORTFOLIO_PLAN). Each script must pass the M1 story-authored gate +
   carry the craft-notes block the 16 existing scripts established.
3. **CJK adaptation lane** (Tier 2): Qwen on Pearl Star adapts en_US scripts
   for ja_JP/zh_CN/zh_TW/ko_KR(hold) per the existing
   `translate_chapter_script.py` path; ja_JP flagships get native-authored
   scripts (genre-led market, not translations) — Pearl_Writer.
4. **Vessel consumption is M4's wiring**, but scripts authored here must
   already USE the vessel (as ep_001's therapist does) — writer prompt cites
   the brand-mode vessel from manga_mode_vessels.yaml.

Exit PROOF: 37 en_US + 16 ja_JP-native scripts on main passing the entry gate
(byte-verified, craft-notes present); refuter-style spot audit of 5.
Owner: Pearl_Writer + Pearl_Research. Budget: 0 GPU-h (LLM: subscription/local
only). **Blocked on: M1 gates (soft), nothing hard.**

## 4. Milestone M4 — R3/R4 vessels wired + researched

1. Wire `manga_mode_vessels.yaml` into `story_architect.py` beat shaping +
   the chapter-writer prompt assembly (the two integration points the audit
   named). The M1 wiring gate flips green here.
2. Commission `docs/research/manga_craft/teacher_apparatus_per_genre.md` —
   the researched per-genre apparatus mapping R3 requires (upgrades the 3
   C-grade vessels; validates the 15×2 set against genre dossiers).
   Owner: Pearl_Research.
3. Author the missing authority doc the config cites
   (MANGA_MODE_WRAPPER_DESIGN.md) or re-point the citation.
4. **R4:** author `docs/specs/MUSIC_MODE_MANGA_V1_SPEC.md`
   (NEW-ARTIFACT-JUSTIFIED: zero music×manga treatment exists; registry row
   in same PR) applying music-mode's existing ideas (data-driven mix,
   first-person wrapper — PR #1580 lineage) to the 15 music vessels; then one
   pilot script (music-mode brand × romance) through the M3 lane.
5. Teacher-never-named stays enforced: add the name-scan (V3's method) to the
   story-authored gate.

Exit PROOF: story_architect run whose emitted beats differ with/without vessel
(diff artifact); apparatus research doc; music pilot script passing gates.
Owner: Pearl_Dev + Pearl_Research + Pearl_Writer. Budget: 0 GPU-h.
**Blocked on: M3 wave 1 (for the pilot script only).**

## 5. Milestone M5 — R5 banks + assembly at scale (GPU begins)

*Only after a series has a gate-passing story (R6 law).*

1. **Bank contract per series** (existing vehicles: scene_inventory /
   object_inventory / character_pose_inventory YAMLs — the stillness_en_01
   set is the template): author for each M3 flagship series.
2. **Bank renders** via V5 single-dispatch decompose
   (`render_v5_episode.py`, PR #1276 V5.1 2-stage merges first — review it,
   don't fork): per-panel layers saved per V5 §8 become bank assets;
   L1/L3/L4 rendered per contract spec §4.2/4.4/4.5 (the
   `RESUME_COMMANDS.sh` pattern from the demo, generalized). LOW priority
   per Q-MANGA-03 (~2–4 GPU-h pilot; ~40 GPU-h/series-bank estimated at
   13–28s/image).
3. **Face lock:** PuLID node install on Pearl Star (V2-01 Phase B workstream,
   already proposed — activate it) → per-series reference sheets; LoRA
   training (Phase C) only for flagships after PuLID proves insufficient
   (Q-MANGA-04 default). Exit per series: qa_face_distance pairwise ≤0.4
   across every episode appearance (now a wired gate, not a loose script).
4. **Assembly at scale:** `assemble_from_bank.py` (landed) driven by
   manifests generated FROM continuity_state (Milestone C generator,
   OPD-135 — gates ep_002+ dispatch; respect that gate) — panels → existing
   bubble/webtoon compose lane → episodes.
5. Anatomical negative-prompt pass = V2-01 Phase D workstreams (proposed →
   activate with Phase B).

Exit PROOF per series: bank manifest ≥ N plates/poses/objects ALL REAL
(provenance table 0 INTERIM); 1 episode assembled end-to-end; face-distance
gate green; validate_layer green. Budget: pilot 2–4 GPU-h (Q-MANGA-03), then
~40 GPU-h/series off-hours. **Blocked on: Pearl Star reachability + OPD-135
Milestone C for ep_002+; PR #3075 dispatch-bug lane (reference, don't race).**

## 6. Milestone M6 — R7 pro-bar protocol

1. Ratify the blind-judge protocol (audit §3-R7): 10 episodes × ≥4 genres ×
   2 published comparators each; human JP pros (operator-recruited);
   Qwen2.5-VL pre-screen on Pearl Star; 8-axis rubric; PASS = median ≥4, no
   axis <3; verdict artifact `artifacts/qa/manga_blind10_<date>/`.
2. First judged sample = M5's first 4 assembled episodes + the April ep_001.
3. Until a sample PASSES, no manga ships with any "bestseller/pro" claim —
   CLAUDE.md rule (M1) enforces the language.

Exit PROOF: VERDICT.md with per-judge scorecards. Budget: 0 GPU-h (pre-screen
minutes). **Blocked on: M5 first episodes + operator recruiting judges
(operator-tier).**

## 7. Milestone M7 — R8 locale rollout waves

- **Wave A (plans):** run the 2X.4/2X.5 generators with M2 allocations for the
  8 zero-plan locales (fr_FR first — strongest manga culture; then de_DE,
  es_ES, es_US, it_IT, hu_HU, zh_SG after their research lands; zh_HK after
  its deferred spec). ≤180-file PRs per locale (catalog scale-up doctrine).
- **Wave B (stories):** M3 lane per locale per its M2 allocation — Western
  lanes get the illustrated self-help picture-book shape (Q-MANGA-02), NOT
  genre-manga.
- **Wave C (banks/assembly):** M5 per flagship, copy-across decision doc
  first (upgrade copy-across from SPECCED: one analysis doc deciding which
  brands/series copy vs stand alone, per platform families config).
- **pt_BR (Q-MANGA-01):** joins the registry only by operator ratification
  (PR #1604 lineage), then enters Wave A.
- **ko_KR:** stays plan-complete/ship-gated (Q-MANGA-05).
- **Japan manga-only catalog:** proceeds per JAPAN_MANGA_ONLY_CATALOG_V1_SPEC
  once Q-MANGA-07 legal entity clears (operator-tier).

Exit PROOF per locale: grid row fully green in the conformance TSV re-run.
**Blocked on: M2 (allocations), operator Qs 01/05/07.**

---

## 8. Dispatch order + blocking summary

```
NOW (no GPU, no operator):   M1 rails → M2 allocation → M3 wave 1 (en_US 37)
                              └ M4 research + music sub-spec in parallel
ON Pearl Star return:        M5 pilot (Q-MANGA-03 envelope) → RESUME_COMMANDS.sh
ON operator answers:         Q-01 pt_BR · Q-03 GPU envelope · Q-05 ko_KR ·
                             Q-06 tentpole (rec: B) · Q-07 Japan legal entity ·
                             M6 judge recruiting
```

**Tentpole D1 options (Q-MANGA-06):** (A) keep warrior_calm ja_JP as battle
and re-author its profile; (B) re-point to the cultivation-burnout hybrid its
authored script already proves (**recommended** — story asset exists, zero
new risk); (C) drop the tentpole flag for ja_JP. Not self-ratified.

**Reuse ledger (nothing re-authored):** run_manga_pipeline.run_one_book ·
generate_catalog_plan_from_strategic.py · translate_chapter_script.py ·
render_v5_episode.py + PR #1276 · continuity_state_generator (OPD-135) ·
manga_mode_vessels.yaml · bestseller_gate.py · validate_layer.py ·
qa_face_distance.py · bubble_render/webtoon_compose · pearl_star_t2i_enqueue ·
saturation snapshot branch (review-gated reuse for M5 throughput) · V2-01
phase workstreams B–E (activate, don't recreate) · Phase 2X.3/2X.4/2X.5
workstreams (activate).

**Genuinely new artifacts (each NEW-ARTIFACT-JUSTIFIED + registry row):**
assemble_from_bank.py + manifest schema + make_object_sprite.py (landed —
true void: no bank-assembly lane existed) · locale_genre_allocations.yaml
(M2) · teacher_apparatus_per_genre.md (M4) · MUSIC_MODE_MANGA_V1_SPEC.md
(M4) · the three M1 CI gates · this roadmap.
