# Pearl News — Reader Signal WordPress plugin

Must-use plugin that closes the Phase 2 loop for `docs/PEARL_NEWS_READER_SIGNAL_SPEC.md`.

Provides the REST endpoint that the article frontend (`pearl_news/pipeline/assemble_v52.py` → `pnReaderSignal` IIFE) POSTs poll votes and take submissions to.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| **POST** | `/wp-json/pearl-news/v1/signal` | Append-only log a reader signal |
| **GET**  | `/wp-json/pearl-news/v1/signal/aggregate/<article_id>` | Read per-article tally (last 30 days) |

## POST request body

```json
{
  "kind":       "poll_vote",
  "article_id": "qa-3582",
  "value":     "My chest tightened",
  "ts":        "2026-05-19T12:34:56Z"
}
```

Or:

```json
{
  "kind":       "take",
  "article_id": "qa-3582",
  "text":      "When I read the Gaza funding gap, I cancelled my evening plans…",
  "ts":        "2026-05-19T12:34:56Z"
}
```

## POST response

```json
{
  "ok":         true,
  "signal_id":  "550e8400-e29b-41d4-a716-446655440000",
  "server_ts":  "2026-05-19T12:34:56+00:00"
}
```

Error responses:
- `400 invalid_json` — body wasn't JSON
- `422 unknown_kind` / `bad_article_id` / `bad_value` / `empty_text` / `text_too_long` / `honeypot`
- `429 rate_limited` — IP exceeded 20/min or 500/day
- `500 log_unavailable` — couldn't open the daily JSONL file

## GET aggregate response

```json
{
  "ok":             true,
  "article_id":    "qa-3582",
  "poll_tally":     {"My chest tightened": 12, "I scrolled past": 4, "I felt nothing": 2, "I texted someone": 7},
  "poll_total":     25,
  "take_count":     8,
  "last_signal_ts": "2026-05-19T14:22:31Z",
  "window_days":    30
}
```

## Install

```bash
# On the WordPress host (e.g. pearlnewsuna.org)
mkdir -p wp-content/mu-plugins
cp pearl_news/wp_plugin/pearl-news-signal.php wp-content/mu-plugins/

# That's it — must-use plugins auto-load. No activation step in WP Admin.

# Verify with curl:
curl -X POST -H 'Content-Type: application/json' \
     -d '{"kind":"poll_vote","article_id":"test","value":"My chest tightened","ts":"2026-05-19T12:00:00Z"}' \
     https://pearlnewsuna.org/wp-json/pearl-news/v1/signal
# → HTTP 200 {"ok":true,"signal_id":"...","server_ts":"..."}

# Check the log:
ls -la wp-content/uploads/pearl-news-signals/
# → 2026-05-19.jsonl
cat wp-content/uploads/pearl-news-signals/2026-05-19.jsonl | tail -1
# → {"kind":"poll_vote","article_id":"test","ts":"2026-05-19T12:00:00Z","ip":"...","ua":"...","signal_id":"...","server_ts":"...","plugin_v":"0.2.0"}
```

## Storage

Signals append to:
```
wp-content/uploads/pearl-news-signals/YYYY-MM-DD.jsonl
```

One file per UTC day. Append-only. The included `.htaccess` denies PHP execution + directory listing inside the folder. JSONL records contain hashed IP + UA (using `AUTH_SALT`), so no raw PII.

## Sync to Phoenix Omega

Once signals are accumulating on the WP host, run:

```bash
bash scripts/ops/fetch_wp_signals.sh             # rsync mode
# or
bash scripts/ops/fetch_wp_signals.sh --rest      # REST fallback
```

This pulls the daily JSONLs into `artifacts/pearl_news/reader_signals/` and runs `pearl_news/pipeline/reader_signal_ingest.py` to aggregate into `_engagement_scores.json`.

## Anti-abuse

- **Rate limit:** 20 signals per IP per minute, 500 per day (uses WP transients; no DB writes per request)
- **Honeypot fields:** `website`, `url_field`, `homepage` — if any are non-empty, signal is rejected (real frontend doesn't send these)
- **Server-side timestamps:** `server_ts` is the authoritative time; `ts` from the client is preserved for ordering but not trusted
- **Anonymized identifiers:** IP and UA are hashed with `AUTH_SALT` before storage; 16-char truncation
- **CORS:** narrow allowlist — only `https://pearlnewsuna.org` and the `www` variant
- **No raw `text` of takes returned via GET** — aggregate endpoint exposes only counts

## EI v2 hook (Phase 3 — future)

The plugin fires a WordPress action when a signal is logged:

```php
do_action('pearl_news_signal_logged', $record);
```

A future webhook-bridge plugin can subscribe to that and POST individual signals to a Phoenix Omega service for real-time EI v2 boost computation. For now, batch sync (`fetch_wp_signals.sh`) suffices.

## Configuration constants

If the defaults don't suit your environment, override in `wp-config.php` before this plugin loads:

```php
// In wp-config.php, BEFORE the line that requires wp-settings.php:
define('PEARL_NEWS_SIGNAL_RATE_MIN', 50);   // raise minute limit
define('PEARL_NEWS_SIGNAL_RATE_DAY', 2000); // raise daily limit
define('PEARL_NEWS_SIGNAL_MAX_TEXT', 8000); // allow longer takes
```

## Uninstall

Remove the plugin file:
```bash
rm wp-content/mu-plugins/pearl-news-signal.php
```

The logs persist at `wp-content/uploads/pearl-news-signals/`. Delete that directory manually if you want a clean wipe.

## Version

- 0.2.0 — initial Phase 2 release (2026-05-19)
