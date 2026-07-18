# Genre-First Writing Pilot — Verdict + Writing Path

**Date:** 2026-07-01  
**Branch:** `agent/manga-genre-first-pilot-20260701` (clean worktree off `origin/main`)  
**Doctrine bar:** Genre/story leads; self-help topic subtly embedded (shown, not lectured).

---

## Discovery (pre-write)

| Series | Genre | Topic | EI author | SSOT plan |
|---|---|---|---|---|
| `cognitive_clarity__en_US__psychological_thriller__series01` | psychological_thriller | boundaries | Mira Dewpath | `The Line You Don't Cross` |
| `stabilizer_healing__en_US__workplace_drama__series01` | workplace_drama | burnout | Brook Dewpath | `The Last to Leave the Office` |
| `stillness_press__en_US__iyashikei__series02` | iyashikei | somatic_healing | Dove Softwind | `The Warmth of Small Rooms` |

**Schema reused:** `chapter_script_writer_handoff` — same as `the_alarm_is_lying` gold pilot (`artifacts/manga/chapter_scripts/.../ep_001.yaml`).

**Craft bibles honored:**
- Thriller: assumption planted, caption/art gap, diffuse threat, widened-gap ending (`psychological_thriller.md`)
- Workplace: meeting deadline hook, caption/smile irony, chibi release, commute landing, no sermon (`workplace_drama.md`)
- Iyashikei: weather-first, high silence, environmental correlatives, no emotional labeling (`iyashikei_minimalism.md`)

**Judgment method:** Blind-read each script for (1) would a reader pick this up for the **genre story**? (2) is the topic **shown** through plot/body or **lectured**?

---

## Per-script genre-first verdict

### 1. `cognitive_clarity__en_US__psychological_thriller__series01/ep_001.yaml`

| Criterion | Verdict | Evidence |
|---|---|---|
| Story leads? | **PASS** | Compliance investigation frame; paranoia grammar (locked door → notebook); Marcus as institutional pressure, not wellness coach |
| Topic subtle? | **PASS** | Boundaries via after-hours access trail + unsent "yes" + report sent while hypothesis may be wrong — no "you need boundaries" copy |
| Genre bible? | **PASS** | Opens on confident read of orderly office (panels 1–4); ends on caption/art contradiction (panels 22–25) |

**Risk to watch at scale:** Analyst internal monologue can drift into CBT explainer — keep mechanism in **plot evidence**, not brain diagrams (contrast: `the_loop_is_not_thinking` ch02 failure mode from status audit).

---

### 2. `stabilizer_healing__en_US__workplace_drama__series01/ep_001.yaml`

| Criterion | Verdict | Evidence |
|---|---|---|
| Story leads? | **PASS** | Q3 review deck crisis; peer contrast (Ren); institutional night office as setting |
| Topic subtle? | **PASS** | Burnout via knuckle-white tumbler grip, untouched food, "Just left" lie at 8:26 PM — never named burnout |
| Genre bible? | **PASS** | Meeting hook (1–3); chibi death-metal insert (14); end-of-day train/convenience landing (18–23) |

**Honest note:** Panel 14 chibi is mandatory pressure valve — without it, chapter skews heavy; reconnect to slide twelve (panel 15) per bible.

---

### 3. `stillness_press__en_US__iyashikei__series02/ep_001.yaml`

| Criterion | Verdict | Evidence |
|---|---|---|
| Story leads? | **PASS** | Small-room autumn slice; second cup, neighbor parcel, indigo cloth — reader comes for atmosphere |
| Topic subtle? | **PASS** | Somatic healing in shoulders (5), cloth weight (22), toe flex (25) — zero therapy vocabulary |
| Genre bible? | **PASS** | Weather hook (1); ~40% silent panels; no cliffhanger; baseline return (26) |

**Strongest doctrine fit of the three** — closest to `the_alarm_is_lying` register without copying its smoke-detector beat.

---

## Writing path (scale note)

**To author a series on-doctrine at scale:**

1. **Pick from SSOT** — `manga_series_plans/{locale}/` supplies `genre`, `topic`, `manga_author` (EI persona), format routing.
2. **Read lane bible Section 1 + 6** — market contract + failure modes before plotting.
3. **Story Architect handoff** (when automating) — carrier beats embedded mid-chapter, not first/last (`MANGA_STORY_ARCHITECT_SPEC.md`).
4. **Chapter Writer** — panel-level YAML in `chapter_script_writer_handoff` shape; Tier-1 Claude for en_US; Qwen after doctrine proven for CJK.
5. **Genre-first QC** — lint against bible failure modes (iyashikei emotional labeling; thriller supernatural; workplace preachy advice).
6. **Render** — separate GPU-gated step (`chapter_runner` DAG); not part of writing.

**EI author system + craft bibles — sufficient?**

| Layer | Sufficiency | Gap |
|---|---|---|
| Craft bibles (20 lanes) | **Sufficient** for human/Claude authoring | Need automated bible-lint in `chapter_qc` |
| EI `manga_authors/` (263 YAML) | **Sufficient for voice/persona** | Not yet wired as mandatory Chapter Writer input in production path |
| Story Architect + Teaching Library | **Specified, thin throughput** | Automate genre_blueprint → beat sheet before panel prose |
| `writer_stub` vs Tier-1 writer | **Gap** | DAG defaults to stub for CI; scale needs explicit Tier-1 writer dispatch for en_US pilots |

**Do not duplicate:** catalog generators, new bibles, parallel script schemas.

---

## Decisions

| ID | Decision | Alt rejected |
|---|---|---|
| Q-MANGA-PILOT-GENRES-01 | Thriller / workplace / iyashikei spread | 3× same brand — insufficient doctrine proof |
| Q-MANGA-PILOT-LOCALE-01 | en_US only | CJK before en_US gold — risks topic-forward Qwen drift |
| Q-MANGA-PILOT-WORKTREE-01 | Clean worktree off `origin/main`; surgical `git add` only | Work on poisoned main tree — PR #245 trap |

---

## NEXT_ACTION

1. Operator review 3 scripts (opened in Finder).
2. Merge pilot PR → fan out ep_002–014 on best genre-fit series (iyashikei + workplace first — lowest didactic risk).
3. Wire `manga_authors/{persona}.yaml` into Chapter Writer prompt assembly.
4. **Renders:** queue via `pscli` / `weekly_manga_rollout.py` when CJK GPU lane free — writing lane is unblocked now.
