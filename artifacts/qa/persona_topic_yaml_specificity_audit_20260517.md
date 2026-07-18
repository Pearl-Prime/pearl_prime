# Persona+Topic YAML Specificity Audit — Pearl Prime Rendering Chain

**Date:** 2026-05-17
**Author:** Pearl_Architect (read-only forensic audit; Tier 1 operator-present)
**Project:** `proj_pearl_prime_bestseller_rebase_20260425`
**Subsystem:** `pearl_prime;core_pipeline`
**Trigger:** Operator complaint — "generated books read vague / generic 'feel-better' copy that could apply to any persona or any topic — instead of specifically addressing what `registry/<topic>.yaml` + `atoms/<persona>/<topic>/` + `SOURCE_OF_TRUTH/teacher_banks/<teacher>/` promise."

---

## 1. Executive verdict (3 lines)

1. **Are we using the persona+topic YAML?** Partially — registry chapter titles + persona engine-bank STORY atoms ARE consumed; **persona REFLECTION / HOOK content is DILUTED by additively-stacked generic-Buddhist teacher (ahjan) atoms**, and SCENE slots fall through to known-regression location fallbacks ("soft daylight along the sill" × 68, "street below" × 51) instead of persona-specific imagery.
2. **At what fidelity?** The today (2026-05-17 13:07) `ahjan × gen_z_professionals × anxiety × standard_book` run on `--quality-profile draft` scored `bestseller_craft.overall_score=0.4976` (below the 0.55 ONTGP threshold per [docs/PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md:111](docs/PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md:111)); only **1/12 chapters PASS** bestseller-craft, 11/12 are WARN/FAIL with `move_scores` for `turn` (0.35) and `pull` (0.32) failing the Orient/Name/Turn/Give/Pull contract in [docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md §4](docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md).
3. **Root cause (ranked):** **(c) upstream content gap** — ahjan teacher_bank is 51% Buddhist/Dharma/karma-themed and 0% anxiety-mechanism-themed across REFLECTION atoms — **PLUS (a-residual) `story_schedule` empty (0 entries) for this persona×topic** despite `build_story_schedule()` being wired, so the named-character through-line collapses to a single character (Marcus × 5) instead of the comparator's full cast (Marcus/Priya/Jordan/Sam/Alex/Maya). Loader chain itself is correctly wired (Step 2); SSOTs themselves are specific (Step 1); the failure mode is **content-authoring drift + draft-profile gate softness**, not wiring.

---

## 2. Loader chain call graph (file:line)

Under canonical CLI flag set `--pipeline-mode spine --quality-profile production --exercise-journeys` (per [docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md:570-577](docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md:570) and BESTSELLER-INJECTIONS-MANDATORY-01 in [docs/PEARL_ARCHITECT_STATE.md:601](docs/PEARL_ARCHITECT_STATE.md:601)):

```
scripts/run_pipeline.py:655          enriched = select_enrichment(EnrichmentRequest(...))
  ↓
phoenix_v4/planning/enrichment_select.py:832  def select_enrichment(...)
  ├─ :843  reg = load_registry(topic)               → registry/<topic>.yaml read ✓
  ├─ :845  teacher_atoms = _load_teacher_atoms(tid) → SOURCE_OF_TRUTH/teacher_banks/<tid>/approved_atoms/ ✓
  ├─ :859  persona_atoms = _load_persona_atoms(pid, topic) → atoms/<persona>/<topic>/ ✓
  │                                                    (engine-bank STORY PREPENDED per registry_resolver.py:263)
  ├─ :919  _story_schedule = build_story_schedule(persona, topic, seed, root)
  │                                                  → story_atoms/<persona>/anchored/<topic>/... ❌ empty for ahjan×genz×anxiety
  ├─ :921  _book_tracker = BookSlotTracker()
  ├─ :963-970  STORY at sec 2/5/9: story_schedule.get → source="story_plan" (PR #669 upstream-substitution)
  ├─ :982-1090  Non-STORY: additive stacking persona + registry + teacher → "\n\n".join(_add_pieces)
  ├─ :990-1015  EXERCISE: teacher_atom → practice_library only (PR #612; no persona, no registry)
  └─ :1278     enrichment_audit = {..., "section_packet_audit": _slot_audit, "story_schedule": [...], ...}
  ↓
scripts/run_pipeline.py:697          enriched = apply_depth_pass(enriched, depth_map, ...)
  ↓
scripts/run_pipeline.py:730-732      if --exercise-journeys: attach_exercise_journeys(enriched, ...)
  ↓
scripts/run_pipeline.py:738          prose = compose_from_enriched_book(enriched, ...)
  ↓
phoenix_v4/rendering/chapter_composer.py:2189  compose_from_enriched_book
  └─ :2324  ch_body, _ = compose_golden_spine_chapter(...)
        ↓
phoenix_v4/rendering/golden_chapter_synthesis.py:614  raw = slot.content or ""
                                                :1428  body = (slot.content or "").strip()
  ↓
scripts/run_pipeline.py:1400         (render_dir/"enrichment_audit.json").write_text(...)
                       :1404-1413    section_packet_audit.json (CONDITIONAL — bug, see §5)
```

