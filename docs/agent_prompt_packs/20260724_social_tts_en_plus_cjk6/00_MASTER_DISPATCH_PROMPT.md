# EXECUTE — Pearl_PM Master Dispatch: Social-Media TTS — English + CJK6 (2026-07-24)

You are **Pearl_PM**, lead for the pack at
`docs/agent_prompt_packs/20260724_social_tts_en_plus_cjk6/`. Operator directive:
finish the English social-media voice bank on self-hosted CosyVoice2, then build
out the same for the 6 CJK locales (ja-JP, ko-KR, zh-CN, zh-TW, zh-HK, zh-SG) —
per-language "gotcha" text-prep research, translation, voicing, and a
CosyVoice2-vs-Qwen3-TTS A/B. This is an execution prompt, not a plan request.

## Turn contract (binds every lane)
- No stopping at plan / PR-open / tests-running / cleanup-later. Each lane ends
  MERGED-or-BLOCKED (or LANDED-OFFLINE on GitHub 403), blocker + resume named.
- STARTUP_RECEIPT first: `git branch --show-current`, HEAD SHA,
  `git status --short | head`, `gh auth status`, `git fetch origin`.
- Live-truth: every path/voice-id/count in this pack is a CLAIM verified
  2026-07-24 — re-verify before acting (files move; the bank was last touched
  Jul 21). Especially: confirm the live CosyVoice2 endpoint + API path before a
  scale run (config says `/api/v3/cross-lingual/with-cache`, the onbox script
  POSTs `/api/v1/tts` — reconcile against what the server actually serves).
- **Pearl Star GPU rule (RAP):** TTS is GPU work on Pearl Star. Read
  `docs/ROBUST_AGENT_PROTOCOL.md` before any run >10s; prefer queue-first
  dispatch; `PYTHONPATH=. python3 scripts/ci/check_rap_compliance.py` should not
  regress. Verify the node is reachable first (`curl -s --max-time 8
  "$COSYVOICE_URL/api/v1/health"` or the live health path).
- Layer-honest: a voiced MP3 is EXECUTED-REAL at most; "sounds good" is an
  operator-listen call (PROVEN-AT-BAR), never an agent's to assert. Byte-verify
  every audio artifact (real bytes, plays, correct language) — the repo has a
  history of stub-as-done.
- No monitor-parking: drive sub-agents with polling/SendMessage.

## Read first (you)
`TTS_STATE_2026-07-24.txt` (this pack), `config/tts/social_media_voice_matrix.yaml`,
`config/tts/locale_voice_routing.yaml`, `config/tts/social_media_tts_text_prep.yaml`,
`artifacts/research/social_media_tts_text_prep_2026-07-19/REPORT.md`, CLAUDE.md
(LLM Tier Policy + RAP).

## Dispatch order
| Wave | Lane | File | Depends on |
|---|---|---|---|
| 0 | Lane 1 — Finish English voice bank | `01_Pearl_Int_finish_english_voice_bank.md` | nothing — run now |
| 1 (parallel) | Lane 2 — CJK6 gotcha research | `02_Pearl_Research_cjk6_tts_gotchas.md` | nothing (research) |
| 1 (parallel) | Lane 3 — CJK6 translation | `03_Pearl_Localization_cjk6_translate.md` | nothing (needs EN SSOT, already exists) |
| 2 | Lane 4 — CJK6 voice + A/B | `04_Pearl_Int_cjk6_voice_and_ab.md` | Lanes 2 + 3 landed |

Dispatch each as a fresh agent with the lane file pasted verbatim. Serialize any
two lanes that would both run a Pearl Star scale job (single GPU — don't
double-book it; Lane 1 finishes before Lane 4 starts its scale run).

## Cross-cutting hard rules (repeat in every lane)
1. **NO SSML.** Plain speakable text only; pacing via punctuation. SSML and
   engine-param modulation are `forbidden` in the matrix — operator killed them
   after a listen (OPD-SMV-03). Do not reintroduce.
2. **Use `generate_voice_bank_onbox.py`, NOT `generate_voice_bank.py`** — the
   latter skips text-prep (bug). Any voicing must apply `apply_text_prep()`.
3. **zh-HK = Cantonese (`yue`), never Mandarin.** Hard rule in
   locale_voice_routing.yaml. A Mandarin zh-HK render is a defect, not a pass.
4. **zh-TW translation = Tier-1 Claude only.** Qwen emits Simplified at zh-TW
   (repo-proven); never route zh-TW through Qwen. Detection: s2t AND non-Big5.
5. **Free engines only.** CosyVoice2 self-hosted (unlimited) is the CJK default.
   DashScope cloud TTS free quota is a *sampling/A-B* tool only (10k-110k chars
   can't cover a bank) — never the production bank engine. ElevenLabs (paid) is
   out of scope for this pack.

## Closeout
```
CLOSEOUT_RECEIPT: SOCIALTTS-DISPATCH-DONE
lanes: <4 statuses MERGED-or-BLOCKED>
english_bank: <atoms voiced / total, manifest path, sample clips for operator>
cjk6: <per-locale: research done? translated count? voiced count? engine chosen>
operator_reads_pending: <EN listen; CJK samples>
NEXT_ACTION: <single most important next step — likely operator listen>
```
Append a dated line to this pack's INDEX.md when all lanes report.
