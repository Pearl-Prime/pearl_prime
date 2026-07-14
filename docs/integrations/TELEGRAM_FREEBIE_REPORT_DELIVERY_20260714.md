# Telegram Freebie Report Delivery

Telegram delivery is env-gated. Required env var name: `FREEBIE_TELEGRAM_BOT_TOKEN`.

Local testing must use dry-run mode only:

```bash
python3 scripts/freebies/deliver_freebie_report.py --channel telegram --address @sample_user --slug anxiety-nervous-system-reset --dry-run
```

Dry-run output is sanitized and must not print bot tokens or real message API URLs.
