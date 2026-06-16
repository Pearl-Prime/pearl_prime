# Manga V5.1 — Ship Readiness / Go-Trigger Sheet (2026-06-12)

**Owner:** Pearl_PM • **Tier:** 1 (Claude Code, operator-present) • **Status:** BLOCKED on Pearl Star endpoint
**Series:** `stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying`
**Ship branch (existing — do NOT fork fresh from main):** `agent/post-pr478-manga-activation`

> This sheet is the operator's exact go-trigger for shipping V5.1 episodes the moment Pearl Star (`http://192.168.1.112:8188`) is back online. ep_001 is RENDER-COMPLETE and PUBLISH-pending. ep_002 is RENDER-pending (all upstream PRs merged). Nothing below executes while the endpoint is down.

---

## 0. PREFLIGHT — must all pass before anything else

Run from a host with the integration env loaded:

```bash
eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
```

### 0.1 — Pearl Star ComfyUI endpoint UP (HARD GATE — currently FAILING)

```bash
curl -s -m 6 http://192.168.1.112:8188/system_stats | head -c 400; echo
```

- **PASS** = JSON object with a `"devices"` array (GPU name + `vram_total`).
- **FAIL** = empty output, `curl: (28)` timeout, or HTTP 000 → **STOP. Pearl Star is down. Do not render, do not publish.** Bring the rig + ComfyUI online, re-run, then continue.

Secondary liveness check (queue must answer):

```bash
curl -s -m 6 http://192.168.1.112:8188/queue | head -c 200; echo
```

PASS = JSON (`queue_running` / `queue_pending`). FAIL = same stop condition as above.

### 0.2 — R2 secrets present in GitHub **Actions** secrets (GATE-OP-1, operator-only)

```bash
gh secret list --repo Ahjan108/phoenix_omega_v4.8 \
  | grep -E 'R2_ACCOUNT_ID|R2_BUCKET|R2_ACCESS_KEY_ID|R2_SECRET_ACCESS_KEY'
```

- **PASS** = all four names listed.
- **FAIL** = any missing → publish step E is **BLOCKED**. Operator adds them at the repo Actions secrets page. (Render of ep_002 does NOT need these; only outward publish does.)

### 0.3 — Pearl Star self-hosted runner online (GATE-OP-2, operator-only)

```bash
gh api repos/Ahjan108/phoenix_omega_v4.8/actions/runners \
  --jq '.runners[] | "\(.name)\t\(.status)\t\(.busy)"'
```

PASS = a `pearl-star` runner with `status=online`. If absent, operator installs the marker via SSH (see §3 GATE-OP-2). This gate blocks any Actions-driven publish, not the local render.

**Preflight verdict:** all three green → proceed. Any red → resolve that line first; do not improvise around it.

---

## 1. ep_002 — RENDER (single dispatch)

