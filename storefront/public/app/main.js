// Pearl Prime storefront — app shell + hash router + page renders.
// Static ES module (no build step): served by Cloudflare Pages, verifiable locally.
import {
  money, prettyBrand, formatPill, coverClass, coverSVG, starString,
  escapeHtml, placeholderRating, prettyText,
} from "./format.js";
import { getCatalog, getSku, getReviews, postReview, getLibrary } from "./api.js";
import * as cart from "./cart.js";

const $app = document.getElementById("app");
const state = { locale: (window.PP_CONFIG && window.PP_CONFIG.locale) || "en-US" };
const ACTIVE_LOCALES = ["en-US", "ja-JP"]; // Phase A; zh-TW/zh-CN/ko-KR = Phase B/C
let brandsCache = [];
let brandMap = {}; // {locale: {brand_id: localized label}} from ./app/brands.json
let currentStars = 5;

const truncate = (s, n) => (s.length > n ? s.slice(0, n - 1) + "…" : s);
const brandName = (locale, id) => (brandMap[locale] && brandMap[locale][id]) || null;
const brandLabel = (s) => brandName(s.locale, s.brand_id) || s.brand_label || prettyBrand(s.brand_id);

const HERO = {
  "en-US": { eyebrow: "Pearl Prime · A quieter shelf", h1: `Calm-tech books, audiobooks &amp; manga for a <em>noisy world</em>.`, p: "Anxiety, focus, sleep, burnout — practical companions that talk to you like an adult who happens to be struggling." },
  "ja-JP": { eyebrow: "Pearl Prime · 静かな棚", h1: `騒がしい世界のための、<em>静けさ</em>の本・オーディオ・マンガ。`, p: "不安、集中、睡眠、燃え尽き — 等身大のあなたに寄り添う、実践的な一冊を。" },
};
const LABELS = {
  "en-US": { featured: "Featured", book: "Books", audiobook: "Audiobooks", manga: "Manga", reviews: "Reviews", write: "Write a review →", buy: "Buy now", add: "Add to cart", results: "results", library: "library", account: "Your account", empty: "Your library is empty. Purchases appear here with download & read access.", preview: "Preview · first pages", readFull: "Read the full volume", sample: "30-second sample · free preview" },
  "ja-JP": { featured: "注目", book: "書籍", audiobook: "オーディオブック", manga: "マンガ", reviews: "レビュー", write: "レビューを書く →", buy: "今すぐ購入", add: "カートに入れる", results: "件", library: "ライブラリ", account: "アカウント", empty: "ライブラリは空です。購入した作品はここに表示され、ダウンロード・閲覧できます。", preview: "試し読み・最初のページ", readFull: "全巻を読む", sample: "30秒サンプル・無料試聴" },
};
const T = () => LABELS[state.locale] || LABELS["en-US"];

function ratingDisplay(sku, reviews) {
  if (reviews && reviews.length) {
    const count = reviews.length;
    const avg = reviews.reduce((x, r) => x + (Number(r.stars) || 0), 0) / count;
    return { avg, count };
  }
  if (sku.review_summary && sku.review_summary.count) {
    return { avg: sku.review_summary.avg_stars, count: sku.review_summary.count };
  }
  return placeholderRating(sku.sku_id); // sample-mode placeholder only
}

// ─── Chrome ────────────────────────────────────────────────────────────────
function localeSwitcher() {
  const locs = [
    ["en-US", "English (US)", true], ["ja-JP", "日本語", true],
    ["zh-TW", "繁體中文", false], ["zh-CN", "简体中文", false], ["ko-KR", "한국어", false],
  ];
  const opts = locs.map(([c, l, on]) =>
    `<a href="#/" data-locale="${c}">${escapeHtml(l)}${on ? "" : ' <span class="pp-locale-soon">soon</span>'}</a>`).join("");
  return `<div class="pp-locale-switcher"><span class="pp-locale-current">${escapeHtml(state.locale)}</span> ▾
    <div class="pp-locale-dropdown">${opts}</div></div>`;
}

