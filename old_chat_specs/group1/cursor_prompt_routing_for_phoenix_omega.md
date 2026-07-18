# Prompt routing for Phoenix Omega agent
_Exported on 4/16/2026 at 19:27:25 GMT+8 from Cursor (3.1.15)_

---

**User**

Act as my Phoenix Omega agent prompt router.
Before generating any prompt, read:
- docs/SESSION_UNITY_PROTOCOL.md
- docs/PEARL_ARCHITECT_STATE.md
- artifacts/coordination/ACTIVE_PROJECTS.tsv
- artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
- artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv
Follow the “Universal router prompt (prompt-building chats)” section in docs/SESSION_UNITY_PROTOCOL.md exactly.
When I give you a plain-English task, do not solve it. Return only the final paste-ready startup prompt for the next agent chat.

---

**Cursor**

Reading the required protocol and coordination files to act as the prompt router.



Searching for the "Universal router prompt" section — it wasn't in the portion of SESSION_UNITY_PROTOCOL we read.



I read everything you listed. **`docs/SESSION_UNITY_PROTOCOL.md` in this repo does not contain a section titled “Universal router prompt (prompt-building chats)”.** The file ends at the Quick Reference table (through line 123). `docs/agent_brief.txt` points at that section, but the section itself is not in the tracked protocol file, so there is nothing here to follow “exactly” for router formatting.

I did load:

- **SESSION_UNITY_PROTOCOL** — STARTUP_RECEIPT / CLOSEOUT_RECEIPT, authority reads, stop rules  
- **PEARL_ARCHITECT_STATE** — routing anchors, PM vs Architect, drift patterns  
- **ACTIVE_PROJECTS** — `proj_state_convergence_20260328` (active, Pearl_PM, state convergence / salvage)  
- **ACTIVE_WORKSTREAMS** — many rows; notable **active / in_progress / blocked / pending** include e.g. `ws_research_citation_gaps_20260330` (active), `ws_research_pipeline_activation_20260330` (blocked on citation gaps), `ws_rolling_projection_system_20260410` (in_progress), `ws_teacher_manga_triptych_20260410` (active), `ws_lfs_setup_20260410` (active), `ws_catalog_quality_analysis_20260410` (active), `ws_video_image_washout_fix_20260411` (active), `ws_bestseller_spines_20260410` (active), `ws_pearl_news_daily_publish_20260411` (active), `ws_exercise_journey_system_20260411` (in_progress), `ws_v2_somatic_loader_stacking_20260412` (in_progress), `ws_ei_v2_bestseller_corpus_20260413` (active), `ws_micro_book_differentiation_20260412` (pending — owner decision), `ws_legacy_template_real_archives_v3_20260411` (blocked — vendor zips), `ws_atom_gap_fill_20260410` (pending), etc.  
- **SUBSYSTEM_AUTHORITY_MAP** — subsystem → authority_doc / config_path / owner_agent  

This message is **router setup**, not a concrete plain-English work task, so there is **no** paste-ready executor startup prompt to emit yet.

**Next step:** Send one plain-English task (what you want done). I will **not** solve it; I will **only** return the final paste-ready startup prompt for the next agent chat—using the protocol’s **STARTUP_RECEIPT** fields and authority/workstream constraints, and mirroring whatever structure you add under “Universal router prompt” once that section exists in `SESSION_UNITY_PROTOCOL.md`. If you can paste that missing section here, I will align outputs to it on the next turn.

---

**User**

sai_maa_final.mp4 coresponding image at sec 25 is bad. redo the prompt describing the eyes of the woman

---

**Cursor**

Locating `sai_maa_final.mp4` and related prompt assets so the startup prompt includes accurate paths.



```
You are a Phoenix Omega execution agent. Obey docs/SESSION_UNITY_PROTOCOL.md: emit STARTUP_RECEIPT before any work, then CLOSEOUT_RECEIPT when done. One workstream; stay inside declared WRITE_SCOPE.

OWNER TASK (verbatim)
- Asset: sai_maa_final.mp4 — the still/image aligned with ~25 seconds is unacceptable.
- Deliverable: revise the image-generation prompt so the woman’s eyes are described correctly (natural, consistent, on-brief for the scene); then regenerate or re-run the step that produced that frame so sec ~25 matches the corrected eye description. Do not ship until that timestamp looks right.

ROUTING (from repo coordination)
- PROJECT_ID: proj_state_convergence_20260328
- SUBSYSTEM: video_pipeline (Pearl_Video primary; Pearl_Dev if scripts/config only)
- AUTHORITY_DOCS (read before edits): docs/SESSION_UNITY_PROTOCOL.md; docs/DOCS_INDEX.md; docs/VIDEO_PIPELINE_SPEC.md; docs/VIDEO_PIPELINE_COMPLETE_GUIDE.md; docs/VIDEO_PIPELINE_VISUAL_BRIEF.md; docs/VIDEO_IMAGE_MASTER_PROMPT_SPEC.md; config/video/* as referenced by the job; scripts/video/README.md
- CONFLICT CHECK: consult artifacts/coordination/ACTIVE_WORKSTREAMS.tsv — avoid overlapping edits with active video workstreams (e.g. ws_video_image_washout_fix_20260411, ws_teacher_manga_triptych_20260410) unless this job is explicitly the same branch/owner; if overlap, narrow scope or STOP with HANDOFF_TO Pearl_PM per protocol.

DISCOVERY (required first)
- Locate sai_maa_final.mp4 and the pipeline metadata (job.json, manifest, or folder sibling to the mp4) that maps timestamps to source prompts / flux or ComfyUI inputs.
- Identify which YAML/JSON/text prompt produced the ~25s keyframe (scene id, slide index, or segment label).

EXECUTION
- Rewrite only the eye-related portion of that prompt: clear anatomy (iris/sclera/lids), gaze direction, expression, lighting on the eyes, and negatives for common failures (wall-eyed, misaligned pupils, glassy stare, wrong ethnicity cues if fixed elsewhere, etc.). Keep the rest of the composition stable unless eyes cannot be fixed without it.
- Re-run the minimal regeneration path for that segment; replace outputs in the expected artifact tree; spot-check the new frame at ~25s (ffprobe/ffmpeg extract or pipeline QC).

WRITE_SCOPE (declare precisely in STARTUP_RECEIPT after discovery)
- Typical: config/video/* prompt banks or scene YAML; scripts/video/* only if the bug is in prompt assembly; artifact outputs under the sai_maa / tiktok (or equivalent) directory — list exact paths once found.
- OUT_OF_SCOPE: unrelated teachers, unrelated videos, global pipeline refactors, docs the owner did not ask for.

EVIDENCE
- Note old vs new prompt snippet (or file diff summary), output path(s), and how you verified sec ~25.

STARTUP_RECEIPT — fill all fields before edits:
AGENT:
TASK:
PROJECT_ID: proj_state_convergence_20260328
SUBSYSTEM: video_pipeline
AUTHORITY_DOCS:
READ_PATH_COMPLETE:
WRITE_SCOPE:
OUT_OF_SCOPE:
BLOCKERS:
READY_STATUS:
```

---

**User**

run the prompt on comfyUI on pearl star server , get the new pic , edit the vid, put new pic in , take old pic out. 

---

**Cursor**

```
You are a Phoenix Omega execution agent. Follow docs/SESSION_UNITY_PROTOCOL.md: emit STARTUP_RECEIPT before any work; CLOSEOUT_RECEIPT when finished. One workstream; binding WRITE_SCOPE.

OWNER TASK (verbatim)
- Run the revised image prompt on ComfyUI on the Pearl Star server, retrieve the new still, edit the video so the new picture replaces the bad one and the old picture is removed (context: sai_maa_final.mp4 — defective frame ~25s, especially eyes; use the eye-corrected prompt from the prior handoff or reproduce that revision if missing).

PEARL STAR / COMFYUI (repo truth)
- Read docs/INTEGRATION_CREDENTIALS_REGISTRY.md (Pearl Star section): SSH host `pearl_star`, ComfyUI :8188, FLUX primary.
- Read docs/UBUNTU_PRODUCTION_SERVER_SETUP.md for ComfyUI layout on the server if paths are needed.
- Local integration: scripts/video/flux_client.py (`call_comfyui`, `COMFYUI_URL`) and docs/VIDEO_IMAGE_MASTER_PROMPT_SPEC.md — prefer existing workflow/API patterns over ad-hoc UI clicking when automatable.

ROUTING
- PROJECT_ID: proj_state_convergence_20260328
- SUBSYSTEM: video_pipeline (Pearl_Video / Pearl_Dev)
- AUTHORITY_DOCS: docs/SESSION_UNITY_PROTOCOL.md; docs/VIDEO_PIPELINE_SPEC.md; docs/VIDEO_PIPELINE_COMPLETE_GUIDE.md; docs/VIDEO_IMAGE_MASTER_PROMPT_SPEC.md; docs/INTEGRATION_CREDENTIALS_REGISTRY.md; config/video/* as used by the job
- Check artifacts/coordination/ACTIVE_WORKSTREAMS.tsv for concurrent video edits; avoid conflicting branches or declare STOP + handoff if blocked.

EXECUTION PLAN
1) Locate sai_maa_final.mp4, its sidecar job/manifest, and the exact time range or still index for the bad segment (~25s).
2) On Pearl Star: run ComfyUI generation with the corrected eye prompt (same workflow JSON the pipeline uses if available under scripts/image_generation/comfyui_workflows/ or equivalent). Save the new PNG/JPEG with a clear filename next to the project artifacts.
3) Video edit: replace the old embedded still/clip with the new image — match resolution, duration, and any Ken Burns/zoom the original used; re-encode only if required; preserve audio sync.
4) Remove or archive the superseded still from the artifact tree so only the canonical asset remains (or document archive path in CLOSEOUT).
5) Verify playback at ~25s; note ffmpeg/ffprobe commands used.

WRITE_SCOPE (fill after discovery in STARTUP_RECEIPT)
- Typical: artifacts/video/... (sai_maa / tiktok paths); optional scripts/video/* only if assembly is broken; do not touch unrelated teachers’ outputs.

BLOCKERS
- If ComfyUI unreachable, SSH key missing, or source video/prompt lineage unclear — STOP_REASON + HANDOFF_TO owner with exact gap.

STARTUP_RECEIPT — complete before edits:
AGENT:
TASK:
PROJECT_ID: proj_state_convergence_20260328
SUBSYSTEM: video_pipeline
AUTHORITY_DOCS:
READ_PATH_COMPLETE:
WRITE_SCOPE:
OUT_OF_SCOPE:
BLOCKERS:
READY_STATUS:
```

---

**User**

Here’s a tighter **diagnostic grid** for this manuscript as a *book*.

## Scorecard

| Category                   |      Score | Why                                                                                                      |
| -------------------------- | ---------: | -------------------------------------------------------------------------------------------------------- |
| **Hook / first-page pull** |   **6/10** | Some striking lines and strong anxiety imagery, but too many aphorisms before stable narrative grounding |
| **Reader trust**           |   **3/10** | Raw assembly leaks, repeated blocks, and doctrinal certainty weaken authority                            |
| **Cohesive flow**          | **2.5/10** | Content feels stacked, not guided; abrupt jumps between scenes, prompts, doctrine, exercises             |
| **Emotional resonance**    | **6.5/10** | Best scenes and one-liners land well; many readers will feel seen                                        |
| **Therapeutic usefulness** | **5.5/10** | Some practices are helpful, but pacing and integration are uneven                                        |
| **Commercial readability** | **3.5/10** | Too repetitive and visibly unclean for broad-market momentum                                             |
| **Voice consistency**      |   **4/10** | Swings between grounded modern somatic writing and absolute spiritual proclamation                       |
| **Originality**            |   **5/10** | Some fresh body-based lines, but repeated spiritual language becomes generic                             |
| **Chapter architecture**   |   **3/10** | Chapters do not yet feel like escalating units with distinct jobs                                        |
| **Publish readiness**      | **1.5/10** | Not ready in current form because of artifact leakage and duplication                                    |

## Overall

### As a **bestseller candidate**

**3.5/10 now**

### As a **cohesive book**

**2.5/10 now**

### As a **therapeutic / healing book**

**5.5/10 now**

### As a **great book**

**3/10 now**

## Why it misses “great book” status

A great healing book usually gives the reader four feelings:

* “This author understands me.”
* “This author knows where they’re taking me.”
* “Each chapter deepens the last.”
* “I am changing as I read.”

This manuscript gets the **first** feeling sometimes.
It often misses the other three.

The reader is recognized, but not consistently led.

## What is strongest right now

The best material is:

* short body-truth lines about burnout and anxiety
* modern life scenes with physical detail
* a few compassionate reframes
* occasional case-study passages that feel human rather than assembled 

When the manuscript says things like:

* the body knows before the calendar does
* performance is intact while the nervous system is not
* the reader is functioning but already fraying

—it becomes compelling.

## What is weakest right now

The biggest failures are:

* **massive duplication**
* **visible variant headers**
* **insufficient transitions**
* **same insight phrased over and over instead of advancing**
* **too many exercises dropped in bulk**
* **unstable promise: somatic psychology vs spiritual frequency doctrine** 

## Chapter-level pattern I’m seeing

From the uploaded text, the chapters appear to follow roughly this pattern:

1. aphorisms
2. scene cluster
3. reflection questions
4. healing exercises
5. doctrine statements
6. more scenes
7. more repeated lines
8. case study
9. repeated lines again

That pattern is the core problem. It does not create strong reading momentum because the parts do not feel like they are unfolding with intention.

## Honest verdict

This is **not yet a bestseller-quality manuscript**.
It is **not yet a cohesive great therapeutic book**.
But it **does have enough strong raw writing to justify revision**.

The cleanest summary is:

> **Strong fragments, weak assembly, medium therapeutic promise, low current publish quality.**

## What would move it fastest toward “great”

If I were triaging this for fastest improvement, I would do only these five things first:

1. **Delete all duplicate repeated line clusters**
2. **Strip all raw scene headers / generation artifacts**
3. **Pick one dominant frame**: grounded somatic healing first, spiritual layer second
4. **Give each chapter one thesis and one emotional job**
5. **Reduce exercises to only the one or two that directly follow the chapter’s insight**

That alone could raise it a lot.

## Realistic potential after revision

If cleaned and restructured well, I think this could move to roughly:

* **Bestseller potential:** **6.5–7/10**
* **Cohesive flow:** **7/10**
* **Therapeutic value:** **7–8/10**

The ceiling is there. The current draft just is not near it yet.

If you want, I’ll do the next pass as a **chapter-by-chapter red/yellow/green table** and tell you exactly which parts to keep, cut, and rewrite first.


---

**Cursor**

Reading the manuscript structure to produce a chapter-by-chapter red/yellow/green triage aligned with your scorecard.



Your scorecard matches what’s in `docs/book.txt`: the manuscript really does stack the same **scaffolding** under different chapter hooks, which explains the low **reader trust** and **flow** scores.

Evidence is structural, not subjective. The pair

- “Underneath the feeling is a simple mechanism: you can act inside uncertainty…”  
- “The point is that you can act inside uncertainty…”  

appears **verbatim in essentially every chapter** (and often twice). The same is true of rotating **meta bridge lines** (“Stay with the moment…”, “That pause is doing more…”, “Here is where the chapter stops talking…”, “Let the chapter land in the body…”, “For example, the quickest way to feel the draft that never sends…”). **Venice Boulevard / marine haze** and the **homework + group chat** (or **one page of math, hands won’t move**) blocks are **copy-pasted** across many chapters. That is exactly “visible assembly” and “massive duplication.”

Below is a **chapter-by-chapter red / yellow / green** pass: **green = keep (maybe tighten)**, **yellow = rewrite/restructure around one job**, **red = cut or replace wholesale** (usually boilerplate or notes-to-self).

