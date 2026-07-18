# TTS provider hardening — closeout record (2026-04-10)

**Workstream:** `ws_tts_provider_hardening_20260410`  
**Project:** `proj_state_convergence_20260328`  
**Status:** completed (coordination row in `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`)

This document is the **single place** for what shipped, what was explicitly deferred, CI truth, commits, and how to sync locally. It complements the audit item in `artifacts/audit/PIPELINE_VERIFICATION_AUDIT.md` (hardcoded ElevenLabs URL in `run_soundtrack_engine.py`).

---

## 1. Scope that shipped (narrow lane)

**Goal:** Remove the **hardcoded ElevenLabs API host** from the video pipeline soundtrack stage while keeping **governed config** and **downstream JSON shape** stable.

| Item | Detail |
|------|--------|
| **Code** | `scripts/video/run_soundtrack_engine.py` — ElevenLabs TTS URL built from `config/tts/locale_voice_routing.yaml` → `provider_config.elevenlabs.base_url` + `/text-to-speech/{voice_id}`. If that YAML slice is missing, the script falls back to `${ELEVENLABS_BASE_URL}/text-to-speech/...` (spec placeholder only). |
| **Preserved** | Key `elevenlabs_api_calls` in `soundtrack_plan.json` (consumers such as `scripts/video/run_multilang_renderer.py`). |
| **PR** | [PR #354](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/354) — *fix(video): config-driven ElevenLabs URL in soundtrack stage (post–PR #351)* |
| **Merge commit (PR #354)** | `cebd91c5ad3bec367f2561c5dad2c0e9ad51ed9b` |

**PR #351** (pipeline verification audit, docs-only) remains the separate, merged audit; this lane did **not** reopen or amend #351.

---

## 2. What was split out and not merged (deferred)

Unmerged follow-up commit on `agent/pipeline-verification-audit` (message: drop ElevenLabs API — replace with CosyVoice2/Edge-TTS across all scripts) touched four files. Only the soundtrack script change was **redesigned** and merged as the narrow PR above; the rest stays **out of scope** for this workstream:

| File | Reason deferred |
|------|------------------|
| `scripts/audio/generate_presenter_audio.py` | Would change EN/cross-deck presenter policy vs governed `config/tts/*.yaml` without a migration spec. |
| `scripts/onboarding/generate_briefing_narration.py` | `specs/BRAND_ADMIN_ONBOARDING_TTS_SPEC.md` still centers ElevenLabs for briefing narration. |
| `scripts/pearl_practice/run_practice.py` | Practice audio path needs its own subsystem review and approval. |

**Next organizational step (not started here):** a **Pearl_PM / Pearl_Architect** migration spec (scope + acceptance criteria + phased PRs) for any **repo-wide** ElevenLabs → CosyVoice2 / Edge-TTS move. That is a **new** lane, not an extension of `ws_tts_provider_hardening_20260410`.

---

## 3. CI truth at merge (#354)

Recorded from GitHub **statusCheckRollup** on PR #354:

| Check | Result |
|-------|--------|
| Core tests | SUCCESS |
| Release gates | SUCCESS |
| EI V2 gates | SUCCESS |
| GitHub governance check (Verify governance) | SUCCESS |
| auto-merge | SKIPPED |
| Workers Builds: pearl-prime | FAILURE |

**Policy:** `Workers Builds: pearl-prime` is treated as **non-blocking** for merge per `docs/GITHUB_GOVERNANCE.md` (must not be a required ruleset context for `main`).

---

## 4. Config guarantee (production path)

On `main`, `config/tts/locale_voice_routing.yaml` includes:

```yaml
provider_config:
  elevenlabs:
    base_url: "https://api.elevenlabs.io/v1"
```

Therefore the **`${ELEVENLABS_BASE_URL}`** branch in code is a **fallback** when governed YAML is absent or incomplete — not the normal emission path when the repo config is present.

---

## 5. Workstream coordination commits

| Role | SHA (prefix) | Note |
|------|--------------|------|
| Closeout / row update to `completed` | `cf28ebad53` | Updates `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` with merge evidence and CI summary. |

**Note:** `origin/main` continues to advance after any closeout commit. A later tip (e.g. `562d7da5ec…`) does not invalidate the evidence rows above; it only means more commits landed afterward.

---

## 6. Validation performed (narrow change)

- `python3 -m py_compile scripts/video/run_soundtrack_engine.py`
- `python3 -m pytest tests/video/test_vce_stages.py::test_soundtrack_engine_writes_json tests/video/test_vce_stages.py::test_platform_and_multilang`

---

## 7. Local sync (safe default)

Prefer fast-forward only (preserves intentional local commits):

```bash
git fetch origin
git checkout main
git pull --ff-only origin main
```

Use `git reset --hard origin/main` **only** when discarding local changes on `main` is intentional.

---

## 8. References

- PR #354: https://github.com/Ahjan108/phoenix_omega_v4.8/pull/354  
- PR #351 (audit docs): merged separately; audit artifact: `artifacts/audit/PIPELINE_VERIFICATION_AUDIT.md`  
- TTS routing authority: `config/tts/locale_voice_routing.yaml`, `config/tts/engines.yaml`  
- Active workstreams: `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`  

---

*Owner: Pearl_GitHub (execution); Pearl_PM / Pearl_Architect (deferred migration spec). Last updated: 2026-04-10.*
