// GET /api/sku/:id — one SKU + its visible reviews + the cached rating summary.
import { json, bad, getDB, SKU_SELECT } from "../../_lib.js";

export async function onRequestGet({ params, env }) {
  try {
    const db = getDB(env);
    const id = params.id;
    const sku = await db.prepare(
      `SELECT ${SKU_SELECT}, COALESCE(r.avg_stars, 0) AS avg_stars, COALESCE(r.count, 0) AS reviews_count
       FROM sku s LEFT JOIN sku_review_summary r ON r.sku_id = s.sku_id
       WHERE s.sku_id = ?`
    ).bind(id).first();
    if (!sku) return bad(404, "SKU not found");

    const reviews = await db.prepare(
      `SELECT review_id, reviewer_name, stars, body, verified_purchase, helpful_count, locale, created_at
       FROM review WHERE sku_id = ? AND status = 'visible' ORDER BY created_at DESC LIMIT 50`
    ).bind(id).all();

    const summary = await db.prepare(
      `SELECT avg_stars, count, star_1, star_2, star_3, star_4, star_5 FROM sku_review_summary WHERE sku_id = ?`
    ).bind(id).first();

    return json({ sku, reviews: reviews.results || [], summary: summary || null });
  } catch (e) { return bad(500, String(e && e.message || e)); }
}
