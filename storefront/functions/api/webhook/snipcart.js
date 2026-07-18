// POST /api/webhook/snipcart — Snipcart order lifecycle (wraps Stripe).
// order.completed -> write order + order_item + grant entitlements (§10.4 / AMENDMENT .3).
// order.refunded  -> flip status + revoke entitlements (§10.6).
// Idempotent via webhook_event_log.
//
import { json, bad, getDB, nowSec, sha256Hex } from "../../_lib.js";

// Verify the webhook is genuinely from Snipcart: the X-Snipcart-RequestToken must
// validate against Snipcart's API. If no secret is configured yet (pre-provision),
// skip with a warning so local/test flows still work; once SNIPCART_WEBHOOK_SECRET
// is set the webhook hard-rejects forged calls.
async function snipcartAuthOk(request, env) {
  const secret = env && env.SNIPCART_WEBHOOK_SECRET;
  const token = request.headers.get("x-snipcart-requesttoken");
  if (!secret) { console.warn("SNIPCART_WEBHOOK_SECRET unset — skipping webhook validation (pre-provision)"); return true; }
  if (!token) return false;
  try {
    const r = await fetch(`https://app.snipcart.com/api/requestvalidation/${encodeURIComponent(token)}`, {
      headers: { Accept: "application/json", Authorization: secret },
    });
    return r.ok;
  } catch (_) { return false; }
}

export async function onRequestPost({ request, env }) {
  try {
    if (!(await snipcartAuthOk(request, env))) return bad(401, "invalid Snipcart request token");
    const db = getDB(env);
    const event = await request.json().catch(() => ({}));
    const kind = event.eventName || event.event || "";
    const content = event.content || {};
    const token = content.token || event.token || "";
    const evtId = (event.id || token || "evt") + ":" + (kind || "unknown");
    const ts = nowSec();

    const seen = await db.prepare("SELECT 1 FROM webhook_event_log WHERE event_id = ? LIMIT 1").bind(evtId).first();
    if (seen) return json({ ok: true, dedup: true });

    if (kind === "order.completed") {
      const email = (content.email || "").trim().toLowerCase();
      const emailHash = email ? await sha256Hex(email) : null;
      const locale = (content.metadata && content.metadata.locale) || "en-US";
      const currency = (content.currency || "usd").toUpperCase();
      const totalCents = Math.round((content.finalGrandTotal != null ? content.finalGrandTotal : (content.total || 0)) * 100);
      const orderId = "ord_" + (token || crypto.randomUUID());
      await db.prepare(
        `INSERT OR IGNORE INTO order_table (order_id, account_id, email, locale, currency, total_cents, snipcart_token, status, created_at, paid_at)
         VALUES (?, NULL, ?, ?, ?, ?, ?, 'paid', ?, ?)`
      ).bind(orderId, email, locale, currency, totalCents, token || null, ts, ts).run();

      for (const it of (content.items || [])) {
        const skuId = it.id;
        if (!skuId) continue;
        await db.prepare(
          `INSERT INTO order_item (order_item_id, order_id, sku_id, qty, unit_price_cents, currency, email_hash)
           VALUES (?, ?, ?, ?, ?, ?, ?)`
        ).bind("oi_" + crypto.randomUUID(), orderId, skuId, it.quantity || 1, Math.round((it.price || 0) * 100), currency, emailHash).run();
        if (emailHash) {
          await db.prepare(
            `INSERT OR IGNORE INTO account_library (email_hash, sku_id, order_id, granted_at) VALUES (?, ?, ?, ?)`
          ).bind(emailHash, skuId, orderId, ts).run();
        }
      }
    } else if (kind === "order.refunded" && token) {
      await db.prepare("UPDATE order_table SET status = 'refunded' WHERE snipcart_token = ?").bind(token).run();
      await db.prepare(
        "UPDATE account_library SET revoked_at = ? WHERE order_id IN (SELECT order_id FROM order_table WHERE snipcart_token = ?)"
      ).bind(ts, token).run();
    }

    await db.prepare(
      "INSERT OR IGNORE INTO webhook_event_log (event_id, event_type, payload_hash, received_at, processed) VALUES (?, ?, NULL, ?, 1)"
    ).bind(evtId, kind, ts).run();
    return json({ ok: true });
  } catch (e) { return bad(500, String(e && e.message || e)); }
}
