/**
 * Brand Director roster data helpers (shared by BrandDirectorDashboard).
 *
 * Ops deep-links MUST go to brand_handoff_dashboard.html — the real-asset-gated
 * Brand Director Operations page. brand_admin.html is a stale setup console that
 * hardcodes phantom weekly title counts (titles:6/4/3…) and must not be presented
 * as the available-books surface.
 */

export function isAssigned(row) {
  return Boolean(String(row?.brand_director_name || "").trim());
}

export function statusText(value) {
  return String(value || "").replace(/_/g, " ") || "none";
}

/** Real Brand Director ops surface (downloadable assets / empty when none). */
export function brandOpsUrl(brandId) {
  return `/brand_handoff_dashboard.html?brand=${encodeURIComponent(brandId)}`;
}

export function brandWizardUrl(brandId) {
  return `/wizard.html?brand=${encodeURIComponent(brandId)}`;
}

export function staticRowsFromIndex(index) {
  return Object.entries(index || {})
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([brandId, record]) => ({
      brand_id: brandId,
      base_brand: record.arch || brandId.replace(/_[a-z]{2}_[a-z]{2}$/i, ""),
      display_brand: record.display_brand || record.d || brandId,
      lane: record.lane || "",
      teacher: record.t || "",
      is_teacher: Boolean(record.is_teacher),
      lifecycle: record.lifecycle || "unknown",
      active: String(record.lifecycle || "").toLowerCase() === "active",
      buildable: record.buildable !== false,
      brand_director_name: record.brand_director_name || "",
      brand_director_id: record.brand_director_id || "",
      brand_director_status: record.brand_director_status || "unassigned",
      assignment_source: record.brand_director_name ? "brand_admin_brands" : "none",
      wizard_url: brandWizardUrl(brandId),
      ops_url: brandOpsUrl(brandId),
      wizard_access: record.buildable === false ? "blocked" : "available",
      ops_access: record.buildable === false ? "blocked" : "available",
    }));
}

export function summaryFromRows(rows) {
  const assigned = rows.filter(isAssigned).length;
  return {
    total: rows.length,
    assigned,
    unassigned: rows.length - assigned,
    active: rows.filter((row) => row.active).length,
    inactive: rows.filter((row) => !row.active).length,
    wizard_ready: rows.filter((row) => row.wizard_access === "available").length,
    ops_ready: rows.filter((row) => row.ops_access === "available").length,
  };
}
