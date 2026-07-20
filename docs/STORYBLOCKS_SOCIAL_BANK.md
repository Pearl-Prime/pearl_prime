# Storyblocks → Social Media Content Bank

**Layer:** CODE-WIRED CLI + EXECUTED-REAL when keys load and confirm runs.  
**EULA:** confirm-first only; no shared HD pool; MAU = distinct download user_ids / UTC month (cap 104).

## Pearl_Int — keys

```bash
# From labeled dashboard paste (docs/storyblocks_api_key1.txt or docs/storyblocks_api_key.txt):
python3 scripts/storyblocks/install_keychain_creds.py --from-file docs/storyblocks_api_key1.txt
# or KEY=val staging:
python3 scripts/storyblocks/install_keychain_creds.py --from-file docs/storyblocks_keys.env

eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
python3 -c "from scripts.storyblocks.api_client import StoryblocksAPIClient; StoryblocksAPIClient(); print('ok')"
```

## Fill a bank

```bash
eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"

python3 scripts/storyblocks/fill_social_bank.py \
  --brand-id way_stream_sanctuary \
  --locale en-US \
  --topics anxiety,burnout,boundaries \
  --media video,image \
  --max-per-topic 2

# Index HD already on disk from an earlier receipt (no API):
python3 scripts/storyblocks/fill_social_bank.py \
  --bootstrap-receipt artifacts/storyblocks/social_bank_fill_20260720.json
```

## Outputs

| Path | Role |
|------|------|
| `artifacts/storyblocks_licensed/{work_unit}/` | Licensed HD only |
| `artifacts/storyblocks/{work_unit}/BANK_INDEX.json` | Topic → asset map |
| `artifacts/storyblocks/{work_unit}/MANIFEST.tsv` | Inventory |
| `artifacts/storyblocks/social_bank_latest.json` | Pointer for consumers |

## Consumers

`scripts/social/build_video_snippet_bank.py` prefers Storyblocks stills from `BANK_INDEX` / `social_bank_latest.json`, then Pexels.

Push/merge when GitHub is unavailable: **`pearlstar_offline`**.