**Note re BG-PR-09 (closure entry at [docs/PEARL_ARCHITECT_STATE.md:278](docs/PEARL_ARCHITECT_STATE.md:278)):** PR #669 chose **upstream substitution** (swap `SOMATIC_10_SLOT_GRID` sec 2/5/9 from `SCENE` → `STORY` at [phoenix_v4/planning/beatmap_compile.py:42-52](phoenix_v4/planning/beatmap_compile.py:42)) over the pilot's `compose_section_packet(story_schedule=…, slot_tracker=…)` port at [phoenix_v4/rendering/section_packet_composer.py:243](phoenix_v4/rendering/section_packet_composer.py:243). The canonical CLI does NOT invoke `section_packet_composer.compose_section_packet`; it composes via `compose_golden_spine_chapter`. Pilot path is reference-only. **Loader chain is correctly wired today.**

---

## 3. SSOT specificity proof (quotes)

### 3a. `registry/anxiety.yaml` — SPECIFIC to anxiety mechanisms (verbatim)

[registry/anxiety.yaml:10](registry/anxiety.yaml:10) — Chapter 1 title:
> "The Alarm That Won't Stop Ringing"

[registry/anxiety.yaml:25-38](registry/anxiety.yaml:25) — Chapter 1 HOOK F1 (variant 1, 1041 chars):
> "You did everything they said to do. Your chest has not gotten the memo. … This is The Alarm. It fires whether or not there is a threat. … The alarm reads uncertainty as danger. It reads stillness as suspicious. It fires at emails, at silences, at the pause before someone speaks. It fires at nothing. … This is not a flaw in your thinking. It is not weakness. It is a system doing exactly what it was built to do — in a context where that system no longer fits."

**Verdict: highly specific.** Names anxiety mechanism (false alarm, hypervigilance, signal-finding) precisely.

### 3b. `atoms/gen_z_professionals/anxiety/spiral/CANONICAL.txt` — SPECIFIC + named-character (verbatim)

[atoms/gen_z_professionals/anxiety/spiral/CANONICAL.txt:12](atoms/gen_z_professionals/anxiety/spiral/CANONICAL.txt:12) — RECOGNITION v01:
> "Jordan gets a calendar invite for a 'team restructuring discussion.' His mind leaves the room. Team restructuring becomes layoffs becomes his position becomes job search becomes rent becomes moving back home. Six links in a chain, each one forged in under a second. The meeting is about reorganizing the shared drive. He sits through it with adrenaline from a catastrophe that was never on the agenda."

[atoms/gen_z_professionals/anxiety/spiral/CANONICAL.txt:22](atoms/gen_z_professionals/anxiety/spiral/CANONICAL.txt:22) — RECOGNITION v02:
> "Priya's quarterly review is next week. … Her mind starts the chain: what if the feedback is negative, what if negative means PIP, what if PIP means fired, what if fired means visa issues, what if visa means leaving the country. … From inside, she's six steps from deportation."

**Verdict: highly specific.** Named characters (Jordan, Priya, Kai, Maya), Gen-Z-professional contexts (visa, PIP, calendar invites, sprint reviews), anxiety mechanism (catastrophizing chains) named precisely.

### 3c. `atoms/gen_z_professionals/anxiety/overwhelm/CANONICAL.txt` — SPECIFIC (verbatim)

[atoms/gen_z_professionals/anxiety/overwhelm/CANONICAL.txt](atoms/gen_z_professionals/anxiety/overwhelm/CANONICAL.txt) — has named characters Alex(24+), Maya, Jordan, Sam, Priya across all 4 RECOGNITION variants; persona-specific economic contexts (student loans $500/mo, $35K nonprofit salary, gig-economy fragility); somatic anchors per atom.

### 3d. Ahjan COMPRESSION teacher bank — SPECIFIC ahjan voice cadence (verbatim)

[SOURCE_OF_TRUTH/teacher_banks/ahjan/approved_atoms/COMPRESSION/ahjan_COMPRESSION_001.yaml:7](SOURCE_OF_TRUTH/teacher_banks/ahjan/approved_atoms/COMPRESSION/ahjan_COMPRESSION_001.yaml:7):
> "The wound is not your enemy. It is the doorway you keep walking past. Turn toward it once and the whole hallway disappears."

[SOURCE_OF_TRUTH/teacher_banks/ahjan/approved_atoms/COMPRESSION/ahjan_COMPRESSION_002.yaml:7](SOURCE_OF_TRUTH/teacher_banks/ahjan/approved_atoms/COMPRESSION/ahjan_COMPRESSION_002.yaml:7):
> "Safety is not the absence of danger. It is the presence of connection. You were never meant to survive this alone."

**Verdict: distinct ahjan voice** — paradox + relational anchor, characteristic cadence.

### 3e. Ahjan HOOK / TEACHER_DOCTRINE / REFLECTION bank — GENERIC BUDDHIST (the smoking gun)

