# Local Credentials Intake Runbook

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

4. Use `docs/all_credentials.txt` only as a human reference for service-matched
   sign-in where required to obtain the real API token, channel secret, app
   secret, or application password.
