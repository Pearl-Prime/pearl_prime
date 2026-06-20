// Pearl Prime storefront — data access. Calls the Worker API (/api/*) and, when
// that is unavailable (static local verification with no D1), falls back to the
// committed sample fixture so the UI is always exercisable.

const API_BASE = "/api";
const _samples = {};

async function sample(locale = "en-US") {
  if (!_samples[locale]) {
    let r = null;
    try { r = await fetch(`./app/sample_catalog.${locale}.json`); } catch (_) { r = null; }
    _samples[locale] = (r && r.ok) ? await r.json() : [];
  }
  return _samples[locale];
}

async function tryApi(path, opts) {
  try {
    const r = await fetch(API_BASE + path, opts);
    if (!r.ok) return null;
    const ct = r.headers.get("content-type") || "";
    if (!ct.includes("json")) return null;
    return await r.json();
  } catch (_) {
    return null; // network/route absent -> caller falls back
  }
}

function matchQuery(s, q) {
  const qq = q.toLowerCase();
  return [s.title, s.subtitle, s.brand_id, s.topic, s.persona, s.series_title]
    .some((f) => (f || "").toLowerCase().includes(qq));
}

export async function getCatalog({ locale = "en-US", brand = null, type = null, q = null, limit = 24, cursor = null } = {}) {
  const qs = new URLSearchParams({ locale, limit: String(limit) });
  if (brand) qs.set("brand", brand);
  if (type) qs.set("product_type", type);
  if (q) qs.set("q", q);
  if (cursor) qs.set("cursor", cursor);
  const api = await tryApi("/catalog?" + qs.toString());
  if (api && Array.isArray(api.items)) return api;

  let items = (await sample(locale)).filter((s) => s.locale === locale);
  if (brand) items = items.filter((s) => s.brand_id === brand);
  if (type) items = items.filter((s) => s.product_type === type);
  if (q) items = items.filter((s) => matchQuery(s, q));
  return { items: items.slice(0, limit), total: items.length, source: "sample" };
}

export async function getSku(id, locale = "en-US") {
  const api = await tryApi("/sku/" + encodeURIComponent(id));
  if (api && api.sku) return api;
  for (const loc of [locale, "en-US", "ja-JP"]) {
    const found = (await sample(loc)).find((s) => s.sku_id === id);
    if (found) return { sku: found, reviews: [], summary: null, source: "sample" };
  }
  return { sku: null, reviews: [], summary: null, source: "sample" };
}

export async function getReviews(skuId) {
  const api = await tryApi("/review?sku_id=" + encodeURIComponent(skuId));
  if (api && Array.isArray(api.reviews)) return api.reviews;
  try { return JSON.parse(localStorage.getItem("pp_reviews_" + skuId) || "[]"); }
  catch (_) { return []; }
}

export async function postReview(skuId, payload) {
  const api = await tryApi("/review", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ sku_id: skuId, ...payload }),
  });
  if (api && api.ok) return api;
  // local fallback: persist so the review renders immediately
  const key = "pp_reviews_" + skuId;
  let arr = [];
  try { arr = JSON.parse(localStorage.getItem(key) || "[]"); } catch (_) {}
  arr.unshift({
    review_id: "local_" + Date.now(), sku_id: skuId, ...payload,
    verified_purchase: 0, status: "visible", helpful_count: 0,
    created_at: new Date().toISOString().slice(0, 10),
  });
  localStorage.setItem(key, JSON.stringify(arr));
  return { ok: true, source: "local" };
}

export async function getLibrary() {
  // Production: GET /api/account/library (signed R2 urls). Local: localStorage entitlements.
  const api = await tryApi("/account/library");
  if (api && Array.isArray(api.items)) return api.items;
  let owned = [];
  try { owned = JSON.parse(localStorage.getItem("pp_library") || "[]"); } catch (_) {}
  if (!owned.length) return [];
  const all = [...(await sample("en-US")), ...(await sample("ja-JP"))];
  return owned.map((id) => all.find((s) => s.sku_id === id)).filter(Boolean);
}

export function grantLocalEntitlement(skuId) {
  let owned = [];
  try { owned = JSON.parse(localStorage.getItem("pp_library") || "[]"); } catch (_) {}
  if (!owned.includes(skuId)) { owned.push(skuId); localStorage.setItem("pp_library", JSON.stringify(owned)); }
}
