# Pearl Star Job Queue V1 — Phase A install RUNBOOK (operator-run)

**You are the operator.** This runbook is the exact, ordered set of commands you
run on Pearl Star to stand up the Phase A job queue. Every command uses *your*
sudo — nothing here has been executed for you. There is also a NOPASSWD option
(§B) if you'd rather grant a one-time passwordless-sudo drop-in and let an
execution agent run it.

- **Authority:** `docs/specs/PEARL_STAR_JOB_QUEUE_V1_SPEC.md` (§8 Phase A) ·
  `docs/PEARL_STAR_JOB_QUEUE_V1_SESSION_HANDOFF_20260611.md` (§5).
- **Tier policy:** every component is Tier-2 (free + local) per `CLAUDE.md` —
  Postgres, Procrastinate, ComfyUI, Ollama, CosyVoice2. **No paid LLM API.**
- **Host:** `ssh pearl_star` (Tailscale `100.92.68.74`, user `ahjan108`).
- **Contract:** see `scripts/pearl_star/contract/PROCRASTINATE_CONTRACT.md` for
  the schema/venv/queue/stall contract every piece agrees on.

> The install scripts are **idempotent** — re-running any of them is safe; each
> echoes what it does and SKIPs work already done.

---

## 0. Prerequisites (one-time, on Pearl Star)

```bash
ssh pearl_star
# Confirm the box + GPU:
uptime ; nvidia-smi --query-gpu=name,memory.total,memory.used --format=csv
# Confirm ComfyUI checkout location (the kit assumes ~/phoenix_server/ComfyUI):
ls -d ~/phoenix_server/ComfyUI

# Get the repo onto Pearl Star (or pull latest) so the install scripts are present.
# (Use whatever clone path you already use; the scripts are relative-path safe.)
cd ~/phoenix_omega   # <- your repo checkout on Pearl Star
git fetch origin && git checkout <this-branch-or-merge-commit>
cd scripts/pearl_star/install
```

**Edit `00_config.sh` ONLY if your paths differ from the defaults** (ComfyUI
home, user). The defaults match `pearl_star_dispatcher.py`
(`~/phoenix_server/ComfyUI`, user `ahjan108`). Also review `PS_CPQ_PIN` — pin it
to a real ComfyUI-Persistent-Queue commit SHA after a quick upstream check
(spec §14 stale-extension risk).

---

## A. OPERATOR PATH (interactive sudo) — recommended

Run the four install steps in order. You'll be prompted for your sudo password.

```bash
cd ~/phoenix_omega/scripts/pearl_star/install

sudo -v                       # cache sudo creds for the session
bash 01_postgres17.sh         # PostgreSQL 17 + db/role/schema + synchronous_commit=on
bash 04_directories.sh        # pearl-star user + /opt,/var/lib,/var/log dirs + tmpfs heartbeat
bash 02_procrastinate.sh      # venv /opt/pearl-star/venv + procrastinate + schema --apply + deploy sources
bash 03_comfyui_persistent_queue.sh   # ComfyUI-Persistent-Queue custom_node (pinned)
```

> Order note: run `04_directories.sh` (creates the `pearl-star` user + dirs)
> **before** `02_procrastinate.sh` (which `chown`s the venv to that user).
> `01` first because `02` applies the Procrastinate schema into the DB `01`
> created.

### A.1 Write the queue env file + install the systemd units

The units read `/etc/pearl-star/queue.env`. Generate it from `00_config.sh`, then
install the 5 unit files from `scripts/pearl_star/systemd/`.

```bash
cd ~/phoenix_omega/scripts/pearl_star

# --- queue.env (DSN + tunables; sourced by every unit) ---
. install/00_config.sh
sudo install -d -m 0750 /etc/pearl-star
sudo tee /etc/pearl-star/queue.env >/dev/null <<EOF
PS_QUEUE_DSN=$(ps_dsn)
PS_PG_SCHEMA=${PS_PG_SCHEMA}
PS_COMFY_URL=${PS_COMFY_URL}
PS_OUTPUT_DIR=${PS_OUTPUT_DIR}
PS_LIB_DIR=${PS_LIB_DIR}
PS_LOG_DIR=${PS_LOG_DIR}
PS_DLQ_DIR=${PS_DLQ_DIR}
PS_ALERT_DIR=${PS_ALERT_DIR}
PS_HEARTBEAT_DIR=${PS_HEARTBEAT_DIR}
PS_HEARTBEAT_FORENSIC=${PS_HEARTBEAT_FORENSIC}
PS_HEARTBEAT_INTERVAL_S=${PS_HEARTBEAT_INTERVAL_S}
PS_WATCHDOG_TICK_S=${PS_WATCHDOG_TICK_S}
PS_HEARTBEAT_SILENCE_KILL_S=${PS_HEARTBEAT_SILENCE_KILL_S}
PS_SIGTERM_GRACE_S=${PS_SIGTERM_GRACE_S}
EOF
sudo chmod 0640 /etc/pearl-star/queue.env   # contains the DB password — keep tight

# --- install the 5 units ---
sudo install -m 0644 systemd/comfyui.service                 /etc/systemd/system/comfyui.service
sudo install -m 0644 systemd/procrastinate-worker.service    /etc/systemd/system/procrastinate-worker.service
sudo install -m 0644 systemd/pearl-star-watchdog.service     /etc/systemd/system/pearl-star-watchdog.service
sudo install -m 0644 systemd/pearl-star-monitor.service      /etc/systemd/system/pearl-star-monitor.service
sudo install -d /etc/systemd/system/postgresql@17-main.service.d
sudo install -m 0644 systemd/postgresql@17-main.service.d/pearl-star.conf \
     /etc/systemd/system/postgresql@17-main.service.d/pearl-star.conf

sudo systemctl daemon-reload
sudo systemctl enable --now postgresql@17-main comfyui procrastinate-worker \
     pearl-star-watchdog pearl-star-monitor
```

