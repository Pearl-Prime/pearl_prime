// Pearl Prime storefront — formatting + presentation helpers (no deps, browser ESM).

export const LOCALE_CURRENCY = {
  "en-US": "USD", "ja-JP": "JPY", "zh-TW": "TWD", "zh-CN": "CNY", "ko-KR": "KRW",
};
const ZERO_DECIMAL = new Set(["JPY", "KRW"]);
const SYMBOL = { USD: "$", JPY: "¥", TWD: "NT$", CNY: "¥", KRW: "₩" };

export function money(cents, currency) {
  if (cents == null) return "";
  if (ZERO_DECIMAL.has(currency)) return (SYMBOL[currency] || "") + String(cents);
  return (SYMBOL[currency] || "") + (cents / 100).toFixed(2);
}

// Snipcart wants a decimal string in the SKU currency (whole-unit for JPY/KRW).
export function snipcartPrice(cents, currency) {
  return ZERO_DECIMAL.has(currency) ? String(cents) : (cents / 100).toFixed(2);
}

const GENRE_SUFFIX = /_(healing|shojo|iyashikei|cultivation|seinen|josei|shonen|kodomo)$/;
export function prettyBrand(brandId = "") {
  return brandId.replace(GENRE_SUFFIX, "").split("_")
    .map((w) => (w ? w[0].toUpperCase() + w.slice(1) : w)).join(" ");
}

export function formatPill(pt) {
  return ({ book: "Book / EPUB", audiobook: "Audiobook / M4B", manga: "Manga / WEBTOON", music: "Music" })[pt] || pt;
}
export function coverClass(pt) {
  return ({ book: "is-book", audiobook: "is-audio", manga: "is-manga", music: "is-music" })[pt] || "is-book";
}
export function prettyText(s = "") { return s.replace(/_/g, " "); }

export function escapeHtml(s = "") {
  return String(s).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

// Deterministic 32-bit FNV-ish hash for stable placeholders keyed by sku_id.
export function hashInt(str = "") {
  let h = 2166136261;
  for (let i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 16777619); }
  return Math.abs(h);
}

// Placeholder rating until sku_review_summary carries real data (the /api path
// returns the real aggregate; this only fires in the static sample fallback).
export function placeholderRating(skuId) {
  const h = hashInt(skuId);
  return { avg: Math.round((4.2 + (h % 8) / 10) * 10) / 10, count: 18 + (h % 480) };
}
export function starString(avg) {
  const full = Math.max(0, Math.min(5, Math.round(avg)));
  return "★★★★★".slice(0, full) + "☆☆☆☆☆".slice(0, 5 - full);
}

// Token-only amber-gradient SVG cover placeholder (real covers stream from R2 once seeded).
let _cid = 0;
export function coverSVG(sku) {
  const h = hashInt(sku.sku_id || "");
  const id = "ppg" + (_cid++);
  const initial = ((sku.title || sku.series_title || "?").trim()[0] || "?").toUpperCase();
  const brand = prettyBrand(sku.brand_id).toUpperCase();
  const cx = 50 + (h % 200);
  const cy = 90 + (h % 260);
  const r = 50 + (h % 70);
  return `<svg viewBox="0 0 300 450" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="${escapeHtml(sku.title || "")}">
  <defs><linearGradient id="${id}" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#1a1410"/><stop offset="0.62" stop-color="#0e0a06"/><stop offset="1" stop-color="#92400e"/>
  </linearGradient></defs>
  <rect width="300" height="450" fill="url(#${id})"/>
  <circle cx="${cx}" cy="${cy}" r="${r}" fill="#d97706" opacity="0.12"/>
  <circle cx="${300 - cx}" cy="${450 - cy}" r="${r * 0.6}" fill="#d97706" opacity="0.07"/>
  <text x="150" y="215" text-anchor="middle" font-family="Cormorant Garamond, Georgia, serif" font-size="150" fill="#d97706" opacity="0.92">${escapeHtml(initial)}</text>
  <text x="150" y="418" text-anchor="middle" font-family="DM Mono, monospace" font-size="13" letter-spacing="3" fill="#faf6f0" opacity="0.68">${escapeHtml(brand)}</text>
</svg>`;
}