**State:** pose-library (#1333), beatsheet (#1316), continuity-state generator (#1310), 32 panel_prompts (#1421) ALL MERGED. `continuity_state/ep_002` exists on disk. **No render yet.** Remaining work = the one `render_v5_episode.py` invocation below, then the bubble/compose/publish tail (same as ep_001).

### 1.1 — Dry-run first (no GPU; validates config + prompt compile)

```bash
python3 scripts/manga/render_v5_episode.py \
  --profile-id stillness_en_01 \
  --artifacts-series-id stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying \
  --episode-id ep_002 \
  --dry-run
```

Expect: `=== SUMMARY ep=ep_002: ... dry_run=32 ...` (32 panels compiled, 0 fail). If panel count ≠ 32 or any `PROMPT_FAIL`, stop and investigate before the real render.

### 1.2 — Full render (the single go-command)

```bash
python3 scripts/manga/render_v5_episode.py \
  --profile-id stillness_en_01 \
  --artifacts-series-id stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying \
  --episode-id ep_002 \
  --skip-existing
```

Notes:
- `--comfy-url` defaults to `http://192.168.1.112:8188` (Pearl Star) — no need to pass it.
- First dispatch loads ~20.5 GB unet; `COMFYUI_POLL_TIMEOUT_SEC` defaults to 1800 s. Warm-cache panels ~1.5–3 min each.
- `--skip-existing` makes the run resumable (cache-keyed); safe to re-run after an interruption.
- Single-panel smoke/retry: add `--only-panel ep002_001` (writes a timestamped telemetry sidecar, does not clobber the full-run telemetry).

### 1.3 — Output locations

| Artifact | Path |
|---|---|
| Per-panel (composite + layers + telemetry) | `artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/panels_v5/ep_002/<panel_id>/composite.png` |
| Operator-flat mirror (one PNG per panel) | `artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/composed_v5_qwen/ep_002/<panel_id>.png` |
| Run telemetry (canonical record) | `artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/panels_v5/ep_002/_run_telemetry.json` |

### 1.4 — Verify panel count = 32

```bash
ls artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/composed_v5_qwen/ep_002/*.png | wc -l
```

Expect `32`. Cross-check the run summary:

```bash
python3 -c "import json,sys; d=json.load(open('artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/panels_v5/ep_002/_run_telemetry.json')); print('total',d['panels_total'],'success',d['success_count'],'fail',d['fail_count'],'val_pass',d['validation_pass_count'])"
```

PASS = `total 32 success 32 fail 0`. Any `fail > 0` → inspect that panel's `summary.reason` (timeout / layer-count-mismatch / OOM hint) and re-run with `--only-panel <id>`. Then run the same bubble/compose/publish tail as ep_001 (§2.D–E) once quality is operator-accepted.

---

## 2. ep_001 — PUBLISH (A–E on the ship branch)

**State:** 35/35 panels rendered + quality-ACCEPTED (OPD-147 Milestone A) at
`artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/composed_v4_qwen/ep_001/`.
**Publish = ws_post_pr478_manga_activation steps A–E**, executed on the EXISTING ship branch. The ws forbids forking fresh from main.

```bash
git fetch origin
git checkout agent/post-pr478-manga-activation
git pull --ff-only origin agent/post-pr478-manga-activation
eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
```

### A. Replace mock translations with real Qwen output

```bash
python3 scripts/manga/translate_chapter_script.py \
  --in artifacts/manga/chapter_scripts/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/ep_001.yaml \
  --force
```

Ship-quality (paid, operator-present per Tier policy):

```bash
python3 scripts/manga/translate_chapter_script.py \
  --in artifacts/manga/chapter_scripts/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/ep_001.yaml \
  --backend-overrides ja_JP=google_ai,zh_TW=deepseek,zh_CN=deepseek \
  --force
```

### B. Render panels via ComfyUI

ep_001 panels are already rendered + ACCEPTED at `.../composed_v4_qwen/ep_001/` (35 PNGs). **No re-render.** Proceed to C. (If a fresh render is ever needed, drive from `artifacts/manga/panel_prompts/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/ep_001.panel_prompts.json`.)

### C. Push renders to R2 + commit manifest

> **GATE-OP-1 (operator-only):** requires `R2_ACCOUNT_ID` / `R2_BUCKET` / `R2_ACCESS_KEY_ID` / `R2_SECRET_ACCESS_KEY` in GitHub Actions secrets (Preflight §0.2). If not set, this step fails — stop here until the operator adds them.

```bash
python3 scripts/artifacts/r2_sync.py push \
  --namespace manga_rendered_books \
  --src artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/composed_v4_qwen/ep_001/ \
  --series-id stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying \
  --book-id ep_001 \
  --manifest artifacts/manifests/manga_rendered_books/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/ep_001.yaml

git add artifacts/manifests/manga_rendered_books/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/ep_001.yaml
git commit -m "feat(qa): ep_001 render manifest"
```

### D. Compose per-locale episode strips

Produces Canvas-ready payloads for en_US, ja_JP, zh_TW, zh_CN:

```python
from phoenix_v4.manga.chapter.bubble_render import render_bubbles_on_panels
from phoenix_v4.manga.chapter.webtoon_compose import compose_episode_strips
import yaml, json
from pathlib import Path

chapter = yaml.safe_load(Path("artifacts/manga/chapter_scripts/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/ep_001.yaml").read_text())
manifest = json.load(open("artifacts/manga/panel_prompts/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/ep_001.panel_prompts.json"))
# … reconstruct panel_images_manifest from the composed_v4_qwen/ep_001 dir …

for locale in ["en_US", "ja_JP", "zh_TW", "zh_CN"]:
    bubbled = render_bubbles_on_panels(
        chapter_script=chapter,
        lettering_spec=chapter,                # v3 schema; same fields
        panel_images_manifest=panel_images_manifest,
        bubble_style_config=None,
        out_dir=Path(f"out/bubbled/{locale}/ep_001/"),
        locale=locale,
    )
    payload = compose_episode_strips(
        chapter_script=chapter,
        panel_images_manifest=bubbled,
        out_dir=Path(f"out/episodes/{locale}/ep_001/"),
        episode_id="ep_001",
    )
    print(f"{locale}: {payload['total_height']}px / {len(payload['segments'])} segments")
```

### E. Build WEBTOON Canvas submission package — en_US + zh_TW (OUTWARD-FACING — operator pulls this trigger)

> **GATE-OP-2 (operator-only):** requires the Pearl Star self-hosted-runner marker installed + runner online (Preflight §0.3). This is the outward-facing publish; the operator confirms before submitting.

```bash
# en_US
python3 scripts/publish/webtoon_canvas_upload.py \
  --episodes out/episodes/en_US/ep_001/ \
  --series-id stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying \
  --episode-id ep_001

# zh_TW
python3 scripts/publish/webtoon_canvas_upload.py \
  --episodes out/episodes/zh_TW/ep_001/ \
  --series-id stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying \
  --episode-id ep_001
```

(ja_JP → LINE Manga Indies connector pending; not in this ship.)

---

## 3. What is BLOCKED and why

| Blocker | Gate | Owner | Blocks | Unblock action |
|---|---|---|---|---|
| Pearl Star ComfyUI `http://192.168.1.112:8188` DOWN (HTTP 000 / timeout) | Preflight §0.1 | operator (rig) | **Everything** — ep_002 render AND ep_001 publish-by-render | Power/start rig + ComfyUI; `curl -s -m 6 .../system_stats` returns JSON |
| R2 secrets not in GitHub Actions secrets | GATE-OP-1 | operator | ep_001 publish step C (R2 push) | Add `R2_ACCOUNT_ID` / `R2_BUCKET` / `R2_ACCESS_KEY_ID` / `R2_SECRET_ACCESS_KEY` at repo Actions secrets |
| Pearl Star self-hosted-runner marker not installed / runner offline | GATE-OP-2 | operator (SSH) | ep_001 publish step E (Canvas, Actions-driven) | `ssh pearlstar.tail7fd910.ts.net` → `git pull origin main` → `bash scripts/agent/install_pearl_star_marker.sh` → `python3 scripts/agent/assert_remote.py` (expect "✓ remote-mode active: pearl-star") |

ep_002 render (§1) needs ONLY the endpoint (§0.1) — it is local and does not require GATE-OP-1/2. The R2 + runner gates apply only to the outward ep_001 publish tail (§2 C/E).

---

## 4. When Pearl Star is online, do X

**Run Preflight §0 (all 3 green) → fire the ep_002 render in §1.2 → verify 32 panels in §1.4; in parallel, once GATE-OP-1 + GATE-OP-2 are green, walk ep_001 publish A→E on branch `agent/post-pr478-manga-activation`, with the operator pulling the step E Webtoon Canvas trigger (en_US + zh_TW).**
