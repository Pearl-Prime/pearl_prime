# M6 Blind-10 — Blockers (live audit 2026-07-08)

**Verified HEAD:** `ba9ab86e6` (#4740 merged — ep001_029 byte gate fix)

---

## Machine blocker list

```
M6-BLK-001  M5_INSUFFICIENT_RENDERS
M6-BLK-002  JUDGES_NOT_RECRUITED
M6-BLK-003  PEARL_STAR_GPU_QUEUE          (SOFT — Ollama online; pre-screen in flight)
M6-BLK-004  COMPARATOR_ASSETS_PENDING     (SOFT — pilot CLEARED; full 18 pending)
M6-BLK-005  SLOT_02_BYTE_GATE             # CLEARED 2026-07-08 (#4740)
```

---

## M6-BLK-001 — M5 insufficient renders (HARD)

**Blocks:** Full blind-10 human run (slots 03–10); slot_01 human packet discouraged until M5 upgrade.

**Evidence:**
- `CANDIDATE_SET.tsv`: 2/10 `prescreen_only`, 2/10 INTERIM wiring proofs, 6/10 ABSENT (script-only)
- Closeout handoff: 2 image banks, pilot PuLID only
- `demo_alarm_metaphor_6p` is 6-panel excerpt with INTERIM layers — not blind-10 eligible

**Unblock:** M5 delivers ≥ 8 end-to-end assembled episodes (0 INTERIM, byte floor) across ≥ 4 genres per roadmap §6.

---

## M6-BLK-002 — Judges not recruited (HARD)

**Blocks:** Any PROVEN-AT-BAR claim; human scoring.

**Requirement:** ≥ 3 manga professionals per locale lane (JP-native for ja_JP). Operator-tier per roadmap.

**Sourcing lane:** `ready_to_recruit` — outreach **drafted, not sent**; `JUDGE_PROSPECT_LIST_SLOT_01.md` landed 2026-07-08. Zero judges confirmed.

**Unblock:** Operator sends outreach to 8–10 prospects; log ≥ 3 confirmed in `SOURCING_TRACKER.yaml` → `judges.recruited[]`.

---

## M6-BLK-003 — Pearl Star GPU queue (SOFT — pre-screen + M5)

**Blocks:** M5 bank renders at scale; Qwen2.5-VL pre-screen if Ollama offline.

**Evidence (2026-07-08 live check):** Tailscale Ollama at `pearlstar.tail7fd910.ts.net:11434` → HTTP 200; models include `qwen2.5vl:7b`, `gemma3:27b`. Slot_01 pre-screen **in flight** via `run_frame_judge.py --judge-only`.

**Remaining risk:** PR #3075 ComfyUI dispatch-bug lane still OPEN — blocks M5 scale renders, not current pre-screen.

**Unblock (M5 scale):** Pearl Star ComfyUI queue dispatch fixed; merge #3075.

---

## M6-BLK-004 — Comparator assets pending (SOFT — pilot subset CLEARED)

**Blocks:** Judge packet distribution for slots needing comparators.

**Pilot P0 status (2026-07-08):**
- `yotsuba_v1_ch1_pages_5-8.pdf` — **ACQUIRED** (2,147,398 B, sha256 `748ad17e…`)
- `barakamon_v1_ch1_pages_6-10.pdf` — **ACQUIRED** (2,279,981 B, sha256 `074a1f95…`)
- `validate_manga_blind10_comparators.py --require-p0` → **exit 0**, `pilot_ready: true`, `acquired: 2`
- Acquisition method: `OFFICIAL_PREVIEW` (licensed retail preview pages)

**Full blind-10:** 18 comparators still `PENDING_OPERATOR_SCAN` (slots 02–10).

**Unblock (full):** Operator acquires remaining 18 licensed scans per checklist; record sha256 in registry.

---

## M6-BLK-005 — Slot_02 byte gate — **CLEARED** (2026-07-08)

**Was:** `ep001_029.png` = 12,741 bytes (floor 99,690).

**Post-#4740 truth:** `ep_001_from_continuity` — **35/35** panels pass byte gate; ep001_029 reassembled at 2,093,369 B after manifest `shot_type: establishing` fix.

**Current status:** slot_02 → `prescreen_only` in `CANDIDATE_SET.tsv`; eligible for pre-screen when Pearl Star online.

---

## What is NOT blocked

- Protocol ratification (this artifact set)
- **P0 comparator pilot subset** (slot_01 Yotsuba + Barakamon — validated)
- Slot_01 / slot_02 Qwen2.5-VL pre-screen (when Pearl Star online)
- Judge recruitment outreach prep (`JUDGE_PROSPECT_LIST_SLOT_01.md` — send is operator action)
- Comparator sourcing for slots 02–10 (`COMPARATOR_SCAN_DELIVERY_CHECKLIST.md`)
- Pilot scheduling lane (`BLIND10_SCHEDULING_MEMO.md`)
