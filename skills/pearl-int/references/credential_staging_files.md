# Pearl_Int — Gitignored Credential Staging Files

When the operator has just generated new credentials in a developer portal
(Cloudflare R2 token, ElevenLabs key, RunComfy token, etc.) and pasted them
into a local-only file, Pearl_Int reads that file and loads the values into
macOS Keychain in a single non-interactive pass — no operator paste prompts.

## Where credentials are staged

The repo's `.gitignore` reserves these paths as local-only credential stashes
that operators may use as a transient hand-off to Pearl_Int:

| File                              | Service             |
|-----------------------------------|---------------------|
| `docs/cloudflare_api.txt`         | Cloudflare + R2     |
| `docs/cloudflare_credentials.txt` | Cloudflare + R2 (alt) |
| `.claude/cloudflare_credentials.txt` | Cloudflare + R2 (alt) |
| `docs/11.txt`                     | ElevenLabs          |
| `config/local/ghl_funnel_webhook.url` | GHL freebie inbound webhook (one-line URL) |
| `cloudflare_workers_ai.txt`       | Workers AI          |

These files MUST stay gitignored. Pearl_Int reads them; it never commits
them, never echoes their contents, and never includes their values in tool
output that gets logged.

## The Cloudflare R2 token result page format

When the operator creates an R2 API token at *Cloudflare Dashboard → R2 →
Manage R2 API Tokens*, Cloudflare's result page is shown once and contains:

```
CLOUDFLARE_ACCOUNT_ID=<32-char hex>
CLOUDFLARE_API_TOKEN=cfut_<48 chars>

Use the following credentials for S3 clients:
Access Key ID
<32-char hex>
Click to copy
Secret Access Key
<64-char hex>
Click to copy
Use jurisdiction-specific endpoints for S3 clients:
DefaultEuropean Union (EU)
https://<32-char hex>.r2.cloudflarestorage.com
```

The operator typically pastes this verbatim into `docs/cloudflare_api.txt`.

## How Pearl_Int parses + loads

```bash
FILE=/Users/<user>/phoenix_omega/docs/cloudflare_api.txt
SERVICE="phoenix-omega"  # canonical Keychain service name (see scripts/ci/load_integration_env_from_keychain.py)

ACC=$(grep -E '^CLOUDFLARE_ACCOUNT_ID=' "$FILE" | cut -d= -f2-)
TOK=$(grep -E '^CLOUDFLARE_API_TOKEN=' "$FILE" | cut -d= -f2-)
AKI=$(awk '/^Access Key ID$/{getline; print; exit}' "$FILE")
SAK=$(awk '/^Secret Access Key$/{getline; print; exit}' "$FILE")
ENDPOINT=$(grep -oE 'https://[a-f0-9]+\.r2\.cloudflarestorage\.com' "$FILE" | head -1)
BUCKET="phoenix-omega-artifacts"  # confirm with operator if non-default

# CORRECT scheme: -s phoenix-omega -a <NAME>
# (NOT -s NAME -a $USER — that's a different keying the loader will not find)
security add-generic-password -s "$SERVICE" -a CLOUDFLARE_ACCOUNT_ID -w "$ACC"      -U
security add-generic-password -s "$SERVICE" -a CLOUDFLARE_API_TOKEN  -w "$TOK"      -U
security add-generic-password -s "$SERVICE" -a R2_ACCOUNT_ID         -w "$ACC"      -U
security add-generic-password -s "$SERVICE" -a R2_ACCESS_KEY_ID      -w "$AKI"      -U
security add-generic-password -s "$SERVICE" -a R2_SECRET_ACCESS_KEY  -w "$SAK"      -U
security add-generic-password -s "$SERVICE" -a R2_BUCKET             -w "$BUCKET"   -U
security add-generic-password -s "$SERVICE" -a R2_ENDPOINT           -w "$ENDPOINT" -U

unset ACC TOK AKI SAK ENDPOINT
```

Print only `OK <name> len=<int>` per success. Never echo values.

## Verify with the canonical loader

```bash
eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
```

This emits `export <NAME>=<value>` for every registered name found at
`service=phoenix-omega, account=<NAME>`. If a Keychain entry was added with
the wrong scheme (e.g. `-a $USER -s NAME`) the loader silently skips it —
verify with `--verbose` for skip notices on stderr.

## EU jurisdiction nuance

Cloudflare R2 buckets created in the EU jurisdiction expose an S3 endpoint
whose host hash differs from `CLOUDFLARE_ACCOUNT_ID`. Default-jurisdiction
buckets use `https://<account_id>.r2.cloudflarestorage.com`; EU buckets use
the URL printed on the token result page (which `R2_ENDPOINT` captures).

`scripts/artifacts/r2_sync.py` reads `R2_ENDPOINT` first and falls back to
the default format when unset — so consumers work for both jurisdictions
without code changes per bucket.

## Token rotation hygiene

If a credential value enters the chat transcript at any point (operator
paste, agent tool output, screenshot OCR, error message), Pearl_Int treats
it as compromised and asks the operator to rotate at the issuing portal,
then re-stage in the gitignored file. Account IDs are not authentication
material on their own — bucket/endpoint hashes the same — but tokens, keys,
and secrets always rotate.

## After loading

The staging file remains gitignored and on disk. Operator decides whether
to keep it (for re-runs after Keychain wipe / new dev environment) or
delete it. Keychain is the live source of truth; the file is a one-shot
hand-off.
