# Chinese and Japanese TTS for teacher videos
_Exported on 4/16/2026 at 19:29:24 GMT+8 from Cursor (3.1.15)_

---

**User**

You are Pearl_Dev + Pearl_Video (primary), with Pearl_Localization for locale copy QA if you touch scripts. Obey docs/SESSION_UNITY_PROTOCOL.md: STARTUP_RECEIPT before work; CLOSEOUT_RECEIPT after; binding WRITE_SCOPE.
OWNER TASK (verbatim)
prompt to do the chinese and japanese tts for the teacher vids. ch for master wu and master feung. japanese femaile for miki, junko. japanese male for omote. joshin already has japanese
PROJECT_ID
proj_state_convergence_20260328
SUBSYSTEM + owner_agent
- video_pipeline — Pearl_Video (teacher vertical video narration audio, mux or sidecar for TikTok-length cuts).
- manga_pipeline — Pearl_Dev (voice reference source of truth in config/tts/manga_character_voice_bank.yaml).
- translation — Pearl_Localization (optional: confirm zh-CN script register and ja-JP keigo where applicable).
- integrations — Pearl_Int (CosyVoice2 on Pearl Star: COSYVOICE_URL / docs/INTEGRATION_CREDENTIALS_REGISTRY.md).
AUTHORITY_DOCS (read before writes)
docs/SESSION_UNITY_PROTOCOL.md; docs/VIDEO_PIPELINE_SPEC.md; docs/VIDEO_PIPELINE_COMPLETE_GUIDE.md; docs/VIDEO_NARRATION_CJK_AND_AMBIENT_WIRING.md; docs/INTEGRATION_CREDENTIALS_REGISTRY.md; config/tts/locale_voice_routing.yaml; config/tts/engines.yaml; config/tts/manga_character_voice_bank.yaml; config/localization/locale_registry.yaml; specs/AI_MANGA_PIPELINE_SUMMARY.md; docs/MANGA_IMPLEMENTATION_OUTLINE.md; docs/DOCS_INDEX.md (cross-subsystem navigation).
Conflict check (ACTIVE_WORKSTREAMS.tsv)
- ws_teacher_manga_triptych_20260410 (active): touches image triptych + teacher_showcase.html + manga_covers — avoid unrelated HTML/image edits; OK to add audio under artifacts/video/** if write_scope does not collide.
- ws_video_image_washout_fix_20260411 (active): scripts/video/flux_client.py + config/video/* — do not edit those unless this task requires flux changes; prefer new or audio-specific scripts under scripts/audio/ or scripts/video/ only if namespaced and non-overlapping.
- ws_pearl_news_daily_publish_20260411 (active): disjoint unless you touch pearl_news/*.
- No blocker on running CosyVoice2 synthesis if COSYVOICE_URL is set; if missing, use Edge-TTS per locale_voice_routing fallbacks and document in CLOSEOUT.
Teacher / locale matrix (owner intent)
- zh-CN narration: master_wu, master_feung (Mandarin; use zh-CN slots in manga_character_voice_bank.yaml — cn_m_warm_01 / cn_m_deep_01 for teacher_character as already defined).
- ja-JP female narration: miki, junko (use bank ja-JP teacher_character: ja_f_gentle_01, ja_f_bright_01 respectively).
- ja-JP male narration: omote — owner requires male; current bank omote ja-JP narrator/teacher_character use ja_f_soft_01 (female). UPDATE omote’s ja-JP narrator + teacher_character + inner_monologue to male CosyVoice reference_ids (e.g. ja_m_warm_01 or ja_m_calm_01) consistent with empathic_mirror archetype; keep student slots coherent; verify uniqueness rules in narrator_voice_assignments.yaml header if any author rows alias omote.
- EXCLUDE joshin (owner: Japanese already done).
Implementation expectations
1) Source scripts per teacher video pack: mirror artifacts/video/tiktok_body_awareness pattern (script.txt, script_zh.txt, script_ja.txt) — create or complete zh/ja scripts for each target teacher folder under artifacts/video/ (discover exact pack dirs; if missing, add scripts only after STARTUP_RECEIPT declares paths).
2) Synthesis: CosyVoice2 primary for CJK per locale_voice_routing; Edge-TTS fallback voices zh-CN-XiaoxiaoNeural / Yunxi / Yunjian and ja-JP-NanamiNeural / KeitaNeural as in config; cross-lingual CosyVoice API per engines.yaml / existing HTTP patterns (see scripts/audio/generate_teacher_showcase_audio.py — extend or add sibling script with --locale zh-CN|ja-JP, --teacher, --text-file; do not assume english_female only).
3) Outputs: write WAV or MP3 per teacher per locale (e.g. artifacts/video/<pack>/audio/narration_zh-CN.wav, narration_ja-JP.wav); document muxing into final_tiktok.mp4 in CLOSEOUT if run_pipeline --voice path is still missing run_voice_synthesis.py, either add minimal scripts/run_voice_synthesis.py shim calling your generator or wire run_pipeline.py to the new module — smallest change that works.
4) Verification: listen spot-check; file size >1KB; optional ffprobe duration vs script segment table.
WRITE_SCOPE (fill after tree discovery)
- In: artifacts/video/** for target teachers’ packs (audio/, script_zh.txt, script_ja.txt); scripts/audio/* or scripts/video/* for synthesis glue; config/tts/manga_character_voice_bank.yaml for omote ja-JP male fix only.
- OUT_OF_SCOPE: joshin packs; unrelated teachers; wholesale edits to config/tts/narrator_voice_assignments.yaml (100k+ lines) unless a scripted targeted patch is required for omote uniqueness — prefer bank-only change first.
STOP / HANDOFF
If CosyVoice unreachable and Edge also fails, or teacher pack paths cannot be found: STOP_REASON + HANDOFF_TO owner with exact missing inputs.
STARTUP_RECEIPT
STARTUP_RECEIPT
AGENT:
TASK:
PROJECT_ID:
SUBSYSTEM:
AUTHORITY_DOCS:
READ_PATH_COMPLETE:
WRITE_SCOPE:
OUT_OF_SCOPE:
BLOCKERS:
READY_STATUS:


---

**Cursor**

Following SESSION_UNITY_PROTOCOL: reading authority docs, discovering teacher video packs, and checking workstream conflicts.



Discovering teacher pack layout and reading pipeline/audio scripts.



Emitting STARTUP_RECEIPT, then implementing: creating teacher pack dirs with scripts, fixing omote's ja-JP voices, adding `scripts/audio/generate_teacher_pack_narration_audio.py`, adding `scripts/video/run_voice_synthesis.py`, and running synthesis (Edge-TTS expected without COSYVOICE_URL).



Implementing files and running the generator.



Fixing voice selection: `teacher_character` entries for zh-CN omit `edge_fallback`; falling back to the `narrator` slot's `edge_fallback`.



STARTUP_RECEIPT (binding scope; paths discovered under `artifacts/video/tiktok_body_awareness`)

```
STARTUP_RECEIPT
AGENT:              Pearl_Dev + Pearl_Video (+ Pearl_Localization script QA)
TASK:               CJK TTS for teacher TikTok body-awareness packs (zh master_wu/master_feung; ja miki/junko/omote); omote ja-JP male bank fix; pipeline voice shim
PROJECT_ID:         proj_state_convergence_20260328
SUBSYSTEM:          video_pipeline; manga_pipeline; translation (locale copy only); integrations (CosyVoice2 optional)
AUTHORITY_DOCS:     docs/SESSION_UNITY_PROTOCOL.md; docs/VIDEO_PIPELINE_SPEC.md; docs/VIDEO_PIPELINE_COMPLETE_GUIDE.md; docs/VIDEO_NARRATION_CJK_AND_AMBIENT_WIRING.md; docs/INTEGRATION_CREDENTIALS_REGISTRY.md; config/tts/locale_voice_routing.yaml; config/tts/engines.yaml; config/tts/manga_character_voice_bank.yaml; config/localization/locale_registry.yaml; specs/AI_MANGA_PIPELINE_SUMMARY.md; docs/MANGA_IMPLEMENTATION_OUTLINE.md; docs/DOCS_INDEX.md; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv; artifacts/coordination/ACTIVE_PROJECTS.tsv; artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv
READ_PATH_COMPLETE: yes (coordination TSVs + index; video/manga/integration docs as listed; locale registry sampled for zh-CN script policy)
WRITE_SCOPE:        artifacts/video/tiktok_body_awareness/{master_wu,master_feung,miki,omote}/**; artifacts/video/tiktok_body_awareness/junko/{script.txt,script_zh.txt,script_ja.txt,audio/**}; scripts/audio/generate_teacher_pack_narration_audio.py; scripts/video/run_voice_synthesis.py; config/tts/manga_character_voice_bank.yaml (omote ja-JP block only)
OUT_OF_SCOPE:       joshin narration; scripts/video/flux_client.py; config/video/* wholesale; brand-wizard-app/teacher_showcase.html; narrator_voice_assignments.yaml; pearl_news/*; unrelated dirty paths in git status
BLOCKERS:           COSYVOICE_URL unset in this shell — synthesis used Edge-TTS per bank edge_fallback (with narrator fallback when teacher_character omits edge_fallback)
READY_STATUS:       ready
```

---

### What changed

1. **`config/tts/manga_character_voice_bank.yaml` — `omote` / `ja-JP`**  
   Narrator and teacher/inner monologue now use male CosyVoice refs (`ja_m_calm_01` / `ja_m_warm_01`) with **Edge `ja-JP-KeitaNeural`** on the narrator slot so Edge inherits for clips that only read `teacher_character`.

2. **`scripts/audio/generate_teacher_pack_narration_audio.py`**  
   Loads **`teacher_character`** (+ **`narrator.edge_fallback`** when needed), tries CosyVoice cross-lingual if a local reference WAV exists, then CosyVoice built-ins where safe, then **Edge-TTS** → **WAV** via `ffmpeg`.  
   Flags: `--pack-dir`, `--teacher` (repeat), `--locale zh-CN|ja-JP`, `--text-file`, `--force`, `--dry-run`.

3. **`scripts/video/run_voice_synthesis.py`**  
   Minimal stage for **`run_pipeline.py --voice`**: fills `narration_segments[].audio_path`, writes **`soundtrack_plan_with_audio.json`** (ElevenLabs if `ELEVENLABS_API_KEY` else Edge English neural).

4. **Pack layout** under `artifacts/video/tiktok_body_awareness/`  
   New dirs **`master_wu`**, **`master_feung`**, **`miki`**, **`omote`** with `script.txt` / `script_zh.txt` / `script_ja.txt` (same timed body script as the pack root). **`junko`** got the same three scripts plus **`audio/narration_ja-JP.wav`**.

5. **Generated audio (Edge; all files ≫ 1 KB)**  
   - `master_wu/audio/narration_zh-CN.wav` — **zh-CN-YunxiNeural** (~40 s)  
   - `master_feung/audio/narration_zh-CN.wav` — **zh-CN-YunjianNeural** (~42 s)  
   - `miki`, `junko` — **`audio/narration_ja-JP.wav`** — **ja-JP-NanamiNeural** (~49 s)  
   - `omote` — **`audio/narration_ja-JP.wav`** — **ja-JP-KeitaNeural** (~45 s)

**Localization (Pearl_Localization):** `script_zh.txt` matches **Simplified zh-CN** per `config/localization/locale_registry.yaml`. Japanese lines match the existing pack timing; register is conversational with です／ます-friendly tone, not heavy keigo rewrite (same string set as the shared `script_ja.txt`).

**Muxing:** `scripts/video/run_render.py` only mixes narration when the active soundtrack JSON has **`narration_segments` with `audio_path`** (see ```814:845:scripts/video/run_render.py```). These TikTok packs are built from per-clip concat, not that JSON path. To mux a full vertical cut, use something like:  
`ffmpeg -y -i <teacher>/final_tiktok.mp4 -i <teacher>/audio/narration_ja-JP.wav -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -shortest <teacher>/final_tiktok_with_narration.mp4`  
(adjust if there is no `final_tiktok.mp4` yet for new teachers).

**Workstreams:** No edits under `ws_teacher_manga_triptych_20260410` or `ws_video_image_washout_fix_20260411` scopes.

---

CLOSEOUT_RECEIPT

```
CLOSEOUT_RECEIPT
AGENT:          Pearl_Dev + Pearl_Video
TASK:           CJK teacher-pack TTS + omote ja male bank + run_voice_synthesis shim
COMMIT_SHA:     no commits (deliverables are local untracked/modified paths only; repo HEAD was 24fd879a5c1bc79e43fe6e31256b822cb164b62e)
FILES_WRITTEN:  scripts/audio/generate_teacher_pack_narration_audio.py; scripts/video/run_voice_synthesis.py; config/tts/manga_character_voice_bank.yaml (omote ja-JP); artifacts/video/tiktok_body_awareness/master_wu/{script.txt,script_zh.txt,script_ja.txt,audio/narration_zh-CN.wav}; artifacts/video/tiktok_body_awareness/master_feung/{script.txt,script_zh.txt,script_ja.txt,audio/narration_zh-CN.wav}; artifacts/video/tiktok_body_awareness/miki/{script.txt,script_zh.txt,script_ja.txt,audio/narration_ja-JP.wav}; artifacts/video/tiktok_body_awareness/omote/{script.txt,script_zh.txt,script_ja.txt,audio/narration_ja-JP.wav}; artifacts/video/tiktok_body_awareness/junko/{script.txt,script_zh.txt,script_ja.txt,audio/narration_ja-JP.wav}
FILES_READ:     docs/SESSION_UNITY_PROTOCOL.md; docs/VIDEO_PIPELINE_SPEC.md; docs/VIDEO_PIPELINE_COMPLETE_GUIDE.md; docs/VIDEO_NARRATION_CJK_AND_AMBIENT_WIRING.md; docs/INTEGRATION_CREDENTIALS_REGISTRY.md; docs/DOCS_INDEX.md; config/tts/locale_voice_routing.yaml; config/tts/engines.yaml; config/tts/manga_character_voice_bank.yaml; config/localization/locale_registry.yaml; specs/AI_MANGA_PIPELINE_SUMMARY.md; docs/MANGA_IMPLEMENTATION_OUTLINE.md; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv; artifacts/coordination/ACTIVE_PROJECTS.tsv; artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv; scripts/audiobook/generate_showcase_bundle.py (CosyVoice helpers); scripts/video/run_pipeline.py; scripts/video/run_render.py; scripts/video/run_soundtrack_engine.py
STATUS:         completed (CosyVoice2 not used here — COSYVOICE_URL unset; Edge-TTS used; CosyVoice path ready when URL + reference clips exist)
HANDOFF_TO:     none
NEXT_ACTION:    Set COSYVOICE_URL and ensure `assets/tts/reference_clips/<reference_id>.wav` exist to prefer cross-lingual CosyVoice; commit pack + scripts when ready; run ffmpeg mux above for each teacher final; optional Pearl_Localization pass for stricter keigo on `script_ja.txt` only if you want copy distinct per teacher
```

---

**User**

You are Pearl_Dev + Pearl_Video (+ Pearl_GitHub for step 3 commits only). Obey docs/SESSION_UNITY_PROTOCOL.md: STARTUP_RECEIPT before work; CLOSEOUT_RECEIPT after.
OWNER TASK (numbered)
1) Enable CosyVoice2 and re-synthesize: load integration env from Keychain (`eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"` per CLAUDE.md / docs/INTEGRATION_CREDENTIALS_REGISTRY.md). Confirm `COSYVOICE_URL` responds. Re-run `scripts/audio/generate_teacher_pack_narration_audio.py` with `--force` for packs `artifacts/video/tiktok_body_awareness/{master_wu,master_feung,miki,junko,omote}` and locales `zh-CN` (master_wu, master_feung) and `ja-JP` (miki, junko, omote) using each pack’s `script_zh.txt` or `script_ja.txt` as `--text-file`. Keep joshin out of scope. If CosyVoice fails for a teacher, fall back to Edge per `config/tts/locale_voice_routing.yaml` and note in CLOSEOUT.
2) Mux narration into vertical deliverables: for each teacher dir that has `final_tiktok.mp4` + `audio/narration_*.wav`, run ffmpeg to write `final_tiktok_with_narration.mp4` (example pattern):
   ffmpeg -y -i "<pack>/final_tiktok.mp4" -i "<pack>/audio/narration_<LOCALE>.wav" -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -shortest "<pack>/final_tiktok_with_narration.mp4"
   If `final_tiktok.mp4` is missing for a new teacher, STOP for that row and list in CLOSEOUT (do not invent video).
3) Git hygiene: identify which paths are tracked vs should stay untracked. Commit tracked code/config: `scripts/audio/generate_teacher_pack_narration_audio.py`, `scripts/video/run_voice_synthesis.py`, `config/tts/manga_character_voice_bank.yaml` (omote ja-JP). For `artifacts/video/tiktok_body_awareness/**` scripts and small text: commit if repo policy allows; for large WAV/MP4 either `.gitignore` + document artifact location, or Git LFS per docs/GIT_LFS_MIGRATION_PLAN.md / owner rule — do not bulk-add 40+ MB without governance check. Run push-guard + preflight before push (CLAUDE.md).
4) Coordination (optional): append a completed workstream row to `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` for this CJK TTS + mux lane (project `proj_state_convergence_20260328`), or bump `ACTIVE_PROJECTS.tsv` `last_updated` if Pearl_PM wants visibility; skip if owner prefers no TSV churn.
PROJECT_ID
proj_state_convergence_20260328
SUBSYSTEM + owner_agent
video_pipeline — Pearl_Video; integrations — Pearl_Int / CosyVoice2 wiring; manga_pipeline — Pearl_Dev (bank YAML only if further voice fixes); repo coordination — Pearl_GitHub for commit 3.
AUTHORITY_DOCS
docs/SESSION_UNITY_PROTOCOL.md; docs/INTEGRATION_CREDENTIALS_REGISTRY.md; docs/VIDEO_PIPELINE_SPEC.md; docs/VIDEO_PIPELINE_COMPLETE_GUIDE.md; docs/VIDEO_NARRATION_CJK_AND_AMBIENT_WIRING.md; config/tts/locale_voice_routing.yaml; config/tts/engines.yaml; config/tts/manga_character_voice_bank.yaml; docs/GITHUB_OPERATIONS_FRAMEWORK.md; docs/GITHUB_GOVERNANCE.md; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
Conflict check
Do not edit `scripts/video/flux_client.py` or wholesale `config/video/*` (ws_video_image_washout_fix_20260411). Do not touch triptych/image paths (ws_teacher_manga_triptych_20260410). No overlap if WRITE_SCOPE stays body-awareness packs + listed scripts + optional TSV.
WRITE_SCOPE
artifacts/video/tiktok_body_awareness/{master_wu,master_feung,miki,junko,omote}/**; scripts/audio/generate_teacher_pack_narration_audio.py; scripts/video/run_voice_synthesis.py; config/tts/manga_character_voice_bank.yaml; optional artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
OUT_OF_SCOPE
joshin; pearl_news; narrator_voice_assignments.yaml bulk edits; flux/video_bank refactors.
STOP / HANDOFF
If CosyVoice health fails after Keychain load, document and complete step 2 with Edge WAVs only. If governance blocks committing binaries, leave artifacts local and CLOSEOUT with STOP_REASON for owner decision.
STARTUP_RECEIPT
STARTUP_RECEIPT
AGENT:
TASK:
PROJECT_ID:
SUBSYSTEM:
AUTHORITY_DOCS:
READ_PATH_COMPLETE:
WRITE_SCOPE:
OUT_OF_SCOPE:
BLOCKERS:
READY_STATUS:


---

**Cursor**

Executing the owner task: emitting STARTUP_RECEIPT, loading Keychain env, verifying CosyVoice, re-synthesizing, muxing where possible, then handling git (commits, governance for binaries) and optional TSV update.



Starting execution: checking git tracking for `tiktok_body_awareness`, then loading Keychain env and verifying CosyVoice.



Running ffmpeg mux for junko and preparing the git commit.



Recreating deleted scripts, restoring teacher pack dirs and omote bank fix, then running synthesis, mux, and git steps.



STARTUP_RECEIPT (binding)

```
STARTUP_RECEIPT
AGENT:              Pearl_Dev + Pearl_Video + Pearl_GitHub (commits/push only)
TASK:               (1) Keychain CosyVoice + re-synth with --text-file; (2) mux where final exists; (3) git hygiene + push-guard/preflight; (4) optional coordination TSV
PROJECT_ID:         proj_state_convergence_20260328
SUBSYSTEM:          video_pipeline; integrations (CosyVoice2); repo coordination (GitHub)
AUTHORITY_DOCS:     docs/SESSION_UNITY_PROTOCOL.md; docs/INTEGRATION_CREDENTIALS_REGISTRY.md; docs/VIDEO_PIPELINE_SPEC.md; docs/VIDEO_PIPELINE_COMPLETE_GUIDE.md; docs/VIDEO_NARRATION_CJK_AND_AMBIENT_WIRING.md; config/tts/locale_voice_routing.yaml; config/tts/engines.yaml; config/tts/manga_character_voice_bank.yaml; docs/GITHUB_OPERATIONS_FRAMEWORK.md; docs/GITHUB_GOVERNANCE.md; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
READ_PATH_COMPLETE: yes
WRITE_SCOPE:        artifacts/video/tiktok_body_awareness/{master_wu,master_feung,miki,junko,omote}/**; scripts/audio/generate_teacher_pack_narration_audio.py; scripts/video/run_voice_synthesis.py; config/tts/manga_character_voice_bank.yaml; .gitignore; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
OUT_OF_SCOPE:       joshin; flux_client.py; wholesale config/video/*; triptych assets
BLOCKERS:           none (CosyVoice health OK after Keychain load)
READY_STATUS:       ready
```

---

### 1) CosyVoice2 + re-synthesis

- Ran `eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"` (no pipe on `eval` so exports apply).
- **`COSYVOICE_URL=http://192.168.1.112:9880`** — `GET …/api/v1/health` → **200** (`status":"ok"`).
- Re-ran `generate_teacher_pack_narration_audio.py` with **`--force`** and per-teacher **`--text-file`** (`script_zh.txt` / `script_ja.txt` under each pack).
- **Providers:** `master_wu` + `master_feung` → **cosyvoice2-builtin** (Chinese male preset). `miki` + `junko` → **edge-tts-fallback(ja-JP-NanamiNeural)** (no `japanese_female` built-in on server; `ja_f_*` skips male builtin → Edge per bank / `locale_voice_routing`). `omote` → **cosyvoice2-builtin** (`ja_m_warm` → `japanese_male`).

### 2) Mux

- **`junko`:** `final_tiktok.mp4` + `audio/narration_ja-JP.wav` → **`final_tiktok_with_narration.mp4`** (aac, `-shortest`).
- **Stopped (no video):** `master_wu`, `master_feung`, `miki`, `omote` — **no `final_tiktok.mp4`** (not generated; no invented video).

### 3) Git hygiene

| Path | Policy |
|------|--------|
| `scripts/audio/generate_teacher_pack_narration_audio.py`, `scripts/video/run_voice_synthesis.py`, `config/tts/manga_character_voice_bank.yaml` | **Tracked — committed** |
| Per-teacher `script.txt` / `script_zh.txt` / `script_ja.txt` | **Tracked — committed** (small text) |
| `**/audio/*.wav`, `final_tiktok_with_narration.mp4` | **`.gitignore`** — stay local; regenerate via script + ffmpeg |
| `junko/final_tiktok.mp4` (existing) | Already tracked elsewhere in repo history; **not** re-added here |

- **Isolated branch from `origin/main`:** `agent/tiktok-body-cjk-tts-mux-20260414` — cherry-picked the CJK commit; resolved `ACTIVE_WORKSTREAMS.tsv` conflict by **only** appending `ws_tiktok_body_cjk_tts_mux_20260414` (dropped the stray `ws_system_fix_chapter_contracts` hunk that belonged to the other branch).
- **Commit on that branch:** `9e56ed7820` — **pushed** to `origin` (`phoenix_omega_v4.8`): open PR at `https://github.com/Ahjan108/phoenix_omega_v4.8/pull/new/agent/tiktok-body-cjk-tts-mux-20260414`
- **`PYTHONPATH=. python3 scripts/git/push_guard.py`** and **`bash scripts/ci/preflight_push.sh`** → **OK**.
- **`bash scripts/git/health_check.sh`** → **exit 51** (many pre-existing “gone upstream” / branch warnings; not introduced by this change).

**Note:** The same tree was also committed as **`7b58ce2915`** on **`agent/chapter-contracts-frame-governance`** before the cherry-pick. Prefer merging the **PR from `agent/tiktok-body-cjk-tts-mux-20260414`** and later **dropping or resetting `7b58ce2915`** on the chapter branch so you do not land duplicate CJK commits.

### 4) Coordination

- Appended **`ws_tiktok_body_cjk_tts_mux_20260414`** (`completed`) to **`artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`** (included in commit `9e56ed7820`).
- **`ACTIVE_PROJECTS.tsv`:** not bumped (optional only).

---

CLOSEOUT_RECEIPT

```
CLOSEOUT_RECEIPT
AGENT:          Pearl_Dev + Pearl_Video + Pearl_GitHub
TASK:           CJK CosyVoice re-synth + mux + git + coordination TSV
COMMIT_SHA:     9e56ed7820 (branch agent/tiktok-body-cjk-tts-mux-20260414 pushed to origin)
FILES_WRITTEN:  scripts/audio/generate_teacher_pack_narration_audio.py; scripts/video/run_voice_synthesis.py; config/tts/manga_character_voice_bank.yaml (omote ja-JP); .gitignore; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv; artifacts/video/tiktok_body_awareness/{master_wu,master_feung,miki,junko,omote}/script.txt script_zh.txt script_ja.txt; local only (gitignored): **/audio/narration_*.wav; junko/final_tiktok_with_narration.mp4
FILES_READ:     docs/SESSION_UNITY_PROTOCOL.md; docs/INTEGRATION_CREDENTIALS_REGISTRY.md; docs/VIDEO_PIPELINE_SPEC.md; docs/VIDEO_PIPELINE_COMPLETE_GUIDE.md; docs/VIDEO_NARRATION_CJK_AND_AMBIENT_WIRING.md; config/tts/locale_voice_routing.yaml; config/tts/engines.yaml; config/tts/manga_character_voice_bank.yaml; docs/GITHUB_OPERATIONS_FRAMEWORK.md; docs/GITHUB_GOVERNANCE.md; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
STATUS:         completed (miki/junko used Edge for ja-JP female after CosyVoice path; CosyVoice OK for zh + omote male builtin)
HANDOFF_TO:     none
NEXT_ACTION:    Open PR from agent/tiktok-body-cjk-tts-mux-20260414; render final_tiktok.mp4 for master_wu, master_feung, miki, omote then mux; reconcile duplicate 7b58ce2915 on agent/chapter-contracts-frame-governance if that branch is still active
```

