import { useMemo } from "react";
import { useTranslation } from "../useTranslation.jsx";

/** Maps wizard i18n locale codes to `?locale=` for GET /wizard/step/music-survey. */
export function wizardLocaleToMusicSurveyLocale(lc) {
  switch (lc) {
    case "ja":
      return "ja";
    case "zh":
      return "zh-cn";
    case "tw":
      return "zh-tw";
    default:
      return "en";
  }
}

/**
 * Music mode step 4 — embeds the static musician reflections survey via same-origin
 * GET /wizard/step/music-survey (replaces deprecated file:// loading).
 */
export function MusicianReflectionsSurveyPane({ state: _state, update: _update, i18n = {} }) {
  const { t } = useTranslation();
  const surveyLocale = useMemo(
    () => wizardLocaleToMusicSurveyLocale(i18n.locale || "en"),
    [i18n.locale],
  );
  const src = `/wizard/step/music-survey?locale=${encodeURIComponent(surveyLocale)}`;

  const eyebrow = "Music mode · Step 4";
  const title = "Musician reflections survey";
  const subtitle =
    "Pearl Prime music mode — capture your voice, themes, and healing intent. Responses become the YAML profile that drives reflections, lyric companions, and podcast atoms.";
  const helper =
    "The full survey loads below. Submit uses POST /wizard/music-survey/save from the embedded page (same origin).";

  return (
    <div>
      <div className="mb-8">
        <p className="mb-2 text-[10px] font-bold uppercase tracking-[0.2em] text-violet-600">{t("steps", eyebrow)}</p>
        <h2 className="text-2xl font-extrabold tracking-tight text-white sm:text-3xl">{t("steps", title)}</h2>
        <p className="mt-2 max-w-2xl text-sm leading-relaxed text-white">{t("steps", subtitle)}</p>
        <p className="mt-2 text-xs text-white">{t("steps", helper)}</p>
      </div>
      <iframe
        title="Musician reflections survey"
        src={src}
        className="min-h-[720px] w-full rounded-2xl border-2 border-gray-200 bg-white shadow-inner"
        sandbox="allow-forms allow-scripts allow-same-origin"
      />
    </div>
  );
}
