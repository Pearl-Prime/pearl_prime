# Manga Blind-10 Protocol (R7 / Milestone M6)

<!-- NEW-ARTIFACT-JUSTIFIED: ratifies audit §3-R7 proposal into an operator-runnable
acceptance lane. Zero paid APIs. Registry row: manga_blind10_protocol_v1. -->

**Authority:** `artifacts/qa/MANGA_VISION_CONFORMANCE_AUDIT_2026-07-03.md` §R7 ·
`docs/specs/MANGA_100PCT_PRODUCTION_ROADMAP_2026-07-03.md` §6 ·
`docs/PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md` Layer 4 analog
**Taxonomy label:** **SPECCED** (protocol ratified; no sample **PROVEN-AT-BAR** yet)
**Date ratified:** 2026-07-08
**Verified repo HEAD at authoring:** `6e44f414335c4faa3ba63642dce0c7beb962f69e`

---

## 0. Purpose and honesty constraints

M6 is the **acceptance lane** for R7 (judged at top-Japanese-pro bar). It is **not**
a backdoor to claim M5 solved, M3 complete, or manga shippable.

- `register_gate` PASS, story-authored gate PASS, and internal craft audits are **at most**
  `authored candidate` / `EXECUTED-REAL`. None imply **PROVEN-AT-BAR**.
- Until a blind-10 run **PASSES** under this protocol, no manga axis, series, or catalog
  row may be claimed `bestseller`, `pro bar`, or `shippable at register`.
- INTERIM layers (`provenance: INTERIM`) may appear in pre-screen or wiring proofs but
  **must not** enter the human judge packet as final art.

---

## 1. Sample shape

| Parameter | Rule |
|---|---|
| Episodes | **10** per run (`blind10`) |
| Genre spread | **≥ 4 distinct `genre_id` values** across the 10 slots |
| Locale mix | Match production intent: en_US lanes → EN-market pros; ja_JP lanes → JP-native pros |
| Episode completeness | Full episode (webtoon vertical strip or paged export), **not** a demo strip or character sheet |
| Byte floor | Every panel in judge packet **≥ 50_000 bytes** (same stub-as-done law as M1) |
| Assembly path | Prefer M5 bank-assembled episodes (`assemble_from_bank.py`, provenance table 0 INTERIM). Legacy full renders (April `composed_v3_qwen`) allowed **only** as slot-01 pilot until M5 E2E lands |

**Roadmap first sample (target queue):** M5's first **4** assembled end-to-end episodes
+ April `stillness_press` ep_001 re-render or successor.

---

## 2. Comparator selection rules

Comparators are **published, professional, same-register** excerpts — not Phoenix output.

### 2.1 Matching dimensions (all required)

1. **Genre register** — same `genre_id` family (e.g. `iyashikei`, `action_battle`, `psychological_thriller`)
2. **Demographic lane** — shojo / shonen / seinen / josei / webtoon vertical as applicable
3. **Locale market** — JP comparators for ja_JP candidates; US/EU webtoon or print for en_US
4. **Format** — vertical scroll episode or magazine page spread comparable to candidate delivery

### 2.2 Count and sourcing

- **2 comparators per candidate episode** (fixed)
- Source: operator-licensed scans, purchased volumes, or publisher marketing assets **with provenance recorded** in `COMPARATOR_REGISTRY.yaml`
- **Do not** use AI-generated or Phoenix-internal images as comparators
- Research anchors: `artifacts/research/manga_quality_bar/01_iyashikei_craft_study.md` and genre craft bibles under `docs/research/manga_craft/`

### 2.3 Blind presentation

- Judges receive **candidate + 2 comparators** without Phoenix branding
- Randomize left/middle/right (or A/B/C) per judge session; record seed in scorecard
- Judges score **only the candidate slot** on the rubric; comparators calibrate the 4–5 anchor

---

## 3. Judge packet contents (per episode)

```
judge_packets/slot_<NN>_<short_id>/
  PACKET.md              # operator assembly instructions
  episode_manifest.yaml  # series_id, genre, locale, panel list, paths
  comparators.yaml       # 2 entries: title, creator, volume/chapter, page range, image paths
  panels/                # symlinks or copies of candidate panels (operator prepares)
  README_FOR_JUDGE.md    # blind instructions (no repo jargon)
```

