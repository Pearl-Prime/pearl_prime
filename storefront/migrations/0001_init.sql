-- Pearl Prime Storefront — D1 migration 0001 (init)
--
-- Canonical schema per docs/specs/PEARL_PRIME_STOREFRONT_V1_SPEC.md:
--   §7.2  sku                         (catalog projection cache)
--   §9.1  sku_search                  (FTS5 over sku — see note below)
--   §10.3 order_table + order_item    (Snipcart-wraps-Stripe; §AMENDMENT-2026-06-04.2/.3)
--   §11.2 review                      (guest reviews ok per Q-PRP-AUTH-01)
--   §11.3 sku_review_summary          (aggregate cache)
--   §11.1 review_rate_limit           (max 10/day per email_hash)
--   §AMENDMENT-2026-06-04.5 subscription (music brand subs; Phase B, schema ready now)
--   account + account_library + webhook_event_log (entitlements + webhook idempotency)
--
-- Anti-drift (§7.5): `sku` is a PROJECTION CACHE of the catalog CSVs, NOT a source
-- of truth — seeded by scripts/storefront/project_skus.py; catalog regen overwrites it.
--
-- NOTE on sku_search: the spec sketch uses `content='sku'`, but it indexes
-- columns (series_title, archetype) that do not exist on `sku`, so an
-- external-content FTS5 table + sync triggers would fail in D1. We use a
-- standalone FTS5 table populated explicitly by the seed instead — same query
-- surface for /api/search, and manga series_title / brand archetype index
-- without bloating the `sku` row. Re-seed regenerates both tables together.

