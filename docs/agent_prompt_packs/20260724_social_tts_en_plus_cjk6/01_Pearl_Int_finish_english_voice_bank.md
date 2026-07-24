# EXECUTE — Lane 1 (Pearl_Int): Finish the English social-media voice bank

This is an execution prompt. End state: **all 1,642 evergreen English atoms
voiced on self-hosted CosyVoice2 through the text-prep-applying script, a real
manifest + MP3s landed (local + R2), and 3-5 sample clips surfaced for the
operator listen.** Do not stop at plan / tests-running / "a few samples."

## Reality check (verified 2026-07-24 — re-verify)
- English is NOT voiced at scale yet. Only 8 audition clips exist on disk. This
  is the FIRST real run.
- The bank: `SOURCE_OF_TRUTH/social_media_atoms/evergreen_en_us_atoms.jsonl`
  (~1,642 lines; `wc -l` to confirm). All `draft_only: true` — that's fine for
  voicing a draft bank; the operator listen is the gate, not the draft flag.
- Voices (ratified OPD-SMV-03, `config/tts/social_media_voice_matrix.yaml`):
  `corporate_managers → english_male`, `gen_z_professionals → english_female`,
  `healthcare_rns → english_female`. Stock CosyVoice2 voices. NO SSML, NO
  engine-param modulation (both `forbidden` — operator killed them).

## Contract (in-band)
- STARTUP_RECEIPT: branch, HEAD, `git status --short | head`, `gh auth status`,
  `git fetch origin`. Branch from origin/main:
  `git checkout -b agent/finish-en-social-voice-bank-20260724 origin/main`.
- **RAP / Pearl Star:** read `docs/ROBUST_AGENT_PROTOCOL.md` first (GPU run
  >10s). Load env: `eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"`
  (verify by exit code, never `--verbose` — it leaks). Health-check CosyVoice2
  before the run; if unreachable, STOP and report (do not fabricate audio).
- **Use `scripts/social_media/generate_voice_bank_onbox.py`** (applies
  `apply_text_prep`), NOT `generate_voice_bank.py` (skips it — known bug). Its
  args: `--atoms --matrix --text-prep --out --manifest [--r2-prefix]
  [--cosy http://127.0.0.1:9880] [--limit N --offset N] [--skip-upload] [--force]`.
- Preflight before any push: push_guard, preflight_push, health_check.
- Layer-honest: your job produces EXECUTED-REAL audio. "Bestseller/great voice"
  is the operator's listen call. Do not assert quality.

## Steps
1. **Reconcile the endpoint.** Config `provider_config.cosyvoice2` says synth
   path `/api/v3/cross-lingual/with-cache`; the onbox script POSTs `/api/v1/tts`.
   Hit the live server, confirm which path actually synthesizes, and use that
   (patch the script's path only if the live server requires it — minimal diff,
   documented).
2. **Smoke (3 atoms).** Run `--limit 3` across the 3 personas. Verify each MP3:
   real bytes (not stub), plays, is English, and the text-prep actually fired
   (manifest should carry `speakable_text` differing from raw where a rule
   applied — e.g. a colon became a period, "RN" became "nurse"). If text-prep
   did NOT alter any eligible atom, STOP — the prep isn't wired; fix before scale.
3. **Pilot (30 atoms)** across personas/topics. Re-verify bytes + a spot-listen
   sample set. Confirm voice-gender matches persona (corporate=male, others=female).
4. **Scale (all 1,642).** Full run with resume (`--offset`/`--limit` in batches
   if the GPU job is long; never a single unbounded call that can't resume).
   Write `artifacts/social_media_voice_bank_2026-07-24/MANIFEST.tsv` + MP3s;
   upload to R2 (prefix per script default `social_media/voice_bank/20260719b/`
   or a dated `.../20260724/` — pick one, record it). Big audio → R2, not git.
5. **Verify at scale:** manifest row count == atoms voiced; 0 stub-sized files
   (guard: bytes floor); sample 10 clips across personas/topics for the operator.
6. **Wire the reels caption check:** confirm `caption_source: voice_bank_speakable`
   resolves (the reels pipeline's `DEFAULT_MANIFEST` currently points at a
   non-existent `2026-07-19` path — update it to the manifest you just wrote, or
   note the exact one-line change needed).
7. **Land:** commit code/config diffs + the manifest (NOT the MP3s — those go to
   R2) on the branch → PR → merge per rules. Auto-open the sample clips for the
   operator (`open <clip>`).

## Closeout
```
CLOSEOUT_RECEIPT: SOCIALTTS-L1-DONE
voiced: <N>/1642   manifest: <path>   r2_prefix: <prefix>
text_prep_fired: <yes + example raw->speakable diff>
endpoint_used: <path>   voices: english_male/english_female confirmed
sample_clips_for_operator: <3-5 paths, opened in Finder>
reels_caption_wiring: <resolved / one-line-change-needed: ...>
pr: <# + SHA>   github: <MERGED / BLOCKED-403 offline @ sha>
acceptance_layer: EXECUTED-REAL (audio is real) — operator listen = PROVEN-AT-BAR, pending
NEXT_ACTION: operator listen to sample clips → approve or name fixes
```
Append a dated note to this pack's INDEX.md. BLOCKED ok only with blocker +
resume signal named (e.g. "CosyVoice2 unreachable @ <url>").
