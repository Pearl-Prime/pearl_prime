# Manga PassB Bar Packet — V1 Spec

**Status:** SPECCED (gt30d C02 · 2026-07-22)  
**Keepers:** I043, I029  
**Owner:** Pearl_Architect (Claude) → Cursor D07 implements lettering/proof hooks  
**Acceptance layer for this doc:** SPECCED — bar packet not EXECUTED-REAL

## 0. Purpose

Define the **proof packet** required before claiming PassB bar progress:
reading-graph, spread layout solver, JLREQ/SFX lettering. Doctrine may exist on main;
implementation + proof-wave prerequisites must not be faked.

Source signal: `old_chat_specs/Untitled 362.txt` (BLOCKED — bar packet not assembled).

## 1. Packet contents (must all exist to claim CODE-WIRED)

| Component | Proof artifact | Notes |
|---|---|---|
| reading_graph | Machine-readable graph + one pilot episode walk | No fake merge SHAs |
| spread_layout | Solver output for ≥1 spread | Label INTERIM if stand-in |
| jlreq_sfx_lettering | Lettering/bubble V2 path proof | Ties to I029 / webtoon lettering |
| bar_checklist | TSV/MD listing PASS/FAIL per component | Human-auditable |

## 2. Acceptance layers

- **SPECCED:** this document.
- **CODE-WIRED:** Cursor D07 hooks exist and are imported by a non-test consumer OR declared `status: unwired` with reason.
- **EXECUTED-REAL:** byte-verified panels + lettering on a real episode (not stubs).
- **PROVEN-AT-BAR:** blind-judged sample (nothing is, today — do not claim).

## 3. Cursor D07 checklist (lettering + proof hooks)

1. [ ] Confirm existing `scripts/manga/` lettering/compositing surfaces; extend, do not fork.
2. [ ] Emit bar checklist path under `artifacts/qa/` for one pilot.
3. [ ] Stop at first systemic blocker; record BLOCKED with evidence.
4. [ ] Never mark RENDER_PROGRESS ok/done under 50_000 bytes.
5. [ ] JLREQ/SFX: pilot only; no catalog fanout in this lane.

## 4. Explicitly not claimed

Cloud/Codespaces substrate fanout (I044) remains OPERATOR_GATE — out of this pack.

## 5. Signal

`gt30d-c02-spec-terminal` when this file lands.