-- ---------------------------------------------------------------------------
-- §7.2 — catalog projection cache
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sku (
  sku_id         TEXT PRIMARY KEY,     -- <product_type>_<locale>_<brand_id>_<inner_key> (§2.5)
  locale         TEXT NOT NULL,        -- 'en-US' | 'ja-JP' | 'zh-TW' | 'zh-CN' | 'ko-KR'
  brand_id       TEXT NOT NULL,
  product_type   TEXT NOT NULL,        -- 'book' | 'audiobook' | 'manga' | 'music'
  sub_type       TEXT,                 -- music only: 'track'|'album'|'brand_subscription' (AMENDMENT .5)
  topic          TEXT,                 -- book/audiobook
  persona        TEXT,                 -- book/audiobook
  series_id      TEXT,                 -- manga
  title          TEXT NOT NULL,
  subtitle       TEXT,
  description    TEXT,
  cover_url      TEXT,                 -- R2 key
  preview_url    TEXT,                 -- R2 key (sample chapter / 30s audio / first manga pages)
  asset_url      TEXT,                 -- R2 key (full paid asset; signed at download)
  price_cents    INTEGER NOT NULL,     -- locale currency smallest unit (JPY/KRW zero-decimal)
  currency       TEXT NOT NULL,        -- 'USD' | 'JPY' | 'TWD' | 'CNY' | 'KRW'
  status         TEXT NOT NULL,        -- 'active' | 'draft' | 'archived'
  bundle_id      TEXT,
  upstream_path  TEXT,                 -- source catalog row's output_target_path
  created_at     INTEGER NOT NULL,
  updated_at     INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_sku_locale_brand_type ON sku(locale, brand_id, product_type);
CREATE INDEX IF NOT EXISTS idx_sku_locale_status     ON sku(locale, status);
CREATE INDEX IF NOT EXISTS idx_sku_brand_status      ON sku(brand_id, status);

-- ---------------------------------------------------------------------------
-- §9.1 — full-text search (standalone FTS5; populated by the seed)
-- ---------------------------------------------------------------------------
CREATE VIRTUAL TABLE IF NOT EXISTS sku_search USING fts5(
  sku_id UNINDEXED,
  title, subtitle, brand_id, topic, persona, series_title, archetype, description,
  tokenize = 'unicode61'
);

-- ---------------------------------------------------------------------------
-- §10.3 — orders (Snipcart wraps Stripe)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS order_table (
  order_id          TEXT PRIMARY KEY,
  account_id        TEXT,                       -- nullable for guest checkout
  email             TEXT NOT NULL,
  locale            TEXT NOT NULL,
  currency          TEXT NOT NULL,
  total_cents       INTEGER NOT NULL,
  snipcart_token    TEXT UNIQUE,                -- Snipcart order token (AMENDMENT .3)
  stripe_session_id TEXT UNIQUE,
  stripe_payment_intent_id TEXT,
  status            TEXT NOT NULL,              -- 'pending'|'paid'|'refunded'|'failed'
  created_at        INTEGER NOT NULL,
  paid_at           INTEGER
);
CREATE TABLE IF NOT EXISTS order_item (
  order_item_id     TEXT PRIMARY KEY,
  order_id          TEXT NOT NULL REFERENCES order_table(order_id),
  sku_id            TEXT NOT NULL REFERENCES sku(sku_id),
  qty               INTEGER NOT NULL DEFAULT 1,
  unit_price_cents  INTEGER NOT NULL,
  currency          TEXT NOT NULL,
  email_hash        TEXT                        -- SHA-256(email): verified-purchase match for guests (§11.1)
);
CREATE INDEX IF NOT EXISTS idx_order_account        ON order_table(account_id, paid_at DESC);
CREATE INDEX IF NOT EXISTS idx_order_item_sku       ON order_item(sku_id);
CREATE INDEX IF NOT EXISTS idx_order_item_email_hash ON order_item(email_hash);

-- ---------------------------------------------------------------------------
-- §11.2 — reviews
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS review (
  review_id          TEXT PRIMARY KEY,
  sku_id             TEXT NOT NULL REFERENCES sku(sku_id),
  account_id         TEXT,                       -- nullable (guest reviews; Q-PRP-AUTH-01)
  reviewer_name      TEXT NOT NULL,              -- display name; defaults to "Reader"
  email_hash         TEXT,                       -- SHA-256(email); "already reviewed" check
  stars              INTEGER NOT NULL CHECK (stars BETWEEN 1 AND 5),
  body               TEXT NOT NULL,              -- 250..4000 chars (validated in Worker)
  verified_purchase  INTEGER NOT NULL DEFAULT 0,
  status             TEXT NOT NULL DEFAULT 'visible', -- 'visible'|'hidden'|'spam'
  helpful_count      INTEGER NOT NULL DEFAULT 0,
  reported_count     INTEGER NOT NULL DEFAULT 0,
  locale             TEXT NOT NULL,
  created_at         INTEGER NOT NULL,
  updated_at         INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_review_sku_status ON review(sku_id, status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_review_account    ON review(account_id, created_at DESC);

-- §11.3 — review aggregate cache
CREATE TABLE IF NOT EXISTS sku_review_summary (
  sku_id     TEXT PRIMARY KEY REFERENCES sku(sku_id),
  avg_stars  REAL NOT NULL,
  count      INTEGER NOT NULL,
  star_1     INTEGER NOT NULL DEFAULT 0,
  star_2     INTEGER NOT NULL DEFAULT 0,
  star_3     INTEGER NOT NULL DEFAULT 0,
  star_4     INTEGER NOT NULL DEFAULT 0,
  star_5     INTEGER NOT NULL DEFAULT 0,
  updated_at INTEGER NOT NULL
);

-- §11.1 — per-email review rate limit (max 10/day)
CREATE TABLE IF NOT EXISTS review_rate_limit (
  email_hash TEXT NOT NULL,
  day        TEXT NOT NULL,                      -- 'YYYY-MM-DD'
  count      INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (email_hash, day)
);

-- ---------------------------------------------------------------------------
-- accounts + entitlements + webhook idempotency
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS account (
  account_id   TEXT PRIMARY KEY,
  email        TEXT UNIQUE NOT NULL,
  display_name TEXT,
  locale       TEXT,
  created_at   INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS account_library (
  email_hash TEXT NOT NULL,
  sku_id     TEXT NOT NULL REFERENCES sku(sku_id),
  order_id   TEXT REFERENCES order_table(order_id),
  granted_at INTEGER NOT NULL,
  revoked_at INTEGER,                            -- set on refund (§10.6)
  PRIMARY KEY (email_hash, sku_id)
);
CREATE INDEX IF NOT EXISTS idx_library_sku ON account_library(sku_id);

CREATE TABLE IF NOT EXISTS webhook_event_log (
  event_id     TEXT PRIMARY KEY,                 -- Snipcart event id / idempotency key
  event_type   TEXT NOT NULL,
  payload_hash TEXT,
  received_at  INTEGER NOT NULL,
  processed    INTEGER NOT NULL DEFAULT 0
);

-- ---------------------------------------------------------------------------
-- §AMENDMENT-2026-06-04.5 — music brand subscriptions (Phase B; schema ready now)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS subscription (
  subscription_id          TEXT PRIMARY KEY,
  account_id               TEXT,
  email                    TEXT NOT NULL,
  brand_id                 TEXT NOT NULL,
  snipcart_subscription_id TEXT UNIQUE,
  status                   TEXT NOT NULL,        -- 'active'|'past_due'|'cancelled'|'expired'
  started_at               INTEGER NOT NULL,
  next_renewal_at          INTEGER,
  cancelled_at             INTEGER,
  locale                   TEXT NOT NULL,
  currency                 TEXT NOT NULL,
  price_cents              INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_subscription_email_status ON subscription(email, status);
CREATE INDEX IF NOT EXISTS idx_subscription_brand_status ON subscription(brand_id, status);