> **Before enabling `comfyui.service`**, open it and confirm `User=`,
> `WorkingDirectory=`, and the `ExecStart` python path match this box. If you
> already run ComfyUI another way (tmux, a different unit), skip enabling this
> one — but make sure ComfyUI is up on `127.0.0.1:8188` before the smokes.

### A.2 Verify the units are healthy

```bash
systemctl --no-pager status postgresql@17-main comfyui procrastinate-worker \
  pearl-star-watchdog pearl-star-monitor | sed -n '1,40p'
pscli status        # should return in < 2 s (spec §13 criterion 5)
```

Now jump to **§C — Acceptance smokes**.

---

## B. NOPASSWD AGENT PATH (optional) — grant, run, then REMOVE

If you'd rather have an execution agent run the install unattended, grant a
**scoped, temporary** passwordless-sudo drop-in for the install user, let the
agent run §A + §C, then **remove the drop-in**. Do not leave NOPASSWD in place.

### B.1 Grant (you do this once, with your sudo)

```bash
# Replace ahjan108 if the agent runs as a different account.
echo 'ahjan108 ALL=(ALL) NOPASSWD: ALL' | sudo tee /etc/sudoers.d/99-pearl-star-install
sudo chmod 0440 /etc/sudoers.d/99-pearl-star-install
sudo visudo -cf /etc/sudoers.d/99-pearl-star-install   # syntax check — MUST say "parsed OK"
```

> Tighter alternative (recommended): scope it to just the binaries the install
> touches instead of `ALL`:
> ```
> ahjan108 ALL=(ALL) NOPASSWD: /usr/bin/apt-get, /usr/bin/systemctl, /usr/bin/install, /usr/sbin/useradd, /usr/sbin/groupadd, /bin/systemd-tmpfiles, /usr/bin/tee, /usr/bin/sed, /bin/su, /usr/bin/python3
> ```

### B.2 Agent runs the install

The agent runs exactly the §A commands (01 → 04 → 02 → 03, then §A.1) and the
§C smokes A1/A2. **A3 reboots the box** — only run A3 if you've explicitly told
the agent to, and expect the SSH session to drop for ~5 minutes.

### B.3 REMOVE the drop-in (mandatory post-install)

```bash
sudo rm -f /etc/sudoers.d/99-pearl-star-install
sudo visudo -c            # confirm sudoers still parses cleanly
```

The queue keeps running after removal — the systemd units don't need NOPASSWD;
only the one-time install did.

---

## C. Acceptance smokes (spec §13 / handoff §5.3)

Evidence is appended to `${PS_EVIDENCE_DIR:-/tmp/pearl_star_phase_a_evidence}/`.
Set `PS_EVIDENCE_DIR` to a path you'll later copy into the repo evidence bundle
`artifacts/qa/pearl_star_phase_a_install_evidence_20260611/`.

```bash
cd ~/phoenix_omega/scripts/pearl_star
. install/00_config.sh
export PS_EVIDENCE_DIR=~/pearl_star_phase_a_evidence
```

### A1 — book-cover dispatch (pass: COMPLETED + output file < 60 s)

```bash
bash smoke/A1_book_cover_dispatch.sh
```
Expect: an image in `/var/lib/pearl-star/output/` and `pscli status` showing the
job succeeded, all within 60 s.

### A2 — watchdog stall detect + recover (pass: STALL_WARN→KILL→retry succeeds)

```bash
bash smoke/A2_watchdog_stall.sh
```
Expect: `watchdog.log` shows `STALL_WARN` (~30 s) then `AUTO-KILL reason=stall`
(~60 s); after `FORCE_STALL` is cleared, the retry lands a real output. (This
script toggles one `FORCE_STALL=1` line in `/etc/pearl-star/queue.env` and
restarts the worker — needs sudo.)