function header() {
  return `<header class="pp-header"><div class="pp-header-inner">
    <a class="pp-wordmark" href="#/">Pearl <em>Prime</em></a>
    <div class="pp-search">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4-4"/></svg>
      <input id="pp-search" type="search" placeholder="Search titles, brands, topics…" autocomplete="off" />
    </div>
    <div class="pp-header-actions">
      ${localeSwitcher()}
      <button class="pp-icon-btn" data-cart-open aria-label="Cart">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M6 6h15l-1.5 9h-12z"/><circle cx="9" cy="20" r="1.3"/><circle cx="18" cy="20" r="1.3"/><path d="M6 6L5 3H2"/></svg>
        <span class="pp-cart-badge" data-cart-badge style="display:none">0</span>
      </button>
      <span class="pp-sign-in">Sign in<span class="pp-optional">optional</span></span>
    </div>
  </div></header>`;
}

function chipRail() {
  const chips = brandsCache.slice(0, 14).map((b) =>
    `<a class="pp-chip" href="#/search?brand=${encodeURIComponent(b)}">${escapeHtml(brandName(state.locale, b) || prettyBrand(b))}</a>`).join("");
  return `<div class="pp-chip-rail">${chips}</div>`;
}

function footer() {
  return `<footer class="pp-footer"><div>Pearl Prime · pearlprime.shop</div>
    <div><a href="#/">Home</a><a href="#/library">Library</a><a href="#/search">Browse</a></div></footer>`;
}

// ─── Cards ───────────────────────────────────────────────────────────────────
function skuCard(sku) {
  cart.registerSku(sku);
  const rt = ratingDisplay(sku);
  return `<a class="pp-card" href="#/p/${encodeURIComponent(sku.sku_id)}">
    <div class="pp-cover ${coverClass(sku.product_type)}">${coverSVG(sku)}</div>
    <div class="pp-card-meta">
      <span class="pp-card-brand">${escapeHtml(brandLabel(sku))}</span>
      <span class="pp-card-title">${escapeHtml(sku.title || "")}</span>
      <span class="pp-card-subtitle">${escapeHtml(truncate(sku.subtitle || "", 92))}</span>
      <div class="pp-card-rating"><span class="pp-stars">${starString(rt.avg)}</span><span>${rt.avg.toFixed(1)} · ${rt.count}</span></div>
      <div class="pp-card-footer"><span class="pp-price">${money(sku.price_cents, sku.currency)}</span><span class="pp-format-pill">${escapeHtml(sku.product_type)}</span></div>
    </div></a>`;
}

// ─── Specialized viewers (Phase A) ───────────────────────────────────────────
function audioPlayer() {
  const t = T();
  const chapters = [1, 2, 3, 4].map((n) =>
    `<div class="pp-audio-chapter${n > 1 ? " is-locked" : ""}"><span>Chapter ${n}</span><span class="pp-chapter-time">${n > 1 ? "🔒" : "sample"}</span></div>`).join("");
  return `<div class="pp-audio-player pp-mt-16">
    <div class="pp-sample-banner">▶ ${escapeHtml(t.sample)}</div>
    <div class="pp-audio-controls">
      <button class="pp-play-btn" aria-label="Play sample"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg></button>
      <div class="pp-audio-waveform"><div class="pp-audio-progress" style="width:16%"></div></div>
      <div class="pp-audio-time"><strong>0:05</strong> / 0:30</div>
    </div>
    <div class="pp-audio-chapter-list">${chapters}</div>
  </div>`;
}

function mangaPreview(sku) {
  const t = T();
  const pages = [1, 2, 3].map((n) =>
    `<div class="pp-reader-page"><span class="pp-reader-page-num">P${n}</span>${coverSVG({ sku_id: sku.sku_id + "_p" + n, title: sku.title, brand_id: sku.brand_id })}</div>`).join("");
  return `<section class="pp-section pp-container">
    <div class="pp-section-title">${escapeHtml(t.preview)}</div>
    <div class="pp-reader-pages" style="max-width:440px;margin:0 auto">${pages}</div>
    <div class="pp-reader-paywall">
      <h3>${escapeHtml(t.readFull)}</h3>
      <p>WEBTOON vertical reader + PDF download unlock after purchase.</p>
      ${cart.buyButtonHTML(sku, { label: t.buy, cls: "pp-btn-primary pp-btn-large", mode: "buy" })}
    </div>
  </section>`;
}

