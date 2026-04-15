import React, { createContext, useContext, useMemo } from "react";

import stringsEn from "./strings-en.json";

// Lazy-load locale files — they'll be code-split by Vite
const LOCALE_LOADERS = {
  en: () => Promise.resolve(stringsEn),
  ja: () => import("./strings-ja.json"),
  zh: () => import("./strings-zh.json"),
  tw: () => import("./strings-tw.json"),
};

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
 * Detect locale from URL search params or pathname.
 * /wizard-ja.html or ?lang=ja -> "ja"
 */
export function detectLocale() {
  const params = new URLSearchParams(window.location.search);
  const fromParam = params.get("lang");
  if (fromParam && LOCALE_LOADERS[fromParam]) return fromParam;

  const path = window.location.pathname;
  const match = path.match(/wizard-(ja|zh|tw)\./);
  if (match) return match[1];

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
