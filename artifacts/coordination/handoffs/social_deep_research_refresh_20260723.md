# Social deep research refresh — 2026-07-23

**Agent:** Pearl_Research · **Lane:** `social-writer-lane-a-research-20260723` ·
**Project:** `proj_social_atom_bank_vibe_20260721` · **Subsystem:** `social_media`

**Status:** RESEARCHED (research layer only — see acceptance-layer note below). No atom content was
authored in this lane; this is the research Lane C (atom authoring) must cite before writing
MICRO_STORY, CASE_PROOF, CAROUSEL_SLIDE, THREAD_UNIT, or VIDEO_BEAT atoms, and before touching the
existing HOOK_COVER/CTA_ANCHOR families' hashtag/CTA assumptions.

## Why this lane ran

A live content audit found assembled social posts read as generic and dead. Root cause named by the
operator: the atom bank's populated families are template-generated abstractions with no concrete
story or proof content behind them, and MICRO_STORY/CASE_PROOF have zero rows. This lane's mission
was to produce genuinely current, cited platform research to close that gap before Lane C writes
another atom.

## What this lane found (read the digest for full detail — this is the short version)

1. **The gap is five families wide, not two.** `MICRO_STORY`, `CASE_PROOF`, `CAROUSEL_SLIDE`,
   `THREAD_UNIT`, and `VIDEO_BEAT` all have **zero rows** across all three SOURCE_OF_TRUTH atom files
   (1,686 + 250 + 60 = 1,996 total rows, none in these five families).
2. **The pilot posts confirm the diagnosis with hard numbers**: 20 pilot posts average 7.5
   hashtags/post (range 5–10), use only **2 unique CTAs** and **5 unique opening hooks** total across
   all 20 posts, and one live example shows the persona slug leaking into the sentence as raw
   metadata ("corporate managers: more discipline will fix exhaustion is not the whole story").
