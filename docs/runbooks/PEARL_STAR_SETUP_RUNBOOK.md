# Pearl Star — Autonomous Self-Monitoring Setup Runbook

**Last updated:** 2026-06-02
**Owner:** Pearl_Int
**When to use:** Rebuilding Pearl Star from a clean Ubuntu install, or onboarding a new GPU host that will run autonomous (laptop-off) orchestrators that need GitHub CLI + R2 sample uploads. Sister doc: [`skills/pearl-int/references/pearl_star_node_inventory.md`](../../skills/pearl-int/references/pearl_star_node_inventory.md).

## What this gives you

After completing this runbook, Pearl Star can:

1. Commit progress (`gh pr list`, `git push`) under the operator's GitHub identity.
2. Upload artifacts to Cloudflare R2 (`rclone copy ... r2:phoenix-omega-artifacts/...`).
3. Survive operator-laptop-off — the orchestrator runs detached via `nohup` and writes a monitorable log.

## Prerequisites on the operator's laptop

1. Tailscale up; `ssh pearl_star "echo ok"` returns `ok`.
2. macOS Keychain contains, under `service=phoenix-omega`:
   - `GH_TOKEN` (PAT with scopes `repo` + `workflow`)
   - `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_ENDPOINT`, `R2_BUCKET` (R2 bucket-scoped token)
3. `gh` is authenticated locally (`gh auth status` shows the active account). If `GH_TOKEN` is not yet in Keychain but the operator's local `gh` is authenticated, capture it once:
   ```bash
   TOK=$(gh auth token)
   security add-generic-password -s phoenix-omega -a GH_TOKEN -w "$TOK" -U
   security add-generic-password -s phoenix-omega -a GITHUB_TOKEN -w "$TOK" -U
   unset TOK
   ```

## Pearl Star prerequisites (the host itself)

Pearl Star needs (already shipped on the canonical Ubuntu 24.04 image):

| Tool | Why | Already on canonical image? |
|---|---|---|
| `curl` / `wget` | fetch gh + rclone binaries | yes |
| `unzip` | extract rclone archive | yes |
| `git` | clone phoenix_omega | yes |
| `python3` | run repo scripts | yes |
| ComfyUI on `:8188` | render backend | yes (`~/phoenix_server/ComfyUI`) |
| Ollama on `:11434` | Tier-2 LLM (Qwen + Gemma) | yes |

What's **not** on the base image and gets installed by this runbook:

| Tool | Install path | Sudo? |
|---|---|---|
| `gh` (GitHub CLI) | `~/.local/bin/gh` (tarball) | no |
| `rclone` | `~/.local/bin/rclone` (zip) | no |
| `tmux` | **not installed** — substituted by `nohup` | would need sudo; skipped |

## Step 1 — Install `gh` user-local

```bash
ssh pearl_star 'mkdir -p ~/.local/bin
cd /tmp
GH_VER="2.45.0"
curl -fsSL -o gh.tar.gz "https://github.com/cli/cli/releases/download/v${GH_VER}/gh_${GH_VER}_linux_amd64.tar.gz"
tar -xzf gh.tar.gz
cp gh_${GH_VER}_linux_amd64/bin/gh ~/.local/bin/gh
chmod +x ~/.local/bin/gh
rm -rf gh.tar.gz gh_${GH_VER}_linux_amd64
~/.local/bin/gh --version
grep -q "HOME/.local/bin" ~/.bashrc || echo "export PATH=\$HOME/.local/bin:\$PATH" >> ~/.bashrc'
```

**Verify:** `~/.local/bin/gh --version` prints `gh version 2.45.0` (or newer).

## Step 2 — Install `rclone` user-local

```bash
ssh pearl_star 'mkdir -p ~/.local/bin
cd /tmp
RCLONE_VER="v1.69.0"
curl -fsSL -o rclone.zip "https://downloads.rclone.org/${RCLONE_VER}/rclone-${RCLONE_VER}-linux-amd64.zip"
unzip -q rclone.zip
cp rclone-*-linux-amd64/rclone ~/.local/bin/rclone
chmod +x ~/.local/bin/rclone
rm -rf rclone.zip rclone-*-linux-amd64
~/.local/bin/rclone version'
```

**Verify:** `~/.local/bin/rclone version` prints `rclone v1.69.0` (or newer).

## Step 3 — Auth `gh` on Pearl Star (no token in chat / logs)

Pipe the operator's existing token from Keychain → SSH stdin → `gh auth login --with-token`. The token never appears on a command line, never echoes to stdout, and never gets logged:

```bash
security find-generic-password -s phoenix-omega -a GH_TOKEN -w 2>/dev/null \
  | ssh pearl_star '~/.local/bin/gh auth login --with-token'

# Verify
ssh pearl_star '~/.local/bin/gh auth status'
```

Expected: `✓ Logged in to github.com account <name>`, scopes include `repo` and `workflow`.

If the host already has a stale partial auth, run `ssh pearl_star '~/.local/bin/gh auth logout'` first.

## Step 4 — Configure `rclone` R2 remote (no secrets in chat / logs)

Pull R2 creds from Keychain on the laptop, push via SSH environment, write `~/.config/rclone/rclone.conf` remotely, then unset locally. Pass `no_check_bucket=true` — the R2 token is bucket-scoped and has no account-level `CreateBucket` permission, so the default upload path 403s otherwise.

