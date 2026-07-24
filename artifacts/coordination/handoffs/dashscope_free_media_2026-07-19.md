# Handoff — DashScope free media investigation 2026-07-19

**AGENT:** Pearl_Int  
**WHY:** Operator asked whether the same Singapore DashScope account can still do free video / image / TTS after translation credit looked spent.

## Verdict

- **Docs:** Yes — Singapore new-user free quota is **per model**: ~**50s** Wan video, **50–200** Wan / **100** Qwen images, **10k** CosyVoice / **110k** Qwen3-TTS chars, **1M tokens** text. Valid **90 days**. Not a shared pool across families.
- **Live key:** Authenticates (`/models` 200). **All generation blocked by `Arrearage`** (overdue). That blocks free leftovers too.
- **Sambert:** Not on Singapore intl pricing / models list — treat as Beijing-legacy; use CosyVoice / Qwen3-TTS on SG.

## Artifacts

| Path | Role |
|------|------|
| `artifacts/research/dashscope_free_media_2026-07-19/REPORT.md` | Full table + OPERATOR ACTION |
| `artifacts/research/dashscope_free_media_2026-07-19/probe.log` | Redacted HTTP transcript |
| Branch `agent/dashscope-free-media-20260719` | Offline land (GitHub 403) |

## Operator next

1. Pay Alibaba overdue balance (Billing).  
2. Singapore Free Quota tab → read remaining for Wan / image / CosyVoice / qwen3-tts / translation model.  
3. Re-run a 1-call smoke per family only after arrears clear (operator-present; do not pipeline-wire).

## Do not

- Do not push (GitHub suspended).  
- Do not wire paid DashScope media into scheduled pipelines without policy decision.  
- Do not use Beijing console numbers.