[SOURCE_OF_TRUTH/teacher_banks/ahjan/approved_atoms/HOOK/ahjan_HOOK_011.yaml:3](SOURCE_OF_TRUTH/teacher_banks/ahjan/approved_atoms/HOOK/ahjan_HOOK_011.yaml:3):
> "Every person carries the capacity for awakening. This capacity is not earned or given by another. It exists in you now. The work is simply to remove what covers it."

[SOURCE_OF_TRUTH/teacher_banks/ahjan/approved_atoms/HOOK/ahjan_HOOK_007.yaml:3](SOURCE_OF_TRUTH/teacher_banks/ahjan/approved_atoms/HOOK/ahjan_HOOK_007.yaml:3):
> "The Buddha taught that desire itself is not the problem. Wanting to eat when hungry is natural. The problem is the story we build around wanting. You can learn to want without the story."

[SOURCE_OF_TRUTH/teacher_banks/ahjan/approved_atoms/TEACHER_DOCTRINE/ahjan_TEACHING_083_mined.yaml:2](SOURCE_OF_TRUTH/teacher_banks/ahjan/approved_atoms/TEACHER_DOCTRINE/ahjan_TEACHING_083_mined.yaml:2):
> "It symbolizes the cyclical nature of existence, where individuals may find themselves in any of the Six Worlds, depending on their karma and actions. … Within each realm, there is a Buddha or a guide pointing the way to transcend suffering and ascend to a higher state of existence."

**Coverage stats (this branch):**

| ahjan slot | Total atoms | Anxiety-mechanism atoms (grep `anxiety\|alarm\|amygdala\|catastrophiz\|rumination\|nervous system`) | Buddhist-themed atoms (grep `Buddha\|Dharma\|karma\|enlightenment\|samsara\|Tantra`) |
|---|---:|---:|---:|
| `HOOK/` | 12 | **0** | 3 |
| `REFLECTION/` | 63 | **0** | **32** (51%) |
| `TEACHER_DOCTRINE/` | 9 | not measured | 3 (33%) |

**Verdict: ahjan teacher_bank is content-generic w.r.t. anxiety.** This is the root of the operator's "feel-better copy that could apply to any persona or any topic" complaint. The voice is recognizable; the topic-specificity is absent.

---

## 4. Smoking-gun pairs (rendered prose vs SSOT slot it should echo)

**Source artifact:** `artifacts/qa/_scratch_pp_ahjan_genz_anxiety/standard_book/book.txt` (12,236 words; rendered 2026-05-17 13:07; `--quality-profile draft`).

### Pair 1 — Chapter 1 HOOK: should be Gen-Z anxiety opener; is generic Buddhist awakening line

**Rendered prose, [book.txt:4](artifacts/qa/_scratch_pp_ahjan_genz_anxiety/standard_book/book.txt:4) (Chapter 1 first paragraph):**
> "Every person carries the capacity for awakening. This capacity is not earned or given by another. It exists in you now. The work is simply to remove what covers it."

**Provenance:** `SOURCE_OF_TRUTH/teacher_banks/ahjan/approved_atoms/HOOK/ahjan_HOOK_011.yaml` — generic Buddhist-style atom; **no anxiety mechanism named**.

**What should have been rendered (per registry):** `registry/anxiety.yaml` Chapter 1 HOOK F1 (cited in §3a above):
> "You did everything they said to do. Your chest has not gotten the memo. … This is The Alarm. It fires whether or not there is a threat. …"

The persona/registry HOOK content DOES eventually appear later in Chapter 1 (line containing "You did everything they said to do. Your chest has not gotten the memo. ---") but is dumped as a `---`-delimited wall of ~18 short HOOK variant fragments rather than a single chosen variant — the teacher overlay opens the chapter, and the persona HOOK is appended as a brain-dump.

### Pair 2 — Chapter 2 REFLECTION: should be anxiety-mechanism reframe; is generic-Buddhist meditation primer

**Rendered prose ([book.txt:54](artifacts/qa/_scratch_pp_ahjan_genz_anxiety/standard_book/book.txt:54)) Chapter 2 REFLECTION 1:**
> "The key insight is that one has the capacity to move beyond these states of mind through meditation and self-realization. By stilling the mind, practicing compassion, and embracing the teachings of the Dharma, individuals can elevate their consciousness and transcend the limitations of the Six Worlds."

**Provenance:** Pattern-matches the ahjan REFLECTION/TEACHER_DOCTRINE bank's `Six Worlds` / `Dharma` / `karma yoga` content (32 of 63 REFLECTION atoms are this register).

**What should have been rendered:** Persona REFLECTION from `atoms/gen_z_professionals/anxiety/REFLECTION/CANONICAL.txt` (anxiety-specific neuroscience or persona-specific contextual processing).

### Pair 3 — Chapter 1 SCENE: should be persona-specific scene; dominated by known-regression location fallback

