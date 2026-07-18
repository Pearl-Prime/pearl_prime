// /api/review — GET ?sku_id= lists visible reviews; POST submits one.
// Spec §11: 1-5 stars, 250-4000 char body, guest reviews ok (Q-PRP-AUTH-01),
// verified-purchase badge auto-applied from order_item, name moderation deny-list.
import { json, bad, getDB, nowSec, sha256Hex } from "../_lib.js";

export async function onRequestGet({ request, env }) {
  try {
    const db = getDB(env);
    const skuId = new URL(request.url).searchParams.get("sku_id");
    if (!skuId) return bad(400, "sku_id required");
    const rs = await db.prepare(
      `SELECT review_id, reviewer_name, stars, body, verified_purchase, helpful_count, locale, created_at
       FROM review WHERE sku_id = ? AND status = 'visible' ORDER BY created_at DESC LIMIT 100`
    ).bind(skuId).all();
    return json({ reviews: rs.results || [] });
  } catch (e) { return bad(500, String(e && e.message || e)); }
}

export async function onRequestPost({ request, env }) {
  try {
    const db = getDB(env);
    const b = await request.json().catch(() => ({}));
    const skuId = b.sku_id;
    const stars = parseInt(b.stars, 10);
    const body = (b.body || "").toString().trim();
    const name = ((b.reviewer_name || "Reader").toString().trim() || "Reader").slice(0, 80);
    const locale = (b.locale || "en-US").toString();
    const email = (b.email || "").toString().trim().toLowerCase();

    if (!skuId) return bad(400, "sku_id required");
    if (!(stars >= 1 && stars <= 5)) return bad(400, "stars must be an integer 1-5");
    if (body.length < 250 || body.length > 4000) return bad(400, "body must be 250-4000 characters");
    if (/pearl\s*prime|phoenix/i.test(name)) return bad(400, "reviewer name may not impersonate the brand");

    const sku = await db.prepare("SELECT sku_id FROM sku WHERE sku_id = ?").bind(skuId).first();
    if (!sku) return bad(404, "SKU not found");

    const emailHash = email ? await sha256Hex(email) : null;
    let verified = 0;
    if (emailHash) {
      const day = new Date().toISOString().slice(0, 10);
      const rl = await db.prepare("SELECT count FROM review_rate_limit WHERE email_hash = ? AND day = ?").bind(emailHash, day).first();
      if (rl && rl.count >= 10) return bad(429, "daily review limit reached");
      await db.prepare(
        `INSERT INTO review_rate_limit (email_hash, day, count) VALUES (?, ?, 1)
         ON CONFLICT(email_hash, day) DO UPDATE SET count = count + 1`
      ).bind(emailHash, day).run();
      const owns = await db.prepare("SELECT 1 FROM order_item WHERE sku_id = ? AND email_hash = ? LIMIT 1").bind(skuId, emailHash).first();
      verified = owns ? 1 : 0;
    }

    const ts = nowSec();
    const reviewId = "rev_" + crypto.randomUUID();
    await db.prepare(
      `INSERT INTO review (review_id, sku_id, account_id, reviewer_name, email_hash, stars, body,
        verified_purchase, status, helpful_count, reported_count, locale, created_at, updated_at)
       VALUES (?, ?, NULL, ?, ?, ?, ?, ?, 'visible', 0, 0, ?, ?, ?)`
    ).bind(reviewId, skuId, name, emailHash, stars, body, verified, locale, ts, ts).run();

    await recomputeSummary(db, skuId, ts);
    return json({ ok: true, review_id: reviewId, verified_purchase: verified });
  } catch (e) { return bad(500, String(e && e.message || e)); }
}

async function recomputeSummary(db, skuId, ts) {
  const a = await db.prepare(
    `SELECT COUNT(*) AS c, AVG(stars) AS avg,
       SUM(CASE WHEN stars=1 THEN 1 ELSE 0 END) AS s1,
       SUM(CASE WHEN stars=2 THEN 1 ELSE 0 END) AS s2,
       SUM(CASE WHEN stars=3 THEN 1 ELSE 0 END) AS s3,
       SUM(CASE WHEN stars=4 THEN 1 ELSE 0 END) AS s4,
       SUM(CASE WHEN stars=5 THEN 1 ELSE 0 END) AS s5
     FROM review WHERE sku_id = ? AND status = 'visible'`
  ).bind(skuId).first();
  await db.prepare(
    `INSERT INTO sku_review_summary (sku_id, avg_stars, count, star_1, star_2, star_3, star_4, star_5, updated_at)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
     ON CONFLICT(sku_id) DO UPDATE SET avg_stars=excluded.avg_stars, count=excluded.count,
       star_1=excluded.star_1, star_2=excluded.star_2, star_3=excluded.star_3,
       star_4=excluded.star_4, star_5=excluded.star_5, updated_at=excluded.updated_at`
  ).bind(skuId, a.avg || 0, a.c || 0, a.s1 || 0, a.s2 || 0, a.s3 || 0, a.s4 || 0, a.s5 || 0, ts).run();
}
