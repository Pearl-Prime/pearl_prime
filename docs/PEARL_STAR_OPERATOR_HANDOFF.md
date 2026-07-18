# Pearl Star — Operator handoff

**Purpose:** One place for networking, SSH, env vars, services, repo expectations, and remote access.  
**Audience:** Pearl_Dev / operator (Mac + Ubuntu Pearl Star).  
**Last updated:** 2026-04-17

---

## 1. What Pearl Star is

Ubuntu box used as the **local inference server** for Phoenix Omega:

| Service | Port | Role |
|--------|------|------|
| SSH | 22 | Admin |
| Ollama | 11434 | LLM API (`/v1` OpenAI-compatible); tags at `/api/tags` |
| ComfyUI | 8188 | Image gen (`/system_stats`, workflows) |
| CosyVoice2 | 9880 | CJK TTS — **FastAPI:** `GET /api/v1/health`, `POST /api/v1/tts` (WAV body) |

**SSH user:** `ahjan108` (not `ahjan`).  
**Hostname:** often `pearlstar`; mDNS may answer as `pearlstar.local` on the LAN.

---

## 2. LAN IP and “no magic IP” in the repo

- Home DHCP **can change** the server’s IPv4 after reboot, Wi‑Fi vs Ethernet, or router changes.
- **Do not rely on a fixed octet** in docs or in your head. Tracked code uses **`PEARL_STAR_IP`** (and explicit `COMFYUI_URL` / `QWEN_BASE_URL` / `COSYVOICE_URL` where needed).
- Helper module: `scripts/ci/pearl_star_urls.py` — builds default URLs **only** from `PEARL_STAR_IP` (no hardcoded LAN IP in those defaults).

**Router:** Create a **DHCP reservation** (MAC → fixed IPv4) for the **interface you actually use** (Wi‑Fi `wlp…` or `enp…`). Example collected once on-box:

- Default route was via **`wlp7s0`** → MAC **`50:ee:32:af:09:87`** (reserve that if Wi‑Fi stays primary).
- Ethernet **`enp8s0`** had a different MAC — reserve that instead if you move to wired-only.

---

## 3. macOS Keychain (operator Mac)

**Service name:** `phoenix-omega`  
**Account name:** equals the **env var name** (e.g. `PEARL_STAR_IP`).

Minimum set for Pearl-backed work:

| Account (env var) | Example value shape |
|--------------------|----------------------|
| `PEARL_STAR_IP` | Current LAN IPv4 only (no `http://`) |
| `COMFYUI_URL` | `http://<PEARL_STAR_IP>:8188` |
| `COSYVOICE_URL` | `http://<PEARL_STAR_IP>:9880` |
| `QWEN_BASE_URL` | `http://<PEARL_STAR_IP>:11434/v1` |

**Load into shell (repo root):**

```bash
eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
python3 scripts/ci/check_integration_env.py
```

**Update a value from CLI** (account = env name, service fixed):

```bash
security add-generic-password -U -a PEARL_STAR_IP -s phoenix-omega -w "<NEW_IPV4>" login.keychain-db
# repeat for COMFYUI_URL, COSYVOICE_URL, QWEN_BASE_URL as needed
```

Canonical registry: `docs/INTEGRATION_CREDENTIALS_REGISTRY.md`  
Machine list: `scripts/ci/integration_env_registry.py`

---

## 4. SSH (operator Mac → Pearl Star)

**`~/.ssh/config`** (on the Mac, not in git) should look like:

```sshconfig
Host pearl_star
  HostName <current-lan-ipv4-or-pearlstar.local>
  User ahjan108
  AddressFamily inet
  IdentityFile ~/.ssh/id_ed25519_pearl_star
```

- **`User` must be `ahjan108`** for this server.
- **`AddressFamily inet`** avoids some IPv6/mDNS oddities when you use `.local`.
- **Key auth:** `ssh-copy-id` must be run **from the Mac**; public key lives in Pearl’s `~/.ssh/authorized_keys`.

**Test:**

```bash
ssh pearl_star "hostname && uname -a"
```

---

## 5. Ollama model naming

**Default on Pearl Star:** **`qwen2.5:14b`** (not `qwen3:14b` in operator docs).  
Verify on server: `ollama list` / `curl -s localhost:11434/api/tags`.

---

## 6. CosyVoice2 API (repo alignment)

Live server speaks:

- `GET  http://<host>:9880/api/v1/health`
- `POST http://<host>:9880/api/v1/tts` with JSON `{"text":"…","speaker":"chinese_female"}` (etc.) — response is **WAV** bytes.

Presenter script was updated to use this path: `scripts/audio/generate_presenter_audio.py`.  
Korean: no Korean built-in on that stack — **Edge-TTS** path for `briefing_kr` / `ko` locale.

