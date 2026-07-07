# M6 Blind-10 — Blockers (live audit 2026-07-08)

**Verified HEAD:** `6e44f414335c4faa3ba63642dce0c7beb962f69e`

---

## Machine blocker list

```
M6-BLK-001  M5_INSUFFICIENT_RENDERS
M6-BLK-002  JUDGES_NOT_RECRUITED
M6-BLK-003  PEARL_STAR_GPU_QUEUE
M6-BLK-004  COMPARATOR_ASSETS_PENDING
```

---

## M6-BLK-001 — M5 insufficient renders (HARD)

**Blocks:** Full blind-10 human run (slots 02–10); slot_01 human packet discouraged until M5 upgrade.

**Evidence:**
- `CANDIDATE_SET.tsv`: 1/10 `prescreen_only`, 2/10 INTERIM wiring proofs, 7/10 ABSENT
- Closeout handoff: 2 image banks, pilot PuLID only, no full 35-panel M5-assembled ep_001 at 0 INTERIM
- `demo_alarm_metaphor_6p` is 6-panel excerpt with INTERIM layers — not blind-10 eligible

**Unblock:** M5 delivers ≥ 4 end-to-end assembled episodes (0 INTERIM) across ≥ 4 genres per roadmap §6.

---

## M6-BLK-002 — Judges not recruited (HARD)

**Blocks:** Any PROVEN-AT-BAR claim; human scoring.

**Requirement:** ≥ 3 manga professionals per locale lane (JP-native for ja_JP). Operator-tier per roadmap.

**Unblock:** Operator recruits and schedules blind review sessions.

---

## M6-BLK-003 — Pearl Star GPU queue (SOFT — pre-screen + M5)

**Blocks:** M5 bank renders at scale; Qwen2.5-VL pre-screen if Ollama offline.

**Reference:** PR #3075 dispatch-bug lane; closeout handoff.

**Unblock:** Pearl Star ComfyUI + Ollama online; queue dispatch fixed.

---

## M6-BLK-004 — Comparator assets pending (SOFT — human packet)

**Blocks:** Judge packet distribution for slots needing comparators.

**Evidence:** `COMPARATOR_REGISTRY.yaml` → all `asset_status: PENDING_OPERATOR_SCAN`

**Unblock:** Operator sources licensed scans per registry; record sha256.

---

## What is NOT blocked

- Protocol ratification (this artifact set)
- Slot_01 Qwen2.5-VL pre-screen (when Pearl Star online)
- Judge recruitment outreach (parallel)
- Comparator sourcing (parallel)