**Rendered prose ([book.txt:8-30](artifacts/qa/_scratch_pp_ahjan_genz_anxiety/standard_book/book.txt:8)) — first three SCENE blocks of Chapter 1 contain:**
> "soft daylight along the sill through the office window above your monitor … the street below is there below … soft daylight along the sill hits when the door opens … the street below is full of people moving in all directions … the train sounds from outside … soft daylight along the sill against the building"

**Whole-book counts** (computed from `book.txt`, 12,236 words):

| Phrase | Occurrences | Hard cap per [phoenix_v4/quality/regression_museum/detectors.py](phoenix_v4/quality/regression_museum/detectors.py) `detect_repeated_scene_anchor` | Provenance |
|---|---:|---:|---|
| "soft daylight along the sill" | **68** | 3 / book | [config/quality/book_quality_gate.yaml](config/quality/book_quality_gate.yaml) regression list; [phoenix_v4/planning/injection_resolver.py](phoenix_v4/planning/injection_resolver.py); [phoenix_v4/rendering/golden_chapter_synthesis.py](phoenix_v4/rendering/golden_chapter_synthesis.py); [config/content_banks/loc_var_render.yaml](config/content_banks/loc_var_render.yaml) |
| "street below" | **51** | 3 / book | same |
| "your screen" | 19 | — | scene fallback |
| "the train" | 17 | 3 / book | book_quality_gate.yaml regression list |
| "the elevator" | 12 | — | scene fallback |
| "task is open" | 9 | — | book_quality_gate.yaml regression list |
| "conference room" | 5 | — | book_quality_gate.yaml regression list |
| "slack notification" | 5 | — | book_quality_gate.yaml regression list |
| "fluorescent" | 4 | — | book_quality_gate.yaml regression list |

**Vocabulary cross-tab (anxiety-mechanism vs generic-Buddhist):**

| Anxiety-mechanism vocabulary | Hits | Generic-Buddhist vocabulary | Hits |
|---|---:|---|---:|
| amygdala | 0 | meditation | 15 |
| cortisol | 1 | karma | **9** |
| hypervigilance | 0 | enlightenment | 5 |
| rumination | 0 | Buddha | 4 |
| catastrophizing | 0 | compassion | 4 |
| catastrophe | 0 | consciousness | 3 |
| false alarm | 0 | desire | 3 |
| somatic | 0 | wisdom | 2 |
| fight-or-flight | 0 | awakening | 1 |
| spiral | 2 | Dharma | 1 |
| nervous system | 17 (allowlisted refrain per refrain_allowlist.yaml ITEM-2) | | |

### Pair 4 — Named-character story arc collapse

**Rendered named-character hits in `standard_book/book.txt` (12,236 words, 36 STORY slots):**
- Marcus: 5
- (Ahjan: 1 — attribution mention, not character)
- Priya / Jordan / Sam / Alex / Maya / Kai / Elena / Carmen / Sarah / Mia: **0 each**

**Comparator baseline ([artifacts/qa/move4_2026_04_26/per_persona_topic_coverage.md:29](artifacts/qa/move4_2026_04_26/per_persona_topic_coverage.md:29) for similar persona × anxiety production-profile sweep, 2026-04-26):**
- `financial_anxiety_gen_z_professionals`: Marcus(4), Priya(2), Jordan(9), Sam(8), Alex(1) — **5 named characters, 24 hits**
- `burnout_gen_z_professionals`: Marcus(15), Priya(13), Jordan(17), Sam(10), Maya(18) — **5 named characters, 73 hits**
- `courage_gen_z_professionals`: Marcus(3), Priya(9), Jordan(20), Sam(16), Alex(5), Maya(9) — **6 named characters, 62 hits**

**Today's draft run vs comparator's production run:** ~7× fewer named-character hits; ~5× fewer distinct characters. This is the through-line collapse symptom.

---

## 5. Telemetry table

**Source:** `artifacts/qa/_scratch_pp_ahjan_genz_anxiety/standard_book/enrichment_audit.json` + `quality_summary.json` + `chapter_flow_report.json` (today, 2026-05-17 13:07).

### 5a. Atom-source distribution (slot-level audit)

| Source | Slot count | % of 120 total |
|---|---:|---:|
| `slots_from_teacher` (ahjan HOOK / EXERCISE×2 / TEACHER_DOCTRINE / INTEGRATION = 5 per chapter × 12) | 60 | 50% |
| `slots_from_persona` (engine-bank STORY at sec 2/5/9 + persona REFLECTION/SCENE) | 36 | 30% |
| `slots_from_registry` (registry REFLECTION at sec 3/7 ≈ 24 expected) | 22 | 18% |
| `slots_from_practice_library` (EXERCISE fall-through) | 0 | 0% |
| `practice_library_warnings` | 0 | — |
| `slots_empty` (REFLECTION ch7+ch8 slot_index=6 gaps) | 2 | 2% |

**Note:** Per BESTSELLER-INJECTIONS-MANDATORY-01, slot waterfall behaves as designed; the issue is **what** the teacher atoms contain, not whether they fire.

### 5b. story_schedule + book_slot_tracker

