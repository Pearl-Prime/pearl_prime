# M6 Blind-10 — Blockers (live audit 2026-07-08)

**Verified HEAD:** `2ca947a9fa85a9793f3f097cf10bfdcf5ef31f66` (origin/main)

---

## Machine blocker list

```
M6-BLK-001  M5_INSUFFICIENT_RENDERS
M6-BLK-002  JUDGES_NOT_RECRUITED
M6-BLK-003  PEARL_STAR_GPU_QUEUE
M6-BLK-004  COMPARATOR_ASSETS_PENDING
M6-BLK-005  SLOT_02_BYTE_GATE
```

---

## M6-BLK-001 — M5 insufficient renders (HARD)

**Blocks:** Full blind-10 human run (slots 02–10); slot_01 human packet discouraged until M5 upgrade.

**Evidence:**
- `CANDIDATE_SET.tsv`: 1/10 `prescreen_only`, 1/10 partial M5 (byte gate), 2/10 INTERIM wiring proofs, 6/10 ABSENT
- Closeout handoff: 2 image banks, pilot PuLID only
- `demo_alarm_metaphor_6p` is 6-panel excerpt with INTERIM layers — not blind-10 eligible

**Unblock:** M5 delivers ≥ 8 end-to-end assembled episodes (0 INTERIM, byte floor) across ≥ 4 genres per roadmap §6.

---

## M6-BLK-002 — Judges not recruited (HARD)

**Blocks:** Any PROVEN-AT-BAR claim; human scoring.

**Requirement:** ≥ 3 manga professionals per locale lane (JP-native for ja_JP). Operator-tier per roadmap.

**Sourcing lane:** `ready_to_recruit` — outreach **drafted, not sent**; `JUDGE_OUTREACH_SEND_CHECKLIST.md` landed 2026-07-08. Zero judges confirmed.

**Unblock:** Operator sends outreach to 8–10 prospects; log ≥ 3 confirmed in `SOURCING_TRACKER.yaml` → `judges.recruited[]`.

---

## M6-BLK-003 — Pearl Star GPU queue (SOFT — pre-screen + M5)

**Blocks:** M5 bank renders at scale; Qwen2.5-VL pre-screen if Ollama offline.

**Reference:** PR #3075 dispatch-bug lane; closeout handoff.

**Unblock:** Pearl Star ComfyUI + Ollama online; queue dispatch fixed.

---

## M6-BLK-004 — Comparator assets pending (SOFT — human packet)

**Blocks:** Judge packet distribution for slots needing comparators.

**Evidence:** `validate_manga_blind10_comparators.py --require-p0` → exit 1; `acquired: 0`; 2 missing_p0 errors. `comparators/` has README + manifest only — no PDFs.

**Sourcing lane:** `ready_to_source` — `COMPARATOR_SCAN_DELIVERY_CHECKLIST.md` landed 2026-07-08. P0 pilot: Yotsuba&! + Barakamon (slot 01).

**Unblock:** Operator acquires licensed scans per checklist; record sha256 in registry; validator exit 0.

---

## M6-BLK-005 — Slot_02 byte gate (SOFT — M5 upgrade path)

**Blocks:** Using `ep_001_from_continuity` (0-INTERIM M5 assembly) for human blind-10 instead of legacy v3.

**Evidence:** `assembled/ep_001_from_continuity/` — 35 panels, `layers_interim: 0`, but `ep001_029.png` = **12,741 bytes** (floor 99,690). 34/35 panels pass.

**Unblock:** Re-render or re-export ep001_029 ≥ 99,690 bytes; update `CANDIDATE_SET.tsv` slot 02 → `blind10_eligible: prescreen_only` or `yes`.

---

## What is NOT blocked

- Protocol ratification (this artifact set)
- Slot_01 Qwen2.5-VL pre-screen (when Pearl Star online) — legacy `composed_v3_qwen`
- Judge recruitment outreach prep (`JUDGE_OUTREACH_SEND_CHECKLIST.md` — send is operator action)
- Comparator sourcing prep (`COMPARATOR_SCAN_DELIVERY_CHECKLIST.md` — scan is operator action)
- Pilot scheduling lane (`BLIND10_SCHEDULING_MEMO.md`)
