# Lane 04 — Blind-Judge Packet (first PROVEN-AT-BAR attempt for social)

~~~text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_QA for Phoenix Omega.

Repo: Pearl-Prime/pearl_prime. Substrate: fresh branch off latest origin/main
(agent/social-blind10-packet-20260724). Explicit-path staging; poison protocol.

STARTUP_RECEIPT:
- AGENT=Pearl_QA
- LANE=social_blind10_packet_20260724
- EXECUTION_MODE=local_fallback ; BACKGROUND_SAFE=yes
- PERSISTENCE_SURFACES=branch/PR/operator-read-packet
- RESUME_SURFACE=artifacts/coordination/handoffs/social_blind10_packet_2026-07-24.md

READ FIRST:
- docs/PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md (the Layer-4 blind-read precedent — mirror
  its method, do not reinvent)
- docs/PEARL_SOCIAL_MEDIA_WRITER_AGENT_SPEC_2026-07-18.md (the bar being judged)
- artifacts/qa/social_variety_repair_20260724/ (Lane 03's AFTER set — the candidates)

PRE-REQUISITE CHECKS:
- social-variety-repair-landed=<sha> exists (Lane 03 merged). Missing → STOP, BLOCKED.
- Q-SOCIAL-BLIND10-READ-01 ratified by operator (dispatcher's batch). Missing → build the packet
  anyway, mark BLOCKED-ON-OPERATOR-READ at the end (packet ready ≠ read done — never conflate).

LIVE STATE RECONCILIATION: fetch; confirm Lane 03's regenerated pilot set is on main; re-verify both
gates green on it.

DISCOVERY REPORT before action: current SHA; candidate post inventory; control-set sourcing plan.

PROVENANCE:
- research: docs/social_media_YT4.txt (what platform-native strong content looks like) + the
  bestseller Layer-4 method
- documents: acceptance scorecard doc; SOCIAL_MEDIA_100PCT plan (names the missing PROVEN-AT-BAR)
- builds_on: Layer-4 blind-read protocol (bestseller precedent); operator_read_packets convention
- inventory: EXTENDS (new packet artifacts only; no code)

MISSION (narrow): produce the subsystem's first blind-judgeable packet:
1. Select 10 repaired posts (Lane 03 AFTER set) spanning ≥4 platforms × ≥5 topics.
2. Assemble 10 CONTROL posts: strong platform-native exemplars in the same niches, drawn from the
   tracked research corpus (templates/examples quoted inside the committed research docs). License
   discipline: controls are for private operator comparison inside the packet — quote minimally,
   cite source doc + line, never redistribute externally.
3. Shuffle-blind the 20 into a read packet (IDs only, key sealed in a separate file):
   artifacts/operator_read_packets/social_blind10_20260724/{packet.md,sealed_key.json,scoring_sheet.tsv}
   Scoring sheet per post: would-stop-scroll (1–5), reads-native-vs-template (1–5), would-save/share
   (1–5), identifiable-template-smell (free text).
4. Pre-screen pass (agent, non-binding): run both wired gates + record your own blinded scores in a
   SEPARATE file not shown to the operator before their read.
5. `open artifacts/operator_read_packets/social_blind10_20260724/packet.md` as the last step —
   operator review is the deliverable trigger.

DELIVERABLES: the packet dir (committed); handoff; PR.

SMALLEST SAFE BATCH: smoke = 2+2 mini-packet renders correctly blinded; pilot/scale = full 10+10.

HANG PREVENTION: standard 2/3 polling rules; max window 3 h.

TESTS/PROOFS: blinding integrity check (no candidate/control label leakage in packet.md — grep for
source paths in the packet body); gate verdicts attached; sealed key verifiable.

DO NOT: score on the operator's behalf and report a Layer-4 verdict — ONLY the operator's read is
Layer 4; do not include any UN-tracked external content in the packet; do not touch coordination
hot files.

LANDING CONTRACT: MERGED (packet PR squash-merged + signal + `open` command run) or BLOCKED.
Note: MERGED here means the PACKET landed. The Layer-4 verdict lands later as an OPD row +
golden-freeze of approved posts (sidebar-parity pattern) — name that as NEXT_ACTION.

CLEANUP LEDGER + HANDOFF: artifacts/coordination/handoffs/social_blind10_packet_2026-07-24.md

CLOSEOUT_RECEIPT: standard fields + full MERGE_SHA.
SIGNAL: social-blind10-packet-ready=<full merge SHA>
ACCEPTANCE LAYER: packet = EXECUTED-REAL. PROVEN-AT-BAR only after operator read approves ≥
threshold; if approved, NEXT_ACTION = freeze approved posts as goldens + wire parity gate
(enforcement-promotion rule).
~~~
