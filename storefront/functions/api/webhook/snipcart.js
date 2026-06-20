// POST /api/webhook/snipcart — Snipcart order lifecycle (wraps Stripe).
// order.completed -> write order + order_item + grant entitlements (§10.4 / AMENDMENT .3).
// order.refunded  -> flip status + revoke entitlements (§10.6).
// Idempotent via webhook_event_log.
//
// SECURITY TODO (operator-gated): verify the X-Snipcart-RequestToken header against
// the Snipcart validation API using SNIPCART_WEBHOOK_SECRET before trusting the body.
import { json, bad, getDB, nowSec, sha256Hex } from "../../_lib.js";

export async function onRequestPost({ request, env }) {
  try {
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
