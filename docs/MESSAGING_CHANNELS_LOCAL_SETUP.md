# Messaging Channels Local Setup

This mirrors the existing channel model already present in the admin UI:

- LINE
- WhatsApp
- WeChat
- FB Messenger
- iMessage

## What this setup does

- stores non-secret channel metadata in `.messaging_channels.local.yaml`
- stores secrets in macOS Keychain
- gives you a single local place to keep your already-created channel details

## Run setup

```bash
/bin/zsh ./scripts/integrations/setup_messaging_channels_local.sh
```

Or do the one-pass setup for everything:

```bash
/bin/zsh ./scripts/integrations/setup_all_local_integrations.sh
```

If `docs/all_credentials.txt` exists locally, the master setup can import the
local source metadata first. That is only a helper for service-matched human
lookup. It does not turn plain web-login credentials into API tokens.

The messaging setup script also pre-fills any conservative hints it can safely
extract from that file, such as:

- a general account email hint
- a phone/profile hint
- an iMessage handle default when an obvious account email exists

It still requires the real API tokens, IDs, and recipient identifiers that the
platforms issue.

It will ask, channel by channel, whether you want to configure:

- LINE
- WhatsApp
- WeChat
- Messenger
- iMessage

## Verify

```bash
/bin/zsh ./scripts/integrations/check_messaging_channels_local.sh
```

## Send a message

Dry-run first:

```bash
/bin/zsh ./scripts/integrations/send_message.sh --channel line --message "test from phoenix" --dry-run
```

Real send:

```bash
/bin/zsh ./scripts/integrations/send_message.sh --channel line --message "test from phoenix"
```

Other channels:

```bash
/bin/zsh ./scripts/integrations/send_message.sh --channel whatsapp --message "test from phoenix"
/bin/zsh ./scripts/integrations/send_message.sh --channel messenger --message "test from phoenix"
/bin/zsh ./scripts/integrations/send_message.sh --channel wechat --message "test from phoenix"
/bin/zsh ./scripts/integrations/send_message.sh --channel imessage --message "test from phoenix"
```

If you need to override the recipient for one send:

```bash
/bin/zsh ./scripts/integrations/send_message.sh --channel messenger --to RECIPIENT_ID --message "test from phoenix"
```

Shortcut wrappers:

```bash
/bin/zsh ./scripts/integrations/send_line.sh --message "test from phoenix"
/bin/zsh ./scripts/integrations/send_whatsapp.sh --message "test from phoenix"
/bin/zsh ./scripts/integrations/send_messenger.sh --message "test from phoenix"
/bin/zsh ./scripts/integrations/send_wechat.sh --message "test from phoenix"
/bin/zsh ./scripts/integrations/send_imessage.sh --message "test from phoenix"
```

## Notes

- `.messaging_channels.local.yaml` is gitignored.
- `.integration_sources.local.yaml` is gitignored.
- Keychain services are named `phoenix-omega-line`, `phoenix-omega-whatsapp`, `phoenix-omega-wechat`, and `phoenix-omega-messenger`.
- iMessage is stored as a local handle only because it does not use a normal public API-key model like the others.
- This creates a clean local source of truth for channels you already set up. It does not bypass platform logins, approvals, or business verification.
- LINE push uses the LINE Messaging API user/group ID model.
- WhatsApp and Messenger use Meta Graph API access tokens and recipient IDs/phone numbers.
- WeChat custom send requires the recipient `openid`, not just the public-facing WeChat ID.
- Use only service-matched credentials or generated app tokens. Do not try random username/password combinations across services.
