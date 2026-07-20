/**
 * Teacher-onboarding i18n — separate from wizard `i18n.jsx`.
 *
 * Uses BCP-47 locale keys matching config/localization/locale_registry.yaml
 * (en-US, ja-JP, …) and localStorage key `phoenix_teacher_onboarding_locale`
 * so it never cross-contaminates the wizard's `phoenix_lane` key.
 *
 * Why not reuse i18n.jsx detectLocale()? That module resolves to short wizard
 * keys (en/ja/tw) and loads strings-*.json for BrandWizard. Teacher onboarding
 * needs the full 14-locale contract at locales/teacher_onboarding/<locale>.json.
 */
import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import enUS from "./locales/teacher_onboarding/en-US.json";

export const TEACHER_ONBOARDING_LOCALE_KEY = "phoenix_teacher_onboarding_locale";

/** Canonical 14 locales (registry order). */
export const TEACHER_ONBOARDING_LOCALES = [
  { code: "en-US", flag: "🇺🇸", name: "United States", lang: "English" },
  { code: "ja-JP", flag: "🇯🇵", name: "Japan", lang: "日本語" },
  { code: "ko-KR", flag: "🇰🇷", name: "Korea", lang: "한국어" },
  { code: "zh-TW", flag: "🇹🇼", name: "Taiwan", lang: "繁體中文" },
  { code: "zh-CN", flag: "🇨🇳", name: "China", lang: "简体中文" },
  { code: "zh-HK", flag: "🇭🇰", name: "Hong Kong", lang: "粵語" },
  { code: "zh-SG", flag: "🇸🇬", name: "Singapore", lang: "中文/EN" },
  { code: "es-US", flag: "🇺🇸", name: "US Hispanic", lang: "Español" },
  { code: "es-ES", flag: "🇪🇸", name: "Spain", lang: "Español" },
  { code: "fr-FR", flag: "🇫🇷", name: "France", lang: "Français" },
  { code: "de-DE", flag: "🇩🇪", name: "Germany", lang: "Deutsch" },
  { code: "it-IT", flag: "🇮🇹", name: "Italy", lang: "Italiano" },
  { code: "hu-HU", flag: "🇭🇺", name: "Hungary", lang: "Magyar" },
  { code: "pt-BR", flag: "🇧🇷", name: "Brazil", lang: "Português" },
];

const LOCALE_CODES = new Set(TEACHER_ONBOARDING_LOCALES.map((l) => l.code));

const LOCALE_LOADERS = {
  "en-US": () => Promise.resolve(enUS),
  "ja-JP": () => import("./locales/teacher_onboarding/ja-JP.json"),
  "zh-TW": () => import("./locales/teacher_onboarding/zh-TW.json"),
  "zh-CN": () => import("./locales/teacher_onboarding/zh-CN.json"),
  "zh-HK": () => import("./locales/teacher_onboarding/zh-HK.json"),
  "zh-SG": () => import("./locales/teacher_onboarding/zh-SG.json"),
  "ko-KR": () => import("./locales/teacher_onboarding/ko-KR.json"),
  "es-US": () => import("./locales/teacher_onboarding/es-US.json"),
  "es-ES": () => import("./locales/teacher_onboarding/es-ES.json"),
  "fr-FR": () => import("./locales/teacher_onboarding/fr-FR.json"),
  "de-DE": () => import("./locales/teacher_onboarding/de-DE.json"),
  "it-IT": () => import("./locales/teacher_onboarding/it-IT.json"),
  "hu-HU": () => import("./locales/teacher_onboarding/hu-HU.json"),
  "pt-BR": () => import("./locales/teacher_onboarding/pt-BR.json"),
};

function flatten(obj, prefix = "") {
  const result = {};
  for (const [k, v] of Object.entries(obj || {})) {
    if (k === "_meta") continue;
    const key = prefix ? `${prefix}.${k}` : k;
    if (v && typeof v === "object" && !Array.isArray(v)) {
      Object.assign(result, flatten(v, key));
    } else {
      result[key] = v;
    }
  }
  return result;
}

const FLAT_EN = flatten(enUS);

export function normalizeTeacherOnboardingLocale(raw) {
  if (!raw) return null;
  const s = String(raw).trim().replace(/_/g, "-");
  if (LOCALE_CODES.has(s)) return s;
  // tolerate lowercase
  const hit = [...LOCALE_CODES].find((c) => c.toLowerCase() === s.toLowerCase());
  return hit || null;
}

export function readStoredTeacherOnboardingLocale() {
  try {
    return normalizeTeacherOnboardingLocale(localStorage.getItem(TEACHER_ONBOARDING_LOCALE_KEY));
  } catch {
    return null;
  }
}

export function writeStoredTeacherOnboardingLocale(code) {
  const locale = normalizeTeacherOnboardingLocale(code);
  if (!locale) return null;
  try {
    localStorage.setItem(TEACHER_ONBOARDING_LOCALE_KEY, locale);
  } catch {
    /* ignore quota / private mode */
  }
  return locale;
}

export function clearStoredTeacherOnboardingLocale() {
  try {
    localStorage.removeItem(TEACHER_ONBOARDING_LOCALE_KEY);
  } catch {
    /* ignore */
  }
}

async function loadLocaleStrings(locale) {
  const code = normalizeTeacherOnboardingLocale(locale) || "en-US";
  const loader = LOCALE_LOADERS[code] || LOCALE_LOADERS["en-US"];
  try {
    const mod = await loader();
    const data = mod?.default || mod || enUS;
    const flat = flatten(data);
    // Never render blank — fall back per-key to en-US.
    return { ...FLAT_EN, ...Object.fromEntries(Object.entries(flat).filter(([, v]) => v != null && v !== "")) };
  } catch {
    return { ...FLAT_EN };
  }
}

const Ctx = createContext({
  locale: null,
  strings: FLAT_EN,
  t: (key, fallback) => FLAT_EN[key] ?? fallback ?? key,
  setLocale: () => {},
  clearLocale: () => {},
  ready: false,
});

export function TeacherOnboardingI18nProvider({ children }) {
  const [locale, setLocaleState] = useState(() => readStoredTeacherOnboardingLocale());
  const [strings, setStrings] = useState(FLAT_EN);
  const [ready, setReady] = useState(() => !readStoredTeacherOnboardingLocale());

  useEffect(() => {
    let cancelled = false;
    if (!locale) {
      setStrings(FLAT_EN);
      setReady(true);
      return undefined;
    }
    setReady(false);
    loadLocaleStrings(locale).then((flat) => {
      if (!cancelled) {
        setStrings(flat);
        setReady(true);
      }
    });
    return () => {
      cancelled = true;
    };
  }, [locale]);

  const setLocale = useCallback((code) => {
    const next = writeStoredTeacherOnboardingLocale(code);
    if (next) setLocaleState(next);
  }, []);

  const clearLocale = useCallback(() => {
    clearStoredTeacherOnboardingLocale();
    setLocaleState(null);
  }, []);

  const t = useCallback(
    (key, fallback) => {
      const v = strings[key];
      if (v == null || v === "") return fallback ?? FLAT_EN[key] ?? key;
      return v;
    },
    [strings]
  );

  const value = useMemo(
    () => ({ locale, strings, t, setLocale, clearLocale, ready }),
    [locale, strings, t, setLocale, clearLocale, ready]
  );

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useTeacherOnboardingI18n() {
  return useContext(Ctx);
}
