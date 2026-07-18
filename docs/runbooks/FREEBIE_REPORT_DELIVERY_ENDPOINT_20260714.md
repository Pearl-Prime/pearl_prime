# Freebie Report Delivery Endpoint Runbook

The local endpoint adapter is `scripts/freebies/deliver_freebie_report.py`.

Dry run:

```bash
python3 scripts/freebies/deliver_freebie_report.py --channel email --address test@example.com --slug anxiety-nervous-system-reset --dry-run
```

Production dispatch must be env-gated. Do not persist PII in public storage. If report files are later stored in R2, use private keys and short-lived signed URLs only.
