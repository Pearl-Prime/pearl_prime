# Freebie Messaging Channel Hardening

Supported channel contract:

- WhatsApp: env-gated provider adapter; dry-run supported.
- Telegram: env-gated bot token; dry-run supported.
- Email: universal fallback through existing capture/GHL workflow.
- LINE: Japan-only when env is configured; dry-run supported.
- Messenger: Japan/fallback when env is configured; dry-run supported.

Missing credentials must fail closed with a clear message. Tests must not send real messages.