// ─── Pages ───────────────────────────────────────────────────────────────────
async function pageLanding() {
  const { items } = await getCatalog({ locale: state.locale, limit: 80 });
  const t = T();
  const hero = HERO[state.locale] || HERO["en-US"];
  const pick = (type, n) => items.filter((s) => s.product_type === type).slice(0, n);
  const section = (title, list) => list.length
    ? `<section class="pp-section pp-container"><div class="pp-section-title">${escapeHtml(title)}</div><div class="pp-grid">${list.map(skuCard).join("")}</div></section>` : "";
  return `${chipRail()}
  <section class="pp-hero pp-container">
    <div class="pp-hero-eyebrow">${hero.eyebrow}</div>
    <h1>${hero.h1}</h1>
    <p>${hero.p}</p>
  </section>
  ${section(t.featured, items.slice(0, 8))}
  ${section(t.book, pick("book", 8))}
  ${section(t.audiobook, pick("audiobook", 4))}
  ${section(t.manga, pick("manga", 4))}`;
}

function filtersHTML(type, q) {
  const base = q ? `q=${encodeURIComponent(q)}&` : "";
  const types = [["", "All formats"], ["book", "Books"], ["audiobook", "Audiobooks"], ["manga", "Manga"]];
  const rows = types.map(([v, l]) =>
    `<a class="pp-filter-row" href="#/search?${base}${v ? "product_type=" + v : ""}">
       <input type="radio" ${(type === v || (!type && !v)) ? "checked" : ""} readonly> ${l}</a>`).join("");
  return `<div class="pp-filter-group"><span class="pp-filter-label">Format</span><div class="pp-filter-options">${rows}</div></div>`;
}

async function pageSearch(params) {
  const q = params.get("q") || "";
  const brand = params.get("brand") || null;
  const type = params.get("product_type") || null;
  const { items, total } = await getCatalog({ locale: state.locale, q: q || null, brand, type, limit: 48 });
  const title = q ? `“${escapeHtml(q)}”` : brand ? escapeHtml(prettyBrand(brand)) : "everything";
  const grid = items.length ? `<div class="pp-grid">${items.map(skuCard).join("")}</div>`
    : `<p class="pp-card-subtitle">No results — try a different term.</p>`;
  return `${chipRail()}
  <div class="pp-results-layout pp-container">
    <aside class="pp-filters">${filtersHTML(type, q)}</aside>
    <div>
      <div class="pp-results-header"><span class="pp-result-count"><strong>${total}</strong> ${T().results} · ${title}</span></div>
      ${grid}
    </div>
  </div>`;
}

function reviewsBlock(sku, reviews, rt) {
  const t = T();
  const list = reviews.length
    ? reviews.map((r) => `<div class="pp-mt-16">
        <div class="pp-card-rating"><span class="pp-stars">${starString(r.stars)}</span> <strong>${escapeHtml(r.reviewer_name || "Reader")}</strong>${r.verified_purchase ? ' <span class="pp-verified-bay">Verified</span>' : ""}</div>
        <p class="pp-card-subtitle">${escapeHtml(r.body || "")}</p></div>`).join("")
    : `<p class="pp-card-subtitle">Be the first to review this.</p>`;
  return `<div class="pp-mt-32"><div class="pp-section-title">${t.reviews} · ${rt.count}</div>${list}
    <div class="pp-mt-16"><a class="pp-btn-ghost" href="#/review/${encodeURIComponent(sku.sku_id)}">${t.write}</a></div></div>`;
}

