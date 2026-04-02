# Local Credentials Intake Runbook

> **Canonical registry:** For the full list of every integration credential this repo uses, see [docs/INTEGRATION_CREDENTIALS_REGISTRY.md](./INTEGRATION_CREDENTIALS_REGISTRY.md).

This runbook is for local-only credential sources such as
`docs/all_credentials.txt`.

## Rules

- Never commit local credential files.
- Never paste secrets back into chat unless absolutely required.
- Use only service-matched credentials or app-specific tokens.
- Do not try random username/password combinations across services.
- If a service needs an API token and the local file only has a web login,
  stop and do the manual login/token-generation flow instead.

## Current local source

If present, this repo may use:

- `docs/all_credentials.txt`

That file is local-only and gitignored.

## Intake command

```bash
/bin/zsh ./scripts/integrations/intake_all_credentials_local.sh
```

What it does:

- reads `docs/all_credentials.txt` if present
- imports the structured WordPress application-password block into:
  - `.env.wordpress.local`
  - macOS Keychain service `phoenix-omega-wordpress`
- writes local non-secret source metadata to:
  - `.integration_sources.local.yaml`

What it does not do:

- it does not brute-force or spray passwords
- it does not invent Messenger/WhatsApp/LINE/WeChat API tokens from plain logins
- it does not store raw credential dumps back into tracked repo files

## Safe follow-up flow

1. Run the intake command.
2. If WordPress imported successfully, test with:

```bash
/bin/zsh ./scripts/integrations/test_wordpress_local.sh
```

3. For messaging channels, run:

```bash
/bin/zsh ./scripts/integrations/setup_messaging_channels_local.sh
```

That setup script will prefill any safe hints it can extract from the local
credentials file, but it will still ask for the actual platform-issued API
tokens and recipient IDs.

4. Use `docs/all_credentials.txt` only as a human reference for service-matched
   sign-in where required to obtain the real API token, channel secret, app
   secret, or application password.

5. If you want a short checklist of what is still missing for each messaging
   channel, run:

```bash
/bin/zsh ./scripts/integrations/report_messaging_requirements_local.sh
```
