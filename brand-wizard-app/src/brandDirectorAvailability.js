// Real-asset availability helpers for Brand Director surfaces.
//
// Listing / catalog metadata / planned titles are NOT available books.
// Only delivery rows with a real downloadable file+url count. Empty means empty.

const LANE_SUFFIX_RE =
  /_(en_us|es_us|es_es|fr_fr|de_de|it_it|hu_hu|pt_br|zh_tw|zh_hk|zh_cn|zh_sg|ja_jp|ko_kr)$/;

export function baseBrandFromId(brandId) {
  return String(brandId || "").replace(LANE_SUFFIX_RE, "");
}

export function opsUrlForBrand(brandId) {
  return `/brand_handoff_dashboard.html?brand=${encodeURIComponent(brandId)}`;
}

export function wizardUrlForBrand(brandId) {
  return `/wizard.html?brand=${encodeURIComponent(brandId)}`;
}

export function isProductionPending(delivery) {
  if (!delivery || typeof delivery !== "object") return false;
  if (delivery.production_files_ready === false) return true;
  const st = String(delivery.delivery_status || "")
    .trim()
    .toLowerCase();
  return (
    st === "catalog_ready_production_files_pending" ||
    /production[_ ]?files[_ ]?pending/.test(st)
  );
}

/**
 * Return only real downloadable production assets from a brand_deliveries payload.
 * Catalog-only / planned / production-pending → [].
 */
export function availableDownloadableAssets(delivery) {
  if (!delivery || typeof delivery !== "object") return [];
  if (isProductionPending(delivery)) return [];
  const weeks = delivery.weeks;
  if (!weeks || typeof weeks !== "object") return [];

  const out = [];
  for (const week of Object.keys(weeks).sort()) {
    const platforms = weeks[week] || {};
    if (!platforms || typeof platforms !== "object") continue;
    for (const [platform, files] of Object.entries(platforms)) {
      if (platform === "catalog_metadata") continue;
      if (!Array.isArray(files)) continue;
      for (const item of files) {
        if (!item || typeof item !== "object") continue;
        if (item.production_files_ready === false) continue;
        const url = String(item.url || "").trim();
        const filename = String(item.file || "").trim();
        if (!url || !filename) continue;
        if (/\.(md|cue)$/i.test(filename)) continue;
        out.push({
          week,
          platform,
          file: filename,
          url,
          kb: item.kb,
        });
      }
    }
  }
  return out;
}

export function availableBooksSummary(delivery) {
  const assets = availableDownloadableAssets(delivery);
  return {
    count: assets.length,
    assets,
    empty: assets.length === 0,
    empty_label: "No titles available yet",
  };
}

export async function loadDeliveryForBrand(brandId) {
  const base = baseBrandFromId(brandId);
  if (!base) return null;
  try {
    const response = await fetch(`brand_deliveries/${base}.json`, {
      cache: "no-store",
    });
    if (!response.ok) return null;
    const body = await response.json();
    return body && typeof body === "object" ? body : null;
  } catch (_) {
    return null;
  }
}
