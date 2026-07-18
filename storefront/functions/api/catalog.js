// GET /api/catalog — browse SKUs by locale / brand / product_type, with cursor
// pagination + review aggregate join. Spec §7 + §9.4 (24/page, ?cursor=last_sku_id).
import { json, bad, getDB, SKU_SELECT } from "../_lib.js";

export async function onRequestGet({ request, env }) {
  try {
    const db = getDB(env);
    const u = new URL(request.url);
    const locale = u.searchParams.get("locale") || "en-US";
    const brand = u.searchParams.get("brand");
    const type = u.searchParams.get("product_type");
    const q = u.searchParams.get("q");
    const cursor = u.searchParams.get("cursor");
    const limit = Math.min(Math.max(parseInt(u.searchParams.get("limit") || "24", 10) || 24, 1), 96);

    const where = ["s.locale = ?", "s.status = 'active'"];
    const args = [locale];
    if (brand) { where.push("s.brand_id = ?"); args.push(brand); }
    if (type) { where.push("s.product_type = ?"); args.push(type); }
    if (q) {
      const like = "%" + q + "%";
      where.push("(s.title LIKE ? OR s.subtitle LIKE ? OR s.topic LIKE ? OR s.persona LIKE ?)");
      args.push(like, like, like, like);
    }

    const countRow = await db.prepare(`SELECT COUNT(*) AS n FROM sku s WHERE ${where.join(" AND ")}`).bind(...args).first();
    const total = countRow ? countRow.n : 0;

    const pageWhere = where.slice();
    const pageArgs = args.slice();
    if (cursor) { pageWhere.push("s.sku_id > ?"); pageArgs.push(cursor); }
    const sql = `SELECT ${SKU_SELECT},
        COALESCE(r.avg_stars, 0) AS avg_stars, COALESCE(r.count, 0) AS reviews_count
      FROM sku s LEFT JOIN sku_review_summary r ON r.sku_id = s.sku_id
      WHERE ${pageWhere.join(" AND ")} ORDER BY s.sku_id LIMIT ?`;
    pageArgs.push(limit + 1);
    const rs = await db.prepare(sql).bind(...pageArgs).all();
    const rows = rs.results || [];
    const hasMore = rows.length > limit;
    const items = rows.slice(0, limit);
    return json({ items, total, cursor: hasMore ? items[items.length - 1].sku_id : null, locale });
  } catch (e) {
    return bad(500, String(e && e.message || e));
  }
}