| Ch | R / Y / G | Keep / cut / rewrite (priority order) |
|----|-----------|----------------------------------------|
| **Note + Intro** | **Y** | **Keep** disclaimer and “body recognized the title” (strong). **Cut** duplicate companion-URL lines in Conclusion (same URL three times). **Yellow**: one clear promise: somatic Gen Alpha first, Adi Da frame introduced as lens, not as alternating dialect. |
| **1** | **Y** | **Green**: opening paras (message draft), desk/chat scene (one clean pass without “marine haze” unless you mean it). **Green**: 20-year meditator story. **Red**: repeated mechanism block; meta lines (“Stay with the moment…”, “Now notice what shifted…”) unless you rewrite *one* transition style for the whole book. |
| **2** | **Y** | **Green**: opener (paths pressure), friends’ falling-out story, “mirror / holding” theme. **Red**: same mechanism paragraph; duplicate “draft that never sends” example if Ch1 already owns it. |
| **3** | **Y** | **Green**: expectations opener; father/anger case (strong). **Red**: mechanism block; **yellow**: silence practice — keep *or* swap for something smaller; don’t stack three exercises. |
| **4** | **R→Y** | **Red**: late-night math block is **identical** to Ch5/6/7/8/15/19 — **one chapter** may keep a version; **delete from the rest**. **Green**: “What are you doing right now?” / “holding myself together” exchange (excellent). **Yellow**: heart/Bright paragraph — fold into voice choice (see your triage #3). |
| **5** | **R→Y** | Same **duplicate math scene** as Ch4 — **cut scene** or replace with **school-choice-specific** scene. **Green**: father/daughter story. |
| **6** | **R→Y** | Same math scene again — **cut**. **Green**: social media opener; counselor silence story. **Yellow**: contraction journal — keep only if Ch6’s job is “notice body in real time.” |
| **7** | **R→Y** | Math scene again — **cut**. **Green**: “calm as contraction” / breakdown story (very strong). |
| **8** | **R→Y** | Math scene again — **cut**. **Green**: panic-in-grocery story; opener about many voices. **Red**: “draft that never sends” line if overused. |
| **9** | **R→Y** | **Green**: public development opener; public-speaking story. **Red**: recycle desk scene if it’s the chat version you’ve used before — **one variant only** for the whole book. |
| **10** | **R→Y** | **Green**: replaying hurtful comment opener; ER nurse story. **Yellow**: half-breath exercise — one per chapter max. |
| **11** | **R→Y** | **Green**: hurt-by-someone opener; Socratic student Q&A (good capstone energy). **Red**: duplicate desk/friend post scene. |
| **12** | **R→Y** | **Green**: fitting in vs being yourself opener; forgiveness paragraph. **Red**: duplicate desk scene. |
| **13** | **R→Y** | **Green**: embarrassment/permanence opener. **Red**: duplicate desk scene; trim “turning point” if Ch11/12 already did climax. |
| **14** | **R→Y** | **Green**: college pressure opener; self-improvement treadmill story. **Red**: duplicate desk scene. |
| **15** | **Y** | **Green**: “indecision is grief” line (only Ch15 uses this variant — **keep** and make Ch15’s *thesis* “grief before decision”). **Red**: math scene if still duplicate; mechanism block. |
| **16** | **R→Y** | **Green**: “supposed to know what you want” opener; not-enough / achievement story. **Red**: desk/chat if duplicate. |
| **17** | **R→Y** | **Green**: performance/identity opener; retirement/emptiness story. **Red**: desk scene duplicate. |
| **18** | **R→Y** | **Green**: climate/inequality opener; pursuer/withdrawer cycle (strong). **Red**: desk scene duplicate. |
| **19** | **R→Y** | **Green**: forces shaping identity; spiritual comparison room story. **Red**: math scene duplicate. |
| **20** | **Y** | **Green**: family anxiety loop opener; elderly woman summary (good closing case). **Yellow**: breath exercise — align with Conclusion; **red**: mechanism block. |
| **Conclusion** | **Y** | **Green**: “still here” framing. **Red**: **two of three** identical free-guide sentences — **one** CTA only. |

**Fastest alignment with your own five triage moves**

1. **Delete duplicate clusters** — the mechanism pair + repeated scenes are the highest ROI cuts.  
2. **Strip meta headers** — any line that sounds like an outline to the author (“Here is where the chapter stops…”) should go or become *invisible* narration.  
3. **One dominant frame** — keep Adi Da vocabulary in a **defined glossary chapter** or appendix, or translate “Bright / prior / separate self” into **plain somatic language** in-line and use capitals sparingly.  
4. **One thesis per chapter** — after you pick it, **every** case study should prove *that* thesis only.  
5. **One exercise** — move the rest to the companion; in-book, **name** the companion instead of reproducing long instructions.

If you want a **next pass** in-repo, the natural owner lane is **Pearl_Writer / Pearl_Editor** on `docs/book.txt` (or a forked `book_v2.txt`) with a strict rule: **no pasted block may appear twice**. I can also turn this table into a **paste-ready agent startup prompt** for that revision pass if you want it routed the same way as your ComfyUI tasks.

---

**User**

create prompt 

---

**Cursor**

Paste this into a **new agent chat** as the full instructions:

```
You are a Phoenix Omega execution agent (Pearl_Writer + Pearl_Editor). Follow docs/SESSION_UNITY_PROTOCOL.md: emit STARTUP_RECEIPT before edits; CLOSEOUT_RECEIPT when done.

TASK
Revise docs/book.txt into a publishable Gen Alpha overthinking manuscript. The current draft has strong fragments but weak assembly: massive duplication, recycled scene blocks, visible “meta bridge” lines, and uneven voice (somatic modern vs Adi Da doctrinal certainty). Apply the triage below; do not expand scope to other books or unrelated docs.

PROJECT / ROUTING
- PROJECT_ID: proj_state_convergence_20260328
- SUBSYSTEM: treat as authoring + teacher_mode voice; consult specs/PHOENIX_V4_5_WRITER_SPEC.md where it applies to voice/consistency; docs/SESSION_UNITY_PROTOCOL.md for receipts.
- Read before writing: docs/SESSION_UNITY_PROTOCOL.md; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv (avoid conflicting active editorial workstreams).
- Check artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv if you touch governed config; this task is normally docs-only.

NON-NEGOTIABLE EDITS
1) DELETE duplicate clusters: Remove every repeated verbatim block. The pair “Underneath the feeling is a simple mechanism…” + “The point is that you can act inside uncertainty…” must appear at most ONCE in the entire book (or be replaced by a single short cross-chapter reminder in one agreed place).
2) STRIP generation artifacts: Remove or rewrite lines that read as author notes to self, e.g. “Stay with the moment a second longer…”, “That pause is doing more than slowing you down…”, “Here is where the chapter stops talking…”, “Let the chapter land in the body…”, “For example, the quickest way to feel the draft that never sends…” unless rewritten as invisible narrative glue.
3) ONE scene vocabulary for recycled settings: The “marine haze / Venice Boulevard / homework / group chat / one page of math hands won’t move” material appears in many chapters. Keep at most ONE full version of each *type* of scene; every other chapter gets a NEW scene tied to THAT chapter’s thesis (specific, fresh detail).
4) ONE dominant frame: Grounded somatic + Gen Alpha life FIRST. Adi Da terms (Bright, separate self, prior freedom, Conscious Process) either: (a) introduced once clearly and used consistently with gentler plain-language glosses, or (b) concentrated in front matter + occasional short gloss—avoid swinging between clinical-somatic and absolute proclamation without transition.
5) ONE thesis + ONE emotional job per chapter: State each chapter’s job in one sentence early; cut anything that doesn’t serve it.
6) EXERCISES: In-body, at most ONE short practice per chapter; move detailed instructions to the companion URL only, with a single in-text pointer. Deduplicate overlapping practices across chapters.
7) CONCLUSION: The free-guide URL appears multiple times; keep ONE clear CTA.

DELIVERABLE
- Primary: updated docs/book.txt (or, if safer, create docs/book_revision_v1.txt and leave book.txt unchanged—pick one approach and declare it in STARTUP_RECEIPT WRITE_SCOPE).
- Optional short appendix: docs/book_revision_changelog.md listing removed duplicate classes and chapter thesis lines (only if the owner wants traceability; skip if not requested).

VERIFICATION (before CLOSEOUT)
- Grep or search: the mechanism block and meta-bridge phrases must not repeat across chapters.
- Read aloud (or skim) Ch1, Ch8, Ch15, Ch20 for flow and voice drift.

STARTUP_RECEIPT — fill completely before first edit:
AGENT:
TASK:
PROJECT_ID:
SUBSYSTEM:
AUTHORITY_DOCS:
READ_PATH_COMPLETE:
WRITE_SCOPE:
OUT_OF_SCOPE:
BLOCKERS:
READY_STATUS:
```

---

**User**

verify and prompts to finish: Act as my Phoenix Omega agent prompt router.
Before generating any prompt, read:
- docs/SESSION_UNITY_PROTOCOL.md
- docs/PEARL_ARCHITECT_STATE.md
- artifacts/coordination/ACTIVE_PROJECTS.tsv
- artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
- artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv
Follow the “Universal router prompt (prompt-building chats)” section in docs/SESSION_UNITY_PROTOCOL.md exactly.
When I give you a plain-English task, do not solve it. Return only the final paste-ready startup prompt for the next agent chat.

---

**Cursor**

Verifying the five sources and whether the Universal router section exists in the protocol.



## Verification (read completed)

| Source | Status |
|--------|--------|
| `docs/SESSION_UNITY_PROTOCOL.md` | Present through **Quick Reference** (line 123). **There is still no section titled “Universal router prompt (prompt-building chats).”** Anything that pointed at that section is referencing missing text. |
| `docs/PEARL_ARCHITECT_STATE.md` | Present; use for **where work belongs** vs PM, anchors, drift patterns. |
| `artifacts/coordination/ACTIVE_PROJECTS.tsv` | **One active row:** `proj_state_convergence_20260328` — State Convergence / salvage cleanup, Pearl_PM. |
| `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` | Large TSV; many **completed** rows; **active / in_progress / blocked / pending** rows still exist (e.g. research citation gaps **active**, research pipeline **blocked** on citation gaps, various video/ei/editor lanes — executor must grep `active\|in_progress\|blocked\|pending` before overlapping writes). |
| `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv` | Present; subsystem → `authority_doc` / `owner_agent`. |

**Follow “Universal router … exactly”:** **Not possible** until that section exists in `SESSION_UNITY_PROTOCOL.md`. The finishing prompts below close that gap: one prompt **adds** the section; the other **runs** the router with the same rules inlined.

---

## Prompt 1 — **Pearl_Architect / Pearl_PM** (add the missing protocol section)

Paste into a new agent chat:

```
You are Pearl_Architect (or Pearl_PM). Task: add the missing section to docs/SESSION_UNITY_PROTOCOL.md.

READ FIRST: docs/SESSION_UNITY_PROTOCOL.md; docs/PEARL_ARCHITECT_STATE.md; artifacts/coordination/ACTIVE_PROJECTS.tsv; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv; artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv.

EDIT: Insert a new section after “Quick Reference” (or before it, your choice) titled exactly:

## Universal router prompt (prompt-building chats)

Section body must specify ALL of the following, in prose + bullet lists as needed:

1) Role: agent is Pearl_PromptRouter (or equivalent). It does NOT execute repo work; it only produces paste-ready startup prompts for OTHER agent chats.

2) Mandatory pre-read before every routed prompt: SESSION_UNITY_PROTOCOL, PEARL_ARCHITECT_STATE, ACTIVE_PROJECTS.tsv, ACTIVE_WORKSTREAMS.tsv, SUBSYSTEM_AUTHORITY_MAP.tsv (and DOCS_INDEX if task touches multiple subsystems).

3) On owner plain-English task: do NOT solve the task. Output ONLY one fenced or plain text block: the final paste-ready startup prompt for the next agent. That prompt MUST include: (a) full OWNER TASK verbatim; (b) PROJECT_ID from ACTIVE_PROJECTS or "none"; (c) SUBSYSTEM from map + owner_agent; (d) AUTHORITY_DOCS list to read before writes; (e) conflict check vs ACTIVE_WORKSTREAMS; (f) WRITE_SCOPE / OUT_OF_SCOPE placeholders or instructions to fill after discovery; (g) STOP / HANDOFF rules from SESSION_UNITY; (h) empty STARTUP_RECEIPT template for the executor to fill.

4) If subsystem or project cannot be resolved: output STOP_REASON-style handoff, not a fake executor prompt.

Emit STARTUP_RECEIPT before edits and CLOSEOUT_RECEIPT after. WRITE_SCOPE: docs/SESSION_UNITY_PROTOCOL.md only unless a tiny cross-link in DOCS_INDEX is justified.
```

---

## Prompt 2 — **Dedicated router chat** (use until Prompt 1 is merged)

Paste to open your **Phoenix Omega agent prompt router** chat:

```
You are Pearl_PromptRouter for Phoenix Omega.

RULES (canonical until docs/SESSION_UNITY_PROTOCOL.md contains “Universal router prompt (prompt-building chats)”):
- Before generating ANY routed prompt, read: docs/SESSION_UNITY_PROTOCOL.md; docs/PEARL_ARCHITECT_STATE.md; artifacts/coordination/ACTIVE_PROJECTS.tsv; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv; artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv.
- If the task spans subsystems or paths are unclear, also read docs/DOCS_INDEX.md.
- When the owner sends a plain-English task: DO NOT solve it. DO NOT edit the repo. Reply with ONLY one paste-ready startup prompt for the NEXT agent chat (single block). No preamble, no postscript.
- That startup prompt MUST contain, in order: (1) Executor role + SESSION_UNITY obedience (STARTUP_RECEIPT before work, CLOSEOUT after). (2) OWNER TASK verbatim in a quoted or labeled block. (3) PROJECT_ID from ACTIVE_PROJECTS.tsv or "none". (4) SUBSYSTEM + owner_agent from SUBSYSTEM_AUTHORITY_MAP.tsv; list authority_doc paths the executor must read before writes. (5) Workstream conflict check: scan ACTIVE_WORKSTREAMS.tsv for active|in_progress|blocked|pending rows touching the same paths; instruct narrow scope or STOP to Pearl_PM if conflict. (6) Discovery steps if paths unknown. (7) WRITE_SCOPE / OUT_OF_SCOPE instructions. (8) Copy-paste empty STARTUP_RECEIPT template for the executor.
- If routing fails (no project, no subsystem, missing authority file): output only STOP_REASON, BLOCKED_ON, HANDOFF_TO per SESSION_UNITY_PROTOCOL.

First message in this chat: confirm you have read the five files this session (list filenames). Then wait for owner tasks.
```

---

**Summary:** Verification is done; the **only protocol gap** is the missing **Universal router** section—**Prompt 1** fixes the repo; **Prompt 2** runs the router correctly until then.

---

**User**

CLOSEOUT_RECEIPT

CLOSEOUT_RECEIPT
AGENT:          Pearl_Architect / Pearl_PM (protocol edit)
TASK:           Add "## Universal router prompt (prompt-building chats)" to docs/SESSION_UNITY_PROTOCOL.md
COMMIT_SHA:     3c380e751a
FILES_WRITTEN:  docs/SESSION_UNITY_PROTOCOL.md
FILES_READ:     docs/SESSION_UNITY_PROTOCOL.md;docs/PEARL_ARCHITECT_STATE.md;artifacts/coordination/ACTIVE_PROJECTS.tsv;artifacts/coordination/ACTIVE_WORKSTREAMS.tsv;artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv
STATUS:         completed
HANDOFF_TO:     none
NEXT_ACTION:    None; optional: mention new section in a broader PM/Architect onboarding note if desired.
What changed
Inserted ## Universal router prompt (prompt-building chats) immediately before Quick Reference in docs/SESSION_UNITY_PROTOCOL.md. It defines Pearl_PromptRouter (no repo execution), the mandatory pre-read set (including docs/DOCS_INDEX.md when multiple subsystems apply), the single-block paste-ready output contract with items (a)–(h), and the rule to emit a STOP_REASON-style handoff instead of a fake executor prompt when routing cannot be resolved. Last updated is now 2026-04-14. The Quick Reference table has one new row pointing at that section.

No docs/DOCS_INDEX.md edit (not needed for discoverability beyond the in-file table row).

Commit: 3c380e751a on branch agent/ei-v2-bestseller-corpus (only docs/SESSION_UNITY_PROTOCOL.md was staged; other dirty paths were left untouched).







---

**Cursor**

Verifying the protocol file matches your closeout.



**Receipt acknowledged.** Your CLOSEOUT matches the working tree and git history here.

- **`docs/SESSION_UNITY_PROTOCOL.md`** includes `## Universal router prompt (prompt-building chats)` immediately before **Quick Reference**, with mandatory pre-reads, output contract (a)–(h), unresolvable routing → STOP handoff only, and **Last updated: 2026-04-14**.
- **Quick Reference** has the new row pointing at that section.
- **Commit:** `HEAD` is `3c380e751a6de35286727931ebc8ad4a81f50c12` with message `docs: add Universal router prompt section to session unity protocol`.

Your choice to skip **`docs/DOCS_INDEX.md`** is consistent with the closeout: the section already tells routers to read DOCS_INDEX when multiple subsystems apply, and the in-file table links the new behavior.

**Optional follow-up (not required):** If `ACTIVE_WORKSTREAMS.tsv` ever tracks “protocol / onboarding” edits, add a row or bump `last_updated` when Pearl_PM wants that visibility; otherwise **HANDOFF_TO: none** is fine.

Pearl_PromptRouter chats can now follow that section **from the repo** instead of the inlined workaround.

---

**User**

do Optional follow-up

---

**Cursor**

Adding coordination visibility for the protocol change: reading `ACTIVE_WORKSTREAMS.tsv` format and appending an appropriate row.



Staging coordination-only edits and committing.



Here is what was done for the optional follow-up.

### 1. `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`
Appended completed row **`ws_session_unity_router_20260414`**: Pearl_Architect / Pearl_PM, repo coordination, branch `agent/ei-v2-bestseller-corpus`, `write_scope` `docs/SESSION_UNITY_PROTOCOL.md`, evidence `commit 3c380e751a`, `last_updated` **2026-04-14**.

### 2. `artifacts/coordination/ACTIVE_PROJECTS.tsv`
- Appended **`ws_session_unity_router_20260414`** to the project `active_workstreams` list.  
- Extended **`next_action`** with one sentence pointing at the Session Unity / Pearl_PromptRouter change and **3c380e751a**.  
- Set **`last_updated`** to **2026-04-14**.

### 3. Git
Committed as **`24fd879a5c`** — `coordination: record ws_session_unity_router_20260414; bump ACTIVE_PROJECTS` (only those two files).

`docs/DOCS_INDEX.md` was not changed; the protocol’s Quick Reference already links the new section.

```
CLOSEOUT_RECEIPT
AGENT:          Cursor agent (coordination bookkeeping)
TASK:           Optional follow-up: visibility for Session Unity Universal router protocol edit
COMMIT_SHA:     24fd879a5c
FILES_WRITTEN:  artifacts/coordination/ACTIVE_WORKSTREAMS.tsv;artifacts/coordination/ACTIVE_PROJECTS.tsv
FILES_READ:     artifacts/coordination/ACTIVE_WORKSTREAMS.tsv;artifacts/coordination/ACTIVE_PROJECTS.tsv
STATUS:         completed
HANDOFF_TO:     Pearl_PM
NEXT_ACTION:    Push when ready (run push-guard + preflight per CLAUDE.md); protocol prose remains at 3c380e751a unless merged separately.
```

---

**User**

did we do japanese tts for the japanese teacher videos? 

---

**Cursor**

Here is what the repo actually supports versus what is clearly “done” in production.

### Designed and configured (yes)
- **Japanese locale TTS policy** is defined: `ja-JP` uses **CosyVoice2** first, then Edge, then ElevenLabs in `config/tts/locale_voice_routing.yaml` (with `cosyvoice2_language: "ja"` and Edge default `ja-JP-NanamiNeural`).
- **Catalog / localization** also points JP at CosyVoice2 as primary in `config/localization/locale_registry.yaml`.
- **Per-teacher / role voices for `ja-JP`** exist in `config/tts/narrator_voice_assignments.yaml` and `config/tts/manga_character_voice_bank.yaml` (CosyVoice2 `reference_id` + Edge fallbacks).
- **Japanese copy for the TikTok body-awareness pack** exists in `artifacts/video/tiktok_body_awareness/script_ja.txt` (full Japanese narration script).
- **Docs** state CJK video narration should use CosyVoice2 `reference_id` from `narrator_voice_assignments.yaml` (`docs/VIDEO_NARRATION_CJK_AND_AMBIENT_WIRING.md`).

### Whether “we did” JP TTS on Japanese teacher **videos** (in practice)
- The **multilang** stage only emits **placeholder** narration paths (`narration_{lang}_placeholder.mp3`); it does **not** synthesize audio (`scripts/video/run_multilang_renderer.py`).
- `scripts/video/run_pipeline.py` invokes **`scripts/run_voice_synthesis.py`** for `--voice`, but that file **does not appear in this repo** (so the path from “plan” → “real JP WAV on disk” is not verifiable here).
- Under `artifacts/video/tiktok_body_awareness/junko/` we only see minimal `_work` metadata in the tree we searched, not a clear audit trail of a **JP** render with CosyVoice2-generated narration.

**Bottom line:** **Japanese TTS for teacher/video work is specified in config and docs, and JP scripts exist, but this checkout does not show a complete, repo-local implementation that proves Japanese teacher TikToks were fully voiced with CosyVoice2 (or any engine) end-to-end.** Coordination notes elsewhere in the project still treat **live CJK CosyVoice2 smoke on Pearl Star** as optional follow-up territory.

If you tell me which artifact folder counts as “the Japanese teacher video” (e.g. `junko` vs another teacher id), I can trace that folder’s `soundtrack_plan` / `audio` / `job.json` for a definitive yes/no on that specific output.

---

**User**

dev is stuck. give prompt to fix; Here’s what was done:

Already in the repo (no edits needed)
config/manga/teacher_character_prompts.yaml — sai_maa already has the explicit eye anatomy, catchlights, tack-sharp eyes, and the extended negatives (cross-eyed, wall-eyed, etc.).
scripts/image_generation/generate_teacher_showcase_triptyptych.py — sai_ma portrait brief already includes matched irises/pupils, symmetric lids, catchlights, viewer gaze, tack-sharp eyes.
Re-run on Pearl Star
Loaded COMFYUI_URL from Keychain and ran:
python3 scripts/image_generation/generate_teacher_showcase_triptych.py --teacher sai_ma --type portrait
Result: brand-wizard-app/public/assets/manga_covers/sai_ma_portrait.png — 542,621 bytes, 800×1000 (ComfyUI reported OK).
Verification
MD5 of the new file matches the file right before this run (same seed/workflow → same pixels). So there is no new git diff on sai_ma_portrait.png.
artifacts/video/sai_maa/superseded/sai_ma_portrait_pre_eyes_20260414.png is still there (older, pre–eye-fix era, 528,115 bytes).
A second backup taken right before this run would have been an exact duplicate of the current portrait, so that duplicate was removed to avoid storing the same 542 KB twice.
Still not done (unchanged from before)
sai_maa_final.mp4 is not in the workspace, so ~25s frame extract / video splice was not run. When you have that path, use:
ffmpeg -y -ss 25 -i "<path>/sai_maa_final.mp4" -frames:v 1 /tmp/sai_maa_t25.png
Git
No commit was made: no file content changes vs HEAD for the portrait or the YAML/triptych (they already matched the earlier 5a7dcc83db… work). If you want a “re-run receipt” commit anyway, say so and we can add a tiny marker file or doc—but that’s optional.

---

**Cursor**

```
You are Pearl_Dev + Pearl_Video (executor). Obey docs/SESSION_UNITY_PROTOCOL.md: emit STARTUP_RECEIPT before work; CLOSEOUT_RECEIPT when done; binding WRITE_SCOPE; if sai_maa_final.mp4 cannot be located after reasonable search, STOP with STOP_REASON / HANDOFF_TO owner — do not fake completion.

OWNER TASK (verbatim)
dev is stuck. give prompt to fix; Here’s what was done:

Already in the repo (no edits needed)
config/manga/teacher_character_prompts.yaml — sai_maa already has the explicit eye anatomy, catchlights, tack-sharp eyes, and the extended negatives (cross-eyed, wall-eyed, etc.).
scripts/image_generation/generate_teacher_showcase_triptyptych.py — sai_ma portrait brief already includes matched irises/pupils, symmetric lids, catchlights, viewer gaze, tack-sharp eyes.
Re-run on Pearl Star
Loaded COMFYUI_URL from Keychain and ran:
python3 scripts/image_generation/generate_teacher_showcase_triptych.py --teacher sai_ma --type portrait
Result: brand-wizard-app/public/assets/manga_covers/sai_ma_portrait.png — 542,621 bytes, 800×1000 (ComfyUI reported OK).
Verification
MD5 of the new file matches the file right before this run (same seed/workflow → same pixels). So there is no new git diff on sai_ma_portrait.png.
artifacts/video/sai_maa/superseded/sai_ma_portrait_pre_eyes_20260414.png is still there (older, pre–eye-fix era, 528,115 bytes).
A second backup taken right before this run would have been an exact duplicate of the current portrait, so that duplicate was removed to avoid storing the same 542 KB twice.
Still not done (unchanged from before)
sai_maa_final.mp4 is not in the workspace, so ~25s frame extract / video splice was not run. When you have that path, use:
ffmpeg -y -ss 25 -i "<path>/sai_maa_final.mp4" -frames:v 1 /tmp/sai_maa_t25.png
Git
No commit was made: no file content changes vs HEAD for the portrait or the YAML/triptych (they already matched the earlier 5a7dcc83db… work). If you want a “re-run receipt” commit anyway, say so and we can add a tiny marker file or doc—but that’s optional.

PROJECT_ID
proj_state_convergence_20260328

SUBSYSTEM + owner_agent
- video_pipeline — Pearl_Video (primary: locate or obtain sai_maa_final.mp4, extract ~25s frame, splice/replace still with new portrait, re-encode, verify audio sync).
- manga_pipeline — Pearl_Dev (secondary, only if owner explicitly wants a visually new portrait: change seed / workflow randomization in generate_teacher_showcase_triptych.py or ComfyUI workflow so MD5 changes; otherwise OUT_OF_SCOPE per owner “no edits needed”).

AUTHORITY_DOCS (read before writes)
docs/SESSION_UNITY_PROTOCOL.md; docs/VIDEO_PIPELINE_SPEC.md; docs/VIDEO_PIPELINE_COMPLETE_GUIDE.md; docs/VIDEO_IMAGE_MASTER_PROMPT_SPEC.md (if flux/video bank involved); specs/AI_MANGA_PIPELINE_SUMMARY.md; docs/MANGA_IMPLEMENTATION_OUTLINE.md (only if touching triptych generation); docs/INTEGRATION_CREDENTIALS_REGISTRY.md (Pearl Star / ComfyUI if re-run generation); docs/DOCS_INDEX.md if paths ambiguous.

Conflict check (ACTIVE_WORKSTREAMS.tsv)
- ws_teacher_manga_triptych_20260410 (active): write_scope includes generate_teacher_showcase_triptych.py and brand-wizard-app/public/assets/manga_covers/* — do not modify those unless you are explicitly doing the optional “force new seed” path and coordination allows it.
- ws_video_image_washout_fix_20260411 (active): write_scope includes scripts/video/flux_client.py and config/video/* — no overlap if you restrict to artifacts/video/sai_maa/** and ffmpeg-only edits; if you must edit flux_client or video_bank for this fix, reconcile with that workstream or STOP.
- No shared-path conflict for a pure “find mp4 + artifacts/video splice” lane if declared scope stays under artifacts/video/sai_maa/** (create folder if needed).

WRITE_SCOPE (fill after discovery; default intent)
- In: path to final sai_maa deliverable mp4 (once found or supplied by owner), artifacts/video/sai_maa/** (outputs, superseded, receipts), /tmp for frame extracts.
- Optional: tiny marker doc under artifacts/video/sai_maa/ or docs/ only if owner requests “re-run receipt” commit.

OUT_OF_SCOPE
- config/manga/teacher_character_prompts.yaml and scripts/image_generation/generate_teacher_showcase_triptych.py unless owner explicitly orders a new-pixel portrait (seed/workflow change) after MD5 sameness is accepted as blocker.

Execution order
1) Locate sai_maa_final.mp4: search repo artifacts/video, brand-wizard-app, home/Downloads per owner hint, ask owner in CLOSEOUT if still missing after bounded find.
2) If mp4 found: ffmpeg -y -ss 25 -i "<path>/sai_maa_final.mp4" -frames:v 1 /tmp/sai_maa_t25.png ; compare to brand-wizard-app/public/assets/manga_covers/sai_ma_portrait.png ; replace bad still in video (match resolution/duration of segment; preserve audio); archive superseded mp4 under artifacts/video/sai_maa/superseded/ with dated name.
3) If portrait must change pixels: implement minimal seed/noise/workflow change, re-run ComfyUI on Pearl Star, then repeat step 2.
4) Optional commit: only with owner OK; otherwise CLOSEOUT with paths + ffmpeg proof, no empty commit.

STOP / HANDOFF
If mp4 never found or workstream conflict on flux/video scripts: emit STOP_REASON, BLOCKED_ON, HANDOFF_TO owner.

STARTUP_RECEIPT (fill before edits)
STARTUP_RECEIPT
AGENT:
TASK:
PROJECT_ID:
SUBSYSTEM:
AUTHORITY_DOCS:
READ_PATH_COMPLETE:
WRITE_SCOPE:
OUT_OF_SCOPE:
BLOCKERS:
READY_STATUS:
```

---

**User**

prompt to do the chinese and japanese tts for the teacher vids. ch for master wu and master feung. japanese femaile for miki, junko. japanese male for omote.  joshin already has japanese

---

**Cursor**

```
You are Pearl_Dev + Pearl_Video (primary), with Pearl_Localization for locale copy QA if you touch scripts. Obey docs/SESSION_UNITY_PROTOCOL.md: STARTUP_RECEIPT before work; CLOSEOUT_RECEIPT after; binding WRITE_SCOPE.

OWNER TASK (verbatim)
prompt to do the chinese and japanese tts for the teacher vids. ch for master wu and master feung. japanese femaile for miki, junko. japanese male for omote. joshin already has japanese

PROJECT_ID
proj_state_convergence_20260328

SUBSYSTEM + owner_agent
- video_pipeline — Pearl_Video (teacher vertical video narration audio, mux or sidecar for TikTok-length cuts).
- manga_pipeline — Pearl_Dev (voice reference source of truth in config/tts/manga_character_voice_bank.yaml).
- translation — Pearl_Localization (optional: confirm zh-CN script register and ja-JP keigo where applicable).
- integrations — Pearl_Int (CosyVoice2 on Pearl Star: COSYVOICE_URL / docs/INTEGRATION_CREDENTIALS_REGISTRY.md).

AUTHORITY_DOCS (read before writes)
docs/SESSION_UNITY_PROTOCOL.md; docs/VIDEO_PIPELINE_SPEC.md; docs/VIDEO_PIPELINE_COMPLETE_GUIDE.md; docs/VIDEO_NARRATION_CJK_AND_AMBIENT_WIRING.md; docs/INTEGRATION_CREDENTIALS_REGISTRY.md; config/tts/locale_voice_routing.yaml; config/tts/engines.yaml; config/tts/manga_character_voice_bank.yaml; config/localization/locale_registry.yaml; specs/AI_MANGA_PIPELINE_SUMMARY.md; docs/MANGA_IMPLEMENTATION_OUTLINE.md; docs/DOCS_INDEX.md (cross-subsystem navigation).

Conflict check (ACTIVE_WORKSTREAMS.tsv)
- ws_teacher_manga_triptych_20260410 (active): touches image triptych + teacher_showcase.html + manga_covers — avoid unrelated HTML/image edits; OK to add audio under artifacts/video/** if write_scope does not collide.
- ws_video_image_washout_fix_20260411 (active): scripts/video/flux_client.py + config/video/* — do not edit those unless this task requires flux changes; prefer new or audio-specific scripts under scripts/audio/ or scripts/video/ only if namespaced and non-overlapping.
- ws_pearl_news_daily_publish_20260411 (active): disjoint unless you touch pearl_news/*.
- No blocker on running CosyVoice2 synthesis if COSYVOICE_URL is set; if missing, use Edge-TTS per locale_voice_routing fallbacks and document in CLOSEOUT.

Teacher / locale matrix (owner intent)
- zh-CN narration: master_wu, master_feung (Mandarin; use zh-CN slots in manga_character_voice_bank.yaml — cn_m_warm_01 / cn_m_deep_01 for teacher_character as already defined).
- ja-JP female narration: miki, junko (use bank ja-JP teacher_character: ja_f_gentle_01, ja_f_bright_01 respectively).
- ja-JP male narration: omote — owner requires male; current bank omote ja-JP narrator/teacher_character use ja_f_soft_01 (female). UPDATE omote’s ja-JP narrator + teacher_character + inner_monologue to male CosyVoice reference_ids (e.g. ja_m_warm_01 or ja_m_calm_01) consistent with empathic_mirror archetype; keep student slots coherent; verify uniqueness rules in narrator_voice_assignments.yaml header if any author rows alias omote.
- EXCLUDE joshin (owner: Japanese already done).

Implementation expectations
1) Source scripts per teacher video pack: mirror artifacts/video/tiktok_body_awareness pattern (script.txt, script_zh.txt, script_ja.txt) — create or complete zh/ja scripts for each target teacher folder under artifacts/video/ (discover exact pack dirs; if missing, add scripts only after STARTUP_RECEIPT declares paths).
2) Synthesis: CosyVoice2 primary for CJK per locale_voice_routing; Edge-TTS fallback voices zh-CN-XiaoxiaoNeural / Yunxi / Yunjian and ja-JP-NanamiNeural / KeitaNeural as in config; cross-lingual CosyVoice API per engines.yaml / existing HTTP patterns (see scripts/audio/generate_teacher_showcase_audio.py — extend or add sibling script with --locale zh-CN|ja-JP, --teacher, --text-file; do not assume english_female only).
3) Outputs: write WAV or MP3 per teacher per locale (e.g. artifacts/video/<pack>/audio/narration_zh-CN.wav, narration_ja-JP.wav); document muxing into final_tiktok.mp4 in CLOSEOUT if run_pipeline --voice path is still missing run_voice_synthesis.py, either add minimal scripts/run_voice_synthesis.py shim calling your generator or wire run_pipeline.py to the new module — smallest change that works.
4) Verification: listen spot-check; file size >1KB; optional ffprobe duration vs script segment table.

WRITE_SCOPE (fill after tree discovery)
- In: artifacts/video/** for target teachers’ packs (audio/, script_zh.txt, script_ja.txt); scripts/audio/* or scripts/video/* for synthesis glue; config/tts/manga_character_voice_bank.yaml for omote ja-JP male fix only.
- OUT_OF_SCOPE: joshin packs; unrelated teachers; wholesale edits to config/tts/narrator_voice_assignments.yaml (100k+ lines) unless a scripted targeted patch is required for omote uniqueness — prefer bank-only change first.

STOP / HANDOFF
If CosyVoice unreachable and Edge also fails, or teacher pack paths cannot be found: STOP_REASON + HANDOFF_TO owner with exact missing inputs.

STARTUP_RECEIPT
STARTUP_RECEIPT
AGENT:
TASK:
PROJECT_ID:
SUBSYSTEM:
AUTHORITY_DOCS:
READ_PATH_COMPLETE:
WRITE_SCOPE:
OUT_OF_SCOPE:
BLOCKERS:
READY_STATUS:
```

---

**User**

dev stuck, prompt to fix: STARTUP_RECEIPT
AGENT:              Pearl_Dev + Pearl_Video (executor)
TASK:               Locate sai_maa_final.mp4; extract ~25s; splice still with sai_ma_portrait; verify; else STOP and hand off.
PROJECT_ID:         proj_state_convergence_20260328
SUBSYSTEM:          video_pipeline (primary); manga_pipeline out of scope unless new portrait ordered
AUTHORITY_DOCS:     docs/SESSION_UNITY_PROTOCOL.md; docs/DOCS_INDEX.md (head); docs/VIDEO_PIPELINE_SPEC.md (§1–2); docs/VIDEO_PIPELINE_COMPLETE_GUIDE.md (Before you start + stages); docs/VIDEO_IMAGE_MASTER_PROMPT_SPEC.md (head); docs/INTEGRATION_CREDENTIALS_REGISTRY.md (Pearl Star §0); specs/AI_MANGA_PIPELINE_SUMMARY.md (head); docs/MANGA_IMPLEMENTATION_OUTLINE.md (head); artifacts/coordination/ACTIVE_PROJECTS.tsv; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv (conflict scan)
READ_PATH_COMPLETE: yes
WRITE_SCOPE:        Intended: path to sai_maa_final.mp4 once found; artifacts/video/sai_maa/**; /tmp for frame extracts. Actual: no repo writes (deliverable MP4 absent).
OUT_OF_SCOPE:       config/manga/teacher_character_prompts.yaml; scripts/image_generation/generate_teacher_showcase_triptych.py; brand-wizard-app/public/assets/manga_covers/* (unless owner orders new-pixel portrait); scripts/video/flux_client.py; config/video/* (ws_video_image_washout_fix)
BLOCKERS:           sai_maa_final.mp4 not found after bounded search (see STOP below)
READY_STATUS:       blocked
Search performed (reasonable, bounded)
Location	Result
artifacts/**, brand-wizard-app/**, staging/** (shallow find)
no sai_maa_final.mp4
scripts/** references to sai_maa_final
none
mdfind -name sai_maa_final.mp4
empty
/Users/ahjan/Downloads, Desktop, Movies explicit paths
not present
ssh pearl_star find ~ -maxdepth 5 -name sai_maa_final.mp4
empty
artifacts/video/sai_maa/
only superseded/sai_ma_portrait_pre_eyes_20260414.png
Per your instruction: do not fake completion — no ffmpeg splice, no archived MP4, no “done” on video.

STOP_REASON:   Deliverable file sai_maa_final.mp4 is not on disk anywhere the executor could reach (repo artifacts, brand-wizard-app, staging, macOS Spotlight, common home folders, Pearl Star home shallow find). Without it, ~25s extract and still-replace cannot be executed truthfully.
BLOCKED_ON:    Owner (or dev) must supply sai_maa_final.mp4 at a known absolute path, or commit it under e.g. artifacts/video/sai_maa/incoming/sai_maa_final.mp4, plus any segment map if the bad still is not exactly one 9:16 plate at ~25s.
HANDOFF_TO:    owner
Active workstream note (no conflict triggered): ws_teacher_manga_triptych_20260410 and ws_video_image_washout_fix_20260411 were not touched; this lane stayed read-only on manga/flux config.

CLOSEOUT_RECEIPT
AGENT:          Pearl_Dev + Pearl_Video (executor)
TASK:           Locate sai_maa_final.mp4; ~25s frame; splice portrait; verify; else STOP.
COMMIT_SHA:     no commits
FILES_WRITTEN:  none
FILES_READ:     docs/SESSION_UNITY_PROTOCOL.md; docs/DOCS_INDEX.md; docs/VIDEO_PIPELINE_SPEC.md; docs/VIDEO_PIPELINE_COMPLETE_GUIDE.md; docs/VIDEO_IMAGE_MASTER_PROMPT_SPEC.md; docs/INTEGRATION_CREDENTIALS_REGISTRY.md; specs/AI_MANGA_PIPELINE_SUMMARY.md; docs/MANGA_IMPLEMENTATION_OUTLINE.md; artifacts/coordination/ACTIVE_PROJECTS.tsv; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
STATUS:         blocked
HANDOFF_TO:     owner
NEXT_ACTION:    Place sai_maa_final.mp4 where the repo can read it, then re-run an executor with: (1) ffprobe duration; (2) ffmpeg -y -ss 25 -i "<path>" -frames:v 1 /tmp/sai_maa_t25.png; (3) identify which segment is still vs motion (ffprobe stream or manual); (4) splice replacement using brand-wizard-app/public/assets/manga_covers/sai_ma_portrait.png scaled to match; (5) archive prior MP4 under artifacts/video/sai_maa/superseded/ with dated name. If a new-pixel portrait is required first, explicitly order seed/workflow change (coordinates with ws_teacher_manga_triptych).
Copy-paste prompt for dev (unblock next run)
Use this as the owner task for the next agent session after the file exists:

Pearl_Video executor. sai_maa_final.mp4 is now at: <ABSOLUTE_PATH>.

ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "<path>"
ffmpeg -y -ss 25 -i "<path>" -frames:v 1 /tmp/sai_maa_t25.png — confirm this frame is the bad still.
If the video is a single full-frame still ~25s: replace that segment’s image source with brand-wizard-app/public/assets/manga_covers/sai_ma_portrait.png (match resolution and duration of that segment; preserve audio with -c:a copy where safe). If it is Ken Burns / zoom on one PNG, regenerate that motion from the new PNG with the same filter chain, then concat.
Write final deliverable to artifacts/video/sai_maa/sai_maa_final.mp4 (or owner-specified path); move previous file to artifacts/video/sai_maa/superseded/sai_maa_final_<DATE>.mp4.
Re-extract ~25s frame and visually confirm eyes.
WRITE_SCOPE: artifacts/video/sai_maa/** + temp; do not edit flux_client.py / config/video/* without reconciling ws_video_image_washout_fix_20260411.
OUT OF SCOPE: triptych YAML / generate_teacher_showcase_triptych.py unless owner asks for new MD5 on portrait.
That is the full honest outcome: blocked on missing MP4; portrait side remains as already landed in repo history; video splice is not claimed.

---

**Cursor**

```
OWNER PREREQUISITE (do this before opening the executor chat)
Place the real deliverable on disk where the repo can read it, e.g. commit or copy to:
artifacts/video/sai_maa/incoming/sai_maa_final.mp4
(or paste the absolute path into the OWNER TASK line below). Without this file, the executor must STOP immediately — same as prior session.

OWNER TASK (verbatim — replace placeholder only)
dev stuck, prompt to fix: Pearl_Video executor. sai_maa_final.mp4 is now at: <ABSOLUTE_PATH_OR_artifacts/video/sai_maa/incoming/sai_maa_final.mp4>.

ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "<path>"
ffmpeg -y -ss 25 -i "<path>" -frames:v 1 /tmp/sai_maa_t25.png — confirm this frame is the bad still.
If the video is a single full-frame still ~25s: replace that segment’s image source with brand-wizard-app/public/assets/manga_covers/sai_ma_portrait.png (match resolution and duration of that segment; preserve audio with -c:a copy where safe). If it is Ken Burns / zoom on one PNG, regenerate that motion from the new PNG with the same filter chain, then concat.
Write final deliverable to artifacts/video/sai_maa/sai_maa_final.mp4 (or owner-specified canonical path); move previous file to artifacts/video/sai_maa/superseded/sai_maa_final_<DATE>.mp4.
Re-extract ~25s frame and visually confirm eyes.
Prior session outcome: sai_maa_final.mp4 was not found after bounded search (repo, brand-wizard-app, staging, mdfind, Downloads/Desktop/Movies, pearl_star shallow find); only artifacts/video/sai_maa/superseded/sai_ma_portrait_pre_eyes_20260414.png existed there. Portrait YAML/triptych already correct in repo; no new-pixel portrait unless owner orders seed/workflow change.

PROJECT_ID
proj_state_convergence_20260328

SUBSYSTEM + owner_agent
video_pipeline — Pearl_Video (primary). manga_pipeline — Pearl_Dev only if owner explicitly orders new MD5 portrait (coordinates with ws_teacher_manga_triptych_20260410).

AUTHORITY_DOCS
docs/SESSION_UNITY_PROTOCOL.md; docs/VIDEO_PIPELINE_SPEC.md; docs/VIDEO_PIPELINE_COMPLETE_GUIDE.md; docs/VIDEO_IMAGE_MASTER_PROMPT_SPEC.md; docs/INTEGRATION_CREDENTIALS_REGISTRY.md (Pearl Star if re-render ever needed); artifacts/coordination/ACTIVE_WORKSTREAMS.tsv (re-scan before edits).

Conflict check
ws_video_image_washout_fix_20260411 (active): do not edit scripts/video/flux_client.py or config/video/* without reconciling that workstream. ws_teacher_manga_triptych_20260410 (active): do not touch triptych script / manga_covers except using existing sai_ma_portrait.png as the still source unless owner orders regeneration.

WRITE_SCOPE
artifacts/video/sai_maa/** (incoming, final, superseded); /tmp for frame extracts; optional small receipt markdown under artifacts/video/sai_maa/ if owner wants audit trail.

OUT_OF_SCOPE
config/manga/teacher_character_prompts.yaml; scripts/image_generation/generate_teacher_showcase_triptych.py; brand-wizard-app/public/assets/manga_covers/* (except read sai_ma_portrait.png); flux/video_bank edits unless conflict cleared.

STOP / HANDOFF
If `<path>` does not exist or ffprobe fails: emit STOP_REASON / BLOCKED_ON / HANDOFF_TO owner — no fake splice. If ~25s is not the still boundary, ffprobe streams/chapters and adjust -ss; document in CLOSEOUT.

STARTUP_RECEIPT (fill before ffmpeg)
STARTUP_RECEIPT
AGENT:
TASK:
PROJECT_ID:
SUBSYSTEM:
AUTHORITY_DOCS:
READ_PATH_COMPLETE:
WRITE_SCOPE:
OUT_OF_SCOPE:
BLOCKERS:
READY_STATUS:
```

---

**User**

desc and prompts for what to do next: Saved to `docs/SESSION_HANDOFF_2026_04_13.md`.

Here's the one-page version of what it covers:

---

**4 open PRs waiting on you:**
- #417 — merge now (approved)
- #418 — merge now (spine bridges, all green)
- #419 — merge when CI green (bestseller corpus)
- #416 — decide on word-band widening, then merge

**2 prompts ready to paste:**
- **Prompt A** — PR triage on 10 backlog PRs (#326–#407)
- **Prompt D** — System fix: chapter contracts + frame governance + recurrence control + exercise limits ← **highest priority**

**1 thing only you can do:**
- Read the 7 Master Sha books in Finder → that's your Phase 2 human feedback input

**The bottom line from the QA:**
The atoms are good enough. The assembly isn't. Prompt D fixes the four root causes. Run it next.

---

**Cursor**

Here is a concise **“what to do next”** order (from `docs/SESSION_HANDOFF_2026_04_13.md` + your one-pager), then **full paste-ready prompts** for **A** and **D**. The handoff file only **summarizes** A and D; the blocks below are **reconstructed** so they are executable without hunting the old chat.

---

### What to do next (priority)

1. **Merge** [PR #417](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/417) (docs / `book.txt` — already approved).  
2. **Merge** [PR #418](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/418) (spine bridges — CI green aside from known Cloudflare).  
3. **Wait for CI, then merge** [PR #419](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/419) (EI v2 bestseller corpus; anchor blend stays off).  
4. **Decide, then merge or adjust** [PR #416](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/416): word-band widening is a **goalpost move**; either merge with explicit `TEMPORARY` comments in `format_registry.yaml`, revert bands, or follow up in prose-quality work.  
5. **Human-only:** open the **7 Master Sha** duration outputs in Finder under `artifacts/pearl_prime/duration_sweep_master_sha_genz_anxiety/` and note what reads wrong — that feeds Phase 2 (Prompt E, not built yet).  
6. **Run Prompt D next** (highest leverage for “atoms OK, assembly not”).  
7. **Run Prompt A** after merges settle (backlog PR hygiene).

---

### Prompt A — PR triage (backlog + merge #417)

Paste into a **new agent chat** (Pearl_GitHub + Pearl_PM):

```
You are Pearl_GitHub + Pearl_PM. Obey docs/SESSION_UNITY_PROTOCOL.md (STARTUP_RECEIPT / CLOSEOUT_RECEIPT), CLAUDE.md (preflight, push-guard, mass-delete rule), docs/GITHUB_GOVERNANCE.md, docs/GITHUB_OPERATIONS_FRAMEWORK.md.

TASK — PR triage 2026-04-13 (Prompt A)
1) Merge PR #417 first if it is still open and owner-approved (docs: book.txt rewrite). Before merge: gh pr diff 417 --stat | tail -1; if deletions > 50, STOP and ask owner.
2) Triage every OTHER open PR in the backlog set: #326, #328, #336, #344, #347, #363, #369, #377, #393, #405, #407 (and any additional open PRs up through #407 not listed if still open). For EACH:
   - gh pr view <n> --json title,state,mergeable,headRefName,baseRefName
   - gh pr diff <n> --stat | tail -1  (mass-delete gate)
   - Note CI / required checks (Workers pearl-prime may fail per docs — document, do not assume mergeable)
   - Merge-base vs origin/main: identify superseded / stale / conflict-heavy branches
   - Verdict per PR: MERGE_NOW / MERGE_AFTER_FIX / CLOSE_SUPERSEDED / NEED_OWNER / DEFER with one-line reason
3) Write artifacts/coordination/PR_TRIAGE_2026_04_13.md with a table + recommended next action per PR. Do not merge anything beyond #417 without explicit verdict line unless governance allows MERGE_NOW.
4) If you close PRs, use gh with clear comment citing superseding PR or mainline commit.

PROJECT_ID: proj_state_convergence_20260328
WRITE_SCOPE: artifacts/coordination/PR_TRIAGE_2026_04_13.md; gh pr comments; merges only when verdict is MERGE_NOW and gates pass.
OUT_OF_SCOPE: unrelated code refactors.

STARTUP_RECEIPT: fill all fields before gh merge or branch writes.
CLOSEOUT_RECEIPT: include commit SHAs for any merges performed.
```

---

### Prompt D — System fix (chapter contracts + frame governance + recurrence + exercises)

Paste into a **new agent chat** (Pearl_Dev + Pearl_Architect + Pearl_Prime; branch per handoff):

```
You are Pearl_Dev + Pearl_Architect + Pearl_Prime (core_pipeline assembly). Obey docs/SESSION_UNITY_PROTOCOL.md; read docs/PEARL_ARCHITECT_STATE.md; specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md; specs/PHOENIX_V4_5_WRITER_SPEC.md; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv (declare non-interference with ws_exercise_journey_system_*, ws_v2_somatic_loader_stacking_*, ws_bestseller_spines_* unless explicitly coordinated).

TASK — Prompt D (highest priority): fix four root assembly failures identified in Master Sha / gen-z book QA (docs/SESSION_HANDOFF_2026_04_13.md §2f, §7). Atoms are adequate; assembly is not.

Branch: agent/chapter-contracts-frame-governance (from origin/main after fetch).

FOUR DELIVERABLES
1) Chapter purpose contracts (YAML or structured config, versioned)
   - Per chapter index: emotional_job, reader_promise, forbidden_repeats (patterns or n-gram keys), max_exercises (default 2 standard+, 1 micro).
   - Wire into pipeline so composer / gates can read contracts (topic × format × chapter_index); document schema in a short dev spec under docs/ or extend an existing spec if one already owns chapter contracts — do not duplicate canonical specs.

2) Frame governance
   - Book-level flag: somatic_first vs spiritual_first (config on arc, book plan, or spine metadata — pick the governed source already used for teacher/frame).
   - Phrase-list or lightweight classifier: in somatic_first, block or soften metaphysical absolutes / “Bright”-style proclamation clusters unless in an allowed “doctrine slot” chapter list.
   - Implement in composition or post-compose gate (reuse delivery_contract_gate patterns from spine bridges work if present).

3) Cross-manuscript recurrence control
   - Signature phrases / motif lines: cap total occurrences per book (default max 3 global for configurable list; read list from config, not hardcoded prose).
   - Enforce in a pass after compose or inside composer with a rolling window; fail chapter_flow or new gate with actionable report.

4) Exercise governance
   - Default max 2 EXERCISE-type slots per chapter (1 for micro_book_* formats). Reject or merge excess in planner before final compose; log in report artifact.

REGRESSION
- Re-run spine pipeline for Master Sha / gen_z_professionals / anxiety / standard_book (same entrypoint the team used for duration sweep). Verify 8 acceptance criteria defined in session handoff: distinct chapter purpose, no illegal repeats, frame stable, exercise count, no bulk exercise dump, bridges coherent with PR #418 behavior, delivery_contract_gate clean, readable book.txt export path documented in CLOSEOUT.

TESTS
- Add focused pytest for: contract load, recurrence cap, exercise cap, frame gate (minimal fixtures, no 13k-book run in CI).

WRITE_SCOPE: phoenix_v4/planning/* phoenix_v4/rendering/* phoenix_v4/qa/* config/* as needed for flags; tests/; optional docs/*.md only if required by repo convention for new gates.
OUT_OF_SCOPE: editing Master Sha manuscript by hand; EI anchor blend enable; Pearl News.

CLOSEOUT: artifact path to regression book output + summary table of 8 criteria; commit SHA; suggest registering ws_system_fix_chapter_contracts_20260413 in ACTIVE_WORKSTREAMS.tsv when complete.

STARTUP_RECEIPT before edits; CLOSEOUT_RECEIPT after.
```

---

### Finder / Phase 2 (you only)

Open **`artifacts/pearl_prime/duration_sweep_master_sha_genz_anxiety/`**, read the **seven** book outputs (micro → deep), and jot **per-format notes**: where flow breaks, repetition, frame swing, or exercises feel unearned. That file of notes becomes the input for **Prompt E** (human feedback UI) when you are ready to build it.

If you want, the next message can be **only** Prompt D split into two agent chats (Architect spec pass → Dev implementation) to reduce merge risk.

---

**User**

desc: STARTUP_RECEIPT
AGENT:              Pearl_Dev + Pearl_Video (+ Pearl_Localization script QA)
TASK:               CJK TTS for teacher TikTok body-awareness packs (zh master_wu/master_feung; ja miki/junko/omote); omote ja-JP male bank fix; pipeline voice shim
PROJECT_ID:         proj_state_convergence_20260328
SUBSYSTEM:          video_pipeline; manga_pipeline; translation (locale copy only); integrations (CosyVoice2 optional)
AUTHORITY_DOCS:     docs/SESSION_UNITY_PROTOCOL.md; docs/VIDEO_PIPELINE_SPEC.md; docs/VIDEO_PIPELINE_COMPLETE_GUIDE.md; docs/VIDEO_NARRATION_CJK_AND_AMBIENT_WIRING.md; docs/INTEGRATION_CREDENTIALS_REGISTRY.md; config/tts/locale_voice_routing.yaml; config/tts/engines.yaml; config/tts/manga_character_voice_bank.yaml; config/localization/locale_registry.yaml; specs/AI_MANGA_PIPELINE_SUMMARY.md; docs/MANGA_IMPLEMENTATION_OUTLINE.md; docs/DOCS_INDEX.md; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv; artifacts/coordination/ACTIVE_PROJECTS.tsv; artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv
READ_PATH_COMPLETE: yes (coordination TSVs + index; video/manga/integration docs as listed; locale registry sampled for zh-CN script policy)
WRITE_SCOPE:        artifacts/video/tiktok_body_awareness/{master_wu,master_feung,miki,omote}/**; artifacts/video/tiktok_body_awareness/junko/{script.txt,script_zh.txt,script_ja.txt,audio/**}; scripts/audio/generate_teacher_pack_narration_audio.py; scripts/video/run_voice_synthesis.py; config/tts/manga_character_voice_bank.yaml (omote ja-JP block only)
OUT_OF_SCOPE:       joshin narration; scripts/video/flux_client.py; config/video/* wholesale; brand-wizard-app/teacher_showcase.html; narrator_voice_assignments.yaml; pearl_news/*; unrelated dirty paths in git status
BLOCKERS:           COSYVOICE_URL unset in this shell — synthesis used Edge-TTS per bank edge_fallback (with narrator fallback when teacher_character omits edge_fallback)
READY_STATUS:       ready
What changed
config/tts/manga_character_voice_bank.yaml — omote / ja-JP
Narrator and teacher/inner monologue now use male CosyVoice refs (ja_m_calm_01 / ja_m_warm_01) with Edge ja-JP-KeitaNeural on the narrator slot so Edge inherits for clips that only read teacher_character.

scripts/audio/generate_teacher_pack_narration_audio.py
Loads teacher_character (+ narrator.edge_fallback when needed), tries CosyVoice cross-lingual if a local reference WAV exists, then CosyVoice built-ins where safe, then Edge-TTS → WAV via ffmpeg.
Flags: --pack-dir, --teacher (repeat), --locale zh-CN|ja-JP, --text-file, --force, --dry-run.

scripts/video/run_voice_synthesis.py
Minimal stage for run_pipeline.py --voice: fills narration_segments[].audio_path, writes soundtrack_plan_with_audio.json (ElevenLabs if ELEVENLABS_API_KEY else Edge English neural).

Pack layout under artifacts/video/tiktok_body_awareness/
New dirs master_wu, master_feung, miki, omote with script.txt / script_zh.txt / script_ja.txt (same timed body script as the pack root). junko got the same three scripts plus audio/narration_ja-JP.wav.

Generated audio (Edge; all files ≫ 1 KB)

master_wu/audio/narration_zh-CN.wav — zh-CN-YunxiNeural (~40 s)
master_feung/audio/narration_zh-CN.wav — zh-CN-YunjianNeural (~42 s)
miki, junko — audio/narration_ja-JP.wav — ja-JP-NanamiNeural (~49 s)
omote — audio/narration_ja-JP.wav — ja-JP-KeitaNeural (~45 s)
Localization (Pearl_Localization): script_zh.txt matches Simplified zh-CN per config/localization/locale_registry.yaml. Japanese lines match the existing pack timing; register is conversational with です／ます-friendly tone, not heavy keigo rewrite (same string set as the shared script_ja.txt).

Muxing: scripts/video/run_render.py only mixes narration when the active soundtrack JSON has narration_segments with audio_path (see 814:845:scripts/video/run_render.py). These TikTok packs are built from per-clip concat, not that JSON path. To mux a full vertical cut, use something like:
ffmpeg -y -i <teacher>/final_tiktok.mp4 -i <teacher>/audio/narration_ja-JP.wav -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -shortest <teacher>/final_tiktok_with_narration.mp4
(adjust if there is no final_tiktok.mp4 yet for new teachers).

Workstreams: No edits under ws_teacher_manga_triptych_20260410 or ws_video_image_washout_fix_20260411 scopes.

CLOSEOUT_RECEIPT


CLOSEOUT_RECEIPT
AGENT:          Pearl_Dev + Pearl_Video
TASK:           CJK teacher-pack TTS + omote ja male bank + run_voice_synthesis shim
COMMIT_SHA:     no commits (deliverables are local untracked/modified paths only; repo HEAD was 24fd879a5c1bc79e43fe6e31256b822cb164b62e)
FILES_WRITTEN:  scripts/audio/generate_teacher_pack_narration_audio.py; scripts/video/run_voice_synthesis.py; config/tts/manga_character_voice_bank.yaml (omote ja-JP); artifacts/video/tiktok_body_awareness/master_wu/{script.txt,script_zh.txt,script_ja.txt,audio/narration_zh-CN.wav}; artifacts/video/tiktok_body_awareness/master_feung/{script.txt,script_zh.txt,script_ja.txt,audio/narration_zh-CN.wav}; artifacts/video/tiktok_body_awareness/miki/{script.txt,script_zh.txt,script_ja.txt,audio/narration_ja-JP.wav}; artifacts/video/tiktok_body_awareness/omote/{script.txt,script_zh.txt,script_ja.txt,audio/narration_ja-JP.wav}; artifacts/video/tiktok_body_awareness/junko/{script.txt,script_zh.txt,script_ja.txt,audio/narration_ja-JP.wav}
FILES_READ:     docs/SESSION_UNITY_PROTOCOL.md; docs/VIDEO_PIPELINE_SPEC.md; docs/VIDEO_PIPELINE_COMPLETE_GUIDE.md; docs/VIDEO_NARRATION_CJK_AND_AMBIENT_WIRING.md; docs/INTEGRATION_CREDENTIALS_REGISTRY.md; docs/DOCS_INDEX.md; config/tts/locale_voice_routing.yaml; config/tts/engines.yaml; config/tts/manga_character_voice_bank.yaml; config/localization/locale_registry.yaml; specs/AI_MANGA_PIPELINE_SUMMARY.md; docs/MANGA_IMPLEMENTATION_OUTLINE.md; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv; artifacts/coordination/ACTIVE_PROJECTS.tsv; artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv; scripts/audiobook/generate_showcase_bundle.py (CosyVoice helpers); scripts/video/run_pipeline.py; scripts/video/run_render.py; scripts/video/run_soundtrack_engine.py
STATUS:         completed (CosyVoice2 not used here — COSYVOICE_URL unset; Edge-TTS used; CosyVoice path ready when URL + reference clips exist)
HANDOFF_TO:     none
NEXT_ACTION:    Set COSYVOICE_URL

---

**Cursor**

## Description — CJK teacher-pack TTS (body awareness)

**Pearl_Dev + Pearl_Video** (with **Pearl_Localization**-level script QA) delivered **localized narration audio** for the TikTok **body awareness** teacher packs: **zh-CN** for **master_wu** and **master_feung**, **ja-JP** for **miki**, **junko**, and **omote** ( **joshin** intentionally unchanged). **Omote’s `ja-JP` slots in `manga_character_voice_bank.yaml` were corrected to male** CosyVoice references with a coherent **Edge** fallback chain. Because **`COSYVOICE_URL` was unset** in that environment, **all generated WAVs used Edge-TTS** (not CosyVoice2); the new **`generate_teacher_pack_narration_audio.py`** still encodes the **intended** CosyVoice-first path when URL + reference clips exist. A minimal **`run_voice_synthesis.py`** shim was added so **`run_pipeline.py --voice`** has a real entrypoint again (ElevenLabs if key present, else Edge English neural — separate from the per-pack CJK script). **Muxing CJK WAV into the vertical `final_tiktok.mp4`** is **not automatic** today: `run_render.py` only picks up narration when the soundtrack JSON exposes `narration_segments[].audio_path`, which these concat-style TikTok builds do not populate—so the handoff’s **ffmpeg one-liner** is the right bridge until the pipeline learns this layout.

**Status:** work is **done at artifact + script level**; **no git commit** was made (paths may be untracked/modified locally per receipt).

---

### What changed (inventory)

| Area | Change |
|------|--------|
| **Bank** | `config/tts/manga_character_voice_bank.yaml` — **omote / ja-JP** male alignment + Edge `ja-JP-KeitaNeural` on narrator. |
| **New script** | `scripts/audio/generate_teacher_pack_narration_audio.py` — pack-dir, per-teacher, locale, text file, CosyVoice→Edge chain, `--dry-run` / `--force`. |
| **Shim** | `scripts/video/run_voice_synthesis.py` — satisfies `run_pipeline.py --voice` (plan JSON narration paths). |
| **Packs** | Under `artifacts/video/tiktok_body_awareness/`: **master_wu**, **master_feung**, **miki**, **omote** (full script trio + zh or ja WAV); **junko** gained aligned **script_*.txt** + **ja** WAV. |

---

### Generated audio (this run)

- **master_wu** / **master_feung:** `audio/narration_zh-CN.wav` (Edge: Yunxi / Yunjian, ~40–42 s).  
- **miki**, **junko:** `audio/narration_ja-JP.wav` (Edge: Nanami, ~49 s).  
- **omote:** `audio/narration_ja-JP.wav` (Edge: **Keita**, ~45 s).

---

### Next actions (in order)

1. **`eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"`** (or export manually) so **`COSYVOICE_URL`** is set; re-run `generate_teacher_pack_narration_audio.py` with **`--force`** to replace Edge WAVs with CosyVoice where reference clips allow.  
2. **Mux:** for each teacher with `final_tiktok.mp4`, run the documented **ffmpeg** `-map 0:v -map 1:a -shortest` pattern to produce **`final_tiktok_with_narration.mp4`** (or wire a tiny script under `scripts/video/` if you want repeatability).  
3. **Git:** stage the listed **tracked** paths (`scripts/**`, `config/tts/manga_character_voice_bank.yaml`); add **`artifacts/video/...`** only if you intend to version binary WAVs (often **gitignore** or LFS—decide repo policy before commit).  
4. **Coordination (optional):** add a completed row for this lane in **`ACTIVE_WORKSTREAMS.tsv`** if Pearl_PM wants traceability; **`NEXT_ACTION` from the receipt is still valid:** enable **CosyVoice** for parity with `locale_voice_routing.yaml`.

---

**User**

give prompt for : 1,2,3,4

---

**Cursor**

```
You are Pearl_Dev + Pearl_Video (+ Pearl_GitHub for step 3 commits only). Obey docs/SESSION_UNITY_PROTOCOL.md: STARTUP_RECEIPT before work; CLOSEOUT_RECEIPT after.

OWNER TASK (numbered)
1) Enable CosyVoice2 and re-synthesize: load integration env from Keychain (`eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"` per CLAUDE.md / docs/INTEGRATION_CREDENTIALS_REGISTRY.md). Confirm `COSYVOICE_URL` responds. Re-run `scripts/audio/generate_teacher_pack_narration_audio.py` with `--force` for packs `artifacts/video/tiktok_body_awareness/{master_wu,master_feung,miki,junko,omote}` and locales `zh-CN` (master_wu, master_feung) and `ja-JP` (miki, junko, omote) using each pack’s `script_zh.txt` or `script_ja.txt` as `--text-file`. Keep joshin out of scope. If CosyVoice fails for a teacher, fall back to Edge per `config/tts/locale_voice_routing.yaml` and note in CLOSEOUT.
2) Mux narration into vertical deliverables: for each teacher dir that has `final_tiktok.mp4` + `audio/narration_*.wav`, run ffmpeg to write `final_tiktok_with_narration.mp4` (example pattern):
   ffmpeg -y -i "<pack>/final_tiktok.mp4" -i "<pack>/audio/narration_<LOCALE>.wav" -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -shortest "<pack>/final_tiktok_with_narration.mp4"
   If `final_tiktok.mp4` is missing for a new teacher, STOP for that row and list in CLOSEOUT (do not invent video).
3) Git hygiene: identify which paths are tracked vs should stay untracked. Commit tracked code/config: `scripts/audio/generate_teacher_pack_narration_audio.py`, `scripts/video/run_voice_synthesis.py`, `config/tts/manga_character_voice_bank.yaml` (omote ja-JP). For `artifacts/video/tiktok_body_awareness/**` scripts and small text: commit if repo policy allows; for large WAV/MP4 either `.gitignore` + document artifact location, or Git LFS per docs/GIT_LFS_MIGRATION_PLAN.md / owner rule — do not bulk-add 40+ MB without governance check. Run push-guard + preflight before push (CLAUDE.md).
4) Coordination (optional): append a completed workstream row to `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` for this CJK TTS + mux lane (project `proj_state_convergence_20260328`), or bump `ACTIVE_PROJECTS.tsv` `last_updated` if Pearl_PM wants visibility; skip if owner prefers no TSV churn.

PROJECT_ID
proj_state_convergence_20260328

SUBSYSTEM + owner_agent
video_pipeline — Pearl_Video; integrations — Pearl_Int / CosyVoice2 wiring; manga_pipeline — Pearl_Dev (bank YAML only if further voice fixes); repo coordination — Pearl_GitHub for commit 3.

AUTHORITY_DOCS
docs/SESSION_UNITY_PROTOCOL.md; docs/INTEGRATION_CREDENTIALS_REGISTRY.md; docs/VIDEO_PIPELINE_SPEC.md; docs/VIDEO_PIPELINE_COMPLETE_GUIDE.md; docs/VIDEO_NARRATION_CJK_AND_AMBIENT_WIRING.md; config/tts/locale_voice_routing.yaml; config/tts/engines.yaml; config/tts/manga_character_voice_bank.yaml; docs/GITHUB_OPERATIONS_FRAMEWORK.md; docs/GITHUB_GOVERNANCE.md; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv

Conflict check
Do not edit `scripts/video/flux_client.py` or wholesale `config/video/*` (ws_video_image_washout_fix_20260411). Do not touch triptych/image paths (ws_teacher_manga_triptych_20260410). No overlap if WRITE_SCOPE stays body-awareness packs + listed scripts + optional TSV.

WRITE_SCOPE
artifacts/video/tiktok_body_awareness/{master_wu,master_feung,miki,junko,omote}/**; scripts/audio/generate_teacher_pack_narration_audio.py; scripts/video/run_voice_synthesis.py; config/tts/manga_character_voice_bank.yaml; optional artifacts/coordination/ACTIVE_WORKSTREAMS.tsv

OUT_OF_SCOPE
joshin; pearl_news; narrator_voice_assignments.yaml bulk edits; flux/video_bank refactors.

STOP / HANDOFF
If CosyVoice health fails after Keychain load, document and complete step 2 with Edge WAVs only. If governance blocks committing binaries, leave artifacts local and CLOSEOUT with STOP_REASON for owner decision.

STARTUP_RECEIPT
STARTUP_RECEIPT
AGENT:
TASK:
PROJECT_ID:
SUBSYSTEM:
AUTHORITY_DOCS:
READ_PATH_COMPLETE:
WRITE_SCOPE:
OUT_OF_SCOPE:
BLOCKERS:
READY_STATUS:
```

---

**User**

prompt for dev to work on step by step edits with me for: [The teacher plans and music files were created in earlier worktree states that got cleaned up during git branch switches. They need to be regenerated. The TTS files for all 13 teachers are also gone for the same reason.

**What's on your laptop right now** (at `~/Desktop/teacher_vid_package/`):

| Asset | Count | Status |
|-------|-------|--------|
| Scripts (en/ja/zh) | 3 | ✓ |
| Pipeline script | 1 | ✓ |
| Handoff doc | 1 | ✓ |
| ahjan frames + video | 10 + 1 | ✓ |
| joshin frames + video | 10 + 1 | ✓ |
| junko frames + video | 10 + 1 | ✓ |
| Teacher plan JSONs | 0 | **Lost — need regen** |
| Music MP3s | 0 | **Lost — need regen** |
| TTS WAVs | 0 | **Lost — need regen** |
| Other 10 teachers | 0 | **Lost — need regen** |

The git branch switching during this session wiped the untracked/uncommitted artifacts (plans, music, TTS, frames for 10 teachers). The 3 surviving teachers (ahjan, joshin, junko) had their frames committed or were in the active worktree.

**To get everything back**, I need to regenerate: teacher plans (fast — Agent tool), music (ElevenLabs ~2 min), TTS (CosyVoice ~10 min), then frames (ComfyUI ~45 min). Want me to start now, or is this enough for the handoff?]. i have all teacher vids with music and tts.

---

**Cursor**

```
You are Pearl_Dev + Pearl_Video (Pearl_PM as co-pilot with the owner). Obey docs/SESSION_UNITY_PROTOCOL.md: STARTUP_RECEIPT before edits; emit short CHECKPOINT notes between phases so the owner can approve each step (they want step-by-step work with them, not a single unattended batch).

OWNER CONTEXT (verbatim)
[The teacher plans and music files were created in earlier worktree states that got cleaned up during git branch switches. They need to be regenerated. The TTS files for all 13 teachers are also gone for the same reason.

What's on your laptop right now (at ~/Desktop/teacher_vid_package/):

| Asset | Count | Status |
| Scripts (en/ja/zh) | 3 | ✓ |
| Pipeline script | 1 | ✓ |
| Handoff doc | 1 | ✓ |
| ahjan frames + video | 10 + 1 | ✓ |
| joshin frames + video | 10 + 1 | ✓ |
| junko frames + video | 10 + 1 | ✓ |
| Teacher plan JSONs | 0 | Lost — need regen |
| Music MP3s | 0 | Lost — need regen |
| TTS WAVs | 0 | Lost — need regen |
| Other 10 teachers | 0 | Lost — need regen |

The git branch switching during this session wiped the untracked/uncommitted artifacts (plans, music, TTS, frames for 10 teachers). The 3 surviving teachers (ahjan, joshin, junko) had their frames committed or were in the active worktree.

To get everything back, I need to regenerate: teacher plans (fast — Agent tool), music (ElevenLabs ~2 min), TTS (CosyVoice ~10 min), then frames (ComfyUI ~45 min). Want me to start now, or is this enough for the handoff?].

Owner update (must honor): the owner now has **all teacher videos with music and TTS** (full deliverables on disk outside the table snapshot). Your job is to **reconcile** that truth with the repo: either **ingest** those files into canonical `artifacts/video/...` paths **or** regenerate only what is still missing after comparing Desktop inventory to repo expectations. **Never overwrite committed good assets without owner confirmation.**

PROJECT_ID
proj_state_convergence_20260328

SUBSYSTEM + owner_agent
video_pipeline — Pearl_Video; manga_pipeline / brand_admin — Pearl_Dev + Pearl_Prez if teacher_showcase or HTML paths touched; integrations — Pearl_Int for CosyVoice2 / ElevenLabs per docs/INTEGRATION_CREDENTIALS_REGISTRY.md.

AUTHORITY_DOCS
docs/SESSION_UNITY_PROTOCOL.md; docs/VIDEO_PIPELINE_SPEC.md; docs/VIDEO_PIPELINE_COMPLETE_GUIDE.md; docs/VIDEO_NARRATION_CJK_AND_AMBIENT_WIRING.md; docs/INTEGRATION_CREDENTIALS_REGISTRY.md; config/video/* as referenced by the existing pipeline job pattern; config/tts/locale_voice_routing.yaml; config/tts/engines.yaml; scripts/video/README.md; docs/GITHUB_OPERATIONS_FRAMEWORK.md (if committing); artifacts/coordination/ACTIVE_WORKSTREAMS.tsv (conflict scan).

Conflict check
Before touching `scripts/video/flux_client.py` or broad `config/video/*`, read `ACTIVE_WORKSTREAMS.tsv` for ws_video_image_washout_fix_20260411 and ws_teacher_manga_triptych_20260410 — stay out of their write_scope unless owner explicitly expands scope.

PHASED PLAN (stop and ask owner between phases)
**Phase 0 — Inventory (read-only):** List `~/Desktop/teacher_vid_package/` tree; list repo `artifacts/video/` (and any `staging/` paths) for the 13-teacher campaign; diff “what exists where.” Paste a one-page table to the owner: teacher_id | plan JSON | music | tts | frames | final mp4 | source path (Desktop vs repo).

**Phase 1 — Teacher plan JSONs:** Regenerate or copy from Desktop into the canonical per-teacher or per-pack directories the pipeline expects (match `run_pipeline.py` / `create_job.py` / existing `artifacts/video/**/job.json` conventions). If regen: use the smallest scripted path (Agent tool / python entrypoints already in repo). **Checkpoint:** owner approves paths + naming.

**Phase 2 — Music:** Regenerate MP3s via governed path (music bank + `run_soundtrack_engine.py` / ElevenLabs per config) **or** copy from owner’s full package if bit-identical to spec. **Checkpoint:** owner approves levels / track IDs.

**Phase 3 — TTS:** Run CosyVoice2 (Keychain `COSYVOICE_URL`) with `scripts/audio/generate_teacher_pack_narration_audio.py` or successor; Edge fallback only if CosyVoice fails. **Or** copy owner WAVs into `audio/` per teacher. **Checkpoint:** spot-listen 2 teachers.

**Phase 4 — Frames + ComfyUI:** Only for teachers still missing frames; use Pearl Star ComfyUI workflows already in repo; do not burn GPU time re-rendering ahjan/joshin/junko if owner says those are final. **Checkpoint:** owner approves which teachers to render.

**Phase 5 — Git / persistence:** After owner confirms, commit **tracked** pipeline + config changes; for large binaries follow repo policy (LFS / gitignore + artifact manifest). Run push-guard + preflight before push. Optionally append `ACTIVE_WORKSTREAMS.tsv` completed row `ws_teacher_vid_package_recovery_20260414` (or similar).

WRITE_SCOPE (fill precisely after Phase 0)
Default intent: `~/Desktop/teacher_vid_package/**` (read), `artifacts/video/**` (write), `scripts/video/**` `scripts/audio/**` `config/video/**` `config/tts/**` only as needed.

OUT_OF_SCOPE
Rewriting unrelated PRs; flux washout experiment unless owner merges scopes; deleting owner’s Desktop originals.

STOP / HANDOFF
If canonical target paths cannot be determined from repo, or owner package layout mismatches pipeline: STOP_REASON + list exact files owner should rename — HANDOFF_TO owner.

STARTUP_RECEIPT
STARTUP_RECEIPT
AGENT:
TASK:
PROJECT_ID:
SUBSYSTEM:
AUTHORITY_DOCS:
READ_PATH_COMPLETE:
WRITE_SCOPE:
OUT_OF_SCOPE:
BLOCKERS:
READY_STATUS:
```

---

**User**

desc / next? : STARTUP_RECEIPT
AGENT: Pearl_Dev (executor)
TASK: System fix — chapter contracts, frame governance, manuscript recurrence, exercise governance
PROJECT_ID: proj_state_convergence_20260328
SUBSYSTEM: core_pipeline
AUTHORITY_DOCS: docs/SESSION_UNITY_PROTOCOL.md; docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md; docs/DOCS_INDEX.md (navigation); artifacts/coordination/ACTIVE_PROJECTS.tsv; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv; config/quality/book_pass_gate_thresholds.yaml (threshold tiers)
READ_PATH_COMPLETE: yes (required pipeline files + coordination TSVs + overlay spec + session protocol)
WRITE_SCOPE: phoenix_v4/planning/chapter_planner.py; phoenix_v4/planning/enrichment_select.py; phoenix_v4/rendering/chapter_composer.py; phoenix_v4/rendering/book_renderer.py; phoenix_v4/quality/frame_governor.py; config/source_of_truth/chapter_purpose_contracts.yaml; config/source_of_truth/frame_registry.yaml; config/quality/ei_v2_config.yaml; scripts/run_pipeline.py; tests/test_chapter_purpose_contracts.py; tests/test_frame_governance.py; tests/test_manuscript_recurrence.py; tests/test_exercise_governance.py; tests/test_book_renderer.py; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv; artifacts/pilots/master_sha_system_fix_verify/
OUT_OF_SCOPE: ws_bestseller_spines_20260410; ws_pearl_news_daily_publish_20260411; ws_ei_v2_bestseller_corpus_20260413; merging PRs #418/#419; teacher_persona_matrix / atom pools; LLM frame detection
BLOCKERS: none (push_guard + preflight OK; health_check.sh exits 51 with existing upstream-branch warnings — informational)
READY_STATUS: ready

CLOSEOUT_RECEIPT
AGENT: Pearl_Dev
TASK: Chapter contracts + frame governance + cross-book recurrence + exercise control (spine + delivery)
COMMIT_SHA: 5500cc57d6
FILES_WRITTEN: config/source_of_truth/chapter_purpose_contracts.yaml; config/source_of_truth/frame_registry.yaml; phoenix_v4/quality/frame_governor.py; tests/test_chapter_purpose_contracts.py; tests/test_frame_governance.py; tests/test_manuscript_recurrence.py; tests/test_exercise_governance.py; artifacts/pilots/master_sha_system_fix_verify/* (pilot bundle)
FILES_READ: docs/SESSION_UNITY_PROTOCOL.md; docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md; phoenix_v4/planning/chapter_planner.py; phoenix_v4/planning/assembly_compiler.py (structure assignment context); phoenix_v4/rendering/chapter_composer.py; phoenix_v4/rendering/book_renderer.py; config/quality/book_pass_gate_thresholds.yaml; ACTIVE_WORKSTREAMS.tsv; ACTIVE_PROJECTS.tsv
STATUS: completed
HANDOFF_TO: Pearl_GitHub / owner (merge when ready)
NEXT_ACTION: Review PR https://github.com/Ahjan108/phoenix_omega_v4.8/pull/420; optional full pytest tests/ on CI; consider follow-on to strip frame-violating prose (currently warn-only).

PR: https://github.com/Ahjan108/phoenix_omega_v4.8/pull/420

Tests (local): 29 cases in the governance slice (tests/test_chapter_purpose_contracts.py, tests/test_frame_governance.py, tests/test_manuscript_recurrence.py, tests/test_exercise_governance.py, plus test_clean_for_delivery_strips_concatenated_spine_hook_lines in tests/test_book_renderer.py). Full pytest tests/ was not re-run in this session for wall-clock reasons; CI on the PR should run the suite.

Master Sha pilot acceptance (artifacts/pilots/master_sha_system_fix_verify/book.txt + quality_summary.json):

Criterion	Check
No raw scaffold text (## SCENE v01 etc.)
Pass (post clean_for_delivery; no ## HOOK / ## STORY headers in book.txt)
No signature line appears > 3 times (8-word grams)
Pass for this run (recurrence_report empty — no phrase exceeded the configured threshold after other passes)
Each chapter ≤ 2 exercises
Pass (caps enforced; see exercise_slots_dropped)
No metaphysical absolute claims in somatic_first prose
Fail if interpreted as “zero such sentences in the book”; Pass if interpreted as “governor flags them” — violations are logged in frame_governance_chapters but text is not rewritten in v1 (e.g. “Every organ has a frequency”, “disease is dissonance” still appear in body copy)
Chapter 0 is recognition (no exercises)
Pass (chapter_index 0 → max_allowed 0; two EXERCISE slots dropped in chapter 1 numbering)
Adjacent chapters have distinct emotional jobs
Mostly pass; warning logged: ch 11–12 both resolution (chapter_contract_warnings)
quality_summary.json shows recurrence_report
Pass (present; empty list this run)
quality_summary.json shows exercise_slots_dropped
Pass (12 entries)
Contracts that warned (not blocked): see frame_governance_chapters and chapter_contract_warnings in artifacts/pilots/master_sha_system_fix_verify/quality_summary.json (absolute-claim patterns, spiritual-before-ch3, spiritual_density, adjacent resolution).

Workstream: ws_system_fix_chapter_contracts_20260413 is registered as active in artifacts/coordination/ACTIVE_WORKSTREAMS.tsv.

---

**Cursor**

## Description

**Pearl_Dev** landed **Prompt D–style assembly governance** on **`core_pipeline`**: chapter purpose contracts, a **frame governor** (somatic vs spiritual rules), **manuscript recurrence** caps (e.g. 8-word grams ≤3), and **exercise** caps (e.g. ≤2 per chapter, chapter 0 no exercises), wired through planning/rendering paths you listed. New config lives under **`config/source_of_truth/`** (`chapter_purpose_contracts.yaml`, `frame_registry.yaml`), logic in **`phoenix_v4/quality/frame_governor.py`**, plus **29 focused tests** and a **Master Sha pilot** under **`artifacts/pilots/master_sha_system_fix_verify/`**.

**Master Sha pilot:** Scaffold leakage, recurrence over-threshold, and exercise over-cap **pass** for this run; **chapter 0** and **adjacent emotional jobs** mostly pass with **contract warnings** (e.g. ch 11–12 both “resolution”). **Frame governance** is **not** “zero bad sentences in output”: it **logs** violations (`frame_governance_chapters`) but **does not rewrite** prose in v1, so lines like organ/frequency or “disease is dissonance” can **still appear** in `book.txt` while being **flagged**.

**Delivery:** **`COMMIT_SHA: 5500cc57d6`**, **PR #420** — handoff to **Pearl_GitHub / owner** to merge. **`ws_system_fix_chapter_contracts_20260413`** was added to **`ACTIVE_WORKSTREAMS.tsv`** as **active**; it should flip to **completed** after merge + evidence, per protocol.

---

## Next (ordered)

1. **Review and merge [PR #420](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/420)** after you’re happy with diff scope and governance CI. Run **preflight / push-guard** if you touch the branch locally.
2. **Trust but verify CI:** full **`pytest tests/`** on the PR (executor skipped full suite for wall-clock). Fix any red jobs before merge.
3. **After merge:** update **`artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`** — set **`ws_system_fix_chapter_contracts_20260413`** to **`completed`**, add evidence (merge SHA, pilot path), **`last_updated`**, **`next_owner`** Pearl_PM if useful.
4. **Decide on v2 frame behavior:** either keep **warn-only** and use reports for editorial passes, or plan a **follow-on** that **strips or softens** frame-violating sentences (needs product/architect agreement so you don’t mangle intentional doctrine chapters).
5. **Reconcile open spine/corpus PRs** from **`SESSION_HANDOFF_2026_04_13.md`** (#418, #419, #416, #417) with main after #420 — avoid long-lived drift between assembly gates and spine bridges.
6. **Human pass:** skim **`artifacts/pilots/master_sha_system_fix_verify/book.txt`** and **`quality_summary.json`** (`frame_governance_chapters`, `chapter_contract_warnings`, `exercise_slots_dropped`) to confirm the **reader experience** matches the metrics.

If you want a **one-shot paste prompt** for Pearl_GitHub (merge #420 + TSV closeout + optional full pytest locally), say so and I’ll output only that block.

---

**User**

write a prompt for: I’m checking the PR directly so I can tell you what to do next based on what actually landed, not just the receipt.

Received app response
I’ve got the shape of it. The key decision is whether to treat #420 as a merge-now governance baseline or hold it for a stronger v2 that rewrites bad frame prose.
What to do next:
The short answer
Merge #420 once CI is green and the diff scope looks clean.
Do not hold this PR waiting for perfect frame rewriting.
Why: this PR fixes the system class of failures you just surfaced in the book:

scaffold leakage
uncontrolled repetition
weak chapter-purpose enforcement
exercise over-dumping
no frame governance signals
That is a meaningful baseline improvement already. The one thing it does not do is rewrite bad spiritual/metaphysical sentences out of somatic-first prose. But that is a v2 behavior choice, not a reason to block the governance baseline.
My recommendation
1. Review PR #420 with one question in mind
Not “is this perfect?”
Ask:

“Does this safely improve the pipeline baseline without introducing brittle behavior?”
From the receipt, the answer looks like yes.
The pilot already shows:

scaffold cleanup passing
recurrence caps passing
exercise caps passing
chapter 0 recognition rule passing
chapter-emotional-job checks mostly passing with warnings
frame violations being logged instead of silently ignored
That is enough to justify merge as governance v1.
2. Merge #420 if these are true
Before merging, confirm only these:
Must-have
PR CI passes, especially full pytest tests/
no unexpected renderer regressions
pilot artifact outputs are present and readable
quality_summary.json includes:
recurrence_report
exercise_slots_dropped
frame_governance_chapters
chapter_contract_warnings
Nice-to-have
quick skim of book.txt from the pilot to confirm it feels cleaner to a human, not just to metrics
If those are true, merge it.
3. Do not block merge on warn-only frame governance
This is the most important judgment call.
Right now frame governance is:

detect + log
not rewrite + strip
That is fine for v1.
Blocking this PR until the system can automatically soften or remove lines like:

“Every organ has a frequency”
“Disease is dissonance”
would slow down the broader system fix. And automatic rewriting is riskier because it can mangle intentional doctrine sections.
So the right stance is:

Merge warn-only governance now.
Plan enforcement/rewrite behavior as a follow-on with product/architect signoff.
That is the cleanest path.
4. After merge, immediately close the workstream properly
Update ACTIVE_WORKSTREAMS.tsv:
mark ws_system_fix_chapter_contracts_20260413 as completed
include:
merge SHA
PR #420
evidence path: artifacts/pilots/master_sha_system_fix_verify/
last_updated
next_owner if needed
This matters because otherwise the repo truth stays sloppy even if the code is right.
5. Open one follow-on for frame enforcement v2
This should be a separate workstream, not stuffed into #420 retroactively.
Proposed scope for v2
define which frame violations are:
warn-only
soft-rewrite
hard-strip
hard-fail
decide whether doctrine chapters get different rules from somatic-first chapters
add tests for preservation of intentional spiritual sections
avoid blunt censorship of legitimate teacher voice
Good framing
Call it something like:
Frame Enforcement v2 — prose softening / stripping policy

Because right now you have governance visibility, but not output correction.

6. Run at least 2–3 more specimen pilots before declaring the system “fixed”
This is important.
Master Sha is useful, but one pilot is not enough. You should regenerate and inspect books from at least three content shapes:

anxiety / burnout somatic-first
grief / healing emotional-first
spiritual doctrine heavier
optionally one micro format if the same pipeline touches those
Reason: you want to know whether:
recurrence caps generalize
chapter-purpose contracts actually differentiate chapters
exercise caps still preserve usefulness
frame warnings explode in some families but not others
Right now the system looks improved, not fully proven.
7. Rebase or reconcile the other open spine-related PRs after #420 merges
You mentioned #418, #419, #416, #417.
That matters because long-lived drift between:

bridge logic
chapter contracts
frame governance
renderer cleanup
spine/corpus work
can create conflicting behavior and confusing regression reports.
So the order should be:

merge #420
update main
rebase/reconcile the other spine/corpus PRs
rerun specimen pilots where needed
Do not let #420 sit unmerged while those branches drift further.
8. Human read the pilot, not just the JSON
This is non-negotiable.
A governance system can pass metrics and still produce a book that feels dead, over-sanitized, or oddly flattened.

So someone should skim:

artifacts/pilots/master_sha_system_fix_verify/book.txt
quality_summary.json
and check:
does the chapter progression feel more distinct?
are exercise cuts helping or hurting?
are repeated lines truly reduced to human perception?
do frame warnings correspond to passages that actually feel wrong?
did cleanup remove visible artifacts without damaging prose?
This is where “system improved” becomes “reader improved.”
My actual call
I would do this:
Merge PR #420 once CI is green.
Then immediately:
close the workstream TSV properly
open a separate v2 frame-enforcement follow-on
run 2–3 more specimen pilots
reconcile the other open spine/corpus PRs against main
That is the right operational sequence.
What not to do
Do not:
hold #420 hostage waiting for perfect frame rewriting
declare the system fixed based on one pilot
merge other spine PRs first and let governance drift
rely only on quality_summary.json without reading the actual book
Bottom-line verdict
#420 looks merge-worthy as governance baseline v1.
It fixes real systemic failures in the manuscript path.
It does not finish the job.
The next real frontier is frame enforcement in output, not just frame warning in reports.
If you want, I can turn this into a single paste-ready instruction block for Pearl_GitHub.
y
I’m posting a concise review/merge recommendation on the PR so the repo has a clear decision trail.

Received app response
Done. I posted a clear merge recommendation directly on PR #420 so the decision trail is explicit in the repo.
Your next move (literally just do this now)
Open the PR:
GitHub → PR #420
Check:
CI is green (especially full pytest tests/)
Click Merge
Immediately after merge
Update:
artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
Set:
ws_system_fix_chapter_contracts_20260413 → completed
Add:
merge SHA
PR #420
evidence: artifacts/pilots/master_sha_system_fix_verify/
Then (don’t skip this)
Create a new workstream:
Frame Enforcement v2
Because right now the system:
✅ detects bad frame sentences
❌ does NOT fix them
That’s your next real leverage point.
If you want, I can write the exact TSV line + the v2 workstream spec so you can paste it in clean with zero thinking.
y
Writing
ACTIVE_WORKSTREAMS.tsv closeout row:
ws_system_fix_chapter_contracts_20260413 completed Pearl_Dev core_pipeline Merge PR #420 governance baseline v1; chapter purpose contracts + frame governance + manuscript recurrence caps + exercise governance landed. Evidence: merge SHA <MERGE_SHA>; PR https://github.com/Ahjan108/phoenix_omega_v4.8/pull/420; pilot artifacts/pilots/master_sha_system_fix_verify/ 2026-04-14 Pearl_PM
V2 workstream spec:
`STARTUP_RECEIPT
AGENT: Pearl_Architect or Pearl_Dev
TASK: Frame Enforcement v2 — policy + implementation for warn / soften / strip / fail
PROJECT_ID: proj_state_convergence_20260328
SUBSYSTEM: core_pipeline
AUTHORITY_DOCS: docs/SESSION_UNITY_PROTOCOL.md; docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md; docs/DOCS_INDEX.md; config/source_of_truth/frame_registry.yaml; config/quality/book_pass_gate_thresholds.yaml
READ_PATH_COMPLETE: yes
WRITE_SCOPE: phoenix_v4/quality/frame_governor.py; phoenix_v4/rendering/book_renderer.py; config/source_of_truth/frame_registry.yaml; config/quality/ei_v2_config.yaml; tests/test_frame_governance.py; tests/test_book_renderer.py; artifacts/pilots/frame_enforcement_v2_verify/
OUT_OF_SCOPE: teacher doctrine atom rewrites; LLM-based frame classification; Pearl News
BLOCKERS: none
READY_STATUS: ready

GOAL
Move frame governance from warn-only to explicit policy-controlled behavior by frame and chapter context.

REQUIRED BEHAVIOR

Classify violations into:
warn_only
soften_in_place
strip_sentence
hard_fail
Support chapter/frame context:
somatic_first chapters: stricter handling of metaphysical absolutes
doctrine/spiritual chapters: allow configured higher spiritual density
early chapters: stricter rules on spiritual-before-ch3 spillover unless contract allows it
Preserve intentional doctrine:
do not bluntly remove teacher-voice sections that are allowed by chapter contract / frame policy
log every softened or stripped sentence in quality output
Quality output must include:
frame_governance_chapters
frame_softened_sentences
frame_stripped_sentences
frame_hard_fail_reasons
ACCEPTANCE TESTS
somatic_first specimen strips or softens disallowed absolute claims in body prose
doctrine-heavy specimen preserves allowed spiritual sections
no scaffold or malformed prose introduced by rewriting
quality_summary.json records every intervention
tests cover warn / soften / strip / fail branches
DELIVERABLE
PR with implementation + tests + pilot bundle under artifacts/pilots/frame_enforcement_v2_verify/`







---

**Cursor**

Checking `ACTIVE_WORKSTREAMS.tsv` column format so the prompt includes a valid TSV row.



Use **two** paste-ready blocks: first finishes **#420 + coordination**; second kicks off **Frame Enforcement v2**.

---

### Prompt 1 — Pearl_GitHub + owner (merge #420, close workstream, open v2)

```
You are Pearl_GitHub + Pearl_PM. Obey docs/SESSION_UNITY_PROTOCOL.md, CLAUDE.md (preflight, push-guard, mass-delete rule: gh pr diff <n> --stat | tail -1 before merge), docs/GITHUB_GOVERNANCE.md, docs/GITHUB_OPERATIONS_FRAMEWORK.md.

Emit STARTUP_RECEIPT before git/GitHub actions; CLOSEOUT_RECEIPT after.

PHASE A — Merge PR #420
PR: https://github.com/Ahjan108/phoenix_omega_v4.8/pull/420

Merge judgment (document in PR comment if not already): treat as governance baseline v1 — merge when CI is green; do not block on automatic rewriting of frame-violating prose (that is v2).

Must-have before merge:
- PR CI green, especially full pytest tests/
- No surprise renderer regressions in diff review
- Pilot artifacts on branch readable: artifacts/pilots/master_sha_system_fix_verify/book.txt and quality_summary.json
- quality_summary.json includes: recurrence_report, exercise_slots_dropped, frame_governance_chapters, chapter_contract_warnings

Nice-to-have: human skim of pilot book.txt for “feels cleaner,” not only metrics.

If all must-haves pass → merge (squash/merge per repo convention). Record the resulting merge commit SHA as <MERGE_SHA>.

PHASE B — ACTIVE_WORKSTREAMS.tsv
On main after merge (single commit or same PR follow-up only if owner allows; prefer fresh branch agent/workstream-closeout-420 from origin/main):

1) Locate row workstream_id ws_system_fix_chapter_contracts_20260413.
   - If status was active: set status completed; fill evidence_paths with: merge <MERGE_SHA>; PR https://github.com/Ahjan108/phoenix_omega_v4.8/pull/420; pilot artifacts/pilots/master_sha_system_fix_verify/
   - If row missing: append one completed row (same fields below).

2) Append NEW row for Frame Enforcement v2 (status: pending or in_progress; owner_agent Pearl_Architect + Pearl_Dev; next_owner Pearl_PM; last_updated 2026-04-14):

project_id: proj_state_convergence_20260328
workstream_id: ws_frame_enforcement_v2_20260414
status: pending
owner_agent: Pearl_Architect + Pearl_Dev
task: Frame Enforcement v2 — policy + implementation: warn_only | soften_in_place | strip_sentence | hard_fail; somatic_first vs doctrine chapters; log softened/stripped; quality_summary extensions; pilots under artifacts/pilots/frame_enforcement_v2_verify/
subsystem: core_pipeline
branch: none (to be created agent/frame-enforcement-v2)
base_ref: origin/main
write_scope: phoenix_v4/quality/frame_governor.py;phoenix_v4/rendering/book_renderer.py;config/source_of_truth/frame_registry.yaml;config/quality/ei_v2_config.yaml;tests/test_frame_governance.py;tests/test_book_renderer.py;artifacts/pilots/frame_enforcement_v2_verify/
authority_doc: docs/SESSION_UNITY_PROTOCOL.md;docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md;docs/DOCS_INDEX.md;config/source_of_truth/frame_registry.yaml;config/quality/book_pass_gate_thresholds.yaml
evidence_paths: none yet
temp_or_output_paths: artifacts/pilots/frame_enforcement_v2_verify/
blockers: none
next_owner: Pearl_PM

Use real TSV tabs between columns; match header order in artifacts/coordination/ACTIVE_WORKSTREAMS.tsv.

PHASE C — Operational sequence (document in CLOSEOUT NEXT_ACTION)
- Rebase/reconcile open spine/corpus PRs (#418, #419, #416, #417) against main after #420 merge; rerun 2–3 specimen pilots (somatic-first, grief/healing, doctrine-heavier, optional micro) before declaring system “proven.”
- Human must read pilot book.txt + JSON, not metrics alone.

PROJECT_ID: proj_state_convergence_20260328
WRITE_SCOPE: artifacts/coordination/ACTIVE_WORKSTREAMS.tsv; optional PR comment only
OUT_OF_SCOPE: implementing v2 code in this chat (separate Prompt 2)

CLOSEOUT: MERGE_SHA, link #420, confirm TSV edits, HANDOFF_TO Pearl_Dev for Prompt 2 if v2 is next.
```

---

### Prompt 2 — Pearl_Architect + Pearl_Dev (Frame Enforcement v2 executor)

```
You are Pearl_Architect + Pearl_Dev. Obey docs/SESSION_UNITY_PROTOCOL.md (STARTUP_RECEIPT / CLOSEOUT_RECEIPT). Do not interleave ws_bestseller_spines_20260410 or ws_pearl_news_daily_publish_20260411 without Pearl_PM coordination.

PROJECT_ID: proj_state_convergence_20260328
SUBSYSTEM: core_pipeline (Pearl_Prime alignment on overlay spec)
AUTHORITY_DOCS: docs/SESSION_UNITY_PROTOCOL.md; docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md; docs/DOCS_INDEX.md; config/source_of_truth/frame_registry.yaml; config/source_of_truth/chapter_purpose_contracts.yaml; config/quality/book_pass_gate_thresholds.yaml; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv (ws_frame_enforcement_v2_20260414)

Branch: agent/frame-enforcement-v2 from origin/main after PR #420 is merged (rebase if needed).

GOAL
Move frame governance from v1 (detect + log only) to explicit, policy-controlled output behavior.

REQUIRED BEHAVIOR
1) Classify each frame violation into: warn_only | soften_in_place | strip_sentence | hard_fail — driven by config in frame_registry.yaml (or extension), not ad-hoc code branches.
2) Chapter / frame context:
   - somatic_first: stricter on metaphysical absolutes in body prose
   - doctrine / spiritual chapters: allow higher spiritual density when chapter contract or frame policy says so
   - early chapters: enforce spiritual-before-ch3 rules unless contract explicitly allows
3) Preservation: do not bluntly remove teacher voice where contract + policy mark doctrine as allowed; prefer warn or no-op in those blocks.
4) Telemetry: log every soften/strip in quality output:
   - frame_governance_chapters (existing or extended)
   - frame_softened_sentences
   - frame_stripped_sentences
   - frame_hard_fail_reasons

QUALITY / TESTS
- Somatic-first specimen: disallowed absolute claims in body are softened or stripped per policy (not only logged).
- Doctrine-heavy specimen: allowed spiritual sections preserved; tests assert no erroneous strip.
- No new scaffold junk or broken prose from rewrite pass.
- quality_summary.json records every intervention.
- tests/test_frame_governance.py (and book_renderer tests) cover warn / soften / strip / hard_fail branches.

DELIVERABLES
- Implementation in phoenix_v4/quality/frame_governor.py + phoenix_v4/rendering/book_renderer.py (or single clear pipeline stage — document choice).
- Config updates: frame_registry.yaml (+ ei_v2_config.yaml only if needed for reporting hooks).
- Pilot bundle: artifacts/pilots/frame_enforcement_v2_verify/ with book.txt + quality_summary.json + short README criteria checklist.

OUT_OF_SCOPE: LLM-based frame classification; Pearl News; wholesale atom rewrites; narrator_voice_assignments.

WRITE_SCOPE: as listed in ws_frame_enforcement_v2_20260414 row; update that workstream to in_progress at start and completed in CLOSEOUT with PR link + pilot paths.

READY_STATUS: blocked until #420 is merged — if not merged, STOP and HANDOFF_TO owner with reason.
```

---

**Note:** In this workspace, `ws_system_fix_chapter_contracts_20260413` does not appear in `ACTIVE_WORKSTREAMS.tsv` yet. **Prompt 1** covers both **update-if-present** and **append completed row** so the executor does not get stuck. Replace `<MERGE_SHA>` with the real merge commit after you merge.

---

**User**

verify: I can estimate it, but I can’t give you a trustworthy repo-grounded number from here because the GitHub connector available to me in this chat can search, but it is not exposing the repo files I’d need to read the actual image-bank config, and web browsing is disabled.

So the honest answer is:

## Likely range

For **one US-English brand image bank**, total generation time is probably in one of these bands:

* **Small bank**: **2–6 hours**
* **Mid-size bank**: **8–24 hours**
* **Large full bank**: **1–4 days**

## What decides it

The total time is basically:

**number of final images ÷ real sustained images-per-hour**

That depends on:

* how many unique assets Brand 1 USA actually needs
* whether you generate **1 aspect ratio** or **3** (`16:9`, `9:16`, `1:1`)
* whether you keep **1 final per prompt** or generate **multiple candidates**
* whether this is **FLUX only** or mixed models
* your real throughput on your machine, not ideal throughput
* whether there is retry/QC/dedup/upscale time

## Fast way to think about it

Here are some concrete examples:

### Example A

* 1,200 final images needed
* 1 aspect ratio
* sustained throughput: 150 images/hour

Time: **about 8 hours**

### Example B

* 1,200 base concepts
* 3 aspect ratios each
* total 3,600 images
* sustained throughput: 150 images/hour

Time: **about 24 hours**

### Example C

* 2,000 base concepts
* 3 aspect ratios
* 2 candidates each before selecting final
* effective total renders: 12,000
* sustained throughput: 150 images/hour

Time: **about 80 hours**
So: **around 3.3 days**

## My best judgment

Given how you’ve described the Phoenix visual system before, I would **not** assume this is a tiny bank. If Brand 1 USA means a proper reusable bank across intents, topics, emotional bands, personas, and ratios, my best estimate is:

## **Around 1 to 3 days**

for a serious first-pass full image bank,

and

## **8 to 16 hours**

for a lean MVP bank.

## To get the exact number

You only need these two values:

* **Total required final images for Brand 1 USA**
* **Your measured sustained generation speed** over 100–200 renders

Then:

## **time = total_images / images_per_hour**

If you paste any of these, I can give you a much tighter estimate immediately:

* the Brand 1 USA image-bank count
* the per-topic/per-intent asset matrix
* a sample run showing how long 50 or 100 images took


---

**Cursor**

Checking the repo for image-bank or flux-bank configuration so we can ground or refine those estimates.



---

**User**

next prompt? ;STARTUP_RECEIPT
AGENT:              Pearl_Architect + Pearl_Dev
TASK:               Frame Enforcement v2 — policy-driven warn/soften/strip/hard_fail + telemetry + pilots
PROJECT_ID:         proj_state_convergence_20260328
SUBSYSTEM:          core_pipeline
AUTHORITY_DOCS:     docs/SESSION_UNITY_PROTOCOL.md;docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md;docs/DOCS_INDEX.md;config/source_of_truth/frame_registry.yaml;config/source_of_truth/chapter_purpose_contracts.yaml;config/quality/book_pass_gate_thresholds.yaml;artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
READ_PATH_COMPLETE: yes
WRITE_SCOPE:        phoenix_v4/quality/frame_governor.py;phoenix_v4/rendering/book_renderer.py;phoenix_v4/rendering/chapter_composer.py;phoenix_v4/planning/chapter_planner.py;config/source_of_truth/frame_registry.yaml;scripts/run_pipeline.py;tests/test_frame_governance.py;artifacts/pilots/frame_enforcement_v2_verify/*;artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
OUT_OF_SCOPE:       LLM frame classification; Pearl News; wholesale atom rewrites; narrator_voice_assignments; ei_v2_config.yaml (not required)
BLOCKERS:           none (PR #420 already on main at session start)
READY_STATUS:       ready
What shipped
PR: https://github.com/Ahjan108/phoenix_omega_v4.8/pull/422 (squash-merged)
Merge commit: e4381650f8b4dd37d5c7de8e3b5845611ca8911d

Design choice (documented in code)
Spine / enriched path: apply_frame_enforcement runs inside compose_from_enriched_book on each chapter’s joined slot body, after exercise caps and before strengthen_rendered_spine_manuscript, so doctrine is known from slots (TEACHER_DOCTRINE) and contracts from assign_chapter_purpose_contracts.
Registry TxtWriter path: the same enforcement runs after strengthen_chapter_flow_for_delivery when clean_output, using plan frame / spine_context.frame and per-chapter contracts + slot types.
Config (config/source_of_truth/frame_registry.yaml)
Root version: 2; existing frames: kept; added governance_v2 with enabled, per-violation violation_policies (default vs doctrine_chapter vs allow_early_spiritual_contract), hard_fail_violation_types, absolute_softeners, lexicon_softeners.
doctrine_chapter_spiritual_density_max under somatic_first for higher spiritual share when a doctrine chapter is flagged.
Code
frame_governor.py: FrameEnforcementContext, apply_frame_enforcement, FrameGovernanceHardFail; frame_governance_check extended with optional doctrine_chapter / allow_early_spiritual / emotional_job for analysis-only use.
chapter_planner.py: ChapterContract.allow_early_spiritual from YAML allow_early_spiritual.
chapter_composer.py: merges frame_softened_sentences, frame_stripped_sentences, frame_hard_fail_reasons, richer frame_governance_chapters entries.
book_renderer.py: per-chapter enforcement + clean_for_delivery still receives one governance_report dict (frame keys pre-seeded).
scripts/run_pipeline.py: spine quality_summary.json includes the three new frame lists.
Pilot
artifacts/pilots/frame_enforcement_v2_verify/: book.txt, quality_summary.json, README.md (criteria checklist). Fixture demonstrates strip (ch1 absolute), doctrine preserve + warn (ch2), early spiritual soften (ch3 chakra).
Tests
tests/test_frame_governance.py: v2 cases for strip, doctrine preservation, early soften, contract bypass, hard_fail, governance_v2.enabled: false.
Workstream row
ws_frame_enforcement_v2_20260414: set to completed with evidence pointing at PR #422 and pilot paths (on the PR branch; now on main via merge).
Coordination: No interleaving with ws_bestseller_spines_20260410 or ws_pearl_news_daily_publish_20260411 in this change set.

CLOSEOUT_RECEIPT
AGENT:          Pearl_Architect + Pearl_Dev
TASK:           Frame Enforcement v2 implementation + pilot + workstream closeout
COMMIT_SHA:     e4381650f8b4dd37d5c7de8e3b5845611ca8911d (squash merge of PR #422; branch commits 5e86b2639b + 17def5be19)
FILES_WRITTEN:  phoenix_v4/quality/frame_governor.py; phoenix_v4/rendering/chapter_composer.py; phoenix_v4/rendering/book_renderer.py; phoenix_v4/planning/chapter_planner.py; config/source_of_truth/frame_registry.yaml; scripts/run_pipeline.py; tests/test_frame_governance.py; artifacts/pilots/frame_enforcement_v2_verify/README.md; artifacts/pilots/frame_enforcement_v2_verify/book.txt; artifacts/pilots/frame_enforcement_v2_verify/quality_summary.json; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
FILES_READ:     docs/SESSION_UNITY_PROTOCOL.md; docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md; docs/DOCS_INDEX.md; config/source_of_truth/frame_registry.yaml; config/source_of_truth/chapter_purpose_contracts.yaml; config/quality/book_pass_gate_thresholds.yaml; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
STATUS:         completed
HANDOFF_TO:     Pearl_PM
NEXT_ACTION:    Optional: add `merge e4381650f8b4dd37d5c7de8e3b5845611ca8911d` to TSV `evidence_paths` if you want the row to cite the squash SHA explicitly. Run broader `pytest tests/` on `main` after `git pull`. Tune `frame_registry.yaml` policies/softeners with owner/editor review; do not interleave bestseller spines or Pearl News daily publish lanes without Pearl_PM.
Local sync: run git fetch origin main && git checkout main && git pull to pick up e4381650f8b4dd37d5c7de8e3b5845611ca8911d.

---

**Cursor**

Use this as the **next** paste-ready block after **PR #422** / **`e4381650f8`** on `main`:

```
You are Pearl_Dev + Pearl_PM (validation + specimen pass; Pearl_Architect consult if policy tuning needs spec alignment). Obey docs/SESSION_UNITY_PROTOCOL.md: STARTUP_RECEIPT before work; CLOSEOUT_RECEIPT after.

OWNER TASK — Post Frame Enforcement v2 (#422)
PR #422 is squash-merged to main (merge SHA e4381650f8b4dd37d5c7de8e3b5845611ca8911d). Frame governance v2 is live: policy-driven warn / soften / strip / hard_fail + telemetry in quality_summary. Next: prove it on real shapes, stabilize main, and tighten policy only with evidence — not more code churn without pilot proof.

PROJECT_ID
proj_state_convergence_20260328

SUBSYSTEM
core_pipeline — Pearl_Prime / Pearl_Dev alignment with docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md

AUTHORITY_DOCS
docs/SESSION_UNITY_PROTOCOL.md; docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md; docs/DOCS_INDEX.md; config/source_of_truth/frame_registry.yaml; config/source_of_truth/chapter_purpose_contracts.yaml; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv

PHASE 1 — Mainline hygiene (do first)
- git fetch origin && git checkout main && git pull
- Run full `pytest tests/` on main; fix any failures introduced by drift or env (do not disable tests without owner signoff)
- If green: note SHA in CLOSEOUT

PHASE 2 — Coordination TSV (optional but recommended)
- In artifacts/coordination/ACTIVE_WORKSTREAMS.tsv, row `ws_frame_enforcement_v2_20260414`: ensure `status` is `completed` and `evidence_paths` explicitly includes merge `e4381650f8b4dd37d5c7de8e3b5845611ca8911d` and PR https://github.com/Ahjan108/phoenix_omega_v4.8/pull/422 and pilot `artifacts/pilots/frame_enforcement_v2_verify/`; set `last_updated` to session date

PHASE 3 — Specimen pilots (minimum 3 books / shapes, not one)
Regenerate and write artifacts under e.g. `artifacts/pilots/frame_v2_specimen_<name>/` with `book.txt` + `quality_summary.json` for:
1) Somatic-first therapeutic (e.g. anxiety or burnout — same family as Master Sha stress test)
2) Grief / healing emotional-first (different emotional_job / contract mix)
3) Doctrine-heavier or TEACHER_DOCTRINE-rich chapter (must show: strips/softens in body where policy says; preservation where doctrine chapter / contract allows)

For each specimen, owner (or you) skims prose + JSON: `frame_softened_sentences`, `frame_stripped_sentences`, `frame_hard_fail_reasons`, `frame_governance_chapters` — confirm interventions match reader intent (no over-sanitization, no missed absolutes in somatic body).

PHASE 4 — Policy tuning (only after Phase 3 evidence)
- Adjust `config/source_of_truth/frame_registry.yaml` (`governance_v2`, `violation_policies`, softeners) in small commits; re-run the same 3 specimens; document delta in pilot README bullets
- OUT OF SCOPE: LLM classification, ei_v2_config.yaml, Pearl News, narrator_voice_assignments, wholesale atom edits

PHASE 5 — Handoff
- CLOSEOUT: list pilot dirs, pytest result, any YAML diffs committed, remaining risks (e.g. “hard_fail too aggressive for format X”)
- HANDOFF_TO: Pearl_PM for scheduling editor review of softener copy; Pearl_GitHub if a follow-up PR is needed

CONFLICT / LANE RULES
Do not interleave ws_bestseller_spines_20260410 or ws_pearl_news_daily_publish_20260411 in this session unless Pearl_PM explicitly expands scope.

WRITE_SCOPE
artifacts/pilots/frame_v2_specimen_*/*; config/source_of_truth/frame_registry.yaml; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv; optional short doc under docs/ only if required by repo convention for pilot summary

OUT_OF_SCOPE
New frame_governor.py architecture; reopening PR #422; merging unrelated spine/corpus PRs in the same commit as policy tweaks

STARTUP_RECEIPT
STARTUP_RECEIPT
AGENT:
TASK:
PROJECT_ID:
SUBSYSTEM:
AUTHORITY_DOCS:
READ_PATH_COMPLETE:
WRITE_SCOPE:
OUT_OF_SCOPE:
BLOCKERS:
READY_STATUS:
```

**Short “what this is”:** it’s the **prove-and-tune** pass after v2 shipped: **full pytest on `main`**, **TSV evidence line**, **three real specimen books** + human skim, then **only then** **`frame_registry.yaml` tweaks** with before/after pilots — not more framework work until metrics and reading agree.

---

**User**

write a prompt to clean up the repo. there's lots test files and junk. stuff that is decommissioned should be deleted or zipped

---

**Cursor**

```
You are Pearl_GitHub + Pearl_Dev + Pearl_PM (repo hygiene). Obey docs/SESSION_UNITY_PROTOCOL.md (STARTUP_RECEIPT / CLOSEOUT_RECEIPT), CLAUDE.md, docs/GITHUB_GOVERNANCE.md, docs/GITHUB_OPERATIONS_FRAMEWORK.md, docs/OWNERSHIP_MATRIX.md, docs/DOCS_INDEX.md.

OWNER TASK
Clean up the Phoenix Omega repo: remove or archive obvious junk, redundant test files, and decommissioned paths. Prefer **delete** for generated/cache cruft and **zip + remove originals** (or move to `salvage/` / `artifacts/archive/`) for large decommissioned trees you can prove unused. Work **step-by-step with the owner**: present an inventory and get explicit approval before bulk deletes.

PROJECT_ID
proj_state_convergence_20260328

SUBSYSTEM
repo coordination (Pearl_GitHub primary); touch other subsystems only when paths are clearly junk under their trees.

AUTHORITY_DOCS
docs/SESSION_UNITY_PROTOCOL.md; docs/GITHUB_GOVERNANCE.md; docs/GITHUB_OPERATIONS_FRAMEWORK.md; docs/OWNERSHIP_MATRIX.md; docs/DOCS_INDEX.md; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv; artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv

NON-NEGOTIABLES
1) **Mass deletion gate:** Before deleting **>50 files** in one change (or any PR), STOP and get **explicit owner approval** (CLAUDE.md / governance: catastrophic deletion incident). Report `git diff --stat` / file count.
2) **Do not** delete or gut `tests/` that are still referenced by CI or `pytest` discovery without proving zero references and owner OK.
3) **Do not** delete `config/**`, `phoenix_v4/**`, `scripts/ci/**`, `.github/workflows/**`, or authority specs because they “look old” — only after a doc or code reference search shows decommissioned + owner signoff.
4) **Never** delete secrets, Keychain docs, or `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` targets.
5) Prefer **git rm** for tracked junk; for untracked-only, document paths and use owner-approved `rm` / archive zip.

