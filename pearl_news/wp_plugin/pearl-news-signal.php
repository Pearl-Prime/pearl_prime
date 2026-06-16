<?php
/**
 * Plugin Name:       Pearl News — Reader Signal
 * Description:       REST endpoint that accepts poll votes + take submissions
 *                    from Pearl News article sidebars, append-only-logs them to
 *                    daily JSONL files for downstream EI v2 ingest.
 * Version:           0.2.0 (Phase 2 — 2026-05-19)
 * Author:            Pearl News (Phoenix Omega)
 * License:           GPL-2.0-or-later
 *
 * Install:
 *   1. Copy this file to wp-content/mu-plugins/pearl-news-signal.php
 *      (the directory may need to be created; mu-plugins auto-load with no UI)
 *   2. WP will pick it up immediately — no activation step.
 *   3. Verify with:
 *        curl -X POST -H 'Content-Type: application/json' \
 *             -d '{"kind":"poll_vote","article_id":"test","value":"My chest tightened","ts":"2026-05-19T12:00:00Z"}' \
 *             https://pearlnewsuna.org/wp-json/pearl-news/v1/signal
 *      → expect HTTP 200 with {"ok":true,"signal_id":"..."}
 *   4. Logs accumulate at:
 *        wp-content/uploads/pearl-news-signals/YYYY-MM-DD.jsonl
 *
 * Spec: docs/PEARL_NEWS_READER_SIGNAL_SPEC.md
 * Frontend: pearl_news/pipeline/assemble_v52.py (pnReaderSignal IIFE)
 * Downstream ingest: pearl_news/pipeline/reader_signal_ingest.py
 */

