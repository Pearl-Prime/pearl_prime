import React, { createContext, useContext, useMemo } from "react";

import stringsEn from "./strings-en.json";

// Lazy-load locale files — they'll be code-split by Vite.
// One short key per translated string file. zh-HK and zh-SG intentionally reuse
// the Traditional (tw) and Simplified (zh) wizard copy respectively — documented
// aliases below, never a silent US-English fallback.
const LOCALE_LOADERS = {
  en: () => Promise.resolve(stringsEn),
  ja: () => import("./strings-ja.json"),
  zh: () => import("./strings-zh.json"),
  tw: () => import("./strings-tw.json"),
  ko: () => import("./strings-ko.json"),
  es: () => import("./strings-es.json"),
  es_es: () => import("./strings-es_es.json"),
  fr: () => import("./strings-fr.json"),
  de: () => import("./strings-de.json"),
  it: () => import("./strings-it.json"),
  hu: () => import("./strings-hu.json"),
  pt: () => import("./strings-pt.json"),
};

// Normalize any incoming locale/lane/market token to a LOCALE_LOADERS key.
// Accepts short keys (ja), lane codes (ja_jp / ja-JP), and market words (japan).
// zh-HK → tw (Traditional), zh-SG → zh (Simplified): intentional, documented.
const LOCALE_ALIASES = {
  en: "en", en_us: "en", "en-us": "en", us: "en", usa: "en", united_states: "en",
  ja: "ja", ja_jp: "ja", "ja-jp": "ja", jp: "ja", japan: "ja",
  ko: "ko", ko_kr: "ko", "ko-kr": "ko", kr: "ko", korea: "ko",
  zh: "zh", zh_cn: "zh", "zh-cn": "zh", cn: "zh", china: "zh", "zh-hans": "zh",
  sg: "zh", zh_sg: "zh", "zh-sg": "zh", singapore: "zh",
  tw: "tw", zh_tw: "tw", "zh-tw": "tw", taiwan: "tw", "zh-hant": "tw",
  hk: "tw", zh_hk: "tw", "zh-hk": "tw", hong_kong: "tw",
  es: "es", es_us: "es", "es-us": "es", mexico: "es", latam: "es",
  es_es: "es_es", "es-es": "es_es", spain: "es_es",
  fr: "fr", fr_fr: "fr", "fr-fr": "fr", france: "fr",
  de: "de", de_de: "de", "de-de": "de", germany: "de",
  it: "it", it_it: "it", "it-it": "it", italy: "it",
  hu: "hu", hu_hu: "hu", "hu-hu": "hu", hungary: "hu",
  pt: "pt", pt_br: "pt", "pt-br": "pt", brazil: "pt", br: "pt",
};

/** Resolve any locale/lane/market token to a supported wizard locale key, or null. */
export function resolveLocaleKey(raw) {
  if (!raw) return null;
  const norm = String(raw).toLowerCase().replace(/[\s-]+/g, "_");
  if (LOCALE_LOADERS[norm]) return norm;
  if (LOCALE_ALIASES[norm]) return LOCALE_ALIASES[norm];
  // hyphenated form (es-es) also present in alias table
  const hy = String(raw).toLowerCase();
  if (LOCALE_ALIASES[hy]) return LOCALE_ALIASES[hy];
  return null;
}

const I18nContext = createContext({ locale: "en", strings: {} });

// Flatten nested object into dot-path keys
function flatten(obj, prefix = "") {
  const result = {};
  for (const [k, v] of Object.entries(obj)) {
    const key = prefix ? `${prefix}.${k}` : k;
    if (v && typeof v === "object" && !Array.isArray(v)) {
      Object.assign(result, flatten(v, key));
    } else {
      result[key] = v;
    }
  }
  return result;
}

export function I18nProvider({ locale, strings, children }) {
  const flat = useMemo(() => flatten(strings), [strings]);
  return (
    <I18nContext.Provider value={{ locale, strings: flat }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useLocale() {
  return useContext(I18nContext);
}

/**
 * Translation hook. Returns t(category, key) function.
 * t("ui", "Continue") -> looks up "ui.Continue" in flat strings
 * Falls back to the key itself (English) if not found.
 */
export function useT() {
  const { strings } = useContext(I18nContext);
  return function t(category, key) {
    if (key === undefined) {
      // Single arg: direct dot-path
      return strings[category] || category;
    }
    const path = `${category}.${key}`;
    return strings[path] || key;
  };
}

/**
 * Detect locale from URL search params, market/lane hints, or pathname.
 *   ?lang=fr / ?lang=fr-FR / ?lang=fr_fr  -> "fr"
 *   ?market=brazil / ?lane=pt_br          -> "pt"
 *   /wizard-ja.html                        -> "ja"
 * Falls back to "en" only when nothing resolves.
 */
export function detectLocale() {
  const params = new URLSearchParams(window.location.search);
  const fromParam =
    resolveLocaleKey(params.get("lang")) ||
    resolveLocaleKey(params.get("locale")) ||
    resolveLocaleKey(params.get("lane")) ||
    resolveLocaleKey(params.get("market"));
  if (fromParam) return fromParam;

  const path = window.location.pathname;
  const match = path.match(/wizard-([a-z_]+)/);
  if (match) {
    const key = resolveLocaleKey(match[1]);
    if (key) return key;
  }

  try {
    const stored = localStorage.getItem("phoenix_lane") || localStorage.getItem("phoenix_onboarding_market");
    const key = resolveLocaleKey(stored);
    if (key) return key;
  } catch (_) {}

  return "en";
}

/**
 * Load strings for a locale. Returns { locale, strings }.
 */
export async function loadLocale(locale) {
  const loader = LOCALE_LOADERS[locale] || LOCALE_LOADERS.en;
  const mod = await loader();
  return { locale, strings: mod.default || mod };
}

export { LOCALE_LOADERS };