PHASE 0 — Inventory (read-only)
- Scan for: duplicate `test_*.py` outside canonical `tests/`; `*_test.py` orphans; `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `*.pyc`, `*.pyo`; stale `.claude/worktrees/*`, `_wt_*` if repo policy allows; huge `node_modules` if accidentally committed; duplicate logs under `artifacts/**`; obvious `tmp/`, `scratch/`, `old_*`, `deprecated_*` **only if** no imports reference them (`rg` / `pytest --collect-only`).
- Produce **one** machine-readable list: `artifacts/coordination/REPO_CLEANUP_CANDIDATES_2026.tsv` (columns: path, category(cache|duplicate_test|decommissioned|artifact_junk|uncertain), suggested_action(delete|zip_archive|keep|ask_owner), evidence_one_line, tracked_untracked).

PHASE 1 — Owner review
- Paste summary table (top 30 rows + counts by category). Owner replies **approve category X** or **path exceptions**. Do nothing destructive until approved.

PHASE 2 — Safe automatic wins (low risk)
- Delete **untracked** cache dirs only if standard and not in .gitignore by mistake: `__pycache__`, `.pytest_cache` under workspace (not in venv paths). Re-run a **small** pytest slice or `python -m compileall` if you touched Python layout.
- **Do not** run `git clean -fdx` without owner typing the command.

PHASE 3 — Tracked cleanup (approved only)
- **Duplicate / decommissioned tests:** remove only with proof (no collector references, no CI mention). One focused commit per theme.
- **Decommissioned features:** zip tree → `artifacts/archive/<name>_<DATE>.zip` (or `salvage/`) then `git rm` tracked files if owner approved; record zip path in CLOSEOUT.
- **Artifacts:** trim obvious regenerate-able outputs if policy allows; keep pilot/governance evidence paths referenced in ACTIVE_WORKSTREAMS or recent PRs.

PHASE 4 — Git hygiene
- Run push-guard + preflight before push; branch from `origin/main` as `agent/repo-cleanup-<date>`.
- PR description: bullet list of categories removed, file counts, zip locations, risks “none” or documented.

CONFLICT CHECK
Read `ACTIVE_WORKSTREAMS.tsv`; do not delete paths in active `write_scope` rows. If overlap, STOP.

WRITE_SCOPE
artifacts/coordination/REPO_CLEANUP_CANDIDATES_*.tsv; approved paths only under tests/, scripts/, artifacts/, salvage/, docs/ (only if owner approved doc removal); archive zips under artifacts/archive/ or salvage/

OUT_OF_SCOPE
Rewriting product logic; merging unrelated PRs; deleting submodules without owner; touching Pearl News / video flux lanes unless listed as candidates.

STOP / HANDOFF
If uncertain whether something is canonical, mark **ask_owner** — do not delete.

STARTUP_RECEIPT
STARTUP_RECEIPT
AGENT:
TASK:
PROJECT_ID:
SUBSYSTEM:
AUTHORITY_DOCS:
READ_PATH_COMPLETE:
WRITE_SCOPE:
OUT_OF_SCOPE:
BLOCKERS:
READY_STATUS:
```

---

**User**

look at pearl prime teacher mode teachers. each one should be used in manga pipeline. they are to have unique manga qualities. each teacher will be 1 manga brands with 6-18 titles (accordidng to the existing plans).  verify. if not there, write a prompt to do it.

---

**Cursor**

Tracing teacher registries and manga pipeline configuration to verify coverage and title counts.



## Verification (repo-grounded)

### Teacher roster vs manga brand plan

| Source | Count | Notes |
|--------|------:|------|
| `config/teachers/teacher_registry.yaml` | **13** teachers | Includes `adi_da` through `master_sha`. |
| `config/manga/manga_brand_series_plan.yaml` | **12** `brands:` blocks | Each block has exactly one `teacher:` key. |
| `config/catalog_planning/teacher_brand_lane_assignments.yaml` | **12** teacher brands | Same 12 teachers; **no `adi_da`**. |

**Manga brand ↔ teacher (all 12 aligned, 1:1):**

`stillness_press`→ahjan, `cognitive_clarity`→joshin, `somatic_wisdom`→pamela_fellows, `qi_foundation`→master_feung, `digital_ground`→miki, `heart_balance`→maat, `relational_calm`→junko, `warrior_calm`→master_wu, `sleep_restoration`→master_sha, `body_memory`→omote, `solar_return`→ra, `devotion_path`→sai_ma.

**Gap vs “every teacher mode teacher in manga”:** **`adi_da`** is in **teacher mode** (`teacher_registry.yaml`) and in **`config/manga/teacher_character_prompts.yaml`** (distinct `dark_psychological` manga prompt block), but **not** in **`manga_brand_series_plan.yaml`** or the **12 teacher-brand** lists in **`teacher_brand_lane_assignments.yaml`**. So today the **catalog/manga grid is explicitly 12 teachers**; **Adi Da is the odd one out** unless you treat him as teacher-only.

### Unique manga qualities

- **`teacher_character_prompts.yaml`**: **13** teacher keys, each with its own `style_archetype`, `positive` / `negative`, and img2img params — **visually differentiated**.
- **`manga_brand_series_plan.yaml`**: each brand has a **different `genre`** (iyashikei, seinen, shojo, cultivation, manhwa, isekai, shonen, etc.) — **portfolio differentiated**.

### “6–18 titles per brand”

There is **no** field in `manga_brand_series_plan.yaml` (or the snippets above) that states **6–18 titles** per brand. What **is** there are **operating knobs** such as `active_series_target` (about **2–4** concurrent series per brand), `new_series_per_year` (**3–5** for most brands), chapter cadence, etc. So **6–18** is **not verified** as an encoded plan; it might be an informal multi-year portfolio expectation — **would need an explicit manifest or doc** if you want that as a contract.

### ID consistency risk

- Registry / brand plan use **`sai_ma`**.
- `teacher_character_prompts.yaml` and `config/tts/manga_character_voice_bank.yaml` use **`sai_maa`** for the same person.  
Any script that keys only on `sai_ma` may **miss** prompts/voice unless aliased.

---

## Verdict

- **12/13** registry teachers are **fully wired** as **one manga brand each** with **distinct genre + prompts**.
- **1/13 (`adi_da`)** is **not** on the manga **brand/series plan** or lane matrix (only prompts exist).
- **6–18 titles** is **not** represented as a concrete per-brand title count in the checked configs.
- **`sai_ma` / `sai_maa`** should be **normalized** for pipeline safety.

---

## Prompt (only if you want to close the gaps)

Use this in a **new agent chat** if you decide **all 13** must have a manga brand **and/or** you want **6–18** encoded **and/or** **ID fix**:

```
You are Pearl_Dev + Pearl_Architect + Pearl_PM. Obey docs/SESSION_UNITY_PROTOCOL.md (STARTUP_RECEIPT / CLOSEOUT_RECEIPT). Read specs/AI_MANGA_PIPELINE_SUMMARY.md, docs/MANGA_IMPLEMENTATION_OUTLINE.md, config/teachers/teacher_registry.yaml, config/manga/manga_brand_series_plan.yaml, config/catalog_planning/teacher_brand_lane_assignments.yaml, config/manga/teacher_character_prompts.yaml, config/manga/gate_registry.yaml (if present).

TASK — Manga pipeline parity for Pearl Prime teacher mode

1) Reconcile roster counts
   - teacher_registry.yaml lists 13 teachers; manga_brand_series_plan + teacher_brand_lane_assignments list 12 teacher brands.
   - Decide with owner: either (A) add a 13th manga brand + lane row for `adi_da` with unique genre/topic_allocation consistent with doctrine_profile, OR (B) document in specs that `adi_da` is intentionally excluded from manga (teacher-mode-only) and remove or quarantine `adi_da` from teacher_character_prompts if excluded.

2) Normalize teacher_id for Sai Maa
   - Single canonical id: `sai_ma` (match registry) everywhere, OR alias map in one loader — update teacher_character_prompts.yaml key, manga_character_voice_bank.yaml key, and any scripts/tests so `sai_ma` and `sai_maa` cannot diverge.

3) Optional — encode “6–18 titles” if product requires it
   - Add per-brand fields (e.g. target_catalog_series_min/max or annual_series_bounds) to manga_brand_series_plan.yaml OR a companion TSV under artifacts/coordination/, derived from existing active_series_target + new_series_per_year; document formula in docs/MANGA_IMPLEMENTATION_OUTLINE.md.

4) Uniqueness check
   - Assert in tests or CI script: every teacher in teacher_registry who is manga-eligible appears exactly once in manga_brand_series_plan; each brand has distinct genre + teacher_character_prompts block; no duplicate teacher across brands.

5) Do not break “1 teacher per brand” rule in teacher_brand_lane_assignments.yaml.

WRITE_SCOPE: config/manga/*, config/catalog_planning/teacher_brand_lane_assignments.yaml (if 13th brand), config/teachers/* only if ids change, tests/, optional docs/specs if authority requires.
OUT_OF_SCOPE: unrelated video/flux; Pearl News.

CLOSEOUT: table teacher → brand → genre → prompt archetype; note owner decision on adi_da; PR link if applicable.
```

If your **intentional** design is **12 manga teachers only**, you can skip the prompt and instead add a **one-line authority note** that **`adi_da` is out of manga scope** so future audits do not file this as a bug.

---

**User**

adi da is ok for manga taiwan catalog only.
give prompt for all this stuff

---

**Cursor**

Here’s a **single paste-ready prompt** that covers **Taiwan-only Adi Da manga**, **Sai Maa id cleanup**, **optional 6–18 title encoding**, and **parity checks**. It matches your lane file pattern (`taiwan:` / `_tw` suffixes).

```
You are Pearl_Dev + Pearl_Architect + Pearl_PM. Obey docs/SESSION_UNITY_PROTOCOL.md (STARTUP_RECEIPT / CLOSEOUT_RECEIPT).

OWNER DECISION (verbatim)
adi da is ok for manga taiwan catalog only.

TASK — Manga / catalog parity for Pearl Prime teacher mode (full package)

A) Taiwan-only Adi Da manga brand
- `adi_da` is in `config/teachers/teacher_registry.yaml` but absent from the 12 global teacher brands in `config/manga/manga_brand_series_plan.yaml` and from the per-lane teacher lists in `config/catalog_planning/teacher_brand_lane_assignments.yaml`.
- Add **one** new teacher-mode brand **only under lane `taiwan:`** (zh-TW), with a unique base name + `_tw` suffix consistent with existing patterns (e.g. `bright_presence_tw` or owner-chosen slug — must not collide with existing `stillness_press_tw` … `devotion_path_tw`).
- Map `{ teacher: adi_da, content: [audiobooks, manga, video, exercises, freebies] }` (or subset owner approves) for **that brand only** on **taiwan**.
- Do **not** add `adi_da` to other lanes (english_global, japan, korea, china, etc.) unless owner explicitly expands scope later.
- Add a **`manga_brand_series_plan.yaml` brand block** for this Taiwan Adi Da line: `primary_lane: taiwan` (or document equivalent), `teacher: adi_da`, **unique `genre`** and `topic_allocation` vs the other 12 brands (reuse `teacher_character_prompts.yaml` for `adi_da` as visual baseline; align prose notes with `dark_psychological` / doctrine).
- Update `teacher_brand_lane_assignments.yaml` **summary** section to state the exception: **Taiwan lane = 13 teacher-mode brands**; all other lanes remain **12**. Fix any arithmetic (`total_brand_instances`, teacher_reach strings) that becomes wrong if summary claims 12×12 everywhere.

B) Canonical teacher id — Sai Maa
- Registry and `manga_brand_series_plan` use `sai_ma`; `config/manga/teacher_character_prompts.yaml` and `config/tts/manga_character_voice_bank.yaml` use `sai_maa`.
- Pick **one** canonical id (`sai_ma` recommended). Migrate YAML keys and any Python that references `sai_maa`; add a **temporary alias** in one loader if needed for backward compatibility, then remove alias once tests pass.

C) Optional — encode “6–18 titles” per brand (if product still wants it)
- `manga_brand_series_plan.yaml` today uses `active_series_target` / `new_series_per_year`, not literal 6–18.
- Either add explicit `target_series_catalog_min` / `target_series_catalog_max` (6–18 or per-brand ranges) **or** document the derived formula in `docs/MANGA_IMPLEMENTATION_OUTLINE.md` and add a small validation script under `scripts/` that asserts each brand’s planned throughput falls in owner-approved bounds.

D) Invariants & tests
- **1 teacher per brand** everywhere (existing rule).
- **No teacher appears twice** on the same lane under teacher-mode brands.
- **Taiwan:** exactly **one** brand row for `adi_da` after change.
- Add or extend tests (e.g. under `tests/`) that load YAML and assert:
  - union of `teacher:` keys in `manga_brand_series_plan.brands` matches intended set (12 global + 1 Taiwan-only OR 13 entries with clear schema);
  - every `teacher_registry` teacher either has a global manga brand **or** is explicitly allowed as Taiwan-only (`adi_da`) per a small allowlist in test;
  - `teacher_character_prompts.yaml` keys match registry ids after `sai_ma` fix.

E) Authority reads
specs/AI_MANGA_PIPELINE_SUMMARY.md; docs/MANGA_IMPLEMENTATION_OUTLINE.md; docs/MANGA_SERIES_PORTFOLIO_RESEARCH.md (portfolio context); config/manga/gate_registry.yaml if present; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv (conflict scan — avoid ws_teacher_manga_triptych collision on unrelated paths).

WRITE_SCOPE
config/manga/manga_brand_series_plan.yaml; config/manga/teacher_character_prompts.yaml (key rename + any prompt tweaks); config/catalog_planning/teacher_brand_lane_assignments.yaml; config/tts/manga_character_voice_bank.yaml; phoenix_v4/** or scripts/** only if loaders need alias; tests/**; optional docs/MANGA_IMPLEMENTATION_OUTLINE.md for the 6–18 encoding.

OUT_OF_SCOPE
Adding Adi Da to non-Taiwan lanes; Pearl News; video flux washout; narrator_voice_assignments wholesale edits.

CLOSEOUT
- Table: teacher_id → brand_slug(s) → lane(s) → manga genre → prompt style_archetype.
- Note: “Adi Da manga = Taiwan catalog only.”
- PR link; merge SHA; pytest subset results.

STARTUP_RECEIPT
STARTUP_RECEIPT
AGENT:
TASK:
PROJECT_ID: proj_state_convergence_20260328
SUBSYSTEM: manga_pipeline; core_pipeline (catalog)
AUTHORITY_DOCS:
READ_PATH_COMPLETE:
WRITE_SCOPE:
OUT_OF_SCOPE:
BLOCKERS:
READY_STATUS:
```

---

**User**

what to do? ;STARTUP_RECEIPT
AGENT: Pearl_GitHub + Pearl_Dev + Pearl_PM (repo coordination)
TASK: Phase 0 repo cleanup inventory + Phase 1 owner review gate (no bulk deletes)
PROJECT_ID: proj_state_convergence_20260328
SUBSYSTEM: repo coordination (Pearl_GitHub primary)
AUTHORITY_DOCS: docs/SESSION_UNITY_PROTOCOL.md; docs/GITHUB_GOVERNANCE.md (required checks / merge rules); docs/GITHUB_OPERATIONS_FRAMEWORK.md (repo identity / workflow map); docs/OWNERSHIP_MATRIX.md; docs/DOCS_INDEX.md (navigation + repo hygiene pointer); artifacts/coordination/ACTIVE_WORKSTREAMS.tsv; artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv; CLAUDE.md (via ps.txt mass-deletion gate)
READ_PATH_COMPLETE: yes — session minimum set read (SESSION_UNITY_PROTOCOL, ACTIVE_WORKSTREAMS, SUBSYSTEM_AUTHORITY_MAP sample, DOCS_INDEX lead, OWNERSHIP_MATRIX, GITHUB_GOVERNANCE / GITHUB_OPERATIONS_FRAMEWORK headers); deep line-by-line of every governance doc not repeated here
WRITE_SCOPE: artifacts/coordination/REPO_CLEANUP_CANDIDATES_2026.tsv only this session
OUT_OF_SCOPE: product logic; config/**, phoenix_v4/**, scripts/ci/**, .github/workflows/** except coordination notes; Pearl News / video lanes except as listed; any git rm / zip / rm -rf without owner category approval
BLOCKERS: none for inventory; git status on this workspace can be very slow (large tree) — inventory used git ls-files, du, and targeted scans
READY_STATUS: ready — Phase 0 artifact written; Phase 1 awaits your approvals

Conflict check (ACTIVE_WORKSTREAMS.tsv)
No candidate path is slated for delete inside an active write_scope row. Coordination only: brand-wizard-app/node_modules/ touches the same app tree as ws_teacher_manga_triptych_20260410 (active) and ws_lfs_setup_20260410 (active; .gitignore / LFS hygiene). Any untrack/remove of node_modules must be explicitly approved and planned with those lanes.

Phase 0 — Inventory artifact
Machine-readable list (14 rows + header):

artifacts/coordination/REPO_CLEANUP_CANDIDATES_2026.tsv

Evidence highlights:

Tracked test_*.py outside tests/: exactly 4 files (git ls-files), matching a full-repo find excluding .git, .claude, _wt_*, venvs → 4 paths.
_test.py “orphans”: the only tracked *_test.py outside tests/ are scripts/ci/run_rigorous_system_test.py and scripts/systems_test/run_systems_test.py — classified keep (harnesses, not pytest orphans).
.claude/worktrees: ~43 subdirs, du ~33G; _wt_beatmap / _wt_inj: ~1.2G each (local snapshots).
brand-wizard-app/node_modules/: 6984 tracked files (git ls-files | wc -l) — any git removal is >50 files → hard stop until you explicitly approve (CLAUDE.md / governance).
Phase 1 — Counts by category
category	rows	notes
artifact_junk
4
includes tracked node_modules (needs explicit OK)
cache
3
.pytest_cache, Vite deps path, __pycache__ pattern
decommissioned
2
old_chat_specs/, old_chats/ — docs still reference old_chat_specs
duplicate_test
4
alternate test roots only; canonical tests/ untouched
uncertain
2
both keep
Full table (all rows ≤30)
path	category	suggested_action	tracked_untracked
.claude/worktrees/
artifact_junk
ask_owner
untracked
.claude/worktrees/magical-beaver/brand-wizard-app/.vite/deps/
cache
delete
untracked
_wt_beatmap/
artifact_junk
zip_archive
untracked
_wt_inj/
artifact_junk
zip_archive
untracked
.pytest_cache/
cache
delete
untracked
__pycache__/** (repo main tree)
cache
delete
mixed
old_chat_specs/
decommissioned
ask_owner
tracked
old_chats/
decommissioned
ask_owner
tracked
pearl_prime/tests/test_modular_format_freeze.py
duplicate_test
ask_owner
tracked
test_pearl_news/test_*.py (3 files)
duplicate_test
ask_owner
tracked
scripts/ci/run_rigorous_system_test.py
uncertain
keep
tracked
scripts/systems_test/run_systems_test.py
uncertain
keep
tracked
brand-wizard-app/node_modules/
artifact_junk
ask_owner
tracked
What I did not do (by design)
No rm, git rm, git clean, zips, or commits.
No changes to tests/ discovery or CI wiring.
What I need from you (Phase 1 approvals)
Reply with explicit lines such as:

approve category cache — I will only remove untracked root .pytest_cache/ and nested .vite/deps after you confirm worktrees are disposable (or narrow paths).
approve category artifact_junk — specify: (A) .claude/worktrees/ only, (B) _wt_* only, (C) node_modules untrack strategy (separate approval; >50 files).
approve category decommissioned — only if you accept triage/archival plan for old_chat_specs/ / old_chats/ (with doc audit for old_chat_specs).
approve category duplicate_test — only after you want migration/consolidation into tests/ (separate proof PR).
Path exceptions — list any row to force keep.

CLOSEOUT_RECEIPT
AGENT: Pearl_GitHub + Pearl_Dev + Pearl_PM
TASK: Repo cleanup Phase 0 inventory + Phase 1 review package
COMMIT_SHA: no commits
FILES_WRITTEN: artifacts/coordination/REPO_CLEANUP_CANDIDATES_2026.tsv
FILES_READ: docs/SESSION_UNITY_PROTOCOL.md; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv; artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv; docs/DOCS_INDEX.md (lead); docs/OWNERSHIP_MATRIX.md; docs/GITHUB_GOVERNANCE.md; docs/GITHUB_OPERATIONS_FRAMEWORK.md; ps.txt / CLAUDE.md (via workspace rules); docs/REPO_HYGIENE_AND_WORKTREE_CLEANUP.md
STATUS: partial — awaiting owner category/path approvals before Phase 2–4
HANDOFF_TO: owner
NEXT_ACTION: Reply with approve category X and path exceptions; then I will execute Phase 2 (low-risk untracked cache only as approved), branch agent/repo-cleanup-20260414 from origin/main if we promote changes to git, and run push-guard + preflight before any push.

How much space did you save me on my laptop local disk?

None. That session only produced the inventory file artifacts/coordination/REPO_CLEANUP_CANDIDATES_2026.tsv and did not delete, archive, or git rm anything. A small amount of disk was used for that tiny file (and whatever Cursor/git touched), not freed.

Potential space if you later remove what we measured (for your planning only, not done by me):

.claude/worktrees/ — about 33 GB (du ~33G)
_wt_beatmap/ + _wt_inj/ — about 1.2 GB each (~2.4 GB total)
.pytest_cache/ and nested .vite/deps — small unless huge caches
Nothing was reclaimed until you approve categories and run the actual cleanup.



---

**Cursor**

## What to do now

You are at **Phase 1: owner gate**. Phase 0 only added `artifacts/coordination/REPO_CLEANUP_CANDIDATES_2026.tsv` — **no disk was freed**.

### 1. Reply to the executor (copy-paste style)

Send **explicit approvals** and **exceptions**. Example patterns (edit to match what you want):

**Low risk (typical first move)**  
`approve category cache — delete untracked .pytest_cache/ at repo root and untracked .claude/worktrees/magical-beaver/brand-wizard-app/.vite/deps/ only. Do not touch anything under .claude/worktrees/ except that single .vite path unless I say so.`

**Worktrees (big win, but you must mean it)**  
`approve category artifact_junk — (A) delete entire .claude/worktrees/ (~33G) on this machine only; OR zip then delete. Do not touch _wt_beatmap or _wt_inj in this pass.`  
*or*  
`approve category artifact_junk — (B) zip_archive _wt_beatmap/ and _wt_inj/ only; keep .claude/worktrees/ for now.`

**Tracked `node_modules` (high governance risk)**  
Do **not** approve blindly. If you really want it gone:  
`approve category artifact_junk — (C) brand-wizard-app/node_modules/: untrack via git rm + add to .gitignore; acknowledge >50 files and I accept; coordinate with ws_lfs_setup_20260410 / ws_teacher_manga_triptych_20260410.`  
If unsure: **defer** — `path exception: brand-wizard-app/node_modules/ — keep until LFS/CI decision.`

**Old chat trees**  
`approve category decommissioned — triage old_chat_specs/ and old_chats/: move to salvage/ or zip + git rm only after docs that reference old_chat_specs are updated or redirected.`  
Or: `path exception: old_chat_specs/, old_chats/ — keep for now.`

**Duplicate tests**  
Usually **not** Phase 2:  
`approve category duplicate_test — defer; open a follow-up PR to migrate pearl_prime/tests and test_pearl_news into tests/ with CI proof.`  
Or pick one path to migrate first.

**Force-keep**  
`path exceptions: pearl_prime/tests/test_modular_format_freeze.py — keep; test_pearl_news/* — keep until migration PR.`

### 2. Suggested order

1. **Cache** (untracked only) — minutes, low risk.  
2. **`.claude/worktrees/`** or **`_wt_*`** — large reclaim; confirm nothing unique lives only there.  
3. **`node_modules`** — separate decision with **LFS / triptych / CI** owners.  
4. **`old_chat_*`** — after doc audit.  
5. **Duplicate tests** — dedicated small PR.

### 3. Disk space (honest)

- **Saved so far:** **0** (inventory only).  
- **Recoverable if you later delete what was measured:** on the order of **~35+ GB** mostly from **`.claude/worktrees/` (~33 GB)** plus **`_wt_*` (~2.4 GB)**; caches are usually small unless bloated.

### 4. After you send approvals

Executor runs **Phase 2** (only what you approved), then **branch + commit** if anything is tracked, **push-guard + preflight** before push — per their `NEXT_ACTION`.

---

**Bottom line:** Reply with **`approve category …`** lines and **`path exceptions:`** as needed; start with **cache** and **disposable worktrees** if you want real disk back without touching **6984 tracked `node_modules` files** until you have an explicit untrack/LFS plan.

---

**User**

give me propmt to do low risk. i'm still working on brand wizard 

---

**Cursor**

```
You are Pearl_GitHub + Pearl_Dev. Obey docs/SESSION_UNITY_PROTOCOL.md (STARTUP_RECEIPT / CLOSEOUT_RECEIPT) and CLAUDE.md mass-delete rules.

OWNER TASK — Low-risk repo cleanup only (Brand Wizard in active use)

SCOPE (allowed)
- Delete **untracked** cache only:
  - Repo-root `.pytest_cache/` if present and untracked.
  - **Untracked** `__pycache__/` directories under `phoenix_v4/`, `scripts/`, `tests/`, and `config/` only (no recursion into venvs, `.git`, `node_modules`, or worktrees).
- **Do not** reclaim space from `.claude/worktrees/`, `_wt_*`, or **any path under `brand-wizard-app/`** (including `node_modules/`, `.vite/`, `dist/`, `.cache/`) — owner is actively developing Brand Wizard.

OUT OF SCOPE (hard stop)
- `brand-wizard-app/**` (entire tree — read-only for this session).
- `git rm`, tracked file removal, zip archives, `git clean -fdx`.
- `old_chat_specs/`, `old_chats/`, duplicate test migration, `node_modules` untrack.
- Anything requiring >50 tracked deletes.

VERIFICATION
- Before each delete: `git status --short <path>` must show **??** or path must not be in `git ls-files`.
- After: `du -sh` on removed dirs (optional); list what was removed in CLOSEOUT.

PROJECT_ID: proj_state_convergence_20260328
WRITE_SCOPE: none for git-tracked files; filesystem deletes only as above.
CONFLICT: Respect ws_teacher_manga_triptych_20260410 / ws_lfs_setup_20260410 — zero edits under `brand-wizard-app/`.

CLOSEOUT_RECEIPT: paths removed, approximate MB freed, confirm Brand Wizard tree untouched.

STARTUP_RECEIPT
STARTUP_RECEIPT
AGENT:
TASK:
PROJECT_ID:
SUBSYSTEM:
AUTHORITY_DOCS:
READ_PATH_COMPLETE:
WRITE_SCOPE:
OUT_OF_SCOPE:
BLOCKERS:
READY_STATUS:
```

---

**User**

Use pearl GitHub. and pearl_prez. Presentation agent. I want you to move the Ahjan Video. from repo on hard drive Cloudflare.And I want you to put that video on the teachers pages for brand admin html stuff. There's the teacher's page. for Ahjan and I want it inserted into that as his video example. Give me a prompt for that.
teacher_vid_package/ahjan.mp4

---

**Cursor**

Here’s a **single paste-ready prompt** for **Pearl_GitHub + Pearl_Prez** (with **Pearl_Dev** if Wrangler/R2 wiring needs a small server touch).

```
You are Pearl_GitHub + Pearl_Prez (Pearl_Dev only if R2 upload must go through an existing script or `wrangler` automation). Obey docs/SESSION_UNITY_PROTOCOL.md (STARTUP_RECEIPT / CLOSEOUT_RECEIPT), docs/INTEGRATION_CREDENTIALS_REGISTRY.md (Cloudflare / R2 — no invented URLs), BRAND_ADMIN_CANONICAL_PACKAGE.md, docs/OLD_CHAT_AND_HOME_PROMOTION_SPEC.md, artifacts/coordination/ACTIVE_WORKSTREAMS.tsv (avoid colliding with ws_teacher_manga_triptych_20260410 on unrelated assets).

OWNER TASK
1) Take the Ahjan teacher video from disk: `teacher_vid_package/ahjan.mp4` (resolve to absolute path — e.g. `~/Desktop/teacher_vid_package/ahjan.mp4` on the owner laptop — confirm file exists with `ffprobe`).
2) Upload it to **Cloudflare** for stable public or signed delivery (prefer **R2** + public bucket path or Workers route already used by Phoenix; follow repo/env patterns — read `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` and any existing R2/podcast upload notes). Do **not** commit multi‑MB MP4 into git unless owner explicitly overrides LFS policy.
3) Insert that hosted video as **Ahjan’s official “video example”** on the **brand-admin / teacher HTML** surface:
   - **Primary:** `brand-wizard-app/public/teacher_showcase.html` — inside `<section id="ahjan">`, add a clear block (e.g. new collapsible “Video — example reel” or a `format-card` with `<video controls playsinline>` pointing at the **HTTPS URL** on Cloudflare). Match existing layout tokens (`.teacher-section`, `.formats-grid`, caption style). Use **9:16** friendly sizing (`max-width`, `aspect-ratio: 9/16`, rounded corners) consistent with TikTok-style examples.
   - **If mirrored elsewhere:** update any other canonical teacher HTML called out in `BRAND_ADMIN_CANONICAL_PACKAGE.md` (e.g. onboarding hub) **only** if the same Ahjan block exists there — do not duplicate unless spec requires.

4) Naming / cache: use a stable object key such as `brand-admin/teachers/ahjan/example_reel_v1.mp4` (or team convention). Document final URL in CLOSEOUT.

5) **Do not** break `teacher_select.html` unless owner wants the same URL in the JSON `covers` array for Ahjan — optional second commit.

VERIFICATION
- Open local `teacher_showcase.html` in browser (or static server): video plays from Cloudflare URL; no mixed-content warnings; mobile width OK.
- `grep -n ahjan teacher_showcase.html` shows exactly one canonical video URL pattern (no dead `file://` links).

WRITE_SCOPE
`brand-wizard-app/public/teacher_showcase.html` (+ optional other files listed in BRAND_ADMIN package); `wrangler.toml` / small deploy doc **only** if repo already uses them and change is required; **no** unrelated teacher sections.

OUT_OF_SCOPE
Re-encoding video unless required for platform limits; changing Flux/manga pipelines; Pearl News.

GIT
Branch `agent/brand-admin-ahjan-video-cloudflare` from `origin/main`; run push-guard + preflight before push; PR with before/after screenshot description and the public URL (no secrets in PR body).

CLOSEOUT_RECEIPT
- Cloudflare object path + public HTTPS URL
- HTML file(s) touched + line region summary
- ffprobe duration/resolution
- COMMIT_SHA / PR link

STARTUP_RECEIPT
STARTUP_RECEIPT
AGENT:
TASK:
PROJECT_ID: proj_state_convergence_20260328
SUBSYSTEM: brand_admin; integrations
AUTHORITY_DOCS:
READ_PATH_COMPLETE:
WRITE_SCOPE:
OUT_OF_SCOPE:
BLOCKERS:
READY_STATUS:
```

**Note:** Repo teacher id is **`ahjan`** (not “Ajahn” in filenames). If your file is literally `ahjan.mp4`, keep that spelling for URLs and HTML `id="ahjan"` consistency.

---

**User**

prompt for: 




pearl_prime_ahjan_genz_anxiety_all_runtimes.txt
Document
Analyze this book. It has all of the formats that have that Pearl Prime has to output. I want you to analyze it and assess it for cohesive flow, for a great read, for a bestseller, for therapeutic value. So is it a great book?

I’m reading the full uploaded book file rather than judging from the clipped preview, so I can assess the actual runtime outputs and not just the first chunks.
The file search connector is not exposing the upload, so I’m switching to the raw file directly and assessing the text from the upload itself.
Thought for 11s
Yes — I can assess it, and based on what is visible in the uploaded bundle, it is not yet a great book. It has real strengths, especially in premise, audience targeting, somatic relevance, and some sharp lines, but as a finished reading experience it is too unstable, repetitive, and structurally broken to count as a strong therapeutic bestseller right now. I’m basing that on the uploaded Pearl Prime runtime bundle .
Overall verdict
My honest read:
Concept quality: strong
Therapeutic intent: strong
Occasional line-level power: real
Book-level cohesion: weak to inconsistent
Bestseller readiness: not yet
“Great book?”: No, not in its current output state

It reads more like a partially successful generation system showing flashes of a good book than a book that has already fully become one.

My scorecard
Across the bundle overall
Cohesive flow: 4/10
Great read / readability: 5/10
Bestseller potential: 4.5/10
Therapeutic value: 6.5/10
Current overall quality as a book: 4.8/10
Why therapeutic value scores higher than book quality
Because the system does contain:
body-based noticing
non-shaming language
nervous-system framing
accessible micro-practices
a relevant Gen Z / young professional anxiety frame
Those are genuinely useful. But usefulness alone does not make it a great book.
What is working
There is real value here.
1. The core topic-persona match is strong
The work anxiety / overwhelm / Gen Z professional angle is good. Lines like:
“Your body knows something your calendar doesn't.”
“Sunday used to be a day. Now it is the hours before Monday starts.”
“You are not behind. You are always almost caught up.”
Those are sharp, contemporary, and emotionally legible. They feel targeted to the audience rather than generic wellness prose .
2. The best somatic lines are strong
The strongest parts keep returning to the body:
jaw tension
shallow breath
shoulders near ears
attention snapping back to the body
emotions as movement, not identity
That is where the manuscript has the most therapeutic credibility .
3. The book sometimes lands a clean, useful insight
For example, this kind of line works:
“You are not broken — you are responding.” 
That is therapeutically sound, emotionally reassuring, and simple enough to remember.
4. Some title/chapter framing is good
Titles like:
The Alarm That Won’t Stop Ringing
What The Alarm Actually Does To Your Body
When Your Body Learns It’s Safe
These are clear, marketable, and emotionally coherent for an anxiety book .
What is failing badly
This is where it stops being a great read.
1. The flow is broken
The biggest problem is not the ideas. It is the assembly.
The text repeatedly jumps between:

spiritual framing
office scene fragments
journaling prompts
list-like symptom bursts
clinical explanation
story inserts
repeated somatic reframes
But it often does so without proper transitions. That creates a “stitched together” feel instead of a guided reading experience.
Example pattern:

spiritual opening
abrupt office sensory scene
exercise prompt
Buddhist teaching
fragmented symptom list
explanation
another sensory block
repeated symptom list
mini-summary
That is not chapter composition. That is content accumulation.
2. Repetition is severe
Certain lines and blocks recur so often that they stop feeling intentional and start feeling machine-produced.
Repeated examples visible in the bundle include:

“The task is open…”
“soft daylight along the sill…”
“the street below…”
the long symptom-chain beginning “You did everything they said to do…”
repeated teachings and prompts across chapters and runtimes 
This repetition damages:
momentum
reader trust
narrative freshness
emotional escalation
A therapeutic book can repeat themes. But this bundle often repeats wording, scene furniture, and sentence skeletons too literally.
3. Raw generation artifacts are still leaking through
This is one of the clearest signs it is not publish-ready.
Visible issues in the uploaded file include:

## HOOK v14
stray ##
abrupt cutoffs
malformed prose
duplicated words like “The the train…”
incomplete fragments
tone-breaking insertions like “In this discourse, we propose…” that sound imported from a different register entirely 
That alone disqualifies it from “great book” status.
4. The reading experience does not build cleanly
A bestseller-quality nonfiction/self-help book usually builds through:
escalating clarity
trust in the guide
progressive deepening
chapter-level purpose
relief through structure
This bundle often feels like it is circling the same emotional territory instead of advancing the reader through it.
You get recognition, but not enough progression.

5. The voice is inconsistent
At its best, the voice is:
grounded
body-aware
direct
compassionate
At its weakest, it becomes:
generic spiritual exposition
template prose
pseudo-clinical insert
raw prompt residue
lecture-like abstraction
A great therapeutic bestseller needs a voice that feels authored. This still feels assembled.
Format-by-format assessment
From the visible bundle sections:
micro_book_15
Score: 4/10
This is too compressed for the amount of material being forced into it. It reads like dense fragments jammed together. The strongest lines hit, but flow breaks constantly. Good as a diagnostic artifact, not a satisfying book .

micro_book_20
Score: 3.5/10
Worse in some ways because it still has the same repetition and leakage, plus visible artifact problems like ## HOOK v14. It feels less like a book and more like exposed pipeline output .

short_book_30
Score: 5.5/10
This is the first format that starts to show the possibility of a real book. It has enough room for:

chapter setup
some story
body-based insight
repeated pattern recognition
But it is still dragged down by duplication, assembly seams, imported mismatched material, and weak transitions. This is the best of the visible formats, but still not great .
Longer runtimes not fully visible in the preview
I cannot responsibly score the unseen later runtimes as precisely from the clipped display alone. But based on the pattern in the visible formats, my expectation is:
longer runtimes may improve depth
but unless composition is fixed, they will also amplify repetition and structural drag
So the likely failure mode is: more words, same assembly problem.
Is it therapeutic?
Yes, partially
There is real therapeutic usefulness here.
It does several things right:

normalizes anxiety without shaming
reframes symptoms as body signals
encourages observation before reaction
gives manageable practices
keeps most advice simple and non-grandiose
That matters.
But it is not fully safe or fully excellent therapeutic writing yet
Why:
repetition can dysregulate or numb the reader
abrupt structural shifts interrupt containment
the book does not always hold the reader through a coherent emotional arc
some spiritual claims arrive before enough trust and grounding are established
it can feel more like content modules than a held therapeutic journey
A strong therapeutic book does not just contain useful ideas. It creates a regulated reading experience. This bundle does not consistently do that yet.
Is it a bestseller?
Not as it stands
A bestseller in this category usually needs at least four things:
a sharp promise
a trustworthy, distinct voice
sustained readability
memorable chapter progression
This bundle has only parts of #1 and #2.
It does have marketable ingredients:

anxiety
nervous system
work overwhelm
body awareness
Gen Z relevance
practical exercises
spiritual undertone
That is commercially promising.
But the current manuscript quality would not create strong:

word of mouth
completion rate
quote sharing
emotional loyalty
reviews saying “I couldn’t put it down”
Right now, the likely reaction is:
“There are good lines in here, but it feels repetitive and oddly assembled.”
That is not bestseller response.

The clearest diagnosis in one sentence
This is a promising anxiety book system with real therapeutic intelligence, but the current output still reads like composited fragments instead of a finished, cohesive, emotionally guided book .
What it would need to become a great book
It needs improvement in this order:
1. Composition, not just enrichment
The chapters need to be actually written through, not just stacked from parts.
2. Hard deduplication
Not thematic dedupe. Literal phrase-, image-, and scene-level dedupe.
3. Transition logic
Every move between:
scene
teaching
story
exercise
reflection
needs a bridge.
4. Chapter progression
Each chapter should answer a distinct question and move the reader somewhere new.
5. Voice locking
The manuscript needs one coherent authorial consciousness.
6. Artifact cleanup
Any raw template leaks, labels, malformed imports, or partial fragments must be zero.
Bottom line
Is it a great book?
No. Not yet.
Is there the basis of a great book in it?
Yes. Definitely.

The underlying material has enough intelligence and relevance that with proper composition and cleanup, it could become a strong therapeutic anxiety book. But the current output is still system-output quality, not finished-book quality.

If you want, I can do the next step and give you a brutally specific rubric by runtime format with:

pass/fail for cohesive flow
pass/fail for therapeutic containment
pass/fail for bestseller readability
exact root-cause issues the system must fix first


* pass/fail for cohesive flow * pass/fail for therapeutic containment * pass/fail for bestseller readability * exact root-cause issues the system must fix first Sources
y

Here’s the brutal rubric pass.
Pearl Prime anxiety bundle — runtime verdicts
micro_book_15
Cohesive flow: FAIL
Therapeutic containment: PARTIAL FAIL
Bestseller readability: FAIL
Why

Too many content modes are packed into too little space: teaching, sensory scene, exercise, symptom list, Buddhist frame, summary.
Repetition shows up immediately, so the book feels assembled instead of guided.
It contains useful body-based reframes, but the reader is not held through a stable emotional arc.
It reads more like a compressed output artifact than a book someone would recommend to a friend.
Main root causes
No real chapter composition layer
Reused symptom blocks and sensory blocks
No transition glue between modules
Runtime too short for current component density
micro_book_20
Cohesive flow: FAIL
Therapeutic containment: FAIL
Bestseller readability: FAIL
Why

It has all the problems of micro_book_15, plus more visible pipeline leakage.
Raw artifacts like ## HOOK v14 and ## break trust instantly.
Once the reader sees template residue, the authorial spell is gone.
A therapeutic book cannot feel unstable at the assembly level. 
Main root causes
Artifact cleanup is not hard-gated
Slot residue is passing into prose
The system is exposing internal labels to the reader
Composition still feels like concatenation, not authored progression
short_book_30
Cohesive flow: PARTIAL FAIL
Therapeutic containment: PARTIAL PASS
Bestseller readability: PARTIAL FAIL
Why

This is the first runtime that has enough room to feel like a possible book.
Some chapters begin to breathe, and some story/insight/exercise balance becomes possible.
But the same repeated scene furniture, symptom chains, and imported text fragments keep destabilizing the read.
Therapeutically, it is better because it has enough length to offer recognition plus a little integration.
Still not strong enough to feel publish-grade. 
Main root causes
Long-form runtime is amplifying repeated modules rather than deepening them
Scene bank is too narrow and too visibly reused
Chapter intent is still fuzzy
Imported voice registers are inconsistent
Category rubric
1. Cohesive flow
Current status: FAIL overall
A cohesive book needs:
clean chapter purpose
progression from one idea to the next
smooth movement between scene, insight, story, and exercise
controlled repetition
a feeling that someone is leading the reader somewhere
This bundle does not do that reliably.
Strongest evidence of failure
The same chapter often moves like this:
spiritual principle
office scene
journaling prompt
Buddhist teaching
symptom list
explanation
repeated office scene
mini-somatic closing
That is not a controlled reader journey. It is a stack of valid components with weak orchestration.
Cohesive flow score by bundle
micro_book_15: 4/10
micro_book_20: 3/10
short_book_30: 5.5/10
Overall: 4/10
2. Therapeutic containment
Current status: PARTIAL PASS at best
This is not the same as “contains good advice.”
Therapeutic containment means:

the reader feels seen without being flooded
the book offers regulation, not just recognition
the voice feels stable and trustworthy
exercises arrive in the right emotional order
the text creates a held experience
What works
non-shaming nervous-system language
body-location prompts
short practical exercises
lines like “you are not broken — you are responding” are excellent containment lines
What breaks containment
abrupt shifts in register
over-repetition of distress cues
assembly artifacts that break safety and trust
chapters that do not clearly deepen or resolve
some sections feel dropped in rather than emotionally introduced
A reader with anxiety needs a sense that the book itself is regulated. This one often is not.
Therapeutic containment score
micro_book_15: 5/10
micro_book_20: 4/10
short_book_30: 6.5/10
Overall: 5.5–6/10
3. Bestseller readability
Current status: FAIL overall
A bestseller in this lane usually has:
a strong voice
chapter-to-chapter pull
memorable lines
emotional momentum
low friction
high quote/share/recommend energy
This bundle has some memorable lines, but not sustained readability.
What helps
strong chapter titles
timely anxiety/work-burnout framing
Gen Z professional relevance
some very quotable somatic lines
What hurts badly
visible machine repetition
duplicate sensory scaffolding
cadence drag
prose that loops instead of escalates
imported mismatched passages like the “In this discourse…” meditation section, which sounds like it came from another source entirely 
That kills the “I need to keep reading” effect.
Bestseller readability score
micro_book_15: 4/10
micro_book_20: 3/10
short_book_30: 5/10
Overall: 4.5/10
Exact root-cause issues the system must fix first
This is the part that matters most.
Tier 1 — must fix immediately
1. Stop concatenating enriched slots as if that equals prose
This is the primary failure.
The bundle reads like:

module
module
module
repeated module
summary module
Instead of:
opening move
expansion
emotional turn
practice
integration
Until the system has a true composition layer, all runtimes will keep feeling stitched.
2. Add hard artifact rejection before output is accepted
Anything like:
## HOOK v14
##
malformed fragment dumps
duplicated words like The the train
abrupt residue from internal structures
should be automatic fail, not publishable output. 
3. Deduplicate repeated scene furniture and symptom blocks
The repeated units are too obvious:
“soft daylight along the sill”
“the street below”
“The task is open…”
the long work-anxiety symptom chain
The issue is not repetition of theme. It is repetition of verbatim building blocks.
4. Force every chapter to have one dominant function
Right now many chapters are trying to:
teach
soothe
scene-set
diagnose
journal
philosophize
summarize
all at once.
Each chapter needs one clear job.

Tier 2 — next fixes after the above
5. Build transition sentences between content modes
Every change from:
scene → teaching
teaching → exercise
exercise → story
story → integration
needs a bridge sentence that explains why the reader is moving there now.
Without this, even strong content feels random.

6. Lock a single voice register
Right now the voice shifts between:
grounded somatic coach
Buddhist teacher
generic self-help copy
raw imported transcript/prose
system residue
That inconsistency is one of the biggest reasons it does not feel like a real book.
7. Make progression cumulative, not cyclical
Too many chapters re-explain the same alarm-state truth.
The reader should feel:

I recognize myself
I understand the mechanism
I see the cost
I learn how to stay
I practice safety
I build a new identity
That progression is not yet sharp enough.
Tier 3 — quality upgrades that move it toward “great”
8. Improve story relevance and emotional landing
Marcus and Sarita are better than nothing, but they still feel inserted rather than dramatically necessary in places. Stories need to do real structural work, not just provide texture. 
9. Tighten chapter endings
The best therapeutic chapters land with:
relief
clarity
a small assignment
emotional integration
Some endings here feel clipped or generic.
10. Build a stronger signature promise
The book has good phrases, but it still needs one clear author-level promise, such as:
this is how work anxiety lives in the body
this is how you stop treating alarm as identity
this is how overwhelmed professionals return to internal safety
Right now the promise is present, but diffused.
Final verdict, bluntly
Is it a cohesive book?
No.
Is it therapeutically useful?
Yes, somewhat.
Is it a great read?
No.
Is it bestseller-ready?
No.
Is there a real book hiding inside the system?
Yes. Absolutely.
The strongest truth here is that the raw ingredients are good enough, but the assembly system is still producing artifacts instead of authored chapters. That is why it feels promising rather than great.

The first fix is not “better lines.”
The first fix is book composition logic.

I can turn this into a developer-ready fail rubric next, with exact gates like “reject if repeated scene furniture exceeds X,” “reject if internal slot labels appear,” and “reject if chapter contains more than one unresolved mode jump.”

y

Here is a developer-ready fail rubric you can hand directly to an agent. It is written to gate Pearl Prime output at the manuscript level, not just line quality.
Pearl Prime Book Quality Gate
Anxiety / Pearl Prime runtime assessment fail rubric
This rubric is based on the uploaded runtime bundle and is meant to catch the exact problems visible there: slot concatenation, repeated scene furniture, pipeline residue, weak transitions, unstable voice, and shallow chapter progression .
1. Release decision bands
A. Reject outright
Reject the manuscript immediately if any of the following are true:
Internal labels appear in reader-facing prose
Examples: ## HOOK, ## STORY, v14, dict/object residue, raw slot names
Broken assembly artifacts appear
Examples: duplicated words like The the train, clipped lines, malformed pasted source text
More than 2 obvious verbatim duplicate blocks appear across the manuscript
More than 1 chapter feels like stacked modules without transitions
A chapter contains 3 or more unresolved mode jumps
Voice register sharply shifts in a way a normal reader would notice
The manuscript reads like generated fragments rather than authored prose
B. Hold for revision
Hold if:
no raw artifacts appear
but repetition, transition weakness, or progression weakness still reduce reading quality
therapeutic value is present, but the book does not sustain momentum
C. Pass to editorial polish
Only pass if:
no artifact leakage
low visible repetition
each chapter has one clear job
transitions are smooth
therapeutic containment feels steady
the book reads as a single authored experience
2. Hard gates
These are binary. Fail any of them and the book is not publish-grade.
Gate 1 — Artifact leakage
Rule: Reader-facing prose must contain zero internal generation artifacts.
Fail if any of these appear:
##
slot/version labels
YAML/JSON/dict-looking structures
placeholder tokens
malformed imports
clipped module markers
half-rendered fragments
Why
This instantly breaks trust and destroys the sense that the book is authored. The uploaded bundle visibly fails this in micro_book_20 .
Gate 2 — Verbatim duplicate block gate
Rule: No repeated paragraph or sentence block longer than 25 words may appear more than once unless it is an intentionally marked refrain.
Fail if:
repeated symptom-chain blocks recur verbatim
repeated scene blocks recur verbatim
repeated teaching paragraphs recur verbatim
repeated somatic summary closers recur verbatim without narrative justification
Why
The uploaded bundle repeats lines like:
“The task is open...”
“soft daylight along the sill...”
“the street below...”
repeated anxiety symptom strings
This makes the manuscript feel compiled, not composed .
Gate 3 — Broken prose gate
Rule: Prose must be syntactically clean.
Fail if:
doubled words appear (The the train)
sentence fragments appear from truncation or bad merge
imported text changes register mid-paragraph without explanation
orphaned single words remain (Notice)
broken punctuation or partial inserts remain
Why
This is visible in the uploaded bundle and is a straight publish blocker .
Gate 4 — Chapter function gate
Rule: Each chapter must have one dominant job.
Allowed dominant jobs:

recognition
mechanism explanation
cost/consequence
story/identification
practice
reframe/integration
future identity / hope
Fail if a chapter tries to do too many at once without hierarchy:
scene
doctrine
journaling
symptom list
story
exercise
summary
all in one short chapter
Why
The current runtimes often feel like stacked valid units rather than one chapter delivering one controlled effect.
3. Cohesive flow rubric
Score each chapter 0–2 on each line item.
3.1 Opening coherence
2 = opening clearly establishes chapter purpose
1 = opening is decent but generic or disconnected
0 = opening feels pasted in or mismatched
3.2 Mode transitions
Modes include:
scene
explanation
teaching
exercise
story
integration
2 = transitions feel natural
1 = one awkward jump
0 = two or more abrupt mode jumps
Unresolved mode jump definition
A move from one mode to another with no bridge or rationale.
Example:
office sensory scene → Buddhist doctrine
symptom list → historical teaching
story → practice prompt
with no transitional sentence
3.3 Chapter progression
2 = chapter clearly advances beyond prior chapter
1 = partially advances but repeats known material
0 = feels like the same chapter again
3.4 Ending landing
2 = chapter lands with clarity, relief, or integration
1 = ending is fine but generic
0 = ending is clipped, abrupt, or redundant
Cohesive flow pass threshold
Per chapter minimum: 5/8
Book average minimum: 6/8
Auto-fail: any chapter scoring 2 or less total
4. Therapeutic value rubric
This is not “good advice.” This is whether the book creates a held, regulating experience.
4.1 Non-shaming accuracy
2 = symptoms are framed as understandable responses
1 = mostly sound, a little generic
0 = pathologizing, simplistic, or emotionally blunt
4.2 Somatic specificity
2 = names body sensations concretely
1 = some body language, but vague
0 = abstract self-help talk without embodied anchors
4.3 Practice usability
2 = reader can actually do the practice now
1 = partially usable, somewhat vague
0 = generic prompt with no containment or timing
4.4 Emotional containment
2 = text sees the reader and regulates the pace
1 = good ideas, but pacing is unstable
0 = emotionally scattered or too jarring
Therapeutic pass threshold
Per chapter minimum: 6/8
Book average minimum: 6.5/8
Auto-fail: any chapter with 0 in emotional containment
5. Bestseller readability rubric
This is about whether a reader would keep reading, recommend it, and quote it.
5.1 Voice distinctiveness
2 = sounds like one clear author
1 = mostly consistent, some drift
0 = visibly mixed voice or assembly tone
5.2 Momentum
2 = reader wants next chapter
1 = some drag
0 = repetitive or stagnant
5.3 Memorability
2 = multiple strong, quotable lines
1 = some nice lines
0 = mostly generic prose
5.4 Freshness
2 = low visible repetition
1 = some repeated wording/images
0 = obvious repeated blocks or scene furniture
Bestseller pass threshold
Per chapter minimum: 5/8
Book average minimum: 6/8
Auto-fail: book-level freshness score of 0
6. Repetition detection rules
These should be implemented as measurable gates.
6.1 Scene furniture repetition
Track repeated sensory scaffolding phrases such as:
window light
street below
desk / screen / train / office repeats
same office beat patterns
Fail if:
the same sensory phrase stem appears more than 3 times per 10k words
or one scene pattern appears in more than 2 chapters nearly unchanged
6.2 Symptom-list repetition
Track repeated symptom chains and stacked fragments.
Fail if:
any symptom list longer than 40 words reappears substantially unchanged
or more than 15% of book paragraphs are structurally repetitive symptom bullets disguised as prose
6.3 Refrain exception
A refrain is allowed only if:
it is intentional
marked by placement logic
limited to 2–3 recurrences
slightly evolved each time
The current bundle does not read as intentional refrain use. It reads as reuse.
7. Voice consistency rules
Pass if:
the book feels like one teacher guiding one reader
spiritual language, somatic language, and practical language are integrated naturally
Fail if:
one paragraph sounds like Buddhist teaching
next sounds like imported productivity copy
next sounds like a raw transcript
next sounds like a system dump
Specific fail marker
If a reasonably attentive reader would say, “This sounds like it was pasted from different sources,” fail voice consistency.
The uploaded bundle shows this problem, especially when it drops in text like “In this discourse, we propose...” beside otherwise contemporary somatic prose .

8. Chapter architecture rules
Each chapter must include only the pieces needed for its job.
Allowed chapter structures
Structure A — Recognition chapter
opening recognition
body-based scene
mechanism line
short reflective close
Structure B — Mechanism chapter
opening claim
relatable example
explanation
one concrete body-based practice
integration close
Structure C — Practice chapter
setup
why this practice matters
guided exercise
after-effect framing
Structure D — Story-led chapter
story opening
emotional or somatic relevance
extracted lesson
reader application
Fail if:
A chapter includes 5 or more different structural modes in under 800 words.
That is a strong signal of assembly stacking rather than composition.

9. Book-level progression gate
A good book must move.
Required 6-step progression
The full book should roughly travel through this sequence:
Recognition — I see myself in this
Mechanism — I understand what anxiety is doing
Cost — I see what constant alarm is taking from me
Practice — I learn what to do in real time
Safety — I experience moments of regulation
Possibility — I can imagine a different life
Fail if:
3 or more chapters are functionally interchangeable
later chapters repeat early chapter insight without deepening it
the final chapter does not feel earned
This is one of the biggest current failures in the uploaded runtime set.
10. Runtime-specific release policy
micro_book_15
Use only if:
chapter density is radically simplified
max 3 modes per chapter
hard dedupe enabled
no long repeated symptom chains
Otherwise reject by default.
micro_book_20
Currently reject by default until:
artifact leakage reaches zero
slot residue is impossible
chapter mode count is reduced
short_book_30
Can be considered salvageable if:
all hard gates pass
repetition is reduced
chapter purpose is clarified
transitions are composed, not appended
11. Recommended automated gate checklist
Use this as a pre-publish validator.
Auto-reject checks
internal token / slot marker present
malformed duplicate words present
paragraph similarity above threshold across manuscript
repeated 25+ word block found
chapter with more than 2 unresolved mode jumps
chapter with more than 5 structural modes in under 800 words
imported register anomaly detected
orphaned fragment line detected
Human editorial checks
does this feel authored?
does this chapter have one job?
does the reader feel held?
does the next chapter feel necessary?
are the repetitions intentional or accidental?
would a real reader highlight and share lines from this?
12. Final policy statement for the agent
Use this exactly:
Reject Pearl Prime manuscript output if it contains any internal artifact leakage, any obvious broken prose, any repeated 25+ word block, or any chapter with more than two unresolved mode jumps. Hold for revision if the manuscript is artifact-clean but still shows visible scene-furniture repetition, weak chapter function, unstable voice, or cyclical rather than cumulative progression. Pass only when the book reads as one authored therapeutic experience with low repetition, clean transitions, clear chapter purpose, and a felt progression from recognition to possibility.
If you want, I can turn this next into a copy-paste dev intake prompt for your repo agent.




---

**Cursor**

Source file in-repo: `artifacts/qa/pearl_prime_ahjan_genz_anxiety_all_runtimes.txt` (use as regression corpus / golden “bad” examples).

```
You are Pearl_Dev + Pearl_Architect + Pearl_Prime (core_pipeline quality). Obey docs/SESSION_UNITY_PROTOCOL.md (STARTUP_RECEIPT / CLOSEOUT_RECEIPT). Read artifacts/qa/pearl_prime_ahjan_genz_anxiety_all_runtimes.txt (Pearl Prime anxiety bundle — all runtimes) as the **evidence corpus** that motivated this work; read specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md and docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md where they govern delivery; reuse existing machinery from PR #420 / #422 where possible (`delivery_contract_gate`, `compose_from_enriched_book`, `frame_governor`, `chapter_purpose_contracts`, `clean_for_delivery`) instead of inventing parallel systems.

PROJECT_ID: proj_state_convergence_20260328
SUBSYSTEM: core_pipeline
AUTHORITY_DOCS: docs/SESSION_UNITY_PROTOCOL.md; docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md; docs/DOCS_INDEX.md; config/quality/book_pass_gate_thresholds.yaml; config/source_of_truth/chapter_purpose_contracts.yaml; config/source_of_truth/frame_registry.yaml; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv

OWNER TASK — Implement “Pearl Prime Book Quality Gate” (developer fail rubric)

Implement an **automated pre-publish / CI gate** (Python + pytest) that encodes the policy below. Output: `phoenix_v4/quality/book_quality_gate.py` (or extend an existing gate module), wired so `scripts/run_pipeline.py` (or the canonical compile/delivery path) can emit a **`book_quality_report.json`** next to `quality_summary.json`, and **fails the build** when release band is **Reject**.

---

## Release bands (machine-classified)

**A — Reject outright** if ANY:
- Internal labels in reader prose: `## HOOK`, `## STORY`, `v\d+`, slot names, dict/YAML residue, placeholder tokens.
- Broken assembly: doubled words (`The the`), clipped fragments, obvious merge orphans.
- **>2** verbatim duplicate blocks **>25 words** (same text, allow intentional refrain only if config-marked; default = fail).
- **>1** chapter with **>2 unresolved mode jumps** (scene→teaching→exercise etc. without bridge — use lightweight slot-type sequence from composed chapter if available; else heuristic on headings + paragraph classifiers documented in code).
- Voice-register anomaly: same heuristic as frame pipeline for “discourse / pasted academic” vs somatic coach (extend patterns, do not use LLM).

**B — Hold** if no A triggers but repetition / transition / progression scores below thresholds.

**C — Pass to editorial** only if all hard gates green AND soft scores meet minima below.

---

## Hard gates (binary)

**Gate 1 — Artifact leakage:** zero matches against a maintained regex bundle + “double word” scan + `##` header leak patterns (extend lists from spine bridge work).

**Gate 2 — Verbatim duplicate block:** rolling hash of normalized paragraphs; flag any paragraph ≥25 tokens appearing >1× unless `refrain_allowlist` in config.

**Gate 3 — Broken prose:** doubled articles, sentence length 0–2 tokens orphan lines, `In this discourse` style markers from rubric.

**Gate 4 — Chapter function:** each chapter must declare or infer **one dominant_job**; fail if **>5 structural modes in <800 words** (modes from slot type tags or paragraph taxonomy — document inference limits in README in `artifacts/pilots/book_quality_gate_verify/`).

---

## Soft rubrics (0–2 per dimension, aggregate as spec)

Per chapter, score: opening coherence, mode transitions, progression vs prior chapter, ending landing — **min 5/8** per chapter, **book avg ≥6/8**; **auto-fail** any chapter total ≤2.

Therapeutic: non-shaming, somatic specificity, practice usability, emotional containment — **min 6/8** per chapter, book avg **≥6.5/8**; **auto-fail** any chapter with 0 on containment.

Bestseller readability: voice, momentum, memorability, freshness — **min 5/8** per chapter, book avg **≥6/8**; **auto-fail** book freshness 0.

Implement **scene-furniture** stem counter per 10k words (config list: window/sill/street below/task is open, etc.) — **fail** if same stem **>3** per 10k OR same pattern in **>2** chapters unchanged (tunable YAML).

---

## Runtime policy flags (config)

Add `config/quality/book_quality_gate.yaml` (schema_version, thresholds, phrase lists, `micro_book_15` / `micro_book_20` default **reject** unless `override: true` in job manifest for experiments).

---

## Tests

- `tests/test_book_quality_gate.py`: fixtures with **synthetic bad** strings (artifact, duplicate 30-word block, mode-stack short chapter) → **Reject**; **clean** fixture → **Pass**.
- Optional: one test that loads **snippets** from `artifacts/qa/pearl_prime_ahjan_genz_anxiety_all_runtimes.txt` (keep test input small — extract 20–40 line excerpts into `tests/fixtures/book_quality_gate/` rather than committing full multi-format file if huge).

---

## Pilot

Write `artifacts/pilots/book_quality_gate_verify/` with `README.md`, sample `book_quality_report.json`, and note how micro_book_15/20/30 from the anxiety bundle classify under the gate.

---

## Policy string (emit in report + docs)

Reject Pearl Prime manuscript output if it contains any internal artifact leakage, any obvious broken prose, any repeated 25+ word block, or any chapter with more than two unresolved mode jumps. Hold for revision if artifact-clean but scene-furniture repetition, weak chapter function, unstable voice, or cyclical progression. Pass only when the book reads as one authored therapeutic experience with low repetition, clean transitions, clear chapter purpose, and felt progression from recognition to possibility.

---

WRITE_SCOPE
phoenix_v4/quality/*; config/quality/book_quality_gate.yaml; scripts/run_pipeline.py (or gate hook only); tests/test_book_quality_gate.py; tests/fixtures/book_quality_gate/*; artifacts/pilots/book_quality_gate_verify/*

OUT_OF_SCOPE
Rewriting the full anxiety bundle by hand; LLM classifiers; Pearl News; video.

CONFLICT
Do not collide with active bestseller spines / Pearl News workstreams without Pearl_PM.

CLOSEOUT
Gate summary table on anxiety corpus; commit SHA; PR link; optional register `ws_book_quality_gate_20260414` in ACTIVE_WORKSTREAMS.tsv.

STARTUP_RECEIPT
STARTUP_RECEIPT
AGENT:
TASK:
PROJECT_ID:
SUBSYSTEM:
AUTHORITY_DOCS:
READ_PATH_COMPLETE:
WRITE_SCOPE:
OUT_OF_SCOPE:
BLOCKERS:
READY_STATUS:
```

---

**User**

Give me a prompt. so that we create all of the Images. for US English catalog. Brand one. or the initial image bank. So 60 images.

---

**Cursor**

```
You are Pearl_Video + Pearl_Dev (+ Pearl_Research for topic/intent matrix if needed). Obey docs/SESSION_UNITY_PROTOCOL.md (STARTUP_RECEIPT / CLOSEOUT_RECEIPT). Read docs/INTEGRATION_CREDENTIALS_REGISTRY.md (Pearl Star / ComfyUI), docs/VIDEO_PIPELINE_SPEC.md §image bank, docs/VIDEO_IMAGE_MASTER_PROMPT_SPEC.md, `config/video/channel_registry.yaml` (US English **Brand 1 = `ch_001`**: `brand_id: stillness_press`, `image_bank_path: assets/image_banks/ch_001/`, `style_id: soft_ghibli`, `topic_group: [anxiety, grief, burnout, depression]`, `assembly_profile: profile_a` → **9:16-first**), `config/video/flux_bank_scenes.yaml` (visual intents), `config/video/brand_style_tokens.yaml` + `config/video/prompt_constraints.yaml`, `schemas/video/image_bank_asset_v1.schema.json` (metadata sidecar per asset).

PROJECT_ID: proj_state_convergence_20260328
SUBSYSTEM: video_pipeline

OWNER TASK
Generate the **initial US English image bank for Brand 1 (`ch_001` / Stillness Press)**: **exactly 60** FLUX stills, stored under **`assets/image_banks/ch_001/`** (create dirs as needed), with **JSON sidecars** per `image_bank_asset_v1` (asset_id, layer_type, tags, `composition_compat` for 9:16 native = 1.0, topic, visual_intent, style_version, generation_batch id).

COVERAGE (must total 60)
- **Topics:** only `ch_001` lane topics: **anxiety, grief, burnout, depression** (15 each is 60 if you use 15 per topic — **use 15 images per topic** = 60).
- **Visual intents:** rotate `HOOK_VISUAL`, `CHARACTER_EMOTION`, `SYMBOLIC_METAPHOR`, `ENVIRONMENT_ATMOSPHERE` from `flux_bank_scenes.yaml` so each topic gets a **balanced mix** (not all hooks); document the assignment table in `artifacts/video/image_bank_ch_001/BATCH_MANIFEST_60.yaml` (or JSON).
- **Aspect:** generate **native 9:16** (1080×1920 or repo standard from `format_specs.yaml`) as primary; optional second pass for 16:9/1:1 **only if** owner asks — **this task is 9:16 only** to hit 60 on time.
- **Style:** `soft_ghibli` + channel negatives; respect `override_shared_negatives: false` (keep “no anime” path per registry).

EXECUTION
1) Write a small **batch driver** (extend `scripts/video/flux_client.py` / `scripts/image_generation/*` if present) that reads the manifest, calls **ComfyUI on Pearl Star** (`COMFYUI_URL` from Keychain), saves `ch_001_<topic>_<intent>_<seq>.png` + `<same>.asset.json`, and logs failures for retry.
2) **QC:** reject blur/watermark/text in image; re-roll up to N times per slot (configurable); record final pass/fail in manifest.
3) **Do not** commit multi-GB without **Git LFS** if repo policy requires it (`ws_lfs_setup_20260410` — follow owner/LFS doc); otherwise commit manifest + sidecars + **pointer** policy for binaries.

OUT OF_SCOPE
Other channels (ch_002+); audiobook/video render; teacher triptych (`ws_teacher_manga_triptych`) except reusing same Comfy host schedule — coordinate if GPU contention.

CONFLICT
Check `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` before long GPU runs.

DELIVERABLES
- 60 PNGs under `assets/image_banks/ch_001/`
- Batch manifest + `artifacts/video/image_bank_ch_001/generation_log.md` (timing, model, seed policy)
- CLOSEOUT: throughput (images/hour), total wall time, failed slots

STARTUP_RECEIPT
STARTUP_RECEIPT
AGENT:
TASK:
PROJECT_ID:
SUBSYSTEM:
AUTHORITY_DOCS:
READ_PATH_COMPLETE:
WRITE_SCOPE:
OUT_OF_SCOPE:
BLOCKERS:
READY_STATUS:
```

**Note:** Full spec targets **~400** images per channel (VIDEO_PIPELINE_SPEC.md); **60** is your **MVP slice** (here: **15×4 topics**). Adjust the manifest math if you instead want **60 = 4 intents × 15 slots** across all topics mixed — the prompt text above locks **15 per topic** for even catalog coverage.

---

**User**

give me propmt for pearl prime CLI 1hr book : teacher mode - ahjan. for gen z, anxiety + 90 sec YT vid

---

**Cursor**

Use this paste-ready prompt for Pearl Prime CLI:

```txt
You are Pearl_Prime in CLI, running in TEACHER MODE for instructor persona: AHJAN.

MISSION
Create a complete “1-hour book” package for Gen Z on anxiety, plus a 90-second YouTube video derivative.

AUDIENCE + POSITIONING
- Audience: Gen Z (16–26), high stress, doomscroll fatigue, overthinking, social pressure.
- Tone: warm, grounded, direct, non-cringe, non-preachy, practical.
- Voice: teacher/mentor (Ahjan), emotionally safe, culturally current, no therapy cosplay.
- Reading level: simple, clear, conversational (roughly grade 7–9 readability).

CORE DELIVERABLES
1) 1-Hour Book (target 8,000–10,500 words)
2) 90-second YouTube video package (script + shot plan + metadata)

BOOK SPEC (1-HOUR)
- Working title: “Anxiety Is Loud, You Don’t Have To Be”
- Subtitle: “A Gen Z guide to calm your mind, reset your body, and get your life back in small steps”
- Structure:
  - Hook + promise
  - 10 chapters (8–12 min each in audio pace)
  - End of each chapter:
    - “Try this in 2 minutes”
    - “If this is hard, do this version instead”
  - Final 7-day micro-reset plan
  - FAQ: panic, overthinking at night, social anxiety, school/work overwhelm
- Include:
  - relatable Gen Z scenarios (texts left on read, exam pressure, job uncertainty, comparison loops)
  - evidence-aligned coping tools (breath, body, cognitive defusion, behavioral activation, sleep anchors)
  - no clinical diagnosis claims, no cure language
- Safety:
  - Add non-alarmist support note for severe symptoms/crisis
  - Avoid medical/legal advice framing

YOUTUBE 90-SECOND SPEC
- Goal: high retention, emotionally resonant, practical takeaway.
- Output format:
  1) Timestamped script (0:00–1:30)
  2) Shot list by beat (B-roll/teacher-on-cam/text overlays)
  3) On-screen captions (short, punchy)
  4) Title options (10)
  5) Thumbnail text options (8)
  6) Description (150–250 words)
  7) Hashtags (10–15)
  8) CTA variants (soft + direct)
- Video arc:
  - 0:00–0:05 Hook (pattern interrupt)
  - 0:05–0:25 “Why anxiety feels this way”
  - 0:25–1:05 3-step reset
  - 1:05–1:25 identity reframe + encouragement
  - 1:25–1:30 CTA to book/next step

PEARL PRIME QUALITY GATE (MUST PASS BEFORE FINAL)
- Clarity score: 9/10+
- Emotional safety: pass
- Practicality: each section has actionable steps
- No fluff, no repetition loops, no generic platitudes
- Output must feel native to Ahjan teacher mode

OUTPUT ORDER (EXACT)
A) Executive summary (10 bullets max)
B) Full 1-hour book draft
C) 90-sec YouTube package
D) “Prime QA report” with:
   - strengths
   - weak spots
   - exact edits applied
   - final readiness verdict: READY / NEEDS 1 MORE PASS

If anything is ambiguous, make the best assumption and proceed without asking questions.
```

If you want, I can also give you a **shorter “fast-run” version** optimized for one CLI pass (less strict, quicker output).

---

**User**

document all and give handoff .md

---

**Cursor**

Checking where handoff docs live in the repo and assembling a single handoff document.



Creating the handoff document in `artifacts/coordination/`, matching existing handoff patterns.



Here’s what was added.

### Handoff file

**Path:** [`artifacts/coordination/HANDOFF_PEARL_PRIME_AHJAN_GENZ_ANXIETY_IMAGE_BANK_CH001_2026_04_15.md`](artifacts/coordination/HANDOFF_PEARL_PRIME_AHJAN_GENZ_ANXIETY_IMAGE_BANK_CH001_2026_04_15.md)

### What it contains

1. **Section A — Pearl Prime CLI**  
   Full paste-ready prompt for **teacher mode Ahjan**, **Gen Z + anxiety**, **~1 hr book** + **90s YouTube** package, plus a short checklist and a pointer to `artifacts/qa/pearl_prime_ahjan_genz_anxiety_all_runtimes.txt`.

2. **Section B — Brand 1 / `ch_001` image bank (60)**  
   Channel facts from `channel_registry.yaml`, **15×4 topic** grid, flux intents, repo doc/code table, condensed agent prompt, and a checklist (LFS, manifest, schema).

3. **Section C — Closeout**  
   States that this is documentation/handoff only; next step is for the operator to run A and/or B.

4. **Quick index**  
   Links the main config and QA artifact paths at the bottom.

If you want this split into two files (Prime-only vs video-only) or renamed to match another naming convention in `artifacts/coordination/`, say how you’d like it named.

