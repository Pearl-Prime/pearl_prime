# M6 Blind-10 — Operator Memo (go / no-go)

**Date:** 2026-07-08 · **Run ID:** `manga_blind10_2026-07-08`
**Layer:** SPECCED (protocol landed) — **PROVEN-AT-BAR:** none

---

## What this is

The R7 pro-bar acceptance lane. Analogous to Pearl Prime Layer 4 blind-10, but for
**manga episodes** judged by human manga professionals against published comparators.

M6 does **not** unblock M5, M7, or catalog ship claims by itself.

---

## Live truth (verified 2026-07-08)

| Check | Result |
|---|---|
| `manga_blind10_*` artifacts | **Present** (this folder — protocol only) |
| Full blind-10 judge run | **NOT_RUN** |
| Episodes render-ready for human packet | **1 / 10** (stillness ep_001 legacy) |
| M5 E2E assembled episodes (0 INTERIM) | **0** |
| PROVEN-AT-BAR manga | **0** |

---

## Go / no-go checklist

### Phase A — Pre-screen only (can start when Pearl Star online)

- [ ] Pearl Star Ollama reachable (`qwen2.5vl:7b` loaded)
- [ ] Run `pre_screen/PRESCREEN_RUNBOOK.md` on **slot_01** (stillness ep_001)
- [ ] Pre-screen JSON archived under `pre_screen/`
- [ ] **Do not** claim PROVEN-AT-BAR after pre-screen alone

### Phase B — Full blind-10 (all must be true)

- [ ] **≥ 10** full episodes pass byte + provenance gates (see `CANDIDATE_SET.tsv`)
- [ ] **≥ 4 genres** represented in the 10 slots
- [ ] **≥ 3** human judges recruited per locale lane (JP-native for ja_JP)
- [ ] Comparator scans sourced and logged in `COMPARATOR_REGISTRY.yaml`
- [ ] Judge packets built per `judge_packets/*/PACKET.md`
- [ ] Judges score blind; scorecards filed under `scorecards/`
- [ ] `VERDICT.md` updated with PASS/WARN/FAIL

---

## Recommended dispatch order

```
1. Unblock M5 (Pearl Star #3075, bank renders, 0-INTERIM assembly) for slots 02–05
2. Pre-screen slot_01 on Pearl Star (pilot)
3. Recruit judges (operator-tier — parallel)
4. When slots 02–10 flip to render_ready=yes → assemble judge packets
5. Run blind-10 → emit VERDICT.md
```

---

## One-liner blockers

1. **M5:** only 1 legacy full render; no M5 bank-assembled episode at 0 INTERIM
2. **Judges:** not recruited (operator-tier)
3. **Pearl Star:** GPU queue #3075 still open per closeout handoff

See `BLOCKERS.md` for machine-readable blocker IDs.

---

## Key paths

| Artifact | Path |
|---|---|
| Protocol | `artifacts/qa/manga_blind10_2026-07-08/PROTOCOL.md` |
| Candidate queue | `artifacts/qa/manga_blind10_2026-07-08/CANDIDATE_SET.tsv` |
| Slot 01 pilot packet | `artifacts/qa/manga_blind10_2026-07-08/judge_packets/slot_01_stillness_ep001/` |
| Pre-screen | `artifacts/qa/manga_blind10_2026-07-08/pre_screen/PRESCREEN_RUNBOOK.md` |