---

## 7. Pearl Star `~/.bashrc` (PATH breakage)

**Symptom:** `unexpected EOF while looking for matching '"'`

**Cause:** A line like `export PATH="$HOME/.local/bin:$PATH` **without a closing quote** makes bash treat the rest of the file as inside a string.

**Fix:** One line:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

**Idempotent prepend** (optional, avoids duplicate `.local/bin` on repeated `source`):

```bash
case ":$PATH:" in
  *":$HOME/.local/bin:"*) ;;
  *) export PATH="$HOME/.local/bin:$PATH" ;;
esac
```

**Repo helper** (run on server after `scp` or git pull):

```bash
python3 scripts/pearl_star/fix_bashrc_local_bin_path.py --dry-run
python3 scripts/pearl_star/fix_bashrc_local_bin_path.py
```

---

## 8. Remote access — what actually works

**Fact:** `192.168.1.x` is **private**. From a random remote network, **SSH to the home LAN IP will fail** unless you add a **bridge**.

**Tailscale (recommended):**

1. **On Pearl Star** (while you have console or LAN SSH): install + `sudo tailscale up`, same Tailscale account as your Mac.
2. **On Mac:** install Tailscale, same account.
3. **Remote SSH:** use Pearl’s **Tailscale name / `tailscale ip -4`**, not `192.168.1.x`.

**Installing Tailscale on the Mac alone does nothing for Pearl** until the **server** (or another home jump host) is on the same tailnet.

**Alternatives:** home router **WireGuard/OpenVPN**, **reverse SSH** to a VPS, **outbound-only** health pings (e.g. cron + healthchecks.io) for “is it up” without shell access.

---

## 9. LAN migration checklist (already executed in-session; reuse on next move)

1. **Discovery:** `grep` repo for old IP; `env | grep` old IP after Keychain load; read `~/.ssh/config`.
2. **Keychain:** update `PEARL_STAR_IP`, `COMFYUI_URL`, `COSYVOICE_URL`, `QWEN_BASE_URL`.
3. **SSH:** `HostName` + confirm `User ahjan108` + key path.
4. **Repo:** no hardcoded Pearl LAN IP in touched scripts — use `scripts/ci/pearl_star_urls.py` + docs that say “set `PEARL_STAR_IP`”.
5. **Router:** DHCP reservation for the NIC MAC you use.
6. **Remote:** Tailscale on server + Mac (or other VPN).

**Commit reference (repo IP cleanup):** search git log for message containing `hardcoded Pearl Star LAN` / `PEARL_STAR_IP` (e.g. `418886f3a9` on a feature branch — verify on `main` after merge).

---

## 10. Acceptance tests (from Mac, Keychain loaded)

```bash
cd /path/to/phoenix_omega
eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
python3 scripts/ci/check_integration_env.py

ssh pearl_star "echo SSH_OK && hostname"

curl -sS --max-time 8 "${QWEN_BASE_URL%/v1}/api/tags" | head -c 200
curl -sS --max-time 8 "${COMFYUI_URL%/}/system_stats" | head -c 200
curl -sS --max-time 8 "${COSYVOICE_URL%/}/api/v1/health"
```

Adjust URLs if your env uses trailing slashes differently.

---

## 11. Related docs (repo)

- `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` — credentials / env names  
- `docs/UBUNTU_PRODUCTION_SERVER_SETUP.md` — server install, ports, env examples  
- `docs/SESSION_HANDOFF_2026_04_09.md` — historical PR context (Pearl Star wiring)  
- `scripts/pearl_star/fix_bashrc_local_bin_path.py` — bashrc PATH helper  
- `scripts/ci/pearl_star_urls.py` — URL defaults from `PEARL_STAR_IP`

---

## 12. NEXT_ACTION (standing)

- [ ] **DHCP reservation** on home router for Pearl’s active NIC MAC → stable IPv4.  
- [ ] **Tailscale** (or equivalent) on **Pearl Star + Mac** if remote shell/ops is required.  
- [ ] After any IP change: **Keychain** + **`~/.ssh/config` `HostName`** + `grep` repo for stray old IPs.

---

## CLOSEOUT stub (for agents)

- **session_id:** (fill)  
- **commit_sha:** (fill if repo PR merged)  
- **Keychain items touched:** (list old → new)  
- **SSH config:** changed / confirmed  
- **Acceptance:** SSH / Ollama / ComfyUI / CosyVoice / `check_integration_env` — pass/fail  

---

*This file is operator truth for Pearl Star connectivity; if it disagrees with live `ip a` or router DHCP, trust live state and update this doc.*