**Operator prepares** a single PDF or password-protected folder per judge containing:

1. Cover sheet: slot ID, genre, locale, panel count (no Phoenix series name)
2. Candidate episode pages in read order
3. Comparator excerpt A and B (5–12 pages each, genre-matched)
4. Blank scorecard from `judge_packets/TEMPLATE_scorecard.yaml`

---

## 4. Scoring rubric (8 axes, 1–5)

See `RUBRIC.md` for anchored definitions. Axis IDs:

| ID | Axis |
|---|---|
| A1 | Panel-flow readability |
| A2 | Page-turn / tobira placement |
| A3 | Character consistency |
| A4 | Lettering craft |
| A5 | Genre-trope fluency |
| A6 | Anatomy / hands |
| A7 | Tone / screentone quality |
| A8 | Dialogue register |

Scale: **1** = amateur / broken · **3** = competent serial · **4** = professional publishable · **5** = top-tier reference

---

## 5. Pass / fail rule

**Per episode (candidate only):**

- Compute per-axis **median** across all human judges (minimum **3** judges per locale lane)
- **PASS** iff: median ≥ **4** on **every** axis AND no axis median **< 3**

**Blind-10 run (system level):**

- **PASS** iff: **≥ 8 of 10** episodes PASS per-episode rule
- **WARN** iff: 6–7 of 10 PASS
- **FAIL** iff: ≤ 5 of 10 PASS

Record aggregate in `VERDICT.md` + per-judge `scorecards/judge_<id>_slot_<NN>.yaml`.

---

## 6. Qwen2.5-VL pre-screen role (Tier 2 — Pearl Star)

Pre-screen is **not** blind-10. It filters obvious failures before human recruitment.

| Item | Rule |
|---|---|
| Model | `qwen2.5vl:7b` via local Ollama on Pearl Star (Tier 2) |
| Harness | `scripts/video/run_frame_judge.py` pattern — panel image vs `scene_description` from chapter script |
| Threshold | Default **80/100**; episode median must be ≥ **75** to advance to human packet |
| Scope | All panels in candidate episode |
| On FAIL | Episode **withheld** from judge queue; file `pre_screen/<slot>_prescreen.json` |
| On PASS | Operator still runs human blind-10 — pre-screen does **not** confer PROVEN-AT-BAR |

Runbook: `pre_screen/PRESCREEN_RUNBOOK.md`

---

## 7. Artifact layout (this run)

```
artifacts/qa/manga_blind10_2026-07-08/
  PROTOCOL.md                 # this file
  OPERATOR_MEMO.md            # go/no-go checklist
  CANDIDATE_SET.tsv           # 10 slots, live eligibility
  COMPARATOR_REGISTRY.yaml    # comparator assignments
  RUBRIC.md                   # anchored 8-axis rubric
  VERDICT.md                  # run outcome (NOT_RUN until judges finish)
  BLOCKERS.md                 # explicit blockers
  judge_packets/              # per-slot packets + template
  pre_screen/                 # Tier-2 pre-screen runbook
  scorecards/                 # (empty until run) per-judge YAML
```

---

## 8. Tier policy

| Step | Tier | Who |
|---|---|---|
| Protocol authoring | Tier 1 | Operator-present Claude Code |
| Qwen2.5-VL pre-screen | Tier 2 | Pearl Star / Ollama unattended OK |
| Human blind judging | Operator | Operator-recruited pros — **not delegable to agents** |
| Paid vision APIs | **BANNED** | CI policy |

---

## 9. Exit proof (M6 DONE)

M6 is **DONE** only when a dated folder contains:

- `VERDICT.md` with blind-10 **PASS** or honest **FAIL**
- `scorecards/` populated for ≥ 3 judges × 10 slots
- `CANDIDATE_SET.tsv` rows marked `judged=yes`
- At least one episode path with M5 assembly (`provenance` 0 INTERIM) in the winning set

**Current state:** protocol **SPECCED**; run **NOT_RUN** — see `BLOCKERS.md`.
