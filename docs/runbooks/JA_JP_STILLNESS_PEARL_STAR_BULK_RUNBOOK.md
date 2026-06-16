# ja_JP × stillness_press — Pearl Star autonomous bulk render runbook

**Last updated:** 2026-06-02
**Owner:** Pearl_Int (orchestrator) + Pearl_PM (program scope)
**Sister docs:** [`docs/runbooks/PEARL_STAR_SETUP_RUNBOOK.md`](./PEARL_STAR_SETUP_RUNBOOK.md), [`skills/pearl-int/references/manga_render_path_decision.md`](../../skills/pearl-int/references/manga_render_path_decision.md), [`skills/pearl-int/references/pearl_star_node_inventory.md`](../../skills/pearl-int/references/pearl_star_node_inventory.md).

## What this orchestrator does

Renders the ja_JP locale of stillness_press manga, end-to-end, autonomously on Pearl Star — operator's laptop off. Three phases:

| Phase | Work | Tier | Wall-clock |
|---|---|---|---|
| 0 | Translate available en_US chapter scripts → ja_JP via Pearl Star Ollama `qwen2.5:14b` | Tier 2 (free, unattended-safe) | ~5-15 min/chapter |
| 1 | Smoke: render + bubble + auto-validate one series (today: `the_alarm_is_lying` × ep_001+ep_002, the only authored en_US source). Replaces operator bless with automated gates. | H1=A on Pearl Star ComfyUI | ~30-90 min |
| 2 | Bulk: same render+bubble loop over any other available en_US source; per-chapter sentinels for resumability; daily progress TSV + git commit + R2 sync. **Today exits NO-OP** because only `the_alarm_is_lying` is authored. When more authoring lands, re-running picks it up. | H1=A on Pearl Star ComfyUI | scales with authored chapters |

Auto-validation gates (Phase 1): panel count == expected, each PNG > 50 KB, each bubbled PNG present. Pass → sentinel + R2 samples + git commit. Fail → sentinel + R2 samples + git commit + STOP for operator review.

Hourly: dashboard at `artifacts/manga/bulk_dashboard_ja_jp.html` regenerates from sentinels + progress TSV + recent commits, syncs to R2 so the operator can open the URL from any device.

## H1=A canonical workflow

Brand-1 (the_alarm_is_lying et al) renders use `scripts/image_generation/comfyui_workflows/flux_txt2img_manga.json`:

- Checkpoint: `flux1-dev-fp8.safetensors`
- Steps: 28 · CFG: 3.5 · Sampler: `dpmpp_2m` · Scheduler: `karras` · Denoise: 1.0
- Dims: 1080×1920 WEBTOON vertical

This is the H1=A config per operator decision (`feedback_campaign_h1_h2_decisions`). The pre-2026-06-02 schnell config has been moved to `flux_txt2img_manga_brand2_schnell.json` for brand-2's V1 ship path.

## Prerequisites (verified once via `PEARL_STAR_SETUP_RUNBOOK.md`)

- `~/.local/bin/gh` authed (scopes: `repo`, `workflow`)
- `~/.local/bin/rclone` with R2 remote `r2` (bucket: `phoenix-omega-artifacts`, `no_check_bucket=true`)
- `~/phoenix_omega` checked out (depth full, on `main`)
- ComfyUI on `:8188` reachable (`curl -s http://localhost:8188/system_stats` returns 200)
- Ollama on `:11434` serving `qwen2.5:14b`

If any of these are missing, run the setup runbook first.

## Operator start sequence (three commands; laptop off after step 3)

```
ssh pearl_star
cd ~/phoenix_omega && git pull origin main
nohup bash scripts/manga/orchestrate_ja_jp_stillness_full_render.sh \
    > artifacts/manga/bulk_logs/ja_jp_full_$(date +%Y%m%d_%H%M%S).log 2>&1 &
disown
exit
```

Capture the PID + log path printed in your terminal (visible right before `exit`) — they're useful for the abort + monitor commands below. Then close the laptop.

## Monitoring (any device, anywhere)

