import { useCallback } from "react";
import { useLocale } from "./i18n.jsx";

const LATIN_USER_FACING =
  /(?:>|"|'|\{|\(|^|\s)([A-Za-z][A-Za-z\s'.,!?;:\-—–/()0-9]{7,})/;

/** True when text looks like Latin user-facing copy (not ids, urls, or TODO markers). */
export function looksLikeLatinUserFacing(text) {
  if (typeof text !== "string") return false;
  const trimmed = text.trim();
  if (!trimmed || trimmed.startsWith("TODO_JA:")) return false;
  if (/^\/[\w/.-]+$/.test(trimmed)) return false;
  if (/^[\w.-]+@[\w.-]+$/.test(trimmed)) return false;
  if (/^cmp_[\w_]+$/.test(trimmed)) return false;
  if (/^https?:\/\//.test(trimmed)) return false;
  if (/[\u3040-\u30ff\u4e00-\u9fff]/.test(trimmed)) return false;
  return LATIN_USER_FACING.test(trimmed) || /^[A-Za-z][A-Za-z\s'.,!?;:\-—–/()0-9]{12,}$/.test(trimmed);
}

export function jaTranslateString(strings, category, text) {
  if (text == null || typeof text !== "string") return text;
  if (text.startsWith("TODO_JA:")) return text;
  if (!looksLikeLatinUserFacing(text)) return text;

  const path = `${category}.${text}`;
  const hit = strings?.[path];
  if (hit) return hit;

  const msg = `[BrandWizard-ja] Missing translation: ${path}`;
  console.error(msg);
  if (import.meta.env?.DEV) {
    console.assert(false, msg);
  }
  return `TODO_JA:${path}`;
}

export function pickJaI18n(i18n, key) {
  const value = i18n?.[key];
  if (value == null || (Array.isArray(value) && value.length === 0)) {
    const msg = `[BrandWizard-ja] Missing required i18n.${key}`;
    console.error(msg);
    if (import.meta.env?.DEV) throw new Error(msg);
    return null;
  }
  return value;
}

export function pickJaI18nFields(i18n, spec) {
  const out = {};
  for (const [alias, key] of Object.entries(spec)) {
    out[alias] = pickJaI18n(i18n, key);
  }
  return out;
}

export function translateVoiceTone10(strings, voiceTone10) {
  const out = {};
  for (const [sliderId, positions] of Object.entries(voiceTone10)) {
    out[sliderId] = positions.map((entry) => ({
      ...entry,
      label: jaTranslateString(strings, "voiceTone", entry.label),
      technique: jaTranslateString(strings, "voiceToneTechnique", entry.technique),
      benefits: (entry.benefits || []).map((b) =>
        typeof b === "string" ? jaTranslateString(strings, "voiceToneBenefits", b) : b,
      ),
    }));
  }
  return out;
}

/**
 * JA wizard translation hook — never silently returns English source keys.
 */
export function useJaWizardTranslation() {
  const { strings, locale } = useLocale();

  const t = useCallback(
    (category, key) => {
      if (key === undefined) {
        return jaTranslateString(strings, "misc", category);
      }
      const path = `${category}.${key}`;
      const hit = strings[path];
      if (hit) return hit;
      if (!looksLikeLatinUserFacing(key)) return key;
      const msg = `[BrandWizard-ja] Missing t(): ${path}`;
      console.error(msg);
      if (import.meta.env?.DEV) throw new Error(msg);
      return `TODO_JA:${path}`;
    },
    [strings],
  );

  const td = useCallback(
    (category, items, fields) =>
      items.map((item) => {
        const out = { ...item };
        for (const f of fields) {
          const val = out[f];
          if (!val) continue;
          if (Array.isArray(val)) {
            out[f] = val.map((v) =>
              typeof v === "string" ? jaTranslateString(strings, category, v) : v,
            );
          } else if (typeof val === "string") {
            out[f] = jaTranslateString(strings, category, val);
          }
        }
        return out;
      }),
    [strings],
  );

  const to = useCallback(
    (category, obj, fields) => {
      if (!obj) return obj;
      const out = { ...obj };
      for (const f of fields) {
        const val = out[f];
        if (typeof val === "string") {
          out[f] = jaTranslateString(strings, category, val);
        }
      }
      return out;
    },
    [strings],
  );

  const tv = useCallback(
    (category, obj) => {
      if (!obj) return obj;
      const out = {};
      for (const [k, v] of Object.entries(obj)) {
        if (typeof v === "string") {
          out[k] = jaTranslateString(strings, category, v);
        } else if (typeof v === "object" && v !== null && !Array.isArray(v)) {
          out[k] = tv(category, v);
        } else {
          out[k] = v;
        }
      }
      return out;
    },
    [strings],
  );

  return { t, td, to, tv, locale, isEn: false };
}
