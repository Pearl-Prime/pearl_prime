/**
 * 14-flag locale gate for /teacher_onboarding.
 * Pattern mirrored from pearl_prime_entry.html LANES / selectLane — without
 * mutating that page or sharing its phoenix_lane localStorage key.
 */
import { TEACHER_ONBOARDING_LOCALES, useTeacherOnboardingI18n } from "../../i18n-teacher-onboarding.jsx";

export default function FlagLocaleGate({ onSelect }) {
  const { t, setLocale } = useTeacherOnboardingI18n();

  const handleSelect = (code) => {
    setLocale(code);
    if (typeof onSelect === "function") onSelect(code);
  };

  return (
    <main
      className="flex min-h-screen items-center justify-center bg-[#0e0a06] px-4 py-10 text-stone-100"
      data-testid="teacher-onboarding-flag-gate"
    >
      <div className="w-full max-w-3xl">
        <div className="mb-8 text-center">
          <div className="text-[10px] uppercase tracking-[0.22em] text-amber-500">{t("gate.eyebrow")}</div>
          <h1 className="mt-3 text-4xl font-semibold tracking-tight text-stone-50">{t("gate.heading")}</h1>
          <p className="mx-auto mt-3 max-w-xl text-sm leading-6 text-stone-400">{t("gate.subheading")}</p>
        </div>
        <div
          className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4"
          role="listbox"
          aria-label={t("gate.heading")}
          data-testid="teacher-onboarding-flag-grid"
        >
          {TEACHER_ONBOARDING_LOCALES.map((lane) => (
            <button
              key={lane.code}
              type="button"
              role="option"
              data-locale={lane.code}
              data-testid={`flag-${lane.code}`}
              onClick={() => handleSelect(lane.code)}
              className="flex flex-col items-center gap-1.5 rounded border border-amber-900/30 bg-[#1c1009]/60 px-3 py-5 transition hover:-translate-y-0.5 hover:border-amber-600 hover:bg-amber-900/20"
            >
              <span className="text-3xl leading-none" aria-hidden="true">
                {lane.flag}
              </span>
              <span className="font-mono text-[10px] uppercase tracking-[0.08em] text-stone-400">{lane.name}</span>
              <span className="font-mono text-[9px] text-stone-500">{lane.lang}</span>
            </button>
          ))}
        </div>
      </div>
    </main>
  );
}

export { TEACHER_ONBOARDING_LOCALES };