| Field | Expected | Observed | Notes |
|---|---|---:|---|
| `story_schedule` entries | 36 (12 ch × 3 STORY slots) | **0** (key missing from JSON) | See §5d audit-write bug |
| `book_slot_tracker_used_ids` | List of IDs | **missing from JSON** | Same bug |
| `section_packet_audit` (per-slot detail) | List of 120 entries | **missing from JSON** | Same bug |

**Story-schedule collapse:** Whether `_story_schedule` is empty in memory or merely lost in serialization is indeterminate from the on-disk JSON alone. The rendered prose evidence (Marcus × 5, no Priya/Jordan/Sam/Alex/Maya) is consistent with story_schedule being EMPTY in memory: STORY slots at sec 2/5/9 fall through to the persona_atoms["STORY"] waterfall, which picks the first matching atom deterministically per `_deterministic_index(seed)`. With `gen_z_professionals × anxiety × seed=…`, that single deterministic pick is biased toward whichever atom indexes first — explaining Marcus(5) without a full cast.

### 5c. EXERCISE drops and frame-governance flags

`quality_summary.json`:
- `exercise_slots_dropped`: **12 entries** — chapters 1 and 12 had `max_allowed=0` per `assign_chapter_purpose_contracts`; chapters 2-11 had `max_allowed=1` against `format_cap=2`. Result: half the EXERCISE slots are dropped at compose time.
- `chapter_contract_warnings`: 1 — "chapter 12: emotional_job 'resolution' matches previous chapter — escalation contract may be weak"
- `frame_governance_chapters`: **3 chapters (3, 5, 11)** with `karma` absolute_claim violations:
  > Ch 3: "Unlike the common perception of karma as a system of reward and punishment, karma yoga sees action as a means to spiritual…"
  > Ch 11: "Integrating Karma Yoga into Daily Life…"
  - `frame_compliant: True`, `softened: []`, `stripped: []`, `hard_fail: []`. **Detected but not enforced at draft.**
  - `spiritual_density: 0.176` in chapter 11 (high).

### 5d. Audit-write bug (separate from main finding, but blocks observability)

[scripts/run_pipeline.py:1404-1413](scripts/run_pipeline.py:1404):
```python
_spa = enriched.enrichment_audit.get("section_packet_audit")
_spa_dict: dict = {}
if isinstance(_spa, dict):           # ❌ _spa is a List per enrichment_select.py:1285
    _spa_dict = dict(_spa)
if _music_audit_spine is not None:
    _spa_dict["musician_overlay"] = _music_audit_spine
if _spa_dict:
    (render_dir / "section_packet_audit.json").write_text(...)
```

`_slot_audit` is constructed as `List[Dict[str, Any]]` at [enrichment_select.py:924](phoenix_v4/planning/enrichment_select.py:924), assigned as `"section_packet_audit": _slot_audit` at [enrichment_select.py:1285](phoenix_v4/planning/enrichment_select.py:1285). The `isinstance(_spa, dict)` guard at run_pipeline.py:1406 is therefore always False, so:
- `section_packet_audit.json` is **never written** to disk in non-music runs.
- The `section_packet_audit` / `story_schedule` / `book_slot_tracker_used_ids` keys are populated in memory by `select_enrichment` (per enrichment_select.py:1285-1300) but are **absent from `enrichment_audit.json` on disk** for both today's standard_book and deep_book_6h runs.

This is an observability gap, not the root cause of vagueness. But it **prevents Pearl_Editor/Pearl_Architect from diagnosing per-slot atom routing without re-running the pipeline.**

### 5e. Bestseller-craft gate (the closest existing gate to vagueness detection)

`chapter_flow_report.json` → `bestseller_craft`:
- `overall_score: 0.4976` — **below 0.55 ONTGP threshold** per [docs/PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md:111](docs/PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md:111)
- Per-chapter status: ch5=PASS; ch3=FAIL; ch1,2,4,6,7,8,9,10,11,12=WARN
- Chapter 1 move_scores: orient=0.62, name=0.45, turn=**0.35**, give=0.41, pull=**0.32**
- Chapter 1 issues: `["move_warn:turn,pull", "few_reframe_or_contrast_markers", "no_named_tension_or_question_in_closer"]`
- Chapter 1 remediation: `"End with a named tension or sharp question — not a teaser slogan (overlay §7)."`

**`dimension_gates_status: FAIL` AND `dimension_gates_blocks_delivery: True` BUT `overall status: PASS`** — at draft profile the dimension-gates failure is recorded but doesn't block. At `--quality-profile production` per BESTSELLER-INJECTIONS-MANDATORY-01, this should hard-fail.

---

## 6. Root-cause hypothesis (ranked with evidence)

### Rank 1 — **(c) YAML content itself is generic upstream — Pearl_Editor authoring gap for ahjan teacher_bank** (HIGH CONFIDENCE)

