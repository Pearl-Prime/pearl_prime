# Manga #3075 — Pearl Star REAL L1/L3/L4 Operator Memo

**Date:** 2026-07-08 · **Verified main HEAD:** `9f70a3d6ec` (PR #4725 merged)
**Lane:** M5 stillness pilot — replace INTERIM L1/L3/L4 with REAL bank renders

---

## Live audit (this session)

| Check | Result |
|---|---|
| PR #4725 (M6 blind-10 + manifest bridge) | **MERGED** @ `9f70a3d6ec` |
| PR #3075 (queue-unblock deploy bundle) | **OPEN** — deploy when CJK lane frees GPU |
| `generate_assembly_manifest.py` + ep_001 0-INTERIM | **On main** (L0/L2 only; 35 panels) |
| Stillness L1/L3/L4 bank PNGs (local) | **6/6 REAL** on disk (≥50KB; Jul 2026 pilot jobs 495–497) |
| `demo_alarm_metaphor_6p_REAL_pilot` assembly | **0 INTERIM** provenance table present |
| `RESUME_COMMANDS.sh` contract | **Was broken** (`out_path=` unsupported) — fixed in `enqueue_stillness_real_layers.py` + `out_path` alias on `enqueue_panel_job` |
| Pearl Star SSH from Mac agent | **BLOCKED** (permission denied `100.92.68.74`) — operator must run on-box or with working SSH key |
| M5 at catalog scale | **NO** — 1 pilot series with REAL L1/L3/L4; 34 M3 flagships + warrior/cognitive INTERIM |

---

## Prerequisites

1. **Pearl Star reachable** — Tailscale/SSH to `pearl_star` (or `ahjan108@100.92.68.74`)
2. **Queue RUNNING** — `pscli status` must not show PAUSED; zombie `doing` jobs cleared (PR #3075 deploy when ready)
3. **GPU lane** — OPD-20260629-003: CJK atom lane owns GPU first; manga is **LOW priority** — do not preempt
4. **Repo synced on Pearl Star** — `cd ~/phoenix_omega && git pull` to branch containing this memo
5. **RAP** — queue-first only; never hit ComfyUI `:8188` directly for >10s work

Optional Mac-side queue env (Case C):

```bash
eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
# or source ~/phoenix_omega/.pearl_star_queue.env after operator export
```

---

## Exact run path (canonical)

### Step 0 — Preflight

```bash
cd /path/to/phoenix_omega
git fetch origin && git checkout main && git pull   # or agent/manga-3075-* branch
ssh pearl_star 'set -a; . /etc/pearl-star/queue.env 2>/dev/null; . ~/phoenix_omega/.pearl_star_queue.env 2>/dev/null; set +a; ~/phoenix_omega/scripts/pearl_star/bin/pscli status'
```

### Step 1 — Enqueue stillness L1/L3/L4 (6 images)

```bash
PYTHONPATH=. python3 scripts/manga/enqueue_stillness_real_layers.py
```

Dry-run first:

```bash
PYTHONPATH=. python3 scripts/manga/enqueue_stillness_real_layers.py --dry-run
```

Force re-render (ignore existing local REAL files):

```bash
PYTHONPATH=. python3 scripts/manga/enqueue_stillness_real_layers.py --force
```

**Expected enqueue output:** JSON with `job_id` per layer; `via` = `ssh:pearl_star` (Mac) or `local` (on-box with `PS_QUEUE_DSN`).

**Expected Pearl Star dest paths:** under `/var/lib/pearl-star/manga_out/artifacts/manga/stillness_press__.../image_bank/L{1,3,4}/`.

### Step 2 — Poll jobs

```bash
ssh pearl_star '~/phoenix_omega/scripts/pearl_star/bin/pscli inspect <job_id>'
# or: pscli list --status doing|failed
```

### Step 3 — Fetch REAL PNGs to Mac repo (if enqueued from Mac)

```bash
# Example for one layer — repeat for each job dest_path
scp pearl_star:/var/lib/pearl-star/manga_out/artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/image_bank/L3/kettle_on_burner_boiling.png \
  artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/image_bank/L3/
```

Verify byte floor: each PNG **≥ 50,000 bytes** (CI `check_render_progress_bytes.py`).

### Step 4 — Re-assemble 0-INTERIM demo strip

```bash
PYTHONPATH=. python3 scripts/manga/assemble_from_bank.py \
  --manifest artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/assembly_manifests/demo_alarm_metaphor_6p_REAL_pilot.yaml \
  --out-dir  artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/assembled/demo_alarm_metaphor_6p_real \
  --strip --bubbles --locale en_US
```

Check provenance: `_provenance.md` must show **0 INTERIM** rows.

### Step 5 — Full ep_001 (L0/L2 only; already 0-INTERIM)

```bash
PYTHONPATH=. python3 scripts/manga/generate_assembly_manifest.py \
  --series stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying \
  --profile stillness_en_01 --episode ep_001

PYTHONPATH=. python3 scripts/manga/assemble_from_bank.py \
  --manifest artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/assembly_manifests/ep_001_from_continuity.yaml \
  --out-dir artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/assembled/ep_001_from_continuity/ \
  --bubbles --locale en_US
```

---

## Expected outputs

| Artifact | Path |
|---|---|
| L1 alarm | `artifacts/manga/stillness_press__.../image_bank/L1/wall_alarm_green_idle.png` |
| L3 kettle + cups | `.../image_bank/L3/{kettle_on_burner_boiling,cup_empty,cup_half,cup_full}.png` |
| L4 steam | `.../image_bank/L4/steam_wisp_rising.png` |
| 6p REAL assembly | `.../assembled/demo_alarm_metaphor_6p_real/` + `_provenance.md` |
| 35p ep_001 | `.../assembled/ep_001_from_continuity/` (L0/L2 REAL; no L1/L3/L4 in manifest) |

---

## What still blocks fully real renders at scale

1. **PR #3075 not merged** — on-box deploy (`deploy_manga_queue_unblock.sh`) for zombie reset + `gpu_heavy_lock` + operator-writable `pscli pause`
2. **Pearl Star SSH/auth** — agent session cannot reach box; operator must execute Steps 0–3
3. **CJK GPU priority** — manga batch must wait for OPD-20260629-003 clearance
4. **34 remaining M3 flagships** — no bank contracts + REAL layers beyond stillness pilot
5. **warrior_calm / cognitive_clarity** — INTERIM wiring proofs only (18 layers each)
6. **L2 PuLID stubs** — `image_bank/L2/mira_aoki/*.png` at 132 bytes on Mac; re-run PuLID pilot when GPU free
7. **M6 blind-10** — needs ≥4 genres × 0-INTERIM assembled episodes (stillness = 1 genre)

---

## Legacy RESUME_COMMANDS.sh

Still valid after `out_path` alias fix on `enqueue_panel_job`. Prefer the canonical script above:

`scripts/manga/enqueue_stillness_real_layers.py`

---

## Machine summary

```
manga-3075-runpath=artifacts/qa/manga_3075_operator_memo_2026-07-08.md
manga-3075-enqueue-script=scripts/manga/enqueue_stillness_real_layers.py
manga-3075-local-real-layers=6/6
manga-3075-pr3075=OPEN
manga-3075-pearl-star-reachable=NO (agent session)
```