async function pageProduct(id) {
  const { sku } = await getSku(id, state.locale);
  if (!sku) return notFound();
  const t = T();
  const reviews = await getReviews(id);
  const rt = ratingDisplay(sku, reviews);
  const isAudio = sku.product_type === "audiobook";
  const isManga = sku.product_type === "manga";
  const buy = cart.buyButtonHTML(sku, { label: t.buy, cls: "pp-btn-primary pp-btn-large", mode: "buy" });
  const add = cart.buyButtonHTML(sku, { label: t.add, cls: "pp-btn-secondary pp-btn-large", mode: "add" });
  const specs = [
    ["Format", formatPill(sku.product_type)], ["Brand", brandLabel(sku)],
    ["Topic", prettyText(sku.topic || sku.subtitle || "—")], ["For", prettyText(sku.persona || "—")],
    ["Locale", sku.locale], ["SKU", sku.sku_id],
  ];
  return `<div class="pp-pdp pp-container">
    <div class="pp-pdp-left">
      <div class="pp-cover ${coverClass(sku.product_type)}">${coverSVG(sku)}</div>
      ${isAudio ? audioPlayer() : ""}
    </div>
    <div class="pp-pdp-right">
      <div class="pp-card-brand">${escapeHtml(brandLabel(sku))}</div>
      <h1 class="pp-pdp-title">${escapeHtml(sku.title || "")}</h1>
      <p class="pp-pdp-subtitle">${escapeHtml(sku.subtitle || "")}</p>
      <div class="pp-pdp-rating"><span class="pp-stars">${starString(rt.avg)}</span><a href="#/review/${encodeURIComponent(sku.sku_id)}">${rt.avg.toFixed(1)} · ${rt.count} ${t.reviews.toLowerCase()}</a></div>
      <div class="pp-pdp-price-row"><span class="pp-pdp-price">${money(sku.price_cents, sku.currency)}</span><span class="pp-pdp-format">${formatPill(sku.product_type)}</span></div>
      <div class="pp-pdp-cta-row">${buy}${add}</div>
      <div class="pp-spec-sheet">${specs.map(([k, v]) => `<span class="pp-spec-key">${escapeHtml(k)}</span><span class="pp-spec-val">${escapeHtml(v)}</span>`).join("")}</div>
      ${reviewsBlock(sku, reviews, rt)}
    </div>
  </div>${isManga ? mangaPreview(sku) : ""}`;
}

async function pageReview(id) {
  const { sku } = await getSku(id, state.locale);
  if (!sku) return notFound();
  currentStars = 5;
  return `<div class="pp-review-form pp-container">
    <div class="pp-review-context">
      <div class="pp-review-context-cover">${coverSVG(sku)}</div>
      <div class="pp-review-context-meta">
        <span class="pp-review-context-brand">${escapeHtml(brandLabel(sku))}</span>
        <span class="pp-review-context-title">${escapeHtml(sku.title || "")}</span></div>
    </div>
    <div class="pp-form-row"><label class="pp-form-label">Your rating</label>
      <div class="pp-star-picker">${[1, 2, 3, 4, 5].map((v) => `<span class="pp-star is-filled" data-v="${v}">★</span>`).join("")}</div></div>
    <div class="pp-form-row"><label class="pp-form-label">Name</label><input id="rev-name" type="text" placeholder="Display name (optional)"></div>
    <div class="pp-form-row"><label class="pp-form-label">Email</label><input id="rev-email" type="email" placeholder="you@example.com — enables the verified-purchase badge"></div>
    <div class="pp-form-row"><label class="pp-form-label">Your review</label>
      <span class="pp-form-hint">250–4000 characters.</span>
      <textarea id="rev-body" placeholder="What did this help with? Be specific."></textarea>
      <div class="pp-char-counter" id="rev-counter">0 / 4000</div></div>
    <div class="pp-turnstile-mock"><div class="pp-turnstile-checkbox">✓</div><span class="pp-turnstile-label">I'm human</span><span class="pp-turnstile-mark">Turnstile</span></div>
    <button class="pp-btn-primary pp-btn-large pp-review-submit" data-sku="${escapeHtml(sku.sku_id)}">Submit review</button>
    <div id="rev-msg" class="pp-mt-16"></div>
  </div>`;
}

async function pageLibrary() {
  const t = T();
  const items = await getLibrary();
  const verb = (pt) => (pt === "audiobook" ? "Listen" : pt === "manga" ? "Read" : "Download");
  const cards = items.length
    ? `<div class="pp-grid">${items.map((sku) => `<div class="pp-library-card">
        <div class="pp-cover ${coverClass(sku.product_type)}">${coverSVG(sku)}</div>
        <div class="pp-library-meta"><span class="pp-card-brand">${escapeHtml(brandLabel(sku))}</span><span class="pp-card-title">${escapeHtml(sku.title || "")}</span></div>
        <div class="pp-library-card-actions"><a class="pp-btn-secondary" href="#/p/${encodeURIComponent(sku.sku_id)}">${verb(sku.product_type)}</a></div>
      </div>`).join("")}</div>`
    : `<p class="pp-card-subtitle">${escapeHtml(t.empty)}</p>`;
  return `<div class="pp-library-header pp-container"><div class="pp-library-greeting">${escapeHtml(t.account)}</div><h1 class="pp-library-heading">Your <em>${escapeHtml(t.library)}</em></h1></div>
    <section class="pp-section pp-container">${cards}</section>`;
}