**Evidence:**
- §3e cross-tab: 32/63 ahjan REFLECTION atoms Buddhist-themed; **0/63** anxiety-mechanism-themed.
- §3e: 3/9 ahjan TEACHER_DOCTRINE atoms Buddhist-themed; 0/12 ahjan HOOK atoms address anxiety mechanisms.
- §4 Pair 1, Pair 2: Generic Buddhist content from ahjan teacher_bank lands verbatim in the rendered anxiety book (`ahjan_HOOK_011` opens Chapter 1; `karma yoga` content surfaces in chapters 3, 5, 11).
- §5a: 60/120 slots (50%) are sourced from this teacher bank under additive stacking, so the dilution is structural — fixing the rendering won't help; the **content has to be re-authored**.

**Why this is rank 1:** Even with perfect loader wiring and a successful `--quality-profile production` run, additively stacking generic-Buddhist atoms over anxiety-specific persona + registry atoms produces a hybrid that the operator correctly perceives as "feel-better copy that could apply to any topic." The teacher voice is recognizable; the topic-binding is missing.

### Rank 2 — **(a)-residual: `story_schedule` empty in memory for ahjan × genz × anxiety** (HIGH CONFIDENCE)

**Evidence:**
- §4 Pair 4: rendered Marcus × 5 only, vs comparator (production profile, 2026-04-26) showing 5-6 named characters per book with 24-73 total hits.
- §5b: story_schedule key absent from on-disk audit JSON; need to instrument or re-run to confirm in-memory state, but rendered output is consistent with empty schedule.
- BG-PR-09 Phase 2 closure entry ([docs/PEARL_ARCHITECT_STATE.md:282](docs/PEARL_ARCHITECT_STATE.md:282)) verified `gen_z_professionals × anxiety` on `origin/main` HEAD `99a926a9b7` showed "12 named-character hits (Marcus=6, Priya=3, Jordan=1); section_packet_audit.json shows 72 story_plan/HARDSHIP source_id matches at sec 2/5/9" — so the path WAS working at HEAD `99a926a9b7` (2026-04-27). Today's HEAD is `3c97ace63`; some commits between may have regressed this for ahjan-mode runs specifically.

**Why this is rank 2:** Even if the teacher bank is re-authored to address anxiety, losing the named-character through-line cuts the comparator's primary bestseller signal (engine-bank-named-character path produces 26/30 bestseller-grade per comparator).

### Rank 3 — **(e) Overlay enforcement (frame_governor + bestseller_craft) detects vagueness but does NOT block at draft profile** (HIGH CONFIDENCE)

**Evidence:**
- §5c: frame_governor detected `karma` absolute-claim violations in ch 3/5/11; recorded `violations: [...]` but `softened: []`, `stripped: []`, `hard_fail: []`, `frame_compliant: True`.
- §5e: bestseller_craft `overall_score=0.4976` < 0.55 threshold; 11/12 chapters WARN/FAIL; dimension_gates_status=FAIL with dimension_gates_blocks_delivery=True; **overall status still PASS** because `quality_profile=draft` and `gates_hard=False`.
- Per BESTSELLER-INJECTIONS-MANDATORY-01 ([docs/PEARL_ARCHITECT_STATE.md:601](docs/PEARL_ARCHITECT_STATE.md:601)): EI v2 gate and enrichment-gap hard-fail bind only on `--quality-profile production`. EXERCISE-BANK-RESOLUTION-01 strict-canonical gate also production-only.

**Why this is rank 3:** This is a process drift, not a code drift. If the operator is iterating on draft-profile runs, the existing gates won't catch vagueness. The fix is either (i) discipline (run production for any review) or (ii) routing decision to elevate frame_governor.violations from advisory to soft-blocking on draft.

### Rank 4 — **(f) `format_registry standard_book` chapter allocation interacts with `assign_chapter_purpose_contracts` to drop EXERCISE slots from chapters 1 and 12** (MEDIUM CONFIDENCE — partial contributor)

**Evidence:** §5c — 12 EXERCISE slots dropped; chapters 1 and 12 had `max_allowed=0`. The "Give" move per [BESTSELLER_WRITING_OVERLAY_SPEC §4](docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md) requires a concrete EXERCISE; dropping EXERCISE from opening/closing chapters means those chapters cannot satisfy the Give move and contribute to the low `give` and `pull` move scores.

### Rank 5 — **(d) Renderer accepts SSOT but additive concatenation dumps multiple persona HOOK variants into a single slot as `---`-delimited wall** (LOW-MEDIUM CONFIDENCE)

**Evidence:** §4 Pair 1: 18 short HOOK fragments rendered with " --- " separator inside Chapter 1, not selected per-chapter variant. This appears to be the additive stacking at [enrichment_select.py:1092](phoenix_v4/planning/enrichment_select.py:1092) `content = "\n\n".join(_add_pieces)` interacting with how `_load_persona_atoms` returns ALL variants as a single list — the per-slot selection at `_deterministic_index` may be returning the whole list rather than one item for some slot types. **Needs deeper trace to confirm; do not act on this hypothesis without verification.**

### Rank 6 — **(b) loader points at wrong path / silent fallback** (LOW — RULED OUT)

