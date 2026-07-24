# Lane 02 — Pearl_Research — Wan video capability truth (cloud free tier + self-hosted 16GB)

EXECUTE. Research lane with a MERGED deliverable — not a chat answer. The turn ends only on
`manga-video-capability-research-merged=<full merge SHA>` or one concrete BLOCKER with pushed work.

STARTUP_RECEIPT: AGENT=Pearl_Research, SUBSYSTEM=manga_pipeline (research feed),
WRITE_SCOPE=`docs/research/MANGA_VIDEO_POSE_BANK_CAPABILITY_RESEARCH_2026-07-24.md` (NEW) +
`artifacts/research/manga_video_pose_bank_2026-07-24/` (evidence) + handoff. OUT_OF_SCOPE=all
code, all configs, all governance files. PROVENANCE: research=this lane produces it;
documents=`docs/VIDEO_PIPELINE_DEEP_RESEARCH_V2.md` (2026-04-12, quant-era stale),
`docs/research/QWEN_MODELSTUDIO_FREE_TIER_SOCIAL_RECON_2026-07-19.md`,
`artifacts/research/animation_production_techniques_2026_04_04.md`; builds_on=those three
(EXTEND with a 2026-07 refresh — do not re-derive what they already verified); inventory=UNCHANGED.

## Read first
The three prior research docs above; `artifacts/research/dashscope_free_media_2026-07-19/REPORT.md`;
`docs/MANGA_V5_COMPUTE_SCALING_OPTIONS.md` (Pearl Star empirical truth: RTX 5070 Ti 16GB, 64GB RAM,
Qwen-Image-Layered peaks 10.76GB, ~25min/panel — the GPU is already the manga bottleneck);
`docs/ROBUST_AGENT_PROTOCOL.md`; `old_chat_specs/Untitled 411.txt` (the operator's method research —
treat its model claims as LEADS to verify, not truth).

## Mission — answer these with sourced, dated evidence (web research required)

**A. Cloud free-tier truth (feeds Lane 04/05 directly):**
1. `wan2.7-r2v-2026-06-12` — does it have a real free-quota bucket on the Singapore intl endpoint
   (the 07-19 recon lists it; the free-media REPORT's table shows r2v only under happyhorse at
   10s)? Exact seconds, API request shape (reference video/images input format), and whether the
   existing exempt client could gain it by in-place extension (same async endpoint family?).
2. First/last-frame conditioning and video-continuation on wan2.7 free tier — available? Request
   fields? (The attached method research leans on continuation; the current client has none.)
3. Per-model still buckets usable for anchor/turnaround work (wan2.1-t2i-plus/turbo 200, wan2.2-t2i
   100, qwen-image ~100) — confirm current numbers + the 90-day window + 2026-10-18 expiry.
4. i2v-from-uploaded-image mechanics: can i2v take an EXTERNAL image URL / base64 (our canonical
   anchor rendered on Pearl Star), not just a DashScope-hosted still URL? This is the load-bearing
   consistency mechanism — verify precisely.

**B. Self-hosted scale path on Pearl Star (16GB 5070 Ti, torch 2.11/cu130):**
5. 2026-era Wan open-weights on 16GB: Wan 2.1 1.3B (fp16/fp8), Wan 2.2 5B, 14B via fp8/GGUF
   quants or Wan2GP — VRAM, s/clip throughput at 480–720p, ComfyUI-native vs wrapper. The 04-12
   research's "65–80GB not viable" verdict predates common quants — refresh it.
6. **VACE** (Wan's open reference/control framework) — the open-weights analog of r2v: does it do
   reference-image identity conditioning + pose/motion control on 16GB? License?
7. Alternatives at 16GB for identity-consistent character motion: LTX-Video 2.3 (the 04-12 pick),
   FLUX.1-Kontext (identity editing, stills), AnimateDiff-class. One paragraph each, licenses.
8. Queue-contention estimate: seconds-of-video/day realistically available WITHOUT starving the
   ~25min/panel manga render queue (RAP: everything queue-first via pscli).
9. License → provenance mapping: confirm Wan/VACE weights are Apache-2.0 (or state actual terms)
   → REAL-eligible under the layer contract; note any model whose license would force INTERIM.

**C. Method evidence (feeds the Lane 03 spec):**
10. Cross-clip identity: same-anchor i2v vs r2v/VACE-reference vs per-clip t2v — what does public
    evidence (papers, Alibaba docs, credible community tests) say about drift? Note the attached
    research's claims that survive verification and the ones that don't.
11. Capture-program design: comic-readable key poses (anticipation/impact/follow-through) over
    natural motion; frames-per-clip worth extracting (candidate sampling rates); known failure
    modes (hands, occlusion-reveal hallucination on head turns, clothing mutation across cuts).

**Deliverable:** the research doc with a **decision matrix** (pilot engine = cloud free quota;
scale engine = ranked self-hosted candidates with VRAM/throughput/license columns) + a
`RECOMMENDATIONS` section Lane 03 can cite line-by-line + per-claim source URLs and dates.
Evidence dumps under the artifacts dir. DISCOVERY REPORT before writing; smoke→pilot→scale =
outline → 3 hardest questions (1, 5, 6) → full doc.

## DO NOT
- Do not call any DashScope endpoint (this lane is read/web-only; quota spend is Lane 05's).
- Do not install anything on Pearl Star.
- Do not re-author the 04-12 or 07-19 research — extend, cite, and mark superseded claims inline
  in YOUR doc (never edit theirs beyond a one-line pointer banner if a claim is now provably wrong).

## Landing contract
MERGED (docs-only PR via plumbing pattern off `origin/main^{tree}`; staged-diff gate; required
checks named) or BLOCKED with pushed branch. Cleanup ledger. Handoff:
`artifacts/coordination/handoffs/manga_video_pose_bank_lane02_2026-07-24.md`.
CLOSEOUT_RECEIPT + `SIGNAL: manga-video-capability-research-merged=<full merge SHA>`.