```bash
AK=$(security find-generic-password -s phoenix-omega -a R2_ACCESS_KEY_ID -w 2>/dev/null)
SK=$(security find-generic-password -s phoenix-omega -a R2_SECRET_ACCESS_KEY -w 2>/dev/null)
EP=$(security find-generic-password -s phoenix-omega -a R2_ENDPOINT -w 2>/dev/null)

ssh pearl_star "AK='$AK' SK='$SK' EP='$EP' bash -s" <<'REMOTE' >/dev/null 2>&1
~/.local/bin/rclone config create r2 s3 \
  provider Cloudflare \
  access_key_id "$AK" \
  secret_access_key "$SK" \
  endpoint "$EP" \
  no_check_bucket true
unset AK SK EP
REMOTE

unset AK SK EP
```

> **Important:** `rclone config create` / `update` prints the config it just wrote — that includes the secret. If you run interactively (not redirected to `/dev/null`), the secret will land in your shell history / terminal scroll-back / agent transcript. Always redirect those subcommands when piping Keychain values through.

**Verify (does not print secrets):**

```bash
ssh pearl_star '~/.local/bin/rclone listremotes'
# expected: r2:
```

## Step 5 — End-to-end smoke

```bash
ssh pearl_star 'TS=$(date +%s)
echo "phoenix-omega self-monitoring smoke @ $(date -u +%Y-%m-%dT%H:%M:%SZ)" > /tmp/po_smoke_$TS.txt

~/.local/bin/rclone copy /tmp/po_smoke_$TS.txt r2:phoenix-omega-artifacts/test/
~/.local/bin/rclone ls   r2:phoenix-omega-artifacts/test/ | grep "po_smoke_$TS"
~/.local/bin/rclone delete r2:phoenix-omega-artifacts/test/po_smoke_$TS.txt
~/.local/bin/rclone ls   r2:phoenix-omega-artifacts/test/ | grep -c "po_smoke_$TS"  # expected: 0

rm -f /tmp/po_smoke_$TS.txt'

ssh pearl_star 'cd ~/phoenix_omega 2>/dev/null && ~/.local/bin/gh pr list --limit 1'
```

A passing smoke confirms: upload + verify + delete + confirm-deleted + repo-aware `gh` all work in one shot.

## Step 6 — Clone `phoenix_omega` (public repo, no auth needed)

```bash
ssh pearl_star 'cd ~ && [ -d phoenix_omega/.git ] && cd phoenix_omega && git pull origin main \
  || git -c http.postBuffer=524288000 clone https://github.com/Ahjan108/phoenix_omega_v4.8.git phoenix_omega'

ssh pearl_star 'cd ~/phoenix_omega && git log --oneline -1'
```

`http.postBuffer=524288000` mitigates the `fatal: fetch-pack: invalid index-pack output` transient that can hit on slow links during the initial pack negotiation.

## Step 7 — Long-running orchestrator pattern (no tmux)

For the operator's "laptop-off" 5-day run:

```bash
ssh pearl_star
cd ~/phoenix_omega
git pull origin main

LOG="artifacts/manga/bulk_logs/<scope>_$(date +%Y%m%d_%H%M%S).log"
mkdir -p "$(dirname "$LOG")"

nohup bash scripts/manga/<orchestrator>.sh > "$LOG" 2>&1 &
disown
echo "PID=$! LOG=$LOG"
exit
```

**Monitor (from any device):**

```bash
ssh pearl_star "tail -100 ~/phoenix_omega/<LOG>"
ssh pearl_star "pgrep -af <orchestrator>"
```

**Abort:**

```bash
ssh pearl_star "pkill -f <orchestrator>"
```

The orchestrator must be **resumable** (idempotent re-run that skips completed work via sentinel files) so an interruption is recoverable by simply re-running the same `nohup` command.

## What this runbook does NOT cover

- Installing `tmux` (requires sudo). If the operator wants tmux UX, they run `sudo apt install -y tmux git-lfs` on Pearl Star and the orchestrator's start command becomes `tmux new -d -s <name> "bash ..."`. The `nohup` pattern in Step 7 already covers the laptop-off use case without it.
- Installing CUDA / Python deps — those land via the canonical `~/phoenix_server/ComfyUI/venv` setup.
- Cloudflare R2 bucket creation — operator-territory (`dash.cloudflare.com → R2`). If `rclone lsf r2:<bucket>` returns `AccessDenied`, the bucket either does not exist or the token lacks bucket-level scope; surface to operator, do not auto-create.

## Token rotation hygiene

If at any point a credential value enters the chat transcript, agent stdout, or a log file (operator paste, `rclone config create` echo, error message OCR), Pearl_Int treats it as compromised and asks the operator to rotate:

- **`GH_TOKEN`:** revoke at github.com/settings/tokens, generate a new fine-grained PAT (scopes: `repo`, `workflow`), re-add to Keychain (`-U`), re-auth Pearl Star (Step 3).
- **R2 access key:** Cloudflare Dashboard → R2 → Manage R2 API Tokens → roll the token, copy the new Secret Access Key once, re-add to Keychain (`-U`), re-run Step 4.

Account IDs and endpoint URLs are not authentication material on their own — only access keys, secret keys, and tokens rotate.
