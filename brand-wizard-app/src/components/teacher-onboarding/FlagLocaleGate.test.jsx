import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { render, screen, fireEvent, cleanup, waitFor } from "@testing-library/react";
import TeacherOnboarding from "./TeacherOnboarding.jsx";
import {
  TeacherOnboardingI18nProvider,
  TEACHER_ONBOARDING_LOCALE_KEY,
  TEACHER_ONBOARDING_LOCALES,
} from "../../i18n-teacher-onboarding.jsx";

const store = new Map();
const localStorageMock = {
  getItem: (k) => (store.has(k) ? store.get(k) : null),
  setItem: (k, v) => {
    store.set(String(k), String(v));
  },
  removeItem: (k) => {
    store.delete(k);
  },
  clear: () => store.clear(),
};

vi.stubGlobal("localStorage", localStorageMock);

function renderApp() {
  return render(
    <TeacherOnboardingI18nProvider>
      <TeacherOnboarding />
    </TeacherOnboardingI18nProvider>
  );
}

describe("Teacher onboarding flag-first locale gate", () => {
  beforeEach(() => {
    store.clear();
  });

  afterEach(() => {
    cleanup();
    store.clear();
  });

  it("renders the flag grid as the first content (no Identity section)", () => {
    renderApp();
    expect(screen.getByTestId("teacher-onboarding-flag-gate")).toBeTruthy();
    expect(screen.getByTestId("teacher-onboarding-flag-grid")).toBeTruthy();
    expect(document.querySelector("#identity")).toBeNull();
  });

  it("exposes exactly 14 locale flags", () => {
    expect(TEACHER_ONBOARDING_LOCALES).toHaveLength(14);
    renderApp();
    for (const lane of TEACHER_ONBOARDING_LOCALES) {
      expect(screen.getByTestId(`flag-${lane.code}`)).toBeTruthy();
    }
  });

  it("clicking a flag sets locale and reveals the form (pilot locales)", async () => {
    const pilot = ["en-US", "ja-JP", "zh-TW"];
    for (const code of pilot) {
      store.clear();
      cleanup();
      const { unmount } = renderApp();
      expect(screen.getByTestId("teacher-onboarding-flag-gate")).toBeTruthy();
      fireEvent.click(screen.getByTestId(`flag-${code}`));
      expect(localStorage.getItem(TEACHER_ONBOARDING_LOCALE_KEY)).toBe(code);
      // Locale JSON loads async — wait for form section, not English chrome title.
      await waitFor(() => {
        expect(document.querySelector("#identity")).toBeTruthy();
      });
      expect(screen.queryByTestId("teacher-onboarding-flag-gate")).toBeNull();
      unmount();
    }
  });

  it("does not render sections before a locale is chosen", () => {
    renderApp();
    for (const id of ["identity", "rights", "teachings", "stories", "practices", "voice", "activate"]) {
      expect(document.querySelector(`#${id}`)).toBeNull();
    }
  });
});
