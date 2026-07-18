import { useMemo } from "react";
import { useLocale } from "./i18n.jsx";

/**
 * Translation hook for BrandWizard.
 * t(category, englishString) -> translated string
 * td(category, dataArray, fields) -> array with translated fields
 * to(category, obj, fields) -> object with translated fields
 */
export function useTranslation() {
  const { locale, strings } = useLocale();
  const isEn = locale === "en";

  // t("ui", "Continue") -> looks up "ui.Continue" -> returns Japanese/Chinese/etc
  function t(category, key) {
    if (isEn) return key === undefined ? category : key;
    if (key === undefined) return strings[category] || category;
    const path = `${category}.${key}`;
    return strings[path] || key;
  }

  // Translate specific fields in an array of data objects
  // td("archetypes", ARCHETYPES, ["name", "tagline", "sampleTitle", ...])
  function td(category, items, fields) {
    if (isEn) return items;
    return items.map(item => {
      const out = { ...item };
      for (const f of fields) {
        const val = out[f];
        if (!val) continue;
        if (Array.isArray(val)) {
          out[f] = val.map(v => typeof v === "string" ? (strings[`${category}.${v}`] || v) : v);
        } else if (typeof val === "string") {
          out[f] = strings[`${category}.${val}`] || val;
        }
      }
      return out;
    });
  }

  // Translate specific fields in a single object
  function to(category, obj, fields) {
    if (isEn || !obj) return obj;
    const out = { ...obj };
    for (const f of fields) {
      const val = out[f];
      if (typeof val === "string") {
        out[f] = strings[`${category}.${val}`] || val;
      }
    }
    return out;
  }

  // Translate a plain object's values (keys stay, values get translated)
  // tv("emotions", { calm: "Feeling of peace", ... }) -> { calm: "平穏な気持ち", ... }
  function tv(category, obj) {
    if (isEn || !obj) return obj;
    const out = {};
    for (const [k, v] of Object.entries(obj)) {
      if (typeof v === "string") {
        out[k] = strings[`${category}.${v}`] || v;
      } else if (typeof v === "object" && v !== null && !Array.isArray(v)) {
        out[k] = tv(category, v);
      } else {
        out[k] = v;
      }
    }
    return out;
  }

  return { t, td, to, tv, locale, isEn };
}