### A3 — reboot persistence (pass: 5/5 complete post-reboot, 0 dup, 0 loss)

> ############################################################
> ##  A3 REBOOTS PEARL STAR (`sudo systemctl reboot`).      ##
> ##  The box goes DOWN ~5 minutes. Do NOT run during a     ##
> ##  production batch. It is TWO-PHASE — enqueue, reboot,   ##
> ##  then SSH back and verify.                              ##
> ############################################################

```bash
bash smoke/A3_reboot_persistence.sh enqueue   # queue 5 jobs (PAUSED) + snapshot
bash smoke/A3_reboot_persistence.sh reboot    # type REBOOT to confirm; box reboots
# ... wait ~5 min ...
ssh pearl_star
cd ~/phoenix_omega/scripts/pearl_star && . install/00_config.sh
export PS_EVIDENCE_DIR=~/pearl_star_phase_a_evidence
bash smoke/A3_reboot_persistence.sh verify    # resume + assert 5/5, 0 dup, 0 loss
```

### Six acceptance criteria (spec §13 — all must pass for Phase A DONE)

| # | Criterion | How |
|---|---|---|
| 1 | Reboot-resume | A3 (scaled to 100 mixed jobs for the full criterion) |
| 2 | Stall detection (timeout) | A2 |
| 3 | Crash detection (SIGKILL worker) | `sudo systemctl kill -s SIGKILL procrastinate-worker` mid-job → watchdog logs `WORKER_CRASHED` after >90 s silence → fresh worker completes the retry |
| 4 | VRAM reclaim | after A2's AUTO-KILL, `pscli vram-snapshot` (or watchdog log "VRAM reclaim OK") shows baseline within 30 s |
| 5 | Operator CLI | `pscli status` < 2 s; `pscli pause` halts dispatch, `pscli resume` restarts |
| 6 | Tier policy | from the repo root on any box: `python3 scripts/ci/audit_llm_callers.py` → clean |

### Evidence bundle

Copy the evidence into the repo and open a PR (Pearl_Int / Pearl_PM):

```bash
mkdir -p artifacts/qa/pearl_star_phase_a_install_evidence_20260611
cp ~/pearl_star_phase_a_evidence/*  artifacts/qa/pearl_star_phase_a_install_evidence_20260611/
systemctl --no-pager status postgresql@17-main comfyui procrastinate-worker \
  pearl-star-watchdog pearl-star-monitor \
  > artifacts/qa/pearl_star_phase_a_install_evidence_20260611/systemd_status.txt
nvidia-smi > artifacts/qa/pearl_star_phase_a_install_evidence_20260611/nvidia-smi_pre_post.txt
```

Then append the Phase A PASS block to `docs/specs/PEARL_STAR_JOB_QUEUE_V1_SPEC.md
§13` (handoff §5.6) with verbatim A1/A2/A3 evidence.

---

## D. Day-2 operator quick reference

```bash
pscli status                       # depth + active workers + recent stalls + dlq
pscli list --workload t2i --status todo
pscli inspect <job_id>             # job + heartbeat history + retries
pscli pause / pscli resume         # halt / restart dispatch
pscli drain                        # pre-reboot: pause + wait for in-flight == 0
pscli kill <job_id>                # manual SIGTERM->SIGKILL of the running worker
pscli requeue <job_id>             # failed/stuck -> todo
pscli vram-snapshot                # nvidia-smi diff vs last call
pscli unload-comfyui               # POST /free (evict checkpoint before an llm job)

journalctl -u procrastinate-worker -f      # live worker log
journalctl -u pearl-star-watchdog -n 50    # watchdog decisions
tail -f /var/log/pearl-star/watchdog.log   # stall/kill audit trail
ls /var/lib/pearl-star/operator_alerts/    # alert drops
```

### Clean reboot (no test)
```bash
pscli drain && sudo systemctl reboot
# after boot: units auto-resume; pending jobs dispatch on their own.
```

---

## E. Troubleshooting

| Symptom | Check |
|---|---|
| `pscli status` says DB UNREACHABLE | `systemctl status postgresql@17-main`; `psql "$PS_QUEUE_DSN" -c 'select 1'` |
| A1 no output in 60 s | ComfyUI up? `curl http://127.0.0.1:8188/system_stats`; `journalctl -u comfyui -n 50`; worker log |
| worker won't start | `journalctl -u procrastinate-worker -n 50`; confirm `/etc/pearl-star/queue.env` exists + DSN valid; venv present at `/opt/pearl-star/venv` |
| 03 errors "custom_nodes not found" | set `PS_COMFY_HOME` to the real ComfyUI checkout, re-run `03_*.sh` |
| dispatch won't resume | `ls /var/lib/pearl-star/queue.paused` — `pscli resume` removes it |
| audit_llm_callers flags something | nothing in this kit calls a paid API; re-run `python3 scripts/ci/audit_llm_callers.py` and read the offending path |