if (!defined('ABSPATH')) {
    exit; // Direct access forbidden.
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------
define('PEARL_NEWS_SIGNAL_VERSION',   '0.2.0');
define('PEARL_NEWS_SIGNAL_NAMESPACE', 'pearl-news/v1');
define('PEARL_NEWS_SIGNAL_ROUTE',     '/signal');
define('PEARL_NEWS_SIGNAL_DIR_NAME',  'pearl-news-signals');
define('PEARL_NEWS_SIGNAL_MAX_TEXT',  4000);   // Max chars in a take submission.
define('PEARL_NEWS_SIGNAL_RATE_MIN',  20);     // Max signals per IP per 60s.
define('PEARL_NEWS_SIGNAL_RATE_DAY',  500);    // Max signals per IP per 24h.

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Returns the absolute path to the signal log directory (creates if missing).
 */
function pearl_news_signal_log_dir() {
    $upload = wp_upload_dir();
    $base   = trailingslashit($upload['basedir']) . PEARL_NEWS_SIGNAL_DIR_NAME;
    if (!file_exists($base)) {
        wp_mkdir_p($base);
        // Drop a .htaccess that allows JSON reads but blocks PHP execution.
        @file_put_contents($base . '/.htaccess', "Options -Indexes\n<FilesMatch \"\\.(php|phtml)$\">\n  Deny from all\n</FilesMatch>\n");
    }
    return $base;
}

/**
 * SHA-256 hash of a value (used to anonymize IP / UA before logging).
 */
function pearl_news_signal_hash($value) {
    $salt = defined('AUTH_SALT') ? AUTH_SALT : 'pearl-news-default-salt-change-me';
    return substr(hash_hmac('sha256', (string)$value, $salt), 0, 16);
}

/**
 * Per-IP per-window rate limiting. Returns true if request is within limits.
 * Uses WP object cache (transient) for the counters — no DB writes per request.
 */
function pearl_news_signal_rate_ok($ip_hash) {
    $key_min = 'pn_sig_rate_m_' . $ip_hash;
    $key_day = 'pn_sig_rate_d_' . $ip_hash;
    $minute  = (int) get_transient($key_min);
    $day     = (int) get_transient($key_day);
    if ($minute >= PEARL_NEWS_SIGNAL_RATE_MIN) return false;
    if ($day    >= PEARL_NEWS_SIGNAL_RATE_DAY) return false;
    set_transient($key_min, $minute + 1, 60);
    set_transient($key_day, $day    + 1, 24 * 60 * 60);
    return true;
}

/**
 * Validate + normalize a POSTed signal payload. Returns ['valid'=>bool, ...].
 */
function pearl_news_signal_validate($raw) {
    if (!is_array($raw)) {
        return ['valid' => false, 'reason' => 'payload_not_object'];
    }
    $kind = isset($raw['kind']) ? sanitize_key($raw['kind']) : '';
    if (!in_array($kind, ['poll_vote', 'take'], true)) {
        return ['valid' => false, 'reason' => 'unknown_kind'];
    }
    $article_id = isset($raw['article_id']) ? sanitize_text_field($raw['article_id']) : '';
    if ($article_id === '' || strlen($article_id) > 200) {
        return ['valid' => false, 'reason' => 'bad_article_id'];
    }
    $ts = isset($raw['ts']) ? sanitize_text_field($raw['ts']) : '';
    if ($ts === '' || strlen($ts) > 64) {
        $ts = gmdate('c');  // Server-side fallback to UTC ISO 8601.
    }

    $clean = [
        'kind'       => $kind,
        'article_id' => $article_id,
        'ts'         => $ts,
    ];

    if ($kind === 'poll_vote') {
        $value = isset($raw['value']) ? sanitize_text_field($raw['value']) : '';
        if ($value === '' || strlen($value) > 300) {
            return ['valid' => false, 'reason' => 'bad_value'];
        }
        $clean['value'] = $value;
    } else { // take
        $text = isset($raw['text']) ? sanitize_textarea_field($raw['text']) : '';
        if ($text === '') {
            return ['valid' => false, 'reason' => 'empty_text'];
        }
        if (strlen($text) > PEARL_NEWS_SIGNAL_MAX_TEXT) {
            return ['valid' => false, 'reason' => 'text_too_long'];
        }
        // Honeypot: any client that sends a "website" / "url_field" property is
        // almost certainly a bot. Real frontend never sets these.
        foreach (['website', 'url_field', 'homepage'] as $hpot) {
            if (!empty($raw[$hpot])) {
                return ['valid' => false, 'reason' => 'honeypot'];
            }
        }
        $clean['text'] = $text;
    }

    return ['valid' => true, 'clean' => $clean];
}

// ---------------------------------------------------------------------------
// REST endpoint
// ---------------------------------------------------------------------------

add_action('rest_api_init', function () {
    register_rest_route(PEARL_NEWS_SIGNAL_NAMESPACE, PEARL_NEWS_SIGNAL_ROUTE, [
        'methods'             => 'POST',
        'callback'            => 'pearl_news_signal_handle_post',
        'permission_callback' => '__return_true',  // Public; abuse-protected via rate limit + honeypot.
    ]);
    register_rest_route(PEARL_NEWS_SIGNAL_NAMESPACE, PEARL_NEWS_SIGNAL_ROUTE . '/aggregate/(?P<article_id>[A-Za-z0-9_\-]+)', [
        'methods'             => 'GET',
        'callback'            => 'pearl_news_signal_handle_get_aggregate',
        'permission_callback' => '__return_true',
        'args' => [
            'article_id' => [
                'sanitize_callback' => 'sanitize_text_field',
            ],
        ],
    ]);
});

/**
 * POST /wp-json/pearl-news/v1/signal
 * Body: see PEARL_NEWS_READER_SIGNAL_SPEC.md
 */
function pearl_news_signal_handle_post(WP_REST_Request $req) {
    $raw = $req->get_json_params();
    if ($raw === null) {
        return new WP_REST_Response(['ok' => false, 'error' => 'invalid_json'], 400);
    }

    // Rate limit (per hashed IP)
    $ip       = $req->get_header('X-Forwarded-For') ?: $_SERVER['REMOTE_ADDR'] ?? 'unknown';
    $ip_hash  = pearl_news_signal_hash($ip);
    if (!pearl_news_signal_rate_ok($ip_hash)) {
        return new WP_REST_Response(['ok' => false, 'error' => 'rate_limited'], 429);
    }

    $v = pearl_news_signal_validate($raw);
    if (!$v['valid']) {
        return new WP_REST_Response(['ok' => false, 'error' => $v['reason']], 422);
    }

    // Enrich signal record (server-side only; not echoed back to client)
    $record = $v['clean'];
    $record['ip']         = $ip_hash;
    $record['ua']         = pearl_news_signal_hash($_SERVER['HTTP_USER_AGENT'] ?? '');
    $record['signal_id']  = wp_generate_uuid4();
    $record['server_ts']  = gmdate('c');
    $record['plugin_v']   = PEARL_NEWS_SIGNAL_VERSION;

    // Append-only log to today's JSONL file (UTC date)
    $log_dir   = pearl_news_signal_log_dir();
    $log_path  = trailingslashit($log_dir) . gmdate('Y-m-d') . '.jsonl';
    $line      = wp_json_encode($record, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . "\n";

    $handle = @fopen($log_path, 'ab');
    if (!$handle) {
        return new WP_REST_Response(['ok' => false, 'error' => 'log_unavailable'], 500);
    }
    if (flock($handle, LOCK_EX)) {
        fwrite($handle, $line);
        flock($handle, LOCK_UN);
    }
    fclose($handle);

    // Action hook so other plugins (or a future EI v2 webhook bridge) can react
    do_action('pearl_news_signal_logged', $record);

    return new WP_REST_Response([
        'ok'         => true,
        'signal_id'  => $record['signal_id'],
        'server_ts'  => $record['server_ts'],
    ], 200);
}

/**
 * GET /wp-json/pearl-news/v1/signal/aggregate/<article_id>
 * Returns the aggregate poll tally + take count for one article, derived
 * by walking today's JSONL + the prior 30 days. Read-only.
 */
function pearl_news_signal_handle_get_aggregate(WP_REST_Request $req) {
    $article_id = (string) $req->get_param('article_id');
    if ($article_id === '') {
        return new WP_REST_Response(['ok' => false, 'error' => 'missing_article_id'], 400);
    }

    $log_dir = pearl_news_signal_log_dir();
    $tally   = [];
    $takes   = 0;
    $latest  = '';

    // Walk last 30 days (cheap; daily files small)
    for ($i = 0; $i < 30; $i++) {
        $day      = gmdate('Y-m-d', time() - ($i * 86400));
        $log_path = trailingslashit($log_dir) . $day . '.jsonl';
        if (!file_exists($log_path)) continue;
        $fp = @fopen($log_path, 'rb');
        if (!$fp) continue;
        while (($buf = fgets($fp)) !== false) {
            $rec = json_decode(trim($buf), true);
            if (!is_array($rec) || ($rec['article_id'] ?? '') !== $article_id) continue;
            if (($rec['kind'] ?? '') === 'poll_vote') {
                $val = (string) ($rec['value'] ?? '');
                if ($val !== '') $tally[$val] = ($tally[$val] ?? 0) + 1;
            } elseif (($rec['kind'] ?? '') === 'take') {
                $takes++;
            }
            $ts = (string) ($rec['ts'] ?? '');
            if ($ts > $latest) $latest = $ts;
        }
        fclose($fp);
    }

    return new WP_REST_Response([
        'ok'             => true,
        'article_id'     => $article_id,
        'poll_tally'     => $tally,
        'poll_total'     => array_sum($tally),
        'take_count'     => $takes,
        'last_signal_ts' => $latest,
        'window_days'    => 30,
    ], 200);
}

// ---------------------------------------------------------------------------
// CORS (only needed if Pearl News articles are ever served from a different
// origin than the API — kept narrow + safe).
// ---------------------------------------------------------------------------

add_action('rest_api_init', function () {
    remove_filter('rest_pre_serve_request', 'rest_send_cors_headers');
    add_filter('rest_pre_serve_request', function ($value) {
        $origin = get_http_origin();
        $allowed = [
            'https://pearlnewsuna.org',
            'https://www.pearlnewsuna.org',
        ];
        if ($origin && in_array($origin, $allowed, true)) {
            header('Access-Control-Allow-Origin: ' . $origin);
            header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
            header('Access-Control-Allow-Headers: Content-Type');
            header('Access-Control-Allow-Credentials: false');
            header('Vary: Origin');
        }
        return $value;
    }, 15);
}, 0);
