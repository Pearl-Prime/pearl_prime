# Trend Keywords — Locale-Specific Search Configs
## Used by SerpApi trend scraping system

### Overview
Each locale file configures region-specific search terms for the SerpApi trend
scraping pipeline (250 searches/month budget, 5-tier day-of-week rotation).

### File Naming Convention
`trend_keywords_{locale}.yaml` — e.g. `trend_keywords_ja_JP.yaml`

### Locales Covered
| Locale | Status | Research Source |
|--------|--------|----------------|
| en_US | Production (in main config) | SerpApi + Google Trends |
| ja_JP | Pilot | Rakuten AI + DeepSeek + Web Search |
| ko_KR | Pilot | Rakuten AI + DeepSeek + Web Search |
| zh_TW | Pilot | Rakuten AI + DeepSeek + Web Search |
| zh_CN | Pilot | DeepSeek + Web Search |
| zh_SG | Planned | DeepSeek + Web Search |
| zh_HK | Planned | DeepSeek + Web Search |

### Budget Allocation
- Current: 250 searches/month (US only)
- Proposed: Reserve Tier 5 searches for locale pilots (ja_JP, zh_TW first)
- SerpApi supports regional search (country codes: JP, KR, TW, CN, SG, HK)
- Google Trends has regional data for all target markets

### Integration
- Feeds into: `config/marketing/consumer_language_by_topic_{locale}.yaml`
- Feeds into: `config/marketing/invisible_scripts_by_persona_topic_{locale}.yaml`
- Used by: `scripts/feeds/` trend scraping pipeline
- Used by: `phoenix_v4/planning/catalog_planner.py`