3. **This lane's own AUTHORITY_DOCS were misdiagnosed as missing, then found — correction logged
   in-band, not silently.** A first-pass `git`-only search correctly found all four named research
   docs absent from `origin/main`, but they turned out to exist as real, substantial, already-authored
   files on the local disk of the main checkout, never `git add`ed. A fifth file
   (`docs/research_social_media.txt`, already quote-cited by 22 live atom rows per
   `docs/specs/SOCIAL_MEDIA_100PCT_PRODUCTION_PLAN_2026-07-22.md`) was also found this way. **These
   docs are good and contain directly usable MICRO_STORY/CASE_PROOF/VIDEO_BEAT seed material already**
   — the fix is landing them (one agent-turn, per two independent lanes' sizing), not re-authoring
   them. See digest §0 and R1.
4. **Instagram hashtags are the sharpest confirmed 2026 drift**: platform-enforced hard cap of 5
   hashtags since 2025-12-19 (Instagram's own @Creators account, cited). Our `config/social/
   platform_specs.yaml` allows up to 15 for Instagram surfaces — wrong against both the live platform
   change and our own already-authored (untracked) research, which independently said 3–5 before the
   platform change happened. LinkedIn/TikTok/Threads config ranges are already correct; no change
   needed there.
5. **APAC refresh, native-speaker-validated.** Ran fresh research per market (Japan, Taiwan, Korea,
   Mainland China, Hong Kong, Singapore), then had all six independently reviewed by
   `translate-ja`/`translate-ko`/`translate-zh-cn`/`translate-zh-hk`/`translate-zh-sg`/`translate-zh-tw`
   subagents for cultural/linguistic accuracy. Real corrections surfaced per market (e.g., Korea's
   "group harmony" framing is dated for 2026 wellness content; Hong Kong's code-switching model was
   wrong-shaped — real HK code-switching is intra-sentential, not alternating full sentences;
   Singapore's Xiaohongshu framing overstated reach — it's a diaspora/beauty-luxury niche channel
   there, not a mainstream wellness surface; Taiwan needs a hard simplified→traditional lexical
   substitution checklist). This directly replaces the gap named in
   `docs/specs/SOCIAL_MEDIA_100PCT_PRODUCTION_PLAN_2026-07-22.md` gap-item 5 (APAC native-review
   evidence was previously one operator chat-level assertion, not per-market reviewer sign-off) — for
   the 6 markets this refresh covered. It does not by itself satisfy that plan's demand for **per-row**
   (60-row) sign-off on the existing `apac_localization_atoms.jsonl` — this refresh is market-level
   validation of fresh research claims, not a row-by-row audit of the existing promoted atoms. Full
   unedited reviewer replies are in `NATIVE_SPEAKER_VALIDATION_20260723.md` alongside the digest.

## Deliverables (this lane's write scope only)

- `artifacts/social_media_atoms/pearl_social_media_writer_20260723/deep_research_digest_20260723.md`
  — main digest: discovery report, platform-by-platform findings (§1), MICRO_STORY seeds (§2),
  CASE_PROOF seeds (§3), VIDEO_BEAT/CAROUSEL_SLIDE/THREAD_UNIT structure (§4), APAC refresh (§5),
  verified-cited vs. general-knowledge-uncited findings summary (§6), retire/update recommendations
  (§7), named operator question (§8), sources.
- `artifacts/social_media_atoms/pearl_social_media_writer_20260723/trend_pattern_delta_bank_20260723.md`
  — compact, copy-usable pattern extraction for Lane C (platform deltas, CTA variety categories,
  MICRO_STORY/CASE_PROOF shapes, CAROUSEL_SLIDE structural gap, per-market voice-correction table).
- `artifacts/social_media_atoms/pearl_social_media_writer_20260723/NATIVE_SPEAKER_VALIDATION_20260723.md`
  — full unedited replies from all six native-speaker subagent reviews.
- This handoff.

## What Lane C (atom authoring) must do with this

1. **Cite `deep_research_digest_20260723.md` directly** for any MICRO_STORY, CASE_PROOF,
   CAROUSEL_SLIDE, THREAD_UNIT, or VIDEO_BEAT atom authored from here forward — these five families
   currently have zero rows and are this lane's primary reason for existing.
2. **Pull MICRO_STORY/CASE_PROOF seed material from `docs/research_social_media.txt` first**
   (line ranges cited in digest §2/§3) — it is richer and more directly usable than this lane's own
   web-research synthesis, which is offered only as a secondary/fallback shape.
3. **Do not seed any new HOOK_COVER/CTA_ANCHOR rows with more than 5 hashtags for Instagram
   surfaces**, and diversify CTA_ANCHOR beyond the 2 currently-used lines — see the delta bank's CTA
   variety categories.
4. **Apply the per-market APAC voice corrections table** (delta bank) to any new
   LOCALIZATION_ADAPTER rows, especially the Korea "group harmony" retirement, the Hong Kong
   intra-sentential code-switching correction, and the Taiwan simplified→traditional lexical
   checklist.
5. **Do not treat this refresh as replacing the rakuten/quen docs** — it extends and, in specific
   places, corrects them (see digest §5 per-market subsections); the originals remain valid where not
   explicitly flagged.

## Not this lane's job (flagged, not fixed here)

- Landing the 5 untracked-local docs to `origin/main` (R1) — Pearl_GitHub / whoever owns `docs/`
  outside this lane's write scope.
- Editing `config/social/platform_specs.yaml`'s Instagram hashtag range (R2) — outside this lane's
  write scope and sparse-checkout cone.
- Editing the spec's Platform Rules one-liners for Korea/Hong Kong (R4) or adding a carousel-arc
  metadata field (R5) — spec-owner decisions.
- Any atom authoring at all — that is explicitly Lane C's job, not this lane's.

## Named operator question (see digest §8 for full reasoning)

Does the pipeline need a native/live-video format, or does composited text+B-roll+ambient-audio
fully cover the "alive vs dead" gap for short-form video? **Recommended default: no new format
needed** — every cited 2026 best-practice source for faceless wellness short-form video describes a
format the existing deterministic composited pipeline can already produce.

## CLOSEOUT_RECEIPT

```
AGENT: Pearl_Research
SIGNAL: social-deep-research-refresh=<see commit SHA below>
DIGEST_PATH: artifacts/social_media_atoms/pearl_social_media_writer_20260723/deep_research_digest_20260723.md
HANDOFF: artifacts/coordination/handoffs/social_deep_research_refresh_20260723.md
FINDINGS_VERIFIED_CITED: 34 (live 2026 web sources cited in digest §1-§4/§6, plus direct citations to
  the untracked local docs' own content, plus 6 native-speaker-reviewer corrections in §5 — see §6's
  full roll-up for the itemized list)
FINDINGS_GENERAL_KNOWLEDGE_UNCITED: 6 (flagged individually in digest §6: BAB formula label, the
  four-beat MICRO_STORY fallback template, the CASE_PROOF fallback shapes, Japan's/Korea's specific
  percentage statistics the native reviewers flagged as suspiciously precise/generic-survey-reskinned,
  Taiwan's PDPA "early 2026 update" specifics)
MICRO_STORY_PATTERNS_PROVIDED: 3 (existing-doc Before-and-After format row + hook-quality ladder as
  primary source; four-beat Anchor/Turn/Shift/Residue template as secondary/fallback)
CASE_PROOF_PATTERNS_PROVIDED: 5 (existing-doc shared-struggle social-proof framing + Problem-Mechanism-
  Result case-study structure as primary source; aggregate-pattern, mechanism-plus-caveat, and
  disclosure-first framings as secondary/fallback)
RETIRE_UPDATE_RECOMMENDATIONS: 5 (R1 land untracked docs; R2 fix Instagram hashtag config; R3 do NOT
  retire the existing VIDEO_BEAT beat map; R4 revise Korea/Hong Kong Platform Rules one-liners; R5 add
  carousel slide-arc metadata field)
APAC_NATIVE_SPEAKER_VALIDATION: consulted translate-ja, translate-ko, translate-zh-cn, translate-zh-hk,
  translate-zh-sg, translate-zh-tw via the Agent tool, 2026-07-23. All six returned substantive
  corrections (not just confirmations) — see NATIVE_SPEAKER_VALIDATION_20260723.md for full unedited
  replies and digest §5 for the folded-in, corrected findings per market. Headline corrections: Japan
  (anonymous-culture claim overstated as new/Gen-Z-specific; it's structural/decades-old), Korea
  ("group harmony" dated for 2026 wellness content; "Kakao Story" is a dead product name), Mainland
  China ("no superlatives" too vague — real trigger words named; confessional-only tone needs a
  credential marker too), Hong Kong (code-switching model was the wrong shape; XHS in HK risks reading
  mainland-inflected), Singapore (Xiaohongshu reach overstated; dialect-diversity claim backwards for
  under-50s; register needs warmth not just pragmatism), Taiwan (PDPA-vs-Singapore's-PDPA conflation
  risk flagged and confirmed distinct; simplified-Chinese lexical tells named as the top credibility
  risk).
ACCEPTANCE_LAYER: RESEARCHED (this is the research layer itself — not SPECCED, not CODE-WIRED, not
  EXECUTED-REAL, not PROVEN-AT-BAR; no atom content was authored or promoted in this lane)
NEXT_ACTION: hand to Lane C (atom authoring) — Lane C must cite
  artifacts/social_media_atoms/pearl_social_media_writer_20260723/deep_research_digest_20260723.md
  (plus the trend_pattern_delta_bank and NATIVE_SPEAKER_VALIDATION files in the same directory) when
  authoring MICRO_STORY, CASE_PROOF, CAROUSEL_SLIDE, THREAD_UNIT, and VIDEO_BEAT atoms, and when
  revising HOOK_COVER/CTA_ANCHOR hashtag/CTA-variety assumptions. Separately, flag R1 (land the 5
  untracked docs) and R2 (fix Instagram hashtag config) to whoever owns docs/ and config/social/
  respectively — both are small, concrete, out-of-this-lane's-scope fixes.
```