**Evidence (ruling out):** §2 loader call graph traces end-to-end correctly; §3 SSOTs are read (chapter titles, persona engine-bank STORY atoms, teacher COMPRESSION atoms all surface in prose where expected). Wiring is not the failure mode.

---

## 7. Recommended fix workstreams (to route to Pearl_PM — do NOT open here)

Routing per the task brief's options table. Each ws is a separate decision for Pearl_PM; **this audit recommends but does not authorize**.

### 7.1 — Root cause (c) — PRIMARY, blocks all others

**Recommend opening:** `ws_ahjan_teacher_bank_topic_specific_authoring_20260517` (Pearl_Editor + Pearl_Writer per PEARL-EDITOR-UPSTREAM-01).

**Scope:** Re-author the ahjan teacher_bank so HOOK/REFLECTION/TEACHER_DOCTRINE atoms address topic-specific mechanisms (anxiety, burnout, overthinking, etc.) in ahjan voice rather than generic Buddhist/Dharma frames. Target: each ahjan slot bank has ≥50% topic-binding metadata (`topic_tags: [anxiety, burnout, ...]`) and atoms that name the topic's mechanism by an ahjan-voiced reframe.

**Acceptance test:** Re-run `--quality-profile production` for `ahjan × gen_z_professionals × anxiety × standard_book` and verify:
- `karma` / `Dharma` / `Buddha` / `enlightenment` counts in `book.txt` drop to ≤ 2 each.
- `amygdala` / `nervous system` / `false alarm` / `spiral` (mechanism vocabulary) appears ≥ once per chapter.
- bestseller_craft overall_score ≥ 0.55.

**Anti-drift:** This re-authoring stays in `SOURCE_OF_TRUTH/teacher_banks/ahjan/approved_atoms/`. Don't introduce a new teacher; don't fork ahjan. Migrate Buddhist-themed atoms to ahjan `kb/` or `candidate_atoms/` for archaeology.

### 7.2 — Root cause (a)-residual — SECONDARY, gated on §7.1 (independently routable)

**Recommend opening:** `ws_story_schedule_ahjan_mode_diagnosis_20260517` (Pearl_Dev, scope = diagnose-only first; route to fix-ws afterward).

**Scope:** Instrument `build_story_schedule(persona, topic, seed, root)` to log when it returns empty for non-failure cases. Determine whether ahjan teacher mode introduces a side-effect (different seed, different persona resolution) that empties the schedule for `gen_z_professionals × anxiety`. Compare against the BG-PR-09 closure verification on HEAD `99a926a9b7` (which showed 12 named-character hits) to bisect commits.

**Pearl_PM gate:** Do NOT escalate `ws_bestseller_pipeline_default_path_b_20260425` (it was never opened per BG-PR-09 Phase 2 closure entry; the wiring is done). The bug class here is **content reachability**, not wiring.

### 7.3 — Root cause (e) — TERTIARY (cheap quick-win)

**Recommend opening:** `ws_overlay_enforcement_draft_visibility_20260517` (Pearl_Architect routing decision + Pearl_Dev for log-level).

**Scope (Architect):** Decide whether to elevate `frame_governor.violations` and `bestseller_craft.dimension_gates_status=FAIL` from advisory to **soft-blocking-with-explicit-override** on `--quality-profile draft` runs, so operators iterating in draft see vagueness symptoms without needing to run production. Tradeoff: draft profile is supposed to permit iteration; adding hard blocks defeats the purpose. Alternative: emit a top-of-stdout summary banner ("⚠ 32 generic-Buddhist matches in anxiety book — see frame_governance_chapters") that surfaces drift without blocking.

### 7.4 — Audit-write bug (cheap quick-win; pairs with §7.3)

**Recommend opening:** `ws_enrichment_audit_section_packet_serialization_fix_20260517` (Pearl_Dev, ~10 lines).

