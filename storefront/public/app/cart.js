// Pearl Prime storefront — cart. Real cart = Snipcart drop-in (wraps Stripe) when
// a public key is configured (AMENDMENT-2026-06-04.2/.6). With no key (local
// verification), a lightweight fallback drawer exercises the same add / buy UX
// against the identical SKU data so the flow is demonstrable end-to-end.
import { escapeHtml, money, prettyBrand, snipcartPrice } from "./format.js";
import { grantLocalEntitlement } from "./api.js";

const KEY = (window.PP_CONFIG && window.PP_CONFIG.snipcartKey) || "";
const VER = (window.PP_CONFIG && window.PP_CONFIG.snipcartVersion) || "3.7.1";
const skuReg = new Map();
let localItems = [];

export function snipcartActive() { return !!KEY; }
export function registerSku(sku) { if (sku && sku.sku_id) skuReg.set(sku.sku_id, sku); }
export function cartCount() { return snipcartActive() ? 0 : localItems.length; }

// Buttons carry the canonical Snipcart data-attributes (real, spec-compliant). With
// no key we render plain buttons handled by the local fallback below.
export function buyButtonHTML(sku, { label, cls = "pp-btn-primary", mode = "add" } = {}) {
  registerSku(sku);
  const text = label || (mode === "buy" ? "Buy now" : "Add to cart");
  if (KEY) {
    const sc = mode === "buy" ? "snipcart-checkout" : "snipcart-add-item";
    return `<button class="${cls} ${sc}"` +
      ` data-item-id="${escapeHtml(sku.sku_id)}"` +
      ` data-item-name="${escapeHtml(sku.title || "")}"` +
      ` data-item-price="${snipcartPrice(sku.price_cents, sku.currency)}"` +
      ` data-item-url="/api/sku/${encodeURIComponent(sku.sku_id)}"` +
      ` data-item-description="${escapeHtml(sku.subtitle || "")}"` +
      ` data-item-file-guid="">${escapeHtml(text)}</button>`;
  }
  return `<button class="${cls} pp-local-${mode}" data-sku-id="${escapeHtml(sku.sku_id)}">${escapeHtml(text)}</button>`;
}

function ensureRoot() {
  let el = document.getElementById("pp-cart-root");
  if (!el) { el = document.createElement("div"); el.id = "pp-cart-root"; document.body.appendChild(el); }
  return el;
}
export function openDrawer() { renderDrawer(true); }
export function closeDrawer() { renderDrawer(false); }

function renderDrawer(open) {
  const root = ensureRoot();
  if (!open) { root.innerHTML = ""; return; }
  const sum = localItems.reduce((a, s) => a + s.price_cents, 0);
  const cur = localItems[0] ? localItems[0].currency : "USD";
  const items = localItems.map((s) => `
    <div class="pp-cart-item">
      <div class="pp-cart-item-cover"></div>
      <div class="pp-cart-item-meta">
        <span class="pp-cart-item-brand">${escapeHtml(prettyBrand(s.brand_id))}</span>
        <span class="pp-cart-item-title">${escapeHtml(s.title || "")}</span>
        <span class="pp-cart-item-format">${escapeHtml(s.product_type)}</span>
        <button class="pp-cart-item-remove" data-remove="${escapeHtml(s.sku_id)}">Remove</button>
      </div>
      <span class="pp-cart-item-price">${money(s.price_cents, s.currency)}</span>
    </div>`).join("") || `<p class="pp-cart-snipcart-mark">Your cart is empty.</p>`;
  root.innerHTML = `
    <div class="pp-cart-overlay">
      <aside class="pp-cart-drawer" role="dialog" aria-label="Cart">
        <div class="pp-cart-header"><h2>Your cart</h2><button class="pp-cart-close" aria-label="Close">×</button></div>
        <div class="pp-cart-items">${items}</div>
        <div class="pp-cart-totals">
          <div class="pp-cart-total-row is-grand"><span>Total</span><span class="pp-cart-total-amount">${money(sum, cur)}</span></div>
        </div>
        <div class="pp-cart-footer">
          <button class="pp-btn-primary pp-btn-full pp-local-checkout">Checkout</button>
          <p class="pp-cart-snipcart-mark">Secure checkout by <em>Snipcart</em> · Stripe — <em>local preview</em></p>
        </div>
      </aside>
    </div>`;
}

function updateBadge() {
  const b = document.querySelector("[data-cart-badge]");
  if (b) { const n = cartCount(); b.textContent = String(n); b.style.display = n ? "flex" : "none"; }
}
export function refreshBadge() { updateBadge(); }

export function initCart() {
  if (KEY) {
    const css = document.createElement("link");
    css.rel = "stylesheet"; css.href = `https://cdn.snipcart.com/themes/v${VER}/default/snipcart.css`;
    document.head.appendChild(css);
    const div = document.createElement("div");
    div.id = "snipcart"; div.setAttribute("data-api-key", KEY); div.hidden = true;
    document.body.appendChild(div);
    const js = document.createElement("script");
    js.async = true; js.src = `https://cdn.snipcart.com/themes/v${VER}/default/snipcart.js`;
    document.body.appendChild(js);
    return;
  }
  // Local fallback: one delegated handler for the whole cart UX.
  document.addEventListener("click", (e) => {
    const add = e.target.closest(".pp-local-add");
    const buy = e.target.closest(".pp-local-buy");
    const rm = e.target.closest("[data-remove]");
    const checkout = e.target.closest(".pp-local-checkout");
    const closeBtn = e.target.closest(".pp-cart-close");
    const backdrop = e.target.classList && e.target.classList.contains("pp-cart-overlay");
    if (add) { e.preventDefault(); const s = skuReg.get(add.dataset.skuId); if (s) localItems.push(s); updateBadge(); openDrawer(); }
    else if (buy) { e.preventDefault(); const s = skuReg.get(buy.dataset.skuId); if (s) { grantLocalEntitlement(s.sku_id); location.hash = "#/library"; } }
    else if (rm) { e.preventDefault(); localItems = localItems.filter((s) => s.sku_id !== rm.dataset.remove); updateBadge(); renderDrawer(true); }
    else if (checkout) { e.preventDefault(); localItems.forEach((s) => grantLocalEntitlement(s.sku_id)); localItems = []; updateBadge(); closeDrawer(); location.hash = "#/library"; }
    else if (closeBtn || backdrop) { e.preventDefault(); closeDrawer(); }
  });
}
