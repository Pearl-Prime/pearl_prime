# Qwen2.5-VL pre-screen runbook (Tier 2)

**Role:** Filter obvious panel failures **before** human judge recruitment.
**Does NOT confer PROVEN-AT-BAR.**

---

## Preconditions

- Pearl Star (or local dev box) with Ollama serving `qwen2.5vl:7b`
- Candidate episode has `blind10_eligible` = `prescreen_only` or `yes` in `CANDIDATE_SET.tsv`
- Chapter script YAML with per-panel `scene_description` or equivalent visual text

---

## Slot 01 command (stillness ep_001)

From repo root:

```bash
# Verify Ollama model
ollama list | grep -i qwen2.5vl

# Build beats manifest (panel image + scene text from chapter script)
PYTHONPATH=. python3 artifacts/qa/manga_blind10_2026-07-08/pre_screen/build_prescreen_items.py \
  --slot 01 \
  --output artifacts/qa/manga_blind10_2026-07-08/pre_screen/slot_01_beats.json

# Run vision judge (Tier 2 — local Ollama only; judge-only, no re-render)
PYTHONPATH=. python3 scripts/video/run_frame_judge.py \
  --frames-dir artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/composed_v3_qwen \
  --beats artifacts/qa/manga_blind10_2026-07-08/pre_screen/slot_01_beats.json \
  --text-key scene_description \
  --threshold 80 \
  --judge-model qwen2.5vl:7b \
  --judge-only \
  --report-out artifacts/qa/manga_blind10_2026-07-08/pre_screen/slot_01_prescreen_results.json
```

---

## Pass / withhold rule

| Metric | Advance to human judges? |
|---|---|
| Episode panel median score ≥ **75** | Yes (subject to M5 0-INTERIM gate for full blind-10) |
| Any panel score < **50** on ≥ 3 panels | **Withhold** — fix render lane first |
| Median < **75** | **Withhold** — file results, do not spend judge time |

Archive JSON under `pre_screen/`. Reference harness: `scripts/video/run_frame_judge.py` (Tier policy in module docstring).

---

## Tier policy

- **Qwen2.5-VL:** Tier 2 (Pearl Star / Ollama) — unattended OK
- **Human blind-10:** Operator-present pros only
- **Paid vision APIs:** BANNED
