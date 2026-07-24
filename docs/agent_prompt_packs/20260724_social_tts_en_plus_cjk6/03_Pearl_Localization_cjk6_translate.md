# EXECUTE — Lane 3 (Pearl_Localization): Translate the social bank into CJK6

This is an execution prompt. End state: **the English social atom bank translated
into all six CJK locales (ja-JP, ko-KR, zh-CN, zh-TW, zh-HK, zh-SG), landed as
locale JSONL alongside the English SSOT, ready for Lane 4 to voice.** Do not stop
at the 10-atom pilot that already exists.

## Starting point (verified 2026-07-24 — re-verify)
- English SSOT: `SOURCE_OF_TRUTH/social_media_atoms/evergreen_en_us_atoms.jsonl`
  (~1,642 atoms; `text` field is what gets translated + voiced).
- Existing CJK content is a THIN pilot only:
  `apac_localization_atoms.jsonl` = 10 atoms each for ja-JP/ko-KR/zh-CN/zh-TW/
  zh-HK (+ en-SG). That's a starting sample, not coverage — extend to the full bank.
- Scope decision for this lane: translate the **243 reviewed_candidate** atoms
  first (the operator-vetted core — see the atoms' `review_status`), prove the
  pipeline end-to-end, THEN the 1,399 draft extension. Don't block the whole
  lane on translating 1,642×6 before anything ships.

## Contract (in-band) — locale doctrine is load-bearing
- STARTUP_RECEIPT: branch, HEAD, `git status --short | head`, `gh auth status`,
  `git fetch origin`. Branch from origin/main.
- **zh-TW = Tier-1 Claude ONLY.** Qwen emits Simplified characters at zh-TW
  (repo-proven, 2/2 probes) — NEVER route zh-TW through Qwen/DashScope. Verify
  output is Traditional: detection = s2t-differs AND non-Big5-representable
  (naive s2t false-flags 台/吃/游/群/床 — use the repo's zh-TW detector, don't
  hand-roll). zh-HK written form is also Traditional.
- **zh-HK is Cantonese-audience** — even though written Chinese, keep
  HK-idiomatic word choice; Lane 4 voices it as Cantonese (`yue`). Don't produce
  Mainland-phrased text for HK.
- Other CJK (ja, ko, zh-CN, zh-SG): may use Pearl Star Qwen (Tier-2, free) OR
  Claude (Tier-1). If using Qwen on Pearl Star, that's the free local path — not
  the banned paid DashScope cloud. Follow the existing translation infra
  (`scripts/localization/llm_client.py`, `scripts/localization/*`); reuse, don't
  fork.
- **CJK quality gates are English-tuned and FALSE-FAIL on CJK** (5 prose gates,
  repo-known). If a gate red is a scorer locale-blindness bug, file it — do NOT
  weaken the gate and do NOT corrupt the translation to satisfy an English
  scorer. Name any such gate in the closeout.
- Keep the atom schema intact: translate `text` (and any user-facing field),
  preserve `atom_id`↔source linkage, `persona`, `topic`, `atom_family`,
  assembly graph (`compatible_previous/next`), set `locale` correctly.
- Layer-honest: translated file existence ≠ authored-quality. CJK coverage
  numbers in memory measure file-existence; report ACTUAL translated+verified
  counts, and flag any machine-translated-but-unreviewed rows as such.

## Deliverables
- `SOURCE_OF_TRUTH/social_media_atoms/evergreen_{ja_JP,ko_KR,zh_CN,zh_TW,zh_HK,
  zh_SG}_atoms.jsonl` (or the repo's canonical locale-file naming — match
  existing convention; check how apac_localization is keyed first).
- A short coverage report: per-locale translated count, engine used per locale
  (Claude vs Pearl-Star-Qwen), zh-TW Traditional-purity check result, any
  false-failing CJK gate filed.
- Land on a branch → PR → merge per rules. ≤180-file PRs if large (split by locale).

## Closeout
```
CLOSEOUT_RECEIPT: SOCIALTTS-L3-DONE
translated: ja=<n> ko=<n> zh_CN=<n> zh_TW=<n> zh_HK=<n> zh_SG=<n>  (of <target>)
zh_tw_engine: Claude (Qwen forbidden)   zh_tw_traditional_purity: <pass + method>
zh_hk_register: HK-idiomatic (Cantonese-audience) confirmed
engines_used: <per-locale>   cjk_gate_false_fails_filed: <list or none>
pr(s): <# + SHA>   github: <MERGED / BLOCKED-403 offline @ sha>
acceptance_layer: authored candidate (translated) — TTS-readiness proven by Lane 4
NEXT_ACTION: Lane 4 voices these with the Lane 2 rulesets
```
Append a dated note to this pack's INDEX.md.