function notFound() {
  return `<section class="pp-section pp-container"><h1 class="pp-section-heading">Not found</h1><p class="pp-card-subtitle"><a href="#/">Back to home →</a></p></section>`;
}

// ─── Router ──────────────────────────────────────────────────────────────────
function parseHash() {
  const raw = location.hash.replace(/^#/, "") || "/";
  const [path, qs] = raw.split("?");
  return { seg: path.split("/").filter(Boolean), params: new URLSearchParams(qs || "") };
}

async function route() {
  const { seg, params } = parseHash();
  let content;
  try {
    if (seg.length === 0) content = await pageLanding();
    else if (seg[0] === "search") content = await pageSearch(params);
    else if (seg[0] === "p") content = await pageProduct(decodeURIComponent(seg.slice(1).join("/")));
    else if (seg[0] === "review") content = await pageReview(decodeURIComponent(seg.slice(1).join("/")));
    else if (seg[0] === "library") content = await pageLibrary();
    else content = notFound();
  } catch (err) {
    content = `<section class="pp-section pp-container"><p class="pp-card-subtitle">Something went wrong: ${escapeHtml(String(err))}</p></section>`;
  }
  $app.setAttribute("aria-busy", "false");
  $app.innerHTML = header() + `<main id="pp-main">${content}</main>` + footer();
  cart.refreshBadge();
  window.scrollTo(0, 0);
}

function setStars(v) {
  currentStars = v;
  document.querySelectorAll(".pp-star-picker .pp-star").forEach((s) =>
    s.classList.toggle("is-filled", parseInt(s.dataset.v, 10) <= v));
}

async function submitReview(skuId) {
  const name = (document.getElementById("rev-name").value || "Reader").trim() || "Reader";
  const email = document.getElementById("rev-email").value.trim();
  const body = document.getElementById("rev-body").value.trim();
  const msg = document.getElementById("rev-msg");
  if (body.length < 250) { msg.innerHTML = '<span class="pp-form-hint">Please write at least 250 characters so the review is useful.</span>'; return; }
  if (body.length > 4000) { msg.innerHTML = '<span class="pp-form-hint">Please keep it under 4000 characters.</span>'; return; }
  await postReview(skuId, { reviewer_name: name, stars: currentStars, body, locale: state.locale, email });
  location.hash = "#/p/" + encodeURIComponent(skuId);
}

async function setLocale(l) {
  if (!ACTIVE_LOCALES.includes(l) || l === state.locale) return;
  state.locale = l;
  document.documentElement.lang = l;
  await loadBrands();
  route();
}

function attachEvents() {
  document.addEventListener("keydown", (e) => {
    if (e.target.id === "pp-search" && e.key === "Enter") {
      const q = e.target.value.trim();
      location.hash = q ? "#/search?q=" + encodeURIComponent(q) : "#/";
    }
  });
  document.addEventListener("input", (e) => {
    if (e.target.id === "rev-body") {
      const c = document.getElementById("rev-counter");
      if (c) c.textContent = e.target.value.length + " / 4000";
    }
  });
  document.addEventListener("click", (e) => {
    const open = e.target.closest("[data-cart-open]");
    if (open) { e.preventDefault(); cart.openDrawer(); return; }
    const loc = e.target.closest("[data-locale]");
    if (loc) { e.preventDefault(); setLocale(loc.dataset.locale); return; }
    const star = e.target.closest(".pp-star");
    if (star) { setStars(parseInt(star.dataset.v, 10)); return; }
    const sub = e.target.closest(".pp-review-submit");
    if (sub) { e.preventDefault(); submitReview(sub.dataset.sku); return; }
  });
}

async function loadBrands() {
  const { items } = await getCatalog({ locale: state.locale, limit: 1000 });
  brandsCache = [...new Set(items.map((s) => s.brand_id))].sort();
}

async function loadBrandMap() {
  try { const r = await fetch("./app/brands.json"); if (r.ok) brandMap = await r.json(); } catch (_) {}
}
async function init() {
  cart.initCart();
  attachEvents();
  document.documentElement.lang = state.locale;
  await loadBrandMap();
  await loadBrands();
  await route();
}
window.addEventListener("hashchange", route);
init();