| What | How |
|---|---|
| Dashboard | Open R2 public URL: `https://<r2-public-url>/manga/bulk_dashboard_ja_jp.html` (substitute your bucket's public binding). Refreshes hourly. |
| Recent progress commits | `git log --oneline --grep="progress(ja_jp_bulk):"` on origin/main |
| Live tail | `ssh pearl_star "tail -100 ~/phoenix_omega/artifacts/manga/bulk_logs/ja_jp_full_*.log"` |
| Is orchestrator alive? | `ssh pearl_star "pgrep -af orchestrate_ja_jp_stillness_full_render"` |
| GPU free now | `ssh pearl_star "nvidia-smi --query-gpu=memory.free --format=csv,noheader"` |

The dashboard banner colour reads at a glance:

- ⬛ **PHASE 0/1 IN PROGRESS** — translation or smoke running
- 🟦 **BULK RUNNING (Phase 2)** — smoke validated; Phase 2 underway
- 🟥 **FAILED — operator review needed** — Phase 1 smoke failed; bulk halted; samples in `r2:phoenix-omega-artifacts/manga/ja_jp_smoke_failed/`
- 🟩 **BULK COMPLETE** — all available chapters rendered; deliverables under `artifacts/manga/bubbled/` and `r2:phoenix-omega-artifacts/manga/ja_jp_bulk/`

## Abort (graceful)

```bash
ssh pearl_star "pkill -f orchestrate_ja_jp_stillness_full_render"
```

This kills the orchestrator + its background dashboard loop. Per-chapter sentinels are preserved, so resuming is just re-running the start sequence.

## Resume

```bash
ssh pearl_star
cd ~/phoenix_omega && git pull origin main
nohup bash scripts/manga/orchestrate_ja_jp_stillness_full_render.sh \
    > artifacts/manga/bulk_logs/ja_jp_full_$(date +%Y%m%d_%H%M%S).log 2>&1 &
disown
exit
```

The orchestrator inspects `artifacts/manga/sentinels/` and skips any phase / chapter already complete:

- `ja_jp_phase0_complete.flag` → skip Phase 0
- `SMOKE_OK_ja_jp_stillness.flag` → skip Phase 1
- `BULK_COMPLETE_ja_jp_stillness.flag` → skip Phase 2
- Per-chapter `ja_jp_phase2_<series>__<chapter>.ok` → skip that chapter
- Per-panel: `queue_panel_renders.py --skip-existing` skips any PNG already on disk that's > 1 KB

If Phase 1 smoke failed (`SMOKE_FAILED.flag` present), the orchestrator refuses to start Phase 2 and exits. To re-attempt: delete the SMOKE_FAILED flag after fixing the underlying issue, then re-run.

## Failure mode catalogue

| Symptom | Likely cause | Fix |
|---|---|---|
| Phase 0 fails with `qwen_ollama backend not reachable` | Ollama on `:11434` down on Pearl Star | `ssh pearl_star "systemctl --user status ollama"` (or whatever supervises it); restart; re-run |
| Phase 1 smoke fails with `panel(s) under 50 KB` | ComfyUI degraded render (model not loaded, OOM) | `curl http://localhost:8188/system_stats` on Pearl Star; inspect render workflow; delete bad PNGs; re-run |
| Phase 1 smoke fails with `no bubbled panels` | `phoenix_v4.manga.chapter.bubble_render` import failed or chapter script lacks `text_by_locale[ja_JP]` | Confirm Phase 0 sentinel; inspect bubble_render error in log; if Phase 0 sentinel exists but ja_JP empty in the YAML, re-run Phase 0 with `--force-retranslate` |
| Dashboard not refreshing in R2 | rclone not on PATH inside the orchestrator's shell | Confirm `~/.local/bin/rclone` exists; orchestrator's `PATH` export includes `~/.local/bin`; re-run |
| Orchestrator process gone, no completion sentinel | OOM kill, network drop, ssh client cleanup | `dmesg \| grep -i kill` on Pearl Star; resume via the runbook's resume section |

## What this orchestrator does NOT do

- **Author missing en_US source.** Today only `the_alarm_is_lying × ep_001+ep_002` is authored. The other 15 stillness_press series planned in `config/source_of_truth/manga_book_plans/stillness_press__*` have no chapter scripts yet — they need Pearl_Writer / operator-tier authoring before Phase 2 can do anything for them. The orchestrator detects this and writes a `BULK_COMPLETE_ja_jp_stillness.flag` with a "no additional series" note rather than failing.
- **Render covers.** The original brief mentioned a cover per series; the cover dispatcher `scripts/image_generation/dispatchers/pearl_star_dispatcher.py` is a Python function (not a CLI), and brand-1 cover prompts aren't yet packaged into the orchestrator. Covers can be added in a follow-up.
- **Switch ComfyUI between brand-1 (dev / H1=A) and brand-2 (schnell) per render.** Brand-1 only. If brand-2 needs a parallel bulk, route to `flux_txt2img_manga_brand2_schnell.json` via `queue_panel_renders.py --workflow-path …`.

## Token / secret hygiene reminder

The orchestrator runs entirely on Pearl Star where credentials live in `~/.config/gh/hosts.yml` and `~/.config/rclone/rclone.conf`. It does NOT echo or print any secret. If you ever inspect any of these files manually (e.g., during a setup-runbook step), be careful with the terminal scroll-back / shell history — see the credential rotation guidance at the end of `PEARL_STAR_SETUP_RUNBOOK.md`.
