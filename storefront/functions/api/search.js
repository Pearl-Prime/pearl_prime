// GET /api/search?q=&locale= — FTS5 full-text search over the sku_search index
// (spec §9.1), joined back to sku + review aggregate.
import { json, bad, getDB, SKU_SELECT } from "../_lib.js";

export async function onRequestGet({ request, env }) {
  try {
    const db = getDB(env);
    const u = new URL(request.url);
    const locale = u.searchParams.get("locale") || "en-US";
    const q = (u.searchParams.get("q") || "").trim();
    const limit = Math.min(Math.max(parseInt(u.searchParams.get("limit") || "24", 10) || 24, 1), 96);
    if (!q) return json({ items: [], total: 0, q });

    // FTS5 prefix query; strip quotes/operators that could break MATCH syntax.
    const term = q.replace(/["*():]/g, " ").trim().split(/\s+/).filter(Boolean).map((t) => t + "*").join(" ");
    if (!term) return json({ items: [], total: 0, q });

    const sql = `SELECT ${SKU_SELECT},
        COALESCE(r.avg_stars, 0) AS avg_stars, COALESCE(r.count, 0) AS reviews_count
      FROM sku_search f
      JOIN sku s ON s.sku_id = f.sku_id
      LEFT JOIN sku_review_summary r ON r.sku_id = s.sku_id
      WHERE f.sku_search MATCH ? AND s.locale = ? AND s.status = 'active'
      ORDER BY rank LIMIT ?`;
    const rs = await db.prepare(sql).bind(term, locale, limit).all();
    const items = rs.results || [];
    return json({ items, total: items.length, q });
  } catch (e) {
    return bad(500, String(e && e.message || e));
  }
}
