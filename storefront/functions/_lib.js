// Shared helpers for Pearl Prime storefront Pages Functions (Cloudflare Workers runtime).
// Underscore-prefixed => not routed. Imported by the route handlers under functions/api/.

export const CORS = {
  "access-control-allow-origin": "*",
  "access-control-allow-methods": "GET,POST,OPTIONS",
  "access-control-allow-headers": "content-type",
};

export function json(data, status = 200, extra = {}) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", ...CORS, ...extra },
  });
}
export function bad(status, message) { return json({ error: message }, status); }

export function getDB(env) {
  if (!env || !env.DB) throw new Error("D1 binding 'DB' not configured (uncomment [[d1_databases]] in wrangler.toml)");
  return env.DB;
}

export function nowSec() { return Math.floor(Date.now() / 1000); }

export async function sha256Hex(s) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(String(s)));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

// Public SKU columns. asset_url is intentionally NOT exposed here — the full paid
// asset is only reachable via a signed library URL (§12/§13).
export const SKU_COLS = [
  "sku_id", "locale", "brand_id", "product_type", "sub_type", "topic", "persona",
  "series_id", "title", "subtitle", "description", "cover_url", "preview_url",
  "price_cents", "currency", "status",
];
export const SKU_SELECT = SKU_COLS.map((c) => "s." + c).join(", ");