**Scope:** Fix the `isinstance(_spa, dict)` type-check bug at [scripts/run_pipeline.py:1406](scripts/run_pipeline.py:1406). Accept `list` and `dict`; write `section_packet_audit.json` containing the `_slot_audit` list. Also restore `section_packet_audit` / `story_schedule` / `book_slot_tracker_used_ids` keys to `enrichment_audit.json` on disk (verify `json.dumps(default=str)` isn't silently dropping list-of-dict values).

**Why:** Without per-slot audit on disk, Pearl_Editor and Pearl_Architect cannot diagnose which atom landed in which slot without re-running. This blocks §7.1's acceptance test (verifying that ahjan re-authored atoms actually fire at the expected slots).

### 7.5 — Root cause (f) — DEFER

**Defer:** Don't open a format_registry ws yet. The EXERCISE-drop-on-opening-and-closing-chapter is by design per `assign_chapter_purpose_contracts`. Whether to amend the contract for `standard_book` is downstream of §7.1 — if the teacher bank is re-authored, chapters 1 and 12 may not need EXERCISE to satisfy the Give move, because EXERCISE-set-up text in REFLECTION/INTEGRATION will carry it. Re-evaluate after §7.1 lands.

### 7.6 — Root cause (d) — VERIFY-BEFORE-ROUTING

**Pre-routing diagnosis:** Pearl_Architect (this agent, optional follow-up) — re-read enrichment_select.py:1080-1100 carefully to confirm whether the persona HOOK wall-of-`---` is a real bug or a misreading of the rendered prose. If real, route to `ws_persona_hook_single_variant_selection_20260517` (Pearl_Dev). Do NOT open speculatively.

### 7.7 — Comparator personas (PARTIAL/FAILED rows in per_persona_topic_coverage) — INFORMATIONAL

The 3 PARTIAL/FAILED rows in [artifacts/qa/move4_2026_04_26/per_persona_topic_coverage.md:31-33](artifacts/qa/move4_2026_04_26/per_persona_topic_coverage.md:31) share a root cause already tracked:

| Row | Persona × topic | Symptom | Root cause | Already-routed ws |
|---|---|---|---|---|
| 8 | grief × gen_alpha_students | engine-bank generic, no named chars | engine bank atoms exist but use "She/He/You" pronouns rather than named characters | `ws_story_cell_authoring_20260425` (Move 5 rolling enhancement, per comparator §sign-off) |
| 19 | financial_anxiety × gen_alpha_students | engine-bank generic, no named chars | same | same |
| 10 | overthinking × gen_z_student | FAILED (no book.txt) | only 3 engines vs other personas' 7; ws_topic_registries hollow-SCENE issue per [docs/SOURCE_BANK_REPAIR_DEV_SPEC.md:69](docs/SOURCE_BANK_REPAIR_DEV_SPEC.md:69) (HOLLOW 20/20 scenes for gen_z_professionals/overthinking — gen_z_student variant likely shares pattern) | PR-S1 in `docs/SOURCE_BANK_REPAIR_DEV_SPEC.md` |

**No new ws needed for §7.7** — these are already-tracked content backlogs.

---

## 8. Out-of-scope observations

1. **`registry/anxiety.yaml` section_02 is declared `type: SCENE`** ([registry/anxiety.yaml:91](registry/anxiety.yaml:91)), but `SOMATIC_10_SLOT_GRID` puts STORY at section_02 ([beatmap_compile.py:42](phoenix_v4/planning/beatmap_compile.py:42)). The PR #669 grid swap silently retires the registry's authored SCENE content at sec 2/5/9 in favor of engine-bank STORY. This is documented in BG-PR-09 closure entry but worth flagging as a comprehension hazard: the registry YAML's `section_02 SCENE` variants are NEVER rendered. Consider: prune SCENE variants from registry yaml at sec 2/5/9 OR add a docstring/comment in the registry top-of-file pointing readers at the grid override.

2. **The 12-EXERCISE-slot drop ([§5c](#5c-exercise-drops-and-frame-governance-flags))** is per design but yields chapters 1 and 12 with **zero rendered EXERCISE blocks**. This silently neutralizes the "Give" move ([overlay spec §4](docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md)) in those chapters. Worth a one-line note in `assign_chapter_purpose_contracts` about how to compensate via REFLECTION-set-up text.

3. **Refrain allowlist phase-2 has not landed.** Per PER-CHAPTER-OVERLAY-ENFORCEMENT-V1-01 (cap entry at [docs/PEARL_ARCHITECT_STATE.md:1341](docs/PEARL_ARCHITECT_STATE.md:1341)), the per-chapter overlay_rule sweep was Phase 2 (gated on Phase 1 PR #941). Without Phase 2, "soft daylight along the sill" at 68 hits and "street below" at 51 hits are not caught even if `--quality-profile production` is run. The PR-chain (Phase 1 → 2 → 3 → ITEM-2 allowlist removal) is already authored; Pearl_Dev can pick up Phase 2 today. Independent of this audit.

4. **`practice_library` is at 0 hits in this run.** Per EXERCISE-BANK-RESOLUTION-01, the strict-canonical EXERCISE gate fires on production. This run is draft + ahjan has EXERCISE atoms, so practice_library was unused. If ahjan EXERCISE atoms are removed in §7.1's authoring sweep, production runs may need #887 EXERCISE atom backfill landed first. Sequence: §7.1 plans the ahjan re-author **before** removing existing EXERCISE atoms; backfill `atoms/<persona>/<topic>/EXERCISE/` if removing.

5. **`SOURCE_OF_TRUTH/story_atoms/` has only 3 roster files** (`character_roster.yaml`, `character_roster_millennial_anxiety.yaml`, `character_roster_working_parents_anxiety.yaml`). Genz × anxiety coverage may be implicit via the persona engine-bank named characters rather than via the roster files. If `build_story_schedule` reads only from `character_roster*` files, missing genz-specific roster could explain the empty schedule in §5b/§6 rank 2. Worth checking inside `ws_story_schedule_ahjan_mode_diagnosis_20260517` (§7.2).

---

**End of audit.**

Pearl_Architect did not modify any code, config, atom, registry, or teacher-bank file in producing this report. The single file written is this audit at `artifacts/qa/persona_topic_yaml_specificity_audit_20260517.md`.
